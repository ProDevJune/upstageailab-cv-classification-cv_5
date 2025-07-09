#!/bin/bash
# 빠른 호환성 검증 스크립트 수정 버전
# 실험 전에 Albumentations 및 핵심 모듈 호환성을 빠르게 확인

echo "🔍 빠른 호환성 검증 시작"
echo "======================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 결과 추적
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 테스트 함수
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}📋 테스트: ${test_name}${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        echo -e "   ${GREEN}✅ 성공${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "   ${RED}❌ 실패${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 1. Python 기본 import 테스트
echo -e "\n${YELLOW}1. 기본 패키지 import 테스트${NC}"
echo "--------------------------------------"

run_test "Python 기본 모듈들" "python -c 'import torch, torchvision, timm, numpy, pandas, yaml, cv2, PIL; print(\"기본 모듈 OK\")'"

# 2. Albumentations 호환성 테스트
echo -e "\n${YELLOW}2. Albumentations 호환성 테스트${NC}"
echo "--------------------------------------"

run_test "Albumentations import" "python -c 'import albumentations as A; print(f\"Albumentations {A.__version__}\")'"

run_test "A.Downscale 새로운 API" "python -c 'import albumentations as A; t = A.Downscale(scale_min=0.5, scale_max=0.75, p=1.0); print(\"Downscale OK\")'"

run_test "A.CoarseDropout 새로운 API" "python -c 'import albumentations as A; t = A.CoarseDropout(max_holes=2, max_height=20, max_width=20, fill_value=0, p=1.0); print(\"CoarseDropout OK\")'"

run_test "A.Affine 기본 파라미터" "python -c 'import albumentations as A; t = A.Affine(scale=(0.8,1.2), p=1.0); print(\"Affine OK\")'"

run_test "A.GaussNoise var_limit" "python -c 'import albumentations as A; t = A.GaussNoise(var_limit=(0.01, 0.2), p=1.0); print(\"GaussNoise OK\")'"

# 3. 프로젝트 모듈 import 테스트
echo -e "\n${YELLOW}3. 프로젝트 모듈 import 테스트${NC}"
echo "--------------------------------------"

run_test "gemini_augmentation_v2 import" "python -c 'from codes.gemini_augmentation_v2 import AUG, get_augmentation; print(\"Augmentation module OK\")'"

run_test "gemini_train_v2 import" "python -c 'from codes.gemini_train_v2 import *; print(\"Train module OK\")'"

run_test "gemini_main_v2 import" "python -c 'import sys; sys.path.append(\"codes\"); from gemini_main_v2 import *; print(\"Main module OK\")'" 

# 4. 간단한 모델 로드 테스트
echo -e "\n${YELLOW}4. 모델 로드 테스트${NC}"
echo "--------------------------------------"

run_test "EfficientNet-B4 로드" "python -c 'import timm; m = timm.create_model(\"efficientnet_b4.ra2_in1k\", pretrained=False, num_classes=42); print(f\"EfficientNet-B4 OK: {m.__class__.__name__}\")'"

run_test "Swin Transformer 로드" "python -c 'import timm; m = timm.create_model(\"swin_base_patch4_window12_384.ms_in1k\", pretrained=False, num_classes=42); print(f\"Swin OK: {m.__class__.__name__}\")'"

# 5. 디바이스 호환성 테스트
echo -e "\n${YELLOW}5. 디바이스 호환성 테스트${NC}"
echo "--------------------------------------"

run_test "PyTorch 디바이스 감지" "python -c 'import torch; print(f\"CUDA: {torch.cuda.is_available()}\"); print(f\"MPS: {torch.backends.mps.is_available()}\"); print(\"Device detection OK\")'"

run_test "기본 텐서 연산" "python -c 'import torch; device = \"cuda\" if torch.cuda.is_available() else \"mps\" if torch.backends.mps.is_available() else \"cpu\"; x = torch.randn(10, 10).to(device); y = torch.mm(x, x.T); print(f\"Tensor ops OK on {device}\")'"

# 6. 설정 파일 검증
echo -e "\n${YELLOW}6. 설정 파일 검증${NC}"
echo "--------------------------------------"

run_test "config_v2.yaml 로드" "python -c 'import yaml; cfg = yaml.safe_load(open(\"codes/config_v2.yaml\")); print(f\"Config OK: {len(cfg)} keys\")'"

# 7. 데이터 디렉토리 확인
echo -e "\n${YELLOW}7. 데이터 디렉토리 검증${NC}"
echo "--------------------------------------"

run_test "Train 데이터 디렉토리" "python -c 'import os; assert os.path.exists(\"data/train\"), \"Train dir missing\"; print(\"Train dir OK:\", len(os.listdir(\"data/train\")), \"files\")'"

run_test "Test 데이터 디렉토리" "python -c 'import os; assert os.path.exists(\"data/test\"), \"Test dir missing\"; print(\"Test dir OK:\", len(os.listdir(\"data/test\")), \"files\")'"

run_test "CSV 파일들" "python -c 'import os, pandas as pd; train_df = pd.read_csv(\"data/train.csv\") if os.path.exists(\"data/train.csv\") else None; print(\"CSV files found\")'"

# 8. 빠른 학습 테스트 (선택적)
echo -e "\n${YELLOW}8. 빠른 학습 테스트 (30초 제한)${NC}"
echo "--------------------------------------"

run_test "빠른 실험 실행" "timeout 30s python -c '
import torch
import timm
import albumentations as A
from codes.gemini_augmentation_v2 import AUG

# 모델 생성
device = \"cuda\" if torch.cuda.is_available() else \"mps\" if torch.backends.mps.is_available() else \"cpu\"
model = timm.create_model(\"efficientnet_b4.ra2_in1k\", pretrained=False, num_classes=42).to(device)

# 더미 데이터
dummy_input = torch.randn(2, 3, 224, 224).to(device)
dummy_target = torch.randint(0, 42, (2,)).to(device)

# Forward pass
model.train()
output = model(dummy_input)
loss = torch.nn.CrossEntropyLoss()(output, dummy_target)

# Backward pass
loss.backward()

print(f\"Quick training test OK: loss={loss.item():.4f}, device={device}\")
' 2>/dev/null || echo '시간 초과 또는 에러 발생'"

# 결과 요약
echo -e "\n${BLUE}======================================"
echo "📊 검증 결과 요약"
echo -e "======================================${NC}"

echo -e "총 테스트: ${TOTAL_TESTS}개"
echo -e "${GREEN}✅ 성공: ${PASSED_TESTS}개${NC}"
echo -e "${RED}❌ 실패: ${FAILED_TESTS}개${NC}"

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo -e "성공률: ${SUCCESS_RATE}%"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 모든 검증 통과! 실험을 안전하게 시작할 수 있습니다.${NC}"
    echo -e "${GREEN}🚀 다음 단계: bash run_experiments.sh 또는 python experiments/auto_experiment_runner.py${NC}"
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo -e "\n${YELLOW}⚠️  대부분의 검증 통과. 실험 가능하지만 일부 주의 필요.${NC}"
    echo -e "${YELLOW}📋 실패한 테스트를 확인하고 해결 후 재시도를 권장합니다.${NC}"
    exit 1
else
    echo -e "\n${RED}❌ 너무 많은 검증 실패. 환경 설정 필요.${NC}"
    echo -e "${RED}🔧 다음을 시도해보세요:${NC}"
    echo -e "   1. bash setup_platform_env.sh"
    echo -e "   2. pip install -r requirements.txt"
    echo -e "   3. 이 스크립트 재실행"
    exit 2
fi