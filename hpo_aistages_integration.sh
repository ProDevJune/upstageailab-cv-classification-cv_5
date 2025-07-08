#!/bin/bash

# HPO + AIStages 통합 실행 스크립트
# 로컬 실험부터 대회 서버 제출까지 전체 워크플로우 관리

echo "🎯 HPO + AIStages 통합 실험 시스템"
echo "====================================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function print_info() {
    echo -e "${BLUE}📋 $1${NC}"
}

function show_menu() {
    echo ""
    echo "🚀 작업을 선택하세요:"
    echo "1️⃣  새 HPO 실험 실행"
    echo "2️⃣  기존 실험 결과 확인"
    echo "3️⃣  AIStages 제출 후보 추천"
    echo "4️⃣  AIStages 제출 준비"
    echo "5️⃣  AIStages 결과 기록"
    echo "6️⃣  로컬 vs 서버 분석"
    echo "7️⃣  앙상블 후보 추천"
    echo "8️⃣  전체 리포트 생성"
    echo "0️⃣  종료"
    echo ""
}

function run_hpo_experiments() {
    print_info "HPO 실험 실행"
    
    echo "실험 타입을 선택하세요:"
    echo "1) quick (5-10개, 빠른 실험)"
    echo "2) medium (20개, 중간 실험)"
    echo "3) full (50개, 전체 실험)"
    
    read -p "선택 (1-3): " exp_type
    
    case $exp_type in
        1)
            python start_hpo.py --type quick --max 10
            ;;
        2)
            python codes/auto_experiment_basic.py --type quick --max 20
            ;;
        3)
            python codes/auto_experiment_basic.py --type full --max 50
            ;;
        *)
            print_error "잘못된 선택입니다."
            return
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_status "HPO 실험 완료"
        
        # 자동으로 결과 동기화
        python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
tracker.sync_from_basic_results()
tracker.print_enhanced_summary()
"
    else
        print_error "HPO 실험 실패"
    fi
}

function check_experiment_results() {
    print_info "실험 결과 확인"
    
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
tracker.sync_from_basic_results()
tracker.print_enhanced_summary()

print('\n🏆 로컬 성능 기준 상위 5개:')
import pandas as pd
try:
    df = pd.read_csv('enhanced_experiment_results.csv')
    completed = df[df['status'] == 'completed']
    if len(completed) > 0:
        top_5 = completed.nlargest(5, 'final_f1')[
            ['experiment_id', 'final_f1', 'model_name', 'lr', 'augmentation_level', 'TTA']
        ]
        print(top_5.to_string(index=False))
    else:
        print('완료된 실험이 없습니다.')
except FileNotFoundError:
    print('실험 결과 파일이 없습니다. 먼저 HPO 실험을 실행하세요.')
"
}

function recommend_submission_candidates() {
    print_info "AIStages 제출 후보 추천"
    
    echo "추천 전략을 선택하세요:"
    echo "1) best_local (로컬 성능 우선)"
    echo "2) diverse (다양한 설정 조합)"
    echo "3) conservative (과적합 위험 최소화)"
    
    read -p "선택 (1-3): " strategy
    
    case $strategy in
        1) strategy_name="best_local" ;;
        2) strategy_name="diverse" ;;
        3) strategy_name="conservative" ;;
        *) strategy_name="diverse" ;;
    esac
    
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
tracker.sync_from_basic_results()
candidates = tracker.get_submission_candidates('$strategy_name')
if not candidates.empty:
    print('🎯 제출 후보 실험들:')
    print(candidates.to_string(index=False))
    print('\n📝 제출 준비를 원하시면 메뉴 4번을 선택하세요.')
else:
    print('제출할 수 있는 실험이 없습니다.')
"
}

function prepare_aistages_submission() {
    print_info "AIStages 제출 준비"
    
    # 실험 ID 입력 받기
    echo "제출할 실험 ID를 입력하세요:"
    read -p "실험 ID: " experiment_id
    
    if [ -z "$experiment_id" ]; then
        print_error "실험 ID가 입력되지 않았습니다."
        return
    fi
    
    echo "제출 관련 메모 (선택사항):"
    read -p "메모: " notes
    
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
instructions = tracker.submit_to_aistages('$experiment_id', '$notes')
print(instructions)
"
    
    print_warning "제출 후 반드시 메뉴 5번으로 결과를 기록하세요!"
}

