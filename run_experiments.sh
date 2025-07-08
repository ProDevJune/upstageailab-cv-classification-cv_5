#!/bin/bash

# 크로스 플랫폼 HPO 시스템 통합 실행 스크립트
# macOS MPS / Ubuntu CUDA 자동 감지 및 최적화

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
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 프로젝트 루트 확인
check_project_root() {
    if [[ ! -f "codes/platform_detector.py" ]]; then
        log_error "프로젝트 루트에서 실행해주세요. codes/platform_detector.py 파일이 없습니다."
        exit 1
    fi
}

# Python 환경 확인
check_python_env() {
    log_info "Python 환경 확인 중..."
    
    if ! command -v python &> /dev/null; then
        log_error "Python이 설치되지 않았습니다."
        exit 1
    fi
    
    # PyTorch 설치 확인
    if ! python -c "import torch" 2>/dev/null; then
        log_error "PyTorch가 설치되지 않았습니다."
        log_info "requirements.txt를 확인하고 필요한 패키지를 설치해주세요."
        exit 1
    fi
    
    log_success "Python 환경 확인 완료"
}

# 플랫폼 감지
detect_platform() {
    log_info "플랫폼 감지 중..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux"
        PLATFORM_EMOJI="🐧"
        log_success "Linux 환경 감지"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
        PLATFORM_EMOJI="🍎"
        log_success "macOS 환경 감지"
    else
        PLATFORM="unknown"
        PLATFORM_EMOJI="❓"
        log_warning "알 수 없는 환경: $OSTYPE"
    fi
}

# 디바이스 감지 및 출력
detect_device() {
    log_info "컴퓨팅 디바이스 감지 중..."
    
    python -c "
import torch
import sys

if torch.cuda.is_available():
    print('🚀 CUDA 디바이스 감지')
    print(f'   GPU 개수: {torch.cuda.device_count()}')
    for i in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(i)
        memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f'   - GPU {i}: {name} ({memory:.1f} GB)')
    sys.exit(0)
elif torch.backends.mps.is_available():
    print('🍎 Apple Silicon MPS 감지')
    sys.exit(1)
else:
    print('💻 CPU 전용 환경')
    sys.exit(2)
"
    
    device_status=$?
    case $device_status in
        0) DEVICE_TYPE="cuda" ;;
        1) DEVICE_TYPE="mps" ;;
        2) DEVICE_TYPE="cpu" ;;
        *) DEVICE_TYPE="unknown" ;;
    esac
}

# 시스템 정보 상세 출력
show_system_info() {
    echo ""
    echo -e "${CYAN}🖥️  시스템 정보 상세${NC}"
    echo "================================="
    python -c "
from codes.platform_detector import PlatformDetector
detector = PlatformDetector()
detector.print_system_summary()
"
}

# 메인 메뉴 출력
show_main_menu() {
    echo ""
    echo -e "${PURPLE}🚀 크로스 플랫폼 HPO 시스템${NC}"
    echo "================================="
    echo -e "플랫폼: ${PLATFORM_EMOJI} ${PLATFORM^} + ${DEVICE_TYPE^^}"
    echo ""
    echo "📋 실행 옵션:"
    echo "1) ⚡ 빠른 실험 (20개, 30분/실험)"
    echo "2) 🔬 전체 실험 (50개, 1시간/실험)" 
    echo "3) 🎯 타겟 실험 (사용자 정의)"
    echo ""
    echo "📊 분석 도구:"
    echo "4) 📈 실험 결과 요약"
    echo "5) 🏆 상위 실험 조회"
    echo "6) 📊 하이퍼파라미터 분석"
    echo "7) 📉 결과 시각화"
    echo "8) 🎯 설정 추천"
    echo "9) 📄 분석 리포트 생성"
    echo ""
    echo "🔧 시스템 관리:"
    echo "10) 🖥️  시스템 정보 상세"
    echo "11) 🗑️  오래된 실험 정리"
    echo "12) ⚙️  플랫폼별 설정 생성"
    echo ""
    echo "0) 🚪 종료"
    echo ""
}

# 실험 실행 함수
run_experiment() {
    local exp_type=$1
    local max_exp=${2:-20}
    
    log_info "$exp_type 실험 시작 (최대 ${max_exp}개)"
    log_info "플랫폼: $PLATFORM + $DEVICE_TYPE"
    
    # 실험 전 확인
    echo ""
    echo -e "${YELLOW}⚠️  실험 시작 전 확인사항:${NC}"
    echo "- 실험 타입: $exp_type"
    echo "- 최대 실험 수: $max_exp"
    echo "- 예상 소요 시간: $(( max_exp * 30 ))분 (대략)"
    echo "- 결과 저장: experiment_results.csv"
    echo ""
    
    read -p "계속 진행하시겠습니까? (y/N): " confirm
    
    if [[ $confirm != "y" && $confirm != "Y" ]]; then
        log_info "실험 취소됨"
        return
    fi
    
    # Python 실험 실행
    log_info "실험 시작..."
    python codes/auto_experiment_basic.py \
        --type "$exp_type" \
        --max "$max_exp" \
        --method "smart_grid"
    
    if [[ $? -eq 0 ]]; then
        log_success "실험 완료!"
        echo ""
        echo "📊 빠른 결과 요약:"
        python codes/experiment_tracker.py --action summary
    else
        log_error "실험 중 오류 발생"
    fi
}

# 분석 도구 실행
run_analysis() {
    local action=$1
    local extra_args="${@:2}"
    
    log_info "$action 분석 실행 중..."
    python codes/experiment_tracker.py --action "$action" $extra_args
}

