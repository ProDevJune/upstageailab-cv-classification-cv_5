#!/bin/bash

# V2_2 전용 실험 실행 스크립트
# "효율적 + 기법 조합" 전략에 특화

echo "⚡ V2_2 Experiment Runner - Efficient + Advanced Techniques"
echo "==========================================================="

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# V2_2 실험만 생성
echo "📊 Generating V2_2 experiments..."
python v2_experiment_generator.py --type v2_2

# 생성된 실험 수 확인
exp_count=$(find v2_experiments/configs -name "v2_2_*.yaml" | wc -l)
echo "📈 Generated $exp_count V2_2 experiments"

# 기법별 실험 수 표시
echo ""
echo "📊 V2_2 Experiments by Technique:"
echo "  - Mixup: $(find v2_experiments/configs -name "*mixup*" | wc -l)"
echo "  - CutMix: $(find v2_experiments/configs -name "*cutmix*" | wc -l)"
echo "  - FocalLoss: $(find v2_experiments/configs -name "*focal*" | wc -l)"
echo "  - 2-Stage: $(find v2_experiments/configs -name "*two_stage*" | wc -l)"
echo "  - Dynamic Aug: $(find v2_experiments/configs -name "*dynamic*" | wc -l)"

echo ""
echo "⚡ V2_2 특징:"
echo "  - 효율적 모델 (ResNet50, EfficientNet-B4)"
echo "  - 고급 증강 기법 (Mixup, CutMix)"
echo "  - 클래스 불균형 해결 (FocalLoss)"
echo "  - 2-stage 학습 지원"
echo "  - 적당한 학습 시간 (최대 24시간/실험)"

echo ""
echo "🎯 추천 실행 순서:"
echo "1. 기본 성능 확인: python v2_experiment_generator.py --type v2_2 --phase phase1"
echo "2. 기법별 비교: python v2_experiment_generator.py --type v2_2 --technique mixup"
echo "3. 모델별 비교: python v2_experiment_generator.py --type v2_2 --model resnet50"

echo ""
read -p "어떤 방식으로 실행하시겠습니까? (1: 전체, 2: 기법별, 3: 모델별, 4: 취소): " choice

case $choice in
    1)
        echo "🚀 Starting all V2_2 experiments..."
        ./v2_experiments/run_all_experiments.sh
        ;;
    2)
        echo "기법 선택:"
        echo "1) Mixup"
        echo "2) CutMix"
        echo "3) FocalLoss"
        echo "4) 2-Stage"
        echo "5) Dynamic"
        read -p "선택하세요 (1-5): " tech_choice
        
        case $tech_choice in
            1) technique="mixup" ;;
            2) technique="cutmix" ;;
            3) technique="focal" ;;
            4) technique="2stage" ;;
            5) technique="dynamic" ;;
            *) echo "잘못된 선택"; exit 1 ;;
        esac
        
        echo "🔬 Generating V2_2 experiments with $technique..."
        python v2_experiment_generator.py --type v2_2 --technique $technique
        ./v2_experiments/run_all_experiments.sh
        ;;
    3)
        echo "모델 선택:"
        echo "1) ResNet50"
        echo "2) ResNet101"
        echo "3) EfficientNet-B4"
        read -p "선택하세요 (1-3): " model_choice
        
        case $model_choice in
            1) model="resnet50" ;;
            2) model="resnet101" ;;
            3) model="efficientnet_b4" ;;
            *) echo "잘못된 선택"; exit 1 ;;
        esac
        
        echo "🏗️ Generating V2_2 experiments with $model..."
        python v2_experiment_generator.py --type v2_2 --model $model
        ./v2_experiments/run_all_experiments.sh
        ;;
    4)
        echo "❌ 실행이 취소되었습니다."
        echo "개별 실험 실행: python codes/gemini_main_v2_enhanced.py --config v2_experiments/configs/v2_2_*.yaml"
        ;;
    *)
        echo "잘못된 선택입니다."
        exit 1
        ;;
esac
