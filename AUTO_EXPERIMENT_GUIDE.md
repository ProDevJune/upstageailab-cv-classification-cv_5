# 🚀 자동 실험 시스템 사용 가이드 (OCR 지원 버전)

## 📁 구조
```
experiments/
├── configs/                     # 자동 생성된 실험별 설정 파일들
├── logs/                        # 실험 결과 JSON 로그들  
├── submissions/                 # 제출 관리 관련 파일들
├── experiment_matrix.yaml       # 모델 × 기법 × OCR 조합 정의
├── auto_experiment_runner.py    # 자동 실험 실행기
├── experiment_generator.py      # 실험 매트릭스 생성기 (OCR 지원)
├── submission_manager.py        # 제출 관리 시스템 (OCR 지원)
├── results_analyzer.py          # 결과 분석기
└── experiment_monitor.py        # 실시간 모니터링 대시보드
```

## 🎯 실행 순서

### 1. 초기 설정
```bash
# 파일 권한 설정
chmod +x setup_experiments.sh
./setup_experiments.sh
```

### 2. 실험 매트릭스 생성 (OCR 지원)
```bash
# 🔤 Selective 모드: 상위 기법에만 OCR 실험 추가 (약 32개 실험)
python experiments/experiment_generator.py

# 🔤 All 모드: 모든 조합에 OCR 적용/미적용 (48개 실험)
python experiments/experiment_generator.py --ocr-mode all

# 📷 None 모드: OCR 없이 기존 24개 실험만
python experiments/experiment_generator.py --ocr-mode none

# 시뮬레이션만 실행 (파일 생성 없음)
python experiments/experiment_generator.py --ocr-mode all --dry-run
```

### 3. 자동 실험 실행
```bash
# 모든 실험 순차 실행
python experiments/auto_experiment_runner.py

# 중단된 지점부터 재개
python experiments/auto_experiment_runner.py --resume

# 시뮬레이션만 실행
python experiments/auto_experiment_runner.py --dry-run
```

### 4. 실시간 모니터링 (별도 터미널)
```bash
# 실시간 대시보드 시작
python experiments/experiment_monitor.py

# 한 번만 상태 확인
python experiments/experiment_monitor.py --once
```

### 5. 제출 관리 (OCR 지원)
```bash
# 제출 대기 목록 확인 (OCR 정보 포함)
python experiments/submission_manager.py list-pending

# OCR별로 제출 대기 목록 확인
python experiments/submission_manager.py list-pending-ocr

# 특정 실험 제출 정보 확인 (OCR 포함)
python experiments/submission_manager.py get-submission-info exp_swin_focal_mixup_ocr_001

# 서버 결과 추가
python experiments/submission_manager.py add-server-result \
  --experiment exp_swin_focal_mixup_ocr_001 \
  --score 0.8543 \
  --rank 15 \
  --notes "첫 번째 OCR 실험 제출"

# 성능 차이 분석 (OCR별 분석 포함)
python experiments/submission_manager.py analyze-gaps

# 다음 제출 추천 (OCR 다양성 고려)
python experiments/submission_manager.py recommend-next
```

### 6. 결과 분석
```bash
# 마크다운 리포트 생성
python experiments/results_analyzer.py --generate-report

# 콘솔에 리포트 출력
python experiments/results_analyzer.py

# 요약만 출력
python experiments/results_analyzer.py --summary-only
```

## 📊 실험 매트릭스

### 모델 (4개)
- **swin_transformer**: Swin-B/384, batch_size=32
- **efficientnet_b4**: EfficientNet-B4, batch_size=48  
- **convnext_base**: ConvNeXt-Base, batch_size=28
- **maxvit_base**: MaxViT-Base/384, batch_size=24

