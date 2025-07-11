#!/bin/bash

# 플랫폼별 가상환경 자동 설정 스크립트
# Mac OS (MPS) / Ubuntu (CUDA) / CPU 자동 감지 및 최적 환경 구성

set -e  # 에러 발생시 스크립트 중단

# 동적으로 프로젝트 루트 감지
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/venv"

echo "🔧 플랫폼별 가상환경 설정 시작..."
echo "프로젝트 경로: $PROJECT_ROOT"

# 현재 디렉토리를 프로젝트 루트로 변경
cd "$PROJECT_ROOT"

# Python 버전 확인 (수정된 비교 로직)
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "🐍 Python 버전: $PYTHON_VERSION"

# Python 3.8 이상 체크 (수정된 비교)
if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
    echo "❌ Python 3.8 이상이 필요합니다. 현재: $PYTHON_VERSION"
    echo "🔧 Python 업그레이드 방법:"
    echo "   brew install python@3.11  # macOS"
    echo "   sudo apt install python3.11  # Ubuntu"
    exit 1
else
    echo "✅ Python $PYTHON_VERSION 사용 가능"
fi

# 현재 가상환경 상태 확인
if [[ "$VIRTUAL_ENV" != "" ]]; then
    CURRENT_VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    echo "🔍 현재 활성화된 가상환경 감지: $VIRTUAL_ENV"
    echo "🐍 가상환경 Python 버전: $CURRENT_VENV_PYTHON_VERSION"
    
    # Python 3.11 또는 3.10이면 기존 가상환경 유지
    if [[ "$CURRENT_VENV_PYTHON_VERSION" == "3.11" ]] || [[ "$CURRENT_VENV_PYTHON_VERSION" == "3.10" ]]; then
        echo "✅ 적절한 Python 버전의 가상환경이 이미 활성화되어 있습니다."
        echo "🎯 기존 가상환경을 유지합니다: $CURRENT_VENV_PYTHON_VERSION"
        VENV_PYTHON_VERSION="$CURRENT_VENV_PYTHON_VERSION"
    else
        echo "⚠️  현재 가상환경 Python 버전($CURRENT_VENV_PYTHON_VERSION)이 권장 버전이 아닙니다."
        echo "🔧 새로운 가상환경을 생성합니다..."
        deactivate 2>/dev/null || true
        
        # 기존 가상환경 제거
        if [ -d "$VENV_PATH" ]; then
            echo "🗑️  기존 가상환경 제거 중..."
            rm -rf "$VENV_PATH"
        fi
        
        # 새 가상환경 생성
        echo "📦 새 가상환경 생성 중..."
        python3 -m venv "$VENV_PATH"
        
        # 가상환경 활성화
        echo "🔌 가상환경 활성화..."
        source "$VENV_PATH/bin/activate"
        
        # 가상환경 내 Python 버전 확인
        VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    fi
else
    echo "🔍 활성화된 가상환경이 없습니다."
    
    # 기존 가상환경이 있는지 확인
    if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
        echo "📁 기존 venv 폴더 발견 - 활성화 시도..."
        source "$VENV_PATH/bin/activate"
        EXISTING_VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        
        if [[ "$EXISTING_VENV_PYTHON_VERSION" == "3.11" ]] || [[ "$EXISTING_VENV_PYTHON_VERSION" == "3.10" ]]; then
            echo "✅ 기존 가상환경($EXISTING_VENV_PYTHON_VERSION)을 재사용합니다."
            VENV_PYTHON_VERSION="$EXISTING_VENV_PYTHON_VERSION"
        else
            echo "⚠️  기존 가상환경 Python 버전이 부적절합니다: $EXISTING_VENV_PYTHON_VERSION"
            echo "🗑️  기존 가상환경 제거 중..."
            deactivate 2>/dev/null || true
            rm -rf "$VENV_PATH"
            
            # 새 가상환경 생성
            echo "📦 새 가상환경 생성 중..."
            python3 -m venv "$VENV_PATH"
            
            # 가상환경 활성화
            echo "🔌 가상환경 활성화..."
            source "$VENV_PATH/bin/activate"
            
            # 가상환경 내 Python 버전 확인
            VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        fi
    else
        # 새 가상환경 생성
        echo "📦 새 가상환경 생성 중..."
        python3 -m venv "$VENV_PATH"
        
        # 가상환경 활성화
        echo "🔌 가상환경 활성화..."
        source "$VENV_PATH/bin/activate"
        
        # 가상환경 내 Python 버전 확인
        VENV_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    fi
