#!/bin/bash

# Python 3.13 PyTorch 설치 복구 스크립트

echo "🔧 Python 3.13 PyTorch 설치 복구 중..."

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "🔌 가상환경 활성화 중..."
    source venv/bin/activate
fi

echo "📦 단계별 패키지 설치 시작..."

# 1. 핵심 PyTorch 먼저 설치 (최신 버전)
echo "1️⃣ PyTorch 최신 버전 설치 중..."
pip install torch torchvision torchaudio --upgrade

if [ $? -eq 0 ]; then
    echo "✅ PyTorch 설치 성공"
else
    echo "❌ PyTorch 설치 실패"
    exit 1
fi

# 2. 기본 과학 계산 라이브러리
echo "2️⃣ 기본 라이브러리 설치 중..."
pip install numpy pandas scipy scikit-learn matplotlib seaborn

# 3. 딥러닝 라이브러리
echo "3️⃣ 딥러닝 라이브러리 설치 중..."
pip install timm transformers huggingface-hub accelerate

# 4. 컴퓨터 비전 라이브러리
echo "4️⃣ 컴퓨터 비전 라이브러리 설치 중..."
pip install opencv-python Pillow albumentations imageio

# 5. OCR 라이브러리
echo "5️⃣ OCR 라이브러리 설치 중..."
pip install easyocr pytesseract

# 6. 유틸리티 라이브러리
echo "6️⃣ 유틸리티 라이브러리 설치 중..."
pip install pyyaml tqdm psutil wandb

# 7. HPO 라이브러리 (선택적)
echo "7️⃣ HPO 라이브러리 설치 중..."
pip install optuna

# 8. 개발 도구
echo "8️⃣ 개발 도구 설치 중..."
pip install jupyter notebook ipykernel pytest pytest-cov

echo ""
echo "🔍 설치 검증 중..."

# 설치 검증
python3 -c "
import torch
import torchvision
import timm
import numpy as np
import pandas as pd
import cv2
import PIL
print('✅ 모든 핵심 패키지 import 성공')

# 디바이스 확인
if torch.backends.mps.is_available():
    print('✅ MPS (Apple Silicon) 사용 가능')
    device = 'mps'
else:
    print('⚠️  MPS 사용 불가 - CPU 모드')
    device = 'cpu'

print(f'PyTorch 버전: {torch.__version__}')
print(f'TorchVision 버전: {torchvision.__version__}')
print(f'TIMM 버전: {timm.__version__}')
print(f'사용 디바이스: {device}')

# 간단한 텐서 연산 테스트
x = torch.randn(10, 10).to(device)
y = torch.mm(x, x.t())
print(f'텐서 연산 테스트: {y.shape} on {device}')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Python 3.13 환경 설정 완료!"
    echo ""
    echo "📋 설치된 주요 패키지:"
    echo "   - PyTorch: $(python -c 'import torch; print(torch.__version__)')"
    echo "   - TorchVision: $(python -c 'import torchvision; print(torchvision.__version__)')"
    echo "   - TIMM: $(python -c 'import timm; print(timm.__version__)')"
    echo "   - NumPy: $(python -c 'import numpy; print(numpy.__version__)')"
    echo ""
    echo "🚀 다음 단계:"
    echo "   python pre_experiment_validator.py --quick-test"
else
    echo "❌ 환경 설정 실패"
    echo ""
    echo "🔧 수동 해결 방법:"
    echo "   1. Python 3.11 사용 권장:"
    echo "      brew install python@3.11"
    echo "      /opt/homebrew/bin/python3.11 -m venv venv"
    echo "      source venv/bin/activate"
    echo "      pip install -r requirements_macos.txt"
    echo ""
    echo "   2. 또는 개별 패키지 수동 설치:"
    echo "      pip install torch torchvision torchaudio"
    echo "      pip install timm transformers"
    echo "      pip install opencv-python Pillow"
    exit 1
fi
