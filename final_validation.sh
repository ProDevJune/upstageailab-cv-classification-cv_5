#!/bin/bash
# 최종 검증 실행 스크립트

echo "🎯 최종 사전 검증 실행..."

cd 

# 가상환경 활성화
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

echo "🐍 Python 버전: $(python --version)"
echo "📁 가상환경: $VIRTUAL_ENV"

echo ""
echo "🧪 Swin Transformer 이미지 크기 수정 후 최종 검증..."
python pre_experiment_validator.py

echo ""
echo "✅ 검증 완료!"
echo ""
echo "🚀 다음 단계 (검증 성공시):"
echo "   1. python experiments/experiment_generator.py --ocr-mode selective"
echo "   2. python experiments/auto_experiment_runner.py"
echo "   3. python experiments/experiment_monitor.py"
