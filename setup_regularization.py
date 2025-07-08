#!/usr/bin/env python3
"""
정규화 강화 설정을 위한 HPO 설정 생성기
"""

import yaml
import numpy as np

def create_regularization_configs():
    """다양한 정규화 수준의 설정 파일들을 생성합니다."""
    
    print("🛡️ 정규화 강화 설정 생성기")
    print("=" * 50)
    
    # 기본 설정 로드
    with open('codes/config.yaml', 'r') as f:
        base_config = yaml.safe_load(f)
    
    regularization_levels = {
        'light': {
            'description': '가벼운 정규화',
            'weight_decay': 1e-4,    # 10배 증가
            'dropout_rate': 0.3,     # 기본보다 증가
            'label_smoothing': 0.1,   # 새로 추가
            'mixup_alpha': 0.2,      # MixUp 추가
            'cutmix_alpha': 1.0,     # CutMix 추가
        },
        'medium': {
            'description': '중간 정규화',
            'weight_decay': 5e-4,    # 50배 증가
            'dropout_rate': 0.4,     
            'label_smoothing': 0.15,  
            'mixup_alpha': 0.4,      
            'cutmix_alpha': 1.0,     
            'stochastic_depth': 0.1, # 새로 추가
        },
        'strong': {
            'description': '강한 정규화',
            'weight_decay': 1e-3,    # 100배 증가
            'dropout_rate': 0.5,     
            'label_smoothing': 0.2,   
            'mixup_alpha': 0.6,      
            'cutmix_alpha': 1.0,     
            'stochastic_depth': 0.2,
            'ema_decay': 0.9999,     # EMA 추가
        }
    }
    
    for level, params in regularization_levels.items():
        config = base_config.copy()
        
        # 정규화 파라미터 업데이트
        config['weight_decay'] = params['weight_decay']
        config['experiment_id'] = f'exp_reg_{level}'
        config['experiment_type'] = f'regularization_{level}'
        
        # 새로운 정규화 섹션 추가
        config['regularization'] = {
            'level': level,
            'description': params['description'],
            'dropout_rate': params['dropout_rate'],
            'label_smoothing': params.get('label_smoothing', 0.0),
            'stochastic_depth': params.get('stochastic_depth', 0.0),
            'ema_decay': params.get('ema_decay', None)
        }
        
        # 증강 섹션 업데이트
        config['augmentation']['mixup'] = params.get('mixup_alpha', 0.0) > 0
        config['augmentation']['cutmix'] = params.get('cutmix_alpha', 0.0) > 0
        config['mixup_alpha'] = params.get('mixup_alpha', 0.0)
        config['cutmix_alpha'] = params.get('cutmix_alpha', 0.0)
        
        # 파일 저장
        filename = f'codes/config_reg_{level}.yaml'
        with open(filename, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ {filename} 생성 ({params['description']})")

def explain_regularization_techniques():
    """정규화 기법들을 자세히 설명합니다."""
    
    print(f"\n🎯 정규화 기법별 상세 설명:")
    print(f"=" * 60)
    
    techniques = {
        'Weight Decay (L2 정규화)': {
            'concept': '가중치가 너무 커지지 않도록 페널티 부여',
            'effect': '모델의 복잡도 감소, 일반화 성능 향상',
            'example': 'loss = original_loss + λ * ||weights||²',
            'values': '1e-5 → 1e-3 (100배 증가)'
        },
        'Dropout': {
            'concept': '학습 시 일부 뉴런을 랜덤하게 비활성화',
            'effect': '특정 뉴런에 의존하지 않는 robust한 특징 학습',
            'example': '50% 확률로 뉴런을 0으로 만듦',
            'values': '0.2 → 0.5 (더 많은 뉴런 비활성화)'
        },
        'Label Smoothing': {
            'concept': 'Hard target (0,1)을 Soft target (0.1,0.9)로 변경',
            'effect': '과신(overconfidence) 방지, 일반화 향상',
            'example': '[0,0,1,0] → [0.05,0.05,0.85,0.05]',
            'values': '0.0 → 0.2 (20% 스무딩)'
        },
        'MixUp': {
            'concept': '두 이미지와 라벨을 선형 결합',
            'effect': '결정 경계 스무딩, 새로운 데이터 생성 효과',
            'example': 'new_img = α*img1 + (1-α)*img2',
            'values': 'α ~ Beta(0.2, 0.2) 분포'
        },
        'CutMix': {
            'concept': '한 이미지의 일부를 다른 이미지로 교체',
            'effect': '지역적 특징과 전역적 특징 모두 학습',
            'example': '이미지 A의 일부 영역을 이미지 B로 덮기',
            'values': 'α=1.0 (베타 분포 파라미터)'
        },
        'Stochastic Depth': {
            'concept': '학습 시 일부 레이어를 랜덤하게 건너뛰기',
            'effect': '깊은 네트워크의 과적합 방지',
            'example': 'ResNet의 일부 블록을 확률적으로 skip',
            'values': '10-20% 확률로 블록 스킵'
        }
    }
    
    for technique, info in techniques.items():
        print(f"\n📚 {technique}:")
        print(f"   💡 개념: {info['concept']}")
        print(f"   🎯 효과: {info['effect']}")
        print(f"   📝 예시: {info['example']}")
        print(f"   ⚙️  설정: {info['values']}")

def create_regularization_hpo():
    """정규화 파라미터를 포함한 HPO 설정을 생성합니다."""
    
    hpo_script = '''#!/usr/bin/env python3
"""
정규화 강화 HPO 실험 스크립트
"""

import optuna
import yaml

def objective(trial):
    """정규화 파라미터 최적화를 위한 목적 함수"""
    
    # 정규화 파라미터 샘플링
    params = {
        'weight_decay': trial.suggest_loguniform('weight_decay', 1e-5, 1e-2),
        'dropout_rate': trial.suggest_uniform('dropout_rate', 0.2, 0.6),
        'label_smoothing': trial.suggest_uniform('label_smoothing', 0.0, 0.3),
        'mixup_alpha': trial.suggest_uniform('mixup_alpha', 0.0, 0.8),
        'cutmix_alpha': trial.suggest_uniform('cutmix_alpha', 0.0, 2.0),
    }
    
    # 기본 설정 로드
    with open('codes/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # 정규화 파라미터 적용
    config.update(params)
    config['experiment_id'] = f"exp_reg_hpo_{trial.number:03d}"
    
    # 실제 학습 실행 (여기서는 mock)
    # f1_score = train_and_evaluate(config)
    
    # Mock F1 score (실제로는 학습 결과)
    import random
    f1_score = random.uniform(0.80, 0.94)
    
    return f1_score

def run_regularization_hpo():
    """정규화 강화 HPO 실행"""
    
    print("🚀 정규화 강화 HPO 시작")
    
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20)
    
    print(f"\\n🏆 최고 성과:")
    print(f"   F1 Score: {study.best_value:.4f}")
    print(f"   파라미터: {study.best_params}")
    
    return study.best_params

if __name__ == "__main__":
    best_params = run_regularization_hpo()
    print("\\n✅ 정규화 HPO 완료!")
'''
    
    with open('regularization_hpo.py', 'w') as f:
        f.write(hpo_script)
    
    print(f"\n✅ 정규화 HPO 스크립트 생성: regularization_hpo.py")

if __name__ == "__main__":
    create_regularization_configs()
    explain_regularization_techniques()
    create_regularization_hpo()
    
    print(f"\n🚀 정규화 강화 단계:")
    print(f"1. python codes/gemini_main.py --config codes/config_reg_light.yaml")
    print(f"2. python codes/gemini_main.py --config codes/config_reg_medium.yaml") 
    print(f"3. python codes/gemini_main.py --config codes/config_reg_strong.yaml")
    print(f"4. python regularization_hpo.py (고급 최적화)")
    print(f"5. 성능 비교 후 최적 정규화 수준 선택")
