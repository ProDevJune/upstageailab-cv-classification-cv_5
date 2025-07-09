#!/usr/bin/env python3
"""
V2_1 & V2_2 Enhanced Experiment Generator - FIXED VERSION
v2_1과 v2_2를 위한 자동 실험 config 생성기 (경로 문제 해결됨)
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
        
        # 증강기법 확인
        if technique == 'mixup':
            online_aug = overrides.get('online_aug', {})
            if isinstance(online_aug, dict) and online_aug.get('mixup', False):
                return True
        
        if technique == 'cutmix':
            online_aug = overrides.get('online_aug', {})
            if isinstance(online_aug, dict) and online_aug.get('cutmix', False):
                return True
        
        return False
    
    def generate_v2_2_experiments(self):
        """V2_2 실험 생성"""
        experiments = []
        v2_2_config = self.matrix['v2_2_experiments']
        
        # 조합 생성
        for model in v2_2_config['variations']['models']:
            for criterion in v2_2_config['variations']['criterions']:
                for aug in v2_2_config['variations']['augmentations']:
                    exp_name = f"v2_2_{model['name']}_{criterion['name']}_{aug['name']}_single"
                    
                    # Override 설정 생성
                    overrides = {
                        'model_name': model['model_name'],
                        'criterion': criterion['criterion'],
                        'online_aug': aug['online_aug']
                    }
                    
                    # 라벨 스무딩이 있는 경우 추가
                    if 'label_smooth' in criterion:
                        overrides['label_smooth'] = criterion['label_smooth']
                    
                    experiment = {
                        'name': exp_name,
                        'type': 'v2_2',
                        'base_config': v2_2_config['base_config'],
                        'main_script': 'codes/gemini_main_v2_1_style.py',
                        'overrides': overrides
                    }
                    
                    experiments.append(experiment)
        
        return experiments
    
    def generate_v2_1_experiments(self):
        """V2_1 실험 생성 (모든 조합)"""
        experiments = []
        v2_1_config = self.matrix['v2_1_experiments']
        
        # 모든 조합 생성
        for model in v2_1_config['variations']['models']:
            for lr in v2_1_config['variations']['learning_rates']:
                for batch in v2_1_config['variations']['batch_sizes']:
                    for aug in v2_1_config['variations']['online_augmentations']:
                        for scheduler in v2_1_config['variations']['schedulers']:
                            exp_name = f"v2_1_{model['name']}_{lr['name']}_{batch['name']}_{scheduler['name']}_{aug['name']}"
                            
                            # Override 설정 생성
                            overrides = {
                                'model_name': model['model_name'],
                                'lr': lr['lr'],
                                'batch_size': batch['batch_size'],
                                'online_aug': aug['online_aug'],
                                'scheduler_params': scheduler['scheduler_params']
                            }
                            
                            experiment = {
                                'name': exp_name,
                                'type': 'v2_1',
                                'base_config': v2_1_config['base_config'],
                                'main_script': 'codes/gemini_main_v2_1_style.py',
                                'overrides': overrides
                            }
                            
                            experiments.append(experiment)
        
        return experiments
    
    def generate_cv_experiments(self):
        """Cross-validation 실험 생성"""
        return []  # 현재는 비어있음
    
    def filter_by_phase(self, experiments, phase):
        """Phase별 실험 필터링"""
        return experiments  # 현재는 필터링 없음
    
    def save_experiments(self, experiments):
        """실험 설정 파일들 저장"""
        for exp in experiments:
            # 기본 설정 로드
            with open(f"codes/{exp['base_config']}", 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Override 적용
            for key, value in exp['overrides'].items():
                config[key] = value
            
            # 실험별 설정 저장
            config_path = self.output_dir / "configs" / f"{exp['name']}.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Generated {len(experiments)} experiment configs in {self.output_dir}")
    
    def generate_runner_script(self, experiments):
        """자동 실행 스크립트 생성 - FIXED VERSION"""
        
        # 스크립트 헤더
        script_header = '''#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# V2_1 & V2_2 자동 실험 실행 스크립트 (FIXED VERSION)
echo "🚀 Starting V2_1 & V2_2 Automatic Experiments (FIXED)"
echo "Total experiments: {num_experiments}"
echo "======================================================"

# 현재 디렉토리에서 실행 (경로 문제 해결)
echo "현재 위치: $(pwd)"

# 실험 결과 디렉토리 생성
mkdir -p {output_dir}/results
mkdir -p data/submissions

# 실험 로그 파일
LOG_FILE="{output_dir}/logs/experiment_run_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG_FILE"

'''.format(num_experiments=len(experiments), output_dir=self.output_dir)
        
        # 각 실험별 코드 생성
        script_body = ""
        for i, exp in enumerate(experiments, 1):
            config_name = f"{exp['name']}.yaml"
            
            experiment_code = '''
# ===============================================
# 실험 {exp_num}/{total_exp}: {exp_name}
# ===============================================
echo "🔬 [{exp_num}/{total_exp}] Starting: {exp_name}"
echo "Time: $(date)"
echo "현재 위치: $(pwd)"
echo "설정 파일: {output_dir}/configs/{config_name}"
echo "실행 스크립트: {main_script}"
echo ""

# 실험 실행
if python {main_script} --config {output_dir}/configs/{config_name} 2>&1 | tee -a "$LOG_FILE"; then
    echo "✅ [{exp_num}/{total_exp}] Completed: {exp_name}"
else
    echo "❌ [{exp_num}/{total_exp}] Failed: {exp_name} (Exit code: $?)"
    echo "📋 마지막 20줄 로그:"
    tail -20 "$LOG_FILE" | sed 's/^/   /'
fi

echo "Time: $(date)"
echo "---------------------------------------------"

'''.format(
                exp_num=i,
                total_exp=len(experiments),
                exp_name=exp['name'],
                config_name=config_name,
                main_script=exp['main_script'],
                output_dir=self.output_dir
            )
            
            script_body += experiment_code
        
        # 스크립트 푸터
        script_footer = '''
echo ""
echo "🎉 All experiments completed!"
echo "Check the results in data/submissions/"
echo "Check the logs in v2_experiments/logs/"
'''
        
        # 전체 스크립트 조합
        full_script = script_header + script_body + script_footer
        
        # 스크립트 저장
        script_path = self.output_dir / "run_all_experiments.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(full_script)
        
        # 실행 권한 부여
        os.chmod(script_path, 0o755)
        
        print(f"✅ Generated runner script: {script_path}")

def main():
    parser = argparse.ArgumentParser(description="V2_1 & V2_2 Enhanced Experiment Generator")
    parser.add_argument('--matrix', default='v2_experiment_matrix.yaml', help='Experiment matrix file')
    parser.add_argument('--output', default='v2_experiments', help='Output directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no file generation)')
    parser.add_argument('--phase', choices=['phase1', 'phase2', 'phase3', 'phase4'], help='Experiment phase')
    
    # 타입별 선택 옵션
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
