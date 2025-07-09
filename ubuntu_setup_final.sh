#!/bin/bash

# 🚀 Ubuntu 환경 최종 설정 스크립트 
# 정밀 소스 분석 기반

echo "🐧 Ubuntu 환경 최종 설정 시작..."
echo "================================"

# 1. 환경 정보 출력
echo "📊 시스템 정보:"
echo "  OS: $(uname -s)"
echo "  아키텍처: $(uname -m)"
echo "  Python: $(python3.11 --version 2>/dev/null || echo '미설치')"
echo "  현재 경로: $(pwd)"

# 2. GPU 확인
if command -v nvidia-smi &> /dev/null; then
    echo "  GPU: ✅ NVIDIA GPU 감지"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
else
    echo "  GPU: ❌ NVIDIA GPU 없음 (CPU 모드)"
fi

echo ""

# 3. 가상환경 확인
if [ -f "venv/bin/activate" ]; then
    echo "✅ 가상환경 이미 존재"
    source venv/bin/activate
else
    echo "⚠️ 가상환경 없음. 생성이 필요합니다."
    echo "다음 명령어를 실행하세요:"
    echo "  sudo apt install python3.11-venv python3.11-dev"
    echo "  python3.11 -m venv venv"
    echo "  source venv/bin/activate"
    exit 1
fi

# 4. pip 업그레이드
echo "📈 pip 업그레이드..."
pip install --upgrade pip

# 5. 정확한 패키지 설치
echo "📦 정밀 분석된 패키지 설치 시작..."

# PyTorch CUDA
echo "  🔥 PyTorch CUDA 설치..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

# 컴퓨터 비전
echo "  👁️ 컴퓨터 비전 라이브러리..."
pip install timm==0.9.16 opencv-python==4.9.0.80 albumentations==1.4.13 Pillow==10.3.0 imageio==2.34.2

# 딥러닝 유틸리티
echo "  🤖 딥러닝 유틸리티..."
pip install transformers==4.42.4 huggingface-hub==0.24.5 accelerate==0.33.0

# 데이터 사이언스
echo "  📊 데이터 사이언스..."
pip install pandas==2.0.3 numpy==1.24.4 scipy==1.11.4 scikit-learn==1.3.2 matplotlib==3.7.5 seaborn==0.12.2

# 유틸리티
echo "  🛠️ 유틸리티..."
pip install PyYAML==6.0.1 tqdm==4.66.4 psutil==5.9.8

# 실험 도구
echo "  🔬 실험 도구..."
pip install wandb==0.17.7 optuna==3.6.1

# 6. 설치 검증
echo ""
echo "🧪 설치 검증 중..."
python -c "
import torch
import timm
import albumentations as A
import cv2
import pandas as pd
import numpy as np
import yaml
import wandb
import optuna
from sklearn.metrics import f1_score

print('🎉 모든 핵심 패키지 임포트 성공!')
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ CUDA 사용 가능: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'✅ GPU 개수: {torch.cuda.device_count()}')
    print(f'✅ GPU 이름: {torch.cuda.get_device_name(0)}')
print(f'✅ timm: {timm.__version__}')
print(f'✅ albumentations: {A.__version__}')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Ubuntu 환경 설정 완료!"
    echo ""
    echo "✅ 설정 완료 항목:"
    echo "  • PyTorch 2.4.1 (CUDA 12.1)"
    echo "  • timm 0.9.16 (호환 버전)"
    echo "  • albumentations 1.4.13"
    echo "  • 모든 필수 패키지"
    echo ""
    echo "🚀 바로 시작하기:"
    echo "  python aistages_manager.py"
    echo "  → 메뉴 1번 → quick 실험"
    echo ""
    echo "🔧 또는 단일 실험:"
    echo "  python codes/gemini_main_v2.py --config codes/config.yaml"
else
    echo ""
    echo "❌ 패키지 설치 중 오류 발생"
    echo "수동으로 requirements 파일 사용:"
    echo "  pip install -r requirements_ubuntu_final.txt"
    exit 1
fi
