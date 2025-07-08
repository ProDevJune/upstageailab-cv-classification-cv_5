#!/usr/bin/env python3
"""
AIStages 제출 결과를 enhanced_experiment_results.csv에 기록하는 스크립트
"""

import pandas as pd
import os
from datetime import datetime

def record_aistages_submission():
    """AIStages 제출 결과를 기록합니다."""
    
    print("🎯 AIStages 제출 결과 기록 시스템")
    print("=" * 50)
    
    # 제출 정보
    submission_data = {
        'model_name_submitted': 'ResNet50_F1937_exp005',
        'submission_date': '2025-07-05',
        'submission_time': '16:15',
        'aistages_public_score': 0.7629,
        'local_f1_score': 0.9370,
        'score_difference': 0.1741,  # local - server
        'overfitting_risk': 'High',
        'submission_notes': 'First submission of best performing model'
    }
    
    print(f"📊 기록할 제출 정보:")
    print(f"🆔 모델명: {submission_data['model_name_submitted']}")
    print(f"📅 제출일: {submission_data['submission_date']} {submission_data['submission_time']}")
    print(f"🎯 Local F1: {submission_data['local_f1_score']:.4f}")
    print(f"🌐 Server Score: {submission_data['aistages_public_score']:.4f}")
    print(f"📉 성능 차이: {submission_data['score_difference']:.4f} ({submission_data['score_difference']*100:.1f}% 하락)")
    print(f"⚠️ 과적합 위험: {submission_data['overfitting_risk']}")
    
    try:
        # CSV 파일 읽기
        csv_path = "enhanced_experiment_results.csv"
        if not os.path.exists(csv_path):
            print(f"❌ {csv_path} 파일을 찾을 수 없습니다.")
            return False
            
        df = pd.read_csv(csv_path)
        print(f"📋 총 {len(df)} 개의 실험 기록 발견")
        
        # ResNet50 실험 중 F1 스코어가 0.937에 가장 가까운 것 찾기
        resnet50_experiments = df[df['model_name'].str.contains('resnet50', case=False, na=False)]
        
        if len(resnet50_experiments) == 0:
            print("❌ ResNet50 실험을 찾을 수 없습니다.")
            return False
        
        # F1 스코어 차이로 가장 가까운 실험 찾기
        resnet50_experiments['f1_diff'] = abs(resnet50_experiments['final_f1'] - submission_data['local_f1_score'])
        target_experiment = resnet50_experiments.loc[resnet50_experiments['f1_diff'].idxmin()]
        
        print(f"\n🎯 매칭된 실험:")
        print(f"🆔 실험 ID: {target_experiment['experiment_id']}")
        print(f"📊 F1 Score: {target_experiment['final_f1']:.4f}")
        print(f"🔍 차이: {target_experiment['f1_diff']:.6f}")
        
        # 업데이트
        idx = target_experiment.name
        df.loc[idx, 'aistages_submitted'] = True
        df.loc[idx, 'submission_date'] = submission_data['submission_date']
        df.loc[idx, 'submission_time'] = submission_data['submission_time']
        df.loc[idx, 'aistages_public_score'] = submission_data['aistages_public_score']
        df.loc[idx, 'score_difference_public'] = submission_data['score_difference']
        df.loc[idx, 'overfitting_risk'] = submission_data['overfitting_risk']
        df.loc[idx, 'submission_notes'] = submission_data['submission_notes']
        df.loc[idx, 'recommended_for_ensemble'] = False  # 높은 과적합 위험으로 비추천
        
        # 파일 저장
        df.to_csv(csv_path, index=False)
        
        print(f"\n✅ 성공적으로 기록 완료!")
        print(f"📁 파일: {csv_path}")
        print(f"🆔 업데이트된 실험: {target_experiment['experiment_id']}")
        
        # 분석 결과 출력
        print(f"\n📊 과적합 분석:")
        if submission_data['score_difference'] > 0.15:
            print(f"❌ 심각한 과적합 (15% 이상 성능 저하)")
            print(f"💡 권장: 정규화 대폭 강화, 다른 모델 시도")
        elif submission_data['score_difference'] > 0.05:
            print(f"⚠️ 높은 과적합 위험 (5-15% 성능 저하)")
            print(f"💡 권장: 증강 강화, 앙상블 신중 고려")
        else:
            print(f"✅ 안정적인 성능")
        
        print(f"\n🚀 다음 단계 권장:")
        print(f"1. 다른 고성능 모델 2-3개 더 제출하여 패턴 파악")
        print(f"2. 정규화가 더 강한 모델 개발")
        print(f"3. 로컬 검증 전략 재검토")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = record_aistages_submission()
    if success:
        print("\n🎉 제출 결과 기록 완료!")
    else:
        print("\n💔 기록 실패")
