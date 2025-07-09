#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# AIStages 환경 빠른 체크 스크립트
echo "⚡ AIStages 빠른 환경 체크"
echo "=========================="

# GPU 메모리 (가장 중요)
echo "🎮 GPU 정보:"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
    
    # GPU 메모리 MB 단위로 추출해서 전략 제안
    GPU_MEMORY_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    GPU_MEMORY_GB=$((GPU_MEMORY_MB / 1024))
    
    echo "💡 권장 실행 전략 (GPU 메모리: ${GPU_MEMORY_GB}GB):"
    if [ $GPU_MEMORY_GB -ge 20 ]; then
        echo "   ✅ 모든 시스템 실행 가능 (V2_1, V2_2, V3)"
        echo "   🏆 추천: V2_1 시스템 (최고 성능)"
    elif [ $GPU_MEMORY_GB -ge 12 ]; then
        echo "   ✅ V2_2, V3 시스템 권장"
        echo "   🔥 추천: V3 계층적 시스템 (혁신적)"
    elif [ $GPU_MEMORY_GB -ge 8 ]; then
        echo "   ✅ V2_2 시스템 권장"
        echo "   ⚡ 추천: 효율적 모델 위주"
    else
        echo "   ⚠️  배치 크기 축소 필요"
        echo "   💡 추천: 작은 모델 + Mixed Precision"
    fi
else
    echo "❌ GPU 없음 - CPU 모드 (매우 느림)"
fi

echo ""
echo "🧮 메모리:"
free -h | grep Mem

echo ""
echo "💾 디스크 공간:"
df -h . | tail -1

echo ""
echo "🐍 Python & PyTorch:"
python -c "
import torch
print(f'Python: {torch.version.__version__ if hasattr(torch.version, \"__version__\") else \"Unknown\"}')
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
" 2>/dev/null || echo "PyTorch 설치 확인 필요"

echo ""
echo "🚀 빠른 실행 명령어:"
echo "   전체 시스템 체크: ./check_aistages_system.sh"
echo "   ML 호환성 체크: ./check_ml_compatibility.sh"
echo "   V2_2 실험 시작: ./run_v2_2_only.sh"
echo ""
