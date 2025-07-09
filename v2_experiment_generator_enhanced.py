#!/usr/bin/env python3
"""
Enhanced V2 Experiment Generator
V2 단일 모델 분류 시스템을 위한 확장된 자동 실험 config 생성기
"""

import os
import yaml
import argparse
import itertools
from pathlib import Path
import json
import copy
from datetime import datetime

class EnhancedV2ExperimentGenerator:
    def __init__(self, matrix_file="v2_experiment_matrix.yaml", output_dir="v2_experiments"):
        self.matrix_file = matrix_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 서브 디렉토리 생성
        (self.output_dir / "configs").mkdir(exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        # 확장된 매트릭스 시도
        self.load_enhanced_matrix()
        
        self.load_matrix()
        self.load_base_configs()
        
    def load_enhanced_matrix(self):
        """확장된 실험 매트릭스 로드"""
        enhanced_matrix_file = "v2_experiment_matrix_enhanced.yaml"
        if os.path.exists(enhanced_matrix_file):
            print(f"📊 확장된 실험 매트릭스 사용: {enhanced_matrix_file}")
            self.matrix_file = enhanced_matrix_file
            return True
        else:
            print(f"⚠️ 확장된 매트릭스 파일을 찾을 수 없습니다: {enhanced_matrix_file}")
            print(f"🔄 기본 매트릭스 사용: {self.matrix_file}")
            return False
    
    def load_matrix(self):
        """매트릭스 파일 로드"""
        try:
            with open(self.matrix_file, 'r', encoding='utf-8') as f:
                self.matrix = yaml.safe_load(f)
            print(f"✅ 매트릭스 로드 완료: {self.matrix_file}")
        except Exception as e:
            print(f"❌ 매트릭스 로드 실패: {e}")
            raise
    
    def load_base_configs(self):
        """기본 설정 파일들 로드"""
        try:
            # V2_1 기본 설정
            with open('codes/config_v2_1.yaml', 'r', encoding='utf-8') as f:
                self.base_config_v2_1 = yaml.safe_load(f)
            
            # V2_2 기본 설정  
            with open('codes/config_v2_2.yaml', 'r', encoding='utf-8') as f:
                self.base_config_v2_2 = yaml.safe_load(f)
            
            print("✅ 기본 설정 파일 로드 완료")
        except Exception as e:
            print(f"❌ 기본 설정 파일 로드 실패: {e}")
            raise
    
    def generate_enhanced_experiments(self, experiment_type="comprehensive", limit=None):
        """확장된 실험 매트릭스를 사용한 실험 생성"""
        if 'v2_enhanced_experiments' not in self.matrix:
            print("⚠️ 확장된 실험 매트릭스가 없습니다. 기본 생성기를 사용합니다.")
            return self.generate_experiments(experiment_type, limit)
        
        print(f"🚀 확장된 V2 실험 생성 시작 (타입: {experiment_type})")
        
        enhanced_config = self.matrix['v2_enhanced_experiments']
        combinations = enhanced_config.get('experiment_combinations', {})
        
        experiments = []
        
        if experiment_type == "comprehensive":
            # 모든 우선순위 조합 생성
            for priority_name, priority_config in combinations.items():
                print(f"📋 {priority_name} 실험 생성 중...")
                priority_experiments = self.generate_priority_experiments(priority_name, priority_config, enhanced_config)
                experiments.extend(priority_experiments)
                
        elif experiment_type in combinations:
            # 특정 우선순위만 생성
            priority_config = combinations[experiment_type]
            experiments = self.generate_priority_experiments(experiment_type, priority_config, enhanced_config)
        
        # 제한 적용
        if limit and len(experiments) > limit:
            experiments = experiments[:limit]
            print(f"📝 실험 수를 {limit}개로 제한")
        
        print(f"✅ 총 {len(experiments)}개의 확장된 실험 생성 완료")
        return experiments
    
    def generate_priority_experiments(self, priority_name, priority_config, enhanced_config):
        """우선순위별 실험 생성"""
        experiments = []
        variants = enhanced_config.get('variations', {})
        
        # 각 조합 생성
        for config_set in priority_config:
            for model in config_set.get('models', ['convnextv2_base']):
                for optimizer in config_set.get('optimizers', ['adamw_0001']):
                    for scheduler in config_set.get('schedulers', ['cosine']):
                        for loss in config_set.get('losses', ['ce']):
                            for augmentation in config_set.get('augmentations', ['mixup']):
                                for tta in config_set.get('ttas', ['full_tta']):
                                    for es in config_set.get('early_stopping', ['es_5']):
                                        
                                        exp_name = f"{priority_name}_{model}_{optimizer}_{scheduler}_{loss}_{augmentation}_{tta}_{es}"
                                        
                                        experiment = {
                                            'name': exp_name,
                                            'type': 'enhanced_v2',
                                            'priority': priority_name,
                                            'model': self.find_variant(variants.get('model_variants', []), model),
                                            'optimizer': self.find_variant(variants.get('optimizer_variants', []), optimizer),
                                            'scheduler': self.find_variant(variants.get('scheduler_variants', []), scheduler),
                                            'loss': self.find_variant(variants.get('loss_variants', []), loss),
                                            'augmentation': self.find_variant(variants.get('augmentation_variants', []), augmentation),
                                            'tta': self.find_variant(variants.get('tta_variants', []), tta),
                                            'early_stopping': self.find_variant(variants.get('early_stopping_variants', []), es)
                                        }
                                        
                                        experiments.append(experiment)
        
        return experiments
    
    def find_variant(self, variants_list, variant_name):
        """변형 리스트에서 특정 변형 찾기"""
        for variant in variants_list:
            if variant['name'] == variant_name:
                return variant
        return variants_list[0] if variants_list else {}  # 기본값 반환
    
    def generate_enhanced_config(self, experiment):
        """확장된 실험 설정으로 config 파일 생성"""
        if experiment.get('type') != 'enhanced_v2':
            return self.generate_basic_config(experiment)
        
        # 기본 설정을 기반으로 시작
        config = copy.deepcopy(self.base_config_v2_1)
        
        # 모델 설정
        model_variant = experiment['model']
        config['model_name'] = model_variant['model_name']
        config['image_size'] = model_variant.get('image_size', 384)
        config['batch_size'] = model_variant.get('batch_size', 32)
        
        # 옵티마이저 설정
        optimizer_variant = experiment['optimizer']
        config['optimizer_name'] = optimizer_variant['optimizer_name']
        config['lr'] = optimizer_variant['lr']
        config['weight_decay'] = optimizer_variant.get('weight_decay', 0.00001)
        
        # 스케줄러 설정
        scheduler_variant = experiment['scheduler']
        config['scheduler_name'] = scheduler_variant['scheduler_name']
        if 'scheduler_params' in scheduler_variant:
            config['scheduler_params'] = scheduler_variant['scheduler_params']
        
        # Loss 함수 설정
        loss_variant = experiment['loss']
        config['criterion'] = loss_variant['criterion']
        config['label_smooth'] = loss_variant.get('label_smooth', 0.0)
        
        # 증강 설정
        augmentation_variant = experiment['augmentation']
        config['online_augmentation'] = augmentation_variant.get('online_augmentation', True)
        if 'online_aug' in augmentation_variant:
            config['online_aug'] = augmentation_variant['online_aug']
        if 'dynamic_augmentation' in augmentation_variant:
            config['dynamic_augmentation'] = augmentation_variant['dynamic_augmentation']
        
        # TTA 설정
        tta_variant = experiment['tta']
        config['val_TTA'] = tta_variant.get('val_TTA', True)
        config['test_TTA'] = tta_variant.get('test_TTA', True)
        config['tta_dropout'] = tta_variant.get('tta_dropout', False)
        
        # Early Stopping 설정
        es_variant = experiment['early_stopping']
        config['patience'] = es_variant.get('patience', 5)
        
        # WanDB 설정 개선
        if 'wandb' in config:
            # 확장된 WanDB 설정 적용
            if 'wandb_enhanced' in self.matrix:
                wandb_config = self.matrix['wandb_enhanced']
                if wandb_config.get('model_based_projects', True):
                    config['wandb']['model_based_project'] = True
                
                base_tags = config['wandb'].get('tags', [])
                enhanced_tags = wandb_config.get('tags_per_experiment', [])
                config['wandb']['tags'] = base_tags + enhanced_tags + [experiment['priority']]
        
        return config
    
    def generate_basic_config(self, experiment):
        """기본 실험 설정으로 config 파일 생성"""
        # 기존 방식과 호환성 유지
        config = copy.deepcopy(self.base_config_v2_1)
        
        # 기본적인 설정만 적용
        if 'model_name' in experiment:
            config['model_name'] = experiment['model_name']
        if 'batch_size' in experiment:
            config['batch_size'] = experiment['batch_size']
        if 'lr' in experiment:
            config['lr'] = experiment['lr']
        if 'patience' in experiment:
            config['patience'] = experiment['patience']
        
        return config
    
    def save_experiments(self, experiments):
        """실험 목록 저장"""
        experiment_list_path = self.output_dir / "experiment_list.json"
        
        with open(experiment_list_path, 'w', encoding='utf-8') as f:
            json.dump(experiments, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 실험 목록 저장됨: {experiment_list_path}")
        
        # 설정 파일들 생성
        self.generate_config_files(experiments)
        
        # 실행 스크립트 생성
        self.generate_runner_script(experiments)
    
    def generate_config_files(self, experiments):
        """각 실험에 대한 config 파일 생성"""
        print("⚙️ Config 파일 생성 중...")
        
        for i, exp in enumerate(experiments):
            # Config 생성
            if exp.get('type') == 'enhanced_v2':
                config = self.generate_enhanced_config(exp)
            else:
                config = self.generate_basic_config(exp)
            
            # 파일명 생성
            config_filename = f"{exp['name']}.yaml"
            config_path = self.output_dir / "configs" / config_filename
            
            # 파일 저장
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # 실험 정보에 config 경로 추가
            experiments[i]['config_path'] = str(config_path)
        
        print(f"✅ {len(experiments)}개의 config 파일 생성 완료")
    
    def generate_runner_script(self, experiments):
        """통합 실행 스크립트 생성"""
        script_content = f'''#!/bin/bash
# Enhanced V2 Experiment Runner
# 생성일: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo "🚀 Enhanced V2 Experiments Starting"
echo "총 실험 수: {len(experiments)}"
echo "================================="

cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

'''
        
        for i, exp in enumerate(experiments, 1):
            script_content += f'''
# 실험 {i}: {exp['name']}
echo "🔬 [{i}/{len(experiments)}] Starting: {exp['name']}"
echo "Priority: {exp.get('priority', 'N/A')}"

python codes/gemini_main_v2_1_style.py \\
    --config {exp.get('config_path', '')} \\
    >> v2_experiments/logs/enhanced_experiment_run.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 실험 {i} 완료"
else
    echo "❌ 실험 {i} 실패"
fi

echo "---"
'''
        
        script_content += '''
echo "🎉 모든 Enhanced V2 실험 완료!"
echo "📊 로그 확인: v2_experiments/logs/enhanced_experiment_run.log"
'''
        
        # 스크립트 파일 저장
        script_path = self.output_dir / "scripts" / "run_enhanced_v2_experiments.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 실행 권한 추가
        script_path.chmod(0o755)
        
        print(f"📜 실행 스크립트 생성됨: {script_path}")
    
    def generate_experiments(self, experiment_type="all", limit=None):
        """기본 실험 생성 (호환성 유지용)"""
        print("🔄 기본 실험 생성 모드")
        
        # 간단한 기본 실험들 생성
        experiments = []
        
        base_experiments = [
            {
                'name': 'basic_convnext_mixup',
                'type': 'basic_v2',
                'model_name': 'convnextv2_base.fcmae_ft_in22k_in1k_384',
                'batch_size': 32,
                'lr': 0.0001,
                'patience': 5
            },
            {
                'name': 'basic_efficientnet_cutmix',
                'type': 'basic_v2',
                'model_name': 'efficientnet_b4.ra2_in1k',
                'batch_size': 48,
                'lr': 0.0001,
                'patience': 7
            }
        ]
        
        experiments.extend(base_experiments)
        
        if limit and len(experiments) > limit:
            experiments = experiments[:limit]
        
        return experiments


def main():
    parser = argparse.ArgumentParser(description='Enhanced V2 Experiment Generator')
    parser.add_argument('--type', type=str, default='comprehensive',
                       choices=['comprehensive', 'basic_model_comparison', 'optimizer_comparison', 
                               'scheduler_comparison', 'loss_comparison', 'augmentation_comparison', 'tta_comparison'],
                       help='실험 타입 선택')
    parser.add_argument('--limit', type=int, default=None,
                       help='생성할 실험 수 제한')
    parser.add_argument('--dry-run', action='store_true',
                       help='실제 파일 생성 없이 미리보기만')
    
    args = parser.parse_args()
    
    # 생성기 초기화
    generator = EnhancedV2ExperimentGenerator()
    
    # 실험 생성
    experiments = generator.generate_enhanced_experiments(args.type, args.limit)
    
    if args.dry_run:
        print("🔍 실험 미리보기:")
        for i, exp in enumerate(experiments[:10], 1):  # 처음 10개만 표시
            print(f"  {i}. {exp['name']} (우선순위: {exp.get('priority', 'N/A')})")
        if len(experiments) > 10:
            print(f"  ... 그리고 {len(experiments)-10}개 더")
        print(f"\n📊 총 {len(experiments)}개 실험이 생성될 예정입니다.")
    else:
        # 실험 저장
        generator.save_experiments(experiments)
        print(f"\n🎉 Enhanced V2 실험 시스템 구축 완료!")
        print(f"📁 출력 디렉토리: {generator.output_dir}")
        print(f"🚀 실행 명령: ./v2_experiments/scripts/run_enhanced_v2_experiments.sh")


if __name__ == "__main__":
    main()
