#!/usr/bin/env python3
"""
train.csv 파일 변경사항 분석
"""
import pandas as pd
from pathlib import Path

def analyze_train_changes():
    """기존 vs 새 train.csv 비교 분석"""
    
    print("📊 train.csv 변경사항 분석")
    print("=" * 50)
    
    # 파일 경로
    old_file = "data/train.csv"
    new_file = "/Users/jayden/Downloads/train.csv"
    
    # 파일 존재 확인
    if not Path(old_file).exists():
        print(f"❌ 기존 파일 없음: {old_file}")
        return
        
    if not Path(new_file).exists():
        print(f"❌ 새 파일 없음: {new_file}")
        return
    
    # 데이터 로드
    try:
        old_df = pd.read_csv(old_file)
        new_df = pd.read_csv(new_file)
        
        print(f"✅ 파일 로드 완료")
        print(f"   기존: {len(old_df)}개 샘플")
        print(f"   새로: {len(new_df)}개 샘플")
        
    except Exception as e:
        print(f"❌ 파일 로드 실패: {e}")
        return
    
    # 기본 비교
    print(f"\n📋 기본 정보 비교:")
    print(f"   샘플 수: {len(old_df)} → {len(new_df)} ({len(new_df)-len(old_df):+d})")
    print(f"   컬럼: {list(old_df.columns)} → {list(new_df.columns)}")
    
    # ID 비교 (동일한지 확인)
    old_ids = set(old_df['ID'])
    new_ids = set(new_df['ID']) 
    
    common_ids = old_ids & new_ids
    removed_ids = old_ids - new_ids
    added_ids = new_ids - old_ids
    
    print(f"\n🔍 ID 변경사항:")
    print(f"   공통 ID: {len(common_ids)}개")
    print(f"   제거된 ID: {len(removed_ids)}개")
    print(f"   추가된 ID: {len(added_ids)}개")
    
    if removed_ids:
        print(f"   제거 예시: {list(removed_ids)[:5]}")
    if added_ids:
        print(f"   추가 예시: {list(added_ids)[:5]}")
    
    # 레이블 변경사항 (공통 ID 대상)
    if common_ids:
        old_common = old_df[old_df['ID'].isin(common_ids)].set_index('ID')
        new_common = new_df[new_df['ID'].isin(common_ids)].set_index('ID')
        
        # 레이블이 다른 샘플들
        different_labels = old_common['target'] != new_common['target']
        changed_count = different_labels.sum()
        
        print(f"\n🏷️ 레이블 변경사항:")
        print(f"   변경된 샘플: {changed_count}개 ({changed_count/len(common_ids)*100:.1f}%)")
        
        if changed_count > 0:
            print(f"   변경 예시 (최대 10개):")
            changed_samples = old_common[different_labels].head(10)
            for idx, row in changed_samples.iterrows():
                old_label = row['target']
                new_label = new_common.loc[idx, 'target']
                print(f"     {idx}: {old_label} → {new_label}")
    
    # 클래스 분포 비교
    print(f"\n📊 클래스 분포 비교:")
    old_dist = old_df['target'].value_counts().sort_index()
    new_dist = new_df['target'].value_counts().sort_index()
    
    all_classes = sorted(set(old_dist.index) | set(new_dist.index))
    
    print(f"   클래스   기존    새로   변화")
    print(f"   " + "-" * 30)
    for cls in all_classes:
        old_count = old_dist.get(cls, 0)
        new_count = new_dist.get(cls, 0)
        diff = new_count - old_count
        print(f"   {cls:6d}   {old_count:4d}   {new_count:4d}   {diff:+4d}")
    
    print(f"\n💡 분석 완료")
    print(f"   개선된 train.csv 적용 시 재학습 권장")

if __name__ == "__main__":
    analyze_train_changes()
