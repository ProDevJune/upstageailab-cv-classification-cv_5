#!/bin/bash

# 의존성 충돌 해결책 전체를 git에 커밋하고 푸시

echo "🔧 의존성 충돌 완전 해결책들을 Git에 커밋 중..."

# 실행 권한 부여
chmod +x *.sh

echo "📊 Git 상태 확인:"
git status

echo ""
echo "📝 새로 추가된 의존성 해결 파일들:"
echo "  - fix_dependency_conflicts.sh (강제 재설치로 충돌 해결)"
echo "  - recreate_venv.sh (가상환경 완전 재생성)"
echo "  - test_current_setup.sh (현재 설정 테스트)"
echo "  - DEPENDENCY_RESOLUTION_GUIDE.md (3단계 해결 가이드)"

# 모든 변경사항 추가
git add .

# 커밋
git commit -m "🛠️ Complete dependency conflict resolution system

Multi-tier approach to solve pip dependency resolver issues:

Tier 1 - Quick Test:
- test_current_setup.sh: Check if warnings are just cosmetic
- Fastest solution for cases where dependencies work despite warnings

Tier 2 - Force Resolution:
- fix_dependency_conflicts.sh: Bypass dependency checker with --no-deps
- Sequential installation avoiding resolver conflicts
- Comprehensive testing included

Tier 3 - Nuclear Option:
- recreate_venv.sh: Complete virtual environment recreation
- Clean slate approach guaranteeing resolution
- Backup existing environment before replacement

Documentation:
- DEPENDENCY_RESOLUTION_GUIDE.md: Step-by-step resolution guide
- Clear distinction between warnings vs actual errors
- Recommended execution order with pros/cons

Issues addressed:
❌ albucore requires opencv-python-headless>=4.9.0.80
❌ qudida requires opencv-python-headless>=4.0.1  
❌ seaborn requires matplotlib!=3.6.1,>=3.1
❌ scikit-image requires scipy>=1.11.4

Server execution priority:
1. bash test_current_setup.sh (1min - check if working)
2. bash fix_dependency_conflicts.sh (5min - force fix)
3. bash recreate_venv.sh (10min - nuclear option)"

# 푸시
echo ""
echo "🚀 원격 저장소에 푸시 중..."
git push origin main

echo ""
echo "✅ Git 커밋 및 푸시 완료!"
echo ""
echo "🎯 서버에서 단계별 실행:"
echo "  git pull origin main"
echo ""
echo "🔧 해결 방법 (우선순위 순):"
echo "  1. bash test_current_setup.sh       # 1분 - 현재 상태 테스트"
echo "  2. bash fix_dependency_conflicts.sh # 5분 - 강제 해결 (권장)"
echo "  3. bash recreate_venv.sh            # 10분 - 완전 재생성"
echo ""
echo "📋 해결 후 실험 실행:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
echo ""
echo "💡 핵심 포인트:"
echo "  의존성 경고가 나와도 실제 기능이 작동하면 실험 진행 가능!"
