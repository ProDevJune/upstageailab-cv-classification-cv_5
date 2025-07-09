#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# 실험 실행 전 빠른 안전 점검
echo "⚡ 실험 실행 전 빠른 안전 점검"
echo "============================="

# 1. SSH 세션 체크 (가장 중요)
echo "🔒 세션 안정성:"
if [ -n "$STY" ]; then
    echo "  ✅ GNU Screen 세션"
elif [ -n "$TMUX" ]; then
    echo "  ✅ tmux 세션" 
elif [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "  🚨 SSH 연결이지만 screen/tmux 없음!"
    echo "     🔧 해결: screen -S experiment 실행 후 다시 시작"
    exit 1
else
    echo "  ✅ 로컬 세션"
fi

# 2. 디스크 공간 체크
available_gb=$(df . | tail -1 | awk '{print $4}')
available_gb=$((available_gb / 1024 / 1024))
echo "💾 디스크 공간: ${available_gb}GB"
if [ $available_gb -lt 50 ]; then
    echo "  🚨 디스크 공간 부족! 최소 50GB 필요"
    exit 1
fi

# 3. GPU 메모리 체크
if command -v nvidia-smi &> /dev/null; then
    gpu_free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits)
    gpu_free_gb=$((gpu_free / 1024))
    echo "🎮 GPU 메모리: ${gpu_free_gb}GB 사용가능"
    if [ $gpu_free_gb -lt 20 ]; then
        echo "  ⚠️  GPU 메모리 부족. 다른 프로세스 확인 필요"
    fi
else
    echo "🎮 GPU: nvidia-smi 없음"
    exit 1
fi

# 4. 필수 라이브러리 체크
echo "📚 라이브러리:"
missing=0
for lib in torch sklearn yaml; do
    if python -c "import $lib" 2>/dev/null; then
        echo "  ✅ $lib"
    else
        echo "  ❌ $lib 없음"
        missing=1
    fi
done

if [ $missing -eq 1 ]; then
    echo "  🔧 해결: ./fix_venv_libraries.sh 실행"
    exit 1
fi

# 5. 데이터 존재 확인
if [ -f "data/train.csv" ] && [ -d "data/train" ]; then
    echo "📊 데이터: ✅ 정상"
else
    echo "📊 데이터: ❌ train.csv 또는 train/ 없음"
    exit 1
fi

echo ""
echo "🎉 모든 안전 점검 통과!"
echo "🚀 실험 실행 준비 완료!"
echo ""
echo "권장 실행 순서:"
echo "1. 리소스 모니터링: ./monitor_resources.sh (별도 터미널)"
echo "2. 실험 실행:"
echo "   - 빠른 테스트: ./run_v2_2_only.sh"
echo "   - 최고 성능: ./run_v2_1_only.sh"  
echo "   - 혁신적: python v3_experiment_generator.py --phase phase1"
echo ""
