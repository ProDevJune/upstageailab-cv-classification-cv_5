#!/bin/bash

echo "🔥 강력한 캐시 정리 (메모리 포함)"

# 1. Python 프로세스 종료 (실행 중인 실험이 있다면)
echo "🛑 실행 중인 Python 프로세스 확인..."
pgrep -f "python.*gemini_main" && echo "⚠️ 실행 중인 실험 발견! 종료 후 다시 시도하세요." && exit 1

# 2. GPU 메모리 정리
echo "🎮 GPU 메모리 정리..."
nvidia-smi --gpu-reset 2>/dev/null || echo "⚠️ GPU 리셋 실패 (권한 없음)"

# 3. Python으로 강력한 CUDA 캐시 정리
python3 -c "
import gc
import torch
import sys

print('🔧 메모리 정리 시작...')

# CUDA 캐시 완전 정리
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    print(f'✅ CUDA 캐시 정리: {torch.cuda.memory_allocated()//1024//1024}MB 사용 중')
else:
    print('⚠️ CUDA 사용 불가')

# Python 가비지 컬렉션
gc.collect()
print('✅ Python 메모리 정리 완료')
"

# 4. 시스템 캐시 정리 (가능한 경우)
echo "💾 시스템 캐시 정리..."
sync
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || echo "⚠️ 시스템 캐시 정리 실패 (권한 필요)"

# 5. 프로젝트별 정리
echo "📁 프로젝트 특화 정리..."

# WandB 완전 정리 (오래된 것만)
if [ -d "wandb" ]; then
    echo "📈 WandB 정리 중..."
    find wandb/ -type d -name "run-*" -mtime +1 | head -n -3 | xargs rm -rf 2>/dev/null
fi

# 모델 파일 정리 (1일 이상 된 것)
if [ -d "models" ]; then
    echo "🤖 모델 파일 정리 중..."
    find models/ -name "*.pth" -mtime +1 | head -n -2 | xargs rm 2>/dev/null
fi

echo "✅ 강력한 정리 완료!"
echo "📊 현재 GPU 상태:"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null || echo "GPU 정보 조회 실패"
