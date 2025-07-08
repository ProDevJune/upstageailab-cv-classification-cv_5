# 🚀 자동 실험 시스템 사용 가이드

## 📁 시스템 구성

```
experiments/
├── configs/                     # 자동 생성된 실험별 설정 파일들
├── logs/                        # 실험 결과 JSON 로그들  
├── submissions/                 # 제출 관리 관련 파일들
├── experiment_matrix.yaml       # 모델 × 기법 조합 정의
├── auto_experiment_runner.py    # 자동 실험 실행기
├── experiment_generator.py      # 실험 매트릭스 생성기
├── submission_manager.py        # 제출 관리 시스템
├── results_analyzer.py          # 결과 분석기
└── experiment_monitor.py        # 실시간 모니터링 대시보드
```

## 🎯 빠른 시작

### 1. 시스템 초기화
```bash
cd /Users/jayden/Developer/Projects/cv-classification
chmod +x setup_experiment_system.sh
./setup_experiment_system.sh
```

### 2. 실험 매트릭스 생성
```bash
python experiments/experiment_generator.py
```
- 총 24개 실험 (4개 모델 × 6개 기법) 생성
- 우선순위에 따른 실험 순서 자동 결정
- 각 실험별 설정 파일 자동 생성

### 3. 자동 실험 실행
```bash
# 백그라운드에서 실행
python experiments/auto_experiment_runner.py &

# 또는 포그라운드에서 실행
python experiments/auto_experiment_runner.py
```

### 4. 실시간 모니터링 (별도 터미널)
```bash
python experiments/experiment_monitor.py
```

## 📊 모델 × 기법 조합

### 모델 목록
- **swin_transformer**: Swin-B/384 (배치: 32, 예상시간: 90분)
- **efficientnet_b4**: EfficientNet-B4 (배치: 48, 예상시간: 75분)
- **convnext_base**: ConvNeXt-Base (배치: 28, 예상시간: 100분)
- **maxvit_base**: MaxViT-Base/384 (배치: 24, 예상시간: 110분)

### 기법 목록
- **baseline**: CrossEntropyLoss 기본
- **focal_loss**: FocalLoss (α=1.0, γ=2.0)
- **mixup_cutmix**: MixUp+CutMix (50% 확률)
- **focal_mixup**: FocalLoss + MixUp+CutMix
- **label_smooth**: LabelSmoothingCrossEntropy (0.1)
- **label_mixup**: LabelSmoothing + MixUp+CutMix

## 🎮 명령어 가이드

### 실험 생성기
```bash
# 기본 실행
python experiments/experiment_generator.py

# 시뮬레이션만 (파일 생성 안함)
python experiments/experiment_generator.py --dry-run

# 사용자 정의 매트릭스 파일
python experiments/experiment_generator.py --matrix custom_matrix.yaml
```

### 자동 실험 실행기
```bash
# 기본 실행
python experiments/auto_experiment_runner.py

# 중단된 지점부터 재시작
python experiments/auto_experiment_runner.py --resume

# 시뮬레이션만
python experiments/auto_experiment_runner.py --dry-run

# 사용자 정의 큐 파일
python experiments/auto_experiment_runner.py --queue custom_queue.json
```

### 제출 관리자
```bash
# 제출 대기 목록 (F1 점수 순)
python experiments/submission_manager.py list-pending

# 특정 실험 제출 정보
python experiments/submission_manager.py get-submission-info exp_swin_focal_mixup_001

# 서버 결과 추가
python experiments/submission_manager.py add-server-result \
  --experiment exp_swin_focal_mixup_001 \
  --score 0.8524 \
  --rank 15 \
  --notes "첫 번째 제출"

# 성능 차이 분석
python experiments/submission_manager.py analyze-gaps

# 다음 제출 추천
python experiments/submission_manager.py recommend-next
```

### 결과 분석기
```bash
# 콘솔에 리포트 출력
python experiments/results_analyzer.py

# 마크다운 리포트 생성
python experiments/results_analyzer.py --generate-report

# 특정 파일로 리포트 저장
python experiments/results_analyzer.py --generate-report --output my_report.md

# 요약만 출력
python experiments/results_analyzer.py --summary-only
```

