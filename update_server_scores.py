#!/usr/bin/env python3
"""
3개 모델의 서버 점수를 CSV에 업데이트
"""
import pandas as pd
from pathlib import Path

def update_scores():
    csv_path = "enhanced_experiment_results.csv"
    df = pd.read_csv(csv_path)
    
    print("🔄 서버 점수 업데이트 중...")
    
    updated_count = 0
    
    # 각 행을 확인하고 업데이트
    for idx, row in df.iterrows():
        exp_id = str(row['experiment_id'])
        model_name = str(row.get('model_name', ''))
        
        # EfficientNet-B4 (2507051934)
        if exp_id == '2507051934' or 'efficientnet_b4' in model_name:
            df.loc[idx, 'aistages_submitted'] = True
            df.loc[idx, 'aistages_public_score'] = 0.8619
            df.loc[idx, 'submission_date'] = '2025-07-05'
            df.loc[idx, 'recommended_for_ensemble'] = True
            print(f"✅ EfficientNet-B4 ({exp_id}): 0.8619")
            updated_count += 1
            
        # EfficientNet-B3 (2507052111)
        elif exp_id == '2507052111' or 'efficientnet_b3' in model_name:
            df.loc[idx, 'aistages_submitted'] = True
            df.loc[idx, 'aistages_public_score'] = 0.8526
            df.loc[idx, 'submission_date'] = '2025-07-05'
            df.loc[idx, 'recommended_for_ensemble'] = True
            print(f"✅ EfficientNet-B3 ({exp_id}): 0.8526")
            updated_count += 1
            
        # ConvNeXt-Base (2507052151)
        elif exp_id == '2507052151' or 'convnext' in model_name:
            df.loc[idx, 'aistages_submitted'] = True
            df.loc[idx, 'aistages_public_score'] = 0.8158
            df.loc[idx, 'submission_date'] = '2025-07-05'
            df.loc[idx, 'recommended_for_ensemble'] = True
            print(f"✅ ConvNeXt-Base ({exp_id}): 0.8158")
            updated_count += 1
    
    # 저장
    df.to_csv(csv_path, index=False)
    print(f"\n📁 {updated_count}개 모델 업데이트 완료: {csv_path}")
    
    # 확인
    submitted = df[df['aistages_submitted'] == True]
    print(f"\n🏆 제출된 모델들 ({len(submitted)}개):")
    for _, row in submitted.iterrows():
        if pd.notna(row['aistages_public_score']):
            print(f"- {row['model_name']}: {row['aistages_public_score']}")

if __name__ == "__main__":
    update_scores()
