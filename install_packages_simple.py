#!/usr/bin/env python3
"""
CV Classification 프로젝트 필수 패키지 설치 스크립트 (간단 버전)
"""

import subprocess
import sys
import os

def run_command(command, description):
    """명령어 실행 및 결과 확인"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패:")
        print(f"   오류: {e.stderr}")
        return False

def main():
    """메인 실행"""
    print("🎯 CV Classification 필수 패키지 설치")
    print("=" * 50)
    
    # 핵심 패키지들
    packages = [
        "pip install --upgrade pip",
        "pip install torch torchvision torchaudio",
        "pip install timm",
        "pip install scikit-learn",
        "pip install pandas numpy",
        "pip install matplotlib seaborn",
        "pip install Pillow opencv-python",
        "pip install albumentations",
        "pip install optuna",
        "pip install tqdm pyyaml",
    ]
    
    success_count = 0
    
    for command in packages:
        if run_command(command, command.split()[-1]):  # 패키지 이름만 표시
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"📊 설치 완료: {success_count}/{len(packages)}")
    
    # 설치 확인
    print("\n🔍 설치 확인...")
    try:
        import torch
        import timm
        import sklearn
        import pandas
        import matplotlib
        print("✅ 모든 핵심 패키지 설치 성공!")
        
        # 버전 정보
        print(f"\n📋 버전 정보:")
        print(f"   PyTorch: {torch.__version__}")
        print(f"   TIMM: {timm.__version__}")
        print(f"   Scikit-learn: {sklearn.__version__}")
        
        # 디바이스 확인
        if torch.cuda.is_available():
            print(f"   CUDA: Available")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print(f"   MPS: Available (Apple Silicon)")
        else:
            print(f"   Device: CPU")
            
        print("\n🚀 이제 다음 명령어를 실행하세요:")
        print("   python aistages_manager.py")
        
    except ImportError as e:
        print(f"❌ 일부 패키지 설치 실패: {e}")
        print("수동으로 설치해보세요:")
        print("pip install torch torchvision timm scikit-learn pandas matplotlib")

if __name__ == "__main__":
    main()
