#!/bin/bash

# 🔧 코드 v2 실행 스크립트 (Linux 호환)
# 사용법: ./run_code_v2.sh

echo "🚀 Starting Code v2 System (새 시스템)"
echo "📂 Data: train.csv v1 (최고 성능 달성했던 원본 데이터)"
echo "💻 Code: gemini_main_v2.py (swin_base 기반)"
echo "⚙️ Config: config_v2.yaml"
echo "🆕 Features: 개선된 augmentation, dynamic augmentation, 향상된 모델"
echo ""

# 현재 디렉토리 확인
echo "📍 Current directory: $(pwd)"
echo "📍 Python path: $(which python3 || which python)"

# Albumentations 업데이트 체크 비활성화
export NO_ALBUMENTATIONS_UPDATE=1

# Python 경로 설정하여 실행 (Linux 호환)
export PYTHONPATH="$PWD:$PWD/codes:$PYTHONPATH"

# 실행 (config 파일명만 전달)
python3 codes/gemini_main_v2.py --config config_v2.yaml || python codes/gemini_main_v2.py --config config_v2.yaml

echo ""
echo "✅ Code v2 실행 완료!"
