#!/bin/bash
# 절대 경로로 완전 해결 - 환경변수 지원 (강제 업데이트)

echo "🎯 절대 경로로 EfficientNet-B4 실험 시작"

# 프로젝트 디렉토리로 이동
cd /data/ephemeral/home/upstageailab-cv-classification-cv_5

# 환경변수에서 설정 파일 가져오기 (예비 경로 포함)
if [ -n "$EXPERIMENT_CONFIG" ]; then
    # 상대 경로를 절대 경로로 변환
    if [[ "$EXPERIMENT_CONFIG" = /* ]]; then
        CONFIG_FILE="$EXPERIMENT_CONFIG"
    else
        CONFIG_FILE="/data/ephemeral/home/upstageailab-cv-classification-cv_5/$EXPERIMENT_CONFIG"
    fi
else
    CONFIG_FILE="${1:-codes/practice/exp_golden_efficientnet_b4_202507051902.yaml}"
fi

echo "📄 사용할 설정 파일: $CONFIG_FILE"
echo "🔍 설정 파일 존재 확인: $(ls -la \"$CONFIG_FILE\" 2>/dev/null && echo '✅ 존재' || echo '❌ 없음')"

# 실제 실행
venv/bin/python codes/gemini_main.py --config "$CONFIG_FILE"
