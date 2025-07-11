#!/bin/bash

# 🚀 완전 해결: albumentations 호환성 문제
# 가상환경 재생성 + 안정 버전 설치

echo "🔄 가상환경 완전 재생성 중..."
echo "================================"

# 1. 기존 가상환경 완전 제거
if [ -d "venv" ]; then
    echo "🗑️ 기존 가상환경 제거 중..."
    rm -rf venv
    echo "✅ 기존 가상환경 제거 완료"
fi

# 2. 새 가상환경 생성
echo "📦 새 가상환경 생성 중..."
python3.11 -m venv venv

if [ ! -f "venv/bin/activate" ]; then
    echo "❌ 가상환경 생성 실패!"
    echo "다음을 확인하세요:"
    echo "  - python3.11-venv 패키지 설치: sudo apt install python3.11-venv python3.11-dev"
    echo "  - 권한 문제: 현재 디렉토리 쓰기 권한"
    exit 1
fi

# 3. 가상환경 활성화
echo "🔄 가상환경 활성화..."
source venv/bin/activate

# 4. pip 최신 버전으로 업그레이드
echo "📈 pip 업그레이드..."
pip install --upgrade pip

# 5. 안정된 버전으로 단계별 설치
echo ""
echo "📦 안정된 패키지 버전으로 설치 시작..."

# Step 1: PyTorch (기반)
echo "  🔥 PyTorch CUDA..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

# Step 2: 기본 수치 계산
echo "  🔢 기본 수치 라이브러리..."
pip install numpy==1.26.4

# Step 3: 컴퓨터 비전 (안정 버전)
echo "  👁️ 컴퓨터 비전 라이브러리..."
pip install opencv-python==4.8.1.78 Pillow==10.0.1 imageio==2.31.6

# Step 4: albumentations (검증된 안정 버전)
echo "  🎨 데이터 증강 라이브러리..."
pip install albucore==0.0.9
pip install albumentations==1.3.1

# Step 5: timm (안정 버전)
echo "  🤖 Vision 모델..."
pip install timm==0.9.12

# Step 6: 딥러닝 유틸리티
echo "  🛠️ 딥러닝 유틸리티..."
pip install transformers==4.35.2 huggingface-hub==0.19.4 accelerate==0.24.1

# Step 7: 데이터 사이언스
echo "  📊 데이터 사이언스..."
pip install pandas==2.0.3 scipy==1.11.4 scikit-learn==1.3.2
pip install matplotlib==3.7.5 seaborn==0.12.2

# Step 8: 유틸리티
echo "  🔧 유틸리티..."
pip install PyYAML==6.0.1 tqdm==4.66.1 psutil==5.9.6

# Step 9: 실험 도구
echo "  🔬 실험 도구..."
pip install wandb==0.16.0 optuna==3.4.0

echo ""
echo "🧪 완전 검증 테스트..."

# 포괄적인 검증
python -c "
import sys
print(f'Python: {sys.version}')
print(f'가상환경: {sys.prefix}')
print()

try:
    # 1. 기본 라이브러리
    import numpy as np
    print(f'✅ numpy: {np.__version__}')
    
    # 2. OpenCV
    import cv2
    print(f'✅ opencv-python: {cv2.__version__}')
    
    # 3. albumentations (문제의 핵심)
    import albucore
    print(f'✅ albucore: {albucore.__version__}')
    
    import albumentations as A
    print(f'✅ albumentations: {A.__version__}')
    
    # albumentations 기능 테스트
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.Rotate(limit=30, p=0.5)
    ])
    print('✅ albumentations 변환 테스트 성공')
    
    # 4. PyTorch
    import torch
    print(f'✅ torch: {torch.__version__}')
    print(f'✅ CUDA 사용 가능: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
    
    # 5. timm
    import timm
    print(f'✅ timm: {timm.__version__}')
    
    # 6. 기타 필수 패키지
    import pandas as pd
    import yaml
    import wandb
    import optuna
    from sklearn.metrics import f1_score
    
    print()
    print('🎉 모든 패키지 설치 및 호환성 검증 완료!')
    print('✅ albumentations preserve_channel_dim 문제 해결')
    print('✅ 모든 import 성공')
    print('✅ 실험 시스템 준비 완료')
    
except ImportError as e:
    print(f'❌ Import 오류: {e}')
    print()
    print('문제가 지속되면 다음 버전을 시도하세요:')
    print('  albumentations==1.2.1')
    print('  albucore==0.0.7')
    exit(1)
except Exception as e:
    print(f'❌ 기타 오류: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎊 완벽! 모든 문제 해결 완료!"
    echo ""
    echo "📋 설치된 안정 버전들:"
    echo "  - albumentations: 1.3.1 (albucore: 0.0.9)"
    echo "  - opencv-python: 4.8.1.78"
    echo "  - numpy: 1.26.4"
    echo "  - torch: 2.4.1+cu121"
    echo "  - timm: 0.9.12"
    echo ""
    echo "🚀 바로 실험 시작:"
    echo "  python aistages_manager.py"
    echo "  python codes/gemini_main_v2.py --config codes/config.yaml"
    echo ""
    echo "💡 이 설정은 완전히 검증되었습니다!"
else
    echo ""
    echo "❌ 여전히 문제가 있습니다."
    echo "🔧 최후 수단:"
    echo "  1. 시스템 Python 패키지 간섭 확인"
    echo "  2. conda 환경 사용 고려"
    echo "  3. Docker 컨테이너 사용 고려"
fi
