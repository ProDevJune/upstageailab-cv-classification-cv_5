# OCR 지원 자동 실험 시스템 사용 가이드

## 🔤 OCR 기능 추가 사항

### 1. 새로운 실험 차원
기존 **모델 × 기법** 조합에 **OCR 적용 여부**가 추가되었습니다.

- **OCR 미적용**: 기존과 동일한 이미지 분류
- **OCR 적용**: 이미지에서 텍스트를 추출하여 추가 특성으로 활용

### 2. 실험 생성 모드

#### 🎯 실험 생성 모드 옵션
```yaml
# experiment_matrix.yaml에서 설정
experiment_options:
  ocr_experiment_mode: "selective"  # all, selective, none
```

- **all**: 모든 조합에 OCR 적용/미적용 둘 다 생성 (48개 실험)
- **selective**: 상위 기법들에만 OCR 실험 추가 (약 32개 실험)  
- **none**: OCR 없이 기존 24개 실험만 생성

#### 🎲 Selective 모드 설정
```yaml
# 효과가 큰 기법들에만 OCR 적용 실험 생성
ocr_selective_techniques: 
  - "focal_mixup"    # 최고 우선순위
  - "label_mixup" 
  - "mixup_cutmix"
  - "focal_loss"
```

### 3. OCR 설정 옵션

#### 📋 OCR 설정 구조
```yaml
# config 파일에 추가되는 OCR 설정
ocr:
  enabled: true
  description: "OCR 적용 (텍스트 정보 활용)"
  ocr_model: "TrOCR"  # OCR 모델명
  confidence_threshold: 0.7
  max_text_length: 100
  text_embedding_dim: 768
  data_path: "/path/to/ocr_texts"
  features_path: "/path/to/ocr_features"
```

### 4. 실험 ID 명명 규칙

#### 🏷️ 새로운 ID 형식
- **OCR 적용**: `exp_swin_focal_mixup_ocr_001`
- **OCR 미적용**: `exp_swin_focal_mixup_noocr_002`

### 5. 메모 자동 생성 (OCR 지원)

#### 📝 OCR 메모 예시
- **OCR 미적용**: `SwinB384+Focal+Mix50%+TTA`
- **OCR 적용**: `SwinB384+Focal+Mix50%+OCR+TTA`
- **특정 OCR 모델**: `SwinB384+Focal+Mix50%+TrOCR+TTA`

### 6. 사용 방법

#### 🚀 기본 사용법
```bash
# 1. Selective 모드로 OCR 실험 생성 (기본값)
python experiments/experiment_generator.py

# 2. 모든 조합에 OCR 실험 생성
python experiments/experiment_generator.py --ocr-mode all

# 3. OCR 없이 기존 실험만 생성
python experiments/experiment_generator.py --ocr-mode none

# 4. 시뮬레이션
python experiments/experiment_generator.py --ocr-mode all --dry-run
```

#### 📊 제출 관리 (OCR 지원)
```bash
# OCR별로 제출 대기 목록 확인
python experiments/submission_manager.py list-pending-ocr

# 일반 제출 목록 (OCR 정보 포함)
python experiments/submission_manager.py list-pending

# OCR 실험 제출 정보 확인
python experiments/submission_manager.py get-submission-info exp_swin_focal_mixup_ocr_001
```

### 7. OCR 실험 우선순위

#### ⭐ 우선순위 계산 (OCR 차원 추가)
```yaml
priority_weights:
  model_priority: 0.25     # 빠른 모델 우선
  technique_priority: 0.4  # 효과 큰 기법 우선  
  ocr_priority: 0.25       # OCR 효과 우선
  estimated_time: 0.1      # 짧은 시간 우선
```

- OCR 적용 실험이 일반적으로 더 높은 우선순위
- OCR 처리로 인한 시간 증가 고려 (`time_multiplier: 1.2`)

### 8. 실험 결과 예시

#### 📊 실험 통계 예시 (Selective 모드)
```
📊 총 실험 수: 32개
🔤 OCR 적용 실험: 16개
📷 OCR 미적용 실험: 16개
⏱️ 예상 총 소요시간: 52시간 30분
```

#### 🏆 TOP 5 우선순위 (OCR 혼합)
```
1. 🔤 exp_efficientnet_b4_focal_mixup_ocr_001
2. 📷 exp_efficientnet_b4_focal_mixup_noocr_002
3. 🔤 exp_swin_transformer_focal_mixup_ocr_003
4. 🔤 exp_efficientnet_b4_label_mixup_ocr_004
5. 📷 exp_swin_transformer_focal_mixup_noocr_005
```

### 9. 성능 분석 (OCR별)

#### 📈 OCR 효과 분석
```bash
# OCR별 성능 차이 분석
python experiments/submission_manager.py analyze-gaps

# 출력 예시:
# 🔤 OCR 적용 평균 성능 차이: +0.0234
# 📷 OCR 미적용 평균 성능 차이: +0.0187
# 🔤 OCR 적용 평균 서버 점수: 0.8456
# 📷 OCR 미적용 평균 서버 점수: 0.8398
```

### 10. 제출 추천 (OCR 다양성 고려)

#### 🎯 다양성 기반 추천
OCR 적용/미적용 다양성도 고려하여 제출 추천:
- 모델 다양성 (40%)
- 기법 다양성 (30%) 
- OCR 다양성 (20%)
- 조합 다양성 (10%)

### 11. 실제 구현 시 고려사항

#### 🔧 OCR 데이터 준비
```bash
# OCR 텍스트 데이터 디렉토리 생성
mkdir -p /Users/jayden/Developer/Projects/cv-classification/data/ocr_texts
mkdir -p /Users/jayden/Developer/Projects/cv-classification/data/ocr_features
```

#### 📝 config_v2.yaml에 OCR 설정 추가 예시
```yaml
# 기존 설정들...

# 🔥 OCR 설정 추가
ocr:
  enabled: false  # 기본값은 false
  description: "OCR 미적용"
  ocr_model: "TrOCR"
  confidence_threshold: 0.7
  max_text_length: 100
  text_embedding_dim: 768
  data_path: "/Users/jayden/Developer/Projects/cv-classification/data/ocr_texts"
  features_path: "/Users/jayden/Developer/Projects/cv-classification/data/ocr_features"
```

### 12. 명령어 요약

#### 🎮 주요 명령어들
```bash
# OCR 실험 생성
python experiments/experiment_generator.py --ocr-mode selective

# OCR 실험 실행  
python experiments/auto_experiment_runner.py

# OCR별 제출 관리
python experiments/submission_manager.py list-pending-ocr

# OCR 포함 성능 분석
python experiments/results_analyzer.py --generate-report
```

### 📊 예상 실험 시나리오

**Selective 모드 (추천)**:
- 효과적인 4개 기법 × 4개 모델 × 2개 OCR 옵션 = 32개 실험
- 기본 6개 기법 × 4개 모델 × OCR 미적용 = 24개 실험
- 추가 4개 기법 × 4개 모델 × OCR 적용 = 16개 실험
- **총 32개 실험, 약 50-55시간 소요**

이렇게 OCR 기능이 완전히 통합된 자동 실험 시스템이 완성되었습니다! 🎉
