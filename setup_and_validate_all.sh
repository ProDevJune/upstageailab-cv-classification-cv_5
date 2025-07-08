#!/bin/bash

# 마스터 설치 및 검증 스크립트
# Mac OS (MPS) / Ubuntu (CUDA) 환경 자동 감지, 설치, 검증을 한 번에 실행

set -e  # 에러 발생시 스크립트 중단

# 동적으로 프로젝트 루트 감지
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_DIR="$PROJECT_ROOT"

echo "🚀 자동 실험 시스템 완전 설치 및 검증 시작"
echo "=" $(printf '=%.0s' {1..60})
echo "프로젝트 경로: $PROJECT_ROOT"
echo "스크립트 경로: $SCRIPT_DIR"

# 현재 디렉토리를 프로젝트 루트로 변경
cd "$PROJECT_ROOT"

# 1. 플랫폼 감지
OS=$(uname -s)
ARCH=$(uname -m)

echo ""
echo "🖥️  플랫폼 감지"
echo "OS: $OS"
echo "Architecture: $ARCH"

case "$OS" in
    "Darwin")
        if [[ "$ARCH" == "arm64" ]]; then
            PLATFORM="macos_apple_silicon"
            echo "✅ Apple Silicon Mac (MPS 지원) 감지"
        else
            PLATFORM="macos_intel"
            echo "✅ Intel Mac 감지"
        fi
        ;;
    "Linux")
        if command -v nvidia-smi &> /dev/null; then
            PLATFORM="ubuntu_cuda"
            echo "✅ Ubuntu + NVIDIA GPU (CUDA 지원) 감지"
            nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
        else
            PLATFORM="ubuntu_cpu"
            echo "✅ Ubuntu CPU 환경 감지"
        fi
        ;;
    *)
        PLATFORM="unknown"
        echo "⚠️  알 수 없는 플랫폼 - CPU 모드로 진행"
        ;;
esac

echo ""
echo "📦 단계 1: Python 호팩성 체크 및 플랫폼별 가상환경 설정"
echo "-" $(printf -- '-%.0s' {1..60})

# Python 호팩성 체크 실행
if [ -f "check_python_compatibility.sh" ]; then
    chmod +x check_python_compatibility.sh
    bash check_python_compatibility.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Python 호팩성 체크 실패"
        exit 1
    fi
else
    echo "⚠️  check_python_compatibility.sh 파일을 찾을 수 없습니다"
fi

echo ""
echo "🔧 플랫폼별 가상환경 설정"

# 가상환경 설정 스크립트 실행
if [ -f "setup_platform_env.sh" ]; then
    chmod +x setup_platform_env.sh
    bash setup_platform_env.sh
    
    if [ $? -eq 0 ]; then
        echo "✅ 가상환경 설정 완료"
    else
        echo "❌ 가상환경 설정 실패 - Python 3.13 복구 시도"
        
        # Python 3.13 복구 시도
        if [ -f "fix_python313_packages.sh" ]; then
            chmod +x fix_python313_packages.sh
            echo "🔧 Python 3.13 자동 복구 시작..."
            bash fix_python313_packages.sh
            
            if [ $? -eq 0 ]; then
                echo "✅ Python 3.13 복구 성공"
            else
                echo "❌ Python 3.13 복구 실패"
                echo ""
                echo "🔧 최종 추천 해결 방법:"
                echo "   1. Python 3.11 사용:"
                echo "      brew install python@3.11"
                echo "      rm -rf venv"
                echo "      /opt/homebrew/bin/python3.11 -m venv venv"
                echo "      source venv/bin/activate"
                echo "      pip install -r requirements_macos.txt"
                echo ""
                echo "   2. 또는 수동 패키지 설치:"
                echo "      source venv/bin/activate"
                echo "      pip install torch torchvision torchaudio"
                echo "      pip install timm transformers opencv-python"
                exit 1
            fi
        else
            echo "❌ fix_python313_packages.sh 파일을 찾을 수 없습니다"
            exit 1
        fi
    fi
