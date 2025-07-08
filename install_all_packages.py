#!/usr/bin/env python3
"""
CV Classification 프로젝트 필수 패키지 설치 스크립트
"""

import subprocess
import sys
import os

def run_command(command, description):
    """명령어 실행 및 결과 확인"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 실패:")
        print(f"   오류: {e.stderr}")
        return False

def install_packages():
    """필수 패키지 설치"""
    
    print("🎯 CV Classification 프로젝트 패키지 설치 시작")
    print("=" * 60)
    
    # 기본 패키지 업그레이드
    packages = [
        ("pip install --upgrade pip", "pip 업그레이드"),
        ("pip install wheel setuptools", "기본 도구 설치"),
        
        # 핵심 머신러닝 패키지
        ("pip install torch torchvision torchaudio", "PyTorch 설치"),
        ("pip install timm", "timm (PyTorch Image Models) 설치"),
        
        # 데이터 처리
        ("pip install pandas numpy", "데이터 처리 패키지"),
        ("pip install scikit-learn", "scikit-learn 설치"),
        
        # 시각화
        ("pip install matplotlib seaborn", "시각화 패키지"),
        ("pip install plotly", "plotly 설치"),
        
        # 이미지 처리
        ("pip install Pillow opencv-python", "이미지 처리 패키지"),
        ("pip install albumentations", "데이터 증강 패키지"),
        
        # HPO 관련
        ("pip install optuna", "Optuna HPO 패키지"),
        ("pip install wandb", "WandB 실험 추적"),
        
        # 유틸리티
        ("pip install tqdm", "진행률 표시"),
        ("pip install pyyaml", "YAML 처리"),
        ("pip install jsonlines", "JSON Lines"),
        
        # Jupyter 환경 (선택사항)
        ("pip install jupyter notebook ipywidgets", "Jupyter 환경"),
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for command, description in packages:
        if run_command(command, description):
            success_count += 1
        print()  # 빈 줄
    
    print("=" * 60)
    print(f"📊 설치 완료: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 모든 패키지 설치 성공!")
        return True
    else:
        print("⚠️ 일부 패키지 설치 실패. 개별적으로 설치해보세요.")
        return False

def verify_installation():
    """설치 확인"""
    print("\n🔍 설치 확인 중...")
    
    test_imports = [
        ("torch", "PyTorch"),
        ("torchvision", "TorchVision"),
        ("timm", "TIMM"),
        ("sklearn", "Scikit-learn"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
        ("PIL", "Pillow"),
        ("cv2", "OpenCV"),
        ("albumentations", "Albumentations"),
        ("optuna", "Optuna"),
        ("tqdm", "TQDM"),
        ("yaml", "PyYAML"),
    ]
    
    success_imports = 0
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
            success_imports += 1
        except ImportError:
            print(f"❌ {name} - 설치 필요")
    
    print(f"\n📊 임포트 성공: {success_imports}/{len(test_imports)}")
    
    if success_imports == len(test_imports):
        print("🎉 모든 패키지 정상 작동!")
        
        # 버전 정보 출력
        try:
            import torch
            import timm
            import sklearn
            print(f"\n📋 주요 패키지 버전:")
            print(f"   PyTorch: {torch.__version__}")
            print(f"   TIMM: {timm.__version__}")
            print(f"   Scikit-learn: {sklearn.__version__}")
            
            # GPU 확인
            if torch.cuda.is_available():
                print(f"   CUDA: {torch.version.cuda}")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                print(f"   MPS: Available (Apple Silicon)")
            else:
                print(f"   Device: CPU only")
                
        except:
            pass
            
        return True
    else:
        return False

def main():
    """메인 실행"""
    print("🎯 CV Classification 환경 설정")
    print("이 스크립트는 필요한 모든 패키지를 설치합니다.")
    print()
    
    # 가상환경 확인 (더 정확한 방법)
    in_venv = (
        hasattr(sys, 'real_prefix') or  # virtualenv
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or  # venv
        os.environ.get('VIRTUAL_ENV') is not None or  # 환경변수 확인
        os.environ.get('CONDA_DEFAULT_ENV') is not None  # conda 환경
    )
    
    if in_venv:
        print("✅ 가상환경에서 실행 중")
        venv_path = os.environ.get('VIRTUAL_ENV', 'Unknown')
        print(f"   환경 경로: {venv_path}")
    else:
        print("⚠️ 가상환경이 감지되지 않았습니다.")
        print(f"   Python 경로: {sys.executable}")
        print(f"   Base prefix: {sys.base_prefix}")
        print(f"   Prefix: {sys.prefix}")
        print("계속하시겠습니까? (y/N): ", end="")
        if input().lower() != 'y':
            print("설치 중단됨")
            return
    
    # 패키지 설치
    if install_packages():
        verify_installation()
        
        print("\n🚀 다음 단계:")
        print("1. python aistages_manager.py  # 메인 시스템 실행")
        print("2. 메뉴 2번으로 기존 실험 확인")
        print("3. 메뉴 1번으로 새 HPO 실험 실행")
        
    else:
        print("\n🔧 수동 설치가 필요한 경우:")
        print("pip install torch torchvision timm scikit-learn pandas matplotlib")

if __name__ == "__main__":
    main()
