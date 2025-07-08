#!/usr/bin/env python3

print("🔍 Python 환경 진단 시작...")

import sys
import subprocess
import os

print(f"Python 경로: {sys.executable}")
print(f"Python 버전: {sys.version}")
print(f"가상환경: {os.environ.get('VIRTUAL_ENV', '없음')}")

print("\n📦 설치 시도 중...")

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "torch"])
    print("✅ PyTorch 설치 성공")
except Exception as e:
    print(f"❌ PyTorch 설치 실패: {e}")

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "numpy", "psutil"])
    print("✅ 기본 패키지 설치 성공")
except Exception as e:
    print(f"❌ 기본 패키지 설치 실패: {e}")

print("\n🧪 설치 확인...")

try:
    import torch
    print(f"✅ PyTorch 버전: {torch.__version__}")
    print(f"MPS 사용 가능: {torch.backends.mps.is_available()}")
except ImportError:
    print("❌ PyTorch 임포트 실패")

try:
    import pandas as pd
    import numpy as np
    import psutil
    print("✅ 기본 패키지들 임포트 성공")
except ImportError as e:
    print(f"❌ 기본 패키지 임포트 실패: {e}")

print("\n🎯 진단 완료!")
