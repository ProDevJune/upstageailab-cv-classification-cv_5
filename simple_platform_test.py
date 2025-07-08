#!/usr/bin/env python3
"""
간단한 플랫폼 감지 테스트
문제 해결을 위한 단계별 테스트
"""

print("🧪 단계별 패키지 테스트")
print("=" * 50)

# 1단계: 기본 Python 모듈들
try:
    import sys
    import os
    import platform
    print("✅ 1단계: 기본 Python 모듈 OK")
except ImportError as e:
    print(f"❌ 1단계 실패: {e}")
    exit(1)

# 2단계: PyYAML 테스트
try:
    import yaml
    print(f"✅ 2단계: PyYAML {yaml.__version__} OK")
except ImportError as e:
    print(f"❌ 2단계 실패: {e}")
    print("해결법: pip install PyYAML")
    exit(1)

# 3단계: PyTorch 테스트
try:
    import torch
    print(f"✅ 3단계: PyTorch {torch.__version__} OK")
    print(f"   MPS 사용 가능: {torch.backends.mps.is_available()}")
    print(f"   CUDA 사용 가능: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ 3단계 실패: {e}")
    print("해결법: pip install torch torchvision torchaudio")
    exit(1)

# 4단계: 데이터 처리 패키지들
try:
    import pandas as pd
    import numpy as np
    print(f"✅ 4단계: 데이터 처리 패키지 OK")
    print(f"   Pandas: {pd.__version__}")
    print(f"   NumPy: {np.__version__}")
except ImportError as e:
    print(f"❌ 4단계 실패: {e}")
    print("해결법: pip install pandas numpy")
    exit(1)

# 5단계: 시스템 모니터링
try:
    import psutil
    print(f"✅ 5단계: psutil {psutil.__version__} OK")
except ImportError as e:
    print(f"❌ 5단계 실패: {e}")
    print("해결법: pip install psutil")
    exit(1)

# 6단계: 플랫폼 정보
print("\n🖥️ 시스템 정보:")
print(f"OS: {platform.system()}")
print(f"아키텍처: {platform.machine()}")
print(f"Python: {platform.python_version()}")

if torch.backends.mps.is_available():
    print("🍎 Apple Silicon MPS 감지됨!")
    device = torch.device('mps')
    
    # MPS 테스트
    try:
        x = torch.randn(10, 10).to(device)
        print(f"✅ MPS 텐서 테스트 성공: {x.device}")
    except Exception as e:
        print(f"❌ MPS 테스트 실패: {e}")
        
elif torch.cuda.is_available():
    print("🚀 CUDA 감지됨!")
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f"   GPU {i}: {name} ({memory:.1f} GB)")
else:
    print("💻 CPU 전용 환경")

print("\n✅ 모든 테스트 완료!")
print("🎯 이제 실제 HPO 시스템을 사용할 수 있습니다!")
