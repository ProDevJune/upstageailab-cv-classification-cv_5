#!/bin/bash
# AIStages 서버 전용 설치 스크립트 (단계별 설치)

echo "🚀 AIStages 서버 환경 설정 시작..."
echo "================================"

# 환경 정보 확인
echo "📊 시스템 정보:"
echo "  OS: $(uname -s)"
echo "  아키텍처: $(uname -m)"
echo "  Python: $(python3 --version)"

# GPU 확인
if command -v nvidia-smi &> /dev/null; then
    echo "  GPU: ✅ $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
    nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1 | awk '{print "  VRAM: "$1}'
else
    echo "  GPU: ❌ NVIDIA GPU 없음"
fi

# 가상환경 확인
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "  가상환경: ✅ $(basename $VIRTUAL_ENV)"
else
    echo "  가상환경: ❌ 활성화 필요"
    echo ""
    echo "⚠️  가상환경을 먼저 활성화하세요:"
    echo "   source venv/bin/activate"
    exit 1
fi

echo ""
echo "📦 단계별 패키지 설치 시작..."

# Step 1: pip 업그레이드
echo "⬆️  Step 1: pip 업그레이드..."
pip install --upgrade pip setuptools wheel

# Step 2: PyTorch 설치 (CUDA 12.1)
echo "🔥 Step 2: PyTorch 설치 (CUDA 12.1)..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

if [ $? -ne 0 ]; then
    echo "❌ PyTorch 설치 실패"
    exit 1
fi

# Step 3: 핵심 ML 패키지 (기본 PyPI에서 설치)
echo "🧠 Step 3: 핵심 ML 패키지..."
pip install --no-deps timm==1.0.12
pip install transformers==4.44.2 huggingface-hub

# Step 4: 컴퓨터 비전 패키지
echo "📷 Step 4: 컴퓨터 비전 패키지..."
pip install opencv-python==4.10.0.84
pip install Pillow==10.4.0
pip install albumentations==1.4.18

# Step 5: 데이터 처리 패키지
echo "📊 Step 5: 데이터 처리 패키지..."
pip install numpy==1.26.4
pip install pandas==2.2.3
pip install scikit-learn==1.5.2

# Step 6: 유틸리티 패키지
echo "🔧 Step 6: 유틸리티 패키지..."
pip install pyyaml==6.0.2
pip install tqdm==4.66.5
pip install matplotlib==3.9.2
pip install seaborn

# Step 7: 실험 관리 패키지
echo "📈 Step 7: 실험 관리 패키지..."
pip install wandb==0.18.3
pip install optuna==4.0.0

# Step 8: CUDA 지원 패키지
echo "⚡ Step 8: CUDA 지원 패키지..."
pip install accelerate==1.0.1

echo ""
echo "✅ 모든 패키지 설치 완료!"

# 설치 확인
echo ""
echo "🔍 설치 확인..."
python3 -c "
import sys
print(f'Python: {sys.version.split()[0]}')

try:
    import torch
    print(f'✅ PyTorch: {torch.__version__}')
    print(f'✅ CUDA: {torch.cuda.is_available()} ({torch.version.cuda if torch.cuda.is_available() else \"N/A\"})')
    if torch.cuda.is_available():
        print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
        print(f'✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB')
except Exception as e:
    print(f'❌ PyTorch: {e}')

packages = [
    ('timm', 'TIMM'),
    ('transformers', 'Transformers'), 
    ('cv2', 'OpenCV'),
    ('albumentations', 'Albumentations'),
    ('pandas', 'Pandas'),
    ('numpy', 'NumPy'),
    ('sklearn', 'Scikit-learn'),
    ('matplotlib', 'Matplotlib'),
    ('wandb', 'WandB'),
    ('optuna', 'Optuna')
]

for pkg, name in packages:
    try:
        if pkg == 'cv2':
            import cv2
            print(f'✅ {name}: {cv2.__version__}')
        elif pkg == 'sklearn':
            import sklearn
            print(f'✅ {name}: {sklearn.__version__}')
        else:
            module = __import__(pkg)
            version = getattr(module, '__version__', 'Unknown')
            print(f'✅ {name}: {version}')
    except Exception as e:
        print(f'❌ {name}: Failed to import')
"

echo ""
echo "🎯 다음 단계:"
echo "1. v2 시스템 실행: ./run_aistages_v2.sh"
echo "2. 또는 v1 시스템: python3 codes/gemini_main.py --config codes/config.yaml"
echo "3. 실험 모니터링: tail -f experiment_results.csv"
echo ""
echo "💡 팁:"
echo "  • GPU 모니터링: watch -n 1 nvidia-smi"
echo "  • 제출 파일 확인: ls -la data/submissions/"
echo "  • 실험 결과: tail experiment_results.csv"
