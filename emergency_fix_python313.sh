#!/bin/bash

# Python 3.13 원클릭 복구 스크립트

echo "🚨 Python 3.13 패키지 설치 오류 원클릭 복구"
echo "=" $(printf '=%.0s' {1..60})

# 현재 가상환경 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "🔌 가상환경 활성화 중..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo "❌ 가상환경을 찾을 수 없습니다."
        echo "🔧 가상환경 재생성:"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        exit 1
    fi
fi

echo "🐍 현재 Python 버전: $(python --version)"
echo "📍 가상환경 경로: $VIRTUAL_ENV"

# 방법 1: 최신 버전으로 재설치
echo ""
echo "🔧 방법 1: 최신 호환 버전으로 재설치 시도"
echo "-" $(printf -- '-%.0s' {1..40})

# 기존 PyTorch 제거
pip uninstall torch torchvision torchaudio -y

# 최신 버전 설치
echo "📥 PyTorch 최신 버전 설치 중..."
pip install torch torchvision torchaudio

if [ $? -eq 0 ]; then
    echo "✅ PyTorch 최신 버전 설치 성공"
    
    # 나머지 패키지들 설치
    echo "📥 나머지 패키지 설치 중..."
    pip install timm transformers huggingface-hub
    pip install numpy pandas scipy scikit-learn
    pip install opencv-python Pillow albumentations
    pip install pyyaml tqdm psutil wandb optuna
    pip install jupyter notebook ipykernel
    
    # 설치 검증
    echo "🔍 설치 검증 중..."
    python -c "
import torch
import torchvision  
import timm
import numpy as np
print('✅ 핵심 패키지 import 성공')
print(f'PyTorch: {torch.__version__}')
print(f'TorchVision: {torchvision.__version__}')
print(f'MPS 사용 가능: {torch.backends.mps.is_available()}')
"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Python 3.13 환경 복구 완료!"
        echo ""
        echo "🚀 다음 단계:"
        echo "   python pre_experiment_validator.py --quick-test"
        exit 0
    fi
fi

# 방법 2: 개별 설치
echo ""
echo "🔧 방법 2: 개별 패키지 설치 시도"
echo "-" $(printf -- '-%.0s' {1..40})

declare -a packages=(
    "torch"
    "torchvision" 
    "torchaudio"
    "timm"
    "numpy"
    "pandas"
    "opencv-python"
    "Pillow"
    "pyyaml"
    "tqdm"
    "psutil"
)

for package in "${packages[@]}"; do
    echo "📦 설치 중: $package"
    pip install "$package" --upgrade
    if [ $? -ne 0 ]; then
        echo "⚠️  $package 설치 실패 - 계속 진행"
    fi
done

# 최종 검증
echo ""
echo "🔍 최종 검증 중..."
python -c "
try:
    import torch
    import torchvision
    import numpy as np
    print('✅ 기본 패키지 사용 가능')
    print(f'PyTorch: {torch.__version__}')
    success = True
except ImportError as e:
    print(f'❌ Import 오류: {e}')
    success = False

if success:
    print('🎉 부분적 복구 성공')
else:
    print('❌ 복구 실패')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 부분적 복구 완료!"
    echo ""
    echo "⚠️  모든 패키지가 설치되지 않았을 수 있습니다."
    echo "🔧 완전한 해결을 위해 Python 3.11 사용을 권장합니다:"
    echo ""
    echo "   brew install python@3.11"
    echo "   rm -rf venv"
    echo "   /opt/homebrew/bin/python3.11 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements_macos.txt"
    echo ""
    echo "🚀 현재 상태로 테스트:"
    echo "   python pre_experiment_validator.py --quick-test"
else
    echo ""
    echo "❌ 모든 복구 시도 실패"
    echo ""
    echo "🔧 최종 권장 사항:"
    echo "   1. Python 3.11로 다운그레이드"
    echo "   2. 시스템 Python 재설치"
    echo "   3. 전문가 도움 요청"
    exit 1
fi
