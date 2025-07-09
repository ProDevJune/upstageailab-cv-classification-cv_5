#!/bin/bash

# 서버에서 즉시 Albumentations API 수정하는 스크립트
# gemini_augmentation_v2.py 파일의 fill 파라미터를 즉시 수정

echo "🔧 서버에서 Albumentations API 즉시 수정 중..."

AUGMENTATION_FILE="codes/gemini_augmentation_v2.py"

if [ ! -f "$AUGMENTATION_FILE" ]; then
    echo "❌ $AUGMENTATION_FILE 파일을 찾을 수 없습니다."
    exit 1
fi

echo "📄 현재 파일 백업 중..."
cp "$AUGMENTATION_FILE" "${AUGMENTATION_FILE}.backup_$(date +%Y%m%d_%H%M%S)"

echo "🔄 API 파라미터 수정 중..."

# 1. A.Affine의 fill=(255,255,255) -> fill=255로 변경
sed -i 's/fill=(255,255,255)/fill=255/g' "$AUGMENTATION_FILE"

# 2. A.Rotate의 fill=(255,255,255) -> fill=255로 변경  
sed -i 's/fill=(255,255,255)/fill=255/g' "$AUGMENTATION_FILE"

# 3. A.Perspective의 fill=(255,255,255) -> fill=255로 변경
sed -i 's/fill=(255,255,255)/fill=255/g' "$AUGMENTATION_FILE"

# 4. A.CoarseDropout의 fill=(0,0,0) -> fill=0으로 변경
sed -i 's/fill=(0,0,0)/fill=0/g' "$AUGMENTATION_FILE"

# 5. A.PadIfNeeded의 fill -> value로 변경
sed -i 's/fill=(255, 255, 255)/value=(255, 255, 255)/g' "$AUGMENTATION_FILE"

# 6. A.Rotate에 border_mode 추가 (필요한 경우)
sed -i '/A\.Rotate(/,/)/s/limit=(/border_mode=cv2.BORDER_CONSTANT,\n            limit=(/g' "$AUGMENTATION_FILE"

echo "✅ API 파라미터 수정 완료!"

echo "🧪 즉시 테스트..."
python -c "
try:
    import sys
    sys.path.append('codes')
    from gemini_augmentation_v2 import AUG
    print('✅ gemini_augmentation_v2.py import 성공!')
    
    # 간단한 변환 테스트
    import albumentations as A
    import numpy as np
    
    transform = AUG['basic']
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = transform(image=test_img)
    print('✅ Augmentation 변환 테스트 성공!')
    print('🎉 API 호환성 문제 해결 완료!')
    
except Exception as e:
    print(f'❌ 테스트 실패: {e}')
    print('💡 수동으로 파일을 확인해주세요.')
"

echo ""
echo "🚀 이제 실험을 다시 실행하세요:"
echo "  python quick_test_experiments.py"
echo "  또는"
echo "  python codes/gemini_main_v2.py --config [config_file]"
