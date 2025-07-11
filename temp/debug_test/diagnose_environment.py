#!/usr/bin/env python3
"""
환경 문제 진단 및 해결 스크립트
"""

import sys
import os
import subprocess

def diagnose_environment():
    """현재 환경 상태 진단"""
    
    print("🔍 Python 환경 진단")
    print("=" * 50)
    
    # 1. Python 경로 확인
    print("1️⃣ Python 실행 경로:")
    print(f"   sys.executable: {sys.executable}")
    print(f"   sys.prefix: {sys.prefix}")
    print(f"   sys.base_prefix: {sys.base_prefix}")
    
    # 2. 가상환경 확인
    print("\n2️⃣ 가상환경 상태:")
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"   ✅ VIRTUAL_ENV: {venv_path}")
    else:
        print("   ❌ VIRTUAL_ENV 환경변수 없음")
    
    in_venv = (
        hasattr(sys, 'real_prefix') or  
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    print(f"   가상환경 활성화: {'✅ Yes' if in_venv else '❌ No'}")
    
    # 3. 설치된 패키지 확인
    print("\n3️⃣ 핵심 패키지 설치 상태:")
    packages_to_check = [
        'torch', 'torchvision', 'timm', 'wandb', 
        'albumentations', 'optuna', 'sklearn', 'pandas'
    ]
    
    installed_packages = []
    missing_packages = []
    
    for package in packages_to_check:
        try:
            __import__(package)
            print(f"   ✅ {package}")
            installed_packages.append(package)
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    # 4. pip 목록 확인
    print("\n4️⃣ pip 패키지 목록 (일부):")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')[:10]  # 처음 10개만
        for line in lines:
            if line.strip():
                print(f"   {line}")
        print("   ...")
    except Exception as e:
        print(f"   ❌ pip list 실행 실패: {e}")
    
    return missing_packages

def fix_environment(missing_packages):
    """환경 문제 해결"""
    
    if not missing_packages:
        print("\n✅ 모든 필수 패키지가 설치되어 있습니다!")
        return True
    
    print(f"\n🔧 누락된 패키지 설치: {missing_packages}")
    
    # 방법 1: 현재 Python으로 직접 설치
    print("\n📦 방법 1: 현재 Python 인터프리터로 설치")
    for package in missing_packages:
        print(f"설치 중: {package}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                          check=True, capture_output=True)
            print(f"   ✅ {package} 설치 완료")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ {package} 설치 실패")
    
    # 재확인
    print("\n🔍 재확인:")
    remaining_missing = []
    for package in missing_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} 여전히 없음")
            remaining_missing.append(package)
    
    if not remaining_missing:
        print("\n🎉 모든 패키지 설치 완료!")
        return True
    else:
        print(f"\n⚠️ 여전히 누락: {remaining_missing}")
        return False

def provide_manual_fix():
    """수동 해결 방법 제공"""
    
    print("\n🛠️ 수동 해결 방법:")
    print("=" * 50)
    
    print("1. 가상환경 재활성화:")
    print("   source venv/bin/activate  # Mac/Linux")
    print("   venv\\Scripts\\activate     # Windows")
    print()
    
    print("2. Python 경로 확인:")
    print("   which python")
    print("   python --version")
    print()
    
    print("3. 강제 재설치:")
    print("   python -m pip install --force-reinstall wandb timm albumentations")
    print()
    
    print("4. 캐시 제거 후 설치:")
    print("   python -m pip install --no-cache-dir wandb timm albumentations")
    print()
    
    print("5. 권한 문제가 있다면:")
    print("   python -m pip install --user wandb timm albumentations")

def main():
    """메인 실행"""
    
    print("🚨 Python 환경 문제 해결")
    print("wandb 모듈을 찾을 수 없는 문제를 진단합니다.")
    print()
    
    # 진단
    missing_packages = diagnose_environment()
    
    # 자동 해결 시도
    if missing_packages:
        success = fix_environment(missing_packages)
        
        if success:
            print("\n🚀 이제 실험을 실행할 수 있습니다:")
            print("python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml")
        else:
            provide_manual_fix()
    else:
        print("\n🤔 패키지는 모두 설치되어 있는데 왜 오류가 날까요?")
        print("아마도 다른 Python 인터프리터를 사용하고 있을 수 있습니다.")
        print()
        print("실행해보세요:")
        print("which python")
        print("python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml")

if __name__ == "__main__":
    main()
