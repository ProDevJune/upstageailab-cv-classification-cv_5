#!/usr/bin/env python3
"""
🗂️ CV 분류 프로젝트 스크립트 정리 및 이동 (Python 버전)
루트에 있는 일회성 스크립트들을 temp 폴더로 체계적으로 이동
"""

import os
import shutil
from pathlib import Path

# 색상 코드
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

def log_header(msg):
    print(f"\n{Colors.PURPLE}=== {msg} ==={Colors.NC}")

# 프로젝트 루트 경로
PROJECT_ROOT = "/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5"

# 유지할 핵심 스크립트들
KEEP_SCRIPTS = {
    "run_experiments.sh",
    "setup_venv.sh", 
    "activate_venv.sh",
    "run_full_pipeline.sh",
    "run_ensemble.sh",
    "cleanup.sh",
    "run_b3.sh",
    "run_convnext.sh", 
    "run_absolute.sh",
    "run_v2_experiments.sh",
    "run_experiment.sh",
    "run_experiment_fixed.sh",
    "cleanup_cache.sh",
    "cleanup_deep.sh",
    "cleanup_git_scripts.sh",
    "run_all_priority.sh",
    "run_code_v1.sh",
    "run_code_v2.sh",
    "run_my_configs.sh",
    "run_setup.sh"
}

# 이동할 스크립트들 (카테고리별) - 처음 20개만 테스트
MOVE_SCRIPTS = {
    "temp/fix_scripts": [
        "fix_aistages_paths.sh", "fix_albumentations.sh", "fix_albumentations_api.sh",
        "fix_all_and_test.sh", "fix_and_test_complete.sh", "fix_augmentation_immediate.sh",
        "fix_complete_compatibility.sh", "fix_config_access.sh", "fix_config_data_dir.sh",
        "fix_convnext_rerun.sh"
    ],
    
    "temp/debug_test": [
        "debug_v2_experiment.sh", "check_aistages_path_compatibility.sh", "check_aistages_system.sh",
        "check_experiment_stability.sh", "check_ml_compatibility.sh", "quick_check.sh",
        "quick_safety_check.sh", "final_validation.sh"
    ],
    
    "temp/permissions": [
        "set_all_permissions.sh", "set_permissions.sh", "make_executable.sh",
        "make_scripts_executable.sh"
    ]
}

def ensure_temp_directories():
    """temp 디렉토리 구조 생성"""
    temp_dirs = [
        "temp/fix_scripts",
        "temp/debug_test", 
        "temp/install_setup",
        "temp/permissions",
        "temp/git_commits",
        "temp/emergency"
    ]
    
    for dir_path in temp_dirs:
        full_path = Path(PROJECT_ROOT) / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        log_success(f"디렉토리 준비: {dir_path}")

def move_scripts():
    """스크립트들을 카테고리별로 이동"""
    os.chdir(PROJECT_ROOT)
    
    total_moved = 0
    total_checked = 0
    
    for target_dir, scripts in MOVE_SCRIPTS.items():
        log_info(f"처리 중: {target_dir}")
        moved_count = 0
        
        for script in scripts:
            total_checked += 1
            source_path = Path(script)
            target_path = Path(target_dir) / script
            
            if source_path.exists():
                try:
                    shutil.move(str(source_path), str(target_path))
                    print(f"  ✓ {script} → {target_dir}/")
                    moved_count += 1
                    total_moved += 1
                except Exception as e:
                    log_warning(f"이동 실패: {script} - {e}")
            else:
                print(f"  • {script} (파일 없음)")
        
        log_info(f"{target_dir}: {moved_count}개 파일 이동 완료\n")
    
    return total_moved, total_checked

def main():
    """메인 함수"""
    log_header("🗂️ CV 분류 프로젝트 스크립트 정리 시작")
    
    # 현재 디렉토리 확인
    if not Path(PROJECT_ROOT).exists():
        log_error(f"프로젝트 디렉토리를 찾을 수 없습니다: {PROJECT_ROOT}")
        return
    
    # 작업 개요 출력
    total_scripts = sum(len(scripts) for scripts in MOVE_SCRIPTS.values())
    print(f"\n🔍 작업 개요 (테스트 버전):")
    print(f"  • 이동할 스크립트: {total_scripts}개")
    print(f"  • 유지할 핵심 스크립트: {len(KEEP_SCRIPTS)}개")
    
    # temp 디렉토리 구조 생성
    log_header("📁 디렉토리 구조 생성")
    ensure_temp_directories()
    
    # 스크립트 이동
    log_header("🚀 스크립트 이동 작업")
    total_moved, total_checked = move_scripts()
    
    # 결과 요약
    log_header("📊 정리 결과 요약")
    print(f"✅ 총 {total_moved}/{total_checked}개 파일 이동 완료")
    
    log_success("\n🎉 스크립트 정리 완료!")

if __name__ == "__main__":
    main()
