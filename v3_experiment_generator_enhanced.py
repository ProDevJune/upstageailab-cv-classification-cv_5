#!/usr/bin/env python3
"""
Enhanced V3 Hierarchical Classification Experiment Generator
V3 계층적 분류 시스템을 위한 확장된 자동 실험 config 생성기
"""

import os
import yaml
import argparse
import itertools
from pathlib import Path
import json
import copy
from datetime import datetime

class EnhancedV3ExperimentGenerator:
    def __init__(self, matrix_file="v3_experiment_matrix.yaml", output_dir="v3_experiments"):
        self.matrix_file = matrix_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 서브 디렉토리 생성
        (self.output_dir / "configs" / "modelA").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "configs" / "modelB").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        # 확장된 매트릭스 시도
        self.load_enhanced_matrix()
        
        self.load_matrix()
        self.load_base_configs()
        
    def load_enhanced_matrix(self):
        """확장된 V3 실험 매트릭스 로드"""
        enhanced_matrix_file = "v3_experiment_matrix_enhanced.yaml"
        if os.path.exists(enhanced_matrix_file):
            print(f"📊 확장된 V3 실험 매트릭스 사용: {enhanced_matrix_file}")
            self.matrix_file = enhanced_matrix_file
            return True
        else:
            print(f"⚠️ 확장된 V3 매트릭스 파일을 찾을 수 없습니다: {enhanced_matrix_file}")
            print(f"🔄 기본 V3 매트릭스 사용: {self.matrix_file}")
            return False
    
    def load_matrix(self):
        """매트릭스 파일 로드"""
        try:
            with open(self.matrix_file, 'r', encoding='utf-8') as f:
                self.matrix = yaml.safe_load(f)
            print(f"✅ V3 매트릭스 로드 완료: {self.matrix_file}")
        except Exception as e:
            print(f"❌ V3 매트릭스 로드 실패: {e}")
            raise
    
    def load_base_configs(self):
        """기본 설정 파일들 로드"""
        try:
            # Model A 기본 설정
            with open('codes/config_v3_modelA.yaml', 'r', encoding='utf-8') as f:
                self.base_config_model_a = yaml.safe_load(f)
            
            # Model B 기본 설정  
            with open('codes/config_v3_modelB.yaml', 'r', encoding='utf-8') as f:
                self.base_config_model_b = yaml.safe_load(f)
            
            print("✅ V3 기본 설정 파일 로드 완료")
        except Exception as e:
            print(f"❌ V3 기본 설정 파일 로드 실패: {e}")
            raise
    
    def generate_enhanced_hierarchical_experiments(self, experiment_type="comprehensive", limit=None):
        """확장된 계층적 실험 생성"""
        if 'v3_hierarchical_experiments' not in self.matrix:
            print("⚠️ 확장된 V3 실험 매트릭스가 없습니다. 기본 생성기를 사용합니다.")
            return self.generate_hierarchical_experiments(experiment_type, limit)
        
        print(f"🚀 확장된 V3 계층적 실험 생성 시작 (타입: {experiment_type})")
        
        hierarchical_config = self.matrix['v3_hierarchical_experiments']
        combinations = hierarchical_config.get('experiment_combinations', {})
        
        experiments = []
        
        if experiment_type == "comprehensive":
            # 모든 우선순위 조합 생성
            for priority_name, priority_config in combinations.items():
                print(f"📋 {priority_name} 계층적 실험 생성 중...")
                priority_experiments = self.generate_hierarchical_priority_experiments(priority_name, priority_config, hierarchical_config)
                experiments.extend(priority_experiments)
                
        elif experiment_type in combinations:
            # 특정 우선순위만 생성
            priority_config = combinations[experiment_type]
            experiments = self.generate_hierarchical_priority_experiments(experiment_type, priority_config, hierarchical_config)
        
        # 제한 적용
        if limit and len(experiments) > limit:
            experiments = experiments[:limit]
            print(f"📝 실험 수를 {limit}개로 제한")
        
        print(f"✅ 총 {len(experiments)}개의 확장된 계층적 실험 생성 완료")
        return experiments
    
    def generate_hierarchical_priority_experiments(self, priority_name, priority_config, hierarchical_config):
        """계층적 우선순위별 실험 생성"""
        experiments = []
        variations = hierarchical_config.get('variations', {})
        
        # 각 조합 생성
        for config_set in priority_config:
            for model_a in config_set.get('model_a', ['convnext_base']):
                for model_b in config_set.get('model_b', ['convnext_nano']):
                    for strategy in config_set.get('strategies', ['balanced']):
                        for augmentation in config_set.get('augmentations', ['both_mixup']):
                            for tta in config_set.get('ttas', ['full_tta']):
                                for optimizer in config_set.get('optimizers', ['both_adamw_0001']):
                                    for scheduler in config_set.get('schedulers', ['both_cosine']):
                                        
                                        exp_name = f"{priority_name}_{model_a}_{model_b}_{strategy}_{augmentation}_{tta}_{optimizer}_{scheduler}"
                                        
                                        experiment = {
                                            'name': exp_name,
                                            'type': 'enhanced_hierarchical',
                                            'priority': priority_name,
                                            'model_a': self.find_hierarchical_variant(variations.get('model_a_variants', []), model_a),
                                            'model_b': self.find_hierarchical_variant(variations.get('model_b_variants', []), model_b),
                                            'strategy': self.find_hierarchical_variant(variations.get('hierarchical_strategies', []), strategy),
                                            'augmentation': self.find_hierarchical_variant(variations.get('augmentation_combinations', []), augmentation),
                                            'tta': self.find_hierarchical_variant(variations.get('tta_strategies', []), tta),
                                            'optimizer': self.find_hierarchical_variant(variations.get('optimizer_combinations', []), optimizer),
                                            'scheduler': self.find_hierarchical_variant(variations.get('scheduler_combinations', []), scheduler)
                                        }
                                        
                                        experiments.append(experiment)
        
        return experiments
    
    def find_hierarchical_variant(self, variants_list, variant_name):
        """계층적 변형 리스트에서 특정 변형 찾기"""
        for variant in variants_list:
            if variant['name'] == variant_name:
                return variant
        return variants_list[0] if variants_list else {}  # 기본값 반환
    
    def generate_enhanced_hierarchical_config(self, experiment):
        """확장된 계층적 실험 설정으로 config 파일 생성"""
        if experiment.get('type') != 'enhanced_hierarchical':
            return self.generate_basic_hierarchical_config(experiment)
        
        # Model A 설정 생성
        config_a = copy.deepcopy(self.base_config_model_a)
        model_a_variant = experiment['model_a']
        
        config_a['model_name'] = model_a_variant['model_name']
        config_a['batch_size'] = model_a_variant.get('batch_size', 32)
        config_a['lr'] = model_a_variant.get('lr', 0.0001)
        config_a['patience'] = model_a_variant.get('patience', 7)
        config_a['image_size'] = model_a_variant.get('image_size', 384)
        
        # Model B 설정 생성
        config_b = copy.deepcopy(self.base_config_model_b)
        model_b_variant = experiment['model_b']
        
        config_b['model_name'] = model_b_variant['model_name']
        config_b['batch_size'] = model_b_variant.get('batch_size', 64)
        config_b['lr'] = model_b_variant.get('lr', 0.0001)
        config_b['patience'] = model_b_variant.get('patience', 5)
        config_b['image_size'] = model_b_variant.get('image_size', 384)
        
        # 계층적 전략 적용
        strategy_variant = experiment['strategy']
        config_a['patience'] = strategy_variant.get('model_a_patience', config_a['patience'])
        config_b['patience'] = strategy_variant.get('model_b_patience', config_b['patience'])
        
        # 증강 설정 적용
        augmentation_variant = experiment['augmentation']
        if 'model_a_online_aug' in augmentation_variant:
            config_a['online_aug'] = augmentation_variant['model_a_online_aug']
        if 'model_b_online_aug' in augmentation_variant:
            config_b['online_aug'] = augmentation_variant['model_b_online_aug']
        
        # TTA 설정 적용
        tta_variant = experiment['tta']
        config_a['val_TTA'] = tta_variant.get('model_a_val_tta', True)
        config_a['test_TTA'] = tta_variant.get('model_a_test_tta', True)
        config_b['val_TTA'] = tta_variant.get('model_b_val_tta', True)
        config_b['test_TTA'] = tta_variant.get('model_b_test_tta', True)
        
        # 옵티마이저 설정 적용
        optimizer_variant = experiment['optimizer']
        if 'model_a_optimizer' in optimizer_variant:
            config_a['optimizer_name'] = optimizer_variant['model_a_optimizer']
            config_a['lr'] = optimizer_variant.get('model_a_lr', config_a['lr'])
        if 'model_b_optimizer' in optimizer_variant:
            config_b['optimizer_name'] = optimizer_variant['model_b_optimizer']
            config_b['lr'] = optimizer_variant.get('model_b_lr', config_b['lr'])
        
        # 스케줄러 설정 적용
        scheduler_variant = experiment['scheduler']
        if 'model_a_scheduler' in scheduler_variant:
            config_a['scheduler_name'] = scheduler_variant['model_a_scheduler']
        if 'model_b_scheduler' in scheduler_variant:
            config_b['scheduler_name'] = scheduler_variant['model_b_scheduler']
        
        # WanDB 설정 개선
        for config in [config_a, config_b]:
            if 'wandb' in config:
                # 확장된 WanDB 설정 적용
                if 'wandb_enhanced' in self.matrix:
                    wandb_config = self.matrix['wandb_enhanced']
                    if wandb_config.get('model_based_projects', True):
                        config['wandb']['model_based_project'] = True
                    
                    base_tags = config['wandb'].get('tags', [])
                    enhanced_tags = wandb_config.get('tags_per_experiment', [])
                    config['wandb']['tags'] = base_tags + enhanced_tags + [experiment['priority']]
        
        return config_a, config_b
    
    def generate_basic_hierarchical_config(self, experiment):
        """기본 계층적 실험 설정으로 config 파일 생성"""
        # 기존 방식과 호환성 유지
        config_a = copy.deepcopy(self.base_config_model_a)
        config_b = copy.deepcopy(self.base_config_model_b)
        
        # 기본적인 설정만 적용
        if 'model_a_name' in experiment:
            config_a['model_name'] = experiment['model_a_name']
        if 'model_b_name' in experiment:
            config_b['model_name'] = experiment['model_b_name']
        
        return config_a, config_b
    
    def save_hierarchical_experiments(self, experiments):
        """계층적 실험 목록 저장"""
        experiment_list_path = self.output_dir / "experiment_list.json"
        
        with open(experiment_list_path, 'w', encoding='utf-8') as f:
            json.dump(experiments, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 V3 실험 목록 저장됨: {experiment_list_path}")
        
        # 설정 파일들 생성
        self.generate_hierarchical_config_files(experiments)
        
        # 실행 스크립트 생성
        self.generate_hierarchical_runner_script(experiments)
    
    def generate_hierarchical_config_files(self, experiments):
        """각 계층적 실험에 대한 config 파일 생성"""
        print("⚙️ V3 계층적 Config 파일 생성 중...")
        
        for i, exp in enumerate(experiments):
            # Config 생성 (Model A & Model B)
            if exp.get('type') == 'enhanced_hierarchical':
                config_a, config_b = self.generate_enhanced_hierarchical_config(exp)
            else:
                config_a, config_b = self.generate_basic_hierarchical_config(exp)
            
            # 파일명 생성
            config_a_filename = f"{exp['name']}_modelA.yaml"
            config_b_filename = f"{exp['name']}_modelB.yaml"
            
            config_a_path = self.output_dir / "configs" / "modelA" / config_a_filename
            config_b_path = self.output_dir / "configs" / "modelB" / config_b_filename
            
            # 파일 저장
            with open(config_a_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_a, f, default_flow_style=False, allow_unicode=True)
            
            with open(config_b_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_b, f, default_flow_style=False, allow_unicode=True)
            
            # 실험 정보에 config 경로 추가
            experiments[i]['config_a_path'] = str(config_a_path)
            experiments[i]['config_b_path'] = str(config_b_path)
        
        print(f"✅ {len(experiments)}개의 V3 계층적 config 파일 쌍 생성 완료")
    
    def generate_hierarchical_runner_script(self, experiments):
        """V3 계층적 통합 실행 스크립트 생성"""
        script_content = f'''#!/bin/bash
# Enhanced V3 Hierarchical Experiment Runner
# 생성일: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo "🎯 Enhanced V3 Hierarchical Experiments Starting"
echo "총 계층적 실험 수: {len(experiments)}"
echo "================================="

cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

'''
        
        for i, exp in enumerate(experiments, 1):
            script_content += f'''
# V3 계층적 실험 {i}: {exp['name']}
echo "🔬 [{i}/{len(experiments)}] Starting V3 Hierarchical: {exp['name']}"
echo "Priority: {exp.get('priority', 'N/A')}"
echo "Model A: {exp.get('model_a', {}).get('model_name', 'N/A')}"
echo "Model B: {exp.get('model_b', {}).get('model_name', 'N/A')}"
echo "Strategy: {exp.get('strategy', {}).get('strategy_type', 'N/A')}"

python codes/gemini_main_v3.py \\
    --config {exp.get('config_a_path', '')} \\
    --config2 {exp.get('config_b_path', '')} \\
    >> v3_experiments/logs/enhanced_hierarchical_experiment_run.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ V3 계층적 실험 {i} 완료"
else
    echo "❌ V3 계층적 실험 {i} 실패"
fi

echo "---"
'''
        
        script_content += '''
echo "🎉 모든 Enhanced V3 계층적 실험 완료!"
echo "📊 로그 확인: v3_experiments/logs/enhanced_hierarchical_experiment_run.log"
echo "📈 결과 분석: python v3_experiment_monitor.py --analyze"
'''
        
        # 스크립트 파일 저장
        script_path = self.output_dir / "scripts" / "run_enhanced_v3_hierarchical_experiments.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 실행 권한 추가
        script_path.chmod(0o755)
        
        print(f"📜 V3 계층적 실행 스크립트 생성됨: {script_path}")
    
    def generate_hierarchical_experiments(self, experiment_type="all", limit=None):
        """기본 계층적 실험 생성 (호환성 유지용)"""
        print("🔄 기본 V3 계층적 실험 생성 모드")
        
        # 간단한 기본 실험들 생성
        experiments = []
        
        base_experiments = [
            {
                'name': 'basic_hierarchical_convnext_conservative',
                'type': 'basic_hierarchical',
                'model_a_name': 'convnextv2_base.fcmae_ft_in22k_in1k_384',
                'model_b_name': 'convnextv2_nano.fcmae_ft_in22k_in1k_384',
                'strategy': 'conservative'
            },
            {
                'name': 'basic_hierarchical_mixed_aggressive',
                'type': 'basic_hierarchical',
                'model_a_name': 'efficientnet_b4.ra2_in1k',
                'model_b_name': 'mobilenetv3_small_100.lamb_in1k',
                'strategy': 'aggressive'
            }
        ]
        
        experiments.extend(base_experiments)
        
        if limit and len(experiments) > limit:
            experiments = experiments[:limit]
        
        return experiments


def main():
    parser = argparse.ArgumentParser(description='Enhanced V3 Hierarchical Experiment Generator')
    parser.add_argument('--type', type=str, default='comprehensive',
                       choices=['comprehensive', 'basic_model_combinations', 'strategy_comparison', 
                               'augmentation_comparison', 'tta_comparison', 'optimizer_comparison', 'scheduler_comparison'],
                       help='V3 계층적 실험 타입 선택')
    parser.add_argument('--limit', type=int, default=None,
                       help='생성할 계층적 실험 수 제한')
    parser.add_argument('--dry-run', action='store_true',
                       help='실제 파일 생성 없이 미리보기만')
    
    args = parser.parse_args()
    
    # V3 계층적 생성기 초기화
    generator = EnhancedV3ExperimentGenerator()
    
    # 계층적 실험 생성
    experiments = generator.generate_enhanced_hierarchical_experiments(args.type, args.limit)
    
    if args.dry_run:
        print("🔍 V3 계층적 실험 미리보기:")
        for i, exp in enumerate(experiments[:10], 1):  # 처음 10개만 표시
            print(f"  {i}. {exp['name']}")
            print(f"     우선순위: {exp.get('priority', 'N/A')}")
            print(f"     Model A: {exp.get('model_a', {}).get('model_name', 'N/A')}")
            print(f"     Model B: {exp.get('model_b', {}).get('model_name', 'N/A')}")
            print(f"     전략: {exp.get('strategy', {}).get('strategy_type', 'N/A')}")
            print()
        if len(experiments) > 10:
            print(f"  ... 그리고 {len(experiments)-10}개 더")
        print(f"\n📊 총 {len(experiments)}개 V3 계층적 실험이 생성될 예정입니다.")
    else:
        # 계층적 실험 저장
        generator.save_hierarchical_experiments(experiments)
        print(f"\n🎉 Enhanced V3 계층적 실험 시스템 구축 완료!")
        print(f"📁 출력 디렉토리: {generator.output_dir}")
        print(f"🚀 실행 명령: ./v3_experiments/scripts/run_enhanced_v3_hierarchical_experiments.sh")


if __name__ == "__main__":
    main()
