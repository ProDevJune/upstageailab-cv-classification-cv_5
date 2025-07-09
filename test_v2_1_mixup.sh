#!/bin/bash

# 🔥 V2_1 Mixup/CutMix 대회 긴급 테스트 스크립트
# 내일 저녁 7시 마감 - 24시간 남음!

echo "🚨 V2_1 Mixup/CutMix 긴급 테스트 시작!"
echo "대회 마감: 내일 저녁 7시"
echo "======================================="

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 현재 시간 기록
echo "⏰ 시작 시간: $(date)"

echo ""
echo "🎯 실험 계획:"
echo "1. Mixup (1-2시간) - 가장 검증된 방법"
echo "2. CutMix (1-2시간) - 보조 방법"  
echo "3. Baseline (1-2시간) - 비교군"
echo ""

read -p "어떤 실험을 실행하시겠습니까? (1: Mixup, 2: CutMix, 3: Baseline, 4: 모두): " choice

case $choice in
    1)
        echo "🔥 Mixup 실험 시작!"
        python codes/gemini_main_v2_1_style.py --config codes/mixup_configs/config_v2_1_mixup.yaml
        ;;
    2)
        echo "🔥 CutMix 실험 시작!"
        python codes/gemini_main_v2_1_style.py --config codes/mixup_configs/config_v2_1_cutmix.yaml
        ;;
    3)
        echo "🔥 Baseline 실험 시작!"
        python codes/gemini_main_v2_1_style.py --config codes/mixup_configs/config_v2_1_baseline.yaml
        ;;
    4)
        echo "🔥 모든 실험 병렬 실행!"
        echo "터미널 1: Mixup"
        echo "터미널 2: CutMix"  
        echo "터미널 3: Baseline"
        echo ""
        echo "다음 명령들을 각각 다른 터미널에서 실행하세요:"
        echo ""
        echo "# 터미널 1 (Mixup - 우선순위 1)"
        echo "python codes/gemini_main_v2_1_style.py --config codes/mixup_configs/config_v2_1_mixup.yaml"
        echo ""
        echo "# 터미널 2 (CutMix - 우선순위 2)"  
        echo "python codes/gemini_main_v2_1_style.py --config codes/mixup_configs/config_v2_1_cutmix.yaml"
        echo ""
        echo "# 터미널 3 (Baseline - 비교용)"
        echo "python codes/gemini_main_v2_1_style.py --config codes/mixup_configs/config_v2_1_baseline.yaml"
        echo ""
        echo "🎯 추천: Mixup부터 시작하세요!"
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        echo "대회 시간이 부족합니다. 빠르게 결정하세요!"
        exit 1
        ;;
esac

echo ""
echo "🏆 성공을 기원합니다!"
echo "⏰ 마감까지 시간을 확인하세요: $(date)"
