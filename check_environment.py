#!/usr/bin/env python3
"""
자동 실험 시스템 빠른 시작 스크립트
필요한 Python 패키지들을 확인하고 설치합니다.
"""

import subprocess
import sys
import pkg_resources
from pathlib import Path


def check_and_install_packages():
    """필요한 패키지들을 확인하고 누락된 것들을 설치"""
    
    required_packages = [
        'numpy',
        'pandas', 
        'matplotlib',
        'seaborn',
        'tqdm',
        'psutil',
        'torch',
        'pyyaml'
    ]
    
    missing_packages = []
    
    print("📦 필요한 패키지들을 확인하는 중...")
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print(f"✅ {package}: 설치됨")
        except pkg_resources.DistributionNotFound:
            print(f"❌ {package}: 누락됨")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\\n📥 누락된 패키지들을 설치합니다: {', '.join(missing_packages)}")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 설치 완료")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 설치 실패")
                return False
    else:
        print("✅ 모든 패키지가 설치되어 있습니다!")
    
    return True


def setup_directory_structure():
    """필요한 디렉토리 구조가 있는지 확인"""
    base_dir = Path("")
    
    required_dirs = [
        "experiments",
        "experiments/configs",
        "experiments/logs", 
        "experiments/submissions"
    ]
    
    print("\\n📁 디렉토리 구조를 확인하는 중...")
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}: 존재함")
        else:
            print(f"❌ {dir_path}: 누락됨")
            return False
    
    print("✅ 모든 디렉토리가 준비되어 있습니다!")
    return True


def check_base_files():
    """기본 파일들이 있는지 확인"""
    base_dir = Path("")
    
    required_files = [
        "codes/gemini_main_v2.py",
        "codes/config_v2.yaml",
        "experiments/experiment_matrix.yaml",
        "experiments/experiment_generator.py",
        "experiments/auto_experiment_runner.py"
    ]
    
    print("\\n📄 필수 파일들을 확인하는 중...")
    
    missing_files = []
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}: 존재함")
        else:
            print(f"❌ {file_path}: 누락됨")
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 일부 필수 파일이 누락되었습니다.")
        return False
    
    print("✅ 모든 필수 파일이 준비되어 있습니다!")
    return True


def main():
    print("🚀 자동 실험 시스템 환경 설정을 시작합니다...")
    print("=" * 60)
    
    # 1. 패키지 확인 및 설치
    if not check_and_install_packages():
        print("❌ 패키지 설치에 실패했습니다.")
        sys.exit(1)
    
    # 2. 디렉토리 구조 확인
    if not setup_directory_structure():
        print("❌ 디렉토리 구조가 올바르지 않습니다.")
        print("   실험 매트릭스 생성을 먼저 실행해주세요:")
        print("   python experiments/experiment_generator.py")
        sys.exit(1)
    
    # 3. 기본 파일들 확인
    if not check_base_files():
        print("❌ 필수 파일들이 누락되었습니다.")
        sys.exit(1)
    
    print("\\n" + "=" * 60)
    print("🎉 환경 설정이 완료되었습니다!")
    print("\\n🎯 다음 단계:")
    print("1. 실험 매트릭스 생성: python experiments/experiment_generator.py")
    print("2. 자동 실험 시작:   python experiments/auto_experiment_runner.py")
    print("3. 실시간 모니터링:   python experiments/experiment_monitor.py")
    print("\\n📖 자세한 사용법: AUTO_EXPERIMENT_GUIDE.md 참조")


if __name__ == "__main__":
    main()
