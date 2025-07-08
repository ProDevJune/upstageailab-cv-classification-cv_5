#!/usr/bin/env python3
"""
서버 채점 결과 종합 분석 및 업데이트 (최신 결과 반영)
"""

import pandas as pd
import os
from datetime import datetime

def update_comprehensive_server_analysis():
    """최신 서버 채점 결과를 종합 분석하여 기록합니다."""
    
    print("🎯 서버 채점 결과 종합 분석 및 업데이트")
    print("=" * 60)
    
    # 모든 서버 제출 결과 (최신 업데이트)
    all_submissions = {
        # 기존 결과들 (이전 분석 결과)
        'ResNet50_F1937_exp005': {
            'model_name': 'resnet50.tv2_in1k',
            'image_size': 224,
            'augmentation': 'baseline',
            'aistages_score': 0.7629,
            'submission_date': '2025-07-05',
            'notes': '첫 제출 - 기준선'
        },
        'ResNet50_320px_Strong_exp006': {
            'model_name': 'resnet50.tv2_in1k', 
            'image_size': 320,
            'augmentation': 'strong',
            'aistages_score': 0.7664,
            'submission_date': '2025-07-05',
            'notes': '강한 증강 실험'
        },
        'ResNet50_320px_TTA_exp013': {
            'model_name': 'resnet50.tv2_in1k',
            'image_size': 320, 
            'augmentation': 'moderate',
            'TTA': True,
            'aistages_score': 0.8111,
            'submission_date': '2025-07-05',
            'notes': 'TTA 적용 실험'
        },
        'ResNet50_320px_NoTTA_exp024': {
            'model_name': 'resnet50.tv2_in1k',
            'image_size': 320,
            'augmentation': 'moderate', 
            'TTA': False,
            'aistages_score': 0.8239,
            'submission_date': '2025-07-05',
            'notes': '최고 성능 ResNet50'
        },
        
        # 새로운 결과들 (최신)
        'EfficientNet-B4_v1': {
            'experiment_id': '2507051934',
            'model_name': 'efficientnet_b4.ra2_in1k',
            'image_size': 320,
            'augmentation': 'minimal',
            'TTA': False,
            'aistages_score': 0.8619,  # 최고 점수
            'submission_date': '2025-07-05',
            'notes': '최고 성능 달성'
        },
        'EfficientNet-B4_v2': {
            'experiment_id': '2507052342',
            'model_name': 'efficientnet_b4.ra2_in1k',
            'image_size': 320,
            'augmentation': 'minimal',
            'TTA': False,
            'aistages_score': 0.8399,  # train.csv 업데이트 후
            'submission_date': '2025-07-06',
            'notes': 'train.csv 업데이트 후 성능 하락'
        },
        'EfficientNet-B3_v1': {
            'experiment_id': '2507052111',
            'model_name': 'efficientnet_b3.ra2_in1k', 
            'image_size': 320,
            'augmentation': 'minimal',
            'TTA': False,
            'aistages_score': 0.8526,
            'submission_date': '2025-07-05',
            'notes': '높은 성능'
        },
        'ConvNeXt-Base_v1': {
            'experiment_id': '2507052151',
            'model_name': 'convnext_base.fb_in22k_ft_in1k',
            'image_size': 320,
            'augmentation': 'minimal', 
            'TTA': False,
            'aistages_score': 0.8158,
            'submission_date': '2025-07-05',
            'notes': '준수한 성능'
        }
    }
    
    # 앙상블 결과들
    ensemble_results = {
        '3Model_Ensemble_v1': {
            'models': ['EfficientNet-B4 v1', 'EfficientNet-B3 v1', 'ConvNeXt-Base v1'],
            'individual_scores': [0.8619, 0.8526, 0.8158],
            'ensemble_score': 0.7375,
            'expected_improvement': False,
            'actual_improvement': -13.0,  # 상당한 성능 하락
            'notes': '예상과 달리 성능 하락 - 모델 다양성 부족'
        },
        '2Model_Ensemble_v1': {
            'models': ['EfficientNet-B4 v1', 'EfficientNet-B3 v1'], 
            'individual_scores': [0.8619, 0.8526],
            'ensemble_score': 0.7958,
            'expected_improvement': False,
            'actual_improvement': -7.7,  # 성능 하락
            'notes': '단일 모델보다 낮은 성능'
        }
    }
    
    print("📊 개별 모델 성능 순위:")
    sorted_models = sorted(all_submissions.items(), 
                          key=lambda x: x[1]['aistages_score'], 
                          reverse=True)
    
    for rank, (model_name, data) in enumerate(sorted_models, 1):
        print(f"{rank}. {model_name}: {data['aistages_score']:.4f} 🎯")
        print(f"   📋 {data['model_name']} | 🖼️ {data['image_size']}px | 📝 {data['notes']}")
    
    print(f"\n🎪 앙상블 성능 분석:")
    for ens_name, ens_data in ensemble_results.items():
        print(f"🔗 {ens_name}: {ens_data['ensemble_score']:.4f}")
        avg_individual = sum(ens_data['individual_scores']) / len(ens_data['individual_scores'])
        print(f"   📊 개별 평균: {avg_individual:.4f}")
        print(f"   📉 성능 변화: {ens_data['actual_improvement']:+.1f}%")
        print(f"   📝 {ens_data['notes']}")
    
    # 주요 인사이트 분석
    print(f"\n💡 핵심 인사이트:")
    
    # 1. 최고 성능 모델
    best_model = max(all_submissions.items(), key=lambda x: x[1]['aistages_score'])
    print(f"1. 🏆 최고 성능: {best_model[0]} ({best_model[1]['aistages_score']:.4f})")
    
    # 2. train.csv 업데이트 영향
    v1_score = all_submissions['EfficientNet-B4_v1']['aistages_score']
    v2_score = all_submissions['EfficientNet-B4_v2']['aistages_score']
    train_csv_impact = ((v2_score - v1_score) / v1_score) * 100
    print(f"2. 📉 train.csv 업데이트 영향: {train_csv_impact:+.1f}% ({v1_score:.4f} → {v2_score:.4f})")
    
    # 3. 앙상블 효과
    best_ensemble = max(ensemble_results.items(), key=lambda x: x[1]['ensemble_score'])
    best_individual = best_model[1]['aistages_score']
    ensemble_gap = best_individual - best_ensemble[1]['ensemble_score']
    print(f"3. 🎪 앙상블 vs 단일모델: -{ensemble_gap:.4f} ({-ensemble_gap/best_individual*100:.1f}% 하락)")
    
    # 4. 모델별 특성
    print(f"4. 🔍 모델별 특성:")
    print(f"   • EfficientNet 계열: 최고 성능 (B4 > B3)")
    print(f"   • 320px 해상도: 일관된 성능 향상")
    print(f"   • Minimal 증강: 최적 전략")
    print(f"   • TTA 비활성화: 더 좋은 성능")
    
    # 결과를 새로운 분석 파일에 저장
    analysis_data = {
        'model_name': [],
        'architecture': [],
        'image_size': [],
        'augmentation': [],
        'TTA': [],
        'aistages_score': [],
        'submission_date': [],
        'rank': [],
        'notes': []
    }
    
    for rank, (model_name, data) in enumerate(sorted_models, 1):
        analysis_data['model_name'].append(model_name)
        analysis_data['architecture'].append(data['model_name'])
        analysis_data['image_size'].append(data['image_size'])
        analysis_data['augmentation'].append(data['augmentation'])
        analysis_data['TTA'].append(data.get('TTA', False))
        analysis_data['aistages_score'].append(data['aistages_score'])
        analysis_data['submission_date'].append(data['submission_date'])
        analysis_data['rank'].append(rank)
        analysis_data['notes'].append(data['notes'])
    
    # DataFrame 생성 및 저장
    analysis_df = pd.DataFrame(analysis_data)
    analysis_path = "comprehensive_server_analysis.csv"
    analysis_df.to_csv(analysis_path, index=False)
    print(f"\n📁 종합 분석 저장: {analysis_path}")
    
    # 앙상블 결과도 저장
    ensemble_data = []
    for ens_name, ens_info in ensemble_results.items():
        ensemble_data.append({
            'ensemble_name': ens_name,
            'component_models': ' + '.join(ens_info['models']),
            'individual_avg': sum(ens_info['individual_scores']) / len(ens_info['individual_scores']),
            'ensemble_score': ens_info['ensemble_score'],
            'improvement_pct': ens_info['actual_improvement'],
            'notes': ens_info['notes']
        })
    
    ensemble_df = pd.DataFrame(ensemble_data)
    ensemble_path = "ensemble_analysis.csv"
    ensemble_df.to_csv(ensemble_path, index=False)
    print(f"📁 앙상블 분석 저장: {ensemble_path}")
    
    # 전략 업데이트
    print(f"\n🚀 업데이트된 전략:")
    print(f"1. 🎯 EfficientNet-B4 v1을 주력 모델로 확정")
    print(f"2. 📊 train.csv 변경사항 롤백 검토")
    print(f"3. 🎪 앙상블 대신 단일 모델 최적화 집중")
    print(f"4. 🔍 더 다양한 아키텍처 실험 (ViT, Swin 등)")
    print(f"5. 📈 목표: 0.87+ 달성을 위한 새로운 접근")
    
    return True

if __name__ == "__main__":
    success = update_comprehensive_server_analysis()
    if success:
        print("\n🎉 종합 분석 업데이트 완료!")
    else:
        print("\n💔 분석 실패")
