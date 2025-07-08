#!/usr/bin/env python3
"""
제출 후보 모델들을 찾고 분석하는 스크립트
"""

import os
import pandas as pd
from pathlib import Path

def find_submission_candidates():
    """제출 후보 모델들을 찾고 분석합니다."""
    
    print("🔍 제출 후보 모델 분석 시스템")
    print("=" * 60)
    
    # submissions 디렉토리 스캔
    submissions_dir = Path("/Users/jayden/developer/Projects/cv-classification/data/submissions")
    
    if not submissions_dir.exists():
        print("❌ submissions 디렉토리를 찾을 수 없습니다.")
        return
    
    # 각 submission 폴더 분석
    candidates = []
    
    for folder in submissions_dir.iterdir():
        if folder.is_dir() and folder.name.startswith("25070"):
            csv_files = list(folder.glob("*.csv"))
            if csv_files:
                csv_file = csv_files[0]
                
                # 폴더명에서 정보 추출
                folder_name = folder.name
                
                # 시간 추출 (2507041805 -> 07-04 18:05)
                time_str = folder_name[:10]
                if len(time_str) == 10:
                    month_day = f"{time_str[2:4]}-{time_str[4:6]}"
                    hour_min = f"{time_str[6:8]}:{time_str[8:10]}"
                    datetime_str = f"2025-{month_day} {hour_min}"
                else:
                    datetime_str = "Unknown"
                
                # 모델 정보 추출
                if "resnet50" in folder_name:
                    model = "ResNet50"
                elif "resnet34" in folder_name:
                    model = "ResNet34"
                else:
                    model = "Unknown"
                
                # 이미지 크기 추출
                if "img224" in folder_name:
                    img_size = "224"
                elif "img320" in folder_name:
                    img_size = "320"
                else:
                    img_size = "Unknown"
                
                # TTA 여부
                tta = "Yes" if "TTA_1" in folder_name else "No"
                
                # 증강 타입
                if "dilation_eda_erosion_mixup" in folder_name:
                    aug_type = "Strong"
                elif "dilation_eda" in folder_name:
                    aug_type = "Moderate+"
                elif "eda" in folder_name:
                    aug_type = "Moderate"
                else:
                    aug_type = "Unknown"
                
                candidates.append({
                    'folder_name': folder.name,
                    'csv_path': str(csv_file),
                    'datetime': datetime_str,
                    'model': model,
                    'img_size': img_size,
                    'tta': tta,
                    'augmentation': aug_type,
                    'estimated_id': f"exp_full_{len(candidates)+1:03d}"
                })
    
    # 시간순 정렬
    candidates.sort(key=lambda x: x['datetime'])
    
    print(f"📊 총 {len(candidates)}개의 제출 후보 발견")
    print("\n🏆 추천 제출 후보들:")
    print("-" * 80)
    
    # Top 후보들 출력
    top_candidates = []
    
    for i, candidate in enumerate(candidates):
        print(f"\n{i+1:2d}. {candidate['estimated_id']}")
        print(f"    📁 폴더: {candidate['folder_name'][:50]}...")
        print(f"    📅 시간: {candidate['datetime']}")
        print(f"    🧠 모델: {candidate['model']}")
        print(f"    📏 크기: {candidate['img_size']}px")
        print(f"    🎨 증강: {candidate['augmentation']}")
        print(f"    🔄 TTA: {candidate['tta']}")
        print(f"    📝 CSV: {candidate['csv_path']}")
        
        # ResNet50이고 다양한 설정인 것들을 우선 추천
        if candidate['model'] == 'ResNet50':
            score = 0
            if candidate['img_size'] == '320':
                score += 2  # 큰 이미지 선호
            if candidate['tta'] == 'Yes':
                score += 1  # TTA 선호
            if candidate['augmentation'] in ['Moderate', 'Moderate+']:
                score += 1  # 적절한 증강 선호
            
            candidate['priority_score'] = score
            if score >= 2:
                top_candidates.append(candidate)
    
    print(f"\n🎯 상위 추천 후보 ({len(top_candidates)}개):")
    print("=" * 60)
    
    top_candidates.sort(key=lambda x: x['priority_score'], reverse=True)
    
    for i, candidate in enumerate(top_candidates[:5]):  # 상위 5개만
        print(f"\n🥇 추천 {i+1}: {candidate['estimated_id']}")
        print(f"   🔥 우선순위: {candidate['priority_score']}/4")
        print(f"   🧠 {candidate['model']} | 📏 {candidate['img_size']}px | 🔄 TTA:{candidate['tta']}")
        print(f"   📂 경로: {candidate['csv_path']}")
    
    return top_candidates

def create_submission_guide():
    """제출 가이드를 생성합니다."""
    
    print(f"\n📋 제출 가이드")
    print("=" * 60)
    
    print(f"\n1️⃣ 제출 순서 추천:")
    print(f"   🥇 1순위: exp_full_021 (F1=0.9347) - ResNet50 + 320px + TTA")
    print(f"   🥈 2순위: exp_full_011 (F1=0.9330) - ResNet50 + 320px + minimal aug")
    print(f"   🥉 3순위: 다른 고성능 ResNet50 모델")
    
    print(f"\n2️⃣ 제출할 때 모델명 권장:")
    print(f"   ResNet50_F1935_exp021_320px_TTA")
    print(f"   ResNet50_F1933_exp011_320px")
    print(f"   ResNet50_F1XXX_expYYY_특징")
    
    print(f"\n3️⃣ 패턴 분석을 위한 체크리스트:")
    print(f"   ✅ 이미지 크기 영향 (224px vs 320px)")
    print(f"   ✅ TTA 효과 (TTA vs No-TTA)")
    print(f"   ✅ 증강 수준 영향 (Moderate vs Strong)")
    print(f"   ✅ 일관된 일반화 비율 확인")
    
    print(f"\n4️⃣ 각 제출 후 기록할 정보:")
    print(f"   📊 Public Score")
    print(f"   📈 Local vs Server 비율")
    print(f"   🎯 순위 변화")
    print(f"   💡 패턴 관찰 내용")

if __name__ == "__main__":
    candidates = find_submission_candidates()
    create_submission_guide()
    
    print(f"\n🚀 다음 단계:")
    print(f"1. 위 추천 후보들 중 2-3개 선택")
    print(f"2. AIStages에 순차적으로 제출")
    print(f"3. 각 결과를 record_aistages_corrected.py로 기록")
    print(f"4. 패턴 분석 후 앙상블 전략 수립")
