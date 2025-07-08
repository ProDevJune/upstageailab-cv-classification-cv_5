#!/usr/bin/env python3
"""
timm 모듈 설치 스크립트
"""

import subprocess
import sys

def install_timm():
    """timm 모듈 설치"""
    try:
        print("📦 timm 모듈 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "timm"])
        print("✅ timm 모듈 설치 완료!")
        
        # 설치 확인
        import timm
        print(f"📋 timm 버전: {timm.__version__}")
        print(f"📋 사용 가능한 모델 수: {len(timm.list_models())}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 설치 실패: {e}")
        return False
    except ImportError as e:
        print(f"❌ 설치 후 임포트 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    install_timm()
