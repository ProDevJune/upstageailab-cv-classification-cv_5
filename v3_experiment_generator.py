#!/usr/bin/env python3
"""
V3 Hierarchical Classification Experiment Generator
V3 계층적 분류 시스템을 위한 자동 실험 config 생성기
"""

import os
import yaml
import argparse
import itertools
from pathlib import Path
import json
import copy
from datetime import datetime

class V3ExperimentGenerator:
    def __init__(self, matrix_file="v3_experiment_matrix.yaml", output_dir="v3_experiments"):
        self.matrix_file = matrix_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 서브 디렉토리 생성
        (self.output_dir / "configs" / "modelA").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "configs" / "modelB").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "scripts").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        self.load_matrix()
        self.load_base_configs()
        
    def load_matrix(self):
        """실험 매트릭스 로드"""
        with open(self.matrix_file, 'r', encoding='utf-8') as f:
            self.matrix = yaml.safe_load(f)
    
    def load_base_configs(self):
        """기본 설정 파일들 로드"""
        base_configs = self.matrix['v3_hierarchical_experiments']['base_configs']
        
        # Model A 기본 설정 로드
        with open(f"codes/{base_configs['model_a']}", 'r', encoding='utf-8') as f:
            self.base_config_a = yaml.safe_load(f)
        
        # Model B 기본 설정 로드
        with open(f"codes/{base_configs['model_b']}", 'r', encoding='utf-8') as f:
            self.base_config_b = yaml.safe_load(f)
    
    def generate_hierarchical_experiments(self, phase=None, limit=None):
        """계층적 분류 실험 조합 생성"""
        print("🎯 V3 Hierarchical Classification Experiment Generator")
        print("=" * 60)
        
        variations = self.matrix['v3_hierarchical_experiments']['variations']
        experiments = []
        
        # 모든 조합 생성
        for model_a in variations['model_a_variants']:
            for model_b in variations['model_b_variants']:
                for strategy in variations['hierarchical_strategies']:
                    for aug in variations['augmentation_combinations']:
                        for loss in variations['loss_combinations']:
                            for scheduler in variations['scheduler_combinations']:
                                
                                exp_name = f"v3_{model_a['name']}_{model_b['name']}_{strategy['name']}_{aug['name']}_{loss['name']}_{scheduler['name']}"
                                
                                experiment = {
                                    'name': exp_name,
                                    'type': 'hierarchical',
                                    'model_a_config': self.generate_model_a_config(model_a, strategy, aug, loss, scheduler),
                                    'model_b_config': self.generate_model_b_config(model_b, strategy, aug, loss, scheduler),
                                    'execution_strategy': strategy,
                                    'description': f"Model A: {model_a['name']}, Model B: {model_b['name']}, Strategy: {strategy['description']}, Aug: {aug['description']}"
                                }
                                
                                experiments.append(experiment)
        
    def filter_by_phase(self, experiments, phase):
        """Phase별 실험 필터링"""
        if not phase:
            return experiments
            
        # Phase1: 가장 유망한 조합들만 선별
        if phase == 'phase1':
            priority_combinations = [
                'convnext_base_convnext_nano_balanced',
                'convnext_base_convnext_tiny_balanced', 
                'efficientnet_b4_convnext_nano_balanced'
            ]
            
            filtered = []
            for exp in experiments:
                # 실험명에서 핵심 조합 추출
                for priority in priority_combinations:
                    if priority in exp['name']:
                        filtered.append(exp)
                        break
                        
            # Phase1에서는 최대 3개 실험만
            return filtered[:3]
            
        elif phase == 'phase2':
            # Phase2: 중간 우선순위
            return experiments[3:8]
        elif phase == 'phase3':
            # Phase3: 낮은 우선순위
            return experiments[8:15]
        else:
            return experiments
    
    def save_experiment_configs(self, experiments):
        """실험 설정 파일들 저장"""
        print(f"💾 Saving {len(experiments)} experiment configurations...")
        
        for exp in experiments:
            # Model A 설정 저장
            model_a_path = self.output_dir / "configs" / "modelA" / f"{exp['name']}_modelA.yaml"
            with open(model_a_path, 'w', encoding='utf-8') as f:
                yaml.dump(exp['model_a_config'], f, default_flow_style=False, allow_unicode=True)
            
            # Model B 설정 저장
            model_b_path = self.output_dir / "configs" / "modelB" / f"{exp['name']}_modelB.yaml"
            with open(model_b_path, 'w', encoding='utf-8') as f:
                yaml.dump(exp['model_b_config'], f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Saved configs in {self.output_dir}/configs/")
    
    def generate_runner_script(self, experiments):
        """전체 실험 실행 스크립트 생성"""
        script_content = '''#!/bin/bash

# V3 Hierarchical Classification Experiments Runner
echo "🚀 Starting V3 Hierarchical Classification Experiments"
echo "===================================================="

# 로그 디렉토리 생성
mkdir -p v3_experiments/logs
mkdir -p data/submissions

# 실험 실행
experiment_count=0
success_count=0

'''
        
        for exp in experiments:
            script_content += f'''
# 실험: {exp['name']}
echo "🧪 실험 시작: {exp['name']}"
((experiment_count++))

# Model A 실행
if python codes/gemini_main_v3.py --config v3_experiments/configs/modelA/{exp['name']}_modelA.yaml; then
    echo "✅ Model A 완료: {exp['name']}"
    ((success_count++))
else
    echo "❌ Model A 실패: {exp['name']}"
fi

# Model B 실행 
if python codes/gemini_main_v3.py --config v3_experiments/configs/modelB/{exp['name']}_modelB.yaml; then
    echo "✅ Model B 완료: {exp['name']}"
    ((success_count++))
else
    echo "❌ Model B 실패: {exp['name']}"
fi

echo ""
'''
        
        script_content += '''
echo "🎉 모든 V3 실험 완료!"
echo "📊 결과: $success_count/$((experiment_count * 2)) 성공"
echo "📁 결과 확인: ls -la data/submissions/"
'''
        
        script_path = self.output_dir / "scripts" / "run_v3_experiments.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 실행 권한 부여
        import stat
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        
        print(f"✅ Generated runner script: {script_path}")
    
    def generate_phase_scripts(self, experiments):
        """Phase별 실행 스크립트 생성"""
        phases = ['phase1', 'phase2', 'phase3']
        
        for phase in phases:
            phase_experiments = self.filter_by_phase(experiments, phase)
            if not phase_experiments:
                continue
                
            script_content = f'''#!/bin/bash

# V3 {phase.upper()} Experiments
echo "🚀 Starting V3 {phase.upper()} Experiments"
echo "Generated {len(phase_experiments)} experiments"
echo "====================================="

# 현재 위치 확인
echo "현재 위치: $(pwd)"

# 로그 디렉토리 생성
mkdir -p v3_experiments/logs
mkdir -p data/submissions

# 메인 실행 파일 확인
if [ ! -f "codes/gemini_main_v3.py" ]; then
    echo "⚠️  codes/gemini_main_v3.py를 찾을 수 없습니다. 대체 파일 사용..."
    if [ -f "codes/gemini_main_v2_1_style.py" ]; then
        MAIN_SCRIPT="codes/gemini_main_v2_1_style.py"
    else
        echo "❌ 실행할 메인 스크립트를 찾을 수 없습니다!"
        exit 1
    fi
else
    MAIN_SCRIPT="codes/gemini_main_v3.py"
fi

echo "🐍 사용할 스크립트: $MAIN_SCRIPT"

# 실험 실행
experiment_count=0
success_count=0

'''
            
            for exp in phase_experiments:
                script_content += f'''
# 실험: {exp['name']}
echo "🧪 [{phase.upper()}] 실험 시작: {exp['name']}"
((experiment_count++))

# 설정 파일 확인
if [ -f "v3_experiments/configs/modelA/{exp['name']}_modelA.yaml" ]; then
    echo "   📝 Model A 설정: v3_experiments/configs/modelA/{exp['name']}_modelA.yaml"
    if python "$MAIN_SCRIPT" --config "v3_experiments/configs/modelA/{exp['name']}_modelA.yaml"; then
        echo "   ✅ Model A 완료: {exp['name']}"
        ((success_count++))
    else
        echo "   ❌ Model A 실패: {exp['name']}"
    fi
else
    echo "   ⚠️  Model A 설정 파일 없음: {exp['name']}"
fi

echo ""
'''
            
            script_content += f'''
echo "🎉 V3 {phase.upper()} 실험 완료!"
echo "📊 결과: $success_count/$experiment_count 성공"
echo "📁 결과 확인: ls -la data/submissions/"
'''
            
            script_path = self.output_dir / "scripts" / f"run_v3_{phase}.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 실행 권한 부여
            import stat
            script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
            
            print(f"✅ Generated {phase} script: {script_path}")
    
    def generate_summary_report(self, experiments):
        """실험 요약 보고서 생성"""
        total_experiments = len(experiments)
        model_a_variants = len(set(exp['model_a_config']['model_name'] for exp in experiments))
        model_b_variants = len(set(exp['model_b_config']['model_name'] for exp in experiments))
        
        report = f"""# V3 Hierarchical Classification Experiments Report

생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Experiment Overview
- **Total Experiments**: {total_experiments}
- **Model A Variants**: {model_a_variants}
- **Model B Variants**: {model_b_variants}
- **Hierarchical Strategies**: 3

## 🎯 Phase별 실험 분배
"""
        
        # 개수 제한
        if limit:
            experiments = experiments[:limit]
        
        print(f"📊 Generated {len(experiments)} V3 hierarchical experiments")
        return experiments
    
    def generate_model_a_config(self, model_variant, strategy, aug, loss, scheduler):
        """Model A 설정 생성"""
        config = copy.deepcopy(self.base_config_a)
        
        # 모델 변형 적용
        config['model_name'] = model_variant['model_name']
        config['batch_size'] = model_variant['batch_size']
        config['lr'] = model_variant['lr']
        config['patience'] = model_variant['patience']
        
        # 전략 적용
        if 'model_a_epochs' in strategy:
            config['scheduler_params']['T_max'] = strategy['model_a_epochs']
        
        # 증강 적용
        config['online_aug'] = aug['model_a_online_aug']
        config['augmentation'] = aug['model_a_augmentation']
        
        # 손실 함수 적용
        config['criterion'] = loss['model_a_criterion']
        
        # 스케줄러 적용
        config['scheduler_name'] = scheduler['model_a_scheduler']
        
        return config
    
    def generate_model_b_config(self, model_variant, strategy, aug, loss, scheduler):
        """Model B 설정 생성"""
        config = copy.deepcopy(self.base_config_b)
        
        # 모델 변형 적용
        config['model_name'] = model_variant['model_name']
        config['batch_size'] = model_variant['batch_size']
        config['lr'] = model_variant['lr']
        config['patience'] = model_variant['patience']
        
        # 전략 적용
        if 'model_b_epochs' in strategy:
            config['scheduler_params']['T_max'] = strategy['model_b_epochs']
        
        # 증강 적용
        config['online_aug'] = aug['model_b_online_aug']
        config['augmentation'] = aug['model_b_augmentation']
        
        # 손실 함수 적용
        config['criterion'] = loss['model_b_criterion']
        
        # 스케줄러 적용
        config['scheduler_name'] = scheduler['model_b_scheduler']
        
        return config
    
    def filter_by_phase(self, experiments, phase):
        """실험 우선순위에 따른 필터링"""
        if phase not in self.matrix['experiment_priority']:
            return experiments
        
        phase_patterns = self.matrix['experiment_priority'][phase]
        filtered = []
        
        for exp in experiments:
            exp_pattern = self.create_experiment_pattern(exp)
            if any(self.pattern_matches(exp_pattern, pattern) for pattern in phase_patterns):
                filtered.append(exp)
        
        return filtered
    
    def create_experiment_pattern(self, experiment):
        """실험에서 패턴 문자열 생성"""
        parts = experiment['name'].split('_')[1:]  # 'v3_' 제거
        return '.'.join(parts)
    
    def pattern_matches(self, exp_pattern, filter_pattern):
        """패턴 매칭 확인"""
        if '*' in filter_pattern:
            # 와일드카드 패턴 처리
            filter_parts = filter_pattern.split('.')
            exp_parts = exp_pattern.split('.')
            
            if len(filter_parts) != len(exp_parts):
                return False
            
            for f_part, e_part in zip(filter_parts, exp_parts):
                if f_part != '*' and f_part != e_part:
                    return False
            return True
        else:
            return exp_pattern == filter_pattern
    
    def save_experiment_configs(self, experiments):
        """실험 설정 파일들 저장"""
        print("💾 Saving experiment configurations...")
        
        saved_configs = []
        
        for exp in experiments:
            # Model A 설정 저장
            model_a_path = self.output_dir / "configs" / "modelA" / f"{exp['name']}_modelA.yaml"
            with open(model_a_path, 'w', encoding='utf-8') as f:
                yaml.dump(exp['model_a_config'], f, default_flow_style=False, allow_unicode=True)
            
            # Model B 설정 저장
            model_b_path = self.output_dir / "configs" / "modelB" / f"{exp['name']}_modelB.yaml"
            with open(model_b_path, 'w', encoding='utf-8') as f:
                yaml.dump(exp['model_b_config'], f, default_flow_style=False, allow_unicode=True)
            
            saved_configs.append({
                'name': exp['name'],
                'model_a_config': str(model_a_path),
                'model_b_config': str(model_b_path),
                'description': exp['description']
            })
        
        # 실험 리스트 저장
        experiment_list_path = self.output_dir / "experiment_list.json"
        with open(experiment_list_path, 'w', encoding='utf-8') as f:
            json.dump(saved_configs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(saved_configs)} experiment configurations")
        return saved_configs
    
    def generate_runner_script(self, experiments):
        """V3 전용 실행 스크립트 생성"""
        print("🔧 Generating V3 execution script...")
        
        script_content = f'''#!/bin/bash
# V3 Hierarchical Classification Auto Experiment Runner
# Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo "🎯 V3 Hierarchical Classification Experiments"
echo "Total experiments: {len(experiments)}"
echo "============================================="

cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 실험 결과 로그 파일
LOG_FILE="v3_experiments/logs/v3_experiment_run_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG_FILE"

'''
        
        for i, exp in enumerate(experiments, 1):
            script_content += f'''
# ===== V3 실험 {i}: {exp['name']} =====
echo "🔬 [{i}/{len(experiments)}] Starting V3 Hierarchical: {exp['name']}"
echo "📄 Description: {exp['description']}"

python codes/gemini_main_v3.py \\
    --config v3_experiments/configs/modelA/{exp['name']}_modelA.yaml \\
    --config2 v3_experiments/configs/modelB/{exp['name']}_modelB.yaml \\
    >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ V3 Experiment {i} completed successfully"
else
    echo "❌ V3 Experiment {i} failed"
fi

echo "⏱️ Completed at: $(date)"
echo "============================================="
'''
        
        script_content += '''
echo "🎉 All V3 experiments completed!"
echo "📊 Check results in: data/submissions/"
echo "📝 Full log available in: $LOG_FILE"
'''
        
        # 실행 스크립트 저장
        script_path = self.output_dir / "scripts" / "run_v3_experiments.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 실행 권한 추가
        os.chmod(script_path, 0o755)
        
        print(f"🚀 Created execution script: {script_path}")
        return script_path
    
    def generate_phase_scripts(self, experiments):
        """Phase별 실행 스크립트 생성"""
        print("🔧 Generating phase-specific scripts...")
        
        phases = self.matrix['experiment_priority']
        
        for phase_name, patterns in phases.items():
            phase_experiments = self.filter_by_phase(experiments, phase_name)
            
            if not phase_experiments:
                continue
            
            script_content = f'''#!/bin/bash
# V3 Hierarchical Classification - {phase_name.upper()} Phase
# Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo "🎯 V3 {phase_name.upper()} Phase Experiments"
echo "Total experiments: {len(phase_experiments)}"
echo "============================================="

cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

LOG_FILE="v3_experiments/logs/v3_{phase_name}_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG_FILE"

'''
            
            for i, exp in enumerate(phase_experiments, 1):
                script_content += f'''
# ===== {phase_name.upper()} 실험 {i}: {exp['name']} =====
echo "🔬 [{i}/{len(phase_experiments)}] Starting {phase_name.upper()}: {exp['name']}"

python codes/gemini_main_v3.py \\
    --config v3_experiments/configs/modelA/{exp['name']}_modelA.yaml \\
    --config2 v3_experiments/configs/modelB/{exp['name']}_modelB.yaml \\
    >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ {phase_name.upper()} Experiment {i} completed successfully"
else
    echo "❌ {phase_name.upper()} Experiment {i} failed"
fi
'''
            
            script_content += f'''
echo "🎉 {phase_name.upper()} phase completed!"
'''
            
            # Phase별 스크립트 저장
            script_path = self.output_dir / "scripts" / f"run_v3_{phase_name}.sh"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 실행 권한 추가
            os.chmod(script_path, 0o755)
            
            print(f"📋 Created {phase_name} script: {script_path}")
    
    def generate_summary_report(self, experiments):
        """실험 요약 보고서 생성"""
        print("📊 Generating experiment summary report...")
        
        # 통계 계산
        total_experiments = len(experiments)
        model_a_variants = len(set(exp['name'].split('_')[1] for exp in experiments))
        model_b_variants = len(set(exp['name'].split('_')[2] for exp in experiments))
        
        report = f"""# V3 Hierarchical Classification Experiment Report
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Experiment Overview
- **Total Experiments**: {total_experiments}
- **Model A Variants**: {model_a_variants}
- **Model B Variants**: {model_b_variants}
- **Hierarchical Strategies**: {len(self.matrix['v3_hierarchical_experiments']['variations']['hierarchical_strategies'])}
- **Augmentation Combinations**: {len(self.matrix['v3_hierarchical_experiments']['variations']['augmentation_combinations'])}

## 🎯 Experiment Categories
"""
        
        # Phase별 실험 수 계산
        phases = self.matrix['experiment_priority']
        for phase_name in phases:
            phase_experiments = self.filter_by_phase(experiments, phase_name)
            report += f"- **{phase_name.upper()}**: {len(phase_experiments)} experiments\n"
        
        report += "\n## 📋 Experiment List\n"
        for i, exp in enumerate(experiments, 1):
            report += f"{i}. `{exp['name']}` - {exp['description']}\n"
        
        report += f"""
## 🚀 Execution Commands
```bash
# Run all experiments
./v3_experiments/scripts/run_v3_experiments.sh

# Run specific phase
./v3_experiments/scripts/run_v3_phase1.sh

# Monitor progress
python v3_experiment_monitor.py --realtime
```

## 📁 File Structure
```
v3_experiments/
├── configs/
│   ├── modelA/     # Model A configurations
│   └── modelB/     # Model B configurations
├── scripts/        # Execution scripts
├── logs/          # Experiment logs
└── experiment_list.json
```
"""
        
        # 보고서 저장
        report_path = self.output_dir / "V3_EXPERIMENT_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Created experiment report: {report_path}")
        return report_path

