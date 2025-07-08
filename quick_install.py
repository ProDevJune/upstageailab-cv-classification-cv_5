#!/usr/bin/env python3
"""
빠른 패키지 설치 - wandb 및 누락된 패키지들
"""

import subprocess
import sys

def quick_install():
    """필수 패키지 빠른 설치"""
    
    print("⚡ 빠른 패키지 설치 시작")
    print("=" * 40)
    
    packages = [
        "wandb",
        "timm", 
        "albumentations",
        "optuna"
    ]
    
    for package in packages:
        print(f"📦 {package} 설치 중...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                          check=True, capture_output=True)
            print(f"✅ {package} 설치 완료")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 설치 실패")
            print(f"수동 설치: pip install {package}")
    
    print("\n🔍 설치 확인...")
    
    # 테스트 임포트
    test_modules = ["wandb", "timm", "albumentations", "optuna"]
    success = 0
    
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            success += 1
        except ImportError:
            print(f"❌ {module}")
    
    if success == len(test_modules):
        print("\n🎉 모든 패키지 설치 완료!")
        print("이제 실험을 실행할 수 있습니다:")
        print("python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml")
        return True
    else:
        print(f"\n⚠️ {len(test_modules) - success}개 패키지 설치 필요")
        return False

if __name__ == "__main__":
    quick_install()
