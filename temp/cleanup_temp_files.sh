#!/bin/bash

echo "🧹 임시 파일들을 temp 폴더로 정리"
echo "================================"

# temp 폴더 생성 (이미 있으면 무시)
mkdir -p temp

echo "📁 temp 폴더 생성 완료"

# 실행에 필요없는 임시 파일들 목록
temp_files=(
    "complete_fix.sh"
    "create_simple_config.sh" 
    "debug_path.sh"
    "final_absolute_fix.sh"
    "final_fix_v2.sh"
    "fix_absolute_path.sh"
    "fix_config_access.sh"
    "fix_mps_warning.sh"
    "fix_path_exact.sh"
    "fix_paths_for_linux.sh"
    "fix_run_script.sh"
    "fix_tta_access.sh"
    "import_fix.py"
    "quick_fix_v2.sh"
    "restructure_v2.sh"
    "ultimate_fix_v2.sh"
    "commit_v2_fixes.sh"
    "codes/gemini_main_v2.py.broken"
    "codes/gemini_main_v2.py.backup"
)

echo ""
echo "📦 임시 파일들 이동 중..."

moved_count=0
for file in "${temp_files[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" temp/
        echo "✅ $file -> temp/"
        ((moved_count++))
    else
        echo "⚠️ $file (파일 없음)"
    fi
done

echo ""
echo "🎉 정리 완료!"
echo "📊 총 $moved_count 개 파일을 temp 폴더로 이동했습니다."

echo ""
echo "📂 현재 루트 디렉토리 상태:"
ls -la | grep -E '\.(sh|py)$' | head -10

echo ""
echo "📂 temp 폴더 내용:"
ls -la temp/ | head -10

echo ""
echo "🚀 이제 깔끔한 환경에서 실행하세요:"
echo "./run_code_v2.sh"

echo ""
echo "📋 유지된 주요 파일들:"
echo "✅ run_code_v2.sh (실행 스크립트)"
echo "✅ codes/gemini_main_v2.py (메인 코드)"
echo "✅ codes/config_v2.yaml (설정 파일)"
echo "✅ 기타 필수 실행 파일들"
