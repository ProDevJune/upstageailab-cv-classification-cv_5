# 🚀 V2_1 & V2_2 자동 실험 시스템 사용 가이드

v2_1과 v2_2를 위한 comprehensive 자동 실험 시스템입니다.

## 📊 시스템 구조

```
v2_experiments/
├── configs/                     # 자동 생성된 실험 config 파일들
├── scripts/                     # 실험 실행 스크립트들
├── logs/                        # 실험 로그들
├── results/                     # 분석 결과들
├── experiment_list.json         # 전체 실험 리스트
└── run_all_experiments.sh       # 자동 실행 스크립트
```

## 🎯 실험 매트릭스

### V2_1 실험군: "대형 모델 + 장기 학습"
- **모델**: ConvNeXt-V2 Base/Large, EfficientNet-V2 L
- **학습률**: 0.00005, 0.0001, 0.0002
- **배치 크기**: 16, 32, 48
- **스케줄러**: Warmup 단/장기 변형

### V2_2 실험군: "효율적 + 기법 조합"
- **모델**: ResNet50/101, EfficientNet-B4
- **손실함수**: FocalLoss, CrossEntropyLoss, LabelSmoothingLoss
- **증강기법**: Mixup, CutMix, Dynamic, 조합
- **학습방식**: Single-stage, 2-stage

### CV 실험군: "교차 검증"
- **Folds**: 3-fold, 5-fold
- **모델**: ResNet50, EfficientNet-B4

## 🚀 사용법

### 1. 실험 생성 및 실행

```bash
# 전체 실험 생성 (약 100+ 실험)
python v2_experiment_generator.py

# 특정 단계만 실행
python v2_experiment_generator.py --phase phase1  # 기본 성능 확인
python v2_experiment_generator.py --phase phase2  # 모델 비교
python v2_experiment_generator.py --phase phase3  # 하이퍼파라미터 최적화
python v2_experiment_generator.py --phase phase4  # 고급 기법

# 시뮬레이션 (파일 생성 없이 미리보기)
python v2_experiment_generator.py --dry-run

# 모든 실험 자동 실행
./v2_experiments/run_all_experiments.sh
```

### 2. 실시간 모니터링

```bash
# 실시간 모니터링 (30초마다 업데이트)
python v2_experiment_monitor.py --mode monitor

# 5초마다 업데이트
python v2_experiment_monitor.py --mode monitor --refresh 5

# 백그라운드에서 실행
nohup python v2_experiment_monitor.py --mode monitor > monitor.log 2>&1 &
```

### 3. 결과 분석

```bash
# 실험 결과 분석
python v2_experiment_monitor.py --mode analyze

# 분석 플롯 생성
python v2_experiment_monitor.py --mode analyze --save-plots
```

## 📈 실험 우선순위

### Phase 1: 기본 성능 확인 (3개 실험)
- v2_1 ConvNeXt 기본 설정
- v2_2 ResNet50 + FocalLoss + Mixup
- v2_2 ResNet50 + FocalLoss + CutMix

### Phase 2: 모델 비교 (12개 실험)
- v2_1 대형 모델들
- v2_2 효율적 모델들

### Phase 3: 하이퍼파라미터 최적화 (36개 실험)
- 학습률 탐색
- 동적 증강 비교

### Phase 4: 고급 기법 (24개 실험)
- 2-stage 학습
- 교차 검증

## 🔧 실험 설정 커스터마이징

### 매트릭스 파일 수정
```yaml
# v2_experiment_matrix.yaml 편집
v2_1_experiments:
  variations:
    models:
      - name: "custom_model"
        model_name: "your_model_name"
    learning_rates:
      - name: "custom_lr"
        lr: 0.0005
```

### 새로운 실험 타입 추가
```python
# v2_experiment_generator.py에 함수 추가
def generate_custom_experiments(self):
    # 커스텀 실험 로직
    pass
```

## 📊 모니터링 대시보드

실시간 모니터링 화면에서 확인할 수 있는 정보:

```
📊 Experiment Status - 2025-01-XX XX:XX:XX
============================================================
📈 Total Experiments: 87
✅ Completed: 23 (26.4%)
🔄 Running: 1
⏳ Pending: 63
❌ Failed: 0

📊 By Experiment Type:
  V2_1: 7/28 completed
  V2_2: 15/52 completed
  CV: 1/7 completed

🔬 Currently Running: v2_2_resnet50_focal_mixup_single

🏆 Recently Completed:
  - v2_1_convnextv2_base_lr_medium_batch_32_warmup_short
  - v2_2_resnet50_focal_cutmix_single
  - v2_2_efficientnet_b4_ce_dynamic_single
```

## 🎯 결과 분석 예시

```
📊 Analyzing V2_1 & V2_2 Experiment Results
==================================================
📈 Total analyzed experiments: 23
🏆 Best F1 Score: 0.8756
📊 Average F1 Score: 0.8234

🔬 Performance by Experiment Type:
         count    mean     max
type                        
cv           1  0.8234  0.8234
v2_1         7  0.8456  0.8756
v2_2        15  0.8167  0.8543

🏗️ Performance by Model:
              count    mean     max
model                           
convnextv2        7  0.8456  0.8756
efficientnet      8  0.8234  0.8543
resnet           8  0.8123  0.8456

🥇 Top 5 Experiments:
  0.8756 - v2_1_convnextv2_large_lr_medium_batch_32_warmup_long (v2_1)
  0.8543 - v2_2_efficientnet_b4_focal_mixup_two_stage (v2_2)
  0.8456 - v2_2_resnet50_focal_cutmix_single (v2_2)
  0.8432 - v2_1_convnextv2_base_lr_low_batch_48_warmup_short (v2_1)
  0.8398 - v2_2_resnet101_ce_dynamic_single (v2_2)
```

## ⚠️ 주의사항

### 메모리 제약
- ConvNeXt-V2 Large: 최대 배치크기 16
- EfficientNet-V2 L: 최대 배치크기 8

### 시간 제약
- V2_1 실험: 최대 48시간
- V2_2 실험: 최대 24시간
- CV 실험: 최대 72시간

### GPU 요구사항
- ConvNeXt-V2 Large: 16GB+ GPU 필요
- EfficientNet-V2 L: 24GB+ GPU 필요

## 🛠️ 문제해결

### 실험 중단 시 재시작
```bash
# 특정 실험부터 재시작
./v2_experiments/run_all_experiments.sh | tail -n +N  # N은 시작할 실험 번호
```

### 실패한 실험 재실행
```bash
# 실패한 실험 찾기
python v2_experiment_monitor.py --mode analyze --failed-only

# 개별 실험 재실행
python codes/gemini_main_v2_enhanced.py --config v2_experiments/configs/experiment_name.yaml
```

---

이제 v2_1과 v2_2에 대해서도 완전한 자동 실험 시스템을 사용할 수 있습니다! 🚀
