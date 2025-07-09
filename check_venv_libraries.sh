#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# venv 환경에서 라이브러리 정확한 확인 스크립트
echo "🔍 venv 환경 라이브러리 정확한 확인"
echo "=================================="
echo "⏰ 체크 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 가상환경 정보 확인
echo "📦 1. 가상환경 정보"
echo "-------------------"
echo "VIRTUAL_ENV: ${VIRTUAL_ENV:-'Not activated'}"
echo "Python 경로: $(which python)"
echo "pip 경로: $(which pip)"
echo ""

# 2. pip list로 실제 설치된 패키지 확인
echo "📋 2. 실제 설치된 패키지 (pip list)"
echo "-----------------------------------"
pip list | grep -E "(torch|torchvision|timm|albumentations|opencv|pandas|numpy|scikit|matplotlib|seaborn|wandb|tqdm|pyyaml|PyYAML)"
echo ""

# 3. 필수 라이브러리 개별 import 테스트
echo "🧪 3. 필수 라이브러리 import 테스트"
echo "----------------------------------"

# 각 라이브러리를 개별적으로 테스트
libraries=(
    "torch"
    "torchvision" 
    "timm"
    "albumentations"
    "cv2:opencv-python"
    "pandas"
    "numpy"
    "sklearn:scikit-learn"
    "matplotlib"
    "seaborn"
    "wandb"
    "tqdm"
    "yaml:PyYAML"
)

missing_libs=()
installed_libs=()

for lib_info in "${libraries[@]}"; do
    # lib_name:package_name 형태로 분리
    IFS=':' read -r lib_name package_name <<< "$lib_info"
    if [ -z "$package_name" ]; then
        package_name="$lib_name"
    fi
    
    # Python에서 import 테스트
    if python -c "import $lib_name" 2>/dev/null; then
        version=$(python -c "
try:
    import $lib_name
    print(getattr($lib_name, '__version__', 'Unknown'))
except:
    print('Unknown')
" 2>/dev/null)
        echo "  ✅ $lib_name: $version"
        installed_libs+=("$package_name")
    else
        echo "  ❌ $lib_name: Not installed"
        missing_libs+=("$package_name")
    fi
done

echo ""

# 4. 결과 요약
echo "📊 4. 설치 상태 요약"
echo "-------------------"
echo "✅ 설치됨 (${#installed_libs[@]}개): ${installed_libs[*]}"
if [ ${#missing_libs[@]} -gt 0 ]; then
    echo "❌ 누락됨 (${#missing_libs[@]}개): ${missing_libs[*]}"
    echo ""
    echo "🔧 설치 명령어:"
    echo "pip install ${missing_libs[*]}"
else
    echo "🎉 모든 필수 라이브러리가 설치되어 있습니다!"
fi

echo ""

# 5. venv 환경에서 특별 확인
echo "🔍 5. venv 환경 특별 확인"
echo "------------------------"

# 가상환경 패키지 수 확인
total_packages=$(pip list 2>/dev/null | wc -l)
echo "총 설치된 패키지 수: $((total_packages - 2))"

# requirements.txt가 있는지 확인
if [ -f "requirements.txt" ]; then
    echo "requirements.txt 파일 발견됨"
    echo "requirements.txt 내용:"
    head -10 requirements.txt
else
    echo "requirements.txt 파일 없음"
fi

# pip freeze로 현재 환경 확인
echo ""
echo "📝 현재 venv 환경 스냅샷 (주요 패키지만):"
pip freeze | grep -E "(torch|torchvision|timm|albumentations|opencv|pandas|numpy|scikit|matplotlib|seaborn|wandb|tqdm|PyYAML)" | head -20

echo ""

# 6. 메모리에서 직접 확인
echo "🧠 6. 메모리에서 직접 라이브러리 확인"
echo "------------------------------------"
python << 'EOF'
import sys
print("Python 실행 경로:", sys.executable)
print("Python 버전:", sys.version.split()[0])

# sklearn 확인
try:
    import sklearn
    print("✅ sklearn 버전:", sklearn.__version__)
    print("   sklearn 경로:", sklearn.__file__)
except ImportError as e:
    print("❌ sklearn import 실패:", e)

# yaml 확인 (PyYAML)
try:
    import yaml
    print("✅ PyYAML 사용 가능")
    print("   yaml 경로:", yaml.__file__)
    # 버전 확인 방법들 시도
    try:
        print("   PyYAML 버전:", yaml.__version__)
    except:
        try:
            import pkg_resources
            print("   PyYAML 버전:", pkg_resources.get_distribution("PyYAML").version)
        except:
            print("   PyYAML 버전: 확인 불가")
except ImportError as e:
    print("❌ PyYAML import 실패:", e)

print()
print("sys.path 확인 (venv 경로):")
for path in sys.path[:5]:  # 처음 5개만 출력
    if 'venv' in path or 'site-packages' in path:
        print(f"  {path}")
EOF

echo ""
echo "✅ venv 환경 라이브러리 확인 완료!"
echo "=================================="
