#!/usr/bin/env python3
"""
AIStages 대회 간편 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    print("🎯 AIStages 대회 관리 시스템 실행")
    
    # Python 경로 확인
    python_cmd = sys.executable
    
    # aistages_manager.py 실행
    script_path = os.path.join(os.path.dirname(__file__), 'aistages_manager.py')
    
    try:
        subprocess.run([python_cmd, script_path] + sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 실행 실패: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 사용자가 중단했습니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
