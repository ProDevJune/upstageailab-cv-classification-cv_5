#!/bin/bash
# macOS에서 Ubuntu로 프로젝트 이전을 위한 압축 스크립트

echo "📦 cv-classification 프로젝트 Ubuntu 이전용 압축 시작..."

PROJECT_DIR=""
cd "$PROJECT_DIR"

# 압축 파일명 (날짜 포함)
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
ARCHIVE_NAME="cv-classification_ubuntu_${TIMESTAMP}.tar.gz"

echo "📁 프로젝트 디렉토리: $PROJECT_DIR"
echo "📦 압축 파일명: $ARCHIVE_NAME"

# 제외할 파일/폴더 목록 생성
cat > .exclude_list << 'EOF'
# 가상환경 제외
venv/
.venv/
env/
.env/

# macOS 특화 파일들
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
Icon?
ehthumbs.db
Thumbs.db

# IDE 설정 파일들
.vscode/
.idea/
*.swp
*.swo
*~

# Git 관련 (일부만 제외)
.git/objects/
.git/logs/
.git/refs/remotes/

# 로그 파일들
*.log
logs/*.log
wandb/run-*/files/
wandb/run-*/logs/

# 임시 파일들
temp/
tmp/
*.tmp
*.temp

# Python 캐시
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints/

# 대용량 압축 파일들 (다른 방법으로 이전)
*.tar.gz
*.zip
*.7z
data_*.tar.gz

# 모델 체크포인트 (용량이 큰 것들)
models/checkpoints/
*.pth
*.pt
*.ckpt

# 실험 결과 CSV (선택적)
# enhanced_experiment_results.csv
# experiment_results.csv
EOF

echo ""
echo "🚫 제외될 파일/폴더 목록:"
echo "--------------------------"
cat .exclude_list | grep -v '^#' | grep -v '^$'

echo ""
echo "📊 압축 전 디스크 사용량 확인..."
du -sh . 2>/dev/null || echo "  전체 크기 계산 중..."

echo ""
echo "🗜️  압축 중... (시간이 걸릴 수 있습니다)"

# tar를 사용한 압축 (제외 목록 적용)
tar -czf "../$ARCHIVE_NAME" \
    --exclude-from=.exclude_list \
    -C .. \
    cv-classification

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 압축 완료!"
    
    # 압축 파일 정보
    ARCHIVE_PATH="../$ARCHIVE_NAME"
    ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
    
    echo "📦 압축 파일: $ARCHIVE_PATH"
    echo "📊 압축 파일 크기: $ARCHIVE_SIZE"
    
    echo ""
    echo "🚀 Ubuntu 이전 방법:"
    echo "===================="
    echo ""
    echo "1. 압축 파일 복사:"
    echo "   scp $ARCHIVE_PATH ubuntu-server:/path/to/destination/"
    echo ""
    echo "2. Ubuntu에서 압축 해제:"
    echo "   cd /path/to/destination"
    echo "   tar -xzf $ARCHIVE_NAME"
    echo "   cd cv-classification"
    echo ""
    echo "3. Ubuntu 환경 설정:"
    echo "   chmod +x *.sh"
    echo "   ./setup_and_validate_all.sh"
    echo ""
    echo "4. 데이터 파일 별도 복사 (필요시):"
    echo "   # 대용량 데이터 파일들"
    echo "   scp data_train.tar.gz ubuntu-server:/path/to/cv-classification/"
    echo "   scp data_test.tar.gz ubuntu-server:/path/to/cv-classification/"
    echo "   scp data_csv.tar.gz ubuntu-server:/path/to/cv-classification/"
    echo ""
    echo "📋 Ubuntu에서 추가 설정 사항:"
    echo "=============================="
    echo ""
    echo "• Python 3.11 설치:"
    echo "  sudo apt update"
    echo "  sudo apt install python3.11 python3.11-venv python3.11-dev"
    echo ""
    echo "• CUDA 환경 (GPU 사용시):"
    echo "  nvidia-smi  # GPU 확인"
    echo "  # requirements_ubuntu.txt가 자동으로 사용됨"
    echo ""
    echo "• CPU 전용 환경:"
    echo "  # requirements_cpu.txt가 자동으로 사용됨"
    
    # 임시 파일 정리
    rm -f .exclude_list
    
else
    echo "❌ 압축 실패"
    rm -f .exclude_list
    exit 1
fi

echo ""
echo "🎉 Ubuntu 이전 준비 완료!"
echo ""
echo "⚠️  주의사항:"
echo "============"
echo "• 모든 절대 경로가 상대 경로로 수정되었습니다"
echo "• 플랫폼 자동 감지로 Ubuntu 환경에 맞는 패키지가 설치됩니다"
echo "• 가상환경은 제외되어 Ubuntu에서 새로 생성됩니다"
echo "• 대용량 데이터 파일은 별도로 복사해야 할 수 있습니다"
