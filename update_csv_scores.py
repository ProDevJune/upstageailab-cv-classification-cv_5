#!/usr/bin/env python3
"""
enhanced_experiment_results.csv 파일에 최신 서버 점수를 직접 업데이트
"""

import pandas as pd
import numpy as np

def update_csv_with_server_scores():
    """CSV 파일을 읽어서 서버 점수를 업데이트합니다."""
    
    csv_path = "enhanced_experiment_results.csv"
    
    try:
        # CSV 파일 읽기
        df = pd.read_csv(csv_path)
        print(f"📋 {len(df)} 개의 실험 기록 로드됨")
        
        # 업데이트할 데이터
        updates = [
            {
                'search_id': '2507051934',
                'aistages_public_score': 0.8619,
                'submission_date': '2025-07-05',
                'submission_notes': 'EfficientNet-B4 v1 - 최고 성능 달성',
                'recommended_for_ensemble': True,
                'overfitting_risk': 'Low'
            },
            {
                'search_id': '2507052342', 
                'aistages_public_score': 0.8399,
                'submission_date': '2025-07-06',
                'submission_notes': 'EfficientNet-B4 v2 - train.csv 업데이트 후 성능 하락',
                'recommended_for_ensemble': False,
                'overfitting_risk': 'Moderate'
            },
            {
                'search_id': '2507052111',
                'aistages_public_score': 0.8526, 
                'submission_date': '2025-07-05',
                'submission_notes': 'EfficientNet-B3 v1 - 높은 성능',
                'recommended_for_ensemble': True,
                'overfitting_risk': 'Low'
            },
            {
                'search_id': '2507052151',
                'aistages_public_score': 0.8158,
                'submission_date': '2025-07-05', 
                'submission_notes': 'ConvNeXt-Base v1 - 준수한 성능',
                'recommended_for_ensemble': True,
                'overfitting_risk': 'Moderate'
            }
        ]
        
        updated_count = 0
        
        # 각 업데이트 항목 처리
        for update in updates:
            search_id = update['search_id']
            
            # 실험 ID로 검색 (부분 매칭)
            mask = df['experiment_id'].str.contains(search_id, na=False)
            matching_indices = df[mask].index
            
            if len(matching_indices) > 0:
                # 첫 번째 매칭되는 행 업데이트
                idx = matching_indices[0]
                
                print(f"\n🎯 업데이트 대상: {df.loc[idx, 'experiment_id']}")
                print(f"📊 모델: {df.loc[idx, 'model_name']}")
                print(f"🎯 서버 점수: {update['aistages_public_score']}")
                
                # 기본 업데이트
                df.loc[idx, 'aistages_submitted'] = True
                df.loc[idx, 'aistages_public_score'] = update['aistages_public_score']
                df.loc[idx, 'submission_date'] = update['submission_date']
                df.loc[idx, 'submission_notes'] = update['submission_notes']
                df.loc[idx, 'recommended_for_ensemble'] = update['recommended_for_ensemble']
                df.loc[idx, 'overfitting_risk'] = update['overfitting_risk']
                
                # 일반화 성능 계산
                if pd.notna(df.loc[idx, 'final_f1']) and df.loc[idx, 'final_f1'] > 0:
                    local_f1 = df.loc[idx, 'final_f1']
                    server_score = update['aistages_public_score']
                    
                    # 일반화 비율
                    generalization_ratio = server_score / local_f1
                    df.loc[idx, 'local_server_correlation'] = f"{generalization_ratio:.3f}"
                    
                    # 점수 차이 
                    score_diff = local_f1 - server_score
                    df.loc[idx, 'score_difference_public'] = score_diff
                    
                    print(f"📊 로컬 F1: {local_f1:.4f}")
                    print(f"📊 일반화 비율: {generalization_ratio:.3f} ({generalization_ratio*100:.1f}%)")
                    print(f"📊 점수 차이: {score_diff:.4f}")
                
                updated_count += 1
                print(f"✅ 업데이트 완료")
                
            else:
                print(f"❌ 실험 ID {search_id}를 찾을 수 없습니다.")
        
        if updated_count > 0:
            # 백업 생성
            backup_path = f"enhanced_experiment_results_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(backup_path, index=False)
            print(f"\n💾 백업 생성: {backup_path}")
            
            # 원본 파일 업데이트
            df.to_csv(csv_path, index=False)
            print(f"💾 원본 파일 업데이트: {csv_path}")
            print(f"🎯 총 {updated_count}개 실험 업데이트됨")
            
            # 업데이트된 결과 요약
            print(f"\n📊 업데이트된 서버 점수 요약:")
            submitted_experiments = df[df['aistages_submitted'] == True]
            submitted_experiments = submitted_experiments.sort_values('aistages_public_score', ascending=False)
            
            for _, row in submitted_experiments.iterrows():
                if pd.notna(row['aistages_public_score']):
                    print(f"• {row['model_name']}: {row['aistages_public_score']:.4f}")
            
        else:
            print("❌ 업데이트된 실험이 없습니다.")
            
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    print("🔄 CSV 파일 업데이트 시작...")
    update_csv_with_server_scores()
    print("\n✅ 업데이트 완료!")
