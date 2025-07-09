#!/bin/bash

# 새로 생성된 스크립트들에 실행 권한 부여

chmod +x fix_augmentation_immediate.sh
chmod +x fix_augmentation_immediate.py
chmod +x check_augmentation_env.py  
chmod +x solve_augmentation_complete.sh

echo "✅ 새 스크립트들에 실행 권한 부여 완료!"
echo ""
echo "🎯 권장 실행 순서:"
echo ""
echo "  🔍 1단계: 환경 진단"
echo "     python check_augmentation_env.py"
echo ""
echo "  🔧 2단계: 즉시 수정"  
echo "     python fix_augmentation_immediate.py"
echo ""
echo "  🧪 3단계: 테스트"
echo "     python quick_test_experiments.py"
echo ""
echo "  ⚡ 또는 한 번에:"
echo "     bash solve_augmentation_complete.sh"
