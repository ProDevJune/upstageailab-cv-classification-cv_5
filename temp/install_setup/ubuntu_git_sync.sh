#!/bin/bash
# Ubuntu에서 Git 충돌 방지 및 최신 버전 동기화

echo "🐧 Ubuntu Git 상태 정리 및 동기화..."

# 현재 위치 확인
if [ ! -d ".git" ]; then
    echo "❌ Git 저장소가 아닙니다. cv-classification 디렉토리로 이동하세요."
    exit 1
fi

echo "📊 현재 Git 상태:"
git status --short

echo ""
echo "🔄 Git 동기화 전략:"
echo "1. 로컬 변경사항 임시 저장 (stash)"
echo "2. 원격 저장소에서 최신 버전 가져오기 (pull)"
echo "3. Ubuntu 환경 설정 실행"

echo ""
read -p "계속 진행하시겠습니까? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    
    # 1. 로컬 변경사항 확인
    if [[ -n $(git status --porcelain) ]]; then
        echo "📦 로컬 변경사항 임시 저장 중..."
        git stash push -m "Ubuntu local changes - $(date '+%Y%m%d_%H%M%S')"
        echo "✅ 변경사항이 stash에 저장되었습니다."
    else
        echo "ℹ️  저장할 로컬 변경사항이 없습니다."
    fi
    
    # 2. 원격 저장소에서 최신 버전 가져오기
    echo ""
    echo "🔄 원격 저장소에서 최신 버전 가져오는 중..."
    git fetch origin
    
    # 현재 브랜치 확인
    CURRENT_BRANCH=$(git branch --show-current)
    echo "📍 현재 브랜치: $CURRENT_BRANCH"
    
    # Pull 실행
    git pull origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ 최신 버전 동기화 완료!"
        
        # 3. Ubuntu 환경 설정 실행
        echo ""
        echo "🚀 Ubuntu 환경 설정 시작..."
        
        if [ -f "ubuntu_setup.sh" ]; then
            chmod +x ubuntu_setup.sh
            chmod +x *.sh
            echo "🔧 자동 설정 실행 중..."
            ./ubuntu_setup.sh
        else
            echo "⚠️  ubuntu_setup.sh 파일이 없습니다. 수동 설정이 필요합니다:"
            echo "   chmod +x *.sh"
            echo "   ./setup_and_validate_all.sh"
        fi
        
    else
        echo "❌ Pull 실패. 충돌이 발생했을 수 있습니다."
        echo ""
        echo "🔧 수동 해결 방법:"
        echo "1. 충돌 파일 확인: git status"
        echo "2. 충돌 해결 후: git add . && git commit"
        echo "3. 또는 로컬 변경사항 완전 폐기: git reset --hard origin/main"
        
        echo ""
        read -p "로컬 변경사항을 완전히 폐기하고 원격 버전으로 리셋하시겠습니까? (y/n): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🗑️  로컬 변경사항 폐기 중..."
            git reset --hard origin/main
            echo "✅ 원격 버전으로 리셋 완료!"
        fi
    fi
    
    # 4. 최종 상태 확인
    echo ""
    echo "📊 최종 Git 상태:"
    git status --short
    
    echo ""
    echo "💾 Stash 목록 (임시 저장된 변경사항):"
    git stash list
    
    if [[ -n $(git stash list) ]]; then
        echo ""
        echo "💡 임시 저장된 변경사항 복원 방법:"
        echo "   git stash list  # 목록 확인"
        echo "   git stash show stash@{0}  # 내용 확인"
        echo "   git stash pop  # 최신 stash 복원 (필요시)"
    fi
    
else
    echo "❌ 동기화 취소됨"
fi

echo ""
echo "⚠️  중요 안내:"
echo "============="
echo "• Ubuntu에서는 절대 git add/commit/push 하지 마세요!"
echo "• 모든 개발 작업은 macOS에서 진행하세요"
echo "• Ubuntu는 실행 환경으로만 사용하세요"
echo "• 필요시 git pull로만 최신 버전을 가져오세요"
