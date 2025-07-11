#!/bin/bash

# 🗂️ CV 분류 프로젝트 스크립트 정리 및 이동 스크립트
# 루트에 있는 일회성 스크립트들을 temp 폴더로 체계적으로 이동

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 로그 함수들
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "\n${PURPLE}=== $1 ===${NC}"
}

# 프로젝트 루트 확인
PROJECT_ROOT="/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5"
cd "$PROJECT_ROOT" || exit 1

log_header "🗂️ CV 분류 프로젝트 스크립트 정리 시작"

# 유지할 핵심 스크립트들 (이동하지 않음)
declare -a KEEP_SCRIPTS=(
    "run_experiments.sh"
    "setup_venv.sh"
    "activate_venv.sh"
    "run_full_pipeline.sh"
    "run_ensemble.sh"
    "cleanup.sh"
    "run_b3.sh"
    "run_convnext.sh"
    "run_absolute.sh"
    "run_v2_experiments.sh"
    "run_experiment.sh"
    "run_experiment_fixed.sh"
    "cleanup_cache.sh"
    "cleanup_deep.sh"
    "cleanup_git_scripts.sh"
    "run_all_priority.sh"
    "run_code_v1.sh"
    "run_code_v2.sh"
    "run_my_configs.sh"
    "run_setup.sh"
)

# 이동할 스크립트들 정의 (카테고리별)

# 1. Fix 스크립트들 -> temp/fix_scripts/
declare -a FIX_SCRIPTS=(
    "fix_aistages_paths.sh"
    "fix_albumentations.sh"
    "fix_albumentations_api.sh"
    "fix_all_and_test.sh"
    "fix_all_api_changes.py"
    "fix_and_test_complete.sh"
    "fix_augmentation_1_4_0.py"
    "fix_augmentation_immediate.py"
    "fix_augmentation_immediate.sh"
    "fix_complete_compatibility.sh"
    "fix_config_access.sh"
    "fix_config_data_dir.sh"
    "fix_convnext_rerun.sh"
    "fix_cv_8u_error.sh"
    "fix_cv_8u_error_robust.sh"
    "fix_cv_8u_simple.sh"
    "fix_dataloader_issue.py"
    "fix_dependencies.sh"
    "fix_dependency_conflicts.sh"
    "fix_ensemble_targets.py"
    "fix_environment.sh"
    "fix_experiment_matrix.sh"
    "fix_experiment_stability.sh"
    "fix_linux_compatibility.sh"
    "fix_missing_packages.sh"
    "fix_paths_for_linux.sh"
    "fix_python313_packages.sh"
    "fix_requirements_and_validate.sh"
    "fix_shell_config.py"
    "fix_tta_access.sh"
    "fix_ubuntu_v2.sh"
    "fix_ultimate_and_test.sh"
    "fix_ultimate_compatibility.py"
    "fix_v2_experiments.sh"
    "fix_venv_libraries.sh"
    "fix_warnings.sh"
    "fix_with_requirements.sh"
    "complete_fix.sh"
    "complete_path_fix.sh"
    "final_path_cleanup.sh"
    "manual_fix_lines.sh"
    "nuclear_fix.py"
    "remove_mac_hardcode.sh"
    "remove_value_params.sh"
    "solve_augmentation_complete.sh"
    "resolve_git_conflict.sh"
)

# 2. Debug/Test 스크립트들 -> temp/debug_test/
declare -a DEBUG_TEST_SCRIPTS=(
    "debug_v2_experiment.sh"
    "check_aistages_path_compatibility.sh"
    "check_aistages_system.sh"
    "check_augmentation_env.py"
    "check_current_experiments.py"
    "check_environment.py"
    "check_experiment_stability.sh"
    "check_ml_compatibility.sh"
    "check_python_compatibility.sh"
    "check_venv_libraries.sh"
    "validate_complete_system.sh"
    "validate_experiment_system.py"
    "test_platform_compatibility.py"
    "test_current_setup.sh"
    "test_enhanced_v2.sh"
    "test_experiment_system.py"
    "test_hpo_system.py"
    "test_isolation.py"
    "test_platform_detection.py"
    "test_v2_1_mixup.sh"
    "test_v2_imports.py"
    "test_wandb_improvements.sh"
    "test_yaml_and_validate.sh"
    "test_augmentation_compatibility.py"
    "test_csv_compatibility.py"
    "simple_platform_test.py"
    "diagnose_env.py"
    "diagnose_environment.py"
    "diagnose_venv_detailed.py"
    "diagnose_yaml_issue.py"
    "comprehensive_server_analysis.py"
    "analyze_b4_v1_files.py"
    "analyze_multi_terminal_performance.sh"
    "analyze_optimal_performance_strategy.sh"
    "analyze_performance_drop.py"
    "analyze_train_changes.py"
    "check_actual_results.py"
    "quick_check.sh"
    "quick_safety_check.sh"
    "quick_compatibility_check.sh"
    "quick_compatibility_check_fixed.sh"
    "monitor_resources.sh"
    "final_validation.sh"
)