def main():
    parser = argparse.ArgumentParser(description="V3 Hierarchical Classification Experiment Generator")
    parser.add_argument('--phase', type=str, help='Experiment phase (phase1, phase2, phase3, phase4)')
    parser.add_argument('--limit', type=int, help='Limit number of experiments')
    parser.add_argument('--dry-run', action='store_true', help='Show experiments without saving')
    
    args = parser.parse_args()
    
    try:
        # 실험 생성기 초기화
        generator = V3ExperimentGenerator()
        
        # 실험 생성
        experiments = generator.generate_hierarchical_experiments(
            phase=args.phase,
            limit=args.limit
        )
        
        if args.dry_run:
            print("\n🔍 DRY RUN - Generated experiments:")
            for i, exp in enumerate(experiments, 1):
                print(f"{i}. {exp['name']} - {exp['description']}")
        else:
            # 실험 설정 파일들 저장
            generator.save_experiment_configs(experiments)
            
            # 실행 스크립트 생성
            generator.generate_runner_script(experiments)
            generator.generate_phase_scripts(experiments)
            
            # 요약 보고서 생성
            generator.generate_summary_report(experiments)
            
            print("\n🎉 V3 Experiment Generation Complete!")
            print("Next steps:")
            print("1. Review generated configurations in v3_experiments/configs/")
            print("2. Run experiments: ./v3_experiments/scripts/run_v3_experiments.sh")
            print("3. Monitor progress: python v3_experiment_monitor.py")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
