#!/bin/bash

echo "🔥 Albumentations 호환성 즉시 수정!"
echo "=================================="

echo "📝 gemini_augmentation_v2.py 수정 중..."

python3 << 'EOF'
with open('codes/gemini_augmentation_v2.py', 'r') as f:
    content = f.read()

# PadIfNeeded의 fill을 value로 변경 (Albumentations 2.x 호환)
content = content.replace(
    "A.PadIfNeeded(min_height=cfg.image_size, min_width=cfg.image_size, border_mode=cv2.BORDER_CONSTANT, fill=(255, 255, 255), p=1.0)",
    "A.PadIfNeeded(min_height=cfg.image_size, min_width=cfg.image_size, border_mode=cv2.BORDER_CONSTANT, value=(255, 255, 255), p=1.0)"
)

# 모든 fill 인수를 value로 변경
import re

# fill= 를 value= 로 변경
content = re.sub(r'\bfill=', 'value=', content)

# std_range를 var_limit으로 변경 (GaussNoise)
content = re.sub(r'std_range=', 'var_limit=', content)

# 파일 저장
with open('codes/gemini_augmentation_v2.py', 'w') as f:
    f.write(content)

print("✅ Albumentations 호환성 수정 완료!")
EOF

echo ""
echo "🚀 즉시 실행:"
echo "./run_code_v2.sh"
