#!/usr/bin/env python3
"""
HPO 시스템 실행 가이드
실제 실험을 단계별로 실행
"""

import sys
import os
import subprocess

print("🎯 HPO 시스템 실행 가이드")
print("=" * 50)

def run_command(cmd, description):
    print(f"\n📋 {description}")
    print(f"명령어: {cmd}")
    print("-" * 30)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 성공!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 실패!")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    print("🚀 시작 옵션을 선택하세요:")
    print("1) 📊 플랫폼 정보 확인")
    print("2) ⚡ 빠른 HPO 실험 (5개)")
    print("3) 🔬 중간 HPO 실험 (10개)")
    print("4) 📈 실험 결과 확인")
    print("5) 🎨 결과 시각화")
    print("0) 종료")
    
    choice = input("\n선택 (0-5): ").strip()
    
    if choice == "1":
        run_command("python test_hpo_system.py", "플랫폼 정보 확인")
        
    elif choice == "2":
        print("\n⚡ 빠른 HPO 실험 시작...")
        print("5개 실험, 약 10분 소요 예상")
        confirm = input("계속하시겠습니까? (y/N): ")
        if confirm.lower() == 'y':
            run_command("python codes/auto_experiment_basic.py --type quick --max 5", 
                       "빠른 HPO 실험 실행")
    
    elif choice == "3":
        print("\n🔬 중간 HPO 실험 시작...")
        print("10개 실험, 약 20분 소요 예상")
        confirm = input("계속하시겠습니까? (y/N): ")
        if confirm.lower() == 'y':
            run_command("python codes/auto_experiment_basic.py --type quick --max 10", 
                       "중간 HPO 실험 실행")
    
    elif choice == "4":
        run_command("python codes/experiment_tracker.py --action summary", 
                   "실험 결과 요약")
        run_command("python codes/experiment_tracker.py --action top --n 5", 
                   "상위 5개 실험")
    
    elif choice == "5":
        run_command("python codes/experiment_tracker.py --action visualize", 
                   "결과 시각화 생성")
    
    elif choice == "0":
        print("👋 시스템 종료")
        return
    
    else:
        print("❌ 잘못된 선택")
    
    # 다시 메뉴 표시
    print("\n" + "="*50)
    again = input("다른 작업을 하시겠습니까? (y/N): ")
    if again.lower() == 'y':
        main()

if __name__ == "__main__":
    # 기본 환경 확인
    print("🔍 환경 확인 중...")
    
    # 필수 파일 확인
    required_files = [
        "codes/auto_experiment_basic.py",
        "codes/experiment_tracker.py", 
        "test_hpo_system.py"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 필수 파일이 없습니다: {missing_files}")
        sys.exit(1)
    
    print("✅ 환경 확인 완료")
    
    # 메인 실행
    main()
