#!/bin/bash

# Python 3.13 호환성 체크 및 환경 설정 가이드

echo "🐍 Python 3.13 호환성 체크"
echo "=" $(printf '=%.0s' {1..50})

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo "현재 Python 버전: $PYTHON_VERSION"

if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 13 ]]; then
    echo ""
    echo "⚠️  Python 3.13 이상이 감지되었습니다."
    echo ""
    echo "🔧 Python 3.13 호환성 이슈 및 해결 방법:"
    echo ""
    echo "1. 일부 패키지가 Python 3.13을 완전히 지원하지 않을 수 있습니다:"
    echo "   - ray[tune]: 제한적 지원"
    echo "   - 일부 컴파일 필요 패키지들"
    echo ""
    echo "2. 권장 해결 방법:"
    echo "   A) Python 3.11 사용 (가장 안정적):"
    echo "      brew install python@3.11"
    echo "      /opt/homebrew/bin/python3.11 -m venv venv"
    echo ""
    echo "   B) Python 3.13 계속 사용 (실험적):"
    echo "      - 특별히 준비된 requirements_macos_py313.txt 사용"
    echo "      - 일부 기능 제한 가능"
    echo ""
    echo "3. 현재 설정으로 계속 진행하시겠습니까?"
    echo "   - 'y' 입력: Python 3.13으로 계속 진행"
    echo "   - 'n' 입력: 스크립트 종료 후 Python 3.11 설치 권장"
    echo ""
    read -p "계속 진행하시겠습니까? (y/n): " CONTINUE
    
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
        echo ""
        echo "🔧 Python 3.11 설치 방법:"
        echo "   brew install python@3.11"
        echo "   /opt/homebrew/bin/python3.11 -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements_macos.txt"
        echo ""
        echo "설치 후 다시 ./setup_and_validate_all.sh를 실행해주세요."
        exit 0
    else
        echo ""
        echo "✅ Python 3.13으로 계속 진행합니다."
        echo "   호환 버전 패키지들을 사용합니다."
    fi
    
elif [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
    echo "✅ Python $PYTHON_VERSION는 완전 지원됩니다."
    
else
    echo "❌ Python 3.8 이상이 필요합니다."
    echo "   현재: $PYTHON_VERSION"
    echo ""
    echo "🔧 Python 업그레이드:"
    echo "   brew install python@3.11"
    exit 1
fi

echo ""
echo "🚀 환경 설정을 계속 진행합니다..."
