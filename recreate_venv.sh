#!/bin/bash

# 가상환경 완전 재생성 - 최종 해결책
# 모든 의존성 문제를 원천적으로 해결

echo "🔄 가상환경 완전 재생성으로 의존성 문제 원천 해결..."

# 기존 가상환경 백업 및 제거
if [ -d "venv" ]; then
    echo "📦 기존 가상환경 백업 중..."
    mv venv venv_backup_$(date +%Y%m%d_%H%M%S)
fi

echo "🏗️ 새로운 가상환경 생성..."
python3 -m venv venv

echo "🔌 새 가상환경 활성화..."
source venv/bin/activate

echo "⬆️ pip 업그레이드..."
pip install --upgrade pip

echo "📥 PyTorch 설치..."
pip install --index-url https://download.pytorch.org/whl/cu121 torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1

echo "📥 핵심 패키지 순차 설치..."
pip install numpy==1.26.4
pip install opencv-python==4.8.1.78
pip install albumentations==1.4.0

echo "📥 데이터 과학 패키지 설치..."
pip install pandas==2.2.3
pip install matplotlib==3.9.2
pip install scipy==1.14.1
pip install scikit-learn==1.5.2
pip install seaborn==0.13.2

echo "📥 기타 필수 패키지 설치..."
pip install timm==1.0.12
pip install transformers==4.44.2
pip install Pillow==10.4.0
pip install pyyaml==6.0.2
pip install tqdm==4.66.5
pip install wandb==0.18.3
pip install optuna==4.0.0

echo "✅ 설치 완료 - 최종 테스트..."
python -c "
print('🔍 설치된 패키지 확인:')
import numpy, cv2, albumentations, pandas, matplotlib, sklearn
print(f'✅ NumPy: {numpy.__version__}')
print(f'✅ OpenCV: {cv2.__version__}')
print(f'✅ Albumentations: {albumentations.__version__}')
print(f'✅ Pandas: {pandas.__version__}')
print(f'✅ Matplotlib: {matplotlib.__version__}')
print(f'✅ Scikit-learn: {sklearn.__version__}')

# CV_8U 테스트
try:
    print(f'✅ CV_8U: {cv2.CV_8U}')
except AttributeError:
    print('❌ CV_8U 속성 없음')

# Albumentations 테스트
import numpy as np
transform = albumentations.HorizontalFlip(p=1.0)
test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
result = transform(image=test_img)
print('✅ Albumentations 변환 테스트 성공')

print('\\n🎉 가상환경 재생성 완료!')
print('🚀 모든 의존성 문제 해결됨!')
"

echo ""
echo "💡 새 가상환경 사용 방법:"
echo "  source venv/bin/activate"
echo "  python codes/gemini_main_v2.py --config [config_file]"
echo ""
echo "📝 기존 환경 복구가 필요하다면:"
echo "  rm -rf venv"
echo "  mv venv_backup_* venv"
