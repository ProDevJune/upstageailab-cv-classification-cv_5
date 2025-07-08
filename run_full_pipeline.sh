#!/bin/bash
# CV Classification 완전 재실행 마스터 스크립트
# 개선된 train.csv 기반 순차 실행

set -e  # 오류 발생시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로그 함수들
log_header() {
    echo -e "\n${PURPLE}============================================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}============================================================${NC}"
}

log_phase() {
    echo -e "\n${CYAN}🚀 $1${NC}"
    echo -e "${CYAN}------------------------------------------------------------${NC}"
}

log_step() {
    echo -e "\n${BLUE}📋 $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 타임스탬프 함수
get_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# 진행률 표시 함수
show_progress() {
    local current=$1
    local total=$2
    local step_name=$3
    local percent=$((current * 100 / total))
    
    echo -e "\n${YELLOW}📊 진행률: [$percent%] ($current/$total) - $step_name${NC}"
}

# 메인 실행 함수
main() {
    log_header "🎯 CV Classification 개선된 데이터 완전 재실행"
    echo "시작 시간: $(get_timestamp)"
    
    # 프로젝트 디렉토리로 이동
    cd 
    
    # 총 단계 수
    local total_steps=8
    local current_step=0
    
    # ===============================
    # Phase 1: 개별 모델 재학습
    # ===============================
    log_phase "Phase 1: 개별 모델 재학습 (3단계)"
    
    # 1.1 EfficientNet-B4
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "EfficientNet-B4 학습"
    log_step "Phase 1.1: EfficientNet-B4 재학습"
    
    echo "🔧 실행 명령: ./run_absolute.sh"
    echo "📝 예상 메모: EfficientNet-B4 - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    echo "🎯 목표: 서버 0.865+ (개선 +0.003)"
    
    if [ -f "./run_absolute.sh" ]; then
        log_step "EfficientNet-B4 학습 시작..."
        ./run_absolute.sh
        if [ $? -eq 0 ]; then
            log_success "EfficientNet-B4 학습 완료"
        else
            log_error "EfficientNet-B4 학습 실패"
            exit 1
        fi
    else
        log_error "run_absolute.sh 파일을 찾을 수 없습니다"
        exit 1
    fi
    
    # 결과 확인
    log_step "B4 결과 파일 확인..."
    python execution_tracker_v2.py
    
    # 1.2 EfficientNet-B3
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "EfficientNet-B3 학습"
    log_step "Phase 1.2: EfficientNet-B3 재학습"
    
    echo "🔧 실행 명령: ./run_b3.sh"
    echo "📝 예상 메모: EfficientNet-B3 - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    echo "🎯 목표: 서버 0.855+ (개선 +0.002)"
    
    if [ -f "./run_b3.sh" ]; then
        log_step "EfficientNet-B3 학습 시작..."
        ./run_b3.sh
        if [ $? -eq 0 ]; then
            log_success "EfficientNet-B3 학습 완료"
        else
            log_error "EfficientNet-B3 학습 실패"
            exit 1
        fi
    else
        log_error "run_b3.sh 파일을 찾을 수 없습니다"
        exit 1
    fi
    
    # 1.3 ConvNeXt-Base
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "ConvNeXt-Base 학습"
    log_step "Phase 1.3: ConvNeXt-Base 재학습"
    
    echo "🔧 실행 명령: ./run_convnext.sh"
    echo "📝 예상 메모: ConvNeXt-Base - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    echo "🎯 목표: 서버 0.820+ (개선 +0.004)"
    
    if [ -f "./run_convnext.sh" ]; then
        log_step "ConvNeXt-Base 학습 시작..."
        ./run_convnext.sh
        if [ $? -eq 0 ]; then
            log_success "ConvNeXt-Base 학습 완료"
        else
            log_error "ConvNeXt-Base 학습 실패"
            exit 1
        fi
    else
        log_error "run_convnext.sh 파일을 찾을 수 없습니다"
        exit 1
    fi
    
    log_success "Phase 1 완료: 모든 개별 모델 학습 완료"
    
    # ===============================
    # Phase 2: 앙상블 구성
    # ===============================
    log_phase "Phase 2: 앙상블 구성 (3단계)"
    
    # 2.1 B4 단독 제출 준비
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "B4 단독 제출 준비"
    log_step "Phase 2.1: EfficientNet-B4 단독 제출 준비"
    
    # 최신 B4 결과 찾기
    B4_RESULT=$(find data/submissions -name "*efficientnet_b4*" -type d | sort | tail -1)
    if [ -n "$B4_RESULT" ]; then
        B4_CSV=$(find "$B4_RESULT" -name "*.csv" | head -1)
        log_success "B4 결과 파일 발견: $B4_CSV"
        echo "📝 제출 메모: EfficientNet-B4 단독 (개선된 데이터v2 최고성능)"
    else
        log_warning "B4 결과 파일을 찾을 수 없습니다"
    fi
    
    # 2.2 2모델 앙상블
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "2모델 앙상블 (B4+B3)"
    log_step "Phase 2.2: 2모델 앙상블 (B4+B3)"
    
    echo "🔧 실행 명령: python ensemble_2models_v2.py"
    echo "📝 예상 메모: 2MODELS 앙상블 B4+B3 - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    echo "📊 예상 성능: 서버 0.860+ (vs B4 단독)"
    
    if [ -f "ensemble_2models_v2.py" ]; then
        log_step "2모델 앙상블 시작..."
        python ensemble_2models_v2.py
        if [ $? -eq 0 ]; then
            log_success "2모델 앙상블 완료"
            # 생성된 파일 찾기
            ENSEMBLE_2_FILE=$(ls -t ensemble_2models_v2_*.csv 2>/dev/null | head -1)
            if [ -n "$ENSEMBLE_2_FILE" ]; then
                log_success "앙상블 파일 생성: $ENSEMBLE_2_FILE"
            fi
        else
            log_error "2모델 앙상블 실패"
            exit 1
        fi
    else
        log_error "ensemble_2models_v2.py 파일을 찾을 수 없습니다"
        exit 1
    fi
    
    # 2.3 3모델 앙상블
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "3모델 앙상블 (B4+B3+ConvNeXt)"
    log_step "Phase 2.3: 3모델 앙상블 (B4+B3+ConvNeXt)"
    
    echo "🔧 실행 명령: python ensemble_3models_v2.py"
    echo "📝 예상 메모: 3MODELS 앙상블 B4+B3+ConvNeXt - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    echo "📊 예상 성능: 서버 0.865+ (최종 목표)"
    
    if [ -f "ensemble_3models_v2.py" ]; then
        log_step "3모델 앙상블 시작..."
        python ensemble_3models_v2.py
        if [ $? -eq 0 ]; then
            log_success "3모델 앙상블 완료"
            # 생성된 파일 찾기
            ENSEMBLE_3_FILE=$(ls -t ensemble_3models_v2_*.csv 2>/dev/null | head -1)
            if [ -n "$ENSEMBLE_3_FILE" ]; then
                log_success "앙상블 파일 생성: $ENSEMBLE_3_FILE"
            fi
        else
            log_error "3모델 앙상블 실패"
            exit 1
        fi
    else
        log_error "ensemble_3models_v2.py 파일을 찾을 수 없습니다"
        exit 1
    fi
    
    log_success "Phase 2 완료: 모든 앙상블 구성 완료"
    
    # ===============================
    # 최종 결과 정리
    # ===============================
    current_step=$((current_step + 1))
    show_progress $current_step $total_steps "최종 결과 정리"
    log_phase "최종 결과 및 제출 정보"
    
    echo -e "\n${GREEN}🎉 전체 파이프라인 완료! ${NC}"
    echo "완료 시간: $(get_timestamp)"
    
    # 생성된 모든 결과 파일 표시
    log_step "📁 생성된 제출 파일들:"
    
    # B4 단독
    if [ -n "$B4_CSV" ]; then
        echo -e "${BLUE}1. B4 단독:${NC} $B4_CSV"
        echo -e "   📝 메모: EfficientNet-B4 단독 (개선된 데이터v2 최고성능)"
    fi
    
    # 2모델 앙상블
    if [ -n "$ENSEMBLE_2_FILE" ]; then
        echo -e "${BLUE}2. 2모델 앙상블:${NC} $ENSEMBLE_2_FILE"
        echo -e "   📝 메모: 2MODELS 앙상블 B4+B3 - 320px + Minimal aug - No TTA (개진된 데이터v2)"
    fi
    
    # 3모델 앙상블
    if [ -n "$ENSEMBLE_3_FILE" ]; then
        echo -e "${BLUE}3. 3모델 앙상블:${NC} $ENSEMBLE_3_FILE"
        echo -e "   📝 메모: 3MODELS 앙상블 B4+B3+ConvNeXt - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    fi
    
    # 추가 정보
    log_step "📊 성능 추적 및 분석:"
    echo "• python execution_tracker_v2.py  # 상세 결과 확인"
    echo "• experiment_results_v2.json      # JSON 로그"
    echo "• submission_paths_v2.csv         # CSV 로그"
    
    # 제출 순서 안내
    log_step "🚀 제출 권장 순서:"
    echo "1️⃣ B4 단독 먼저 제출 (베이스라인 확인)"
    echo "2️⃣ 2모델 앙상블 제출 (개선 확인)"
    echo "3️⃣ 3모델 앙상블 제출 (최종 성능)"
    
    # 최종 체크리스트
    log_step "✅ 완료 체크리스트:"
    echo "[ ✅ ] EfficientNet-B4 재학습"
    echo "[ ✅ ] EfficientNet-B3 재학습"
    echo "[ ✅ ] ConvNeXt-Base 재학습"
    echo "[ ✅ ] 2모델 앙상블 구성"
    echo "[ ✅ ] 3모델 앙상블 구성"
    echo "[ ✅ ] 제출 파일 준비"
    
    log_success "🎯 모든 과정이 성공적으로 완료되었습니다!"
    echo -e "\n${PURPLE}이제 AIStages에 순차적으로 제출하고 결과를 확인하세요! 🚀${NC}"
}

# 인터럽트 처리
trap 'echo -e "\n${RED}❌ 스크립트가 중단되었습니다${NC}"; exit 1' INT

# 스크립트 시작 확인
echo -e "${YELLOW}🤔 전체 파이프라인을 실행하시겠습니까? (약 2-3시간 소요예상)${NC}"
echo -e "${YELLOW}계속하려면 Enter를 누르세요. 취소하려면 Ctrl+C를 누르세요.${NC}"
read -r

# 메인 함수 실행
main

echo -e "\n${GREEN}🎉 스크립트 실행 완료! 🎉${NC}"
