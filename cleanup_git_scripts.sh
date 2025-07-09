#!/bin/bash

# Git 관련 커밋 스크립트들을 정리하는 스크립트
# 더 이상 사용하지 않는 커밋 스크립트들을 백업 폴더로 이동

echo "🧹 Git 관련 커밋 스크립트들 정리 중..."

# 백업 폴더 생성
mkdir -p old_git_scripts

# Git 관련 커밋 스크립트들 이동
mv commit_albumentations_fix.sh old_git_scripts/ 2>/dev/null || echo "commit_albumentations_fix.sh 없음"
mv commit_cv8u_fix.sh old_git_scripts/ 2>/dev/null || echo "commit_cv8u_fix.sh 없음"
mv commit_dependency_fixes.sh old_git_scripts/ 2>/dev/null || echo "commit_dependency_fixes.sh 없음"
mv commit_numpy_fix.sh old_git_scripts/ 2>/dev/null || echo "commit_numpy_fix.sh 없음"
mv commit_cross_platform.sh old_git_scripts/ 2>/dev/null || echo "commit_cross_platform.sh 없음"

echo "✅ Git 커밋 스크립트들을 old_git_scripts/ 폴더로 이동했습니다."
echo ""
echo "📋 현재 사용 가능한 주요 스크립트들:"
echo "  🧪 테스트:"
echo "    - test_current_setup.sh (현재 상태 테스트)"
echo "    - python quick_test_experiments.py (실험 테스트)"
echo ""
echo "  🔧 문제 해결:"
echo "    - fix_albumentations_api.sh (API 수정 확인)"  
echo "    - fix_complete_compatibility.sh (완전 호환성 해결)"
echo "    - fix_dependency_conflicts.sh (의존성 충돌 해결)"
echo "    - fix_with_requirements.sh (Requirements 사용)"
echo "    - recreate_venv.sh (가상환경 재생성)"
echo ""
echo "  📖 문서:"
echo "    - GIT_COMMANDS.md (Git 명령어 모음)"
echo "    - ALBUMENTATIONS_API_FIX.md (API 수정 보고서)"
echo "    - DEPENDENCY_RESOLUTION_GUIDE.md (의존성 해결 가이드)"
