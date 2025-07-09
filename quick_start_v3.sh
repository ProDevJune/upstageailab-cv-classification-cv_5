#!/bin/bash

# V3 자동화 시스템 빠른 시작 가이드

echo "🎯 V3 자동화 시스템 빠른 시작 가이드"
echo "================================================"

# 기본 디렉토리로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

echo ""
echo "📋 단계 1: 권한 설정"
echo "bash setup_v3_permissions.sh"
bash setup_v3_permissions.sh

echo ""
echo "📋 단계 2: V3 실험 생성 (10개 제한)"
echo "python v3_experiment_generator.py --type hierarchical --limit 10"
python v3_experiment_generator.py --type hierarchical --limit 10

echo ""
echo "📋 단계 3: V3 실험 상태 확인"
echo "python v3_experiment_monitor.py --status"
python v3_experiment_monitor.py --status

echo ""
echo "📋 단계 4: 통합 대시보드 상태 확인"
echo "python unified_dashboard/unified_monitor.py --status"
python unified_dashboard/unified_monitor.py --status

echo ""
echo "🎉 V3 자동화 시스템 준비 완료!"
echo ""
echo "📚 다음 단계:"
echo "  1. V3 실험 실행: ./v3_experiments/scripts/run_v3_experiments.sh"
echo "  2. 실시간 모니터링: python v3_experiment_monitor.py --realtime"
echo "  3. 통합 대시보드: python unified_dashboard/unified_monitor.py --continuous"
echo "  4. 통합 실행: python unified_dashboard/unified_runner.py --systems v3"
echo ""
echo "💡 도움말:"
echo "  - V3 실험 매트릭스 확인: cat v3_experiment_matrix.yaml"
echo "  - V3 실험 목록 확인: cat v3_experiments/experiment_list.json"
echo "  - 로그 확인: tail -f v3_experiments/logs/*.log"
