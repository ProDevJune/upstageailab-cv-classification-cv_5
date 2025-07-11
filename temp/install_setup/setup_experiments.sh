#!/bin/bash

# 모든 Python 스크립트를 실행 가능하게 만들기
echo "🔧 자동 실험 시스템 파일 권한 설정 중..."

# 현재 디렉토리 확인
if [ ! -d "experiments" ]; then
    echo "❌ experiments 디렉토리를 찾을 수 없습니다."
    echo "   프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Python 스크립트들을 실행 가능하게 만들기
chmod +x experiments/experiment_generator.py
chmod +x experiments/auto_experiment_runner.py
chmod +x experiments/submission_manager.py
chmod +x experiments/results_analyzer.py
chmod +x experiments/experiment_monitor.py

echo "✅ 파일 권한 설정 완료!"
echo ""
echo "🎯 사용 가능한 명령어들:"
echo "  1. 실험 매트릭스 생성: python experiments/experiment_generator.py"
echo "  2. 자동 실험 시작:   python experiments/auto_experiment_runner.py"
echo "  3. 제출 관리:        python experiments/submission_manager.py list-pending"
echo "  4. 결과 분석:        python experiments/results_analyzer.py --generate-report"
echo "  5. 실시간 모니터링:   python experiments/experiment_monitor.py"
echo ""
echo "🚀 시작하려면: python experiments/experiment_generator.py"
