#!/bin/bash

# 🚀 Ubuntu 환경 문제 해결 스크립트
# numpy, opencv, albumentations 버전 충돌 해결

echo "🔧 패키지 버전 충돌 해결 중..."
echo "================================"

# 가상환경 확인
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ 가상환경이 활성화되지 않았습니다!"
    echo "다음 명령어를 실행하세요:"
    echo "  source venv/bin/activate"
    exit 1
fi

echo "✅ 가상환경 활성화됨: $VIRTUAL_ENV"

# pip 업그레이드
pip install --upgrade pip

echo ""
echo "🧹 문제 패키지 제거 중..."

# 충돌하는 패키지들 제거
pip uninstall -y opencv-python-headless opencv-python opencv-contrib-python
pip uninstall -y albumentations albucore
pip uninstall -y numpy

echo ""
echo "📦 올바른 순서로 재설치 중..."

# 1. numpy 먼저 설치 (모든 패키지의 기본)
echo "  1️⃣ numpy 설치..."
pip install numpy==1.26.4

# 2. opencv-python 설치 (numpy 버전과 호환되는)
echo "  2️⃣ opencv-python 설치..."
pip install opencv-python==4.9.0.80

# 3. albucore 먼저 설치 (albumentations 의존성)
echo "  3️⃣ albucore 설치..."
pip install albucore==0.0.13

# 4. albumentations 설치
echo "  4️⃣ albumentations 설치..."
pip install albumentations==1.4.15

# 5. 나머지 패키지들 설치
echo "  5️⃣ 나머지 패키지들 설치..."
pip install timm==0.9.16
pip install Pillow==10.3.0 imageio==2.34.2
pip install PyYAML==6.0.1 tqdm==4.66.4 psutil==5.9.8
pip install wandb==0.17.7 optuna==3.6.1

# 데이터 사이언스 패키지
pip install pandas==2.0.3 scipy==1.11.4 scikit-learn==1.3.2
pip install matplotlib==3.7.5 seaborn==0.12.2

echo ""
echo "🧪 최종 검증 중..."

python -c "
try:
    import numpy as np
    print(f'✅ numpy: {np.__version__}')
    
    import cv2
    print(f'✅ opencv-python: {cv2.__version__}')
    
    import albumentations as A
    print(f'✅ albumentations: {A.__version__}')
    
    import torch
    print(f'✅ torch: {torch.__version__}')
    print(f'✅ CUDA 사용 가능: {torch.cuda.is_available()}')
    
    import timm
    print(f'✅ timm: {timm.__version__}')
    
    import pandas as pd
    import yaml
    import wandb
    import optuna
    
    print('')
    print('🎉 모든 패키지 호환성 문제 해결!')
    print('✅ albumentations import 성공')
    print('✅ numpy 버전 충돌 해결')
    print('✅ opencv 호환성 확인')
    
except Exception as e:
    print(f'❌ 오류 발생: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 모든 문제 해결 완료!"
    echo ""
    echo "🚀 이제 실험을 시작할 수 있습니다:"
    echo "  python aistages_manager.py"
    echo "  python codes/gemini_main_v2.py --config codes/config.yaml"
    echo ""
    echo "📋 설치된 주요 패키지:"
    echo "  - numpy: 1.26.4 (opencv 호환)"
    echo "  - opencv-python: 4.9.0.80"
    echo "  - albumentations: 1.4.15 (albucore 0.0.13)"
    echo "  - torch: 2.4.1+cu121"
    echo "  - timm: 0.9.16"
else
    echo ""
    echo "❌ 문제가 지속됩니다. 가상환경을 재생성하세요:"
    echo "  deactivate"
    echo "  rm -rf venv"
    echo "  python3.11 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements_ubuntu_fixed.txt"
fi
