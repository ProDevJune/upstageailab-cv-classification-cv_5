#!/bin/bash

# V2_1 & V2_2 선택적 실행 스크립트
# 다양한 방식으로 실험을 선택해서 실행할 수 있는 인터페이스

echo "🎯 V2_1 & V2_2 Selective Experiment Runner"
echo "=========================================="

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 도움말 함수
show_help() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "📋 실험 타입별 실행:"
    echo "  $0 --type v2_1              # V2_1 실험만 실행"
    echo "  $0 --type v2_2              # V2_2 실험만 실행"
    echo "  $0 --type cv                # 교차검증 실험만 실행"
    echo ""
    echo "🔧 모델별 실행:"
    echo "  $0 --model convnextv2       # ConvNeXt 모델만"
    echo "  $0 --model resnet50         # ResNet50 모델만"
    echo "  $0 --model efficientnet     # EfficientNet 모델만"
    echo ""
    echo "⚡ 기법별 실행:"
    echo "  $0 --technique mixup        # Mixup 기법만"
    echo "  $0 --technique cutmix       # CutMix 기법만"
    echo "  $0 --technique focal        # FocalLoss 기법만"
    echo "  $0 --technique 2stage       # 2-stage 학습만"
    echo ""
    echo "📊 단계별 실행:"
    echo "  $0 --phase phase1           # 1단계 (기본 성능 확인)"
    echo "  $0 --phase phase2           # 2단계 (모델 비교)"
    echo "  $0 --phase phase3           # 3단계 (하이퍼파라미터 최적화)"
    echo "  $0 --phase phase4           # 4단계 (고급 기법)"
    echo ""
    echo "🎮 조합 실행:"
    echo "  $0 --type v2_1 --model convnextv2 --limit 5    # V2_1 ConvNeXt 5개만"
    echo "  $0 --type v2_2 --technique mixup --phase phase1 # V2_2 Mixup 1단계"
    echo ""
    echo "🔍 미리보기:"
    echo "  $0 --dry-run --type v2_1    # V2_1 실험 목록만 확인"
    echo ""
    echo "🚀 빠른 실행:"
    echo "  $0 --quick                  # 가장 중요한 3개 실험만 실행"
    echo "  $0 --best                   # 베스트 성능 예상 실험들만 실행"
}

# 빠른 실행 모드
run_quick() {
    echo "🚀 Quick Mode: 가장 중요한 3개 실험만 실행"
    python v2_experiment_generator.py --phase phase1 --limit 3
    ./v2_experiments/run_all_experiments.sh
}

# 베스트 실행 모드
run_best() {
    echo "🏆 Best Mode: 베스트 성능 예상 실험들 실행"
    python v2_experiment_generator.py --type v2_1 --model convnextv2 --limit 5
    ./v2_experiments/run_all_experiments.sh
}

# 인터랙티브 모드
run_interactive() {
    echo "🎮 Interactive Mode: 실험 선택"
    echo ""
    echo "어떤 실험을 실행하시겠습니까?"
    echo "1) V2_1 전체 실험"
    echo "2) V2_2 전체 실험"
    echo "3) V2_1 + V2_2 ConvNeXt 모델만"
    echo "4) V2_2 Mixup/CutMix 기법만"
    echo "5) 1단계 기본 성능 확인"
    echo "6) 커스텀 선택"
    echo "7) 종료"
    echo ""
    
    read -p "선택하세요 (1-7): " choice
    
    case $choice in
        1)
            echo "✅ V2_1 전체 실험 실행"
            python v2_experiment_generator.py --type v2_1
            ;;
        2)
            echo "✅ V2_2 전체 실험 실행"
            python v2_experiment_generator.py --type v2_2
            ;;
        3)
            echo "✅ ConvNeXt 모델만 실행"
            python v2_experiment_generator.py --model convnextv2
            ;;
        4)
            echo "✅ Mixup/CutMix 기법만 실행"
            python v2_experiment_generator.py --technique mixup
            python v2_experiment_generator.py --technique cutmix
            ;;
        5)
            echo "✅ 1단계 기본 성능 확인"
            python v2_experiment_generator.py --phase phase1
            ;;
        6)
            echo "커스텀 선택 모드"
            read -p "실험 타입 (v2_1/v2_2/cv/all): " exp_type
            read -p "모델 필터 (선택사항): " model_filter
            read -p "기법 필터 (선택사항): " technique_filter
            read -p "최대 실험 수 (선택사항): " limit
            
            cmd="python v2_experiment_generator.py --type $exp_type"
            [ ! -z "$model_filter" ] && cmd="$cmd --model $model_filter"
            [ ! -z "$technique_filter" ] && cmd="$cmd --technique $technique_filter"
            [ ! -z "$limit" ] && cmd="$cmd --limit $limit"
            
            echo "실행 명령: $cmd"
            eval $cmd
            ;;
        7)
            echo "종료합니다."
            exit 0
            ;;
        *)
            echo "잘못된 선택입니다."
            run_interactive
            ;;
    esac
    
    echo ""
    read -p "생성된 실험을 바로 실행하시겠습니까? (y/n): " run_now
    if [[ $run_now == "y" || $run_now == "Y" ]]; then
        ./v2_experiments/run_all_experiments.sh
    fi
}

# 명령행 인자 처리
ARGS=""
DRY_RUN=false
QUICK=false
BEST=false
INTERACTIVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --best)
            BEST=true
            shift
            ;;
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            ARGS="$ARGS --dry-run"
            shift
            ;;
        --type)
            ARGS="$ARGS --type $2"
            shift 2
            ;;
        --model)
            ARGS="$ARGS --model $2"
            shift 2
            ;;
        --technique)
            ARGS="$ARGS --technique $2"
            shift 2
            ;;
        --phase)
            ARGS="$ARGS --phase $2"
            shift 2
            ;;
        --limit)
            ARGS="$ARGS --limit $2"
            shift 2
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 실행 모드 선택
if [[ $QUICK == true ]]; then
    run_quick
elif [[ $BEST == true ]]; then
    run_best
elif [[ $INTERACTIVE == true ]]; then
    run_interactive
elif [[ -n "$ARGS" ]]; then
    echo "🔬 실험 생성 중..."
    python v2_experiment_generator.py $ARGS
    
    if [[ $DRY_RUN == false ]]; then
        echo ""
        read -p "생성된 실험을 바로 실행하시겠습니까? (y/n): " run_now
        if [[ $run_now == "y" || $run_now == "Y" ]]; then
            ./v2_experiments/run_all_experiments.sh
        else
            echo "실행하려면: ./v2_experiments/run_all_experiments.sh"
        fi
    fi
else
    echo "옵션이 지정되지 않았습니다. 인터랙티브 모드로 실행합니다."
    echo ""
    run_interactive
fi
