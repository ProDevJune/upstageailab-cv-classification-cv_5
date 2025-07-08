#!/usr/bin/env python3
"""
개선된 train.csv 기반 3개 모델 앙상블 (v2)
EfficientNet-B4 + B3 + ConvNeXt-Base 완전 조합
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import os

def find_latest_experiment_results():
    """최신 실험 결과 자동 탐지"""
    submissions_dir = Path("data/submissions")
    
    # 새 실험 결과 패턴 찾기
    experiment_patterns = {
        'efficientnet_b4': None,
        'efficientnet_b3': None,
        'convnext_base': None
    }
    
    if submissions_dir.exists():
        for item in submissions_dir.iterdir():
            if item.is_dir():
                dir_name = item.name
                # EfficientNet-B4 찾기
                if 'efficientnet_b4' in dir_name and 'img320' in dir_name and 'onaug_eda' in dir_name:
                    csv_files = list(item.glob("*.csv"))
                    if csv_files:
                        experiment_patterns['efficientnet_b4'] = {
                            'path': csv_files[0],
                            'exp_id': dir_name.split('-')[0],
                            'dir_name': dir_name
                        }
                
                # EfficientNet-B3 찾기
                elif 'efficientnet_b3' in dir_name and 'img320' in dir_name and 'onaug_eda' in dir_name:
                    csv_files = list(item.glob("*.csv"))
                    if csv_files:
                        experiment_patterns['efficientnet_b3'] = {
                            'path': csv_files[0],
                            'exp_id': dir_name.split('-')[0],
                            'dir_name': dir_name
                        }
                
                # ConvNeXt-Base 찾기
                elif 'convnext_base' in dir_name and 'img320' in dir_name and 'onaug_eda' in dir_name:
                    csv_files = list(item.glob("*.csv"))
                    if csv_files:
                        experiment_patterns['convnext_base'] = {
                            'path': csv_files[0],
                            'exp_id': dir_name.split('-')[0],
                            'dir_name': dir_name
                        }
    
    return experiment_patterns

def create_3model_ensemble_v2():
    """개선된 데이터 기반 B4 + B3 + ConvNeXt 앙상블"""
    
    print("🎪 개선된 train.csv 기반 3모델 앙상블 v2")
    print("=" * 60)
    
    # 최신 실험 결과 자동 탐지
    experiments = find_latest_experiment_results()
    
    missing_models = []
    for model_name, exp_info in experiments.items():
        if not exp_info:
            missing_models.append(model_name)
    
    if missing_models:
        print(f"❌ 필요한 실험 결과를 찾을 수 없습니다: {missing_models}")
        print("\\n다음을 먼저 실행하세요:")
        if 'efficientnet_b4' in missing_models:
            print("   1. ./run_absolute.sh (EfficientNet-B4)")
        if 'efficientnet_b3' in missing_models:
            print("   2. ./run_b3.sh (EfficientNet-B3)")
        if 'convnext_base' in missing_models:
            print("   3. ./run_convnext.sh (ConvNeXt-Base)")
        return None
    
    # 모델 정보 구성 (개선된 데이터 예상 성능 기반)
    models = {
        'EfficientNet-B4': {
            'path': experiments['efficientnet_b4']['path'],
            'exp_id': experiments['efficientnet_b4']['exp_id'],
            'weight': 0.50,  # 최고 성능 예상
            'base_score': 0.8619,  # 기존 점수 참고
            'expected_improvement': 0.003
        },
        'EfficientNet-B3': {
            'path': experiments['efficientnet_b3']['path'],
            'exp_id': experiments['efficientnet_b3']['exp_id'],
            'weight': 0.35,  # 안정적 성능
            'base_score': 0.8526,
            'expected_improvement': 0.002
        },
        'ConvNeXt-Base': {
            'path': experiments['convnext_base']['path'],
            'exp_id': experiments['convnext_base']['exp_id'],
            'weight': 0.15,  # 다양성 기여
            'base_score': 0.8158,
            'expected_improvement': 0.004  # 가장 큰 개선 예상
        }
    }
    
    print("🔍 발견된 실험 결과:")
    
    # 모델별 예측 로드
    predictions = {}
    valid_models = {}
    
    for model_name, model_info in models.items():
        file_path = Path(model_info['path'])
        
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                if 'ID' in df.columns and 'target' in df.columns:
                    predictions[model_name] = df
                    valid_models[model_name] = model_info
                    expected_score = model_info['base_score'] + model_info['expected_improvement']
                    
                    print(f"✅ {model_name}")
                    print(f"   📁 {file_path.parent.name}")
                    print(f"   🆔 실험ID: {model_info['exp_id']}")
                    print(f"   📊 {len(df)}개 예측 (가중치: {model_info['weight']:.1%})")
                    print(f"   🎯 예상점수: {expected_score:.4f} (+{model_info['expected_improvement']:.3f})")
                else:
                    print(f"❌ {model_name}: 잘못된 CSV 형식")
                    return None
            except Exception as e:
                print(f"❌ {model_name} 로드 실패: {e}")
                return None
        else:
            print(f"❌ {model_name}: 파일 없음")
            return None
    
    if len(predictions) < 3:
        print(f"❌ 3개 모델을 모두 로드하지 못했습니다. ({len(predictions)}/3)")
        return None
    
    print(f"\\n🎯 앙상블 구성 (개선된 데이터v2):")
    
    # 기준 DataFrame
    base_df = predictions['EfficientNet-B4'][['ID']].copy()
    ensemble_targets = np.zeros(len(base_df))
    
    total_weight = 0
    model_contributions = []
    
    for model_name, model_info in valid_models.items():
        if model_name in predictions:
            pred_df = predictions[model_name]
            weight = model_info['weight']
            
            # ID 순서 맞추기
            merged = base_df.merge(pred_df[['ID', 'target']], on='ID', how='left')
            
            if merged['target'].isna().any():
                print(f"⚠️ {model_name}: 누락된 예측 {merged['target'].isna().sum()}개")
                continue
            
            ensemble_targets += merged['target'].values * weight
            total_weight += weight
            
            expected_score = model_info['base_score'] + model_info['expected_improvement']
            contribution = expected_score * weight
            model_contributions.append((model_name, weight, expected_score, contribution))
            
            print(f"   🔹 {model_name}: {weight:.1%} (실험ID: {model_info['exp_id']}, 예상: {expected_score:.4f})")
    
    # 가중치 정규화
    if abs(total_weight - 1.0) > 0.001:
        print(f"\\n⚠️ 가중치 합: {total_weight:.3f} → 1.0으로 정규화")
        ensemble_targets = ensemble_targets / total_weight
    
    # 최종 결과
    result_df = pd.DataFrame({
        'ID': base_df['ID'],
        'target': ensemble_targets
    })
    
    # 예상 앙상블 점수 계산
    expected_ensemble_score = sum(contrib[3] for contrib in model_contributions) / total_weight
    best_single_expected = max(contrib[2] for contrib in model_contributions)
    ensemble_improvement = expected_ensemble_score - best_single_expected
    
    # 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"ensemble_3models_v2_{timestamp}.csv"
    result_df.to_csv(output_path, index=False)
    
    # 결과 요약
    print(f"\\n✅ 3모델 앙상블 v2 완료!")
    print(f"📁 출력 파일: {output_path}")
    
    exp_ids = " + ".join([info['exp_id'] for info in valid_models.values()])
    print(f"🆔 사용 실험: {exp_ids}")
    print(f"📊 예상 앙상블 점수: {expected_ensemble_score:.4f}")
    print(f"🎯 예상 개선: {ensemble_improvement:+.4f} (vs 최고 단일)")
    print(f"💡 대회 제출 메모: '3모델 앙상블 B4+B3+ConvNeXt (개선된 데이터v2)'")
    
    # 실행 정보 기록
    result_info = {
        'file_path': output_path,
        'submission_memo': '3모델 앙상블 B4+B3+ConvNeXt (개선된 데이터v2)',
        'models_used': exp_ids,
        'expected_score': expected_ensemble_score,
        'expected_improvement': ensemble_improvement,
        'weights': {name: info['weight'] for name, info in valid_models.items()},
        'timestamp': timestamp
    }
    
    print(f"\\n📋 제출 정보:")
    print(f"   파일: {result_info['file_path']}")
    print(f"   메모: {result_info['submission_memo']}")
    print(f"   구성: {result_info['models_used']}")
    print(f"   예상점수: {result_info['expected_score']:.4f}")
    
    print(f"\\n🚀 다음 단계:")
    print(f"1. AIStages에 {output_path} 제출")
    print(f"2. 새 train.csv 효과 확인")
    print(f"3. 기존 결과 대비 성능 비교")
    
    return result_info

if __name__ == "__main__":
    create_3model_ensemble_v2()
