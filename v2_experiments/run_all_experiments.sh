#!/bin/bash

# V2_1 & V2_2 자동 실험 실행 스크립트
# 총 0개 실험 자동 실행

echo "🚀 Starting V2_1 & V2_2 Automatic Experiments"
echo "Total experiments: 0"
echo "======================================================"

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 실험 결과 디렉토리 생성
mkdir -p v2_experiments/results

# 실험 로그 파일
LOG_FILE="v2_experiments/logs/experiment_run_$(date +%Y%m%d_%H%M%S).log"
echo "📝 Logging to: $LOG_FILE"


echo ""
echo "🎉 All experiments completed!"
echo "Check the results in data/submissions/"
echo "Check the logs in v2_experiments/logs/"