### 기법 (6개)
- **baseline**: CrossEntropy 기본
- **focal_loss**: Focal Loss (α=1.0, γ=2.0)
- **mixup_cutmix**: MixUp + CutMix (50% 확률)
- **focal_mixup**: Focal Loss + MixUp/CutMix
- **label_smooth**: Label Smoothing (0.1)
- **label_mixup**: Label Smoothing + MixUp/CutMix

**총 24개 실험** = 4개 모델 × 6개 기법

## 🔬 결과 JSON 구조

각 실험 완료 후 `experiments/logs/`에 저장:

```json
{
  "experiment_id": "exp_swin_focal_mixup_001",
  "timestamp": "2025-07-07T15:30:45",
  "model": "swin_transformer",
  "technique": "focal_mixup",
  "local_results": {
    "validation_f1": 0.8543,
    "validation_acc": 0.8712,
    "training_time_minutes": 89.5
  },
  "submission": {
    "csv_path": "/path/to/submission.csv",
    "submission_ready": true
  },
  "memo_suggestion": {
    "auto_generated": "SwinB384+Focal+Mix50%",
    "alternatives": ["Swin384 FocalMix", "Auto: SwinB+FocalMix"]
  },
  "server_evaluation": {
    "submitted": false,
    "server_score": null,
    "server_rank": null
  }
}
```

## 🎯 메모 자동 생성 규칙

50자 제한으로 자동 생성:
- **모델 축약**: swin_base → SwinB384, efficientnet_b4 → EffNetB4
- **기법 축약**: FocalLoss → Focal, MixUpCutMix → Mix50%
- **TTA 추가**: test_TTA=True → +TTA
- **파라미터**: α=1.0,γ=2.0 → (α1,γ2)

예시: `SwinB384+Focal+Mix50%+TTA(α1,γ2)`

## 📈 우선순위 시스템

실험은 다음 기준으로 우선순위 결정:
- **모델 우선순위** (30%): 빠른 모델 우선
- **기법 우선순위** (50%): 효과 큰 기법 우선  
- **예상 시간** (20%): 짧은 시간 우선

**기법 우선순위**:
1. focal_mixup (최고 효과 예상)
2. label_mixup
3. mixup_cutmix
4. focal_loss
5. label_smooth
6. baseline

## 🛠️ 에러 처리

- 개별 실험 실패시 다음 실험 계속 진행
- GPU 메모리 부족시 자동 정리 후 재시도
- 중단시 `--resume` 옵션으로 이어서 실행
- 모든 진행 상황은 JSON으로 기록

## 📋 실행 예시 시나리오

```bash
# 터미널 1: 실험 생성 및 실행
cd /Users/jayden/Developer/Projects/cv-classification
python experiments/experiment_generator.py
python experiments/auto_experiment_runner.py &

# 터미널 2: 모니터링
python experiments/experiment_monitor.py

# 터미널 3: 제출 관리 (실험 완료 후)
python experiments/submission_manager.py list-pending
python experiments/submission_manager.py get-submission-info exp_swin_focal_mixup_001

# 서버 제출 후 결과 기록
python experiments/submission_manager.py add-server-result \
  --experiment exp_swin_focal_mixup_001 \
  --score 0.8543 \
  --rank 15

# 최종 분석 리포트 생성
python experiments/results_analyzer.py --generate-report
```

## 🎉 완료 후 활용

1. **최고 성능 조합 확인**: results_analyzer.py로 TOP 5 추출
2. **앙상블 후보 선택**: 다양성 기반 추천 활용
3. **ROI 분석**: 시간 대비 효율적인 조합 파악
4. **서버 vs 로컬 분석**: 성능 차이 패턴 분석
5. **다음 실험 계획**: 효과적인 조합으로 추가 실험

## ⚠️ 주의사항

- 실험 실행 전 충분한 디스크 공간 확보
- 장시간 실행시 시스템 안정성 확인
- 각 실험 약 60-110분 소요 예상
- GPU 메모리 8GB 이상 권장
- 실험 중단시 반드시 `--resume` 옵션 사용
