#!/bin/bash
# AIStages 서버 최소 패키지 설치 (빠른 설치)

echo "⚡ AIStages 서버 최소 패키지 설치..."
echo "================================"

# 가상환경 확인
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  가상환경을 먼저 활성화하세요:"
    echo "   source venv/bin/activate"
    exit 1
fi

echo "📦 필수 패키지만 빠르게 설치 중..."

# PyTorch (CUDA 12.1)
echo "🔥 PyTorch 설치..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

# 핵심 패키지만
echo "🧠 핵심 패키지 설치..."
pip install timm transformers
pip install opencv-python albumentations pillow
pip install pandas numpy scikit-learn
pip install matplotlib pyyaml tqdm

echo ""
echo "🔍 빠른 확인..."
python3 -c "
import torch, timm, transformers, cv2
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ CUDA: {torch.cuda.is_available()}')
print(f'✅ TIMM: {timm.__version__}')
print(f'✅ OpenCV: {cv2.__version__}')
print('🎉 핵심 패키지 설치 완료!')
"

echo ""
echo "🚀 실행 준비 완료!"
echo "다음 명령어로 실행하세요:"
echo "  ./run_aistages_v2.sh"
