#!/usr/bin/env python3
"""
train.csv 업데이트 후 성능 하락 원인 분석
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_performance_drop():
    """train.csv 업데이트 후 성능 하락 원인을 심층 분석합니다."""
    
    print("🔍 train.csv 업데이트 후 성능 하락 원인 분석")
    print("=" * 60)
    
    # 성능 변화 요약
    performance_data = {
        'Model': 'EfficientNet-B4',
        'v1_score': 0.8619,
        'v2_score': 0.8399, 
        'change': -0.0220,
        'change_pct': -2.6
    }
    
    print(f"📊 성능 변화 요약:")
    print(f"• 모델: {performance_data['Model']}")
    print(f"• v1 (원본): {performance_data['v1_score']:.4f}")
    print(f"• v2 (업데이트 후): {performance_data['v2_score']:.4f}")
    print(f"• 변화: {performance_data['change']:+.4f} ({performance_data['change_pct']:+.1f}%)")
    
    # 파일 분석 시도
    current_file = "data/train.csv"
    backup_files = ["data/train_backup_20250705_231253.csv", "data/train_backup_20250705_233639.csv"]
    
    print(f"\n📁 파일 분석:")
    if Path(current_file).exists():
        try:
            current_df = pd.read_csv(current_file)
            print(f"✅ 현재 train.csv: {len(current_df)} 샘플")
            
            # 클래스 분포
            class_dist = current_df['target'].value_counts().sort_index()
            print(f"   클래스 분포: {dict(class_dist)}")
            
        except Exception as e:
            print(f"❌ 현재 파일 읽기 실패: {e}")
    
    # 백업 파일들 분석
    for backup_file in backup_files:
        if Path(backup_file).exists():
            try:
                backup_df = pd.read_csv(backup_file)
                print(f"✅ {backup_file}: {len(backup_df)} 샘플")
            except Exception as e:
                print(f"❌ {backup_file} 읽기 실패: {e}")
    
    print(f"\n💡 성능 하락의 가능한 원인들:")
    
    print(f"\n1. 🏷️ 라벨링 일관성 문제")
    print(f"   • 가장 가능성 높은 원인")
    print(f"   • 개선된 라벨이 더 정확하지만, 테스트 데이터는 원본 기준으로 라벨링")
    print(f"   • 문서 분류의 애매한 경계 (진단서 vs 소견서, 영수증 vs 계산서 등)")
    print(f"   • 해결책: 원본 데이터로 롤백 또는 하이브리드 접근")
    
    print(f"\n2. 📊 클래스 분포 변화")
    print(f"   • 특정 클래스 샘플 수 변화로 인한 불균형 악화")
    print(f"   • config.yaml의 클래스 증강 전략([1, 13, 14])이 새 분포에 부적합")
    print(f"   • 해결책: 클래스 증강 전략 재조정")
    
    print(f"\n3. 🎯 도메인 갭 증가")
    print(f"   • 학습 데이터와 테스트 데이터 간 분포 차이 확대")
    print(f"   • 원본이 테스트 데이터와 더 유사한 특성을 가짐")
    print(f"   • 해결책: 테스트 데이터 특성에 맞는 학습 전략")
    
    print(f"\n4. 🔧 하이퍼파라미터 부적합")
    print(f"   • 기존 설정이 원본 데이터에 최적화되어 있음")
    print(f"   • 새 데이터에는 다른 학습 전략이 필요할 수 있음")
    print(f"   • 해결책: 새 데이터에 맞는 HPO 재실행")
    
    print(f"\n5. 🎪 앙상블 영향")
    print(f"   • 개별 모델 성능 하락이 앙상블에도 부정적 영향")
    print(f"   • v1 모델들의 다양성이 더 효과적이었을 가능성")
    print(f"   • 해결책: v1 데이터로 다양한 모델 재학습")
    
    # 구체적인 사례 분석
    print(f"\n📋 문서 분류 도메인의 특수성:")
    
    document_categories = {
        0: "account_number",
        1: "application_for_payment_of_pregnancy_medical_expenses", 
        2: "car_dashboard",
        3: "confirmation_of_admission_and_discharge",
        4: "diagnosis",
        5: "driver_lisence",
        6: "medical_bill_receipts",
        7: "medical_outpatient_certificate", 
        8: "national_id_card"
    }
    
    ambiguous_pairs = [
        ("diagnosis", "medical_outpatient_certificate"),
        ("medical_bill_receipts", "다른 의료 관련 문서"),
        ("confirmation_of_admission_and_discharge", "diagnosis"),
        ("national_id_card", "driver_lisence")
    ]
    
    print(f"   애매한 경계선이 있는 문서 쌍들:")
    for pair in ambiguous_pairs:
        print(f"   • {pair[0]} ↔ {pair[1]}")
    
    print(f"\n🚀 권장 대응 전략:")
    
    print(f"\n   📊 즉시 실행 (1-2일):")
    print(f"   1. 원본 train.csv로 롤백하여 v1 성능 복구")
    print(f"   2. EfficientNet-B4 v1 모델을 메인으로 확정")
    print(f"   3. 원본 데이터로 다른 아키텍처 실험 (ViT, Swin)")
    
    print(f"\n   🔍 중기 분석 (3-7일):")
    print(f"   1. 백업 파일과 현재 파일의 상세 비교 분석")
    print(f"   2. 변경된 샘플들의 실제 이미지 검토") 
    print(f"   3. 클래스별 성능 변화 분석")
    print(f"   4. 테스트 데이터 특성 역추적")
    
    print(f"\n   🎯 장기 최적화 (1-2주):")
    print(f"   1. 하이브리드 데이터셋 구성 (명확한 오류만 수정)")
    print(f"   2. 두 버전으로 각각 학습하여 앙상블")
    print(f"   3. 도메인 특화 증강 전략 개발")
    print(f"   4. 라벨 노이즈에 강인한 학습 방법 적용")
    
    # 교훈
    print(f"\n📚 핵심 교훈:")
    print(f"   • '개선'이 항상 성능 향상을 의미하지 않음")
    print(f"   • 테스트 데이터와의 일관성이 정확성보다 중요할 수 있음")
    print(f"   • 도메인 특성을 고려한 신중한 데이터 수정 필요")
    print(f"   • 백업과 점진적 검증의 중요성")
    
    return True

if __name__ == "__main__":
    analyze_performance_drop()
