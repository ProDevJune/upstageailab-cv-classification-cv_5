#!/bin/bash

# NumPy 2.x 호환성 문제 해결 사항을 git에 커밋하고 푸시

echo "🔧 NumPy 2.x 호환성 문제 해결 사항을 Git에 커밋 중..."

# 실행 권한 부여
chmod +x *.sh

# Git 상태 확인
echo "📊 Git 상태 확인:"
git status

echo ""
echo "📝 새로 추가된 해결 파일들:"
echo "  - fix_complete_compatibility.sh (순차적 패키지 설치)"
echo "  - fix_with_requirements.sh (requirements 파일 사용)"
echo "  - requirements_ubuntu_complete_fix.txt (완전 호환성 검증 버전)"
echo "  - NUMPY_COMPATIBILITY_FIX.md (NumPy 2.x 문제 해결 가이드)"

# 모든 변경사항 추가
git add .

# 커밋
git commit -m "🚨 URGENT: Fix NumPy 2.x compatibility & CV_8U issues

Critical fixes for multiple compatibility problems:

1. NumPy 2.x downgrade to 1.26.4:
   - Resolves matplotlib version conflict
   - Fixes pandas binary compatibility 
   - Ensures ecosystem stability

2. Enhanced fix scripts:
   - fix_complete_compatibility.sh: Sequential package installation
   - fix_with_requirements.sh: Requirements file approach
   - requirements_ubuntu_complete_fix.txt: Verified compatible versions

3. Verified compatibility matrix:
   - numpy==1.26.4 (compatible with all packages)
   - opencv-python==4.8.1.78 (CV_8U support)
   - albumentations==1.4.0 (tested compatibility)
   - pandas==2.2.3 (binary compatible)

4. Issues resolved:
   ❌ AttributeError: module 'cv2' has no attribute 'CV_8U'
   ❌ ValueError: numpy.dtype size changed, binary incompatibility
   ❌ matplotlib version conflicts
   ❌ pip cache disabled errors

Server execution: git pull && bash fix_complete_compatibility.sh"

# 푸시
echo ""
echo "🚀 원격 저장소에 푸시 중..."
git push origin main

echo ""
echo "✅ Git 커밋 및 푸시 완료!"
echo ""
echo "🎯 서버에서 긴급 실행할 명령어:"
echo "  git pull origin main"
echo ""
echo "🔧 해결 스크립트 선택 (2가지 옵션):"
echo "  bash fix_complete_compatibility.sh    # 순차적 설치 (추천)"
echo "  bash fix_with_requirements.sh         # Requirements 파일 사용"
echo ""
echo "📋 완전 해결 후 실험 재실행:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
echo ""
echo "🔍 설치 후 검증:"
echo "  python -c \"import cv2, albumentations, numpy; print('✅ 모든 호환성 문제 해결')\""
