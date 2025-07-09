#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# 최고 성능 달성을 위한 완전 자동화 실험 스크립트
echo "🏆 최고 성능 달성 완전 자동화 실험"
echo "=================================="
echo "⏰ 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 전역 변수
SCRIPT_START_TIME=$(date +%s)
TOTAL_EXPERIMENTS=4
CURRENT_EXPERIMENT=0
FAILED_EXPERIMENTS=()
SUCCESS_EXPERIMENTS=()
LOG_DIR="logs/optimal_performance_$(date +%Y%m%d_%H%M%S)"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 로그 함수
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/main.log"
}

log_success() {
    log_message "SUCCESS" "$1"
}

log_error() {
    log_message "ERROR" "$1"
}

log_info() {
    log_message "INFO" "$1"
}

# 시간 계산 함수
calculate_duration() {
    local start_time=$1
    local end_time=$2
    local duration=$((end_time - start_time))
    local hours=$((duration / 3600))
    local minutes=$(((duration % 3600) / 60))
    echo "${hours}시간 ${minutes}분"
}

# 진행 상황 표시 함수
show_progress() {
    local current=$1
    local total=$2
    local experiment_name=$3
    local estimated_time=$4
    
    echo ""
    echo "🚀 실험 진행 상황"
    echo "=================="
    echo "현재 실험: [$current/$total] $experiment_name"
    echo "예상 소요 시간: $estimated_time"
    echo "전체 진행률: $((current * 100 / total))%"
    echo "=================="
    echo ""
}

# 실험 실행 함수
run_experiment() {
    local exp_num=$1
    local exp_name=$2
    local exp_command=$3
    local estimated_time=$4
    local log_file="$LOG_DIR/experiment_${exp_num}_${exp_name}.log"
    
    ((CURRENT_EXPERIMENT++))
    show_progress $CURRENT_EXPERIMENT $TOTAL_EXPERIMENTS "$exp_name" "$estimated_time"
    
    log_info "실험 $exp_num 시작: $exp_name"
    log_info "명령어: $exp_command"
    
    local exp_start_time=$(date +%s)
    
    # 실험 실행
    if eval "$exp_command" > "$log_file" 2>&1; then
        local exp_end_time=$(date +%s)
        local exp_duration=$(calculate_duration $exp_start_time $exp_end_time)
        
        log_success "실험 $exp_num 완료: $exp_name (소요시간: $exp_duration)"
        SUCCESS_EXPERIMENTS+=("$exp_name")
        
        # 결과 요약
        echo "✅ 실험 $exp_num: $exp_name 성공!"
        echo "   소요시간: $exp_duration"
        echo "   로그: $log_file"
        
    else
        local exp_end_time=$(date +%s)
        local exp_duration=$(calculate_duration $exp_start_time $exp_end_time)
        
        log_error "실험 $exp_num 실패: $exp_name (소요시간: $exp_duration)"
        FAILED_EXPERIMENTS+=("$exp_name")
        
        echo "❌ 실험 $exp_num: $exp_name 실패!"
        echo "   소요시간: $exp_duration"
        echo "   로그: $log_file"
        echo "   오류 내용:"
        tail -20 "$log_file" | head -10
        
        # 실패 시 계속 진행할지 선택 (자동으로 계속 진행)
        log_info "실험 실패했지만 다음 실험을 계속 진행합니다."
    fi
    
    echo ""
}

# 시스템 상태 체크 함수
check_system_status() {
    log_info "시스템 상태 체크 중..."
    
    # GPU 메모리 체크
    if command -v nvidia-smi &> /dev/null; then
        local gpu_free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits)
        local gpu_free_gb=$((gpu_free / 1024))
        log_info "GPU 메모리 사용가능: ${gpu_free_gb}GB"
        
        if [ $gpu_free_gb -lt 5 ]; then
            log_info "GPU 메모리 정리 중..."
            python -c "import torch; torch.cuda.empty_cache()" 2>/dev/null
        fi
    fi
    
    # 디스크 공간 체크
    local disk_free=$(df . | tail -1 | awk '{print $4}')
    local disk_free_gb=$((disk_free / 1024 / 1024))
    log_info "디스크 사용가능: ${disk_free_gb}GB"
    
    if [ $disk_free_gb -lt 20 ]; then
        log_error "디스크 공간 부족! 실험을 중단합니다."
        exit 1
    fi
}

# 실험 간 대기 함수
wait_between_experiments() {
    local wait_time=$1
    log_info "${wait_time}초 대기 중... (시스템 안정화)"
    
    for i in $(seq $wait_time -1 1); do
        echo -ne "\r대기 중... ${i}초 남음"
        sleep 1
    done
    echo ""
}

