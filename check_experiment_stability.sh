#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# 장시간 실험 안정성 사전 체크 스크립트
echo "🛡️  장시간 실험 안정성 사전 체크"
echo "==============================="
echo "⏰ 체크 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 전역 변수
ISSUES_FOUND=0
CRITICAL_ISSUES=()
WARNINGS=()

log_issue() {
    local level=$1
    local message=$2
    if [ "$level" = "CRITICAL" ]; then
        CRITICAL_ISSUES+=("$message")
        ((ISSUES_FOUND++))
        echo "🚨 CRITICAL: $message"
    elif [ "$level" = "WARNING" ]; then
        WARNINGS+=("$message")
        echo "⚠️  WARNING: $message"
    else
        echo "ℹ️  INFO: $message"
    fi
}

# 1. 디스크 공간 체크
echo "💾 1. 디스크 공간 및 I/O 체크"
echo "-----------------------------"

# 현재 디스크 사용량
current_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
available_space=$(df -h . | tail -1 | awk '{print $4}')
available_space_gb=$(df . | tail -1 | awk '{print $4}')
available_space_gb=$((available_space_gb / 1024 / 1024))

echo "현재 디스크 사용률: ${current_usage}%"
echo "사용 가능 공간: ${available_space} (${available_space_gb}GB)"

if [ $current_usage -gt 80 ]; then
    log_issue "CRITICAL" "디스크 사용률이 ${current_usage}%로 높음. 실험 중 공간 부족 위험"
elif [ $current_usage -gt 70 ]; then
    log_issue "WARNING" "디스크 사용률이 ${current_usage}%임. 모니터링 필요"
fi

if [ $available_space_gb -lt 100 ]; then
    log_issue "CRITICAL" "사용 가능 공간이 ${available_space_gb}GB로 부족. 최소 100GB 필요"
elif [ $available_space_gb -lt 200 ]; then
    log_issue "WARNING" "사용 가능 공간이 ${available_space_gb}GB임. 200GB 이상 권장"
fi

# 쓰기 권한 테스트
echo "쓰기 권한 테스트..."
if touch test_write_permission 2>/dev/null; then
    rm -f test_write_permission
    echo "✅ 쓰기 권한 정상"
else
    log_issue "CRITICAL" "현재 디렉토리에 쓰기 권한 없음"
fi

echo ""

# 2. 메모리 체크
echo "🧮 2. 메모리 및 스왑 체크"
echo "-------------------------"

# 메모리 정보 파싱
total_mem=$(free | grep Mem | awk '{print $2}')
used_mem=$(free | grep Mem | awk '{print $3}')
available_mem=$(free | grep Mem | awk '{print $7}')
total_mem_gb=$((total_mem / 1024 / 1024))
used_mem_gb=$((used_mem / 1024 / 1024))
available_mem_gb=$((available_mem / 1024 / 1024))
mem_usage_percent=$((used_mem * 100 / total_mem))

echo "총 메모리: ${total_mem_gb}GB"
echo "사용 중: ${used_mem_gb}GB (${mem_usage_percent}%)"
echo "사용 가능: ${available_mem_gb}GB"

if [ $mem_usage_percent -gt 85 ]; then
    log_issue "CRITICAL" "메모리 사용률이 ${mem_usage_percent}%로 높음"
elif [ $mem_usage_percent -gt 75 ]; then
    log_issue "WARNING" "메모리 사용률이 ${mem_usage_percent}%임"
fi

if [ $available_mem_gb -lt 32 ]; then
    log_issue "WARNING" "사용 가능 메모리가 ${available_mem_gb}GB로 적음. 큰 모델 실험 시 주의"
fi

# 스왑 체크
swap_total=$(free | grep Swap | awk '{print $2}')
if [ $swap_total -eq 0 ]; then
    log_issue "WARNING" "스왑 메모리가 설정되지 않음. OOM 위험 증가"
fi

echo ""

# 3. GPU 상태 및 안정성 체크
echo "🎮 3. GPU 상태 및 안정성 체크"
echo "-----------------------------"

