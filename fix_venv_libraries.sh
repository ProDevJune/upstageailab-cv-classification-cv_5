#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# venv 환경 진단 및 수정 스크립트
echo "🔧 venv 환경 진단 및 자동 수정"
echo "============================="
echo "⏰ 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 현재 환경 확인
echo "📦 1. 현재 venv 환경 상태"
echo "-------------------------"
echo "가상환경: ${VIRTUAL_ENV:-'Not activated'}"
echo "Python: $(which python)"
echo "pip: $(which pip)"
echo ""

# 2. 누락된 라이브러리만 선별 설치
echo "🔍 2. 누락된 라이브러리 확인 및 설치"
echo "-----------------------------------"

# 확인할 라이브러리 목록
declare -A required_libs=(
    ["sklearn"]="scikit-learn"
    ["yaml"]="PyYAML"
)

missing_packages=()

for import_name in "${!required_libs[@]}"; do
    package_name="${required_libs[$import_name]}"
    
    echo -n "확인 중: $import_name ... "
    
    if python -c "import $import_name" 2>/dev/null; then
        version=$(python -c "
try:
    import $import_name
    print(getattr($import_name, '__version__', 'Unknown'))
except:
    print('Unknown')
" 2>/dev/null)
        echo "✅ 설치됨 ($version)"
    else
        echo "❌ 누락"
        missing_packages+=("$package_name")
    fi
done

# 3. 누락된 패키지 자동 설치
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo ""
    echo "🚀 3. 누락된 패키지 자동 설치"
    echo "-----------------------------"
    echo "설치할 패키지: ${missing_packages[*]}"
    
    for package in "${missing_packages[@]}"; do
        echo ""
        echo "📥 $package 설치 중..."
        
        # pip install 실행
        if pip install "$package"; then
            echo "✅ $package 설치 완료"
        else
            echo "❌ $package 설치 실패"
            
            # 대안 시도
            echo "🔄 대안 방법 시도..."
            if pip install --user "$package"; then
                echo "✅ $package 설치 완료 (--user 옵션)"
            else
                echo "❌ $package 설치 실패 (모든 방법)"
            fi
        fi
    done
    
    echo ""
    echo "🔄 4. 설치 후 재확인"
    echo "-------------------"
    
    for import_name in "${!required_libs[@]}"; do
        package_name="${required_libs[$import_name]}"
        
        echo -n "재확인: $import_name ... "
        
        if python -c "import $import_name" 2>/dev/null; then
            version=$(python -c "
try:
    import $import_name
    print(getattr($import_name, '__version__', 'Unknown'))
except:
    print('Unknown')
" 2>/dev/null)
            echo "✅ $version"
        else
            echo "❌ 여전히 누락"
        fi
    done
    
else
    echo ""
    echo "🎉 모든 필수 라이브러리가 이미 설치되어 있습니다!"
fi

echo ""

# 5. 최종 종합 테스트
echo "🧪 5. 최종 종합 Import 테스트"
echo "-----------------------------"

python << 'EOF'
print("프로젝트 실행을 위한 최종 import 테스트:")
print("=" * 40)

essential_imports = [
    ('torch', 'PyTorch'),
    ('torchvision', 'TorchVision'),
    ('timm', 'TIMM'), 
    ('albumentations', 'Albumentations'),
    ('cv2', 'OpenCV'),
    ('pandas', 'Pandas'),
    ('numpy', 'NumPy'),
    ('sklearn', 'Scikit-learn'),
    ('matplotlib', 'Matplotlib'),
    ('seaborn', 'Seaborn'),
    ('wandb', 'Weights & Biases'),
    ('tqdm', 'TQDM'),
    ('yaml', 'PyYAML')
]

success_count = 0
total_count = len(essential_imports)

for module, name in essential_imports:
    try:
        __import__(module)
        version = getattr(__import__(module), '__version__', 'Unknown')
        print(f"✅ {name}: {version}")
        success_count += 1
    except ImportError as e:
        print(f"❌ {name}: Import 실패 - {e}")

print("=" * 40)
print(f"결과: {success_count}/{total_count} 라이브러리 사용 가능")

if success_count == total_count:
    print("🎉 모든 라이브러리 import 성공! 프로젝트 실행 준비 완료!")
else:
    print("⚠️  일부 라이브러리가 누락되었습니다. 수동 설치가 필요할 수 있습니다.")
    
print()
print("🚀 프로젝트 실행 권장 명령어:")
print("   V2_2 빠른 테스트: ./run_v2_2_only.sh")
print("   V2_1 최고 성능: ./run_v2_1_only.sh")
print("   V3 계층적 분류: python v3_experiment_generator.py --phase phase1")
EOF

echo ""
echo "✅ venv 환경 진단 및 수정 완료!"
echo "==============================="
echo "⏰ 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