function record_aistages_result() {
    print_info "AIStages 결과 기록"
    
    echo "제출한 실험 ID를 입력하세요:"
    read -p "실험 ID: " experiment_id
    
    if [ -z "$experiment_id" ]; then
        print_error "실험 ID가 입력되지 않았습니다."
        return
    fi
    
    echo "AIStages Public Score를 입력하세요:"
    read -p "Public Score: " public_score
    
    if [ -z "$public_score" ]; then
        print_error "Public Score가 입력되지 않았습니다."
        return
    fi
    
    echo "Public 순위를 입력하세요 (선택사항, 비워두면 None):"
    read -p "Public Rank: " public_rank
    
    echo "Private Score를 입력하세요 (선택사항, 최종 순위 발표 후):"
    read -p "Private Score: " private_score
    
    echo "Private 순위를 입력하세요 (선택사항):"
    read -p "Private Rank: " private_rank
    
    echo "추가 메모 (선택사항):"
    read -p "메모: " notes
    
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()

# None 값 처리
public_rank = None if '$public_rank' == '' else int('$public_rank')
private_score = None if '$private_score' == '' else float('$private_score')
private_rank = None if '$private_rank' == '' else int('$private_rank')
notes = None if '$notes' == '' else '$notes'

tracker.record_aistages_result(
    experiment_id='$experiment_id',
    public_score=float('$public_score'),
    public_rank=public_rank,
    private_score=private_score,
    private_rank=private_rank,
    notes=notes
)

print('\n📊 업데이트된 요약:')
tracker.print_enhanced_summary()
"
    
    print_status "결과 기록 완료"
}

function analyze_local_vs_server() {
    print_info "로컬 vs 서버 점수 분석"
    
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
import pandas as pd

tracker = EnhancedExperimentTracker()
try:
    df = pd.read_csv('enhanced_experiment_results.csv')
    submitted = df[df['aistages_submitted'] == True]

    if len(submitted) < 2:
        print('분석을 위한 제출 데이터가 부족합니다 (최소 2개 필요).')
        print('현재 제출된 실험:', len(submitted), '개')
    else:
        print('📈 로컬 vs 서버 점수 상관관계 분석')
        print('=' * 50)
        
        correlation = submitted['final_f1'].corr(submitted['aistages_public_score'])
        mean_diff = submitted['score_difference_public'].mean()
        std_diff = submitted['score_difference_public'].std()
        
        print(f'상관계수: {correlation:.3f}')
        print(f'평균 점수 차이: {mean_diff:+.4f}')
        print(f'점수 차이 표준편차: {std_diff:.4f}')
        
        # 상관관계 해석
        if correlation > 0.8:
            print('✅ 매우 강한 상관관계 - 로컬 validation이 서버 성능을 잘 예측')
        elif correlation > 0.6:
            print('✅ 강한 상관관계 - 로컬 validation이 어느 정도 신뢰할 만함')
        elif correlation > 0.4:
            print('⚠️ 중간 상관관계 - 로컬 validation 개선이 필요할 수 있음')
        else:
            print('❌ 약한 상관관계 - 로컬 validation 전략 재검토 필요')
        
        # 과적합 분석
        overfitting = len(submitted[submitted['overfitting_risk'] == 'high'])
        print(f'\n⚠️ 과적합 위험 높은 실험: {overfitting}개')
        
        if overfitting > 0:
            print('과적합 의심 실험들:')
            high_risk = submitted[submitted['overfitting_risk'] == 'high']
            print(high_risk[['experiment_id', 'final_f1', 'aistages_public_score', 'score_difference_public']].to_string(index=False))
        
        # 시각화 생성
        try:
            tracker.create_correlation_plot()
        except Exception as e:
            print(f'시각화 생성 실패: {e}')

except FileNotFoundError:
    print('❌ 실험 결과 파일이 없습니다.')
except Exception as e:
    print(f'❌ 분석 중 오류 발생: {e}')
"
}