### 실험 모니터
```bash
# 실시간 모니터링 (5초 갱신)
python experiments/experiment_monitor.py

# 10초 간격으로 갱신
python experiments/experiment_monitor.py --interval 10

# 한 번만 상태 확인
python experiments/experiment_monitor.py --once
```

## 📋 실험 결과 JSON 구조

각 실험 완료 후 `experiments/logs/` 디렉토리에 저장되는 JSON 파일:

```json
{
  "experiment_id": "exp_swin_focal_mixup_001",
  "timestamp": "2025-01-07T10:30:00",
  "model": "swin_transformer", 
  "technique": "focal_mixup",
  "config_path": "/path/to/config",
  "success": true,
  "local_results": {
    "validation_f1": 0.8524,
    "validation_acc": 0.8630,
    "training_time_minutes": 85.5,
    "total_epochs": 28,
    "early_stopped": true
  },
  "submission": {
    "csv_path": "/path/to/submission.csv",
    "submission_ready": true,
    "file_size_mb": 2.1,
    "created_at": "2025-01-07T12:45:00"
  },
  "memo_suggestion": {
    "auto_generated": "SwinB384+Focal+Mix50%+TTA",
    "character_count": 24,
    "alternatives": ["SwinB384 Focal+Mix50%", "Auto: SwinB384+Focal+Mix"]
  },
  "server_evaluation": {
    "submitted": false,
    "submission_date": null,
    "server_score": null,
    "server_rank": null,
    "notes": "",
    "performance_gap": null
  }
}
```

## 🔄 일반적인 워크플로우

### 1. 초기 실험 설정 및 실행
```bash
# 1단계: 실험 매트릭스 생성
python experiments/experiment_generator.py

# 2단계: 자동 실험 시작 (백그라운드)
python experiments/auto_experiment_runner.py &

# 3단계: 모니터링 (별도 터미널)
python experiments/experiment_monitor.py
```

### 2. 진행 상황 확인
```bash
# 현재 상태 한 번만 확인
python experiments/experiment_monitor.py --once

# 제출 가능한 실험 확인
python experiments/submission_manager.py list-pending
```

### 3. 제출 및 서버 결과 관리
```bash
# 최고 성능 실험 정보 확인
python experiments/submission_manager.py get-submission-info exp_swin_focal_mixup_001

# 제출 후 서버 결과 추가
python experiments/submission_manager.py add-server-result \
  --experiment exp_swin_focal_mixup_001 \
  --score 0.8524 \
  --rank 15

# 다음 제출 추천받기
python experiments/submission_manager.py recommend-next
```

### 4. 최종 분석 및 리포트
```bash
# 종합 분석 리포트 생성
python experiments/results_analyzer.py --generate-report

# 성능 차이 패턴 분석
python experiments/submission_manager.py analyze-gaps
```

## ⚠️ 주의사항

### 시스템 요구사항
- Python 3.8+
- PyTorch with CUDA
- 충분한 GPU 메모리 (모델에 따라 8GB+ 권장)
- 디스크 공간 (로그 및 모델 저장용)

### 안전 기능
- **GPU 메모리 자동 정리**: 각 실험 후 완전 정리
- **실험 실패 격리**: 한 실험 실패시 다음 실험 계속 진행
- **Resume 기능**: 중단된 지점부터 재시작 가능
- **진행 상황 저장**: 실시간으로 상태 저장

### 문제 해결
```bash
# GPU 메모리 부족시
python experiments/auto_experiment_runner.py --resume

# 특정 실험만 다시 실행하고 싶을 때
# experiment_queue.json에서 해당 실험 status를 'pending'으로 변경

# 로그 확인
tail -f experiments/logs/exp_*.json
```

## 📊 예상 결과

### 전체 실험 시간
- **총 24개 실험**
- **예상 총 시간**: 약 36-40시간
- **최고 우선순위**: EfficientNet-B4 + focal_mixup

### 성능 예상치
- **Baseline 대비 개선**: 2-5% F1 점수 향상 예상
- **최고 조합**: Swin-B384 + focal_mixup 또는 ConvNeXt + label_mixup
- **ROI 최고**: EfficientNet-B4 기반 조합들

이 시스템을 통해 24개의 모든 조합을 체계적으로 테스트하고, 최적의 성능을 달성할 수 있습니다! 🚀
