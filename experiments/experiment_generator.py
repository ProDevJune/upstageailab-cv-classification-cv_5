#!/usr/bin/env python3
"""
실험 매트릭스 생성기 (OCR 지원 버전)
experiment_matrix.yaml을 읽어 모델×기법×OCR 조합을 생성하고
각 실험별 설정 파일을 자동 생성합니다.
"""

import os
import sys
import yaml
import itertools
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExperimentConfig:
    """단일 실험 설정을 담는 데이터 클래스"""
    experiment_id: str
    model_name: str
    technique_name: str
    ocr_option: str
    config_path: str
    priority_score: float
    estimated_time_minutes: int
    description: str
    ocr_enabled: bool


class ExperimentGenerator:
    """실험 매트릭스 생성 및 관리 클래스 (OCR 지원)"""
    
    def __init__(self, matrix_file: str):
        self.matrix_file = matrix_file
        self.base_dir = Path(matrix_file).parent.parent
        self.matrix_data = self._load_matrix()
        self.experiments = []
        
    def _load_matrix(self) -> Dict:
        """매트릭스 YAML 파일 로드"""
        try:
            with open(self.matrix_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"매트릭스 파일 로드 실패: {e}")
    
    def _load_base_config(self) -> Dict:
        """기본 config_v2.yaml 파일 로드"""
        base_config_path = self.matrix_data['global_settings']['base_config_path']
        try:
            with open(base_config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"기본 설정 파일 로드 실패: {e}")
    
    def _calculate_priority_score(self, model_info: Dict, technique_info: Dict, ocr_info: Dict) -> float:
        """실험 우선순위 점수 계산 (OCR 차원 추가)"""
        weights = self.matrix_data['priority_weights']
        
        # 우선순위가 낮을수록 점수가 높음 (1이 최고 우선순위)
        model_score = (5 - model_info['priority']) / 4.0
        technique_score = (7 - technique_info['priority']) / 6.0
        ocr_score = (3 - ocr_info['priority']) / 2.0  # OCR 우선순위
        time_score = max(0, (120 - model_info['estimated_time_minutes'] * ocr_info['time_multiplier']) / 120)
        
        total_score = (
            model_score * weights['model_priority'] +
            technique_score * weights['technique_priority'] +
            ocr_score * weights['ocr_priority'] +
            time_score * weights['estimated_time']
        )
        
        # OCR 우선순위 부스트 적용
        if ocr_info['enabled']:
            boost = self.matrix_data['experiment_options'].get('ocr_priority_boost', 0.0)
            total_score += boost
        
        return round(total_score, 3)
    
    def _create_experiment_config(self, model_key: str, technique_key: str, ocr_key: str,
                                model_info: Dict, technique_info: Dict, ocr_info: Dict) -> Dict:
        """개별 실험용 설정 파일 내용 생성 (OCR 설정 포함)"""
        base_config = self._load_base_config()
        
        # 모델 설정 업데이트
        base_config['model_name'] = model_info['model_name']
        base_config['batch_size'] = model_info['batch_size']
        base_config['image_size'] = model_info['image_size']
        
        # 기법 설정 업데이트
        base_config['criterion'] = technique_info['criterion']
        
        # MixUp/CutMix 설정
        if 'mixup_cutmix_prob' in technique_info:
            base_config['mixup_cutmix']['prob'] = technique_info['mixup_cutmix_prob']
            # prob가 0이면 mixup, cutmix 비활성화
            if technique_info['mixup_cutmix_prob'] == 0.0:
                base_config['augmentation']['mixup'] = False
                base_config['augmentation']['cutmix'] = False
            else:
                base_config['augmentation']['mixup'] = True
                base_config['augmentation']['cutmix'] = True
        
        # Focal Loss 설정
        if 'focal_loss' in technique_info:
            base_config['focal_loss'] = technique_info['focal_loss']
        
        # Label Smoothing 설정
        if 'label_smoothing' in technique_info:
            base_config['label_smoothing'] = technique_info['label_smoothing']
        
        # 🔥 OCR 설정 추가
        base_config['ocr'] = {
            'enabled': ocr_info['enabled'],
            'description': ocr_info['description']
        }
        
        if ocr_info['enabled'] and 'ocr_config' in ocr_info:
            base_config['ocr'].update(ocr_info['ocr_config'])
            
            # OCR 관련 데이터 경로 설정
            global_settings = self.matrix_data['global_settings']
            base_config['ocr']['data_path'] = global_settings.get('ocr_data_path', '')
            base_config['ocr']['features_path'] = global_settings.get('ocr_features_path', '')
        
        # W&B 프로젝트명 업데이트 (OCR 포함)
        experiment_id = f"exp_{model_key}_{technique_key}_{ocr_key}"
        base_config['wandb']['project'] = f"auto-exp-ocr-{experiment_id}"
        
        return base_config
    
    def _should_generate_ocr_experiment(self, technique_key: str) -> bool:
        """특정 기법에 대해 OCR 실험을 생성할지 결정"""
        exp_options = self.matrix_data['experiment_options']
        mode = exp_options.get('ocr_experiment_mode', 'selective')
        
        if mode == 'all':
            return True
        elif mode == 'selective':
            selective_techniques = exp_options.get('ocr_selective_techniques', [])
            return technique_key in selective_techniques
        else:  # mode == 'none'
            return False
    
    def generate_experiments(self) -> List[ExperimentConfig]:
        """모든 모델×기법×OCR 조합에 대한 실험 생성"""
        models = self.matrix_data['models']
        techniques = self.matrix_data['techniques']
        ocr_options = self.matrix_data['ocr_options']
        output_dir = Path(self.matrix_data['global_settings']['output_dir'])
        
        experiments = []
        experiment_counter = 1
        
        print(f"🔬 OCR 지원 실험 매트릭스 생성 중...")
        print(f"   모델: {len(models)}개, 기법: {len(techniques)}개, OCR 옵션: {len(ocr_options)}개")
        
        # OCR 실험 모드 확인
        exp_mode = self.matrix_data['experiment_options'].get('ocr_experiment_mode', 'selective')
        print(f"   OCR 실험 모드: {exp_mode}")
        
        # 총 실험 수 계산
        total_experiments = 0
        for technique_key in techniques.keys():
            if exp_mode == 'all':
                total_experiments += len(models) * len(ocr_options)
            elif exp_mode == 'selective' and self._should_generate_ocr_experiment(technique_key):
                total_experiments += len(models) * len(ocr_options)
            elif exp_mode == 'none' or not self._should_generate_ocr_experiment(technique_key):
                total_experiments += len(models) * 1  # OCR 없음만
        
        print(f"   총 실험 수: {total_experiments}개")
        print()
        
        for model_key, model_info in models.items():
            for technique_key, technique_info in techniques.items():
                
                # OCR 실험 생성 여부 결정
                if self._should_generate_ocr_experiment(technique_key):
                    # OCR 적용/미적용 둘 다 생성
                    ocr_variants = ocr_options.items()
                else:
                    # OCR 미적용만 생성
                    ocr_variants = [('no_ocr', ocr_options['no_ocr'])]
                
                for ocr_key, ocr_info in ocr_variants:
                    # 실험 ID 생성
                    if ocr_info['enabled']:
                        experiment_id = f"exp_{model_key}_{technique_key}_ocr_{experiment_counter:03d}"
                    else:
                        experiment_id = f"exp_{model_key}_{technique_key}_noocr_{experiment_counter:03d}"
                    
                    # 설정 파일 생성
                    config_content = self._create_experiment_config(
                        model_key, technique_key, ocr_key, model_info, technique_info, ocr_info
                    )
                    
                    # 설정 파일 저장
                    config_filename = f"{experiment_id}.yaml"
                    config_path = output_dir / config_filename
                    
                    with open(config_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config_content, f, default_flow_style=False, allow_unicode=True)
                    
                    # 우선순위 점수 계산
                    priority_score = self._calculate_priority_score(model_info, technique_info, ocr_info)
                    
                    # 예상 시간 계산 (OCR 시간 승수 적용)
                    estimated_time = int(model_info['estimated_time_minutes'] * ocr_info['time_multiplier'])
                    
                    # 설명 생성
                    ocr_desc = " + OCR" if ocr_info['enabled'] else ""
                    description = f"{model_info['model_name']} + {technique_info['description']}{ocr_desc}"
                    
                    # 실험 설정 객체 생성
                    experiment = ExperimentConfig(
                        experiment_id=experiment_id,
                        model_name=model_key,
                        technique_name=technique_key,
                        ocr_option=ocr_key,
                        config_path=str(config_path),
                        priority_score=priority_score,
                        estimated_time_minutes=estimated_time,
                        description=description,
                        ocr_enabled=ocr_info['enabled']
                    )
                    
                    experiments.append(experiment)
                    experiment_counter += 1
                    
                    ocr_status = "🔤 OCR" if ocr_info['enabled'] else "📷 No-OCR"
                    print(f"✅ {experiment_id}")
                    print(f"   {description}")
                    print(f"   📁 {config_filename}")
                    print(f"   {ocr_status} ⭐ 우선순위: {priority_score:.3f}, ⏱️ 예상시간: {estimated_time}분")
                    print()
        
        # 우선순위 순으로 정렬
        experiments.sort(key=lambda x: x.priority_score, reverse=True)
        
        return experiments
    
    def save_experiment_queue(self, experiments: List[ExperimentConfig]) -> str:
        """실험 큐를 JSON 파일로 저장"""
        queue_data = {
            'generated_at': datetime.now().isoformat(),
            'total_experiments': len(experiments),
            'ocr_experiments': len([exp for exp in experiments if exp.ocr_enabled]),
            'no_ocr_experiments': len([exp for exp in experiments if not exp.ocr_enabled]),
            'estimated_total_time_hours': sum(exp.estimated_time_minutes for exp in experiments) / 60,
            'experiments': []
        }
        
        for i, exp in enumerate(experiments):
            queue_data['experiments'].append({
                'queue_position': i + 1,
                'experiment_id': exp.experiment_id,
                'model_name': exp.model_name,
                'technique_name': exp.technique_name,
                'ocr_option': exp.ocr_option,
                'ocr_enabled': exp.ocr_enabled,
                'config_path': exp.config_path,
                'priority_score': exp.priority_score,
                'estimated_time_minutes': exp.estimated_time_minutes,
                'description': exp.description,
                'status': 'pending'
            })
        
        # 큐 파일 저장
        queue_file = self.base_dir / "experiments" / "experiment_queue.json"
        import json
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue_data, f, indent=2, ensure_ascii=False)
        
        return str(queue_file)
    
    def print_summary(self, experiments: List[ExperimentConfig]):
        """실험 생성 요약 출력 (OCR 정보 포함)"""
        total_time = sum(exp.estimated_time_minutes for exp in experiments)
        ocr_experiments = [exp for exp in experiments if exp.ocr_enabled]
        no_ocr_experiments = [exp for exp in experiments if not exp.ocr_enabled]
        
        print("=" * 80)
        print("🎯 OCR 지원 실험 매트릭스 생성 완료!")
        print("=" * 80)
        print(f"📊 총 실험 수: {len(experiments)}개")
        print(f"🔤 OCR 적용 실험: {len(ocr_experiments)}개")
        print(f"📷 OCR 미적용 실험: {len(no_ocr_experiments)}개")
        print(f"⏱️  예상 총 소요시간: {total_time // 60}시간 {total_time % 60}분")
        print(f"🚀 최고 우선순위: {experiments[0].experiment_id}")
        print(f"   - {experiments[0].description}")
        print(f"   - 우선순위 점수: {experiments[0].priority_score:.3f}")
        print()
        
        # 모델별 실험 수
        model_counts = {}
        for exp in experiments:
            model_counts[exp.model_name] = model_counts.get(exp.model_name, 0) + 1
        
        print("📈 모델별 실험 수:")
        for model, count in model_counts.items():
            print(f"   - {model}: {count}개")
        print()
        
        # OCR별 실험 수
        print("🔤 OCR별 실험 수:")
        print(f"   - OCR 적용: {len(ocr_experiments)}개")
        print(f"   - OCR 미적용: {len(no_ocr_experiments)}개")
        print()
        
        # TOP 5 우선순위 실험
        print("🏆 TOP 5 우선순위 실험:")
        for i, exp in enumerate(experiments[:5]):
            ocr_icon = "🔤" if exp.ocr_enabled else "📷"
            print(f"   {i+1}. {ocr_icon} {exp.experiment_id}")
            print(f"      {exp.description}")
            print(f"      우선순위: {exp.priority_score:.3f}, 예상시간: {exp.estimated_time_minutes}분")
            print()


