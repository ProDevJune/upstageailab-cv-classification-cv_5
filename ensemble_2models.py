#!/usr/bin/env python3
"""
2개 모델 앙상블 (ConvNeXt 제외)
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def create_2model_ensemble():
    """B4 + B3 앙상블 (ConvNeXt 제외)"""
    
    print("🎪 2개 모델 앙상블 구성 (성능 최적화)")
    print("=" * 50)
    
    # 2개 모델만 사용 (ConvNeXt 제외)
    models = {
        'EfficientNet-B4': {
            'path': 'data/submissions/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8619,
            'weight': 0.70,  # 최고 성능에 높은 비중
        },
        'EfficientNet-B3': {
            'path': 'data/submissions/2507052111-efficientnet_b3.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507052111-efficientnet_b3.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8526,
            'weight': 0.30,  # 안정성 기여
        }
    }
    
    # 모델별 예측 로드
    predictions = {}
    
    for model_name, model_info in models.items():
        file_path = Path(model_info['path'])
        
        if file_path.exists():
            df = pd.read_csv(file_path)
            predictions[model_name] = df
            print(f"✅ {model_name}: {len(df)}개 예측 로드")
            print(f"   🎯 서버 점수: {model_info['server_score']} (가중치: {model_info['weight']:.0%})")
        else:
            print(f"❌ {model_name}: 파일 없음")
            return None
    
    if len(predictions) != 2:
        print("❌ 2개 모델을 모두 로드하지 못했습니다.")
        return None
    
    print(f"\\n🎯 최적화된 2모델 앙상블:")
    
    # 기준 DataFrame
    base_df = predictions['EfficientNet-B4'][['ID']].copy()
    ensemble_targets = np.zeros(len(base_df))
    
    for model_name, model_info in models.items():
        if model_name in predictions:
            pred_df = predictions[model_name]
            weight = model_info['weight']
            
            # ID 순서 맞추기
            merged = base_df.merge(pred_df[['ID', 'target']], on='ID', how='left')
            ensemble_targets += merged['target'].values * weight
            
            print(f"   🔹 {model_name}: {weight:.0%} (점수: {model_info['server_score']})")
    
    # 최종 결과
    result_df = pd.DataFrame({
        'ID': base_df['ID'],
        'target': ensemble_targets
    })
    
    # 예상 점수
    expected_score = sum(models[name]['server_score'] * models[name]['weight'] 
                        for name in models.keys())
    best_single = max(models[name]['server_score'] for name in models.keys())
    improvement = expected_score - best_single
    
    # 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"ensemble_2models_optimized_{timestamp}.csv"
    result_df.to_csv(output_path, index=False)
    
    print(f"\\n✅ 2모델 앙상블 완료!")
    print(f"📁 출력 파일: {output_path}")
    print(f"📊 예상 점수: {expected_score:.4f}")
    print(f"🎯 예상 향상: {improvement:+.4f} (vs 최고 단일)")
    print(f"💡 ConvNeXt 제외로 성능 손실 방지")
    
    print(f"\\n🚀 비교:")
    print(f"   3모델 앙상블: 0.8517 (ConvNeXt 포함)")
    print(f"   2모델 앙상블: {expected_score:.4f} (ConvNeXt 제외)")
    print(f"   차이: {expected_score - 0.8517:+.4f}")
    
    return output_path

if __name__ == "__main__":
    create_2model_ensemble()
