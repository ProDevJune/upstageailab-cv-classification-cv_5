#!/bin/bash

# 모든 스크립트에 실행 권한 부여
chmod +x *.sh

echo "✅ 모든 .sh 파일에 실행 권한을 부여했습니다."
echo ""
echo "🔧 CV_8U 오류 해결 방법:"
echo "1. git pull 로 최신 변경사항 받기"
echo "2. bash fix_cv_8u_error.sh 실행"
echo "3. python codes/gemini_main_v2.py --config [config_file] 으로 테스트"
echo ""
echo "📋 관련 파일들:"
echo "  - fix_cv_8u_error.sh: 자동 수정 스크립트"
echo "  - requirements_ubuntu_fixed.txt: 수정된 requirements"
echo "  - CV_8U_FIX_GUIDE.md: 상세 해결 가이드"
