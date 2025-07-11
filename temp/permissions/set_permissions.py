#!/usr/bin/env python3
"""
모든 스크립트 파일의 실행 권한을 설정합니다.
"""

import os
import stat
from pathlib import Path


def make_executable(file_path):
    """파일을 실행 가능하게 만들기"""
    try:
        current_permissions = os.stat(file_path).st_mode
        os.chmod(file_path, current_permissions | stat.S_IEXEC)
        return True
    except Exception as e:
        print(f"❌ 권한 설정 실패 {file_path}: {e}")
        return False


def main():
    base_dir = Path("")
    
    # 실행 권한을 설정할 파일들
    script_files = [
        "experiments/experiment_generator.py",
        "experiments/auto_experiment_runner.py", 
        "experiments/submission_manager.py",
        "experiments/results_analyzer.py",
        "experiments/experiment_monitor.py",
        "check_environment.py",
        "setup_experiments.sh"
    ]
    
    print("🔧 스크립트 파일들의 실행 권한을 설정합니다...")
    print()
    
    success_count = 0
    for script in script_files:
        file_path = base_dir / script
        if file_path.exists():
            if make_executable(file_path):
                print(f"✅ {script}")
                success_count += 1
            else:
                print(f"❌ {script}")
        else:
            print(f"⚠️  {script}: 파일이 존재하지 않음")
    
    print()
    print(f"🎉 {success_count}개 파일의 실행 권한 설정 완료!")
    print()
    print("🚀 이제 다음 명령어로 시작할 수 있습니다:")
    print("   python check_environment.py")
    print("   python experiments/experiment_generator.py")


if __name__ == "__main__":
    main()
