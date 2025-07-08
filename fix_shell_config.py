#!/usr/bin/env python3
"""
Shell 설정 자동 수정 스크립트
가상환경 친화적으로 .zshrc 설정 변경
"""

import os
import shutil
from pathlib import Path

def backup_zshrc():
    """기존 .zshrc 백업"""
    home = Path.home()
    zshrc_path = home / '.zshrc'
    backup_path = home / '.zshrc.backup'
    
    if zshrc_path.exists():
        shutil.copy2(zshrc_path, backup_path)
        print(f"✅ 기존 .zshrc 백업 완료: {backup_path}")
        return True
    return False

def fix_zshrc():
    """가상환경 친화적으로 .zshrc 수정"""
    
    home = Path.home()
    zshrc_path = home / '.zshrc'
    
    if not zshrc_path.exists():
        print("❌ .zshrc 파일이 없습니다.")
        return False
    
    # 기존 내용 읽기
    with open(zshrc_path, 'r') as f:
        content = f.read()
    
    # 문제되는 줄들 주석 처리
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        # Python alias와 PATH 설정 주석 처리
        if any(pattern in line for pattern in [
            'alias python=',
            'alias python3=', 
            'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"'
        ]):
            if not line.strip().startswith('#'):
                modified_lines.append(f"# (가상환경 친화적으로 주석 처리) {line}")
                print(f"🔧 주석 처리: {line}")
            else:
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    # 가상환경 친화적 설정 추가
    venv_friendly_config = """

# ================================
# 가상환경 친화적 Python 설정
# ================================

# Python 경로를 PATH에 추가하되 가상환경이 우선하도록 설정
export PATH="$PATH:/opt/homebrew/opt/python@3.11/bin"

# 가상환경이 활성화된 경우에만 시스템 Python 사용을 허용하는 함수
python_smart() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        # 가상환경 활성화시 가상환경의 python 사용
        "$VIRTUAL_ENV/bin/python" "$@"
    else
        # 가상환경 비활성화시 시스템 python 사용
        /opt/homebrew/bin/python3.11 "$@"
    fi
}

# 선택적 alias 설정 (필요시 주석 해제)
# alias python=python_smart
# alias python3=python_smart

# 가상환경 활성화시 python 명령어 체크 함수
check_python_env() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        echo "🐍 가상환경 활성화됨: $(basename $VIRTUAL_ENV)"
        echo "Python 경로: $(which python)"
    else
        echo "🌍 시스템 Python 사용 중"
        echo "Python 경로: $(which python)"
    fi
}

# 편의 alias
alias penv="check_python_env"
"""
    
    # 설정이 이미 있는지 확인
    if "가상환경 친화적 Python 설정" not in content:
        modified_lines.append(venv_friendly_config)
        print("✅ 가상환경 친화적 설정 추가")
    
    # 파일에 쓰기
    with open(zshrc_path, 'w') as f:
        f.write('\n'.join(modified_lines))
    
    return True

def create_activation_helper():
    """가상환경 활성화 도우미 스크립트 생성"""
    
    script_content = '''#!/bin/bash
# CV Classification 프로젝트 가상환경 활성화 스크립트

cd 

echo "🎯 CV Classification 프로젝트 가상환경 활성화"

# 가상환경 활성화
source venv/bin/activate

# Python 경로 확인
echo "✅ Python 경로: $(which python)"
echo "✅ Pip 경로: $(which pip)"

# 패키지 확인
python -c "import wandb, timm, torch; print('✅ 주요 패키지 정상')" 2>/dev/null || echo "⚠️ 패키지 재설치 필요"

echo ""
echo "🚀 실험 실행 예시:"
echo "python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml"
echo ""
echo "📊 환경 확인: penv"
'''
    
    script_path = Path.home() / 'activate_cv_project.sh'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # 실행 권한 부여
    os.chmod(script_path, 0o755)
    
    print(f"✅ 활성화 도우미 생성: {script_path}")
    print("사용법: source ~/activate_cv_project.sh")

def main():
    """메인 실행"""
    
    print("🔧 Shell 설정 근본 수정")
    print("=" * 50)
    
    # 1. 백업
    backup_zshrc()
    
    # 2. .zshrc 수정
    if fix_zshrc():
        print("✅ .zshrc 수정 완료")
    
    # 3. 활성화 도우미 생성
    create_activation_helper()
    
    print("\n🎯 적용 방법:")
    print("1. 새 터미널 열기 또는:")
    print("   source ~/.zshrc")
    print()
    print("2. 가상환경 활성화:")
    print("   cd ")
    print("   source venv/bin/activate")
    print()
    print("3. 또는 편리한 활성화:")
    print("   source ~/activate_cv_project.sh")
    print()
    print("4. 실험 실행:")
    print("   python codes/gemini_main.py --config codes/practice/exp_golden_efficientnet_b4_202507051902.yaml")
    
    print("\n⚠️ 변경 사항:")
    print("- 기존 python alias 주석 처리")
    print("- 가상환경 우선 PATH 설정")
    print("- 편의 함수 및 alias 추가")

if __name__ == "__main__":
    main()
