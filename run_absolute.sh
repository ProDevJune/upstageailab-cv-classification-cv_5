#!/bin/bash
# 절대 경로로 완전 해결 - 수정됨

echo "🎯 절대 경로로 EfficientNet-B4 실험 시작"

# 프로젝트 디렉토리로 이동
cd /data/ephemeral/home/upstageailab-cv-classification-cv_5

# 절대 경로로 설정 파일 지정
venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml