#!/bin/bash

echo "🔧 최종 Albumentations 1.4.0 호환성 수정 커밋"

# 변경사항 확인
echo "📋 변경된 파일:"
git status --porcelain

# 수정된 파일 추가
git add codes/gemini_augmentation_v2.py

# 커밋
git commit -m "Final fix: CoarseDropout fill -> max_holes for Albumentations 1.4.0 compatibility

- Replace A.CoarseDropout fill parameter with max_holes
- Complete Albumentations 1.4.0 compatibility
- All deprecated parameters fixed:
  * Downscale: scale_range -> scale_min/scale_max  
  * Affine: fill -> value
  * CoarseDropout: fill -> max_holes"

# 강제 푸시
echo "📤 서버로 강제 푸시 중..."
git push origin lyj/auto --force-with-lease

echo "✅ 모든 수정사항이 서버로 푸시되었습니다!"
echo "🚀 이제 서버에서 git pull 후 다시 테스트해보세요."
