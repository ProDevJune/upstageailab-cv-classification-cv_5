#!/bin/bash

echo "🧹 마지막 임시 파일들도 temp로 이동"
echo "=================================="

# 남은 임시 파일들 이동
remaining_temp_files=(
    "cleanup_temp_files.sh"
    "commit_v2_fixes.sh" 
    "fix_mps_warning.sh"
)

echo "📦 남은 임시 파일들 이동 중..."

for file in "${remaining_temp_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" temp/
        echo "✅ $file -> temp/"
    fi
done

echo ""
echo "🎉 모든 임시 파일 정리 완료!"

echo ""
echo "📊 Git 상태 확인:"
git status --porcelain

echo ""
echo "🚀 이제 완전히 깔끔한 환경입니다:"
echo "./run_code_v2.sh"
