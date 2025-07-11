#!/bin/bash
# 실시간 리소스 모니터링 스크립트

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

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
    
    # 현재 실행 중인 ML 실험 프로세스 찾기
    echo ""
    echo "🔬 ML 실험 프로세스:"
    ml_processes=$(ps aux | grep -E "(gemini_main|experiment)" | grep -v grep | wc -l)
    if [ $ml_processes -gt 0 ]; then
        echo "   🟢 ML 실험 실행 중: ${ml_processes}개"
        ps aux | grep -E "(gemini_main|experiment)" | grep -v grep | awk '{printf("   PID %s: %s\n", $2, $11)}'
    else
        echo "   ⚪ ML 실험 프로세스 없음"
    fi
    
    # 로드 평균
    echo ""
    echo "⚡ 시스템 부하:"
    uptime | awk '{printf("   로드 평균: %s %s %s\n", $(NF-2), $(NF-1), $NF)}'
    
    echo ""
    echo "📝 모니터링 명령어:"
    echo "   실험 상태: ./quick_safety_check.sh"
    echo "   실험 시작: ./run_v2_2_only.sh"
    echo "   로그 확인: tail -f logs/*.log"
    
    sleep 30
done
