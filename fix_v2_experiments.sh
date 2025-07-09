#!/bin/bash

# V2 실험 문제 해결 및 재생성 스크립트
echo "🔧 V2 실험 문제 해결 및 재생성"
echo "================================"

# 현재 위치 확인
echo "현재 디렉토리: $(pwd)"
echo "프로젝트 루트 확인: $(ls -la | grep -E '(codes|data|v2_experiments)' | wc -l)개 핵심 디렉토리 존재"

# 1. v2_experiments 디렉토리 구조 재생성
echo ""
echo "📁 1. 디렉토리 구조 재생성"
mkdir -p v2_experiments/configs
mkdir -p v2_experiments/logs
mkdir -p v2_experiments/scripts
mkdir -p v2_experiments/results

# 2. V2_2 실험 설정 수동 생성
echo ""
echo "🛠️ 2. V2_2 FocalLoss 실험 설정 수동 생성"

cat > v2_experiments/configs/v2_2_resnet50_focal_manual.yaml << 'EOF'
# V2_2 Manual Configuration - FocalLoss + ResNet50
experiment_name: "v2_2_resnet50_focal_manual"
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

echo "✅ 수동 설정 파일 생성 완료: v2_experiments/configs/v2_2_resnet50_focal_manual.yaml"

# 3. 실행 가능한 run_all_experiments.sh 새로 생성
echo ""
echo "🚀 3. 실행 스크립트 재생성"

cat > v2_experiments/run_all_experiments.sh << 'EOF'
#!/bin/bash

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
    echo "해결: ./fix_v2_experiments.sh 실행"
    exit 1
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
        
        # 실험 실행 (codes 디렉토리의 적절한 스크립트 사용)
        if [ -f "codes/gemini_main_v2_1_style.py" ]; then
            python codes/gemini_main_v2_1_style.py --config "$config_file" >> "$LOG_FILE" 2>&1
        elif [ -f "codes/main.py" ]; then
            python codes/main.py --config "$config_file" >> "$LOG_FILE" 2>&1
        else
            echo "   ❌ 실행할 메인 스크립트를 찾을 수 없습니다!"
            echo "   확인 필요: codes/ 디렉토리의 Python 파일들"
            continue
        fi
        
        if [ $? -eq 0 ]; then
            echo "   ✅ 완료: $exp_name"
            ((success_count++))
        else
            echo "   ❌ 실패: $exp_name"
        fi
        
        echo "   완료 시간: $(date)"
        echo ""
    fi
done

echo "🎉 모든 실험 완료!"
echo "📊 결과: $success_count/$experiment_count 성공"
echo "📁 결과 확인: ls -la data/submissions/"
echo "📋 로그 확인: cat $LOG_FILE"
EOF

chmod +x v2_experiments/run_all_experiments.sh

echo "✅ 실행 스크립트 재생성 완료"

# 4. 상태 확인
echo ""
echo "🔍 4. 수정 완료 상태 확인"
echo "------------------------"
echo "설정 파일 수: $(find v2_experiments/configs -name "*.yaml" | wc -l)개"
echo "실행 스크립트: $(ls -la v2_experiments/run_all_experiments.sh)"
echo ""

echo "✅ V2 실험 문제 해결 완료!"
echo ""
echo "🚀 다음 단계:"
echo "   1. 테스트 실행: ./v2_experiments/run_all_experiments.sh"
echo "   2. 전체 실험: ./run_optimal_performance.sh"
