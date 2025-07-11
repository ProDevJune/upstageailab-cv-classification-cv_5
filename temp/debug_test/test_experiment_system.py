#!/usr/bin/env python3
"""
자동 실험 시스템 테스트 스크립트
모든 컴포넌트가 정상 작동하는지 확인합니다.
"""

import sys
import os
from pathlib import Path
import subprocess
import importlib.util

def test_file_exists(file_path: str, description: str):
    """파일 존재 여부 확인"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (파일 없음)")
        return False

def test_python_syntax(file_path: str, description: str):
    """Python 파일 문법 확인"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {description}: 문법 검사 통과")
        return True
    except Exception as e:
        print(f"❌ {description}: 문법 오류 - {e}")
        return False

def test_directory_structure():
    """디렉토리 구조 확인"""
    base_dir = ""
    
    required_dirs = [
        "experiments",
        "experiments/configs",
        "experiments/logs", 
        "experiments/submissions"
    ]
    
    print("🔍 디렉토리 구조 확인")
    print("-" * 40)
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = Path(base_dir) / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (디렉토리 없음)")
            all_ok = False
    
    return all_ok

def test_core_files():
    """핵심 파일들 존재 확인"""
    base_dir = ""
    
    core_files = [
        ("experiments/experiment_matrix.yaml", "실험 매트릭스"),
        ("experiments/experiment_generator.py", "실험 생성기"),
        ("experiments/auto_experiment_runner.py", "자동 실험 실행기"),
        ("experiments/submission_manager.py", "제출 관리자"),
        ("experiments/results_analyzer.py", "결과 분석기"),
        ("experiments/experiment_monitor.py", "모니터링 대시보드"),
        ("codes/gemini_main_v2.py", "메인 스크립트"),
        ("codes/config_v2.yaml", "기본 설정 파일")
    ]
    
    print("\n🔍 핵심 파일 확인")
    print("-" * 40)
    
    all_ok = True
    for file_path, description in core_files:
        full_path = Path(base_dir) / file_path
        if not test_file_exists(str(full_path), description):
            all_ok = False
    
    return all_ok

def test_python_files():
    """Python 파일들 문법 확인"""
    base_dir = ""
    
    python_files = [
        ("experiments/experiment_generator.py", "실험 생성기"),
        ("experiments/auto_experiment_runner.py", "자동 실험 실행기"), 
        ("experiments/submission_manager.py", "제출 관리자"),
        ("experiments/results_analyzer.py", "결과 분석기"),
        ("experiments/experiment_monitor.py", "모니터링 대시보드")
    ]
    
    print("\n🔍 Python 파일 문법 검사")
    print("-" * 40)
    
    all_ok = True
    for file_path, description in python_files:
        full_path = Path(base_dir) / file_path
        if full_path.exists():
            if not test_python_syntax(str(full_path), description):
                all_ok = False
        else:
            all_ok = False
    
    return all_ok

def test_dependencies():
    """필요한 패키지 확인"""
    required_packages = [
        "torch",
        "yaml", 
        "numpy",
        "pandas",
        "psutil",
        "tqdm"
    ]
    
    print("\n🔍 필수 패키지 확인")
    print("-" * 40)
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (설치 필요)")
            all_ok = False
    
    return all_ok

def test_experiment_generator():
    """실험 생성기 테스트"""
    print("\n🔍 실험 생성기 테스트")
    print("-" * 40)
    
    base_dir = ""
    script_path = Path(base_dir) / "experiments" / "experiment_generator.py"
    
    try:
        # Dry run 모드로 테스트
        result = subprocess.run([
            sys.executable, str(script_path), "--dry-run"
        ], capture_output=True, text=True, cwd=base_dir, timeout=30)
        
        if result.returncode == 0:
            print("✅ 실험 생성기 dry-run 성공")
            return True
        else:
            print(f"❌ 실험 생성기 실패: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 실험 생성기 테스트 실패: {e}")
        return False

def run_full_test():
    """전체 테스트 실행"""
    print("🧪 자동 실험 시스템 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("디렉토리 구조", test_directory_structure),
        ("핵심 파일", test_core_files),
        ("Python 문법", test_python_files),
        ("필수 패키지", test_dependencies),
        ("실험 생성기", test_experiment_generator)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {e}")
            results.append((test_name, False))
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("🏁 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"전체 테스트: {passed}/{total} 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 모든 테스트가 통과했습니다!")
        print("자동 실험 시스템이 정상적으로 구성되었습니다.")
        print("\n📋 다음 단계:")
        print("1. python experiments/experiment_generator.py")
        print("2. python experiments/auto_experiment_runner.py")
    else:
        print("\n⚠️  일부 테스트가 실패했습니다.")
        print("실패한 항목들을 수정한 후 다시 테스트해주세요.")
        return False
    
    return True

if __name__ == "__main__":
    success = run_full_test()
    sys.exit(0 if success else 1)
