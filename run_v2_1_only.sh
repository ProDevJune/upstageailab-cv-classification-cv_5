#!/bin/bash

# V2_1 전용 실험 실행 스크립트
# "대형 모델 + 장기 학습" 전략에 특화

echo "🏗️ V2_1 Experiment Runner - Large Model + Long Training"
echo "========================================================"

# 현재 디렉토리에서 실행 (경로 수정 불필요)
# cd 명령어 제거됨

# V2_1 실험만 생성
echo "📊 Generating V2_1 experiments..."
python v2_experiment_generator.py --type v2_1

# 생성된 실험 수 확인
exp_count=$(find v2_experiments/configs -name "v2_1_*.yaml" | wc -l)
echo "📈 Generated $exp_count V2_1 experiments"

# 모델별 실험 수 표시
echo ""
echo "📊 V2_1 Experiments by Model:"
echo "  - ConvNeXt-V2 Base: $(find v2_experiments/configs -name "*convnextv2_base*" | wc -l)"
echo "  - ConvNeXt-V2 Large: $(find v2_experiments/configs -name "*convnextv2_large*" | wc -l)"
echo "  - EfficientNet-V2 L: $(find v2_experiments/configs -name "*efficientnetv2_l*" | wc -l)"

echo ""
echo "⚠️  V2_1 특징:"
echo "  - 대형 모델 (ConvNeXt-V2, EfficientNet-V2)"
echo "  - 긴 학습 시간 (최대 48시간/실험)"
echo "  - 높은 GPU 메모리 요구사항"
echo "  - 최고 성능 추구"

# run_optimal_performance.sh에서 호출될 때는 자동으로 "y" 응답
if [ "$1" = "--auto" ]; then
    confirm="y"
    echo "🤖 자동 모드: V2_1 실험을 자동으로 시작합니다."
else
    echo ""
    read -p "V2_1 실험을 실행하시겠습니까? (y/n): " confirm
fi

if [[ $confirm == "y" || $confirm == "Y" ]]; then
    echo "🚀 Starting V2_1 experiments..."
    ./v2_experiments/run_all_experiments.sh
else
    echo "❌ 실행이 취소되었습니다."
    echo "개별 실험 실행: python codes/gemini_main_v2_1_style.py --config v2_experiments/configs/v2_1_*.yaml"
fi
