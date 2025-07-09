#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# 실험 안정성 문제 자동 수정 스크립트
echo "🔧 실험 안정성 문제 자동 수정"
echo "============================="
echo "⏰ 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. SSH 세션 안정성 보장 (screen/tmux)
echo "🖥️  1. SSH 세션 안정성 설정"
echo "----------------------------"

if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "SSH 연결 감지됨"
    
    if [ -n "$STY" ]; then
        echo "✅ 이미 GNU Screen 세션에서 실행 중"
    elif [ -n "$TMUX" ]; then
        echo "✅ 이미 tmux 세션에서 실행 중"
    else
        echo "⚠️  SSH 연결이지만 screen/tmux 세션이 아님"
        
        # screen 설치 확인 및 설치
        if command -v screen &> /dev/null; then
            echo "✅ screen이 설치되어 있음"
        else
            echo "📦 screen 설치 시도..."
            if sudo apt-get update && sudo apt-get install -y screen; then
                echo "✅ screen 설치 완료"
            else
                echo "❌ screen 설치 실패. 관리자에게 문의하세요."
            fi
        fi
        
        # tmux 설치 확인 및 설치  
        if command -v tmux &> /dev/null; then
            echo "✅ tmux가 설치되어 있음"
        else
            echo "📦 tmux 설치 시도..."
            if sudo apt-get install -y tmux; then
                echo "✅ tmux 설치 완료"
            else
                echo "❌ tmux 설치 실패"
            fi
        fi
        
        echo ""
        echo "🚨 중요: 실험 실행 전에 다음 중 하나를 실행하세요:"
        echo "   screen -S ml_experiment"
        echo "   또는"
        echo "   tmux new-session -s ml_experiment"
    fi
else
    echo "로컬 세션에서 실행 중"
fi

echo ""

# 2. 디스크 공간 정리
echo "💾 2. 디스크 공간 정리"
echo "---------------------"

# 임시 파일 정리
echo "임시 파일 정리 중..."
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.tmp" -delete 2>/dev/null

# 로그 파일 압축
echo "오래된 로그 파일 압축 중..."
find . -name "*.log" -size +100M -exec gzip {} \; 2>/dev/null

# 사용 가능 공간 재확인
available_space_gb=$(df . | tail -1 | awk '{print $4}')
available_space_gb=$((available_space_gb / 1024 / 1024))
echo "정리 후 사용 가능 공간: ${available_space_gb}GB"

echo ""

# 3. 메모리 최적화
echo "🧮 3. 메모리 최적화"
echo "------------------"

# 시스템 캐시 정리 (안전한 방법)
echo "시스템 캐시 정리 시도..."
if [ -w /proc/sys/vm/drop_caches ]; then
    sync
    echo 1 | sudo tee /proc/sys/vm/drop_caches > /dev/null
    echo "✅ 시스템 캐시 정리 완료"
else
    echo "⚠️  시스템 캐시 정리 권한 없음 (정상)"
fi

# Python 메모리 최적화 설정
echo "Python 메모리 최적화 환경 변수 설정..."
export PYTHONHASHSEED=0
export CUDA_CACHE_DISABLE=1
echo "✅ Python 메모리 최적화 설정 완료"

echo ""

# 4. GPU 최적화 및 안정성 설정
echo "🎮 4. GPU 최적화 및 안정성 설정"
echo "-------------------------------"

if command -v nvidia-smi &> /dev/null; then
    # GPU 메모리 정리
    echo "GPU 메모리 정리 중..."
    python -c "
import torch
if torch.cuda.is_available():
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    print('✅ GPU 메모리 캐시 정리 완료')
else:
    print('⚠️  CUDA 사용 불가')
" 2>/dev/null

    # GPU 성능 모드 설정
    echo "GPU 성능 모드 설정 시도..."
    if sudo nvidia-smi -pm 1 &> /dev/null; then
        echo "✅ GPU 성능 모드 활성화"
    else
        echo "⚠️  GPU 성능 모드 설정 권한 없음"
    fi
    
    # GPU 온도 임계값 확인
    gpu_temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)
    if [ "$gpu_temp" -gt 75 ]; then
        echo "⚠️  GPU 온도가 ${gpu_temp}°C로 높음. 팬 속도 조정 권장"
    else
        echo "✅ GPU 온도 정상 (${gpu_temp}°C)"
    fi
else
    echo "❌ nvidia-smi를 찾을 수 없음"
fi

echo ""

# 5. 필수 디렉토리 생성
echo "📁 5. 필수 디렉토리 생성"
echo "------------------------"

required_dirs=(
    "data/submissions"
    "v2_experiments/configs"
    "v2_experiments/logs"
    "v3_experiments/configs/modelA"
    "v3_experiments/configs/modelB"
    "v3_experiments/logs"
    "logs"
    "checkpoints"
)

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "✅ $dir 디렉토리 생성"
    else
        echo "✅ $dir 디렉토리 존재"
    fi
done

echo ""

# 6. 백업 및 체크포인트 설정
echo "💾 6. 백업 및 체크포인트 설정"
echo "-----------------------------"

# 설정 파일 백업
echo "중요 설정 파일 백업 중..."
backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

important_files=(
    "codes/config_v2_1.yaml"
    "codes/config_v2_2.yaml" 
    "codes/config_v3_modelA.yaml"
    "codes/config_v3_modelB.yaml"
    "v2_experiment_matrix.yaml"
    "v3_experiment_matrix.yaml"
)

