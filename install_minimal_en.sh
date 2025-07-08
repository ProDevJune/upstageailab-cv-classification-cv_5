#!/bin/bash
# AIStages Server Minimal Package Installation (English Version)

echo "⚡ AIStages Server Minimal Package Installation..."
echo "================================"

# Virtual Environment Check
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Please activate virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

echo "📦 Installing essential packages only..."

# PyTorch (CUDA 12.1)
echo "🔥 Installing PyTorch..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

# Core packages only
echo "🧠 Installing core packages..."
pip install timm transformers
pip install opencv-python albumentations pillow
pip install pandas numpy scikit-learn
pip install matplotlib pyyaml tqdm

echo ""
echo "🔍 Quick verification..."
python3 -c "
import torch, timm, transformers, cv2
print(f'✅ PyTorch: {torch.__version__}')
print(f'✅ CUDA: {torch.cuda.is_available()}')
print(f'✅ TIMM: {timm.__version__}')
print(f'✅ OpenCV: {cv2.__version__}')
print('🎉 Core packages installed successfully!')
"

echo ""
echo "🚀 Ready to run!"
echo "Execute with:"
echo "  ./run_aistages_v2_en.sh"
