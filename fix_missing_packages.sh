#!/bin/bash
# 실행 권한 설정
chmod +x fix_missing_packages.sh
# Python 3.13 환경에서 누락된 패키지 설치 스크립트

echo "🔧 누락된 패키지 설치 시작..."

# 가상환경 활성화
source venv/bin/activate

# 누락된 패키지들 설치
echo "📦 pyyaml 설치 중..."
pip install pyyaml>=6.0.0

echo "📦 기타 필수 패키지 확인 및 설치..."
pip install --upgrade pip
pip install wheel setuptools

# Python 3.13 호환 패키지들 설치
echo "📦 Python 3.13 호환 패키지 설치 중..."
pip install -r requirements_macos_py313.txt

echo "✅ 패키지 설치 완료!"
echo "🚀 이제 다시 ./setup_and_validate_all.sh를 실행해보세요."
