#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# V2 실험 실행 스크립트 (경로 문제 해결된 버전)
echo "🚀 Starting V2 Experiments (Fixed Version)"
echo "=========================================="

# 현재 디렉토리에서 실행 (상대 경로 사용)
echo "현재 위치: $(pwd)"

# 실험 설정 파일 확인
CONFIG_COUNT=$(find v2_experiments/configs -name "*.yaml" | wc -l)
echo "📊 발견된 실험 설정: ${CONFIG_COUNT}개"

if [ $CONFIG_COUNT -eq 0 ]; then
    echo "❌ 실험 설정 파일이 없습니다!"
    echo "🔧 V2_2 FocalLoss 실험 설정 자동 생성 중..."
    
    # v2_experiments 디렉토리 구조 생성
    mkdir -p v2_experiments/configs
    mkdir -p v2_experiments/logs
    mkdir -p v2_experiments/results
    
    # V2_2 실험 설정 파일 생성
    cat > v2_experiments/configs/v2_2_resnet50_focal_auto.yaml << 'EOF'
# V2_2 Auto Generated Configuration - FocalLoss + ResNet50
experiment_name: "v2_2_resnet50_focal_auto"
model_name: "resnet50.tv2_in1k"
num_classes: 17
img_size: 224
batch_size: 32
epochs: 20
learning_rate: 0.0001

# FocalLoss 설정
criterion: "FocalLoss"
focal_alpha: 0.25
focal_gamma: 2.0

# 데이터 설정
data_dir: "data"
train_csv: "data/train.csv"
test_csv: "data/test.csv"

# 증강 설정
online_aug:
  mixup: true
  cutmix: false
  alpha: 0.4
  num_classes: 17

# 기타 설정
device: "cuda"
num_workers: 4
pin_memory: true
save_dir: "data/submissions"
EOF
    
    CONFIG_COUNT=1
    echo "✅ 실험 설정 파일 자동 생성 완료"
fi

# 로그 디렉토리 생성
mkdir -p v2_experiments/logs
mkdir -p data/submissions

# 로그 파일 설정
LOG_FILE="v2_experiments/logs/experiment_run_$(date +%Y%m%d_%H%M%S).log"
echo "📝 로그 파일: $LOG_FILE"

# 실험 실행
echo ""
echo "🔬 실험 실행 시작..."

experiment_count=0
success_count=0

for config_file in v2_experiments/configs/*.yaml; do
    if [ -f "$config_file" ]; then
        ((experiment_count++))
        exp_name=$(basename "$config_file" .yaml)
        
        echo "🧪 [$experiment_count] 실험 시작: $exp_name"
        echo "   설정 파일: $config_file"
        echo "   시작 시간: $(date)"
        
        # 메인 실행 파일 찾기
        MAIN_SCRIPT=""
        if [ -f "codes/gemini_main_v2_1_style.py" ]; then
            MAIN_SCRIPT="codes/gemini_main_v2_1_style.py"
        elif [ -f "codes/main.py" ]; then
            MAIN_SCRIPT="codes/main.py"
        elif [ -f "codes/train.py" ]; then
            MAIN_SCRIPT="codes/train.py"
        else
            echo "   ❌ 실행할 메인 스크립트를 찾을 수 없습니다!"
            echo "   확인된 codes 디렉토리 파일들:"
            ls -la codes/*.py 2>/dev/null | head -5
            continue
        fi
        
        echo "   🐍 실행 스크립트: $MAIN_SCRIPT"
        
        # 실험 실행
        python "$MAIN_SCRIPT" --config "$config_file" >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            echo "   ✅ 완료: $exp_name"
            ((success_count++))
        else
            echo "   ❌ 실패: $exp_name"
            echo "   📋 마지막 10줄의 로그:"
            tail -10 "$LOG_FILE"
        fi
        
        echo "   완료 시간: $(date)"
        echo ""
    fi
done

echo "🎉 모든 실험 완료!"
echo "📊 결과: $success_count/$experiment_count 성공"
echo "📁 결과 확인: ls -la data/submissions/"
echo "📋 로그 확인: cat $LOG_FILE"

# 생성된 submission 파일 표시
if [ -d "data/submissions" ]; then
    SUBMISSION_COUNT=$(find data/submissions -name "*.csv" | wc -l)
    echo "📈 생성된 submission 파일: ${SUBMISSION_COUNT}개"
    if [ $SUBMISSION_COUNT -gt 0 ]; then
        echo "🏆 최신 submission 파일들:"
        find data/submissions -name "*.csv" -exec ls -lt {} \; | head -3
    fi
fi
