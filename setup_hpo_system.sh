# HPO 자동화 시스템 설치 및 설정 스크립트

echo "🚀 크로스 플랫폼 HPO 시스템 설치 중..."

# 실행 권한 부여
chmod +x run_experiments.sh

# 필요한 디렉토리들 생성
mkdir -p codes/practice
mkdir -p analysis_results
mkdir -p data/submissions
mkdir -p logs
mkdir -p models

# 초기 파일들 생성
touch codes/practice/__init__.py
touch analysis_results/.gitkeep
touch logs/.gitkeep
touch models/.gitkeep

echo "✅ 시스템 설치 완료!"
echo ""
echo "📋 사용법:"
echo "1) 대화형 모드: ./run_experiments.sh"
echo "2) 빠른 실험: ./run_experiments.sh quick 20"
echo "3) 전체 실험: ./run_experiments.sh full 50"
echo "4) 시스템 정보: ./run_experiments.sh info"
echo ""
echo "🎯 시작하려면: ./run_experiments.sh"
