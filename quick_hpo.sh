#!/bin/bash

# 간단한 HPO 실행 스크립트 (문제 해결 버전)

echo "🚀 간단한 HPO 시스템 시작"
echo "=============================="

# 기본 확인
if [[ ! -f "codes/auto_experiment_basic.py" ]]; then
    echo "❌ codes/auto_experiment_basic.py 파일이 없습니다."
    exit 1
fi

# Python 및 패키지 확인
echo "📦 패키지 확인 중..."
python -c "
try:
    import torch
    import yaml
    import pandas as pd
    import numpy as np
    print('✅ 필수 패키지 확인 완료')
    print(f'PyTorch: {torch.__version__}')
    print(f'MPS 사용 가능: {torch.backends.mps.is_available()}')
except ImportError as e:
    print(f'❌ 패키지 오류: {e}')
    exit(1)
"

if [[ $? -ne 0 ]]; then
    echo "❌ 패키지 설치 필요"
    echo "해결법: python -m pip install torch pandas numpy PyYAML matplotlib seaborn psutil"
    exit 1
fi

# 메뉴 표시
echo ""
echo "🎯 HPO 실험 옵션:"
echo "1) ⚡ 빠른 실험 (5개)"
echo "2) 🔬 전체 실험 (20개)"
echo "3) 📊 실험 결과 확인"
echo "4) 🖥️ 플랫폼 정보"
echo ""
read -p "선택하세요 (1-4): " choice

case $choice in
    1)
        echo "⚡ 빠른 실험 시작..."
        python codes/auto_experiment_basic.py --type quick --max 5
        ;;
    2)
        echo "🔬 전체 실험 시작..."
        python codes/auto_experiment_basic.py --type quick --max 20
        ;;
    3)
        echo "📊 실험 결과 확인..."
        python codes/experiment_tracker.py --action summary
        ;;
    4)
        echo "🖥️ 플랫폼 정보..."
        python test_hpo_system.py
        ;;
    *)
        echo "❌ 잘못된 선택"
        ;;
esac