# 3. Install/Setup 스크립트들 -> temp/install_setup/
declare -a INSTALL_SETUP_SCRIPTS=(
    "install_aistages.sh"
    "install_aistages_en.sh"
    "install_all_packages.py"
    "install_minimal.sh"
    "install_minimal_en.sh"
    "install_missing_packages.sh"
    "install_packages.sh"
    "install_packages_simple.py"
    "install_timm.py"
    "setup_and_validate_all.sh"
    "setup_custom_configs.sh"
    "setup_enhanced_v2.sh"
    "setup_ensemble_v2.sh"
    "setup_experiment_system.sh"
    "setup_experiments.sh"
    "setup_files.sh"
    "setup_hpo_system.sh"
    "setup_hyperparameter_system.sh"
    "setup_pipeline.sh"
    "setup_platform_env.sh"
    "setup_v2_auto_experiments.sh"
    "setup_v3_permissions.sh"
    "recreate_venv.sh"
    "ubuntu_setup.sh"
    "ubuntu_setup_final.sh"
    "create_ubuntu_archive.sh"
    "ubuntu_git_sync.sh"
    "prepare_rerun_v2.sh"
    "final_v3_setup.sh"
    "quick_start_v3.sh"
    "quick_install.py"
    "apply_augmented_data.sh"
    "update_train_data.sh"
    "force_hpo_test.py"
    "quick_hpo.sh"
)

# 4. Permissions 스크립트들 -> temp/permissions/
declare -a PERMISSION_SCRIPTS=(
    "set_all_permissions.sh"
    "set_augmentation_permissions.sh"
    "set_final_permissions.sh"
    "set_permissions.py"
    "set_permissions.sh"
    "set_permissions_cv8u.sh"
    "set_permissions_final.sh"
    "set_permissions_quick.sh"
    "set_setup_permissions.sh"
    "set_v3_permissions.sh"
    "make_executable.sh"
    "make_executable_v2.sh"
    "make_mixup_executable.sh"
    "make_scripts_executable.sh"
)

# 5. Git Commit 스크립트들 -> temp/git_commits/
declare -a GIT_COMMIT_SCRIPTS=(
    "commit_albumentations_fix.sh"
    "commit_cross_platform.sh"
    "commit_cv8u_fix.sh"
    "commit_dependency_fixes.sh"
    "commit_final_fix.sh"
    "commit_numpy_fix.sh"
    "git_commit_changes.sh"
)

# 6. Emergency 스크립트들 -> temp/emergency/
declare -a EMERGENCY_SCRIPTS=(
    "emergency_fix_class8_problem.sh"
    "emergency_fix_python313.sh"
    "run_emergency_fix.sh"
    "run_final_fix.sh"
    "run_ultimate_fix.sh"
)

