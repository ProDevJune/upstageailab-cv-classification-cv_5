#!/bin/bash
# Git 상태 정리 및 커밋 스크립트

echo "📝 Git 상태 정리 및 커밋 시작..."

cd 

# 현재 Git 상태 확인
echo "📊 현재 Git 상태:"
git status --short

echo ""
echo "📋 변경된 파일들:"
git diff --name-only

echo ""
echo "🔍 스테이징되지 않은 변경사항:"
git diff --stat

echo ""
read -p "이 변경사항들을 커밋하시겠습니까? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 모든 변경사항 스테이징
    echo "📦 변경사항 스테이징 중..."
    git add .
    
    # 커밋 메시지 작성
    echo "💬 커밋 중..."
    git commit -m "Fix absolute paths and add Ubuntu compatibility

🔧 Path fixes:
- Convert absolute paths to relative paths in all scripts
- Fix PROJECT_ROOT detection in setup_and_validate_all.sh
- Fix project_root detection in pre_experiment_validator.py
- Update setup_platform_env.sh for dynamic path detection

🐧 Ubuntu compatibility:
- Add create_ubuntu_archive.sh for cross-platform deployment
- Add ubuntu_setup.sh for automated Ubuntu environment setup
- Exclude macOS-specific files and paths from archive
- Add platform-specific requirements handling

✅ Bug fixes:
- Fix KeyError issues in pre_experiment_validator.py
- Fix pyyaml import detection logic
- Fix Swin Transformer image size mismatch (224→384)
- Add proper error handling for missing validation keys

📦 Archive optimization:
- Exclude venv, logs, cache files from archive
- Optimize for Ubuntu deployment
- Add comprehensive setup automation"
    
    # 원격 저장소에 푸시
    echo "🚀 원격 저장소에 푸시 중..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Git 커밋 및 푸시 완료!"
        echo ""
        echo "🐧 Ubuntu에서 할 일:"
        echo "1. cd "
        echo "2. git stash  # 로컬 변경사항 임시 저장"
        echo "3. git pull origin main  # 최신 버전 가져오기"
        echo "4. ./ubuntu_setup.sh  # 환경 설정 실행"
        echo ""
        echo "⚠️  Ubuntu에서는 절대 git add/commit/push 하지 마세요!"
        echo "    충돌을 방지하기 위해 pull만 사용하세요."
    else
        echo "❌ 푸시 실패. 수동으로 해결 필요:"
        echo "   git status"
        echo "   git pull origin main"
        echo "   # 충돌 해결 후"
        echo "   git push origin main"
    fi
else
    echo "❌ 커밋 취소됨"
    echo ""
    echo "🔧 수동 커밋 방법:"
    echo "   git add ."
    echo "   git commit -m 'Your commit message'"
    echo "   git push origin main"
fi

echo ""
echo "📊 최종 Git 상태:"
git status --short