for file in "${important_files[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$backup_dir/"
        echo "✅ $file 백업 완료"
    fi
done

echo ""

# 7. 모니터링 스크립트 준비
echo "📊 7. 모니터링 스크립트 준비"
echo "---------------------------"

# 실시간 모니터링 스크립트 생성
cat > monitor_resources.sh << 'EOF'
#!/bin/bash
# 실시간 리소스 모니터링 스크립트

echo "🔍 실시간 리소스 모니터링 시작"
echo "Ctrl+C로 중지"
echo ""

while true; do
    clear
    echo "📊 시스템 리소스 모니터링 - $(date)"
    echo "=================================="
    
    # GPU 정보
    if command -v nvidia-smi &> /dev/null; then
        echo "🎮 GPU 상태:"
        nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader | \
        awk -F', ' '{printf("   %s: %s°C, %s%% 사용률, %s/%s MB 메모리\n", $1, $2, $3, $4, $5)}'
    fi
    
    # 메모리 정보
    echo ""
    echo "🧮 메모리 상태:"
    free -h | grep -E "(Mem|Swap)" | awk '{printf("   %s: %s/%s 사용 (%s 사용가능)\n", $1, $3, $2, $7)}'
    
    # 디스크 정보  
    echo ""
    echo "💾 디스크 상태:"
    df -h . | tail -1 | awk '{printf("   사용률: %s (%s 사용가능)\n", $5, $4)}'
    
    # 실행 중인 Python 프로세스
    echo ""
    echo "🐍 Python 프로세스:"
    ps aux | grep python | grep -v grep | wc -l | awk '{printf("   실행 중: %s개\n", $1)}'
    
    sleep 30
done
EOF

chmod +x monitor_resources.sh
echo "✅ 리소스 모니터링 스크립트 생성 (./monitor_resources.sh로 실행)"

echo ""

# 8. 실험 재시작 스크립트 생성
echo "🔄 8. 실험 재시작 스크립트 생성"
echo "------------------------------"

cat > restart_experiment.sh << 'EOF'
#!/bin/bash
# 실험 중단 시 재시작 스크립트

echo "🔄 실험 재시작 스크립트"
echo "====================="

# 이전 실행 찾기
latest_submission=$(ls -t data/submissions/ | head -1)
if [ -n "$latest_submission" ]; then
    echo "📁 최근 실험 결과: $latest_submission"
    
    # 체크포인트 파일 확인
    if [ -f "data/submissions/$latest_submission"/*.pth ]; then
        echo "✅ 체크포인트 파일 발견"
        echo "   체크포인트에서 재시작할 수 있습니다."
    else
        echo "⚠️  체크포인트 파일 없음. 처음부터 다시 시작해야 합니다."
    fi
else
    echo "📂 이전 실험 결과 없음"
fi

echo ""
echo "재시작 옵션:"
echo "1. V2_1 시스템 재시작: ./run_v2_1_only.sh"
echo "2. V2_2 시스템 재시작: ./run_v2_2_only.sh" 
echo "3. V3 계층적 시스템 재시작: python v3_experiment_generator.py --phase phase1"
EOF

chmod +x restart_experiment.sh
echo "✅ 실험 재시작 스크립트 생성 (./restart_experiment.sh로 실행)"

echo ""

# 9. WandB 설정 확인 및 수정
echo "📈 9. WandB 설정 확인"
echo "--------------------"

# WandB 로그인 상태 확인
if python -c "import wandb; print('로그인됨' if wandb.api.api_key else '로그인 안됨')" 2>/dev/null | grep -q "로그인됨"; then
    echo "✅ WandB 로그인 상태"
else
    echo "⚠️  WandB 로그인 필요"
    echo "다음 명령어로 로그인하세요:"
    echo "  wandb login"
fi

echo ""

# 10. 최종 안전 체크리스트
echo "✅ 10. 최종 안전 체크리스트"
echo "---------------------------"

checklist=(
    "SSH 세션 안정성 (screen/tmux)"
    "충분한 디스크 공간"
    "메모리 최적화"
    "GPU 상태 정상"
    "필수 디렉토리 생성"
    "설정 파일 백업"
    "모니터링 스크립트 준비"
    "재시작 스크립트 준비"
)

echo "실험 실행 전 체크리스트:"
for item in "${checklist[@]}"; do
    echo "  ✅ $item"
done

echo ""
echo "🚀 실험 안전 실행 가이드:"
echo "========================"
echo ""
echo "1. 터미널 세션 보호:"
echo "   screen -S ml_experiment"
echo "   # 또는 tmux new-session -s ml_experiment"
echo ""
echo "2. 리소스 모니터링 시작 (별도 터미널):"
echo "   ./monitor_resources.sh"
echo ""
echo "3. 실험 실행:"
echo "   ./run_v2_2_only.sh  # 빠른 테스트"
echo "   # 또는 ./run_v2_1_only.sh  # 최고 성능"
echo "   # 또는 python v3_experiment_generator.py --phase phase1  # 혁신적"
echo ""
echo "4. 세션 분리 (실험 계속 실행):"
echo "   Ctrl+A, D (screen) 또는 Ctrl+B, D (tmux)"
echo ""
echo "5. 세션 재접속:"
echo "   screen -r ml_experiment"
echo "   # 또는 tmux attach-session -t ml_experiment"

echo ""
echo "✅ 실험 안정성 수정 완료!"
echo "========================="
echo "⏰ 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
