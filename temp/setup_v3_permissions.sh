#!/bin/bash

# v3 시스템 실행 권한 설정
echo "🔧 v3 시스템 실행 권한 설정 중..."

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# 실행 권한 부여
chmod +x run_code_v3.sh

echo "✅ 실행 권한 설정 완료"
echo ""
echo "🔥 Phase 1 v3 시스템 사용법:"
echo "   ./run_code_v3.sh"
echo ""
echo "🏆 적용된 고급 기법:"
echo "   - Focal Loss (클래스 불균형 해결)"
echo "   - Label Smoothing (일반화 성능 향상)"  
echo "   - CutMix & MixUp (강력한 데이터 증강)"
echo ""
echo "📈 예상 성능 향상: +9~14% F1-score"
