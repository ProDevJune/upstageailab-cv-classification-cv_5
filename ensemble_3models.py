#!/usr/bin/env python3
"""
3개 모델 직접 앙상블 (서버 성능 기반 가중치)
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def create_weighted_ensemble():
    """서버 성능 기반 가중 앙상블"""
    
    print("🎪 3개 모델 앙상블 구성")
    print("=" * 50)
    
    # 3개 모델 정보 (서버 점수 기반 가중치)
    models = {
        'EfficientNet-B4': {
            'path': 'data/submissions/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8619,
            'weight': 0.50,  # 최고 성능
            'exp_id': '2507051934'
        },
        'EfficientNet-B3': {
            'path': 'data/submissions/2507052111-efficientnet_b3.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507052111-efficientnet_b3.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8526,
            'weight': 0.35,  # 두 번째 성능
            'exp_id': '2507052111'
        },
        'ConvNeXt-Base': {
            'path': 'data/submissions/2507052151-convnext_base.fb_in22k_ft_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507052151-convnext_base.fb_in22k_ft_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8158,
            'weight': 0.15,  # 다양성 기여
            'exp_id': '2507052151'
        }
    }
    
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
                    print(f"✅ {model_name}: {len(df)}개 예측 로드")
                    print(f"   📁 {file_path.name}")
                    print(f"   🎯 서버 점수: {model_info['server_score']} (가중치: {model_info['weight']:.1%})")
                else:
                    print(f"❌ {model_name}: 잘못된 CSV 형식")
            except Exception as e:
                print(f"❌ {model_name} 로드 실패: {e}")
        else:
            print(f"❌ {model_name}: 파일 없음 - {file_path}")
    
    if len(predictions) < 2:
        print(f"\\n❌ 앙상블에 필요한 최소 모델 수 미달: {len(predictions)}개")
        return None
    
    print(f"\\n🎯 앙상블 구성 ({len(predictions)}개 모델):")
    
    # 기준 DataFrame (첫 번째 모델의 ID 순서 사용)
    first_model = list(predictions.keys())[0]
    base_df = predictions[first_model][['ID']].copy()
    ensemble_targets = np.zeros(len(base_df))
    
    total_weight = 0
    used_weights = []
    
    for model_name in predictions.keys():
        if model_name in valid_models:
            pred_df = predictions[model_name]
            weight = valid_models[model_name]['weight']
            server_score = valid_models[model_name]['server_score']
            
            # ID 순서 맞추기
            merged = base_df.merge(pred_df[['ID', 'target']], on='ID', how='left')
            
            if merged['target'].isna().any():
                print(f"⚠️ {model_name}: 누락된 예측 {merged['target'].isna().sum()}개")
                continue
            
            ensemble_targets += merged['target'].values * weight
            total_weight += weight
            used_weights.append(weight)
            
            print(f"   🔹 {model_name}: {weight:.1%} (점수: {server_score})")
    
    # 가중치 정규화
    if abs(total_weight - 1.0) > 0.001:
        print(f"\\n⚠️ 가중치 합: {total_weight:.3f} → 1.0으로 정규화")
        ensemble_targets = ensemble_targets / total_weight
        total_weight = 1.0
    
    # 최종 앙상블 결과
    result_df = pd.DataFrame({
        'ID': base_df['ID'],
        'target': ensemble_targets
    })
    
    # 예상 점수 계산 (가중 평균)
    expected_score = sum(valid_models[name]['server_score'] * valid_models[name]['weight'] 
                        for name in predictions.keys() if name in valid_models)
    expected_score = expected_score / total_weight
    
    # 개선 예상치
    best_single = max(valid_models[name]['server_score'] for name in valid_models.keys())
    improvement = expected_score - best_single
    
    # 결과 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"ensemble_golden_3models_{timestamp}.csv"
    result_df.to_csv(output_path, index=False)
    
    print(f"\\n✅ 앙상블 완료!")
    print(f"📁 출력 파일: {output_path}")
    print(f"📊 예상 점수: {expected_score:.4f}")
    print(f"🎯 예상 향상: {improvement:+.4f} (vs 최고 단일 모델)")
    print(f"🏆 목표: Public 0.88+ / Private 0.89+")
    
    print(f"\\n🚀 다음 단계:")
    print(f"1. AIStages에 {output_path} 제출")
    print(f"2. Public 점수 확인")
    print(f"3. Private 점수 대기")
    
    return output_path

if __name__ == "__main__":
    create_weighted_ensemble()
