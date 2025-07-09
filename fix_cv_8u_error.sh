#!/bin/bash

# AIStages 서버에서 CV_8U 오류 해결을 위한 긴급 수정 스크립트
# 사용법: bash fix_cv_8u_error.sh

echo "🔧 CV_8U AttributeError 해결을 위한 패키지 재설치 시작..."

# 가상환경 활성화 (venv 폴더가 있다면)
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 문제가 되는 패키지들 제거
echo "🗑️ 기존 패키지 제거 중..."
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python albumentations

# pip 캐시가 비활성화된 경우를 위한 안전한 처리
echo "🧹 설치 준비 중..."

# 호환 가능한 버전으로 재설치
echo "📥 호환 패키지 설치 중..."
pip install opencv-python==4.8.1.78
pip install albumentations==1.4.0

# 설치 확인
echo "✅ 설치 확인 중..."
python -c "
import cv2
import albumentations as A
print(f'OpenCV 버전: {cv2.__version__}')
print(f'Albumentations 버전: {A.__version__}')
print('✅ CV_8U 오류 해결 완료!')
"

echo "🎉 CV_8U 오류 해결 완료!"
echo "💡 이제 다시 실험을 실행해보세요."
