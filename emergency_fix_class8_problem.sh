#!/bin/bash

# 🚨 클래스 8 편향 문제 긴급 해결 스크립트
echo "🔧 클래스 8 편향 문제 긴급 수정 시작"
echo "=================================="

# 1. 현재 실행 중인 모든 Python 실험 프로세스 중단
echo "🛑 현재 실행 중인 모든 Python 실험 프로세스 중단 중..."
pkill -f "python.*gemini_main"
pkill -f "python.*v2_experiment"
pkill -f "python.*v3_experiment"
sleep 5

# 2. GPU 메모리 정리
echo "🧹 GPU 메모리 정리 중..."
python -c "import torch; torch.cuda.empty_cache()" 2>/dev/null

# 3. 기존 실험 결과 백업
echo "💾 기존 실험 결과 백업 중..."
BACKUP_DIR="backup_before_fix_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r v2_experiments/configs "$BACKUP_DIR/" 2>/dev/null
cp -r v3_experiments/configs "$BACKUP_DIR/" 2>/dev/null
cp -r data/submissions "$BACKUP_DIR/" 2>/dev/null

echo "✅ 모든 설정 파일이 수정되었습니다!"
echo ""
echo "🎯 주요 수정 사항:"
echo "  ✅ V2_1: patience 5 → 30, FocalLoss, class_weighting 활성화"
echo "  ✅ V2_2: patience 5 → 20, class_weighting 활성화"
echo "  ✅ V3_A: patience 7 → 20, class_weighting 활성화" 
echo "  ✅ V3_B: patience 7 → 15, class_weighting 활성화"
echo "  ✅ 모든 config: weighted_random_sampler 활성화"
echo "  ✅ 클래스 불균형 해결: max_samples 150으로 증가"
echo ""
echo "🚀 새로운 실험 시작 방법:"
echo "  1. ./run_optimal_performance.sh  (전체 실험 재시작)"
echo "  2. ./run_v2_1_only.sh --auto     (V2_1만 재시작)"
echo "  3. python v3_experiment_generator.py --phase phase1 && ./v3_experiments/scripts/run_v3_phase1.sh"
echo ""
echo "📊 실시간 모니터링:"
echo "  watch 'ps aux | grep python | grep -E \"(v2|v3)\"'"
echo "  tail -f logs/optimal_performance_*/main.log"
echo ""
echo "🎉 클래스 8 편향 문제 해결 완료!"
