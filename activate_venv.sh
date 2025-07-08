#!/bin/bash

# 🔄 가상환경 빠른 활성화 스크립트

if [[ -f "venv/bin/activate" ]]; then
    echo "🔄 가상환경 활성화 중..."
    source venv/bin/activate
    echo "✅ 가상환경 활성화 완료!"
    echo ""
    echo "🎯 사용 가능한 명령어들:"
    echo "  python test_platform_detection.py  # 플랫폼 테스트"
    echo "  ./run_experiments.sh              # HPO 시스템 시작"
    echo "  deactivate                        # 가상환경 비활성화"
    echo ""
    
    # Python 버전 및 주요 패키지 확인
    echo "📋 환경 정보:"
    python --version
    echo "가상환경: $(which python)"
    
    # PyTorch 설치 확인
    python -c "
try:
    import torch
    print(f'PyTorch: {torch.__version__}')
    if torch.backends.mps.is_available():
        print('🍎 MPS 가속 사용 가능')
    elif torch.cuda.is_available():
        print('🚀 CUDA 가속 사용 가능')
    else:
        print('💻 CPU 전용')
except ImportError:
    print('❌ PyTorch 미설치 - setup_venv.sh 실행 필요')
" 2>/dev/null
    
else
    echo "❌ 가상환경이 없습니다."
    echo ""
    echo "🔧 가상환경 설정 방법:"
    echo "  1. ./setup_venv.sh              # 자동 설정"
    echo "  2. python -m venv venv          # 수동 생성"
    echo "     source venv/bin/activate     # 수동 활성화"
fi
