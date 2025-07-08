#!/usr/bin/env python3
"""
새로운 서버 채점 결과를 enhanced_experiment_results.csv에 기록하는 스크립트
"""

import pandas as pd
import os
from datetime import datetime

def record_new_server_scores():
    """새로운 서버 채점 결과를 기록합니다."""
    
    print("🎯 새로운 서버 채점 결과 기록 시스템")
    print("=" * 60)
    
    # 새로운 제출 결과들
    submissions = [
        {
            'experiment_id': '2507052342',  # EfficientNet-B4 v2 (train.csv 업데이트 후)
            'model_name': 'efficientnet_b4.ra2_in1k',
            'version': 'v2',
            'description': '320px + Minimal aug - No TTA v2 (train.csv 업데이트 후)',
            'aistages_public_score': 0.8399,
            'previous_score': 0.8619,  # v1 점수
            'performance_change': -0.0220,  # v2 - v1
            'submission_date': '2025-07-06',
            'submission_notes': 'train.csv 업데이트 후 성능 하락 확인'
        },
        {
            'experiment_id': '2507051934',  # EfficientNet-B4 v1 (원본)
            'model_name': 'efficientnet_b4.ra2_in1k',
            'version': 'v1',
            'description': '320px + Minimal aug - No TTA v1 (원본)',
            'aistages_public_score': 0.8619,
            'previous_score': None,
            'performance_change': None,
            'submission_date': '2025-07-05',
            'submission_notes': '높은 성능의 기준 모델'
        }
    ]
    
    # 앙상블 결과들
    ensemble_results = [
        {
            'ensemble_name': '3모델 앙상블 (B4+B3+ConvNeXt) v1',
            'models': ['EfficientNet-B4 v1', 'EfficientNet-B3 v1', 'ConvNeXt-Base v1'],
            'aistages_public_score': 0.7375,
            'submission_date': '2025-07-06',
            'ensemble_type': '3-model weighted ensemble',
            'notes': '예상보다 낮은 성능 - 모델 간 상관관계 높음'
        },
        {
            'ensemble_name': '2모델 앙상블 (B4+B3) v1',
            'models': ['EfficientNet-B4 v1', 'EfficientNet-B3 v1'],
            'aistages_public_score': 0.7958,
            'submission_date': '2025-07-06',
            'ensemble_type': '2-model weighted ensemble',
            'notes': '단일 모델보다 낮은 성능 - 다양성 부족'
        }
    ]
    
    print("📊 기록할 개별 모델 결과:")
    for sub in submissions:
        print(f"🆔 실험 ID: {sub['experiment_id']}")
        print(f"📋 모델: {sub['model_name']} {sub['version']}")
        print(f"🎯 서버 점수: {sub['aistages_public_score']:.4f}")
        if sub['previous_score']:
            change_pct = (sub['performance_change'] / sub['previous_score']) * 100
            print(f"📈 성능 변화: {sub['performance_change']:+.4f} ({change_pct:+.1f}%)")
        print(f"📝 설명: {sub['description']}")
        print("-" * 40)
    
    print("\n🎪 앙상블 결과:")
    for ens in ensemble_results:
        print(f"🔗 앙상블: {ens['ensemble_name']}")
        print(f"🎯 서버 점수: {ens['aistages_public_score']:.4f}")
        print(f"📋 구성 모델: {', '.join(ens['models'])}")
        print(f"📝 분석: {ens['notes']}")
        print("-" * 40)
    
    try:
        # CSV 파일 읽기
        csv_path = "enhanced_experiment_results.csv"
        if not os.path.exists(csv_path):
            print(f"❌ {csv_path} 파일을 찾을 수 없습니다.")
            return False
            
        df = pd.read_csv(csv_path)
        print(f"📋 총 {len(df)} 개의 실험 기록 발견")
        
        updated_count = 0
        
        # 각 제출 결과 업데이트
        for sub in submissions:
            # 실험 ID로 찾기 (부분 매칭)
            matching_experiments = df[df['experiment_id'].str.contains(sub['experiment_id'], na=False)]
            
            if len(matching_experiments) > 0:
                # 첫 번째 매칭되는 실험 선택
                idx = matching_experiments.index[0]
                experiment = df.loc[idx]
                
                print(f"\n🎯 매칭된 실험:")
                print(f"🆔 실험 ID: {experiment['experiment_id']}")
                print(f"📊 모델: {experiment['model_name']}")
                print(f"📈 로컬 F1: {experiment['final_f1']:.4f}")
                
                # 업데이트
                df.loc[idx, 'aistages_submitted'] = True
                df.loc[idx, 'submission_date'] = sub['submission_date']
                df.loc[idx, 'aistages_public_score'] = sub['aistages_public_score']
                df.loc[idx, 'submission_notes'] = sub['submission_notes']
                
                # 일반화 성능 계산
                if pd.notna(experiment['final_f1']) and experiment['final_f1'] > 0:
                    generalization_ratio = sub['aistages_public_score'] / experiment['final_f1']
                    df.loc[idx, 'local_server_correlation'] = f"{generalization_ratio:.3f}"
                    df.loc[idx, 'score_difference_public'] = experiment['final_f1'] - sub['aistages_public_score']
                    
                    # 성능 분석
                    if generalization_ratio > 0.90:
                        risk_level = "Very Low"
                        recommendation = True
                    elif generalization_ratio > 0.85:
                        risk_level = "Low"  
                        recommendation = True
                    elif generalization_ratio > 0.80:
                        risk_level = "Moderate"
                        recommendation = True
                    else:
                        risk_level = "High"
                        recommendation = False
                        
                    df.loc[idx, 'overfitting_risk'] = risk_level
                    df.loc[idx, 'recommended_for_ensemble'] = recommendation
                    
                    print(f"📊 일반화 비율: {generalization_ratio:.3f} ({generalization_ratio*100:.1f}%)")
                    print(f"⚠️ 과적합 위험: {risk_level}")
                    print(f"🎪 앙상블 추천: {recommendation}")
                
                updated_count += 1
                print(f"✅ 업데이트 완료")
                
            else:
                print(f"❌ 실험 ID {sub['experiment_id']}를 찾을 수 없습니다.")
        
        # 파일 저장
        if updated_count > 0:
            df.to_csv(csv_path, index=False)
            print(f"\n📁 {updated_count}개 실험 업데이트 완료: {csv_path}")
        
        # 앙상블 결과를 별도 파일에 기록
        ensemble_df = pd.DataFrame(ensemble_results)
        ensemble_csv_path = "ensemble_server_results.csv"
        ensemble_df.to_csv(ensemble_csv_path, index=False)
        print(f"📁 앙상블 결과 저장: {ensemble_csv_path}")
        
        # 종합 분석
        print(f"\n📊 종합 분석:")
        print(f"🎯 최고 단일 모델: EfficientNet-B4 v1 (0.8619)")
        print(f"📉 train.csv 업데이트 영향: -2.2% 성능 하락")
        print(f"🎪 앙상블 성능: 단일 모델보다 낮음")
        
        print(f"\n💡 핵심 인사이트:")
        print(f"1. train.csv 업데이트가 성능에 부정적 영향")
        print(f"2. 앙상블보다 단일 모델이 더 우수한 성능")
        print(f"3. 모델 간 다양성 부족으로 앙상블 효과 제한적")
        
        print(f"\n🚀 권장 전략:")
        print(f"1. EfficientNet-B4 v1 모델을 주력으로 사용")
        print(f"2. train.csv 변경사항 재검토 필요")
        print(f"3. 더 다양한 아키텍처로 앙상블 구성")
        print(f"4. 개별 모델 성능 최적화에 집중")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = record_new_server_scores()
    if success:
        print("\n🎉 서버 채점 결과 기록 완료!")
    else:
        print("\n💔 기록 실패")
