#!/bin/bash

# 가장 간단한 CV_8U 오류 해결 스크립트
# pip 캐시나 복잡한 설정 없이 핵심만 처리

echo "🔧 CV_8U 오류 간단 해결..."

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

# 핵심 패키지만 제거하고 재설치
echo "🗑️ 패키지 제거..."
pip uninstall -y opencv-python albumentations

echo "📥 호환 버전 설치..."
pip install --no-cache-dir opencv-python==4.8.1.78
pip install --no-cache-dir albumentations==1.4.0

# 간단 테스트
echo "✅ 테스트..."
python -c "import cv2, albumentations; print('✅ 설치 완료:', cv2.__version__, albumentations.__version__)"

echo "🎉 완료! 실험을 다시 실행하세요."
