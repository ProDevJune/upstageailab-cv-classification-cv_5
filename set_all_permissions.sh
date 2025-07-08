#!/bin/bash

# 모든 스크립트 파일에 실행 권한 부여
echo "🔧 실행 권한 설정 중..."

chmod +x setup_platform_env.sh
chmod +x setup_and_validate_all.sh
chmod +x setup_experiments.sh
chmod +x run_setup.sh

chmod +x experiments/experiment_generator.py
chmod +x experiments/auto_experiment_runner.py
chmod +x experiments/submission_manager.py
chmod +x experiments/results_analyzer.py
chmod +x experiments/experiment_monitor.py

chmod +x pre_experiment_validator.py
chmod +x check_environment.py
chmod +x set_permissions.py

echo "✅ 모든 파일 실행 권한 설정 완료!"
