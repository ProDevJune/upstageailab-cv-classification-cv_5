#!/usr/bin/env python3
"""
V2_1 & V2_2 Enhanced Experiment Generator
v2_1과 v2_2를 위한 자동 실험 config 생성기
"""

import os
import yaml
import argparse
import itertools
from pathlib import Path
import json

class V2ExperimentGenerator:
    def __init__(self, matrix_file="v2_experiment_matrix.yaml", output_dir="v2_experiments"):
        self.matrix_file = matrix_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 서브 디렉토리 생성
        (self.output_dir / "configs").mkdir(exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        self.load_matrix()
        
    def load_matrix(self):
        """실험 매트릭스 로드"""
        with open(self.matrix_file, 'r', encoding='utf-8') as f:
            self.matrix = yaml.safe_load(f)
            
    def generate_all_experiments(self, dry_run=False, phase=None, exp_type='all', model_filter=None, technique_filter=None, limit=None):
        """모든 실험 조합 생성 with 필터링"""
        all_experiments = []
        
        # 타입별 실험 생성
        if exp_type in ['all', 'v2_1']:
            v2_1_experiments = self.generate_v2_1_experiments()
            all_experiments.extend(v2_1_experiments)
        
        if exp_type in ['all', 'v2_2']:
            v2_2_experiments = self.generate_v2_2_experiments()
            all_experiments.extend(v2_2_experiments)
        
        if exp_type in ['all', 'cv']:
            cv_experiments = self.generate_cv_experiments()
            all_experiments.extend(cv_experiments)
        
        # 필터링 적용
        if model_filter:
            all_experiments = [exp for exp in all_experiments 
                             if model_filter.lower() in exp['overrides'].get('model_name', '').lower()]
        
        if technique_filter:
            all_experiments = [exp for exp in all_experiments 
                             if self.has_technique(exp, technique_filter)]
        
        # 우선순위 필터링
        if phase:
            all_experiments = self.filter_by_phase(all_experiments, phase)
        
        # 개수 제한
        if limit:
            all_experiments = all_experiments[:limit]
            
        print(f"📊 Generated experiments: {len(all_experiments)}")
        print(f"   - Type filter: {exp_type}")
        if model_filter:
            print(f"   - Model filter: {model_filter}")
        if technique_filter:
            print(f"   - Technique filter: {technique_filter}")
        if phase:
            print(f"   - Phase: {phase}")
        if limit:
            print(f"   - Limited to: {limit}")
        
        if not dry_run:
            self.save_experiments(all_experiments)
            self.generate_runner_script(all_experiments)
            
        return all_experiments
    
    def has_technique(self, experiment, technique):
        """실험에 특정 기법이 포함되어 있는지 확인"""
        technique = technique.lower()
        
        # 실험 이름에서 확인
        if technique in experiment['name'].lower():
            return True
        
        # Override 설정에서 확인
        overrides = experiment['overrides']
        
        # 손실함수 확인
        if technique == 'focal' and overrides.get('criterion') == 'FocalLoss':
            return True
        
        # 증강기법 확인 (🔥 업데이트됨)
        if technique == 'mixup':
            # 새로운 online_aug 구조 확인
            if overrides.get('online_aug', {}).get('mixup'):
                return True
            # 레거시 augmentation 구조 확인
            if overrides.get('augmentation', {}).get('mixup'):
                return True
        if technique == 'cutmix':
            # 새로운 online_aug 구조 확인
            if overrides.get('online_aug', {}).get('cutmix'):
                return True
            # 레거시 augmentation 구조 확인
            if overrides.get('augmentation', {}).get('cutmix'):
                return True
        if technique == 'dynamic' and overrides.get('dynamic_augmentation', {}).get('enabled'):
            return True
        
        # 2-stage 확인
        if technique == '2stage' and overrides.get('two_stage'):
            return True
        
        return False
    
    def generate_v2_1_experiments(self):
        """V2_1 실험 조합 생성 (🔥 Mixup/CutMix 지원)"""
        experiments = []
        base_config = self.matrix['v2_1_experiments']
        variations = base_config['variations']
        
        # 모든 조합 생성
        for model in variations['models']:
            for lr in variations['learning_rates']:
                for batch in variations['batch_sizes']:
                    for scheduler in variations['schedulers']:
                        # 🔥 NEW: online_augmentations 추가
                        if 'online_augmentations' in variations:
                            for aug in variations['online_augmentations']:
                                # 메모리 제약 확인
                                if self.check_memory_constraint(model['name'], batch['batch_size']):
                                    exp_name = f"v2_1_{model['name']}_{lr['name']}_{batch['name']}_{scheduler['name']}_{aug['name']}"
                                    
                                    experiment = {
                                        'name': exp_name,
                                        'type': 'v2_1',
                                        'base_config': base_config['base_config'],
                                        'main_script': 'codes/gemini_main_v2_1_style.py',
                                        'overrides': {
                                            'model_name': model['model_name'],
                                            'lr': lr['lr'],
                                            'batch_size': batch['batch_size'],
                                            'scheduler_params': scheduler['scheduler_params'],
                                            'online_aug': aug['online_aug']  # 🔥 Mixup/CutMix 설정
                                        }
                                    }
                                    experiments.append(experiment)
                        else:
                            # 기존 방식 (역호환성)
                            if self.check_memory_constraint(model['name'], batch['batch_size']):
                                exp_name = f"v2_1_{model['name']}_{lr['name']}_{batch['name']}_{scheduler['name']}"
                                
                                experiment = {
                                    'name': exp_name,
                                    'type': 'v2_1',
                                    'base_config': base_config['base_config'],
                                    'main_script': 'codes/gemini_main_v2_1_style.py',
                                    'overrides': {
                                        'model_name': model['model_name'],
                                        'lr': lr['lr'],
                                        'batch_size': batch['batch_size'],
                                        'scheduler_params': scheduler['scheduler_params']
                                    }
                                }
                                experiments.append(experiment)
                            
        return experiments
    
    def generate_v2_2_experiments(self):
        """V2_2 실험 조합 생성"""
        experiments = []
        base_config = self.matrix['v2_2_experiments']
        variations = base_config['variations']
        
        # 모든 조합 생성
        for model in variations['models']:
            for criterion in variations['criterions']:
                for aug in variations['augmentations']:
                    for two_stage in variations['two_stage_options']:
                        exp_name = f"v2_2_{model['name']}_{criterion['name']}_{aug['name']}_{two_stage['name']}"
                        
                        experiment = {
                            'name': exp_name,
                            'type': 'v2_2',
                            'base_config': base_config['base_config'],
                            'main_script': 'codes/gemini_main_v2_enhanced.py',
                            'overrides': {
                                'model_name': model['model_name'],
                                'criterion': criterion['criterion'],
                                **aug,
                                'two_stage': two_stage['two_stage']
                            }
                        }
                        
                        # 2-stage 설정 추가
                        if two_stage['two_stage']:
                            experiment['config2'] = two_stage.get('stage2_config', 'config_2stage_2.yaml')
                            
                        # Label smoothing 추가
                        if 'label_smooth' in criterion:
                            experiment['overrides']['label_smooth'] = criterion['label_smooth']
                            
                        experiments.append(experiment)
                        
        return experiments
    
    def generate_cv_experiments(self):
        """교차 검증 실험 생성"""
        experiments = []
        base_config = self.matrix['cross_validation_experiments']
        variations = base_config['variations']
        
        for fold in variations['folds']:
            for model in variations['models']:
                exp_name = f"cv_{fold['name']}_{model['name']}"
                
                experiment = {
                    'name': exp_name,
                    'type': 'cv',
                    'base_config': base_config['base_config'],
                    'main_script': 'codes/gemini_main_v2_enhanced.py',
                    'overrides': {
                        'model_name': model['model_name'],
                        'n_folds': fold['n_folds']
                    }
                }
                experiments.append(experiment)
                
        return experiments
    
    def check_memory_constraint(self, model_name, batch_size):
        """메모리 제약 확인"""
        constraints = self.matrix.get('constraints', {}).get('memory_limit', {})
        if model_name in constraints:
            max_batch = constraints[model_name]['max_batch_size']
            return batch_size <= max_batch
        return True
    
    def filter_by_phase(self, experiments, phase):
        """우선순위에 따른 실험 필터링"""
        priority = self.matrix.get('experiment_priority', {})
        if phase not in priority:
            return experiments
            
        phase_patterns = priority[phase]
        filtered = []
        
        for exp in experiments:
            exp_name = exp['name']
            for pattern in phase_patterns:
                if self.match_pattern(exp_name, pattern):
                    filtered.append(exp)
                    break
                    
        return filtered
    
    def match_pattern(self, name, pattern):
        """패턴 매칭"""
        import fnmatch
        return fnmatch.fnmatch(name, pattern)
    
    def save_experiments(self, experiments):
        """실험 config 파일들 저장"""
        experiment_list = []
        
        for exp in experiments:
            # Base config 로드
            base_config_path = f"codes/{exp['base_config']}"
            with open(base_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Override 적용
            for key, value in exp['overrides'].items():
                if isinstance(value, dict) and key in config:
                    config[key].update(value)
                else:
                    config[key] = value
            
            # Config 파일 저장
            config_path = self.output_dir / "configs" / f"{exp['name']}.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            # 실험 메타데이터 추가
            exp['config_path'] = str(config_path)
            experiment_list.append(exp)
        
        # 실험 리스트 저장
        with open(self.output_dir / "experiment_list.json", 'w') as f:
            json.dump(experiment_list, f, indent=2)
            
        print(f"✅ Generated {len(experiments)} experiment configs in {self.output_dir}")
        
    def generate_runner_script(self, experiments):
        """자동 실행 스크립트 생성"""
        script_content = f'''#!/bin/bash

# V2_1 & V2_2 자동 실험 실행 스크립트
# 총 {len(experiments)}개 실험 자동 실행

echo "🚀 Starting V2_1 & V2_2 Automatic Experiments"
echo "Total experiments: {len(experiments)}"
echo "======================================================"

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 실험 결과 디렉토리 생성
mkdir -p {self.output_dir}/results

# 실험 로그 파일
LOG_FILE="{self.output_dir}/logs/experiment_run_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG_FILE"

'''

        for i, exp in enumerate(experiments, 1):
            config_name = f"{exp['name']}.yaml"
            
            script_content += f'''
# ===============================================
# 실험 {i}/{len(experiments)}: {exp['name']}
# ===============================================
echo "🔬 [{i}/{len(experiments)}] Starting: {exp['name']}"
echo "Time: $(date)"

'''
            
            if exp['type'] == 'v2_2' and exp.get('config2'):
                # 2-stage 실험
                script_content += f'''python {exp['main_script']} \\
    --config {self.output_dir}/configs/{config_name} \\
    --config2 codes/{exp['config2']} \\
    >> "$LOG_FILE" 2>&1
'''
            else:
                # 일반 실험
                script_content += f'''python {exp['main_script']} \\
    --config {self.output_dir}/configs/{config_name} \\
    >> "$LOG_FILE" 2>&1
'''
            
            script_content += f'''
if [ $? -eq 0 ]; then
    echo "✅ [{i}/{len(experiments)}] Completed: {exp['name']}"
else
    echo "❌ [{i}/{len(experiments)}] Failed: {exp['name']}"
fi

echo "Time: $(date)"
echo "---------------------------------------------"

'''

        script_content += '''
echo ""
echo "🎉 All experiments completed!"
echo "Check the results in data/submissions/"
echo "Check the logs in v2_experiments/logs/"
'''

        # 스크립트 저장
        script_path = self.output_dir / "run_all_experiments.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # 실행 권한 부여
        os.chmod(script_path, 0o755)
        
        print(f"✅ Generated runner script: {script_path}")

def main():
    parser = argparse.ArgumentParser(description="V2_1 & V2_2 Enhanced Experiment Generator")
    parser.add_argument('--matrix', default='v2_experiment_matrix.yaml', help='Experiment matrix file')
    parser.add_argument('--output', default='v2_experiments', help='Output directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no file generation)')
    parser.add_argument('--phase', choices=['phase1', 'phase2', 'phase3', 'phase4'], help='Experiment phase')
    
    # 🔥 NEW: 타입별 선택 옵션
    parser.add_argument('--type', choices=['v2_1', 'v2_2', 'cv', 'all'], default='all', 
                       help='Experiment type to generate')
    parser.add_argument('--model', help='Filter by model name (e.g., convnextv2_base, resnet50)')
    parser.add_argument('--technique', help='Filter by technique (e.g., mixup, cutmix, focal)')
    parser.add_argument('--limit', type=int, help='Limit number of experiments')
    
    args = parser.parse_args()
    
    generator = V2ExperimentGenerator(args.matrix, args.output)
    experiments = generator.generate_all_experiments(
        args.dry_run, args.phase, args.type, args.model, args.technique, args.limit
    )
    
    if args.dry_run:
        print("🔍 Dry run completed. No files were generated.")
        print(f"📊 Would generate {len(experiments)} experiments")
        for exp in experiments[:5]:  # 처음 5개만 출력
            print(f"  - {exp['name']}")
        if len(experiments) > 5:
            print(f"  ... and {len(experiments) - 5} more")
    else:
        print(f"🎯 Ready to run {len(experiments)} experiments!")
        print(f"Execute: ./v2_experiments/run_all_experiments.sh")

if __name__ == "__main__":
    main()