if command -v nvidia-smi &> /dev/null; then
    # GPU 온도 체크
    gpu_temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits)
    gpu_power=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits | sed 's/ W//')
    gpu_memory_used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
    gpu_memory_total=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
    gpu_utilization=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | sed 's/ %//')
    
    echo "GPU 온도: ${gpu_temp}°C"
    echo "GPU 전력: ${gpu_power}W"
    echo "GPU 메모리: ${gpu_memory_used}/${gpu_memory_total}MB"
    echo "GPU 사용률: ${gpu_utilization}%"
    
    if [ "$gpu_temp" -gt 85 ]; then
        log_issue "CRITICAL" "GPU 온도가 ${gpu_temp}°C로 높음. 쿨링 문제 가능성"
    elif [ "$gpu_temp" -gt 75 ]; then
        log_issue "WARNING" "GPU 온도가 ${gpu_temp}°C임. 모니터링 필요"
    fi
    
    # GPU 메모리 사용률
    gpu_mem_usage=$((gpu_memory_used * 100 / gpu_memory_total))
    if [ $gpu_mem_usage -gt 90 ]; then
        log_issue "WARNING" "GPU 메모리 사용률이 ${gpu_mem_usage}%로 높음"
    fi
    
    # GPU 스트레스 테스트 (간단한)
    echo "GPU 안정성 테스트 중..."
    python -c "
import torch
try:
    device = torch.device('cuda')
    x = torch.randn(1000, 1000, device=device)
    y = torch.randn(1000, 1000, device=device)
    for _ in range(5):
        z = torch.mm(x, y)
    torch.cuda.synchronize()
    print('✅ GPU 연산 테스트 통과')
except Exception as e:
    print(f'❌ GPU 연산 테스트 실패: {e}')
    exit(1)
" || log_issue "CRITICAL" "GPU 기본 연산 테스트 실패"

else
    log_issue "CRITICAL" "nvidia-smi 명령어를 찾을 수 없음. GPU 모니터링 불가"
fi

echo ""

# 4. 프로세스 및 세션 안정성 체크
echo "🔄 4. 프로세스 및 세션 안정성 체크"
echo "--------------------------------"

# SSH 세션 체크
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    echo "SSH 연결 감지됨"
    
    # screen 또는 tmux 세션 체크
    if [ -n "$STY" ]; then
        echo "✅ GNU Screen 세션에서 실행 중"
    elif [ -n "$TMUX" ]; then
        echo "✅ tmux 세션에서 실행 중"
    else
        log_issue "CRITICAL" "SSH 연결이지만 screen/tmux 세션이 아님. 연결 끊김 시 실험 중단됨"
        echo "해결책: screen 또는 tmux를 사용하세요"
        echo "  screen 설치: sudo apt-get install screen"
        echo "  tmux 설치: sudo apt-get install tmux"
        echo "  사용법: screen -S experiment_session"
    fi
else
    echo "로컬 세션에서 실행 중"
fi

# 백그라운드 프로세스 수 체크
bg_processes=$(ps aux | grep python | grep -v grep | wc -l)
if [ $bg_processes -gt 10 ]; then
    log_issue "WARNING" "Python 프로세스가 ${bg_processes}개 실행 중. 리소스 경쟁 가능성"
fi

echo ""

# 5. 네트워크 연결 안정성 체크
echo "🌐 5. 네트워크 연결 안정성 체크"
echo "------------------------------"

# 외부 연결 테스트 (WandB, PyPI 등)
echo "외부 서비스 연결 테스트:"

# WandB 연결 테스트
if ping -c 1 api.wandb.ai &> /dev/null; then
    echo "✅ WandB (api.wandb.ai) 연결 정상"
else
    log_issue "WARNING" "WandB 서버 연결 실패. 로깅 문제 가능성"
fi

# PyPI 연결 테스트  
if ping -c 1 pypi.org &> /dev/null; then
    echo "✅ PyPI (pypi.org) 연결 정상"
else
    log_issue "WARNING" "PyPI 연결 실패. 패키지 설치 문제 가능성"
fi

echo ""

# 6. 파일 시스템 및 경로 체크
echo "📁 6. 파일 시스템 및 경로 체크"
echo "-----------------------------"