def main():
    parser = argparse.ArgumentParser(description='OCR 지원 실험 매트릭스 생성기')
    parser.add_argument('--matrix', '-m', 
                       default='experiments/experiment_matrix.yaml',
                       help='실험 매트릭스 YAML 파일 경로')
    parser.add_argument('--dry-run', action='store_true',
                       help='실제 파일 생성 없이 시뮬레이션만 실행')
    parser.add_argument('--ocr-mode', choices=['all', 'selective', 'none'],
                       help='OCR 실험 생성 모드 (매트릭스 파일 설정 오버라이드)')
    
    args = parser.parse_args()
    
    try:
        # 실험 생성기 초기화
        generator = ExperimentGenerator(args.matrix)
        
        # OCR 모드 오버라이드
        if args.ocr_mode:
            generator.matrix_data['experiment_options']['ocr_experiment_mode'] = args.ocr_mode
            print(f"🔧 OCR 모드 오버라이드: {args.ocr_mode}")
            print()
        
        if args.dry_run:
            print("🧪 DRY RUN 모드: 실제 파일을 생성하지 않습니다.")
            print()
        
        # 실험 생성
        experiments = generator.generate_experiments()
        
        if not args.dry_run:
            # 실험 큐 저장
            queue_file = generator.save_experiment_queue(experiments)
            print(f"💾 실험 큐 저장: {queue_file}")
            print()
        
        # 요약 출력
        generator.print_summary(experiments)
        
        if not args.dry_run:
            print("🎉 OCR 지원 실험 매트릭스 생성이 완료되었습니다!")
            print("   다음 명령어로 자동 실험을 시작할 수 있습니다:")
            print("   $ python experiments/auto_experiment_runner.py")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