# 스크립트 이동 함수
move_scripts() {
    local target_dir=$1
    shift
    local scripts=("$@")
    
    log_info "이동 대상: ${target_dir}"
    
    local moved_count=0
    local total_count=${#scripts[@]}
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            mv "$script" "$target_dir/"
            log_success "✓ $script → $target_dir/"
            ((moved_count++))
        else
            log_warning "파일 없음: $script"
        fi
    done
    
    log_info "$target_dir: $moved_count/$total_count 파일 이동 완료"
    echo ""
}

# 이동 시작
log_header "📁 카테고리별 스크립트 이동"

echo "🔍 총 이동 예정 파일 수:"
echo "  - Fix 스크립트: ${#FIX_SCRIPTS[@]}개"
echo "  - Debug/Test 스크립트: ${#DEBUG_TEST_SCRIPTS[@]}개"
echo "  - Install/Setup 스크립트: ${#INSTALL_SETUP_SCRIPTS[@]}개"
echo "  - Permission 스크립트: ${#PERMISSION_SCRIPTS[@]}개"
echo "  - Git Commit 스크립트: ${#GIT_COMMIT_SCRIPTS[@]}개"
echo "  - Emergency 스크립트: ${#EMERGENCY_SCRIPTS[@]}개"
echo ""

echo "⚠️ 진행하면 위 스크립트들이 temp/ 하위 폴더로 이동됩니다."
echo "핵심 실행 스크립트들은 루트에 그대로 유지됩니다."
echo ""

read -p "계속 진행하시겠습니까? (y/N): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    log_warning "작업이 취소되었습니다."
    exit 0
fi

# 1. Fix 스크립트들 이동
move_scripts "temp/fix_scripts" "${FIX_SCRIPTS[@]}"

# 2. Debug/Test 스크립트들 이동
move_scripts "temp/debug_test" "${DEBUG_TEST_SCRIPTS[@]}"

# 3. Install/Setup 스크립트들 이동
move_scripts "temp/install_setup" "${INSTALL_SETUP_SCRIPTS[@]}"

# 4. Permission 스크립트들 이동
move_scripts "temp/permissions" "${PERMISSION_SCRIPTS[@]}"

# 5. Git Commit 스크립트들 이동
move_scripts "temp/git_commits" "${GIT_COMMIT_SCRIPTS[@]}"

# 6. Emergency 스크립트들 이동
move_scripts "temp/emergency" "${EMERGENCY_SCRIPTS[@]}"

# 결과 요약
log_header "📊 정리 결과 요약"

echo "✅ 유지된 핵심 스크립트들:"
for script in "${KEEP_SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        echo "  ✓ $script"
    fi
done

echo ""
echo "📁 temp 디렉토리 구조:"
find temp -type f -name "*.sh" -o -name "*.py" | sort | sed 's/^/  /'

echo ""
log_success "🎉 스크립트 정리 완료!"
echo ""
echo "💡 사용법:"
echo "  - 핵심 스크립트들은 루트에 그대로 유지"
echo "  - 일회성 스크립트들은 temp/ 하위 폴더에 정리"
echo "  - 필요시 temp/에서 다시 루트로 복사 가능"

# README 파일 생성
cat > temp/README.md << 'EOF'
# 📁 Temp 디렉토리 - 정리된 스크립트들

이 디렉토리는 프로젝트 루트에서 정리된 일회성 및 보조 스크립트들을 보관합니다.

## 📂 디렉토리 구조

### `fix_scripts/` - 수정 스크립트들
- 특정 문제 해결을 위한 일회성 수정 스크립트들
- albumentations, opencv, 호환성 관련 수정들
- 대부분 완료된 작업이므로 재사용 가능성 낮음

### `debug_test/` - 디버그 및 테스트 스크립트들
- 시스템 검증 및 호환성 테스트
- 플랫폼 감지 및 환경 점검
- 디버깅 도구들

### `install_setup/` - 설치 및 설정 스크립트들
- 패키지 설치 스크립트들
- 환경 설정 스크립트들
- 플랫폼별 설치 도구들

### `permissions/` - 권한 설정 스크립트들
- 파일 권한 설정
- 실행 가능 권한 부여
- 스크립트 활성화 도구들

### `git_commits/` - Git 커밋 스크립트들
- 자동 커밋 스크립트들
- 변경사항 정리 도구들

### `emergency/` - 응급 수정 스크립트들
- 긴급 문제 해결 스크립트들
- 시스템 복구 도구들

## 🚀 사용 방법

필요한 스크립트가 있다면:
```bash
# temp에서 루트로 복사
cp temp/fix_scripts/fix_something.sh .

# 또는 temp에서 직접 실행
./temp/debug_test/test_something.sh
```

## ⚠️ 주의사항

- 이 스크립트들은 특정 시점의 문제 해결용으로 제작됨
- 현재 시스템과 호환되지 않을 수 있음
- 실행 전 내용을 확인하고 필요시 수정하여 사용
EOF

log_success "📚 temp/README.md 생성 완료"
echo ""
echo "🎯 루트 디렉토리가 깔끔하게 정리되었습니다!"
