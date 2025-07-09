#!/usr/bin/env python3
"""
정상 동작하는 소스 방식으로 CSV 테스트
"""

def test_csv_read():
    """정상 소스와 동일한 방식으로 CSV 읽기 테스트"""
    print("=== CSV 읽기 테스트 ===")
    
    # 1. 기본 import 테스트
    try:
        import pandas as pd
        print("✅ pandas import (as pd) 성공")
    except Exception as e:
        print(f"❌ pandas import 실패: {e}")
        return False
    
    # 2. 파일 존재 확인
    import os
    csv_path = "data/train.csv"
    if os.path.exists(csv_path):
        print(f"✅ {csv_path} 파일 존재")
    else:
        print(f"❌ {csv_path} 파일 없음")
        return False
    
    # 3. CSV 읽기 테스트 (정상 소스와 동일)
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ CSV 읽기 성공: {len(df)} rows, {len(df.columns)} columns")
        print(f"   컬럼: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"❌ CSV 읽기 실패: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_read()
    if success:
        print("\n🎉 모든 CSV 테스트 통과!")
    else:
        print("\n❌ CSV 테스트 실패")
