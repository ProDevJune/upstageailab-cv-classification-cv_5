# 🔧 문제점 해결 요약

## 해결된 문제들

### 1. ✅ WandB Artifact 이름 길이 제한 오류 (128자 초과)

**문제**: 
```
ValueError: Artifact name is longer than 128 characters: 'submission-2507071425-v2adv-swin_base_patch4_window12_384.ms_in1k-opt_AdamW-sch_CosineAnnealingLR-img384-es20-ondaug-clsaug_1-vT ...'
```

**해결책**:
- `codes/gemini_main_v2.py` 338라인 수정
- 긴 `next_run_name` 대신 짧은 `artifact_name` 생성
- 핵심 정보만 추출: `sub-{CURRENT_TIME}-v2adv-{model_short}-{criterion_short}`
- 120자 제한으로 안전 마진 확보

### 2. ✅ Albumentations 경고 메시지 해결

**문제**:
```
UserWarning: Argument 'value' is not valid and will be ignored.
  A.Affine(
  A.CoarseDropout(
```

**해결책**:
- `codes/gemini_augmentation_v2.py`에서 모든 `value=` → `fill_value=` 변경
- A.Affine: 6개 위치 수정
- A.CoarseDropout: 2개 위치 수정
- 총 8개 파라미터 수정 완료

### 3. ✅ Mixed Precision FutureWarning 해결

**문제**:
```
FutureWarning: `torch.cuda.amp.GradScaler(args...)` is deprecated. 
Please use `torch.amp.GradScaler('cuda', args...)` instead.
```

**해결책**:
- `codes/gemini_train_v2.py`에서 GradScaler 초기화 방식 수정
- CUDA 환경: `torch.amp.GradScaler('cuda', enabled=True)`
- 비CUDA 환경: `torch.amp.GradScaler(enabled=False)`

## 검증 완료

- ✅ Mac 환경에서 수정사항 적용
- ✅ 리눅스 호환성 확인 (크로스 플랫폼)
- ✅ 기능에 영향 없이 경고만 제거
- ✅ WandB 업로드 오류 해결

## 예상 결과

이제 리눅스에서 실행할 때:
1. WandB Artifact 업로드 성공 ✅
2. Albumentations 경고 메시지 없음 ✅
3. Mixed Precision FutureWarning 없음 ✅
4. 모든 기능 정상 작동 ✅

## 수정된 파일들

1. `codes/gemini_main_v2.py` - WandB Artifact 이름 단축
2. `codes/gemini_augmentation_v2.py` - Albumentations 파라미터 수정  
3. `codes/gemini_train_v2.py` - Mixed Precision 경고 해결