# 플랫폼별 설정 생성
generate_platform_config() {
    log_info "플랫폼별 최적화 설정 생성 중..."
    
    python -c "
from codes.platform_detector import PlatformDetector
from codes.enhanced_config_manager import EnhancedConfigManager

detector = PlatformDetector()
config_manager = EnhancedConfigManager(detector)

# 빠른 실험용 설정
quick_config = config_manager.generate_platform_config('quick')
quick_path = config_manager.save_platform_config(quick_config, 'config_quick_optimized.yaml')
print(f'✅ 빠른 실험용 설정: {quick_path}')

# 전체 실험용 설정
full_config = config_manager.generate_platform_config('full')
full_path = config_manager.save_platform_config(full_config, 'config_full_optimized.yaml')
print(f'✅ 전체 실험용 설정: {full_path}')

# 플랫폼 요약 출력
summary = config_manager.get_platform_summary()
print('\n📊 플랫폼 최적화 요약:')
for key, value in summary.items():
    print(f'   {key}: {value}')
"
    
    if [[ $? -eq 0 ]]; then
        log_success "플랫폼별 설정 생성 완료"
    else
        log_error "설정 생성 중 오류 발생"
    fi
}

# 실험 데이터 정리
cleanup_experiments() {
    log_info "오래된 실험 데이터 정리..."
    
    read -p "몇 일 전 데이터를 정리하시겠습니까? (기본값: 7): " days
    days=${days:-7}
    
    python codes/experiment_tracker.py --action cleanup --days "$days"
}

# 사용자 입력 처리
handle_user_input() {
    local choice=$1
    
    case $choice in
        1)
            run_experiment "quick" 20
            ;;
        2)
            run_experiment "full" 50
            ;;
        3)
            echo ""
            read -p "실험 타입 입력 (quick/full/targeted): " exp_type
            read -p "최대 실험 수 입력: " max_exp
            exp_type=${exp_type:-quick}
            max_exp=${max_exp:-20}
            run_experiment "$exp_type" "$max_exp"
            ;;
        4)
            run_analysis "summary"
            ;;
        5)
            read -p "상위 몇 개 실험을 조회하시겠습니까? (기본값: 10): " n
            n=${n:-10}
            run_analysis "top" "--n $n"
            ;;
        6)
            run_analysis "analyze"
            ;;
        7)
            run_analysis "visualize"
            ;;
        8)
            run_analysis "recommend"
            ;;
        9)
            run_analysis "report"
            ;;
        10)
            show_system_info
            ;;
        11)
            cleanup_experiments
            ;;
        12)
            generate_platform_config
            ;;
        0)
            log_info "시스템을 종료합니다. 👋"
            exit 0
            ;;
        *)
            log_error "잘못된 선택입니다. 다시 시도해주세요."
            ;;
    esac
}

# 메인 루프
main_loop() {
    while true; do
        show_main_menu
        read -p "선택하세요 (0-12): " choice
        echo ""
        
        handle_user_input "$choice"
        
        echo ""
        read -p "Enter 키를 눌러 메뉴로 돌아가세요..."
    done
}

# 초기 설정 확인
initial_setup() {
    log_info "초기 설정 확인 중..."
    
    # 필요한 디렉토리 생성
    mkdir -p codes/practice
    mkdir -p analysis_results
    mkdir -p data/submissions
    mkdir -p logs
    mkdir -p models
    
    # practice 디렉토리가 비어있으면 초기화
    if [[ ! -f "codes/practice/__init__.py" ]]; then
        touch "codes/practice/__init__.py"
        log_success "practice 디렉토리 초기화 완료"
    fi
    
    log_success "초기 설정 완료"
}

# 스크립트 시작점
main() {
    echo -e "${CYAN}🚀 크로스 플랫폼 HPO 시스템 시작${NC}"
    echo "========================================="
    
    # 기본 검사들
    check_project_root
    check_python_env
    detect_platform
    detect_device
    initial_setup
    
    echo ""
    log_success "시스템 초기화 완료!"
    
    # 시작 옵션
    echo ""
    echo "🎯 시작 옵션:"
    echo "1) 메뉴로 바로 이동"
    echo "2) 시스템 정보 먼저 확인"
    echo ""
    read -p "선택하세요 (1-2, 기본값: 1): " start_option
    start_option=${start_option:-1}
    
    if [[ $start_option == "2" ]]; then
        show_system_info
        echo ""
        read -p "Enter 키를 눌러 메뉴로 이동하세요..."
    fi
    
    # 메인 루프 시작
    main_loop
}

# 스크립트 실행
# 파라미터가 있으면 직접 실행, 없으면 대화형 모드
if [[ $# -gt 0 ]]; then
    # 명령줄 인자로 직접 실행
    case $1 in
        "quick")
            check_project_root
            check_python_env
            detect_platform
            detect_device
            initial_setup
            run_experiment "quick" "${2:-20}"
            ;;
        "full")
            check_project_root
            check_python_env
            detect_platform
            detect_device
            initial_setup
            run_experiment "full" "${2:-50}"
            ;;
        "summary")
            check_project_root
            check_python_env
            run_analysis "summary"
            ;;
        "info")
            check_project_root
            check_python_env
            detect_platform
            detect_device
            show_system_info
            ;;
        *)
            echo "사용법: $0 [quick|full|summary|info] [max_experiments]"
            echo "또는 인자 없이 실행하여 대화형 모드 사용"
            exit 1
            ;;
    esac
else
    # 대화형 모드
    main
fi
