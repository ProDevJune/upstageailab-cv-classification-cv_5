#!/bin/bash

# V3 자동화 시스템 최종 실행 권한 설정

echo "🔧 Setting up final V3 automation system permissions..."

# 기본 디렉토리 설정
BASE_DIR="/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5"
cd "$BASE_DIR"

# 모든 Python 파일에 실행 권한 추가
chmod +x *.py
chmod +x v3_experiment_generator.py
chmod +x v3_experiment_monitor.py
chmod +x unified_dashboard/*.py

# 모든 shell 스크립트에 실행 권한 추가
chmod +x *.sh
chmod +x setup_v3_permissions.sh
chmod +x quick_start_v3.sh

# 기존 V2 스크립트 실행 권한 확인
chmod +x run_v2_1_only.sh
chmod +x run_v2_2_only.sh

# V3 실험 디렉토리 생성 및 권한 설정
mkdir -p v3_experiments/{configs/{modelA,modelB},scripts,logs}
chmod +x v3_experiments/scripts/*.sh 2>/dev/null || echo "⚠️ V3 scripts will be created later"

# 통합 대시보드 결과 디렉토리 생성
mkdir -p unified_dashboard/{results,logs}

echo "✅ All permissions set successfully!"
echo ""
echo "🎯 V3 자동화 시스템 구축 완료!"
echo ""
echo "📚 다음 단계:"
echo "  1. 빠른 시작: ./quick_start_v3.sh"
echo "  2. 직접 실행: python v3_experiment_generator.py --help"
echo "  3. 통합 대시보드: python unified_dashboard/unified_monitor.py --help"
echo ""
echo "🎉 Ready to run V3 experiments!"
