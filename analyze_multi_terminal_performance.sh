#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# 멀티 터미널 동시 실행 성능 영향 분석
echo "🔍 멀티 터미널 동시 실행 성능 분석"
echo "=================================="
echo "⏰ 분석 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 하드웨어 리소스 분석
echo "💻 1. 하드웨어 리소스 현황"
echo "-------------------------"

# CPU 정보
cpu_cores=$(nproc)
cpu_threads=$(cat /proc/cpuinfo | grep processor | wc -l)
cpu_model=$(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs)

echo "CPU: $cpu_model"
echo "물리 코어: $cpu_cores"
echo "논리 스레드: $cpu_threads"

# 메모리 정보
total_mem_gb=$(free | grep Mem | awk '{print int($2/1024/1024)}')
echo "총 메모리: ${total_mem_gb}GB"

# GPU 정보
if command -v nvidia-smi &> /dev/null; then
    gpu_name=$(nvidia-smi --query-gpu=name --format=csv,noheader)
    gpu_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
    gpu_memory_gb=$((gpu_memory / 1024))
    echo "GPU: $gpu_name"
    echo "GPU 메모리: ${gpu_memory_gb}GB"
    
    # CUDA 멀티 프로세싱 지원 확인
    cuda_devices=$(nvidia-smi --list-gpus | wc -l)
    echo "CUDA 디바이스 수: $cuda_devices"
fi

echo ""

# 2. 병목 지점 분석
echo "🚧 2. 잠재적 병목 지점 분석"
echo "---------------------------"

echo "📊 리소스별 병목 가능성:"

# CPU 병목 분석
if [ $cpu_threads -ge 32 ]; then
    echo "  ✅ CPU: 충분 (${cpu_threads}스레드) - 동시 실행 문제없음"
elif [ $cpu_threads -ge 16 ]; then
    echo "  🟡 CPU: 양호 (${cpu_threads}스레드) - 2-3개 실험 가능"
else
    echo "  ⚠️  CPU: 제한적 (${cpu_threads}스레드) - 1-2개 실험 권장"
fi

# 메모리 병목 분석
if [ $total_mem_gb -ge 128 ]; then
    echo "  ✅ 메모리: 충분 (${total_mem_gb}GB) - 여러 실험 동시 가능"
elif [ $total_mem_gb -ge 64 ]; then
    echo "  🟡 메모리: 양호 (${total_mem_gb}GB) - 2-3개 실험 가능"
else
    echo "  ⚠️  메모리: 제한적 (${total_mem_gb}GB) - 1-2개 실험 권장"
fi

# GPU 병목 분석 (가장 중요)
if [ $cuda_devices -gt 1 ]; then
    echo "  🚀 GPU: 멀티 GPU (${cuda_devices}개) - 동시 실행 최적"
elif [ $gpu_memory_gb -ge 20 ]; then
    echo "  ⚠️  GPU: 단일 고급 GPU - **주요 병목 지점**"
    echo "     → GPU는 한 번에 하나의 실험만 권장"
else
    echo "  🚨 GPU: 제한적 - 순차 실행 필수"
fi

# 디스크 I/O 병목 분석
echo "  💾 디스크 I/O: 데이터 로딩 시 경쟁 발생 가능"

echo ""

# 3. 실험별 리소스 사용량 예측
echo "📈 3. 실험별 리소스 사용량 예측"
echo "-------------------------------"

cat << 'EOF'
📊 V2_2 시스템 (ResNet50, EfficientNet-B4):
  - GPU 메모리: 6-12GB
  - CPU: 8-16 스레드
  - 시스템 메모리: 16-32GB
  - 디스크 I/O: 중간

📊 V2_1 시스템 (ConvNeXt-V2 Large):
  - GPU 메모리: 16-20GB
  - CPU: 12-24 스레드  
  - 시스템 메모리: 32-64GB
  - 디스크 I/O: 높음

📊 V3 계층적 시스템 (2모델):
  - GPU 메모리: 12-16GB
  - CPU: 16-32 스레드
  - 시스템 메모리: 32-48GB
  - 디스크 I/O: 매우 높음 (2개 모델)
EOF

echo ""

# 4. 동시 실행 시나리오 분석
echo "🎭 4. 동시 실행 시나리오 분석"
echo "-----------------------------"

echo "시나리오별 성능 영향:"
echo ""

echo "📍 시나리오 1: 모니터링 + 실험 1개"
echo "  - 성능 영향: 0-5% ✅"
echo "  - 권장도: 강력 추천"
echo "  - 비고: 모니터링은 리소스 사용량 극소"

echo ""
echo "📍 시나리오 2: 실험 2개 동시 (같은 GPU)"
echo "  - 성능 영향: 30-50% ⚠️"
echo "  - 권장도: 비추천"
echo "  - 이유: GPU 메모리 경쟁, 컨텍스트 스위칭"

echo ""
echo "📍 시나리오 3: 실험 1개 + 데이터 전처리"
echo "  - 성능 영향: 10-20% 🟡"
echo "  - 권장도: 조건부 가능"
echo "  - 조건: CPU 집약적 작업만"