# 프로젝트 파일 존재 확인
required_files=(
    "codes/gemini_main_v2_1_style.py"
    "codes/gemini_main_v2_enhanced.py" 
    "codes/gemini_main_v3.py"
    "v2_experiment_generator.py"
    "v3_experiment_generator.py"
    "data/train.csv"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 존재"
    else
        missing_files+=("$file")
        log_issue "CRITICAL" "$file 파일이 없음"
    fi
done

# data 디렉토리 내 이미지 파일 체크
if [ -d "data/train" ]; then
    train_images=$(find data/train -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" | wc -l)
    echo "훈련 이미지 개수: $train_images"
    if [ $train_images -lt 1000 ]; then
        log_issue "WARNING" "훈련 이미지가 ${train_images}개로 적음"
    fi
else
    log_issue "CRITICAL" "data/train 디렉토리가 없음"
fi

if [ -d "data/test" ]; then
    test_images=$(find data/test -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" | wc -l)
    echo "테스트 이미지 개수: $test_images"
else
    log_issue "CRITICAL" "data/test 디렉토리가 없음"
fi

echo ""

# 7. Python 환경 안정성 체크
echo "🐍 7. Python 환경 안정성 체크"
echo "-----------------------------"

# Python 버전 체크
python_version=$(python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "Python 버전: $python_version"

if [[ "$python_version" < "3.8" ]]; then
    log_issue "CRITICAL" "Python 버전이 $python_version 로 너무 낮음. 최소 3.8 필요"
fi

# 가상환경 체크
if [ -z "$VIRTUAL_ENV" ]; then
    log_issue "WARNING" "가상환경이 활성화되지 않음"
else
    echo "✅ 가상환경 활성화: $VIRTUAL_ENV"
fi

# 필수 라이브러리 재확인
echo "핵심 라이브러리 import 테스트:"
python -c "
critical_imports = ['torch', 'torchvision', 'timm', 'albumentations', 'cv2', 'pandas', 'numpy', 'sklearn', 'yaml']
failed = []
for lib in critical_imports:
    try:
        __import__(lib)
        print(f'✅ {lib}')
    except ImportError:
        print(f'❌ {lib}')
        failed.append(lib)

if failed:
    print(f'실패한 라이브러리: {failed}')
    exit(1)
" || log_issue "CRITICAL" "핵심 라이브러리 import 실패"

echo ""

# 8. 실험 설정 파일 유효성 체크
echo "⚙️  8. 실험 설정 파일 유효성 체크"
echo "--------------------------------"

# 설정 파일들 체크
config_files=(
    "codes/config_v2_1.yaml"
    "codes/config_v2_2.yaml"
    "codes/config_v3_modelA.yaml"
    "codes/config_v3_modelB.yaml"
)

for config in "${config_files[@]}"; do
    if [ -f "$config" ]; then
        echo -n "✅ $config ... "
        # YAML 문법 체크
        python -c "
import yaml
try:
    with open('$config', 'r') as f:
        yaml.safe_load(f)
    print('유효')
except Exception as e:
    print(f'오류: {e}')
    exit(1)
" || log_issue "CRITICAL" "$config 파일 문법 오류"
    else
        log_issue "CRITICAL" "$config 파일이 없음"
    fi
done

echo ""

# 9. 리소스 모니터링 설정 체크
echo "📊 9. 리소스 모니터링 설정 체크"
echo "------------------------------"

# 모니터링 스크립트 존재 확인
if [ -f "v2_experiment_monitor.py" ] || [ -f "v3_experiment_monitor.py" ]; then
    echo "✅ 실험 모니터링 스크립트 존재"
else
    log_issue "WARNING" "실험 모니터링 스크립트가 없음. 진행 상황 추적 어려움"
fi

# wandb 설정 체크
if python -c "import wandb; wandb.login()" &> /dev/null; then
    echo "✅ WandB 로그인 상태"
else
    log_issue "WARNING" "WandB 로그인 필요. 실험 로깅에 문제 가능성"
fi

echo ""

# 10. 최종 결과 및 권장사항
echo "📋 10. 최종 진단 결과"
echo "====================s"

echo "발견된 이슈 요약:"
echo "- 심각한 문제: ${#CRITICAL_ISSUES[@]}개"
echo "- 경고 사항: ${#WARNINGS[@]}개"

if [ ${#CRITICAL_ISSUES[@]} -gt 0 ]; then
    echo ""
    echo "🚨 해결해야 할 심각한 문제들:"
    for issue in "${CRITICAL_ISSUES[@]}"; do
        echo "  • $issue"
    done
    echo ""
    echo "❌ 현재 상태로는 장시간 실험 실행을 권장하지 않습니다."
    echo "   위의 심각한 문제들을 먼저 해결하세요."
else
    echo ""
    echo "✅ 심각한 문제가 발견되지 않았습니다!"
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo "⚠️  주의할 경고 사항들:"
        for warning in "${WARNINGS[@]}"; do
            echo "  • $warning"
        done
        echo ""
        echo "🟡 경고 사항들을 검토한 후 실험을 시작하는 것을 권장합니다."
    else
        echo "🎉 모든 검사를 통과했습니다! 장시간 실험 실행 준비 완료!"
    fi
fi

echo ""
echo "🚀 실험 실행 전 권장 사항:"
echo "1. screen/tmux 세션에서 실행"
echo "2. 실험 모니터링 스크립트 병행 실행"  
echo "3. 디스크 공간 주기적 확인"
echo "4. GPU 온도 모니터링"
echo "5. 중간 체크포인트 저장 설정 확인"

echo ""
echo "✅ 안정성 사전 체크 완료!"
echo "=========================="
echo "⏰ 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"

# 종료 코드 설정
if [ ${#CRITICAL_ISSUES[@]} -gt 0 ]; then
    exit 1
else
    exit 0
fi
