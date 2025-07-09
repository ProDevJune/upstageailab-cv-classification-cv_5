#!/bin/bash

# 불필요한 파일들 정리
echo "🧹 불필요한 파일들 정리 중..."

# Git 관련 스크립트들 제거
if [ -f "mac_git_sync.sh" ]; then
    rm mac_git_sync.sh
    echo "🗑️ mac_git_sync.sh 제거됨"
fi

if [ -f "ubuntu_git_sync.sh" ]; then
    rm ubuntu_git_sync.sh
    echo "🗑️ ubuntu_git_sync.sh 제거됨"
fi

if [ -f "setup_and_sync.sh" ]; then
    rm setup_and_sync.sh
    echo "🗑️ setup_and_sync.sh 제거됨"
fi

echo "✅ 정리 완료!"
