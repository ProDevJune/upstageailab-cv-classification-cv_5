#!/bin/bash

# 확장 가능한 하이퍼파라미터 실험 시스템 전체 검증 스크립트
# Mac/Ubuntu 환경 자동 인식 및 모든 요구사항 검증

echo "🔍 확장 가능한 하이퍼파라미터 실험 시스템 전체 검증"
echo "=========================================="

# 현재 디렉토리 확인
if [ ! -f "validate_experiment_system.py" ]; then
    echo "❌ 프로젝트 루트에서 실행해주세요."
    exit 1
fi

echo "📍 프로젝트 루트: $(pwd)"

# PYTHONPATH에 프로젝트 루트 추가
export PYTHONPATH="$(pwd):$PYTHONPATH"
echo "🔧 PYTHONPATH 설정: $PYTHONPATH"

# Python 실행 가능 확인
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python이 설치되지 않았습니다."
    exit 1
fi

# Python 명령어 결정 - 가상환경 우선 사용
# 가상환경이 활성화된 경우 가상환경의 python을 사용
if [[ "$VIRTUAL_ENV" != "" ]] && command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "🐍 Python 명령어: $PYTHON_CMD"

# 1단계: 전체 시스템 검증
echo ""
echo "1️⃣ 전체 시스템 검증 실행"
echo "----------------------------------------"

$PYTHON_CMD validate_experiment_system.py

VALIDATION_RESULT=$?

if [ $VALIDATION_RESULT -eq 0 ]; then
    echo ""
    echo "✅ 시스템 검증 통과!"
    
    # 2단계: 빠른 테스트 실험 (선택사항)
    echo ""
    echo "2️⃣ 빠른 테스트 실험 실행 (선택사항)"
    echo "----------------------------------------"
    echo "ℹ️ 실제 긴 실험 전에 빠른 테스트로 모든 컴포넌트 동작 확인"
    echo "⏱️ 5-10분 소요됩니다."
    
    read -p "빠른 테스트 실험을 실행하시겠습니까? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🧪 빠른 테스트 실험 시작..."
        
        $PYTHON_CMD quick_test_experiments.py
        
        TEST_RESULT=$?
        
        if [ $TEST_RESULT -eq 0 ]; then
            echo ""
            echo "🎊 모든 검증 완료! 실제 실험 실행 준비됨"
            echo ""
            echo "🚀 실제 실험 실행 방법:"
            echo "   $PYTHON_CMD hyperparameter_system/run_experiments.py"
            echo ""
            echo "📊 명령줄 실행 예시:"
            echo "   # 실험 매트릭스 확인"
            echo "   $PYTHON_CMD hyperparameter_system/experiment_runner.py --matrix"
            echo ""
            echo "   # 특정 모델만 실험"
            echo "   $PYTHON_CMD hyperparameter_system/experiment_runner.py --models efficientnet_b4.ra2_in1k"
            echo ""
            echo "   # 특정 카테고리만 실험"
            echo "   $PYTHON_CMD hyperparameter_system/experiment_runner.py --categories optimizer loss_function"
            echo ""
            echo "🔍 실험 모니터링 (장시간 실행 시 권장):"
            echo "   $PYTHON_CMD experiment_monitor.py"
            echo ""
            exit 0
        else
            echo ""
            echo "❌ 빠른 테스트 실패. 문제 해결 후 재시도하세요."
            exit 1
        fi
    else
        echo ""
        echo "⏭️ 빠른 테스트 생략. 시스템 검증만 완료됨."
        echo ""
        echo "🚀 실제 실험 실행 방법:"
        echo "   $PYTHON_CMD hyperparameter_system/run_experiments.py"
        echo ""
        echo "💡 권장 사항:"
        echo "   1. 먼저 빠른 테스트: $PYTHON_CMD quick_test_experiments.py"
        echo "   2. 실험 모니터링: $PYTHON_CMD experiment_monitor.py"
        exit 0
    fi
    
else
    echo ""
    echo "❌ 시스템 검증 실패. 다음을 확인하세요:"
    echo ""
    echo "📋 해결 방법:"
    echo "1. 누락된 패키지 설치:"
    echo "   pip install torch torchvision timm albumentations opencv-python"
    echo "   pip install pandas numpy scikit-learn matplotlib seaborn tqdm wandb"
    echo "   pip install PyYAML Pillow psutil"
    echo ""
    echo "2. 필요한 파일 확인:"
    echo "   - codes/gemini_main_v2.py"
    echo "   - codes/config_v2.yaml" 
    echo "   - data/train.csv (또는 train0705a.csv)"
    echo "   - data/train/ (훈련 이미지 디렉토리)"
    echo "   - data/test/ (테스트 이미지 디렉토리)"
    echo ""
    echo "3. 권한 설정:"
    echo "   chmod +x setup_hyperparameter_system.sh"
    echo "   ./setup_hyperparameter_system.sh"
    echo ""
    echo "📄 상세 결과: validation_report.yaml 파일 확인"
    echo ""
    exit 1
fi
