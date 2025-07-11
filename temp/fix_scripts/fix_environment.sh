#!/bin/bash

# 실행 권한 추가
chmod +x "$0"

echo "🔧 환경 문제 해결 시작..."
echo "=================================="

# 현재 Python 환경 확인
echo "📍 현재 Python 환경:"
which python
python --version
echo ""

# pip 업그레이드
echo "📦 pip 업그레이드..."
python -m pip install --upgrade pip

# 필수 패키지들 설치
echo ""
echo "📚 필수 패키지 설치 중..."

# 기본 라이브러리들
python -m pip install numpy pandas matplotlib seaborn

# 머신러닝 라이브러리들
python -m pip install scikit-learn

# 딥러닝 관련
python -m pip install timm albumentations

# 유틸리티들
python -m pip install tqdm pillow opencv-python PyYAML psutil

# Weights & Biases (선택사항)
python -m pip install wandb

echo ""
echo "🧪 설치 검증 테스트..."

python -c "
import sys
import importlib

required_modules = [
    'numpy', 'pandas', 'matplotlib', 'seaborn',
    'sklearn', 'torch', 'torchvision', 'timm',
    'albumentations', 'cv2', 'PIL', 'yaml',
    'tqdm', 'psutil'
]

print('📋 모듈 설치 상태 확인:')
missing = []

for module in required_modules:
    try:
        importlib.import_module(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module} - 누락됨')
        missing.append(module)

if missing:
    print(f'\\n❌ 누락된 모듈들: {missing}')
    print('다음 명령으로 수동 설치해보세요:')
    for module in missing:
        if module == 'cv2':
            print('pip install opencv-python')
        elif module == 'sklearn':
            print('pip install scikit-learn')
        else:
            print(f'pip install {module}')
else:
    print('\\n🎉 모든 필수 모듈이 설치되었습니다!')
"

echo ""
echo "🚀 이제 Code v2를 다시 실행해보세요:"
echo "./run_code_v2.sh"