function recommend_ensemble_candidates() {
    print_info "앙상블 후보 추천"
    
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
import pandas as pd

tracker = EnhancedExperimentTracker()
try:
    df = pd.read_csv('enhanced_experiment_results.csv')
    submitted = df[df['aistages_submitted'] == True]

    if len(submitted) < 3:
        print('앙상블 분석을 위한 제출 데이터가 부족합니다 (최소 3개 필요).')
        print('현재 제출된 실험:', len(submitted), '개')
    else:
        print('🎯 앙상블 후보 추천')
        print('=' * 40)
        
        # 앙상블 추천 기준
        ensemble_candidates = df[df['recommended_for_ensemble'] == True]
        
        if len(ensemble_candidates) == 0:
            print('추천된 앙상블 후보가 없습니다.')
            print('상위 성능 모델들을 기반으로 추천:')
            top_models = submitted.nlargest(5, 'aistages_public_score')
            print(top_models[['experiment_id', 'aistages_public_score', 'model_name', 'lr', 'augmentation_level']].to_string(index=False))
        else:
            print(f'추천된 앙상블 후보: {len(ensemble_candidates)}개')
            print(ensemble_candidates[['experiment_id', 'aistages_public_score', 'final_f1', 'model_name', 'overfitting_risk']].to_string(index=False))
            
            # 앙상블 전략 추천
            print('\n📋 앙상블 전략 추천:')
            models = ensemble_candidates['model_name'].value_counts()
            print(f'1. 모델 다양성: {len(models)}개 모델 타입')
            print(f'2. 평균 서버 점수: {ensemble_candidates[\"aistages_public_score\"].mean():.4f}')
            print(f'3. 과적합 위험 낮은 모델: {len(ensemble_candidates[ensemble_candidates[\"overfitting_risk\"] == \"low\"])}개')

        # 최고 성과 전략 분석
        strategies = tracker.analyze_best_strategies()
        if 'best_models' in strategies:
            print('\n🏆 최고 성과 전략 분석:')
            print(f'최고 모델: {list(strategies[\"best_models\"].keys())}')
            print(f'최고 학습률: {list(strategies[\"best_learning_rates\"].keys())}')
            print(f'최고 증강 레벨: {list(strategies[\"best_augmentation\"].keys())}')

except FileNotFoundError:
    print('❌ 실험 결과 파일이 없습니다.')
except Exception as e:
    print(f'❌ 분석 중 오류 발생: {e}')
"
}

function generate_full_report() {
    print_info "전체 리포트 생성"
    
    echo "리포트 타입을 선택하세요:"
    echo "1) 간단 요약 리포트"
    echo "2) 제출용 상세 리포트"
    echo "3) 전체 분석 리포트"
    
    read -p "선택 (1-3): " report_type
    
    case $report_type in
        1)
            python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
tracker.sync_from_basic_results()
tracker.print_enhanced_summary()
"
            ;;
        2)
            echo "제출할 실험 ID들을 입력하세요 (쉼표로 구분):"
            read -p "실험 ID들: " experiment_ids
            
            python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
ids_input = '$experiment_ids'.replace(' ', '')
ids = ids_input.split(',') if ids_input else []
if ids and ids[0]:
    tracker.create_submission_report(ids, 'submission_report.html')
    print('📄 제출용 리포트 생성: submission_report.html')
else:
    print('❌ 실험 ID가 입력되지 않았습니다.')
"
            ;;
        3)
            python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
import pandas as pd
from datetime import datetime

tracker = EnhancedExperimentTracker()
tracker.sync_from_basic_results()

