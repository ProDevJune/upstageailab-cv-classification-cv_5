#!/bin/bash

# V3 자동화 시스템 및 통합 대시보드 실행 권한 설정

echo "🔧 Setting up V3 automation system and unified dashboard permissions..."

# 기본 디렉토리 설정
BASE_DIR="/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5"
cd "$BASE_DIR"

# V3 실험 생성기 실행 권한
chmod +x v3_experiment_generator.py
chmod +x v3_experiment_monitor.py

# V3 실험 스크립트 실행 권한
chmod +x v3_experiments/scripts/*.sh 2>/dev/null || echo "⚠️ V3 scripts directory not found yet"

# 통합 대시보드 실행 권한
chmod +x unified_dashboard/unified_monitor.py
chmod +x unified_dashboard/unified_runner.py

# 기존 V2 스크립트 실행 권한 확인
chmod +x run_v2_1_only.sh
chmod +x run_v2_2_only.sh

# Python 파일들 실행 권한
chmod +x v2_experiment_generator.py
chmod +x v2_experiment_monitor.py

echo "✅ All permissions set successfully!"
echo ""
echo "📋 Available commands:"
echo "  🔬 V3 Experiment Generation: python v3_experiment_generator.py"
echo "  📊 V3 Experiment Monitoring: python v3_experiment_monitor.py"
echo "  🎯 Unified Dashboard: python unified_dashboard/unified_monitor.py"
echo "  🚀 Unified Runner: python unified_dashboard/unified_runner.py"
echo ""
echo "🎉 V3 automation system setup complete!"
