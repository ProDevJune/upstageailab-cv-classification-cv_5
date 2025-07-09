#!/bin/bash

# 실행 권한 부여
chmod +x commit_cv8u_fix.sh
chmod +x fix_cv8u_error.sh
chmod +x set_permissions_cv8u.sh

# CV_8U 오류 수정 사항을 git에 커밋하고 푸시

echo "🔧 CV_8U AttributeError 수정 사항을 Git에 커밋 중..."

# 스크립트 실행 권한 부여
chmod +x *.sh

# Git 상태 확인
echo "📊 Git 상태 확인:"
git status

echo ""
echo "📝 변경된 파일들:"
echo "  - requirements_ubuntu_fixed.txt (호환 버전으로 수정)"
echo "  - fix_cv_8u_error.sh (기본 수정 스크립트)"
echo "  - fix_cv_8u_error_robust.sh (강화된 수정 스크립트)"
echo "  - fix_cv_8u_simple.sh (간단 수정 스크립트)"
echo "  - CV_8U_FIX_GUIDE.md (상세 해결 가이드 - 캐시 오류 대응 포함)"
echo "  - 기타 권한 설정 스크립트들"

# 모든 변경사항 추가
git add .

# 커밋
git commit -m "🔧 Fix CV_8U AttributeError: Update OpenCV & Albumentations compatibility

- opencv-python: 4.10.0.84 → 4.8.1.78
- albumentations: 1.4.18 → 1.4.0
- Add multiple fix scripts: basic, robust, and simple versions
- Add --no-cache-dir support for pip cache disabled environments
- Add CV_8U_FIX_GUIDE.md with comprehensive troubleshooting
- Update requirements_ubuntu_fixed.txt with compatible versions

Resolves AttributeError: module 'cv2' has no attribute 'CV_8U'
Resolves ERROR: pip cache commands can not function since cache is disabled"

# 푸시
echo ""
echo "🚀 원격 저장소에 푸시 중..."
git push origin main

echo ""
echo "✅ Git 커밋 및 푸시 완료!"
echo ""
echo "🎯 서버에서 실행할 명령어:"
echo "  git pull origin main"
echo ""
echo "🔧 수정 스크립트 선택 (3가지 옵션):"
echo "  bash fix_cv_8u_error_robust.sh  # 강화된 버전 (추천)"
echo "  bash fix_cv_8u_simple.sh        # 간단 버전"
echo "  bash fix_cv_8u_error.sh         # 기본 버전"
echo ""
echo "📋 문제 해결 후 다시 실험 실행:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
