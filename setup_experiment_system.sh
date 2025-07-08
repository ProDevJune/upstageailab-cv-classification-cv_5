#!/bin/bash

# 모든 Python 스크립트를 실행 가능하게 만들기
echo "🔧 자동 실험 시스템 파일 권한 설정 중..."

# 현재 디렉토리 확인
if [ ! -d "experiments" ]; then
    echo "❌ experiments 디렉토리를 찾을 수 없습니다."
    echo "   프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Python 스크립트들을 실행 가능하게 설정
chmod +x experiments/experiment_generator.py
chmod +x experiments/auto_experiment_runner.py
chmod +x experiments/submission_manager.py
chmod +x experiments/results_analyzer.py
chmod +x experiments/experiment_monitor.py

echo "✅ 파일 권한이 설정되었습니다:"
echo "   📁 experiments/experiment_generator.py"
echo "   📁 experiments/auto_experiment_runner.py"
echo "   📁 experiments/submission_manager.py"
echo "   📁 experiments/results_analyzer.py"
echo "   📁 experiments/experiment_monitor.py"
echo ""
echo "🚀 자동 실험 시스템이 준비되었습니다!"
echo ""
echo "📋 사용 방법:"
echo "1. 실험 매트릭스 생성:"
echo "   python experiments/experiment_generator.py"
echo ""
echo "2. 자동 실험 시작:"
echo "   python experiments/auto_experiment_runner.py"
echo ""
echo "3. 실시간 모니터링 (별도 터미널):"
echo "   python experiments/experiment_monitor.py"
echo ""
echo "4. 제출 관리:"
echo "   python experiments/submission_manager.py list-pending"
echo ""
echo "5. 결과 분석:"
echo "   python experiments/results_analyzer.py --generate-report"
