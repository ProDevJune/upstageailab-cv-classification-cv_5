#!/bin/bash
# Ubuntu 환경에서의 자동 설정 가이드

echo "🐧 Ubuntu 환경 자동 설정 시작..."
echo "================================"

# 현재 환경 정보
echo "📊 시스템 정보:"
echo "  OS: $(uname -s)"
echo "  아키텍처: $(uname -m)"
echo "  배포판: $(lsb_release -d 2>/dev/null | cut -f2 || echo 'Unknown')"

# Python 버전 확인
if command -v python3.11 &> /dev/null; then
    echo "  Python 3.11: ✅ $(python3.11 --version)"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  Python: $PYTHON_VERSION"
    
    # Python 3.11 설치 권장
    if [[ "$PYTHON_VERSION" != *"3.11"* ]]; then
        echo ""
        echo "🔧 Python 3.11 설치 권장:"
        echo "   sudo apt update"
        echo "   sudo apt install python3.11 python3.11-venv python3.11-dev"
        echo ""
        echo "   설치 후 다시 이 스크립트를 실행하세요."
        echo ""
        read -p "계속 진행하시겠습니까? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    echo "  Python: ❌ 설치되지 않음"
    echo ""
    echo "🔧 Python 설치 필요:"
    echo "   sudo apt update"
    echo "   sudo apt install python3.11 python3.11-venv python3.11-dev"
    exit 1
fi

# GPU 확인
echo ""
echo "🖥️  GPU 환경 확인:"
if command -v nvidia-smi &> /dev/null; then
    echo "  NVIDIA GPU: ✅"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    GPU_ENV="cuda"
else
    echo "  NVIDIA GPU: ❌ (CPU 모드로 설정됨)"
    GPU_ENV="cpu"
fi

echo ""
echo "🚀 자동 환경 설정 실행..."
echo ""

# 메인 설정 스크립트 실행
if [ -f "setup_and_validate_all.sh" ]; then
    chmod +x setup_and_validate_all.sh
    chmod +x setup_platform_env.sh
    chmod +x *.sh
    
    echo "📦 전체 설정 및 검증 실행 중..."
    ./setup_and_validate_all.sh
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Ubuntu 환경 설정 완료!"
        echo ""
        echo "✅ 설정 완료 항목:"
        echo "  • Python 가상환경 생성"
        echo "  • $GPU_ENV 환경에 맞는 PyTorch 설치"
        echo "  • 모든 필수 패키지 설치"
        echo "  • 환경 호환성 검증"
        echo ""
        echo "🚀 다음 단계:"
        echo "  1. 실험 생성: python experiments/experiment_generator.py --ocr-mode selective"
        echo "  2. 실험 실행: python experiments/auto_experiment_runner.py"
        echo "  3. 모니터링: python experiments/experiment_monitor.py"
        echo ""
        
        if [[ "$GPU_ENV" == "cuda" ]]; then
            echo "🔥 CUDA 최적화 팁:"
            echo "  • nvidia-smi로 GPU 사용률 모니터링"
            echo "  • 배치 크기가 GPU 메모리에 맞게 자동 조정됨"
            echo "  • Mixed Precision 자동 활성화"
        else
            echo "🖥️  CPU 최적화 팁:"
            echo "  • 멀티코어 활용을 위한 워커 수 자동 조정"
            echo "  • 메모리 사용량 최적화"
        fi
        
    else
        echo ""
        echo "❌ 환경 설정 중 오류 발생"
        echo ""
        echo "🔧 수동 해결 방법:"
        echo "  1. 가상환경 수동 생성:"
        echo "     python3.11 -m venv venv"
        echo "     source venv/bin/activate"
        echo ""
        echo "  2. 패키지 수동 설치:"
        if [[ "$GPU_ENV" == "cuda" ]]; then
            echo "     pip install -r requirements_ubuntu.txt"
        else
            echo "     pip install -r requirements_cpu.txt"
        fi
        echo ""
        echo "  3. 검증 재실행:"
        echo "     python pre_experiment_validator.py"
        
        exit 1
    fi
else
    echo "❌ setup_and_validate_all.sh 파일을 찾을 수 없습니다"
    echo "   압축 해제가 올바르게 되었는지 확인하세요"
    exit 1
fi

echo ""
echo "📋 Ubuntu 환경 설정 요약:"
echo "========================"
echo "  • 프로젝트 경로: $(pwd)"
echo "  • Python 버전: $(python --version 2>/dev/null || echo 'venv 미활성화')"
echo "  • 환경: $GPU_ENV"
echo "  • 가상환경: $(echo $VIRTUAL_ENV | grep -o '[^/]*$' || echo '미활성화')"
echo ""
echo "💾 로그 파일 확인:"
echo "  • 검증 결과: pre_experiment_validation_*.json"
echo "  • 플랫폼 정보: 스크립트 출력 로그"
echo ""
echo "🎉 Ubuntu 이전 및 설정 완료!"
