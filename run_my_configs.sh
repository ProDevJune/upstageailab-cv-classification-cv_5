#!/bin/bash

# Custom Config Runner - 사용자 정의 YAML 파일들을 순차 실행

echo "🎯 Custom Config Sequential Runner"
echo "=================================="

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 도움말 함수
show_help() {
    echo "사용법:"
    echo "  $0 [옵션]"
    echo ""
    echo "📋 기본 사용법:"
    echo "  $0                          # my_configs/ 폴더의 모든 .yaml 파일 실행"
    echo "  $0 --create-samples         # 샘플 config 파일들 생성"
    echo "  $0 --create-order          # 실행 순서 파일 생성"
    echo "  $0 --dry-run               # 실행 예정 파일들 미리보기"
    echo ""
    echo "🔧 고급 옵션:"
    echo "  $0 --single config.yaml    # 특정 config 파일 하나만 실행"
    echo "  $0 --pattern 'exp_*.yaml'  # 특정 패턴의 파일들만 실행"
    echo "  $0 --config-dir other_dir  # 다른 디렉토리의 config 파일들 실행"
    echo ""
    echo "📁 디렉토리 구조:"
    echo "  my_configs/"
    echo "  ├── my_experiment_1.yaml   # 사용자 정의 실험 1"
    echo "  ├── my_experiment_2.yaml   # 사용자 정의 실험 2"
    echo "  ├── my_experiment_3.yaml   # 사용자 정의 실험 3"
    echo "  ├── execution_order.txt    # 실행 순서 (선택사항)"
    echo "  ├── logs/                  # 실행 로그들"
    echo "  └── results/               # 실험 결과들"
    echo ""
    echo "⚡ 빠른 시작:"
    echo "  1. $0 --create-samples     # 샘플 파일 생성"
    echo "  2. my_configs/ 폴더에서 .yaml 파일들 편집"
    echo "  3. $0                      # 실행!"
}

# 인수 처리
if [[ $# -eq 0 ]]; then
    # 기본 실행
    python custom_config_runner.py
elif [[ $1 == "--help" || $1 == "-h" ]]; then
    show_help
elif [[ $1 == "--create-samples" ]]; then
    python custom_config_runner.py --create-samples
elif [[ $1 == "--create-order" ]]; then
    python custom_config_runner.py --create-order
elif [[ $1 == "--dry-run" ]]; then
    python custom_config_runner.py --dry-run
elif [[ $1 == "--single" ]]; then
    if [[ -z $2 ]]; then
        echo "❌ Error: --single requires a config filename"
        echo "Usage: $0 --single my_experiment.yaml"
        exit 1
    fi
    python custom_config_runner.py --single "$2"
else
    # 나머지 인수들을 그대로 전달
    python custom_config_runner.py "$@"
fi
