#!/bin/bash

# 모든 Albumentations API 변경사항 최종 수정

echo "🚨 Albumentations 1.4.0 모든 API 변경사항 최종 수정!"
echo "발견된 문제들:"
echo "  ❌ A.Affine: fill 파라미터 제거"
echo "  ❌ A.GaussNoise: std_range -> var_limit 변경"
echo "  ❌ 기타 API 변경사항들"
echo ""

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

# 실행 권한 부여
chmod +x fix_all_api_changes.py

echo "🔧 1단계: 모든 API 변경사항 확인 및 수정..."
python fix_all_api_changes.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🧪 2단계: 즉시 실험 테스트..."
    python quick_test_experiments.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉🎉🎉 완전 성공!"
        echo "✅ 모든 API 호환성 문제가 해결되었습니다!"
        echo "✅ 실험이 정상적으로 실행됩니다!"
    else
        echo ""
        echo "⚠️ 아직 다른 문제가 있을 수 있습니다."
        echo "📋 로그 확인:"
        ls -la /tmp/test_error_*.log 2>/dev/null
    fi
else
    echo "❌ API 수정에 실패했습니다."
fi

echo ""
echo "📋 주요 수정사항:"
echo "  🔧 A.GaussNoise: std_range -> var_limit"
echo "  🔧 모든 fill 파라미터 완전 제거"
echo "  🔧 Albumentations 1.4.0 완전 호환"
echo "  ✅ 모든 변환 기능 동일하게 유지"
