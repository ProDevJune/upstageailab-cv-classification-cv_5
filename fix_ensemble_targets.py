#!/usr/bin/env python3
"""
앙상블 결과 파일의 target을 정수로 수정
"""
import pandas as pd
import numpy as np
from pathlib import Path

def fix_ensemble_targets():
    """앙상블 결과의 소수점 target을 정수로 변환"""
    
    print("🔧 앙상블 결과 파일 수정")
    print("=" * 40)
    
    # 수정할 파일들
    files_to_fix = [
        "ensemble_golden_3models_20250705_230345.csv",
        "ensemble_2models_optimized_20250705_230739.csv"
    ]
    
    for filename in files_to_fix:
        if Path(filename).exists():
            print(f"\n📁 수정 중: {filename}")
            
            # 파일 로드
            df = pd.read_csv(filename)
            
            # target 컬럼 확인
            print(f"   원본 target 타입: {df['target'].dtype}")
            print(f"   소수점 값 예시: {df['target'].head()}")
            
            # 정수로 반올림
            df['target'] = np.round(df['target']).astype(int)
            
            # 수정된 파일 저장
            fixed_filename = filename.replace('.csv', '_fixed.csv')
            df.to_csv(fixed_filename, index=False)
            
            print(f"   ✅ 수정 완료: {fixed_filename}")
            print(f"   수정된 target 타입: {df['target'].dtype}")
            print(f"   정수 값 예시: {df['target'].head()}")
            
            # 클래스 범위 확인
            min_class = df['target'].min()
            max_class = df['target'].max()
            unique_classes = df['target'].nunique()
            
            print(f"   클래스 범위: {min_class} ~ {max_class}")
            print(f"   유니크 클래스: {unique_classes}개")
            
        else:
            print(f"❌ 파일 없음: {filename}")
    
    print(f"\n✅ 수정 완료!")
    print(f"📤 수정된 파일들을 대회 서버에 재제출하세요.")

if __name__ == "__main__":
    fix_ensemble_targets()
