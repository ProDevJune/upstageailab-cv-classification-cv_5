#!/usr/bin/env python3
"""
가상환경 및 패키지 설치 진단 도구
"""

import sys
import subprocess
import os

print("🔍 가상환경 진단 시작...")

# 1. Python 환경 정보
print(f"Python 실행 경로: {sys.executable}")
print(f"Python 버전: {sys.version}")
print(f"가상환경: {os.environ.get('VIRTUAL_ENV', '없음')}")

# 2. pip 경로 확인
try:
    pip_result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                               capture_output=True, text=True)
    print(f"pip 정보: {pip_result.stdout.strip()}")
except Exception as e:
    print(f"pip 확인 실패: {e}")

# 3. 설치된 패키지 확인
print("\n📦 설치된 주요 패키지:")
packages_to_check = ['torch', 'yaml', 'pandas', 'numpy', 'matplotlib', 'psutil']

for package in packages_to_check:
    try:
        if package == 'yaml':
            import yaml
            print(f"✅ PyYAML: {yaml.__version__}")
        elif package == 'torch':
            import torch
            print(f"✅ PyTorch: {torch.__version__}")
        elif package == 'pandas':
            import pandas as pd
            print(f"✅ Pandas: {pd.__version__}")
        elif package == 'numpy':
            import numpy as np
            print(f"✅ NumPy: {np.__version__}")
        elif package == 'matplotlib':
            import matplotlib
            print(f"✅ Matplotlib: {matplotlib.__version__}")
        elif package == 'psutil':
            import psutil
            print(f"✅ psutil: {psutil.__version__}")
    except ImportError:
        print(f"❌ {package}: 설치되지 않음")

# 4. PyYAML 특별 확인
print("\n🔍 PyYAML 특별 진단:")
try:
    # 다양한 import 방법 시도
    import yaml
    print("✅ import yaml 성공")
except ImportError as e:
    print(f"❌ import yaml 실패: {e}")
    
    # 대안 시도
    try:
        import ruamel.yaml
        print("⚠️  ruamel.yaml은 있음 (PyYAML 대신)")
    except ImportError:
        print("❌ ruamel.yaml도 없음")

# 5. 패키지 설치 시도
print("\n🔧 누락된 패키지 자동 설치 시도...")
missing_packages = []

# PyYAML 우선 설치
try:
    import yaml
except ImportError:
    missing_packages.append('PyYAML')

# 기타 필수 패키지
essential_packages = ['torch', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'psutil']
for pkg in essential_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing_packages.append(pkg)

if missing_packages:
    print(f"설치할 패키지: {missing_packages}")
    for pkg in missing_packages:
        try:
            print(f"📦 {pkg} 설치 중...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", pkg], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {pkg} 설치 완료")
            else:
                print(f"❌ {pkg} 설치 실패: {result.stderr}")
        except Exception as e:
            print(f"❌ {pkg} 설치 중 오류: {e}")
else:
    print("✅ 모든 필수 패키지가 설치되어 있습니다")

print("\n🧪 최종 테스트...")
try:
    import yaml
    import torch
    print("✅ 핵심 패키지 import 성공!")
    print(f"PyTorch MPS 사용 가능: {torch.backends.mps.is_available()}")
except Exception as e:
    print(f"❌ 최종 테스트 실패: {e}")

print("\n🎯 진단 완료!")
