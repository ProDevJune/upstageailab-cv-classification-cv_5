#!/usr/bin/env python3
"""
정수 target 보장하는 앙상블 스크립트
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

def create_fixed_ensemble():
    """정수 target 보장하는 앙상블"""
    
    print("🎪 수정된 앙상블 구성 (정수 target 보장)")
    print("=" * 50)
    
    # 2모델 앙상블 (ConvNeXt 제외)
    models = {
        'EfficientNet-B4': {
            'path': 'data/submissions/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8619,
            'weight': 0.70,
        },
        'EfficientNet-B3': {
            'path': 'data/submissions/2507052111-efficientnet_b3.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0/2507052111-efficientnet_b3.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv',
            'server_score': 0.8526,
            'weight': 0.30,
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
        else:
            print(f"❌ {model_name}: 파일 없음")
            return None
    
    if len(predictions) != 2:
        print("❌ 2개 모델을 모두 로드하지 못했습니다.")
        return None
    
    # 앙상블 계산
    base_df = predictions['EfficientNet-B4'][['ID']].copy()
    ensemble_targets = np.zeros(len(base_df))
    
    for model_name, model_info in models.items():
        pred_df = predictions[model_name]
        weight = model_info['weight']
        
        merged = base_df.merge(pred_df[['ID', 'target']], on='ID', how='left')
        ensemble_targets += merged['target'].values * weight
        
        print(f"🔹 {model_name}: {weight:.0%} (점수: {model_info['server_score']})")
    
    # ⭐ 핵심: 정수로 반올림 처리
    ensemble_targets_int = np.round(ensemble_targets).astype(int)
    
    # 최종 결과
    result_df = pd.DataFrame({
        'ID': base_df['ID'],
        'target': ensemble_targets_int  # 정수 보장
    })
    
    # 검증
    print(f"\\n🔍 Target 검증:")
    print(f"   데이터 타입: {result_df['target'].dtype}")
    print(f"   최소값: {result_df['target'].min()}")
    print(f"   최대값: {result_df['target'].max()}")
    print(f"   유니크 클래스: {result_df['target'].nunique()}개")
    print(f"   샘플 예시: {result_df['target'].head().tolist()}")
    
    # 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"ensemble_2models_fixed_{timestamp}.csv"
    result_df.to_csv(output_path, index=False)
    
    expected_score = sum(models[name]['server_score'] * models[name]['weight'] 
                        for name in models.keys())
    
    print(f"\\n✅ 수정된 앙상블 완료!")
    print(f"📁 출력 파일: {output_path}")
    print(f"📊 예상 점수: {expected_score:.4f}")
    print(f"🎯 정수 target 보장으로 제출 가능")
    
    return output_path

if __name__ == "__main__":
    create_fixed_ensemble()
