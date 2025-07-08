#!/usr/bin/env python3
"""
EfficientNet-B4 v1 시각화 파일들 정리 및 분석
"""

import os
from pathlib import Path

def analyze_b4_v1_visualizations():
    """EfficientNet-B4 v1의 모든 시각화 파일들을 정리합니다."""
    
    print("🎯 EfficientNet-B4 v1 시각화 파일 분석")
    print("=" * 60)
    
    # 기본 경로들
    submission_path = "data/submissions/2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0"
    wandb_path = "wandb/run-20250705_193425-h3t1bpti"
    
    print(f"📁 주요 파일 경로:")
    print(f"1. 제출 폴더: {submission_path}")
    print(f"2. W&B 로그: {wandb_path}")
    
    # 제출 폴더의 시각화 파일들
    print(f"\n📊 제출 폴더 시각화 파일들:")
    visualization_files = [
        "loss_plot.png",
        "accuracy_plot.png", 
        "f1_plot.png",
        "val_confusion_matrix.png"
    ]
    
    for i, viz_file in enumerate(visualization_files, 1):
        full_path = f"{submission_path}/{viz_file}"
        print(f"{i}. {viz_file}")
        print(f"   경로: {full_path}")
        
        if Path(full_path).exists():
            file_info = Path(full_path).stat()
            print(f"   크기: {file_info.st_size:,} bytes")
            print(f"   수정: {file_info.st_mtime}")
            print(f"   ✅ 파일 존재")
        else:
            print(f"   ❌ 파일 없음")
        print()
    
    # W&B 미디어 파일들
    print(f"📊 W&B 미디어 파일들:")
    wandb_media_path = f"{wandb_path}/files/media/images"
    
    wandb_files = [
        "loss_plot_25_98e3934b25b499c20b20.png",
        "accuracy_plot_26_2335f44a7d5e833acd8b.png",
        "f1_plot_27_518c9d3e38f618bebdef.png", 
        "tta_val_confusion_matrix_28_2584809bb8cc7acdb9f8.png"
    ]
    
    for i, wandb_file in enumerate(wandb_files, 1):
        full_path = f"{wandb_media_path}/{wandb_file}"
        print(f"{i}. {wandb_file}")
        print(f"   경로: {full_path}")
        
        if Path(full_path).exists():
            file_info = Path(full_path).stat()
            print(f"   크기: {file_info.st_size:,} bytes")
            print(f"   ✅ 파일 존재")
        else:
            print(f"   ❌ 파일 없음")
        print()
    
    # 모델 및 결과 파일들
    print(f"📄 모델 및 결과 파일들:")
    result_files = [
        "2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.pht",
        "2507051934-efficientnet_b4.ra2_in1k-opt_AdamW-sch_CosineAnnealingLR-img320-onaug_eda-clsaug_1-TTA_0-MP_0.csv"
    ]
    
    for i, result_file in enumerate(result_files, 1):
        full_path = f"{submission_path}/{result_file}"
        file_type = "모델 파일" if result_file.endswith('.pht') else "제출 파일"
        
        print(f"{i}. {file_type}: {result_file}")
        print(f"   경로: {full_path}")
        
        if Path(full_path).exists():
            file_info = Path(full_path).stat()
            print(f"   크기: {file_info.st_size:,} bytes")
            print(f"   ✅ 파일 존재")
        else:
            print(f"   ❌ 파일 없음")
        print()
    
    # 설정 파일
    print(f"⚙️ 설정 파일:")
    config_file = "codes/practice/exp_golden_efficientnet_b4_202507051902.yaml"
    print(f"1. 설정 파일: {config_file}")
    
    if Path(config_file).exists():
        print(f"   ✅ 파일 존재")
    else:
        print(f"   ❌ 파일 없음")
    
    # 요약
    print(f"\n📋 파일 요약:")
    print(f"• 실험 ID: 2507051934")
    print(f"• 실행 시간: 2025-07-05 19:34:25")
    print(f"• 학습 시간: 24분 20초")
    print(f"• 최종 성능: Local F1 0.9164, Server Score 0.8619")
    print(f"• 주요 특징: 320px + Minimal aug + No TTA")
    
    print(f"\n🎯 시각화 파일 활용 가이드:")
    print(f"1. loss_plot.png: 학습/검증 손실 추이 확인")
    print(f"2. accuracy_plot.png: 정확도 변화 패턴 분석")
    print(f"3. f1_plot.png: F1 스코어 개선 과정 추적")
    print(f"4. val_confusion_matrix.png: 클래스별 성능 분석")
    
    print(f"\n🔍 추가 분석 가능한 파일들:")
    print(f"• W&B summary: wandb/run-20250705_193425-h3t1bpti/files/wandb-summary.json")
    print(f"• 학습 로그: wandb/run-20250705_193425-h3t1bpti/files/output.log")
    print(f"• 상세 설정: wandb/run-20250705_193425-h3t1bpti/files/config.yaml")
    
    return True

if __name__ == "__main__":
    analyze_b4_v1_visualizations()
