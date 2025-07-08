#!/usr/bin/env python3
"""
가상환경 문제 진단 및 해결
"""

import sys
import subprocess
import os

print("🔍 가상환경 문제 진단")
print("=" * 50)

# 1. 현재 Python 정보
print("현재 Python 정보:")
print(f"  실행 경로: {sys.executable}")
print(f"  버전: {sys.version}")
print(f"  sys.path 개수: {len(sys.path)}")

# 2. 환경 변수 확인
print(f"\n환경 변수:")
print(f"  VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', '없음')}")
print(f"  PATH (첫 번째): {os.environ.get('PATH', '').split(':')[0]}")

# 3. 실제 패키지 설치 위치 확인
try:
    result = subprocess.run([sys.executable, "-m", "pip", "show", "PyYAML"], 
                           capture_output=True, text=True)
    if result.returncode == 0:
        print(f"\nPyYAML 설치 정보:")
        print(result.stdout)
    else:
        print(f"\nPyYAML 설치 정보: 설치되지 않음")
        print(result.stderr)
except Exception as e:
    print(f"\nPyYAML 확인 실패: {e}")

# 4. site-packages 직접 확인
site_packages = None
for path in sys.path:
    if 'site-packages' in path and 'venv' in path:
        site_packages = path
        break

if site_packages:
    print(f"\n가상환경 site-packages: {site_packages}")
    if os.path.exists(site_packages):
        yaml_files = [f for f in os.listdir(site_packages) if 'yaml' in f.lower()]
        print(f"YAML 관련 파일들: {yaml_files}")
    else:
        print("site-packages 디렉토리가 존재하지 않습니다!")
else:
    print("\n가상환경 site-packages를 찾을 수 없습니다!")

# 5. 강제 재설치 시도
print(f"\n🔧 강제 재설치 시도...")
try:
    # 제거
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "PyYAML", "-y"], 
                   capture_output=True)
    print("PyYAML 제거 시도 완료")
    
    # 재설치
    result = subprocess.run([sys.executable, "-m", "pip", "install", "PyYAML"], 
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ PyYAML 재설치 성공")
    else:
        print(f"❌ PyYAML 재설치 실패: {result.stderr}")
        
except Exception as e:
    print(f"재설치 중 오류: {e}")

# 6. 최종 테스트
print(f"\n🧪 최종 import 테스트:")
try:
    import yaml
    print(f"✅ PyYAML import 성공: {yaml.__version__}")
except ImportError as e:
    print(f"❌ PyYAML import 여전히 실패: {e}")
    
    # 대안 시도
    print("\n🔍 대안 확인:")
    try:
        import ruamel.yaml as yaml
        print("⚠️ ruamel.yaml을 대신 사용할 수 있습니다")
    except ImportError:
        print("❌ 대안도 없습니다")

print(f"\n🎯 권장 해결책:")
print("1. 가상환경 완전 재생성:")
print("   deactivate")
print("   rm -rf venv")
print("   python3 -m venv venv")
print("   source venv/bin/activate")
print("   python -m pip install PyYAML")
print("")
print("2. 또는 conda 사용:")
print("   conda create -n cv-hpo python=3.11")
print("   conda activate cv-hpo") 
print("   conda install -c conda-forge pyyaml")