fi
echo "📦 가상환경 내 Python 버전: $VENV_PYTHON_VERSION"

# 가상환경이 제대로 활성화되었는지 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ 가상환경 활성화 실패"
    exit 1
else
    echo "✅ 가상환경 활성화 성공: $VIRTUAL_ENV"
fi

# pip 업그레이드
echo "⬆️  pip 업그레이드..."
pip install --upgrade pip setuptools wheel

# 플랫폼 감지
OS=$(uname -s)
ARCH=$(uname -m)

echo "🖥️  감지된 플랫폼: $OS ($ARCH)"

# 플랫폼별 requirements 설치
case "$OS" in
    "Darwin")
        if [[ "$ARCH" == "arm64" ]]; then
            echo "🍎 Apple Silicon (M1/M2/M3) 감지 - MPS 환경 설정"
            # Python 버전에 따른 requirements 선택
            if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 13 ]]; then
                REQUIREMENTS_FILE="requirements_macos_py313.txt"
                echo "🐍 Python 3.13+ 감지 - 호환 버전 사용"
            else
                REQUIREMENTS_FILE="requirements_macos.txt"
            fi
        else
            echo "🍎 Intel Mac 감지 - CPU 환경 설정"
            REQUIREMENTS_FILE="requirements_cpu.txt"
        fi
        ;;
    "Linux")
        # NVIDIA GPU 확인
        if command -v nvidia-smi &> /dev/null; then
            echo "🐧 Ubuntu + NVIDIA GPU 감지 - CUDA 환경 설정"
            REQUIREMENTS_FILE="requirements_ubuntu.txt"
        else
            echo "🐧 Ubuntu CPU 감지 - CPU 환경 설정"
            REQUIREMENTS_FILE="requirements_cpu.txt"
        fi
        ;;
    *)
        echo "⚠️  알 수 없는 플랫폼 - CPU 환경으로 설정"
        REQUIREMENTS_FILE="requirements_cpu.txt"
        ;;
esac

echo "📋 사용할 requirements: $REQUIREMENTS_FILE"

# Requirements 파일 존재 확인
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "❌ Requirements 파일을 찾을 수 없습니다: $REQUIREMENTS_FILE"
    exit 1
fi

# 패키지 설치
echo "📥 패키지 설치 중... (시간이 걸릴 수 있습니다)"
echo "📄 사용할 requirements: $REQUIREMENTS_FILE"

# 패키지 설치 시도
if pip install -r "$REQUIREMENTS_FILE"; then
    echo "✅ 패키지 설치 성공"
else
    echo "❌ 패키지 설치 중 오류 발생"
    echo "🔧 문제 해결 방법:"
    echo "   1. pip install --upgrade pip setuptools wheel"
    echo "   2. pip install torch torchvision torchaudio  # 단계별 설치"
    echo "   3. pip install -r $REQUIREMENTS_FILE  # 다시 시도"
    echo ""
    echo "⚠️  Python 3.13은 일부 패키지와 호환성 문제가 있을 수 있습니다."
    echo "     Python 3.11 사용을 권장합니다."
    exit 1
fi

# 설치 검증
echo "🔍 설치 검증 중..."
python3 -c "
import torch
import torchvision
import timm
import numpy as np
import pandas as pd
import yaml
import cv2
import PIL
print('✅ 기본 패키지 import 성공')

# 디바이스 확인
if torch.cuda.is_available():
    print(f'✅ CUDA 사용 가능: {torch.cuda.device_count()}개 GPU')
    print(f'   주 GPU: {torch.cuda.get_device_name(0)}')
elif torch.backends.mps.is_available():
    print('✅ MPS (Apple Silicon) 사용 가능')
else:
    print('✅ CPU 모드로 설정됨')

print(f'PyTorch 버전: {torch.__version__}')
print(f'TorchVision 버전: {torchvision.__version__}')
print(f'TIMM 버전: {timm.__version__}')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 가상환경 설정 완료!"
    echo ""
    echo "📋 활성화 방법:"
    echo "   source venv/bin/activate"
    echo ""
    echo "🚀 다음 단계:"
    echo "   python pre_experiment_validator.py  # 사전 검증 실행"
    echo "   python experiments/experiment_generator.py  # 실험 생성"
    echo ""
else
    echo "❌ 패키지 설치 또는 검증 실패"
    exit 1
fi
