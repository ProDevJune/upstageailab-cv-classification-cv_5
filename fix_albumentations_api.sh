#!/bin/bash

# Albumentations 1.4.0 API 변경 대응 스크립트
# Affine fill 파라미터 수정 완료

echo "🔧 Albumentations 1.4.0 API 호환성 수정 완료!"

echo "📝 수정된 내용:"
echo "  - A.Affine: fill=(255,255,255) → fill=255"
echo "  - A.Rotate: fill=(255,255,255) → fill=255 추가"
echo "  - A.Perspective: fill=255 파라미터 추가"
echo "  - A.PadIfNeeded: fill=(255, 255, 255) → value=(255, 255, 255)"
echo "  - A.CoarseDropout: fill=(0,0,0) → fill=0"

echo ""
echo "✅ 모든 API 변경사항 수정 완료!"
echo "🚀 이제 실험을 다시 실행해보세요:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
echo "  또는"
echo "  python quick_test_experiments.py"
