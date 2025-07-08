#!/usr/bin/env python3
"""
앙상블 전략 설정 및 실행 시스템
최고 성능 모델들을 조합하여 앙상블 구성
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from typing import List, Dict, Any
import json

def load_experiment_results():
    """실험 결과 로드"""
    results_path = "enhanced_experiment_results.csv"
    if Path(results_path).exists():
        return pd.read_csv(results_path)
    else:
        print("❌ enhanced_experiment_results.csv 파일이 없습니다.")
        return None

def analyze_ensemble_candidates(df):
    """앙상블 후보 분석"""
    # 서버 제출된 모델들만 필터링
    submitted = df[df['aistages_submitted'] == True].copy()
    
    if submitted.empty:
        print("⚠️ 서버 제출 결과가 없습니다.")
        return []
    
    # 성능순 정렬
    submitted = submitted.sort_values('aistages_public_score', ascending=False)
    
    candidates = []
    for _, row in submitted.iterrows():
        candidates.append({
            'experiment_id': row['experiment_id'],
            'model_name': row['model_name'],
            'image_size': row['image_size'],
            'server_score': row['aistages_public_score'],
            'local_f1': row['final_f1'],
            'generalization_ratio': row['aistages_public_score'] / row['final_f1'] if pd.notna(row['final_f1']) else 0,
            'submission_path': row['submission_path'],
            'recommended': row['recommended_for_ensemble']
        })
    
    return candidates

def create_ensemble_strategy(candidates):
    """앙상블 전략 생성"""
    
    # 성능 기반 가중치 계산
    scores = [c['server_score'] for c in candidates]
    max_score = max(scores)
    
    # 다양성을 위한 모델 타입 분석
    model_types = {}
    for candidate in candidates:
        model_family = candidate['model_name'].split('.')[0]
        if model_family not in model_types:
            model_types[model_family] = []
        model_types[model_family].append(candidate)
    
    strategies = []
    
    # 전략 1: Top 성능 기반 앙상블
    top_models = candidates[:3]  # 상위 3개 모델
    top_weights = []
    for candidate in top_models:
        weight = candidate['server_score'] / sum(c['server_score'] for c in top_models)
        top_weights.append(weight)
    
    strategies.append({
        'name': 'top_performance',
        'description': '상위 성능 3개 모델 조합',
        'models': top_models,
        'weights': top_weights,
        'expected_score': sum(c['server_score'] * w for c, w in zip(top_models, top_weights))
    })
    
    # 전략 2: 다양성 기반 앙상블
    diverse_models = []
    used_families = set()
    for candidate in candidates:
        model_family = candidate['model_name'].split('.')[0]
        if model_family not in used_families and len(diverse_models) < 4:
            diverse_models.append(candidate)
            used_families.add(model_family)
    
    if len(diverse_models) >= 2:
        diverse_weights = [1/len(diverse_models)] * len(diverse_models)
        strategies.append({
            'name': 'diversity_based',
            'description': '다양한 아키텍처 조합',
            'models': diverse_models,
            'weights': diverse_weights,
            'expected_score': sum(c['server_score'] * w for c, w in zip(diverse_models, diverse_weights))
        })
    
    # 전략 3: 일반화 성능 기반 앙상블
    if all('generalization_ratio' in c for c in candidates):
        stable_models = [c for c in candidates if c['generalization_ratio'] > 0.85][:3]
        if len(stable_models) >= 2:
            stable_weights = []
            for candidate in stable_models:
                # 일반화 비율과 성능 모두 고려
                weight = (candidate['server_score'] * candidate['generalization_ratio']) / \
                        sum(c['server_score'] * c['generalization_ratio'] for c in stable_models)
                stable_weights.append(weight)
            
            strategies.append({
                'name': 'stable_generalization',
                'description': '안정적 일반화 성능 조합',
                'models': stable_models,
                'weights': stable_weights,
                'expected_score': sum(c['server_score'] * w for c, w in zip(stable_models, stable_weights))
            })
    
    return strategies

def create_ensemble_config(strategy):
    """앙상블 실행을 위한 설정 생성"""
    config = {
        'ensemble_name': strategy['name'],
        'description': strategy['description'],
        'models': [],
        'weights': strategy['weights'],
        'expected_score': strategy['expected_score'],
        'timestamp': pd.Timestamp.now().isoformat()
    }
    
    for i, model in enumerate(strategy['models']):
        config['models'].append({
            'experiment_id': model['experiment_id'],
            'model_name': model['model_name'],
            'submission_path': model['submission_path'],
            'server_score': model['server_score'],
            'weight': strategy['weights'][i]
        })
    
    return config

def main():
    """앙상블 전략 설정 및 저장"""
    
    print("🎪 앙상블 전략 설정 시스템")
    print("=" * 50)
    
    # 실험 결과 로드
    df = load_experiment_results()
    if df is None:
        return
    
    # 앙상블 후보 분석
    candidates = analyze_ensemble_candidates(df)
    if not candidates:
        return
    
    print(f"📊 앙상블 후보: {len(candidates)}개 모델")
    print("\n🏆 후보 모델들:")
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate['model_name']}: {candidate['server_score']:.4f}")
        print(f"   일반화 비율: {candidate['generalization_ratio']:.3f}")
    
    # 앙상블 전략 생성
    strategies = create_ensemble_strategy(candidates)
    
    print(f"\n🎯 생성된 앙상블 전략: {len(strategies)}개")
    
    # 전략별 저장
    ensemble_configs = []
    for strategy in strategies:
        config = create_ensemble_config(strategy)
        
        # 설정 파일 저장
        config_path = f"ensemble_strategy_{strategy['name']}.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        ensemble_configs.append(config)
        
        print(f"\n✅ {strategy['name']} 전략:")
        print(f"   📝 설명: {strategy['description']}")
        print(f"   🎯 예상 점수: {strategy['expected_score']:.4f}")
        print(f"   📁 설정 파일: {config_path}")
        print(f"   🏗️ 구성 모델:")
        for model, weight in zip(strategy['models'], strategy['weights']):
            print(f"      - {model['model_name']}: {weight:.3f} (점수: {model['server_score']:.4f})")
    
    # 실행 스크립트 생성
    create_ensemble_runner(ensemble_configs)
    
    print(f"\n🚀 다음 단계:")
    print(f"1. python ensemble_predictor.py --strategy top_performance")
    print(f"2. 결과 분석 후 최적 전략 선택")
    print(f"3. 최종 앙상블로 서버 제출")

def create_ensemble_runner(configs):
    """앙상블 실행 스크립트 생성"""
    
    runner_code = '''#!/usr/bin/env python3
"""
앙상블 예측 실행기
여러 모델의 예측 결과를 가중 평균하여 최종 예측 생성
"""

import pandas as pd
import numpy as np
import json
import argparse
from pathlib import Path

def weighted_ensemble_predictions(strategy_name):
    """가중 앙상블 예측 실행"""
    
    # 전략 설정 로드
    config_path = f"ensemble_strategy_{strategy_name}.json"
    if not Path(config_path).exists():
        print(f"❌ 설정 파일이 없습니다: {config_path}")
        return None
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"🎪 앙상블 실행: {config['description']}")
    print(f"📊 구성 모델: {len(config['models'])}개")
    
    # 개별 모델 예측 결과 로드
    predictions = []
    valid_models = []
    valid_weights = []
    
    for i, model_info in enumerate(config['models']):
        submission_path = model_info['submission_path']
        
        if Path(submission_path).exists():
            pred_df = pd.read_csv(submission_path)
            
            # ID와 target 컬럼 확인
            if 'ID' in pred_df.columns and 'target' in pred_df.columns:
                predictions.append(pred_df[['ID', 'target']])
                valid_models.append(model_info)
                valid_weights.append(config['weights'][i])
                print(f"✅ 로드: {model_info['model_name']} (가중치: {config['weights'][i]:.3f})")
            else:
                print(f"❌ 잘못된 형식: {submission_path}")
        else:
            print(f"❌ 파일 없음: {submission_path}")
    
    if len(predictions) < 2:
        print(f"❌ 앙상블에 필요한 최소 모델 수(2개) 미달: {len(predictions)}개")
        return None
    
    # 가중치 정규화
    total_weight = sum(valid_weights)
    normalized_weights = [w / total_weight for w in valid_weights]
    
    print(f"\\n🎯 앙상블 구성:")
    for model, weight in zip(valid_models, normalized_weights):
        print(f"   {model['model_name']}: {weight:.3f}")
    
    # 가중 평균 계산
    base_df = predictions[0][['ID']].copy()
    ensemble_targets = np.zeros(len(base_df))
    
    for pred_df, weight in zip(predictions, normalized_weights):
        # ID 순서 맞추기
        merged = base_df.merge(pred_df, on='ID', how='left')
        ensemble_targets += merged['target'].values * weight
    
    # 최종 결과 생성
    result_df = pd.DataFrame({
        'ID': base_df['ID'],
        'target': ensemble_targets
    })
    
    # 결과 저장
    output_path = f"ensemble_{strategy_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv"
    result_df.to_csv(output_path, index=False)
    
    print(f"\\n✅ 앙상블 완료!")
    print(f"📁 저장 경로: {output_path}")
    print(f"📊 예상 점수: {config['expected_score']:.4f}")
    print(f"🎯 다음 단계: AIStages에 {output_path} 제출")
    
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="앙상블 예측 실행")
    parser.add_argument('--strategy', type=str, required=True, 
                       choices=['top_performance', 'diversity_based', 'stable_generalization'],
                       help='앙상블 전략 선택')
    
    args = parser.parse_args()
    weighted_ensemble_predictions(args.strategy)
'''
    
    with open("ensemble_predictor.py", 'w') as f:
        f.write(runner_code)
    
    print(f"\n📝 앙상블 실행기 생성: ensemble_predictor.py")

if __name__ == "__main__":
    main()
