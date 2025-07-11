#!/bin/bash
# 실행 권한 부여
chmod +x fix_requirements_and_validate.sh
# 제대로 된 requirements 기반 패키지 설치 및 검증 스크립트

set -e

echo "🔧 requirements 기반 패키지 재설치 및 검증 시작..."

PROJECT_ROOT=""
cd "$PROJECT_ROOT"

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
fi

echo "🐍 현재 Python 버전: $(python --version)"
echo "📁 가상환경 경로: $VIRTUAL_ENV"

# pip 업그레이드
echo "⬆️  pip 업그레이드..."
pip install --upgrade pip setuptools wheel

# requirements_macos.txt에서 누락된 패키지들 설치
echo "📦 requirements_macos.txt 기반 패키지 설치..."
pip install -r requirements_macos.txt

echo ""
echo "🔍 주요 패키지 설치 확인..."

# 패키지별 확인
packages=(
    "torch:PyTorch"
    "torchvision:TorchVision" 
    "timm:TIMM"
    "numpy:NumPy"
    "pandas:Pandas"
    "yaml:PyYAML"
    "tqdm:tqdm"
    "psutil:psutil"
    "cv2:OpenCV"
    "PIL:Pillow"
)

all_ok=true

for package_info in "${packages[@]}"; do
    package_name="${package_info%%:*}"
    display_name="${package_info##*:}"
    
    if python -c "import $package_name; print(f'✅ $display_name: {getattr($package_name, \"__version__\", \"installed\")}')" 2>/dev/null; then
        :  # 성공
    else
        echo "❌ $display_name: 설치되지 않음"
        all_ok=false
    fi
done

echo ""
if [ "$all_ok" = true ]; then
    echo "✅ 모든 패키지 설치 완료!"
    echo ""
    echo "🧪 사전 검증 실행..."
    python pre_experiment_validator.py
else
    echo "❌ 일부 패키지 설치 실패"
    echo "🔧 개별 설치 시도..."
    
    # 개별적으로 문제가 되는 패키지 설치 시도
    if ! python -c "import yaml" 2>/dev/null; then
        echo "📦 pyyaml 개별 설치..."
        pip install pyyaml==6.0.2
    fi
    
    echo ""
    echo "🧪 사전 검증 재시도..."
    python pre_experiment_validator.py
fi

echo ""
echo "✅ 완료!"
