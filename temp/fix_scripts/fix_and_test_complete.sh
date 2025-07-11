#!/bin/bash

# Albumentations 1.4.0 완전 호환 수정 및 테스트

echo "🚨 긴급! Albumentations 1.4.0 완전 호환 수정"
echo "fill 파라미터가 완전히 제거되었으므로 새로운 코드로 교체합니다."
echo ""

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

# 실행 권한 부여
chmod +x fix_augmentation_1_4_0.py

echo "🔧 1단계: 완전 호환 코드로 교체..."
python fix_augmentation_1_4_0.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🧪 2단계: 실험 테스트 실행..."
    python quick_test_experiments.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 모든 문제 해결 완료!"
        echo "✅ Albumentations 1.4.0과 완전 호환됩니다!"
    else
        echo ""
        echo "⚠️ 실험 테스트에서 다른 문제가 발견되었습니다."
        echo "💡 로그를 확인해보세요:"
        ls -la /tmp/test_error_*.log 2>/dev/null
    fi
else
    echo "❌ 코드 교체에 실패했습니다."
fi

echo ""
echo "📋 주요 변경사항:"
echo "  - 모든 fill 파라미터 제거"
echo "  - border_mode 중복 문제 해결"
echo "  - Albumentations 1.4.0 API에 완전 맞춤"
echo "  - 기능은 동일하게 유지"
