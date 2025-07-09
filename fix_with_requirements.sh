#!/bin/bash

# Requirements 파일을 사용한 완전 호환성 복구 스크립트

echo "🔧 Requirements 파일로 완전 호환성 복구..."

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

echo "🗑️ 문제가 있는 패키지들 제거..."
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python
pip uninstall -y albumentations numpy pandas scikit-learn matplotlib scipy

echo "📥 호환성 검증된 requirements로 재설치..."
pip install --no-cache-dir -r requirements_ubuntu_complete_fix.txt

echo "✅ 간단 테스트..."
python -c "
import cv2, albumentations, numpy, pandas
print(f'✅ NumPy: {numpy.__version__}')
print(f'✅ OpenCV: {cv2.__version__}')  
print(f'✅ Albumentations: {albumentations.__version__}')
print(f'✅ Pandas: {pandas.__version__}')
print('🎉 호환성 문제 해결 완료!')
"

echo "🚀 실험 재실행 가능!"
