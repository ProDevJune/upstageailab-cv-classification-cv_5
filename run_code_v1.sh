#!/bin/bash

# 🔧 코드 v1 실행 스크립트 (기존 시스템)
# 사용법: ./run_code_v1.sh

echo "🚀 Starting Code v1 System (기존 시스템)"
echo "📂 Data: train.csv v1 (최고 성능 달성했던 원본 데이터)"
echo "💻 Code: gemini_main.py (resnet50 기반)"
echo "⚙️ Config: config.yaml"
echo ""

# 실행
python codes/gemini_main.py --config codes/config.yaml

echo ""
echo "✅ Code v1 실행 완료!"
