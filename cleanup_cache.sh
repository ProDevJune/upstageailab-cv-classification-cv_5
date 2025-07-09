#!/bin/bash

echo "🧹 서버 캐시 및 불필요한 파일 정리 시작..."

# 현재 위치 확인
echo "📍 현재 위치: $(pwd)"

# 1. Python 캐시 파일 삭제
echo "🐍 Python 캐시 파일 삭제 중..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

# 2. Jupyter 체크포인트 삭제
echo "📓 Jupyter 체크포인트 삭제 중..."
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null

# 3. 모델 체크포인트 및 로그 정리 (최신 것만 유지)
echo "📊 모델 체크포인트 정리 중..."
if [ -d "models" ]; then
    echo "📁 models 폴더 내용:"
    ls -la models/
    # 7일 이상 된 체크포인트 삭제
    find models/ -name "*.pth" -mtime +7 -delete 2>/dev/null
    find models/ -name "*.pt" -mtime +7 -delete 2>/dev/null
fi

# 4. 로그 파일 정리
echo "📝 로그 파일 정리 중..."
if [ -d "logs" ]; then
    echo "📁 logs 폴더 내용:"
    ls -la logs/
    # 7일 이상 된 로그 삭제
    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
    find logs/ -name "*.out" -mtime +7 -delete 2>/dev/null
fi

# 5. wandb 캐시 정리
echo "📈 WandB 캐시 정리 중..."
if [ -d "wandb" ]; then
    echo "📁 wandb 폴더 크기:"
    du -sh wandb/
    # wandb 캐시 정리 (최신 5개 실행만 유지)
    find wandb/ -type d -name "run-*" | sort | head -n -5 | xargs rm -rf 2>/dev/null
fi

# 6. 임시 파일 삭제
echo "🗑️ 임시 파일 삭제 중..."
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null

# 7. CUDA 캐시 정리 (Python 스크립트로)
echo "🎮 CUDA 캐시 정리 중..."
python3 -c "
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    print('✅ CUDA 캐시 정리 완료')
else:
    print('⚠️ CUDA 사용 불가')
" 2>/dev/null

# 8. 불완전한 실험 결과 파일 정리
echo "🧪 불완전한 실험 파일 정리 중..."
find . -name "*.csv" -size 0 -delete 2>/dev/null
find . -name "submission_*.csv" -mtime +3 -delete 2>/dev/null

# 9. 백업 파일 정리
echo "💾 오래된 백업 파일 정리 중..."
find . -name "*.backup*" -mtime +7 -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null

# 10. 디스크 사용량 확인
echo "💽 정리 후 디스크 사용량:"
df -h .
echo ""
echo "📊 현재 폴더 크기:"
du -sh .
echo ""
echo "📈 주요 폴더별 크기:"
du -sh */ 2>/dev/null | sort -hr | head -10

echo ""
echo "✅ 캐시 및 불필요한 파일 정리 완료!"
echo "🚀 이제 깨끗한 환경에서 실험을 시작할 수 있습니다."
