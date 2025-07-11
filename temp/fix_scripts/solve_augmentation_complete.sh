#!/bin/bash

# Albumentations API 문제 통합 해결 스크립트
# 진단 -> 수정 -> 테스트를 한 번에 실행

echo "🔧 Albumentations API 문제 통합 해결 시작..."

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

echo "1️⃣ 현재 환경 진단 중..."
python check_augmentation_env.py

echo ""
echo "2️⃣ API 호환성 수정 중..."
python fix_augmentation_immediate.py

echo ""
echo "3️⃣ 실험 테스트 실행 중..."
echo "🧪 quick_test_experiments.py 실행..."

python quick_test_experiments.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 모든 문제 해결 완료!"
    echo "✅ 실험이 성공적으로 실행되었습니다!"
else
    echo "⚠️ 아직 문제가 남아있습니다."
    echo ""
    echo "💡 추가 해결 방법:"
    echo "  - bash fix_dependency_conflicts.sh"
    echo "  - bash recreate_venv.sh"
    echo ""
    echo "📋 수동 확인:"
    echo "  - codes/gemini_augmentation_v2.py 파일의 fill 파라미터"
    echo "  - albumentations 버전 호환성"
fi

echo ""
echo "📄 로그 파일들:"
ls -la /tmp/test_error_*.log 2>/dev/null || echo "  (오류 로그 없음)"
