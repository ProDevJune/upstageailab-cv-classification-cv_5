#!/bin/bash
# AIStages 서버에서 v2 시스템 실행 스크립트

echo "🚀 AIStages 서버 - Code v2 System"
echo "================================"
echo "📂 Data: train.csv v1 (최고 성능 달성했던 원본 데이터)"
echo "💻 Code: gemini_main_v2.py (swin_base 기반)"
echo "⚙️ Config: config_v2.yaml"
echo "🆕 Features: 개선된 augmentation, dynamic augmentation, 향상된 모델"
echo ""

# 가상환경 확인
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 가상환경: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️  가상환경을 먼저 활성화하세요:"
    echo "   source venv/bin/activate"
    exit 1
fi

# GPU 확인
if command -v nvidia-smi &> /dev/null; then
    echo "✅ GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
else
    echo "⚠️  GPU를 확인할 수 없습니다."
fi

echo ""
echo "🎯 v2 시스템 실행 중..."

# v2 시스템 실행 (python3 명시)
python3 codes/gemini_main_v2.py --config codes/config_v2.yaml

echo ""
echo "✅ v2 시스템 실행 완료!"
echo ""
echo "📊 결과 확인:"
echo "  • 실험 결과: tail experiment_results.csv"
echo "  • 제출 파일: ls -la data/submissions/"
echo "  • 모델 파일: ls -la models/"
