#!/bin/bash

# 첫 번째 실험이 0분 0초로 끝나는 문제 디버깅 스크립트
echo "🔍 V2_2 FocalLoss 실험 문제 디버깅"
echo "=================================="

# 1. 환경 확인
echo "📋 1. 환경 확인"
echo "현재 위치: $(pwd)"
echo "Python 경로: $(which python)"
echo "가상환경: ${VIRTUAL_ENV:-'None'}"
echo ""

# 2. 필요한 파일들 확인
echo "📁 2. 필요한 파일들 확인"
echo "설정 파일:"
if [ -f "v2_experiments/configs/v2_2_resnet50_focal_auto.yaml" ]; then
    echo "  ✅ v2_experiments/configs/v2_2_resnet50_focal_auto.yaml"
    echo "  첫 10줄:"
    head -10 "v2_experiments/configs/v2_2_resnet50_focal_auto.yaml" | sed 's/^/    /'
else
    echo "  ❌ v2_experiments/configs/v2_2_resnet50_focal_auto.yaml 없음"
fi
echo ""

echo "메인 스크립트:"
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

# 3. 데이터 파일 확인
echo "📊 3. 데이터 파일 확인"
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

# 4. Python 라이브러리 확인
echo "🐍 4. Python 라이브러리 확인"
python -c "
import sys
print(f'Python 버전: {sys.version}')

libraries = ['torch', 'torchvision', 'timm', 'albumentations', 'pandas', 'numpy', 'yaml']
for lib in libraries:
    try:
        __import__(lib)
        print(f'  ✅ {lib}')
    except ImportError as e:
        print(f'  ❌ {lib}: {e}')
"
echo ""

# 5. 직접 실험 실행 테스트
echo "🧪 5. 직접 실험 실행 테스트"
CONFIG_FILE="v2_experiments/configs/v2_2_resnet50_focal_auto.yaml"
MAIN_SCRIPT=""

if [ -f "codes/gemini_main_v2_1_style.py" ]; then
    MAIN_SCRIPT="codes/gemini_main_v2_1_style.py"
elif [ -f "codes/gemini_main.py" ]; then
    MAIN_SCRIPT="codes/gemini_main.py"
else
    echo "❌ 실행할 메인 스크립트가 없습니다!"
    exit 1
fi

echo "사용할 스크립트: $MAIN_SCRIPT"
echo "설정 파일: $CONFIG_FILE"
echo ""

# 간단한 syntax 체크
echo "📝 Python 스크립트 syntax 체크:"
if python -m py_compile "$MAIN_SCRIPT"; then
    echo "  ✅ Syntax 정상"
else
    echo "  ❌ Syntax 오류"
    exit 1
fi
echo ""

# 설정 파일 파싱 테스트
echo "📝 설정 파일 파싱 테스트:"
python -c "
import yaml
try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    print('  ✅ YAML 파싱 성공')
    print(f'  실험 이름: {config.get(\"experiment_name\", \"Unknown\")}')
    print(f'  모델: {config.get(\"model_name\", \"Unknown\")}')
    print(f'  에포크: {config.get(\"epochs\", \"Unknown\")}')
except Exception as e:
    print(f'  ❌ YAML 파싱 실패: {e}')
"
echo ""

# 실제 실행 (dry-run 형태)
echo "🚀 6. 실제 실행 테스트 (첫 몇 초만)"
echo "실행 명령어: timeout 10s python $MAIN_SCRIPT --config $CONFIG_FILE"
echo "시작 시간: $(date)"

timeout 10s python "$MAIN_SCRIPT" --config "$CONFIG_FILE" 2>&1 | head -20

echo ""
echo "종료 시간: $(date)"
echo ""

echo "✅ 디버깅 완료!"
echo "위 결과를 확인하여 문제점을 파악하세요."
