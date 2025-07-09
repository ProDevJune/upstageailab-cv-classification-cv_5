#!/bin/bash

# Ubuntu 서버에서 실험 실행을 위한 스크립트
echo "🎯 EfficientNet-B4 실험 실행 준비..."

# 설정 파일 존재 확인
config_file="temp_configs/018_opt_AdamW_lr0.001_wd0.001_2507091740.yaml"
if [ -f "$config_file" ]; then
    echo "✅ 설정 파일 발견: $config_file"
    echo "🚀 실험 실행 중..."
    EXPERIMENT_CONFIG="$config_file" ./run_absolute.sh
else
    echo "❌ 설정 파일을 찾을 수 없습니다: $config_file"
    echo "📋 먼저 git pull을 실행해주세요."
    echo "📁 현재 temp_configs 폴더 내용:"
    ls -la temp_configs/ 2>/dev/null || echo "temp_configs 폴더가 없습니다."
fi
