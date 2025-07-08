#!/usr/bin/env python3
"""
제공된 최신 서버 채점 결과를 정확히 기록하는 스크립트
"""

import pandas as pd
import os
from datetime import datetime

def record_latest_server_scores():
    """최신 서버 채점 결과를 정확히 기록합니다."""
    
    print("🎯 최신 서버 채점 결과 기록")
    print("=" * 50)
    
    # 사용자가 제공한 정확한 결과들
    latest_results = [
        {
            'model': 'EfficientNet-B4 - 320px + Minimal aug - No TTA v2',
            'experiment_id': '2507052342',  # v2 (train.csv 업데이트 후)
            'server_score': 0.8399,
            'submission_date': '2025-07-06',
            'notes': 'train.csv 업데이트 후 성능 하락',
            'comparison': 'v1 대비 -0.0220 하락'
        },
        {
            'model': 'EfficientNet-B4 - 320px + Minimal aug - No TTA v1',
            'experiment_id': '2507051934',  # v1 (원본)
            'server_score': 0.8619,
            'submission_date': '2025-07-05', 
            'notes': '최고 성능 달성',
            'comparison': '기준 모델'
        },
        {
            'ensemble': '3모델 앙상블 (B4+B3+ConvNeXt) v1',
            'server_score': 0.7375,
            'submission_date': '2025-07-06',
            'notes': '예상보다 매우 낮은 성능',
            'components': ['EfficientNet-B4 v1', 'EfficientNet-B3 v1', 'ConvNeXt-Base v1']
        },
        {
            'ensemble': '2모델 앙상블 (B4+B3) v1',
            'server_score': 0.7958,
            'submission_date': '2025-07-06', 
            'notes': '단일 모델보다 낮은 성능',
            'components': ['EfficientNet-B4 v1', 'EfficientNet-B3 v1']
        }
    ]
    
    print("📊 기록할 결과들:")
    for i, result in enumerate(latest_results, 1):
        if 'ensemble' in result:
            print(f"{i}. 🎪 {result['ensemble']}: {result['server_score']:.4f}")
            print(f"   📋 구성: {', '.join(result['components'])}")
        else:
            print(f"{i}. 🤖 {result['model']}: {result['server_score']:.4f}")
            if 'comparison' in result:
                print(f"   📊 비교: {result['comparison']}")
        print(f"   📝 {result['notes']}")
        print()
    
    # 분석
    print("💡 핵심 분석:")
    
    # v1 vs v2 비교
    v1_score = next(r['server_score'] for r in latest_results if r.get('experiment_id') == '2507051934')
    v2_score = next(r['server_score'] for r in latest_results if r.get('experiment_id') == '2507052342')
    train_csv_impact = ((v2_score - v1_score) / v1_score) * 100
    
    print(f"1. 📉 train.csv 업데이트 영향:")
    print(f"   • v1: {v1_score:.4f} → v2: {v2_score:.4f}")
    print(f"   • 변화: {v2_score - v1_score:+.4f} ({train_csv_impact:+.1f}%)")
    print(f"   • 결론: train.csv 업데이트가 성능에 부정적 영향")
    
    # 앙상블 vs 단일모델
    best_single = max(v1_score, v2_score)
    best_ensemble = max(r['server_score'] for r in latest_results if 'ensemble' in r)
    ensemble_gap = best_single - best_ensemble
    
    print(f"\n2. 🎪 앙상블 vs 단일모델:")
    print(f"   • 최고 단일모델: {best_single:.4f}")
    print(f"   • 최고 앙상블: {best_ensemble:.4f}")  
    print(f"   • 차이: -{ensemble_gap:.4f} ({-ensemble_gap/best_single*100:.1f}%)")
    print(f"   • 결론: 앙상블이 오히려 성능 저하")
    
    # 순위 매기기
    all_scores = []
    for result in latest_results:
        score = result['server_score']
        if 'ensemble' in result:
            name = result['ensemble']
        else:
            name = result['model']
        all_scores.append((name, score))
    
    all_scores.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 성능 순위:")
    for rank, (name, score) in enumerate(all_scores, 1):
        print(f"{rank}. {name}: {score:.4f}")
    
    # CSV 업데이트 시도
    try:
        csv_path = "enhanced_experiment_results.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print(f"\n📋 CSV 파일 발견: {len(df)} 실험")
            
            updated_count = 0
            
            # EfficientNet-B4 실험들 업데이트
            for result in latest_results:
                if 'experiment_id' in result:
                    exp_id = result['experiment_id']
                    # 부분 매칭으로 실험 찾기
                    matching = df[df['experiment_id'].str.contains(exp_id, na=False)]
                    
                    if len(matching) > 0:
                        idx = matching.index[0]
                        df.loc[idx, 'aistages_submitted'] = True
                        df.loc[idx, 'submission_date'] = result['submission_date']
                        df.loc[idx, 'aistages_public_score'] = result['server_score']
                        df.loc[idx, 'submission_notes'] = result['notes']
                        
                        # 일반화 성능 계산
                        if pd.notna(df.loc[idx, 'final_f1']) and df.loc[idx, 'final_f1'] > 0:
                            local_f1 = df.loc[idx, 'final_f1']
                            server_score = result['server_score']
                            generalization = server_score / local_f1
                            
                            df.loc[idx, 'local_server_correlation'] = f"{generalization:.3f}"
                            df.loc[idx, 'score_difference_public'] = local_f1 - server_score
                            
                            # 추천 여부 결정
                            if exp_id == '2507051934':  # v1 (최고 성능)
                                df.loc[idx, 'recommended_for_ensemble'] = True
                                df.loc[idx, 'overfitting_risk'] = 'Low'
                            else:  # v2 (성능 하락)
                                df.loc[idx, 'recommended_for_ensemble'] = False
                                df.loc[idx, 'overfitting_risk'] = 'Moderate'
                        
                        updated_count += 1
                        print(f"✅ 업데이트: {exp_id} → {result['server_score']:.4f}")
            
            # 저장
            if updated_count > 0:
                df.to_csv(csv_path, index=False)
                print(f"\n💾 {updated_count}개 실험 업데이트 완료")
        
        # 앙상블 결과 별도 저장
        ensemble_data = []
        for result in latest_results:
            if 'ensemble' in result:
                ensemble_data.append({
                    'ensemble_name': result['ensemble'],
                    'server_score': result['server_score'],
                    'submission_date': result['submission_date'],
                    'components': ', '.join(result['components']),
                    'notes': result['notes']
                })
        
        if ensemble_data:
            ensemble_df = pd.DataFrame(ensemble_data)
            ensemble_path = "latest_ensemble_results.csv"
            ensemble_df.to_csv(ensemble_path, index=False)
            print(f"💾 앙상블 결과 저장: {ensemble_path}")
        
    except Exception as e:
        print(f"❌ CSV 업데이트 오류: {e}")
    
    # 권장사항
    print(f"\n🚀 권장 전략:")
    print(f"1. 🎯 EfficientNet-B4 v1 모델을 메인으로 사용")
    print(f"2. 📊 train.csv 변경사항 검토/롤백 고려")
    print(f"3. 🔍 앙상블 대신 다양한 단일 모델 개발")
    print(f"4. 📈 ViT, Swin Transformer 등 새로운 아키텍처 시도")
    print(f"5. 🎪 모델 다양성 확보 후 재앙상블 시도")
    
    print(f"\n✅ 기록 완료!")
    return True

if __name__ == "__main__":
    record_latest_server_scores()
