#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# AIStages 서버 사양 정보 수집 스크립트
echo "🖥️  AIStages 서버 사양 정보 수집"
echo "=================================="
echo "⏰ 수집 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 기본 시스템 정보
echo "📋 1. 기본 시스템 정보"
echo "------------------------"
echo "🐧 OS 정보:"
cat /etc/os-release | head -5
echo ""

echo "🏗️ 시스템 아키텍처:"
uname -a
echo ""

echo "⏱️ 시스템 가동 시간:"
uptime
echo ""

# 2. CPU 정보
echo "🧠 2. CPU 정보"
echo "---------------"
echo "CPU 모델:"
cat /proc/cpuinfo | grep "model name" | head -1
echo ""

echo "CPU 코어 수:"
echo "  - 물리 CPU: $(cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l)"
echo "  - 논리 CPU: $(nproc)"
echo "  - CPU 코어: $(cat /proc/cpuinfo | grep "cpu cores" | head -1 | awk '{print $4}')"
echo ""

echo "CPU 주파수:"
cat /proc/cpuinfo | grep "cpu MHz" | head -1
echo ""

# 3. 메모리 정보
echo "🧮 3. 메모리 정보"
echo "-----------------"
echo "메모리 상세 정보:"
free -h
echo ""

echo "메모리 총량:"
cat /proc/meminfo | grep MemTotal
echo ""

# 4. GPU 정보 (NVIDIA)
echo "🎮 4. GPU 정보"
echo "---------------"
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU 감지됨:"
    nvidia-smi --query-gpu=name,memory.total,driver_version,cuda_version --format=csv,noheader,nounits
    echo ""
    
    echo "GPU 상세 정보:"
    nvidia-smi
    echo ""
    
    echo "CUDA 버전:"
    nvcc --version 2>/dev/null || echo "NVCC 명령어를 찾을 수 없음"
    echo ""
else
    echo "❌ NVIDIA GPU 또는 nvidia-smi를 찾을 수 없음"
    echo ""
fi

# 5. 디스크 정보
echo "💾 5. 디스크 정보"
echo "-----------------"
echo "디스크 사용량:"
df -h
echo ""

echo "파일시스템 타입:"
df -T
echo ""

echo "디스크 I/O 정보:"
lsblk 2>/dev/null || echo "lsblk 명령어를 사용할 수 없음"
echo ""

# 6. 네트워크 정보
echo "🌐 6. 네트워크 정보"
echo "-------------------"
echo "네트워크 인터페이스:"
ip addr show 2>/dev/null || ifconfig -a 2>/dev/null || echo "네트워크 정보를 가져올 수 없음"
echo ""

# 7. Python 환경 정보
echo "🐍 7. Python 환경 정보"
echo "----------------------"
echo "Python 버전:"
python --version 2>/dev/null || python3 --version 2>/dev/null || echo "Python을 찾을 수 없음"
echo ""

echo "pip 버전:"
pip --version 2>/dev/null || pip3 --version 2>/dev/null || echo "pip을 찾을 수 없음"
echo ""

echo "가상환경 확인:"
echo "  - VIRTUAL_ENV: ${VIRTUAL_ENV:-'Not set'}"
echo "  - CONDA_DEFAULT_ENV: ${CONDA_DEFAULT_ENV:-'Not set'}"
echo ""

# 8. PyTorch 환경 확인
echo "🔥 8. PyTorch 환경 확인"
echo "----------------------"
python -c "
try:
    import torch
    print(f'PyTorch 버전: {torch.__version__}')
    print(f'CUDA 사용 가능: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'CUDA 버전: {torch.version.cuda}')
        print(f'GPU 개수: {torch.cuda.device_count()}')
        for i in range(torch.cuda.device_count()):
            print(f'GPU {i}: {torch.cuda.get_device_name(i)}')
            print(f'GPU {i} 메모리: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.1f} GB')
    else:
        print('CUDA를 사용할 수 없습니다.')
except ImportError:
    print('PyTorch가 설치되지 않았습니다.')
" 2>/dev/null || echo "Python 실행 실패"
echo ""

# 9. 주요 ML 라이브러리 확인
echo "📚 9. 주요 ML 라이브러리 확인"
echo "-----------------------------"
python -c "
libraries = ['torch', 'torchvision', 'numpy', 'pandas', 'sklearn', 'cv2', 'albumentations', 'timm', 'wandb']
for lib in libraries:
    try:
        module = __import__(lib)
        version = getattr(module, '__version__', 'Unknown')
        print(f'{lib}: {version}')
    except ImportError:
        print(f'{lib}: Not installed')
" 2>/dev/null || echo "라이브러리 확인 실패"
echo ""

# 10. 리소스 사용량
echo "📊 10. 현재 리소스 사용량"
echo "-------------------------"
echo "CPU 사용률:"
top -bn1 | grep "Cpu(s)" | head -1
echo ""

echo "메모리 사용률:"
free | grep Mem | awk '{printf("사용중: %.1f%% (%s/%s)\n", $3/$2 * 100.0, $3, $2)}'
echo ""

if command -v nvidia-smi &> /dev/null; then
    echo "GPU 사용률:"
    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits | \
    awk -F', ' '{printf("GPU 사용률: %s%%, 메모리: %s/%s MB\n", $1, $2, $3)}'
    echo ""
fi

# 11. 프로세스 정보
echo "🔄 11. 주요 프로세스 정보"
echo "-------------------------"
echo "메모리 사용량 상위 5개 프로세스:"
ps aux --sort=-%mem | head -6
echo ""

# 12. 환경 변수
echo "🔧 12. 중요 환경 변수"
echo "--------------------"
echo "CUDA_VISIBLE_DEVICES: ${CUDA_VISIBLE_DEVICES:-'Not set'}"
echo "PYTHONPATH: ${PYTHONPATH:-'Not set'}"
echo "PATH (관련 부분): $(echo $PATH | tr ':' '\n' | grep -E '(cuda|python|conda)' | head -3)"
echo ""

# 13. 마운트 포인트 및 권한
echo "📁 13. 마운트 포인트 및 현재 디렉토리"
echo "-------------------------------------"
echo "현재 작업 디렉토리:"
pwd
echo ""

echo "현재 디렉토리 권한:"
ls -la . | head -5
echo ""

echo "홈 디렉토리 용량:"
du -sh ~ 2>/dev/null || echo "홈 디렉토리 용량 확인 불가"
echo ""

# 14. 시간대 및 로케일
echo "🌍 14. 시간대 및 로케일"
echo "-----------------------"
echo "시간대: $(timedatectl show --property=Timezone --value 2>/dev/null || echo $TZ)"
echo "로케일: ${LANG:-'Not set'}"
echo ""

echo "✅ 시스템 정보 수집 완료!"
echo "=================================="
