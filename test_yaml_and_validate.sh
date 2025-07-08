#!/bin/bash
# yaml import 테스트 및 사전 검증 재실행

echo "🧪 PyYAML import 테스트..."

cd 

# 가상환경 활성화
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

echo "🐍 Python 버전: $(python --version)"

# yaml import 직접 테스트
echo "📦 yaml import 테스트..."
python -c "
try:
    import yaml
    print(f'✅ yaml import 성공: {yaml.__version__}')
    
    # 간단한 yaml 테스트
    data = {'test': 'value'}
    yaml_str = yaml.dump(data)
    loaded = yaml.safe_load(yaml_str)
    print(f'✅ yaml 기능 테스트 성공: {loaded}')
    
except ImportError as e:
    print(f'❌ yaml import 실패: {e}')
    exit(1)
except Exception as e:
    print(f'❌ yaml 기능 테스트 실패: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ yaml 테스트 성공! 사전 검증 재실행..."
    python pre_experiment_validator.py
else
    echo "❌ yaml 테스트 실패. pip로 직접 설치 시도..."
    pip install --force-reinstall pyyaml==6.0.2
    echo "재설치 후 테스트..."
    python -c "import yaml; print(f'✅ 재설치 성공: {yaml.__version__}')"
    echo "사전 검증 재실행..."
    python pre_experiment_validator.py
fi
