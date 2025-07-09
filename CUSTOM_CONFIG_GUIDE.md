# 🎯 Custom Config Sequential Runner 사용 가이드

원하는 설정으로 만든 여러 YAML 파일들을 순차적으로 자동 실행하는 시스템입니다.

## 📁 기본 구조

```
my_configs/
├── my_experiment_1.yaml       # 사용자 정의 실험 1
├── my_experiment_2.yaml       # 사용자 정의 실험 2  
├── my_experiment_3.yaml       # 사용자 정의 실험 3
├── execution_order.txt        # 실행 순서 (선택사항)
├── logs/                      # 실행 로그들
└── results/                   # 실험 결과들
```

## 🚀 빠른 시작

### 1. 샘플 파일 생성
```bash
./run_my_configs.sh --create-samples
```

### 2. Config 파일 편집
```bash
# 생성된 샘플 파일들을 원하는 설정으로 편집
vi my_configs/sample_v2_1_convnext.yaml
vi my_configs/sample_v2_2_resnet_mixup.yaml
vi my_configs/sample_v2_2_efficient_2stage.yaml
```

### 3. 실행
```bash
./run_my_configs.sh
```

## 📝 Config 파일 작성 예시

### V2_1 스타일 (대형 모델 + 장기 학습)
```yaml
# my_configs/convnext_experiment.yaml
model_name: 'convnextv2_base.fcmae_ft_in22k_in1k_384'
criterion: 'CrossEntropyLoss'
optimizer_name: 'AdamW'
lr: 0.0001
scheduler_name: 'CosineAnnealingWarmupRestarts'
scheduler_params:
  T_max: 5000
  max_lr: 0.0001
  min_lr: 0.00001
  warmup_steps: 5
epochs: 8000
batch_size: 32
online_augmentation: true
augmentation:
  eda: true
  dilation: true
  erosion: true
val_TTA: true
test_TTA: true
```

### V2_2 스타일 (효율적 + 기법 조합)
```yaml
# my_configs/resnet_mixup_experiment.yaml
model_name: 'resnet50.tv2_in1k'
criterion: 'FocalLoss'
optimizer_name: 'AdamW'
lr: 0.001
scheduler_name: 'CosineAnnealingLR'
scheduler_params:
  T_max: 50
  max_lr: 0.001
  min_lr: 0.00001
epochs: 100
batch_size: 32
online_augmentation: true
augmentation:
  eda: true
online_aug:
  mixup: true
  cutmix: false
val_TTA: false
test_TTA: false
```

### 2-Stage 학습 설정
```yaml
# my_configs/efficient_2stage_experiment.yaml (Stage 1)
model_name: 'efficientnet_b4.ra2_in1k'
criterion: 'CrossEntropyLoss'
two_stage: true
epochs: 30
lr: 0.001
augmentation:
  easiest: true

# my_configs/efficient_2stage_experiment_stage2.yaml (Stage 2)
model_name: 'efficientnet_b4.ra2_in1k'
criterion: 'FocalLoss'
two_stage: false
epochs: 20
lr: 0.0001
online_aug:
  mixup: true
```

## 🎮 실행 옵션

### 기본 실행
```bash
./run_my_configs.sh                    # 모든 .yaml 파일 실행
```

### 선택적 실행
```bash
./run_my_configs.sh --single my_experiment_1.yaml    # 특정 파일만
./run_my_configs.sh --pattern 'resnet_*.yaml'        # 패턴 매칭
./run_my_configs.sh --config-dir other_configs       # 다른 디렉토리
```

### 미리보기 및 설정
```bash
./run_my_configs.sh --dry-run          # 실행 예정 파일들 미리보기
./run_my_configs.sh --create-order     # 실행 순서 파일 생성
./run_my_configs.sh --create-samples   # 샘플 파일 생성
```

## 📊 실행 순서 제어

### execution_order.txt 파일 생성
```bash
./run_my_configs.sh --create-order
```

