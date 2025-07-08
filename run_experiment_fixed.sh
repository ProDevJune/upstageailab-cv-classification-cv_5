#!/bin/bash
# 올바른 경로로 실험 실행

cd 

echo "🎯 EfficientNet-B4 실험 시작 (경로 수정됨)"

# 올바른 상대 경로로 실행
venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml