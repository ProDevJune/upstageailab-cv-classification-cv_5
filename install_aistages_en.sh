#!/bin/bash
# AIStages Server Environment Setup (English Version)

echo "🚀 AIStages Server Environment Setup..."
echo "================================"

# System Information
echo "📊 System Information:"
echo "  OS: $(uname -s)"
echo "  Architecture: $(uname -m)"
echo "  Python: $(python3 --version)"

# GPU Check
if command -v nvidia-smi &> /dev/null; then
    echo "  GPU: ✅ $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
    nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1 | awk '{print "  VRAM: "$1}'
else
    echo "  GPU: ❌ NVIDIA GPU not found"
fi

# Virtual Environment Check
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "  Virtual Env: ✅ $(basename $VIRTUAL_ENV)"
else
    echo "  Virtual Env: ❌ Activation required"
    echo ""
    echo "⚠️  Please activate virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

echo ""
echo "📦 Step-by-step Package Installation..."

# Step 1: pip upgrade
echo "⬆️  Step 1: Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Step 2: PyTorch Installation (CUDA 12.1)
echo "🔥 Step 2: Installing PyTorch (CUDA 12.1)..."
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

if [ $? -ne 0 ]; then
    echo "❌ PyTorch installation failed"
    exit 1
fi

# Step 3: Core ML Packages
echo "🧠 Step 3: Core ML packages..."
pip install --no-deps timm==1.0.12
pip install transformers==4.44.2 huggingface-hub

# Step 4: Computer Vision Packages
echo "📷 Step 4: Computer Vision packages..."
pip install opencv-python==4.10.0.84
pip install Pillow==10.4.0
pip install albumentations==1.4.18

# Step 5: Data Processing Packages
echo "📊 Step 5: Data processing packages..."
pip install numpy==1.26.4
pip install pandas==2.2.3
pip install scikit-learn==1.5.2

# Step 6: Utility Packages
echo "🔧 Step 6: Utility packages..."
pip install pyyaml==6.0.2
pip install tqdm==4.66.5
pip install matplotlib==3.9.2
pip install seaborn

# Step 7: Experiment Management
echo "📈 Step 7: Experiment management..."
pip install wandb==0.18.3
pip install optuna==4.0.0

# Step 8: CUDA Support
echo "⚡ Step 8: CUDA support packages..."
pip install accelerate==1.0.1

echo ""
echo "✅ All packages installed successfully!"

# Installation Check
echo ""
echo "🔍 Installation verification..."
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
echo "🎯 Next Steps:"
echo "1. Run v2 system: ./run_aistages_v2.sh"
echo "2. Or run v1 system: python3 codes/gemini_main.py --config codes/config.yaml"
echo "3. Monitor experiments: tail -f experiment_results.csv"
echo ""
echo "💡 Tips:"
echo "  • GPU monitoring: watch -n 1 nvidia-smi"
echo "  • Check submissions: ls -la data/submissions/"
echo "  • View results: tail experiment_results.csv"
