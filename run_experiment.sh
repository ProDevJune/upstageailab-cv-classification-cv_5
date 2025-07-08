#!/bin/bash
# CV Classification 프로젝트 실행 스크립트

cd 

echo "🎯 EfficientNet-B4 실험 시작"
echo "절대 경로로 Python 실행하여 환경 문제 완전 우회"

# 절대 경로로 실행
venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml
