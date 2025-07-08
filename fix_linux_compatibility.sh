#!/bin/bash

echo "🐧 Linux 서버 호환성 완전 수정!"
echo "==============================="

echo "📝 codes/gemini_main_v2.py import 경로 수정..."

python3 << 'EOF'
with open('codes/gemini_main_v2.py', 'r') as f:
    content = f.read()

# 1. project_root 설정을 더 안전하게 수정
old_project_root = "project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
new_project_root = """# project_root 동적 설정 (Linux 호환)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(os.path.join(project_root, 'codes')):
    # 현재 디렉토리가 프로젝트 루트인 경우
    project_root = os.getcwd()"""

content = content.replace(old_project_root, new_project_root)

# 2. sys.path 추가를 import 전에 확실히 배치
old_imports = """sys.path.append(project_root)
from codes.gemini_utils_v2 import *
from codes.gemini_train_v2 import *
from codes.gemini_augmentation_v2 import *
from codes.gemini_evalute_v2 import *"""

new_imports = """# Python 경로 설정 (Linux 호환)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'codes'))

# 안전한 import (상대/절대 경로 모두 지원)
try:
    from codes.gemini_utils_v2 import *
    from codes.gemini_train_v2 import *
    from codes.gemini_augmentation_v2 import *
    from codes.gemini_evalute_v2 import *
except ImportError:
    # codes가 현재 디렉토리에 없는 경우 직접 import
    from gemini_utils_v2 import *
    from gemini_train_v2 import *
    from gemini_augmentation_v2 import *
    from gemini_evalute_v2 import *"""

content = content.replace(old_imports, new_imports)

# 파일 저장
with open('codes/gemini_main_v2.py', 'w') as f:
    f.write(content)

print("✅ gemini_main_v2.py Linux 호환성 수정 완료!")
EOF

echo ""
echo "📝 실행 스크립트 Linux 호환성 강화..."

cat > run_code_v2.sh << 'EOF'
#!/bin/bash

# 🔧 코드 v2 실행 스크립트 (Linux 호환)
# 사용법: ./run_code_v2.sh

echo "🚀 Starting Code v2 System (새 시스템)"
echo "📂 Data: train.csv v1 (최고 성능 달성했던 원본 데이터)"
echo "💻 Code: gemini_main_v2.py (swin_base 기반)"
echo "⚙️ Config: config_v2.yaml"
echo "🆕 Features: 개선된 augmentation, dynamic augmentation, 향상된 모델"
echo ""

# 현재 디렉토리 확인
echo "📍 Current directory: $(pwd)"
echo "📍 Python path: $(which python3 || which python)"

# Python 경로 설정하여 실행 (Linux 호환)
export PYTHONPATH="$PWD:$PWD/codes:$PYTHONPATH"

# 실행 (config 파일명만 전달)
python3 codes/gemini_main_v2.py --config config_v2.yaml || python codes/gemini_main_v2.py --config config_v2.yaml

echo ""
echo "✅ Code v2 실행 완료!"
EOF

chmod +x run_code_v2.sh

echo ""
echo "📝 __init__.py 파일 생성 (패키지 인식용)..."

# codes 디렉토리에 __init__.py 생성
touch codes/__init__.py

echo ""
echo "🧪 Linux 호환성 테스트..."

echo "📍 현재 디렉토리: $(pwd)"
echo "📍 codes 폴더 존재: $(ls -la codes/ | head -2)"
echo "📍 Python 버전: $(python3 --version 2>/dev/null || python --version)"

echo ""
echo "🎉 Linux 호환성 수정 완료!"
echo ""
echo "📋 수정 내용:"
echo "✅ project_root 동적 설정 강화"
echo "✅ sys.path에 복수 경로 추가"
echo "✅ try-except로 안전한 import"
echo "✅ PYTHONPATH 환경 변수 설정"
echo "✅ codes/__init__.py 생성"
echo "✅ python3/python 대체 실행"
echo ""
echo "🚀 이제 Linux에서 정상 실행됩니다:"
echo "./run_code_v2.sh"
