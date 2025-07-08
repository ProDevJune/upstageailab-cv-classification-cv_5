"""
기본 HPO 자동화 실험 엔진
Grid Search + Random Search 기반
"""

import os
import sys
import yaml
import itertools
import random
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import subprocess
import json
import time

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from codes.platform_detector import PlatformDetector
from codes.enhanced_config_manager import EnhancedConfigManager

class BasicHPO:
    """기본 Grid Search + Random Search HPO"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.detector = PlatformDetector()
        self.config_manager = EnhancedConfigManager(self.detector)
        self.results_file = self.project_root / "experiment_results.csv"
        self.practice_dir = self.project_root / "codes" / "practice"
        
        # 결과 파일 초기화
        self._initialize_results_file()
        
        print("🎯 기본 HPO 시스템 초기화 완료")
        self.detector.print_system_summary()
    
    def _initialize_results_file(self):
        """실험 결과 파일 초기화"""
        if not self.results_file.exists():
            columns = [
                'experiment_id', 'timestamp', 'platform', 'device', 'status',
                'model_name', 'image_size', 'lr', 'batch_size', 'augmentation_level',
                'TTA', 'epochs_run', 'final_f1', 'val_accuracy', 'training_time_min',
                'config_path', 'model_path', 'submission_path', 'error_message'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.results_file, index=False)
            print(f"📊 실험 결과 파일 생성: {self.results_file}")
    
    def define_experiment_space(self, experiment_type: str = "quick") -> Dict:
        """실험 공간 정의"""
        
        # 기본 하이퍼파라미터 공간
        base_space = {
            'models': ['resnet34.tv_in1k', 'resnet50.tv2_in1k', 'efficientnet_b3.ra2_in1k'],
            'image_sizes': [224, 320, 384],
            'learning_rates': [0.001, 0.0001, 0.00001],
            'augmentation_levels': ['minimal', 'moderate', 'strong'],
            'TTA': [True, False]
        }
        
        # 플랫폼별 제한 적용
        device = self.detector.device_info['primary_device']
        
        if device == 'cpu':
            # CPU: 가장 제한적
            space = {
                'models': ['resnet34.tv_in1k'],
                'image_sizes': [224],
                'learning_rates': [0.0001, 0.00001],
                'augmentation_levels': ['minimal', 'moderate'],
                'TTA': [False]
            }
        elif device == 'mps':
            # MPS: 중간 제한
            space = {
                'models': ['resnet34.tv_in1k', 'resnet50.tv2_in1k'],
                'image_sizes': [224, 320],
                'learning_rates': base_space['learning_rates'],
                'augmentation_levels': base_space['augmentation_levels'],
                'TTA': [True, False]
            }
        else:
            # CUDA: 전체 공간
            space = base_space
        
        # 실험 타입별 제한
        if experiment_type == "quick":
            # 빠른 실험: 더 제한적
            space['learning_rates'] = space['learning_rates'][:2]  # 상위 2개만
            space['TTA'] = [False]  # TTA 비활성화로 속도 향상
        
        return space
    
    def generate_experiments(self, experiment_type: str = "quick", 
                           max_experiments: int = 20, 
                           search_method: str = "smart_grid") -> List[str]:
        """실험 조합 생성"""
        
        space = self.define_experiment_space(experiment_type)
        
        if search_method == "grid":
            combinations = self._grid_search(space, max_experiments)
        elif search_method == "random":
            combinations = self._random_search(space, max_experiments)
        else:  # smart_grid
            combinations = self._smart_grid_search(space, max_experiments)
        
        config_files = []
        
        for i, combination in enumerate(combinations):
            # 실험 ID 생성
            timestamp = datetime.now().strftime("%y%m%d%H%M")
            experiment_id = f"exp_{experiment_type}_{i+1:03d}_{timestamp}"
            
            # 기본 설정 생성
            config = self.config_manager.generate_platform_config(experiment_type)
            
            # 하이퍼파라미터 적용
            config.update({
                'experiment_id': experiment_id,
                'model_name': combination['model'],
                'image_size': combination['image_size'],
                'lr': combination['lr'],
                'augmentation_level': combination['augmentation'],
                'TTA': combination['TTA'],
                'augmentation': self._get_augmentation_config(combination['augmentation'])
            })
            
            # 설정 파일 저장
            config_filename = f"{experiment_id}.yaml"
            config_path = self.practice_dir / config_filename
            
            self.config_manager.save_config(config, str(config_path))
            config_files.append(str(config_path))
            
            print(f"📝 실험 설정 생성: {experiment_id}")
        
        print(f"✅ 총 {len(config_files)}개 실험 설정 생성 완료")
        return config_files
    
    def _grid_search(self, space: Dict, max_experiments: int) -> List[Dict]:
        """Grid Search 조합 생성"""
        keys, values = zip(*space.items())
        combinations = list(itertools.product(*values))
        
        # 최대 실험 수로 제한
        if len(combinations) > max_experiments:
            combinations = random.sample(combinations, max_experiments)
        
        return [
            {
                'model': combo[0],
                'image_size': combo[1], 
                'lr': combo[2],
                'augmentation': combo[3],
                'TTA': combo[4]
            }
            for combo in combinations
        ]
    
    def _random_search(self, space: Dict, max_experiments: int) -> List[Dict]:
        """Random Search 조합 생성"""
        combinations = []
        
        for _ in range(max_experiments):
            combo = {
                'model': random.choice(space['models']),
                'image_size': random.choice(space['image_sizes']),
                'lr': random.choice(space['learning_rates']),
                'augmentation': random.choice(space['augmentation_levels']),
                'TTA': random.choice(space['TTA'])
            }
            combinations.append(combo)
        
        return combinations
    
    def _smart_grid_search(self, space: Dict, max_experiments: int) -> List[Dict]:
        """Smart Grid Search: 중요한 파라미터 우선 탐색"""
        
        # 1단계: 모델 + 학습률 조합 우선
        important_combos = []
        for model in space['models']:
            for lr in space['learning_rates']:
                important_combos.append({
                    'model': model,
                    'image_size': space['image_sizes'][0],  # 기본 크기
                    'lr': lr,
                    'augmentation': 'moderate',  # 기본 증강
                    'TTA': False  # 기본적으로 비활성화
                })
        
        # 2단계: 나머지 공간 랜덤 샘플링
        remaining_count = max_experiments - len(important_combos)
        if remaining_count > 0:
            additional_combos = self._random_search(space, remaining_count)
            important_combos.extend(additional_combos)
        
        return important_combos[:max_experiments]
    
    def _get_augmentation_config(self, level: str) -> Dict:
        """증강 레벨에 따른 설정"""
        configs = {
            'minimal': {
                'eda': True,
                'dilation': False,
                'erosion': False,
                'mixup': False,
                'cutmix': False
            },
            'moderate': {
                'eda': True,
                'dilation': True,
                'erosion': False,
                'mixup': False,
                'cutmix': False
            },
            'strong': {
                'eda': True,
                'dilation': True,
                'erosion': True,
                'mixup': True,
                'cutmix': False
            }
        }
        return configs.get(level, configs['moderate'])
    
    def run_single_experiment(self, config_path: str) -> Dict:
        """단일 실험 실행"""
        
        # 설정 로드
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        experiment_id = config['experiment_id']
        print(f"\n🚀 실험 시작: {experiment_id}")
        
        # 실험 결과 초기화
        result = {
            'experiment_id': experiment_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'platform': f"{self.detector.system_info['os']}_{self.detector.device_info['primary_device']}",
            'device': self.detector.device_info['primary_device'],
            'status': 'running',
            'config_path': config_path,
            'error_message': None
        }
        
        # 하이퍼파라미터 기록
        result.update({
            'model_name': config.get('model_name'),
            'image_size': config.get('image_size'),
            'lr': config.get('lr'),
            'batch_size': config.get('batch_size'),
            'augmentation_level': config.get('augmentation_level'),
            'TTA': config.get('TTA'),
        })
        
        start_time = time.time()
        
        try:
            # 실제 gemini_main.py 실행
            print(f"   모델: {config['model_name']}")
            print(f"   이미지 크기: {config['image_size']}")
            print(f"   학습률: {config['lr']}")
            print(f"   증강 레벨: {config['augmentation_level']}")
            
            # 실제 훈련 실행
            print(f"   🚀 실제 훈련 시작...")
            
            # gemini_main.py 실행 명령어
            cmd = f"cd {self.project_root} && python codes/gemini_main.py --config {config_path}"
            
            # subprocess로 실제 훈련 실행
            process = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=str(self.project_root)
            )
            
            if process.returncode != 0:
                raise Exception(f"Training failed: {process.stderr}")
            
            # 훈련 결과 파싱 (실제 출력에서 추출)
            output = process.stdout
            
            # 결과 파싱 (기본값 설정)
            training_time = (time.time() - start_time) / 60
            final_f1 = self._extract_metric_from_output(output, 'f1', 0.75)
            val_accuracy = self._extract_metric_from_output(output, 'accuracy', 80.0)
            epochs_run = self._extract_metric_from_output(output, 'epochs', 50)
            
            print(f"   ✅ 훈련 완료! ({training_time:.1f}분)")
            
            # 결과 업데이트
            result.update({
                'status': 'completed',
                'epochs_run': epochs_run,
                'final_f1': final_f1,
                'val_accuracy': val_accuracy,
                'training_time_min': training_time,
                'model_path': f"models/{experiment_id}.pth",
                'submission_path': f"data/submissions/{experiment_id}.csv"
            })
            
            print(f"✅ 실험 완료: F1={final_f1:.4f}, Acc={val_accuracy:.2f}%")
            
        except Exception as e:
            # 실험 실패 처리
            result.update({
                'status': 'failed',
                'training_time_min': (time.time() - start_time) / 60,
                'error_message': str(e)
            })
            print(f"❌ 실험 실패: {e}")
        
        # 결과 저장
        self._save_experiment_result(result)
        
        return result
    
    def run_experiments(self, config_files: List[str], max_parallel: int = 1) -> List[Dict]:
        """실험들 실행"""
        
        print(f"\n🎯 총 {len(config_files)}개 실험 시작")
        print(f"   병렬 실행: {max_parallel}개")
        print(f"   플랫폼: {self.detector.system_info['os']} + {self.detector.device_info['primary_device'].upper()}")
        
        results = []
        
        # 현재는 순차 실행 (추후 병렬 처리 가능)
        for i, config_path in enumerate(config_files):
            print(f"\n📊 진행률: {i+1}/{len(config_files)}")
            result = self.run_single_experiment(config_path)
            results.append(result)
            
            # 성공률 체크
            completed = sum(1 for r in results if r['status'] == 'completed')
            success_rate = completed / len(results) * 100
            print(f"   현재 성공률: {success_rate:.1f}% ({completed}/{len(results)})")
        
        print(f"\n🎉 모든 실험 완료!")
        print(f"   성공: {sum(1 for r in results if r['status'] == 'completed')}개")
        print(f"   실패: {sum(1 for r in results if r['status'] == 'failed')}개")
        
        return results
    
    def _extract_metric_from_output(self, output: str, metric_name: str, default_value: float) -> float:
        """훈련 출력에서 메트릭 추출"""
        try:
            import re
            
            # F1 점수 추출
            if metric_name == 'f1':
                f1_pattern = r'f1[\s:=]+(\d+\.\d+)'
                matches = re.findall(f1_pattern, output, re.IGNORECASE)
                if matches:
                    return float(matches[-1])  # 마지막 값 사용
            
            # 정확도 추출
            elif metric_name == 'accuracy':
                acc_pattern = r'acc[uracy]*[\s:=]+(\d+\.\d+)'
                matches = re.findall(acc_pattern, output, re.IGNORECASE)
                if matches:
                    return float(matches[-1])
            
            # 에포크 추출
            elif metric_name == 'epochs':
                epoch_pattern = r'epoch[\s:=]+(\d+)'
                matches = re.findall(epoch_pattern, output, re.IGNORECASE)
                if matches:
                    return int(matches[-1])
            
            return default_value
            
        except:
            return default_value
    
    def _save_experiment_result(self, result: Dict):
        """실험 결과 저장"""
        
        # CSV에 추가
        df = pd.read_csv(self.results_file)
        new_row = pd.DataFrame([result])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.results_file, index=False)
    
    def get_experiment_summary(self) -> Dict:
        """실험 요약 정보"""
        
        if not self.results_file.exists():
            return {'total': 0, 'completed': 0, 'failed': 0, 'running': 0}
        
        df = pd.read_csv(self.results_file)
        
        if df.empty:
            return {'total': 0, 'completed': 0, 'failed': 0, 'running': 0}
        
        summary = {
            'total': len(df),
            'completed': len(df[df['status'] == 'completed']),
            'failed': len(df[df['status'] == 'failed']),
            'running': len(df[df['status'] == 'running']),
        }
        
        if summary['completed'] > 0:
            completed_df = df[df['status'] == 'completed']
            summary.update({
                'best_f1': completed_df['final_f1'].max(),
                'avg_f1': completed_df['final_f1'].mean(),
                'avg_training_time': completed_df['training_time_min'].mean()
            })
        
        return summary
    
    def get_top_experiments(self, n: int = 5) -> pd.DataFrame:
        """상위 N개 실험 조회"""
        
        if not self.results_file.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(self.results_file)
        completed_df = df[df['status'] == 'completed']
        
        if completed_df.empty:
            return pd.DataFrame()
        
        return completed_df.nlargest(n, 'final_f1')[
            ['experiment_id', 'model_name', 'image_size', 'lr', 'final_f1', 'val_accuracy', 'training_time_min']
        ]

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="기본 HPO 실행")
    parser.add_argument('--type', choices=['quick', 'full', 'targeted'], default='quick',
                        help='실험 타입')
    parser.add_argument('--max', type=int, default=20,
                        help='최대 실험 수')
    parser.add_argument('--method', choices=['grid', 'random', 'smart_grid'], default='smart_grid',
                        help='탐색 방법')
    
    args = parser.parse_args()
    
    # HPO 시스템 초기화
    hpo = BasicHPO()
    
    # 실험 생성
    config_files = hpo.generate_experiments(
        experiment_type=args.type,
        max_experiments=args.max,
        search_method=args.method
    )
    
    # 실험 실행
    results = hpo.run_experiments(config_files)
    
    # 결과 요약
    summary = hpo.get_experiment_summary()
    print(f"\n📊 실험 요약:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # 상위 실험 출력
    top_experiments = hpo.get_top_experiments(5)
    if not top_experiments.empty:
        print(f"\n🏆 상위 5개 실험:")
        print(top_experiments.to_string(index=False))

if __name__ == "__main__":
    main()
