#!/bin/bash

echo "🔧 누락된 패키지들 설치 중..."

# 필수 패키지들 순서대로 설치
packages=(
    "PyYAML"
    "matplotlib" 
    "seaborn"
    "scikit-learn"
    "tqdm"
    "pillow"
    "opencv-python"
    "albumentations"
    "timm"
)

for package in "${packages[@]}"; do
    echo "📦 $package 설치 중..."
    pip install "$package"
    if [[ $? -eq 0 ]]; then
        echo "✅ $package 설치 완료"
    else
        echo "❌ $package 설치 실패"
    fi
done

echo ""
echo "🧪 설치 확인 테스트..."

python -c "
try:
    import yaml
    import torch
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import psutil
    import sklearn
    import tqdm
    import PIL
    import cv2
    import albumentations
    import timm
    
    print('✅ 모든 필수 패키지 설치 완료!')
    print(f'PyTorch: {torch.__version__}')
    print(f'PyYAML: {yaml.__version__}')
    print(f'MPS 사용 가능: {torch.backends.mps.is_available()}')
    
except ImportError as e:
    print(f'❌ 일부 패키지 누락: {e}')
"

echo ""
echo "🎯 이제 플랫폼 테스트를 실행해보세요:"
echo "python test_platform_detection.py"
