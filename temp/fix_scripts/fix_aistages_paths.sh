#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# AIStages 경로 자동 수정 스크립트
echo "🔧 AIStages 경로 자동 수정"
echo "========================"
echo "⏰ 시작 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 현재 경로 확인
CURRENT_PATH=$(pwd)
echo "📁 현재 작업 경로: $CURRENT_PATH"
echo ""

# 수정할 파일들 목록
FILES_TO_FIX=(
    "run_optimal_performance.sh"
    "run_v2_1_only.sh"
    "run_v2_2_only.sh"
    "codes/config_v2_1.yaml"
    "codes/config_v2_2.yaml"
    "codes/config_v3_modelA.yaml"
    "codes/config_v3_modelB.yaml"
    "codes/gemini_main_v3.py"
    "v2_experiment_generator.py"
    "v3_experiment_generator.py"
)

# 백업 디렉토리 생성
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 백업 디렉토리 생성: $BACKUP_DIR"
echo ""

echo "🔄 파일별 경로 수정 시작:"
echo "------------------------"

fixed_count=0
error_count=0

for file in "${FILES_TO_FIX[@]}"; do
    echo -n "수정 중: $file ... "
    
    if [ -f "$file" ]; then
        # 백업 생성
        cp "$file" "$BACKUP_DIR/" 2>/dev/null
        
        # 임시 파일 생성
        temp_file=$(mktemp)
        
        # 경로 수정 적용
        sed 's|/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5|.|g' "$file" > "$temp_file"
        
        # 결과 확인 및 적용
        if [ $? -eq 0 ]; then
            mv "$temp_file" "$file"
            echo "✅ 완료"
            ((fixed_count++))
        else
            rm -f "$temp_file"
            echo "❌ 실패"
            ((error_count++))
        fi
    else
        echo "⚠️  파일 없음"
    fi
done

echo ""
echo "📊 수정 결과:"
echo "  성공: $fixed_count 개"
echo "  실패: $error_count 개"
echo "  백업: $BACKUP_DIR/"
echo ""

# 특별히 중요한 파일들 추가 수정
echo "🔧 중요 파일 추가 수정:"
echo "----------------------"

# gemini_main_v3.py의 project_root 수정
if [ -f "codes/gemini_main_v3.py" ]; then
    echo -n "codes/gemini_main_v3.py project_root 수정 ... "
    
    # project_root를 현재 디렉토리 기준으로 동적 설정
    sed -i.bak 's|project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))|project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))|g' codes/gemini_main_v3.py
    
    echo "✅ 완료"
fi

# config 파일들의 data_dir을 상대 경로로 수정
for config_file in codes/config_*.yaml; do
    if [ -f "$config_file" ]; then
        echo -n "$config_file data_dir 수정 ... "
        
        # data_dir을 상대 경로로 수정
        sed -i.bak 's|data_dir: "/.*upstageailab-cv-classification-cv_5/data"|data_dir: "./data"|g' "$config_file"
        sed -i.bak2 's|data_dir: /.*upstageailab-cv-classification-cv_5/data|data_dir: "./data"|g' "$config_file"
        
        echo "✅ 완료"
    fi
done

echo ""

# 실행 권한 복원
echo "🔑 실행 권한 복원:"
echo "-----------------"

chmod +x *.sh 2>/dev/null
echo "✅ 모든 .sh 파일 실행 권한 부여"

if [ -f "codes/gemini_main_v3.py" ]; then
    chmod +x codes/gemini_main_v3.py
    echo "✅ gemini_main_v3.py 실행 권한 부여"
fi

echo ""

# 검증
echo "🔍 수정 결과 검증:"
echo "------------------"

echo "상대 경로 사용 확인:"
problem_found=false

for file in "${FILES_TO_FIX[@]}"; do
    if [ -f "$file" ]; then
        # Mac 경로가 남아있는지 확인
        if grep -q "/Users/jayden" "$file" 2>/dev/null; then
            echo "  ⚠️  $file: Mac 경로 잔존"
            problem_found=true
        else
            echo "  ✅ $file: 경로 수정 완료"
        fi
    fi
done

echo ""

if [ "$problem_found" = false ]; then
    echo "🎉 모든 경로 수정 완료!"
    echo ""
    echo "🚀 이제 AIStages에서 안전하게 실행 가능:"
    echo "  ./run_optimal_performance.sh"
else
    echo "⚠️  일부 파일에 문제가 남아있습니다."
    echo "수동 확인이 필요할 수 있습니다."
fi

echo ""

# 환경별 최적화 설정
echo "⚙️  AIStages 환경 최적화:"
echo "------------------------"

# venv 경로 확인
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ 가상환경 활성화됨: $VIRTUAL_ENV"
else
    echo "⚠️  가상환경이 활성화되지 않음"
    echo "   권장: source venv/bin/activate"
fi

# 현재 디렉토리가 프로젝트 루트인지 확인
if [ -f "data/train.csv" ] && [ -d "codes" ]; then
    echo "✅ 프로젝트 루트 디렉토리 확인"
else
    echo "⚠️  프로젝트 구조 확인 필요"
    echo "   data/train.csv 및 codes/ 디렉토리가 있는지 확인하세요"
fi

echo ""
echo "🏁 최종 실행 준비 상태:"
echo "======================"

ready_to_run=true

# 필수 체크리스트
checks=(
    "데이터 파일:data/train.csv"
    "설정 디렉토리:codes"
    "실행 스크립트:run_optimal_performance.sh"
)

for check in "${checks[@]}"; do
    name=${check%:*}
    path=${check#*:}
    
    if [ -e "$path" ]; then
        echo "  ✅ $name"
    else
        echo "  ❌ $name"
        ready_to_run=false
    fi
done

echo ""

if [ "$ready_to_run" = true ]; then
    echo "🎯 실행 준비 완료!"
    echo ""
    echo "다음 명령어로 최고 성능 실험을 시작하세요:"
    echo "  screen -S optimal_experiment"
    echo "  ./run_optimal_performance.sh"
else
    echo "⚠️  실행 준비 미완료"
    echo "위의 체크리스트를 확인하고 누락된 파일을 준비하세요."
fi

echo ""
echo "✅ AIStages 경로 자동 수정 완료!"
echo "==============================="
echo "⏰ 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
