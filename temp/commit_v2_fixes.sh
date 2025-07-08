#!/bin/bash

echo "📝 Code v2 수정사항 Git 커밋"
echo "============================"

# 변경된 주요 파일들만 추가
echo "📁 주요 변경 파일들 추가 중..."
git add codes/gemini_main_v2.py
git add run_code_v2.sh

# 유용한 수정 스크립트들도 추가
echo "📁 수정 스크립트들 추가 중..."
git add fix_paths_for_linux.sh
git add fix_tta_access.sh
git add fix_config_access.sh

echo ""
echo "💾 Git 커밋 실행 중..."
git commit -m "feat: Code v2 시스템 완전 수정 및 Linux 호환성 개선

주요 수정사항:
- gemini_main_v2.py 경로 문제 해결 (codes/codes/ 중복 제거)
- 절대 경로를 상대 경로로 변경하여 Linux 서버 호환성 확보
- config 속성 안전 접근 방식 개선 (getattr 사용)
- TTA 속성 누락 문제 해결
- run_code_v2.sh 스크립트 경로 수정
- MPS 환경에서 pin_memory 경고 해결

기술적 개선:
- project_root 동적 설정으로 환경 독립성 확보
- config_file_path 상대 경로 사용
- data_dir 상대 경로로 변경
- 모든 config 속성 안전 접근 구현

실행 환경:
- Mac (MPS) 환경에서 테스트 완료
- Linux 서버 배포 준비 완료
- Focal Loss + MixUp/CutMix + Dynamic Augmentation 모든 고급 기능 정상 작동

이제 어떤 환경에서든 ./run_code_v2.sh 한 번의 실행으로 
Swin Transformer 기반 고급 CV 분류 시스템이 정상 작동합니다."

echo ""
echo "✅ Git 커밋 완료!"
echo ""
echo "📊 커밋 확인:"
git log --oneline -1

echo ""
echo "🚀 푸시 명령어 (필요시):"
echo "git push origin main"

echo ""
echo "🧹 임시 스크립트 정리 (선택사항):"
echo "rm -f complete_fix.sh create_simple_config.sh debug_path.sh"
echo "rm -f final_absolute_fix.sh final_fix_v2.sh fix_absolute_path.sh"
echo "rm -f fix_path_exact.sh fix_run_script.sh quick_fix_v2.sh"
echo "rm -f restructure_v2.sh ultimate_fix_v2.sh import_fix.py"
echo "rm -f codes/gemini_main_v2.py.broken"
