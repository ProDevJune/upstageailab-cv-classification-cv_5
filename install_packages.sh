#!/bin/bash

echo "🔧 필수 패키지 설치 시작..."

# pip 업그레이드
echo "📈 pip 업그레이드..."
pip install --upgrade pip

# PyTorch (macOS 최적화)
echo "🍎 PyTorch 설치..."
pip install torch torchvision torchaudio

# 데이터 처리
echo "📊 데이터 처리 패키지..."
pip install pandas numpy

# 시각화
echo "📈 시각화 패키지..."
pip install matplotlib seaborn

# 시스템 모니터링
echo "🖥️ 시스템 패키지..."
pip install psutil

# 기타 유틸리티
echo "🔧 기타 패키지..."
pip install scikit-learn tqdm pyyaml pillow

# 설치 확인
echo ""
echo "🧪 설치 확인..."
python -c "
try:
    import torch
    import pandas as pd
    import numpy as np
    import psutil
    print('✅ 핵심 패키지 설치 성공!')
    print(f'PyTorch: {torch.__version__}')
    if torch.backends.mps.is_available():
        print('🍎 MPS 가속 사용 가능')
    else:
        print('💻 CPU 모드')
except Exception as e:
    print(f'❌ 오류: {e}')
"

echo ""
echo "✅ 패키지 설치 완료!"
echo "🎯 다음: python test_platform_detection.py"
