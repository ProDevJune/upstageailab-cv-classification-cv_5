#!/bin/bash

# V2_1 & V2_2 자동 실험 시스템 설정 스크립트

echo "🚀 Setting up V2_1 & V2_2 Automatic Experiment System"
echo "======================================================"

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 실행 권한 부여
chmod +x v2_experiment_generator.py
chmod +x v2_experiment_monitor.py
chmod +x run_v2_experiments.sh
chmod +x run_v2_1_only.sh
chmod +x run_v2_2_only.sh

# 테스트용 phase1 실험 생성
echo "📊 Generating Phase 1 experiments for testing..."
python v2_experiment_generator.py --phase phase1

echo ""
echo "✅ V2_1 & V2_2 Automatic Experiment System is ready!"
echo ""
echo "🎯 Quick Start Commands:"
echo "  📋 All experiments: ./run_v2_experiments.sh"
echo "  🏗️ V2_1 only: ./run_v2_1_only.sh"
echo "  ⚡ V2_2 only: ./run_v2_2_only.sh"
echo "  🎮 Interactive: ./run_v2_experiments.sh --interactive"
echo "  🚀 Quick test: ./run_v2_experiments.sh --quick"
echo ""
echo "🔧 Advanced Usage:"
echo "  python v2_experiment_generator.py --type v2_1 --model convnextv2"
echo "  python v2_experiment_generator.py --type v2_2 --technique mixup"
echo "  python v2_experiment_generator.py --phase phase1 --limit 5"
echo ""
echo "📚 Full guide: V2_AUTO_EXPERIMENT_GUIDE.md"
echo ""
echo "🔥 Ready to run experiments with full v2_1/v2_2 separation!"