else
    echo "❌ setup_platform_env.sh 파일을 찾을 수 없습니다"
    exit 1
fi

echo ""
echo "🔍 단계 2: 빠른 사전 검증"
echo "-" $(printf -- '-%.0s' {1..40})

# 가상환경 활성화
source venv/bin/activate

# 빠른 검증 실행
python pre_experiment_validator.py --quick-test

if [ $? -eq 0 ]; then
    echo "✅ 빠른 검증 성공"
else
    echo "❌ 빠른 검증 실패 - 환경 문제 발생"
    exit 1
fi

echo ""
echo "🧪 단계 3: 종합 실험 검증"
echo "-" $(printf -- '-%.0s' {1..40})

# 종합 검증 실행
python pre_experiment_validator.py --save-report

VALIDATION_EXIT_CODE=$?

echo ""
echo "📊 단계 4: 검증 결과 분석"
echo "-" $(printf -- '-%.0s' {1..40})

if [ $VALIDATION_EXIT_CODE -eq 0 ]; then
    echo "🎉 모든 검증 완료!"
    echo ""
    echo "✅ 환경 설정: 완료"
    echo "✅ 패키지 설치: 완료"  
    echo "✅ 디바이스 호환성: 완료"
    echo "✅ 모델 검증: 완료"
    echo "✅ 실험 조합 테스트: 완료"
    echo ""
    
    echo "🚀 이제 자동 실험을 안전하게 시작할 수 있습니다!"
    echo ""
    echo "📋 다음 단계:"
    echo "1. 실험 생성:"
    echo "   python experiments/experiment_generator.py --ocr-mode selective"
    echo ""
    echo "2. 실험 실행 (백그라운드):"
    echo "   python experiments/auto_experiment_runner.py &"
    echo ""
    echo "3. 실시간 모니터링 (별도 터미널):"
    echo "   python experiments/experiment_monitor.py"
    echo ""
    echo "4. 제출 관리:"
    echo "   python experiments/submission_manager.py list-pending"
    echo ""
    
    # 플랫폼별 추가 안내
    case "$PLATFORM" in
        "macos_apple_silicon")
            echo "🍎 Apple Silicon 최적화 팁:"
            echo "   - 배치 크기가 자동으로 MPS에 최적화됨"
            echo "   - 통합 메모리 사용량을 모니터링하세요"
            echo "   - Activity Monitor에서 메모리 압박 상태 확인"
            ;;
        "ubuntu_cuda")
            echo "🐧 CUDA 최적화 팁:"
            echo "   - nvidia-smi로 GPU 사용률 모니터링"
            echo "   - Mixed Precision 활성화로 메모리 효율성 증대"
            echo "   - 다중 GPU가 있다면 병렬 실험 고려"
            ;;
    esac
    
else
    echo "⚠️  검증에서 일부 문제 발견"
    echo ""
    echo "❌ 환경에 문제가 있을 수 있습니다."
    echo ""
    echo "🔧 문제 해결 방법:"
    echo "1. 상세 로그 확인:"
    echo "   검증 리포트 JSON 파일을 확인하세요"
    echo ""
    echo "2. 환경 재설정:"
    echo "   rm -rf venv"
    echo "   bash setup_platform_env.sh"
    echo ""
    echo "3. 수동 패키지 설치:"
    case "$PLATFORM" in
        "macos_apple_silicon")
            echo "   pip install -r requirements_macos.txt"
            ;;
        "ubuntu_cuda")
            echo "   pip install -r requirements_ubuntu.txt"
            ;;
        *)
            echo "   pip install -r requirements_cpu.txt"
            ;;
    esac
    echo ""
    echo "4. 다시 검증:"
    echo "   python pre_experiment_validator.py"
    
    exit 1
fi

echo ""
echo "💾 검증 완료 - 로그 파일을 확인하세요"
echo "📊 플랫폼 정보는 platform_info.json에 저장됨"
echo "📋 검증 결과는 pre_experiment_validation_*.json에 저장됨"

echo ""
echo "🎉 자동 실험 시스템 설치 및 검증 완료!"
