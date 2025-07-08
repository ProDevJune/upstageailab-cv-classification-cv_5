#!/bin/bash
# 모든 우선순위 실험 실행 스크립트

cd 

echo "🚀 황금 조합 실험 시리즈 시작"
echo "=" * 50

# 1순위: EfficientNet-B4 (현재 실행 중)
echo "✅ 1순위: EfficientNet-B4 (실행 중...)"

# 2순위: EfficientNet-B3
echo ""
echo "📋 2순위 실행 명령어:"
echo "venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b3_202507051902.yaml"

# 3순위: ConvNeXt-Base  
echo ""
echo "📋 3순위 실행 명령어:"
echo "venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_convnext_base_202507051902.yaml"

echo ""
echo "🎯 실행 가이드:"
echo "1. 현재 EfficientNet-B4 실험 완료 대기 (15-30분)"
echo "2. 완료 후 위 명령어들을 순차 실행"
echo "3. 또는 새 터미널에서 병렬 실행 가능"

echo ""
echo "⚡ 빠른 실행을 위한 개별 스크립트:"
echo "chmod +x run_b3.sh && ./run_b3.sh"
echo "chmod +x run_convnext.sh && ./run_convnext.sh"