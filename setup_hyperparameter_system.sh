#!/bin/bash

# 확장 가능한 하이퍼파라미터 실험 시스템 실행 권한 설정
echo "🔧 확장 가능한 하이퍼파라미터 실험 시스템 권한 설정"

# 실행 권한 부여
chmod +x hyperparameter_system/run_experiments.py
chmod +x hyperparameter_system/experiment_runner.py
chmod +x hyperparameter_system/hyperparameter_configs.py

echo "✅ 권한 설정 완료"

# 필요한 디렉토리 생성
mkdir -p hyperparameter_system/temp_configs

echo "📁 임시 설정 디렉토리 생성 완료"

# 시스템 테스트
echo "🚀 시스템 테스트 실행..."

cd hyperparameter_system
python hyperparameter_configs.py

echo ""
echo "🎊 확장 가능한 하이퍼파라미터 실험 시스템 구축 완료!"
echo ""
echo "📋 실행 방법:"
echo "   python hyperparameter_system/run_experiments.py"
echo ""
echo "📊 명령줄 실행:"
echo "   python hyperparameter_system/experiment_runner.py --matrix"
echo "   python hyperparameter_system/experiment_runner.py --models efficientnet_b4.ra2_in1k"
echo "   python hyperparameter_system/experiment_runner.py --categories optimizer loss_function"