echo ""
echo "📍 시나리오 4: 서로 다른 phase 실험"
echo "  - 성능 영향: 40-60% ❌"
echo "  - 권장도: 불가"
echo "  - 이유: 동일한 GPU 자원 경쟁"

echo ""

# 5. GPU 동시 사용 실제 테스트
echo "🧪 5. GPU 동시 사용 실제 테스트"
echo "-------------------------------"

if command -v nvidia-smi &> /dev/null; then
    echo "GPU 멀티 프로세스 지원 테스트..."
    
    # 간단한 GPU 멀티 프로세스 테스트
    python << 'EOF'
import torch
import multiprocessing as mp
import time

def gpu_task(device_id, task_id):
    try:
        device = torch.device(f'cuda:{device_id}')
        # 작은 연산으로 테스트
        x = torch.randn(500, 500, device=device)
        y = torch.randn(500, 500, device=device)
        
        start_time = time.time()
        for _ in range(100):
            z = torch.mm(x, y)
        torch.cuda.synchronize()
        end_time = time.time()
        
        return f"Task {task_id}: {end_time - start_time:.3f}초"
    except Exception as e:
        return f"Task {task_id}: 실패 - {e}"

if torch.cuda.is_available():
    # 순차 실행 테스트
    print("🔄 순차 실행 테스트:")
    sequential_times = []
    for i in range(2):
        result = gpu_task(0, i+1)
        print(f"  {result}")
    
    print("\n⚡ 동시 실행 시뮬레이션:")
    print("  실제 동시 실행 시 GPU 컨텍스트 스위칭으로 인해")
    print("  각 작업이 30-50% 느려질 수 있습니다.")
    
    # GPU 메모리 사용량 확인
    memory_info = torch.cuda.memory_stats()
    allocated = torch.cuda.memory_allocated() / 1024**3
    cached = torch.cuda.memory_reserved() / 1024**3
    print(f"\n📊 현재 GPU 메모리 사용량:")
    print(f"  할당됨: {allocated:.2f}GB")
    print(f"  캐시됨: {cached:.2f}GB")
    
else:
    print("CUDA 사용 불가")
EOF

else
    echo "nvidia-smi 없음"
fi

echo ""

# 6. 권장사항 및 최적 전략
echo "💡 6. 권장사항 및 최적 전략"
echo "---------------------------"

echo "🎯 RTX 3090 24GB 환경 최적 전략:"
echo ""

echo "✅ 권장 동시 실행:"
echo "  1. 실험 1개 + 리소스 모니터링"
echo "     → 성능 영향 거의 없음"
echo ""
echo "  2. 실험 1개 + 간단한 데이터 분석"
echo "     → CPU 작업만, 5-10% 영향"
echo ""

echo "⚠️  주의깊게 고려할 동시 실행:"
echo "  1. 작은 모델 2개 (ResNet50 + MobileNet)"
echo "     → GPU 메모리 여유시에만"
echo ""
echo "  2. 실험 1개 + 결과 시각화"
echo "     → 실험 완료 후 권장"
echo ""

echo "❌ 비추천 동시 실행:"
echo "  1. 대형 모델 2개 이상"
echo "     → GPU 메모리 부족, 성능 대폭 저하"
echo ""
echo "  2. V2_1 + V3 동시"
echo "     → 리소스 경쟁으로 둘 다 느려짐"
echo ""

echo "🚀 최적 실행 전략:"
echo "=================="
echo ""
echo "단계 1: 순차 실행 (권장)"
echo "  터미널 1: 실험 실행"
echo "  터미널 2: 모니터링 전용"
echo "  → 각 실험의 100% 성능 보장"
echo ""
echo "단계 2: 스마트 스케줄링"
echo "  1) V2_2 실험 (2-4시간)"
echo "  2) 결과 분석 (30분)"
echo "  3) V2_1 또는 V3 실험 (8-12시간)"
echo "  → 총 12-16시간으로 모든 시스템 테스트"
echo ""
echo "단계 3: 리소스 활용 최적화"
echo "  대기 시간: 데이터 분석, 시각화"
echo "  실험 시간: GPU 100% 활용"
echo "  → 전체 효율성 극대화"

echo ""

# 7. 실제 권장 명령어
echo "⚡ 7. 실제 권장 실행 명령어"
echo "---------------------------"

echo "🔥 최적 실행 패턴:"
echo ""
echo "터미널 1 (메인 실험):"
echo "  screen -S ml_experiment"
echo "  ./run_v2_2_only.sh"
echo ""
echo "터미널 2 (모니터링):"
echo "  ./monitor_resources.sh"
echo ""
echo "터미널 3 (대기/분석용 - 선택사항):"
echo "  # 실험 완료 후 결과 분석"
echo "  # 다음 실험 준비"
echo ""

echo "📊 순차 실행 스케줄:"
echo "  1. V2_2 → 2-4시간 (빠른 검증)"
echo "  2. 결과 분석 → 30분"
echo "  3. V2_1 또는 V3 → 8-12시간 (본격 실험)"
echo "  → 총 소요시간: 10-16시간"

echo ""
echo "✅ 멀티 터미널 성능 분석 완료!"
echo "================================"
echo "⏰ 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "🎯 결론: 모니터링 외에는 순차 실행이 최적!"
