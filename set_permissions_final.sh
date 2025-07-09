#!/bin/bash

# 모든 스크립트에 실행 권한 부여 (Git 명령어 제외)

echo "🔧 모든 스크립트에 실행 권한 부여 중..."

# 모든 .sh 파일에 실행 권한 부여
chmod +x *.sh

echo "✅ 모든 .sh 파일에 실행 권한을 부여했습니다."
echo ""
echo "🎯 Albumentations API 수정 완료!"
echo "💡 권장 실행 순서:"
echo ""
echo "  1️⃣ 현재 상태 확인:"
echo "     bash test_current_setup.sh"
echo ""
echo "  2️⃣ 문제가 있으면 해결:"
echo "     bash fix_dependency_conflicts.sh  # 의존성 충돌 해결"
echo "     또는"
echo "     bash recreate_venv.sh            # 가상환경 재생성"
echo ""
echo "  3️⃣ 실험 실행:"
echo "     python quick_test_experiments.py"
echo "     또는"
echo "     python codes/gemini_main_v2.py --config [config_file]"
echo ""
echo "📋 Git 명령어가 필요하면 GIT_COMMANDS.md 참고하세요!"
