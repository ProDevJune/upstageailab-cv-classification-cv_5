#!/bin/bash

# V2_1 & V2_2 자동 실험 시스템 설정 스크립트

echo "🚀 Setting up V2_1 & V2_2 Automatic Experiment System"
echo "======================================================"

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 실행 권한 부여
chmod +x v2_experiment_generator.py
chmod +x v2_experiment_monitor.py

# 실험 생성 및 실행
echo "📊 Generating experiment configurations..."
python v2_experiment_generator.py --phase phase1

echo ""
echo "✅ V2_1 & V2_2 Automatic Experiment System is ready!"
echo ""
echo "🎯 Quick Start Commands:"
echo "  1. Generate all experiments: python v2_experiment_generator.py"
echo "  2. Run experiments: ./v2_experiments/run_all_experiments.sh"
echo "  3. Monitor progress: python v2_experiment_monitor.py --mode monitor"
echo "  4. Analyze results: python v2_experiment_monitor.py --mode analyze"
echo ""
echo "📚 Full guide: V2_AUTO_EXPERIMENT_GUIDE.md"
echo ""
echo "🔥 Estimated total experiments: 80-100+"
echo "⏱️ Estimated total time: 2-7 days (depending on hardware)"
