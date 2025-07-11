#!/bin/bash
# 개선된 train.csv 기반 완전 재실행 준비 스크립트

cd 

echo "🎯 개선된 train.csv 기반 CV Classification 재실행 준비"
echo "=================================================================="

# 1. 실행 권한 설정
echo "🔧 1. 실행 권한 설정..."
chmod +x run_absolute.sh
chmod +x run_b3.sh
chmod +x run_convnext.sh
chmod +x ensemble_2models_v2.py
chmod +x ensemble_3models_v2.py
chmod +x execution_tracker_v2.py
chmod +x setup_ensemble_v2.sh

echo "✅ 실행 권한 설정 완료"

# 2. 디렉토리 확인
echo ""
echo "🔍 2. 환경 확인..."
echo "   📁 프로젝트 경로: $(pwd)"
echo "   📊 train.csv 크기: $(wc -l < data/train.csv) 줄"
echo "   📊 백업 파일: $(ls -la data/train_backup_* 2>/dev/null | wc -l) 개"

# 3. 가상환경 확인
if [ -d "venv" ]; then
    echo "   🐍 가상환경: 존재"
else
    echo "   ❌ 가상환경: 없음"
fi

# 4. 기존 결과 요약
echo ""
echo "📊 3. 기존 성능 기준 (참고용):"
echo "   🥇 EfficientNet-B4: 로컬 0.9419 / 서버 0.8619"
echo "   🥈 EfficientNet-B3: 로컬 0.9187 / 서버 0.8526" 
echo "   🥉 ConvNeXt-Base: 로컬 0.9346 / 서버 0.8158"

# 5. 실행 순서 안내
echo ""
echo "🚀 4. 실행 순서:"
echo "   Phase 1: 개별 모델 재학습"
echo "     1.1) ./run_absolute.sh      # EfficientNet-B4"
echo "     1.2) ./run_b3.sh           # EfficientNet-B3"
echo "     1.3) ./run_convnext.sh     # ConvNeXt-Base"
echo ""
echo "   Phase 2: 앙상블 구성"
echo "     2.1) B4 단독 제출 (Phase 1.1 결과)"
echo "     2.2) python ensemble_2models_v2.py    # B4+B3"
echo "     2.3) python ensemble_3models_v2.py    # B4+B3+ConvNeXt"

# 6. 추적 시스템 안내
echo ""
echo "📋 5. 결과 추적:"
echo "   • python execution_tracker_v2.py  # 전체 가이드 및 추적"
echo "   • experiment_results_v2.json      # 상세 결과 로그"
echo "   • submission_paths_v2.csv         # 제출 파일 목록"

echo ""
echo "✅ 준비 완료! 첫 번째 실험을 시작하세요:"
echo "   ./run_absolute.sh"
echo ""
echo "💡 언제든지 진행상황 확인:"
echo "   python execution_tracker_v2.py"