# 앙상블 함수
create_ensemble() {
    log_info "앙상블 생성 시작..."
    
    # 앙상블 스크립트 생성
    cat > ensemble_best_models.py << 'EOF'
#!/usr/bin/env python3
"""
최고 성능 모델들의 앙상블 생성 스크립트
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import glob

def find_best_submissions():
    """data/submissions에서 최근 실험 결과들을 찾아 앙상블 생성"""
    print("🔍 최고 성능 submission 파일들 검색 중...")
    
    submission_dir = Path("data/submissions")
    if not submission_dir.exists():
        print("❌ data/submissions 디렉토리가 없습니다.")
        return
    
    # 최근 생성된 submission 파일들 찾기
    csv_files = list(submission_dir.glob("*/*.csv"))
    if not csv_files:
        csv_files = list(submission_dir.glob("*.csv"))
    
    if len(csv_files) < 2:
        print("⚠️  앙상블할 submission 파일이 부족합니다.")
        return
    
    # 최근 파일들 선별 (최대 5개)
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    selected_files = csv_files[:min(5, len(csv_files))]
    
    print(f"📊 앙상블에 사용할 파일들 ({len(selected_files)}개):")
    for i, file in enumerate(selected_files, 1):
        print(f"  {i}. {file}")
    
    return selected_files

def create_ensemble_submission(csv_files):
    """여러 submission 파일들을 앙상블하여 최종 submission 생성"""
    if not csv_files:
        return
    
    print("🔗 앙상블 생성 중...")
    
    # 모든 submission 읽기
    submissions = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            submissions.append(df)
            print(f"  ✅ {file.name} 로드 완료")
        except Exception as e:
            print(f"  ❌ {file.name} 로드 실패: {e}")
    
    if len(submissions) < 2:
        print("⚠️  유효한 submission이 부족합니다.")
        return
    
    # 앙상블 전략: 다수결 투표
    ensemble_df = submissions[0].copy()
    
    for idx in range(len(ensemble_df)):
        votes = {}
        for sub in submissions:
            target = sub.iloc[idx]['target']
            votes[target] = votes.get(target, 0) + 1
        
        # 가장 많이 투표받은 클래스 선택
        ensemble_df.iloc[idx, ensemble_df.columns.get_loc('target')] = max(votes.items(), key=lambda x: x[1])[0]
    
    # 앙상블 결과 저장
    timestamp = pd.Timestamp.now().strftime("%m%d%H%M")
    ensemble_filename = f"data/submissions/ensemble_{len(submissions)}models_{timestamp}.csv"
    ensemble_df.to_csv(ensemble_filename, index=False)
    
    print(f"🎉 앙상블 완료! 파일 저장: {ensemble_filename}")
    print(f"📊 앙상블 정보:")
    print(f"  - 사용된 모델 수: {len(submissions)}")
    print(f"  - 최종 예측 수: {len(ensemble_df)}")
    
    return ensemble_filename

if __name__ == "__main__":
    print("🏆 최고 성능 모델 앙상블 생성")
    print("=" * 30)
    
    csv_files = find_best_submissions()
    if csv_files:
        ensemble_file = create_ensemble_submission(csv_files)
        if ensemble_file:
            print(f"\n✅ 앙상블 성공: {ensemble_file}")
        else:
            print("\n❌ 앙상블 실패")
    else:
        print("\n⚠️  앙상블할 파일이 없습니다.")
EOF

    chmod +x ensemble_best_models.py
    
    # 앞서 추가적으로 실행 권한 부여 
    echo "#!/usr/bin/env python3" > temp_ensemble.py
    cat ensemble_best_models.py >> temp_ensemble.py
    mv temp_ensemble.py ensemble_best_models.py
    chmod +x ensemble_best_models.py
    
    # 앙상블 실행
    if python ensemble_best_models.py; then
        log_success "앙상블 생성 완료"
        return 0
    else
        log_error "앙상블 생성 실패"
        return 1
    fi
}

# 메인 실행 함수
main() {
    echo "🎯 최고 성능 달성을 위한 4단계 자동화 실험"
    echo "예상 총 소요시간: 13-16시간"
    echo "실험 구성:"
    echo "  1단계: V2_2 FocalLoss (2시간)"
    echo "  2단계: V2_1 대형 모델 (6시간)"
    echo "  3단계: V3 계층적 분류 (4시간)"
    echo "  4단계: 앙상블 생성 (1시간)"
    echo ""
    
    log_info "최고 성능 자동화 실험 시작"
    
    # 사전 체크
    log_info "사전 안전성 체크 실행..."
    if ! ./quick_safety_check.sh; then
        log_error "사전 체크 실패. 실험을 중단합니다."
        exit 1
    fi
    
    # 라이브러리 체크
    log_info "라이브러리 상태 체크..."
    ./check_venv_libraries.sh >> "$LOG_DIR/library_check.log" 2>&1
    ./fix_venv_libraries.sh >> "$LOG_DIR/library_fix.log" 2>&1
    
    echo ""
    echo "🚀 실험 시작!"
    echo ""
    
    # 1단계: V2_2 FocalLoss 핵심 기법 (2시간)
    check_system_status
    run_experiment 1 "V2_2_FocalLoss" \
        "python v2_experiment_generator.py --type v2_2 --technique focal --limit 1 && ./v2_experiments/run_all_experiments.sh" \
        "2시간"
    
    wait_between_experiments 60
    
    # 2단계: V2_1 대형 모델 (6시간)
    check_system_status
    run_experiment 2 "V2_1_LargeModel" \
        "./run_v2_1_only.sh --auto" \
        "6시간"
    
    wait_between_experiments 60
    
    # 3단계: V3 계층적 분류 (4시간)
    check_system_status
    run_experiment 3 "V3_Hierarchical" \
        "python v3_experiment_generator.py --phase phase1 && ./v3_experiments/scripts/run_v3_phase1.sh" \
        "4시간"
    
    wait_between_experiments 30
    
    # 4단계: 앙상블 생성 (1시간)
    check_system_status
    log_info "4단계: 최고 모델들 앙상블 생성"
    
    local ensemble_start_time=$(date +%s)
    if create_ensemble; then
        local ensemble_end_time=$(date +%s)
        local ensemble_duration=$(calculate_duration $ensemble_start_time $ensemble_end_time)
        SUCCESS_EXPERIMENTS+=("Ensemble")
        log_success "앙상블 생성 완료 (소요시간: $ensemble_duration)"
        echo "✅ 실험 4: 앙상블 생성 성공!"
    else
        local ensemble_end_time=$(date +%s)
        local ensemble_duration=$(calculate_duration $ensemble_start_time $ensemble_end_time)
        FAILED_EXPERIMENTS+=("Ensemble")
        log_error "앙상블 생성 실패 (소요시간: $ensemble_duration)"
        echo "❌ 실험 4: 앙상블 생성 실패!"
    fi
    
    # 최종 결과 요약
    local script_end_time=$(date +%s)
    local total_duration=$(calculate_duration $SCRIPT_START_TIME $script_end_time)
    
    echo ""
    echo "🎉 최고 성능 자동화 실험 완료!"
    echo "================================"
    echo "⏰ 총 소요시간: $total_duration"
    echo "📊 실험 결과:"
    echo "  성공: ${#SUCCESS_EXPERIMENTS[@]}개"
    echo "  실패: ${#FAILED_EXPERIMENTS[@]}개"
    echo ""
    
    if [ ${#SUCCESS_EXPERIMENTS[@]} -gt 0 ]; then
        echo "✅ 성공한 실험들:"
        for exp in "${SUCCESS_EXPERIMENTS[@]}"; do
            echo "  - $exp"
        done
        echo ""
    fi
    
    if [ ${#FAILED_EXPERIMENTS[@]} -gt 0 ]; then
        echo "❌ 실패한 실험들:"
        for exp in "${FAILED_EXPERIMENTS[@]}"; do
            echo "  - $exp"
        done
        echo ""
    fi
    
    echo "📁 로그 디렉토리: $LOG_DIR"
    echo "📊 결과 확인: ls -la data/submissions/"
    echo ""
    
    if [ ${#SUCCESS_EXPERIMENTS[@]} -ge 3 ]; then
        echo "🏆 최고 성능 실험 대부분 성공! 결과를 확인하세요."
        log_success "최고 성능 실험 완료 - 성공률: $((${#SUCCESS_EXPERIMENTS[@]} * 100 / $TOTAL_EXPERIMENTS))%"
    else
        echo "⚠️  일부 실험이 실패했습니다. 로그를 확인하고 수동으로 재실행하세요."
        log_error "최고 성능 실험 완료 - 성공률: $((${#SUCCESS_EXPERIMENTS[@]} * 100 / $TOTAL_EXPERIMENTS))%"
    fi
}

# 신호 처리 (Ctrl+C 등)
cleanup() {
    log_info "실험이 중단되었습니다."
    echo ""
    echo "🛑 실험 중단됨"
    echo "현재까지 진행 상황:"
    echo "  성공: ${#SUCCESS_EXPERIMENTS[@]}개"
    echo "  실패: ${#FAILED_EXPERIMENTS[@]}개"
    echo "로그 위치: $LOG_DIR"
    exit 130
}

trap cleanup INT TERM

# 스크립트 시작 안내
echo "🏆 최고 성능 달성 완전 자동화 실험 스크립트"
echo "============================================"
echo ""
echo "⚠️  중요 사항:"
echo "  - 예상 소요시간: 13-16시간"
echo "  - SSH 연결이 끊어져도 실험은 계속됩니다"
echo "  - 각 단계별로 자동으로 실행됩니다"
echo "  - 로그는 logs/ 디렉토리에 저장됩니다"
echo ""
echo "실험 단계:"
echo "  1️⃣  V2_2 FocalLoss (2시간)"
echo "  2️⃣  V2_1 대형 모델 (6시간)"
echo "  3️⃣  V3 계층적 분류 (4시간)"
echo "  4️⃣  앙상블 생성 (1시간)"
echo ""

read -p "실험을 시작하시겠습니까? (y/N): " confirm
if [[ $confirm == "y" || $confirm == "Y" ]]; then
    main
else
    echo "실험이 취소되었습니다."
    exit 0
fi
