#!/usr/bin/env python3
"""
간단한 테스트 실험 실행기
실제 긴 실험 전에 빠른 테스트로 모든 것이 정상 작동하는지 확인
"""

import sys
import os
import yaml
import tempfile
import subprocess
import time
from pathlib import Path
from datetime import datetime

class QuickTestRunner:
    """빠른 테스트 실험 실행기"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []
        
    def create_test_config(self, model_name: str, category: str) -> str:
        """테스트용 설정 파일 생성 (매우 짧은 실행 시간)"""
        
        # 기본 설정 로드 - 실제 config.yaml을 기반으로 함
        base_config_path = self.project_root / "codes/config.yaml"
        
        try:
            with open(base_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ config.yaml 로드 실패: {e}")
            # 최소한의 기본 설정
            config = {
                'model_name': 'resnet50.tv2_in1k',
                'pretrained': True,
                'fine_tuning': 'full',
                'criterion': 'CrossEntropyLoss',
                'optimizer_name': 'AdamW',
                'lr': 0.0001,
                'weight_decay': 0.00001,
                'scheduler_name': 'CosineAnnealingLR',
                'random_seed': 256,
                'n_folds': 0,
                'val_split_ratio': 0.15,
                'stratify': True,
                'image_size': 224,
                'norm_mean': [0.5, 0.5, 0.5],
                'norm_std': [0.5, 0.5, 0.5],
                'class_imbalance': {'aug_class': [1, 13, 14], 'max_samples': 78},
                'online_augmentation': True,
                'augmentation': {'eda': True, 'dilation': True, 'erosion': False, 'mixup': False, 'cutmix': False},
                'TTA': True,
                'mixed_precision': True,
                'timm': {'activation': None},
                'custom_layer': {},
                'epochs': 10000,
                'patience': 20,
                'batch_size': 32,
                'wandb': {'project': 'upstage-img-clf', 'log': True},
                'data_dir': '/data/ephemeral/home/upstageailab-cv-classification-cv_5/data',
                'train_data': 'train0705a.csv'
            }
        
        # 테스트용으로 수정할 설정들만 오버라이드 (실제 설정은 그대로 유지)
        test_overrides = {
            'model_name': model_name,  # 테스트할 모델로 변경
            'epochs': 1,  # 1 에포크만 테스트
            'batch_size': 4,  # 작은 배치 (너무 작으면 에러 발생 가능)
            'image_size': 128,  # 작은 이미지 크기 (64는 너무 작을 수 있음)
            'patience': 1,  # 조기 종료 빠르게
            'wandb': {'project': 'test-run', 'log': False},  # WandB 비활성화
            'val_split_ratio': 0.95,  # 훈련 95%, 검증 5% (빠른 테스트)
            'mixed_precision': False,  # 안정성 우선
            'class_imbalance': False,  # 복잡한 증강 비활성화
            'online_augmentation': False,  # 온라인 증강 비활성화
            'dynamic_augmentation': {'enabled': False},  # 동적 증강 비활성화
            'augmentation': {
                'eda': False,
                'dilation': False, 
                'erosion': False,
                'mixup': False,
                'cutmix': False
            },
            'TTA': False,  # TTA 비활성화
            'val_TTA': False,  # validation TTA 비활성화
            'test_TTA': False,  # test TTA 비활성화
            'weighted_random_sampler': False,  # weighted sampler 비활성화
            'custom_layer': {'drop': 0.2, 'activation': 'ReLU', 'head_type': 'complex'},  # custom layer 설정
            'scheduler_params': {'T_max': 100, 'min_lr': 0, 'max_lr': 0.01, 'step_size': 50, 'gamma': 0.1, 'factor': 0.1},  # scheduler 파라미터
            'tta_dropout': False,  # TTA dropout 비활성화
            'data_dir': './data',  # 상대 경로로 변경
            'train_data': 'train0705a.csv',  # 훈련 데이터 파일명
            'experiment_id': f"test_{category}_{model_name.replace('.', '_')}_{datetime.now().strftime('%H%M%S')}"
        }
        
        # 기본 설정을 테스트 설정으로 업데이트
        config.update(test_overrides)
        
        # 카테고리별 테스트 설정
        if category == 'optimizer':
            config['optimizer_name'] = 'SGD'
            config['lr'] = 0.01
        elif category == 'loss_function':
            config['criterion'] = 'CrossEntropyLoss'
        elif category == 'scheduler':
            config['scheduler_name'] = 'StepLR'
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f, default_flow_style=False)
            return f.name
    
    def run_quick_test(self, model_name: str, category: str) -> dict:
        """빠른 테스트 실험 실행"""
        
        print(f"\n🧪 테스트 실험: {model_name} + {category}")
        print("-" * 50)
        
        result = {
            'model': model_name,
            'category': category,
            'status': 'running',
            'start_time': datetime.now(),
            'error': None,
            'execution_time': 0
        }
        
        try:
            # 테스트 설정 파일 생성
            test_config_path = self.create_test_config(model_name, category)
            print(f"   📄 테스트 설정: {test_config_path}")
            
            # PYTHONPATH에 프로젝트 루트 추가 (환경변수)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root) + ':' + env.get('PYTHONPATH', '')
            
            # 실행 명령 결정
            if model_name == 'resnet50.tv2_in1k':
                cmd = ['python', 'codes/gemini_main_v2.py', '--config', test_config_path]
            else:
                # 다른 모델들은 gemini_main_v2.py 사용
                cmd = ['python', 'codes/gemini_main_v2.py', '--config', test_config_path]
            
            print(f"   🔧 실행 명령: {' '.join(cmd)}")
            print(f"   ⏳ 테스트 실행 중... (1-3분 예상)")
            
            # 실험 실행
            start_time = time.time()
            process = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=600,  # 10분 타임아웃으로 늘림
                env=env  # 수정된 환경변수 사용
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            result['execution_time'] = execution_time
            
            if process.returncode == 0:
                print(f"   ✅ 테스트 성공! ({execution_time:.1f}초)")
                result['status'] = 'success'
            else:
                print(f"   ❌ 테스트 실패 (코드: {process.returncode})")
                result['status'] = 'failed'
                # 전체 오류 메시지 표시
                full_error = process.stderr if process.stderr else process.stdout
                result['error'] = full_error
                print(f"   🚨 전체 오류 메시지:")
                print(f"   {full_error}")
                
                # 오류를 파일로도 저장
                error_file = f"/tmp/test_error_{model_name.replace('.', '_')}_{category}.log"
                with open(error_file, 'w') as f:
                    f.write(f"명령: {' '.join(cmd)}\n")
                    f.write(f"STDOUT:\n{process.stdout}\n")
                    f.write(f"STDERR:\n{process.stderr}\n")
                print(f"   📄 상세 오류 로그: {error_file}")
            
            # 임시 파일 정리
            try:
                os.unlink(test_config_path)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
            result['error'] = '테스트 시간 초과 (5분)'
            print(f"   ⏰ 테스트 시간 초과")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"   ❌ 테스트 오류: {e}")
        
        return result
    
    def run_comprehensive_test(self) -> bool:
        """포괄적인 빠른 테스트"""
        
        print("🧪 빠른 테스트 실험 시스템")
        print("=" * 60)
        print("🧪 빠른 테스트 실험 시작")
        print("=" * 60)
        print("ℹ️ 실제 긴 실험 전에 모든 컴포넌트가 정상 작동하는지 확인합니다.")
        print("⏱️ 각 테스트는 1-3분 소요되며, 전체 테스트는 5-10분 예상됩니다.")
        
        # 테스트할 조합들 (대표적인 것들만)
        test_combinations = [
            ('resnet50.tv2_in1k', 'optimizer'),
            ('efficientnet_b4.ra2_in1k', 'loss_function'),
            ('efficientnet_b3.ra2_in1k', 'scheduler'),
        ]
        
        all_tests_passed = True
        
        for model, category in test_combinations:
            result = self.run_quick_test(model, category)
            self.test_results.append(result)
            
            if result['status'] != 'success':
                all_tests_passed = False
        
        # 결과 요약
        print(f"\n📊 테스트 결과 요약")
        print("=" * 40)
        
        successful_tests = [r for r in self.test_results if r['status'] == 'success']
        failed_tests = [r for r in self.test_results if r['status'] != 'success']
        
        print(f"   성공: {len(successful_tests)}/{len(self.test_results)}개")
        print(f"   평균 실행 시간: {sum(r['execution_time'] for r in successful_tests) / len(successful_tests):.1f}초" if successful_tests else "   평균 실행 시간: N/A")
        
        if failed_tests:
            print(f"\n❌ 실패한 테스트들:")
            for test in failed_tests:
                print(f"   • {test['model']} + {test['category']}: {test['error'][:50]}...")
        
        if all_tests_passed:
            print(f"\n🎊 모든 테스트 통과! 본격적인 실험 실행 가능")
            return True
        else:
            print(f"\n⚠️ 일부 테스트 실패. 문제 해결 후 재시도 필요")
            return False
    
    def estimate_full_experiment_time(self) -> dict:
        """전체 실험 시간 추정"""
        
        if not self.test_results:
            return {'error': '테스트 결과가 없습니다'}
        
        successful_tests = [r for r in self.test_results if r['status'] == 'success']
        if not successful_tests:
            return {'error': '성공한 테스트가 없습니다'}
        
        # 평균 테스트 시간 (1 에포크)
        avg_test_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
        
        # 실제 실험 시간 추정 (50 에포크 기준)
        estimated_time_per_experiment = avg_test_time * 50
        
        # 전체 실험 수 추정 (4모델 × 6카테고리 × 평균 2.5옵션)
        total_experiments = 4 * 6 * 2.5
        total_estimated_time = estimated_time_per_experiment * total_experiments
        
        return {
            'test_time_per_epoch': avg_test_time,
            'estimated_time_per_experiment': estimated_time_per_experiment / 60,  # 분
            'total_experiments': total_experiments,
            'total_estimated_hours': total_estimated_time / 3600,
            'total_estimated_days': total_estimated_time / (3600 * 24)
        }

def main():
    """메인 실행 함수"""
    
    print("🧪 빠른 테스트 실험 시스템")
    print("=" * 50)
    
    runner = QuickTestRunner()
    
    # 빠른 테스트 실행
    success = runner.run_comprehensive_test()
    
    if success:
        # 전체 실험 시간 추정
        estimation = runner.estimate_full_experiment_time()
        
        if 'error' not in estimation:
            print(f"\n⏱️ 전체 실험 시간 추정:")
            print(f"   실험당 예상 시간: {estimation['estimated_time_per_experiment']:.1f}분")
            print(f"   총 실험 수: {estimation['total_experiments']:.0f}개")
            print(f"   총 예상 시간: {estimation['total_estimated_hours']:.1f}시간 ({estimation['total_estimated_days']:.1f}일)")
        
        print(f"\n🚀 실제 실험 실행 준비 완료!")
        print(f"   python hyperparameter_system/run_experiments.py")
        
        return 0
    else:
        print(f"\n❌ 테스트 실패. 문제 해결 후 재시도하세요.")
        return 1

if __name__ == "__main__":
    exit(main())
