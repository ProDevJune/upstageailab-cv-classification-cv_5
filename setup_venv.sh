#!/bin/bash

# 🚀 CV 분류 프로젝트 가상환경 설정 스크립트
# macOS Apple Silicon 최적화

echo "🔧 CV 분류 프로젝트 환경 설정 시작..."

# 1. 가상환경 생성
echo "📦 Python 가상환경 생성 중..."
python -m venv venv

# 2. 가상환경 활성화 확인
if [[ -f "venv/bin/activate" ]]; then
    echo "✅ 가상환경 생성 완료: venv/"
    echo ""
    echo "🔄 가상환경 활성화 중..."
    source venv/bin/activate
    echo "✅ 가상환경 활성화 완료"
else
    echo "❌ 가상환경 생성 실패"
    exit 1
fi

# 3. pip 업그레이드
echo ""
echo "📈 pip 업그레이드 중..."
pip install --upgrade pip

# 4. macOS Apple Silicon용 PyTorch 설치
echo ""
echo "🍎 macOS Apple Silicon용 PyTorch 설치 중..."
echo "   (MPS 가속 지원 버전)"
pip install torch torchvision torchaudio

# 5. 기타 필수 패키지 설치
echo ""
echo "📚 필수 패키지들 설치 중..."
pip install \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    psutil \
    scikit-learn \
    tqdm \
    pyyaml \
    pillow \
    opencv-python \
    albumentations \
    timm \
    wandb

# 6. requirements.txt 업데이트
echo ""
echo "📝 requirements.txt 업데이트 중..."
pip freeze > requirements_mac.txt

# 7. 설치 확인
echo ""
echo "🧪 설치 확인 중..."
python -c "
import torch
print(f'✅ PyTorch 버전: {torch.__version__}')
print(f'✅ CUDA 사용 가능: {torch.cuda.is_available()}') 
print(f'✅ MPS 사용 가능: {torch.backends.mps.is_available()}')

if torch.backends.mps.is_available():
    print('🍎 Apple Silicon MPS 가속 준비 완료!')
    device = torch.device('mps')
    x = torch.randn(10, 10).to(device)
    print(f'✅ MPS 텐서 테스트 성공: {x.device}')
else:
    print('💻 CPU 전용 모드')
"

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 환경 설정 완료!"
    echo ""
    echo "📋 다음 단계:"
    echo "1. 가상환경 활성화: source venv/bin/activate"
    echo "2. 플랫폼 감지 테스트: python test_platform_detection.py" 
    echo "3. HPO 시스템 시작: ./run_experiments.sh"
    echo ""
    echo "💡 가상환경 비활성화: deactivate"
else
    echo "❌ 패키지 설치 중 오류 발생"
    exit 1
fi

echo ""
echo "🔧 프로젝트별 설정 완료!"
echo "   가상환경: venv/"
echo "   요구사항: requirements_mac.txt"
echo "   플랫폼: macOS Apple Silicon 최적화"
