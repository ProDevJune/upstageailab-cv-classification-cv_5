#!/bin/bash

# 첫 번째 실험이 0분 0초로 끝나는 문제 디버깅 스크립트
echo "🔍 V2 실험 문제 디버깅"
echo "====================="

# 1. 환경 확인
echo "📋 1. 환경 확인"
echo "현재 위치: $(pwd)"
echo "Python 경로: $(which python)"
echo "가상환경: ${VIRTUAL_ENV:-'None'}"
echo ""

# 2. 데이터 파일 확인
echo "📊 2. 데이터 파일 확인"
if [ -f "data/train.csv" ]; then
    echo "  ✅ data/train.csv"
    echo "     크기: $(wc -l < data/train.csv) 줄"
else
    echo "  ❌ data/train.csv 없음"
fi

if [ -d "data/train" ]; then
    echo "  ✅ data/train/ 디렉토리"
    echo "     파일 수: $(find data/train -name "*.jpg" -o -name "*.png" | wc -l)개"
else
    echo "  ❌ data/train/ 디렉토리 없음"
fi
echo ""

# 3. 실험 설정 파일 확인
echo "📁 3. 실험 설정 파일 확인"
CONFIG_COUNT=$(find v2_experiments/configs -name "*.yaml" | wc -l)
echo "설정 파일 수: ${CONFIG_COUNT}개"
if [ $CONFIG_COUNT -gt 0 ]; then
    echo "설정 파일들:"
    find v2_experiments/configs -name "*.yaml" | head -5 | sed 's/^/  /'
fi
echo ""

# 4. 메인 스크립트 확인
echo "🐍 4. 메인 스크립트 확인"
if [ -f "codes/gemini_main_v2_1_style.py" ]; then
    echo "  ✅ codes/gemini_main_v2_1_style.py"
elif [ -f "codes/gemini_main.py" ]; then
    echo "  ✅ codes/gemini_main.py"
else
    echo "  ❌ 메인 스크립트 없음"
    echo "  사용 가능한 Python 파일들:"
    ls -la codes/gemini_main*.py 2>/dev/null | sed 's/^/    /'
fi
echo ""

# 5. 라이브러리 확인
echo "📚 5. Python 라이브러리 확인"
python -c "
libraries = ['torch', 'torchvision', 'timm', 'pandas', 'numpy', 'yaml']
for lib in libraries:
    try:
        __import__(lib)
        print(f'  ✅ {lib}')
    except ImportError as e:
        print(f'  ❌ {lib}: {e}')
"
echo ""

# 6. 로그 파일 확인
echo "📋 6. 최근 로그 파일 확인"
if [ -d "v2_experiments/logs" ]; then
    LATEST_LOG=$(ls -t v2_experiments/logs/*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "최신 로그: $LATEST_LOG"
        echo "마지막 20줄:"
        tail -20 "$LATEST_LOG" | sed 's/^/  /'
    else
        echo "로그 파일 없음"
    fi
else
    echo "로그 디렉토리 없음"
fi

echo ""
echo "✅ 디버깅 완료!"