### 실행 순서 편집
```bash
# my_configs/execution_order.txt
# 원하는 순서대로 config 파일명을 나열

# 1단계: 빠른 테스트
sample_v2_2_resnet_mixup.yaml

# 2단계: 성능 비교
sample_v2_1_convnext.yaml
sample_v2_2_efficient_2stage.yaml

# 3단계: 추가 실험
my_custom_experiment.yaml
```

## 🔍 자동 타입 감지

시스템이 자동으로 각 config 파일을 분석해서 적절한 실행 스크립트를 선택합니다:

### V2_1 자동 감지 조건
- ConvNeXt 모델 사용
- CosineAnnealingWarmupRestarts 스케줄러
- 5000+ 에포크
- 낮은 학습률 (< 0.0001)

### V2_2 자동 감지 조건
- FocalLoss 사용
- two_stage 설정
- online_aug 설정
- dynamic_augmentation 활성화

## 📈 실행 모니터링

### 실시간 로그 확인
```bash
# 실행 중 로그 확인
tail -f my_configs/logs/my_experiment_20250109_143022.log
```

### 결과 확인
```bash
# 결과 JSON 파일 확인
cat my_configs/results/experiment_results.json
```

## 🎯 실사용 예시

### 1. 모델 비교 실험
```bash
# 3가지 모델 성능 비교
mkdir my_configs
cat > my_configs/resnet50_baseline.yaml << EOF
model_name: 'resnet50.tv2_in1k'
criterion: 'CrossEntropyLoss'
lr: 0.001
epochs: 50
batch_size: 64
EOF

cat > my_configs/efficientnet_b4_baseline.yaml << EOF
model_name: 'efficientnet_b4.ra2_in1k'
criterion: 'CrossEntropyLoss'
lr: 0.001
epochs: 50
batch_size: 64
EOF

cat > my_configs/convnext_baseline.yaml << EOF
model_name: 'convnextv2_base.fcmae_ft_in22k_in1k_384'
criterion: 'CrossEntropyLoss'
lr: 0.0001
epochs: 50
batch_size: 32
EOF

./run_my_configs.sh
```

### 2. 증강 기법 비교
```bash
# Mixup vs CutMix vs Dynamic
cat > my_configs/resnet_mixup.yaml << EOF
model_name: 'resnet50.tv2_in1k'
online_aug:
  mixup: true
  cutmix: false
EOF

cat > my_configs/resnet_cutmix.yaml << EOF
model_name: 'resnet50.tv2_in1k'
online_aug:
  mixup: false
  cutmix: true
EOF

cat > my_configs/resnet_dynamic.yaml << EOF
model_name: 'resnet50.tv2_in1k'
dynamic_augmentation:
  enabled: true
EOF

./run_my_configs.sh
```

### 3. 하이퍼파라미터 탐색
```bash
# 학습률 비교
for lr in 0.01 0.001 0.0001; do
cat > my_configs/resnet_lr_${lr}.yaml << EOF
model_name: 'resnet50.tv2_in1k'
lr: ${lr}
epochs: 30
batch_size: 64
EOF
done

./run_my_configs.sh
```

## 🛠️ 고급 사용법

### 실험 실패 시 재실행
```bash
# 실패한 실험만 찾아서 재실행
python custom_config_runner.py --single failed_experiment.yaml
```

### 특정 패턴 실행
```bash
# 특정 접두사를 가진 실험들만 실행
./run_my_configs.sh --pattern 'resnet_*.yaml'
./run_my_configs.sh --pattern 'lr_*.yaml'
```

### 다른 디렉토리 사용
```bash
# 여러 실험 세트 관리
./run_my_configs.sh --config-dir experiments_set1
./run_my_configs.sh --config-dir experiments_set2
```

---

이제 **완전히 자유롭게 원하는 설정으로 여러 실험을 순차 실행**할 수 있습니다! 🚀
