#!/usr/bin/env python3
"""
강력한 환경 재구축 스크립트
모든 문제를 한 번에 해결
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description, check=True):
    """명령어 실행"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {e}")
        if e.stderr:
            print(f"   오류: {e.stderr.strip()}")
        return False

def nuclear_fix():
    """핵폭탄급 해결책"""
    
    print("💣 핵폭탄급 환경 재구축")
    print("=" * 50)
    
    project_dir = ""
    os.chdir(project_dir)
    
    # 1. 기존 가상환경 완전 제거
    print("1️⃣ 기존 환경 완전 제거")
    if Path("venv").exists():
        shutil.rmtree("venv")
        print("   ✅ 기존 venv 삭제")
    
    # 2. 새 가상환경 생성 (절대 경로 사용)
    print("\n2️⃣ 새 가상환경 생성")
    run_command("/opt/homebrew/bin/python3.11 -m venv venv", "가상환경 생성")
    
    # 3. pip 업그레이드
    print("\n3️⃣ pip 업그레이드")
    run_command("venv/bin/python -m pip install --upgrade pip", "pip 업그레이드")
    
    # 4. PyTorch 설치 (CPU 버전)
    print("\n4️⃣ PyTorch 설치")
    pytorch_cmd = "venv/bin/python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    run_command(pytorch_cmd, "PyTorch 설치")
    
    # 5. 핵심 패키지 설치
    print("\n5️⃣ 핵심 패키지 설치")
    packages = [
        "timm",
        "wandb", 
        "albumentations",
        "optuna",
        "scikit-learn",
        "pandas",
        "matplotlib",
        "seaborn",
        "pillow",
        "opencv-python",
        "tqdm",
        "pyyaml"
    ]
    
    for package in packages:
        run_command(f"venv/bin/python -m pip install {package}", f"{package} 설치")
    
    # 6. 설치 확인
    print("\n6️⃣ 설치 확인")
    test_cmd = """
venv/bin/python -c "
import torch
import torchvision
import timm
import wandb
import albumentations
import optuna
import sklearn
import pandas
print('🎉 모든 패키지 설치 성공!')
print(f'PyTorch: {torch.__version__}')
print(f'TIMM: {timm.__version__}')
print(f'Python: {torch.cuda.is_available()}')
"
"""
    
    if run_command(test_cmd, "패키지 확인"):
        print("✅ 모든 패키지 정상 작동!")
    
    # 7. 실행 스크립트 생성
    print("\n7️⃣ 실행 스크립트 생성")
    
    script_content = f"""#!/bin/bash
# CV Classification 프로젝트 실행 스크립트

cd {project_dir}

echo "🎯 EfficientNet-B4 실험 시작"
echo "절대 경로로 Python 실행하여 환경 문제 완전 우회"

# 절대 경로로 실행
{project_dir}/venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml
"""
    
    with open("run_experiment.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("run_experiment.sh", 0o755)
    print("   ✅ run_experiment.sh 생성")
    
    # 8. 최종 테스트
    print("\n8️⃣ 최종 테스트")
    final_test = f"{project_dir}/venv/bin/python -c 'import wandb; print(\"✅ wandb 정상!\")'"
    
    if run_command(final_test, "wandb 최종 테스트"):
        print("\n🎉 완벽하게 해결됨!")
        print(f"\n🚀 이제 다음 명령어로 실험 실행:")
        print(f"./run_experiment.sh")
        print(f"\n또는:")
        print(f"{project_dir}/venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml")
        return True
    else:
        print("\n😡 아직도 문제가 있습니다...")
        return False

def show_debug_info():
    """디버그 정보 출력"""
    print("\n🔍 디버그 정보:")
    print("=" * 30)
    
    commands = [
        ("which python", "현재 python 경로"),
        ("python --version", "Python 버전"),
        ("echo $VIRTUAL_ENV", "가상환경 변수"),
        ("ls -la venv/bin/python", "가상환경 python 확인")
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc, check=False)

if __name__ == "__main__":
    print("😤 이번엔 정말 끝장내겠습니다!")
    print("모든 환경을 처음부터 다시 만들어서 완벽하게 해결하겠습니다.")
    print()
    
    if nuclear_fix():
        print("\n✨ 드디어 해결했습니다!")
    else:
        print("\n🔍 추가 디버그 정보를 확인해보세요:")
        show_debug_info()