try:
    # 전체 분석 리포트 생성
    df = pd.read_csv('enhanced_experiment_results.csv')
    submitted = df[df['aistages_submitted'] == True]

    html_content = f'''
    <html>
    <head>
        <title>HPO + AIStages 전체 분석 리포트</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .success {{ background-color: #d4edda; }}
            .warning {{ background-color: #fff3cd; }}
            .danger {{ background-color: #f8d7da; }}
        </style>
    </head>
    <body>
        <h1>🎯 HPO + AIStages 전체 분석 리포트</h1>
        <p>생성일시: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}</p>
        
        <h2>📊 실험 현황</h2>
        <ul>
            <li>전체 HPO 실험: {len(df)}개</li>
            <li>완료된 실험: {len(df[df[\"status\"] == \"completed\"])}개</li>
            <li>AIStages 제출: {len(submitted)}개</li>
            <li>성공률: {len(df[df[\"status\"] == \"completed\"]) / len(df) * 100 if len(df) > 0 else 0:.1f}%</li>
        </ul>
    '''

    if len(submitted) > 0:
        correlation = submitted['final_f1'].corr(submitted['aistages_public_score']) if len(submitted) >= 2 else 0
        html_content += f'''
        <h2>🏆 AIStages 성과</h2>
        <ul>
            <li>최고 서버 점수: {submitted[\"aistages_public_score\"].max():.4f}</li>
            <li>평균 서버 점수: {submitted[\"aistages_public_score\"].mean():.4f}</li>
            <li>로컬-서버 상관관계: {correlation:.3f}</li>
            <li>과적합 위험 높음: {len(submitted[submitted[\"overfitting_risk\"] == \"high\"])}개</li>
        </ul>
        
        <h2>📈 제출된 실험 결과</h2>
        {submitted[[\"experiment_id\", \"aistages_public_score\", \"final_f1\", \"score_difference_public\", \"model_name\", \"overfitting_risk\"]].to_html(index=False)}
        '''

    completed = df[df['status'] == 'completed']
    if len(completed) > 0:
        html_content += f'''
        <h2>🔬 전체 완료 실험</h2>
        {completed[[\"experiment_id\", \"final_f1\", \"val_accuracy\", \"model_name\", \"lr\", \"augmentation_level\", \"TTA\"]].to_html(index=False)}
        '''

    html_content += '''
    </body>
    </html>
    '''

    with open('full_analysis_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print('📄 전체 분석 리포트 생성: full_analysis_report.html')

except FileNotFoundError:
    print('❌ 실험 결과 파일이 없습니다.')
except Exception as e:
    print(f'❌ 리포트 생성 중 오류 발생: {e}')
"
            ;;
        *)
            print_error "잘못된 선택입니다."
            ;;
    esac
}

# 메인 실행 루프
function main() {
    # 환경 확인
    if [ ! -f "experiment_results.csv" ] && [ ! -f "enhanced_experiment_results.csv" ]; then
        print_warning "실험 결과 파일이 없습니다. 먼저 HPO 실험을 실행하세요."
    fi
    
    while true; do
        show_menu
        read -p "선택하세요 (0-8): " choice
        
        case $choice in
            1)
                run_hpo_experiments
                ;;
            2)
                check_experiment_results
                ;;
            3)
                recommend_submission_candidates
                ;;
            4)
                prepare_aistages_submission
                ;;
            5)
                record_aistages_result
                ;;
            6)
                analyze_local_vs_server
                ;;
            7)
                recommend_ensemble_candidates
                ;;
            8)
                generate_full_report
                ;;
            0)
                print_status "시스템 종료"
                exit 0
                ;;
            *)
                print_error "잘못된 선택입니다. 0-8 사이의 숫자를 입력하세요."
                ;;
        esac
        
        echo ""
        read -p "계속하려면 Enter를 누르세요..."
    done
}

# 스크립트 시작
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "🎯 HPO + AIStages 통합 실험 시스템"
    echo ""
    echo "사용법:"
    echo "  $0                    # 대화형 메뉴 실행"
    echo "  $0 --help            # 도움말 표시"
    echo "  $0 quick             # 빠른 HPO 실험 실행"
    echo "  $0 check             # 실험 결과 확인"
    echo "  $0 submit <exp_id>   # 특정 실험 제출 준비"
    echo ""
    echo "주요 기능:"
    echo "  - HPO 실험 자동 실행"
    echo "  - AIStages 제출 후보 추천"
    echo "  - 로컬 vs 서버 점수 분석"
    echo "  - 과적합 위험도 평가"
    echo "  - 앙상블 후보 추천"
    echo "  - 종합 리포트 생성"
    exit 0
elif [ "$1" == "quick" ]; then
    print_info "빠른 HPO 실험 실행"
    python start_hpo.py
elif [ "$1" == "check" ]; then
    check_experiment_results
elif [ "$1" == "submit" ] && [ -n "$2" ]; then
    print_info "실험 $2 제출 준비"
    python -c "
from enhanced_experiment_tracker import EnhancedExperimentTracker
tracker = EnhancedExperimentTracker()
instructions = tracker.submit_to_aistages('$2')
print(instructions)
"
else
    main
fi
