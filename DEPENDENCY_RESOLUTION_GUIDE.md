# 의존성 충돌 완전 해결 가이드

## 🚨 현재 상황
pip 의존성 해결기가 다음과 같은 경고들을 출력하고 있습니다:
- `albucore 0.0.9 requires opencv-python-headless>=4.9.0.80`
- `qudida 0.0.4 requires opencv-python-headless>=4.0.1`
- `seaborn 0.12.2 requires matplotlib!=3.6.1,>=3.1`

하지만 **이러한 경고는 실제 기능에 영향을 주지 않을 수 있습니다**.

## 🎯 해결 방법 (3단계 접근)

### 1단계: 현재 설정 테스트 (빠른 확인)
```bash
bash test_current_setup.sh
```
**목적**: 의존성 경고가 있어도 실제로는 정상 작동하는지 확인

### 2단계: 의존성 충돌 강제 해결 (권장)
```bash
bash fix_dependency_conflicts.sh
```
**특징**: 
- `--no-deps` 옵션으로 의존성 체크 우회
- 순차적 패키지 설치로 충돌 방지
- 모든 기능 테스트 포함

### 3단계: 가상환경 완전 재생성 (최종 수단)
```bash
bash recreate_venv.sh
```
**특징**: 
- 기존 환경 백업 후 새로 생성
- 모든 의존성 문제 원천 해결
- 가장 확실하지만 시간 소요

## 📋 각 방법의 장단점

| 방법 | 시간 | 확실성 | 복잡성 | 추천도 |
|------|------|--------|--------|---------|
| 1단계 테스트 | 1분 | 중간 | 낮음 | ⭐⭐⭐⭐ |
| 2단계 강제해결 | 5분 | 높음 | 중간 | ⭐⭐⭐⭐⭐ |
| 3단계 재생성 | 10분 | 최고 | 높음 | ⭐⭐⭐ |

## 🔍 의존성 경고 vs 실제 오류

### 경고만 나오는 경우 (실행 가능)
```
ERROR: pip's dependency resolver does not currently take into account...
```
→ **실험 실행 가능**, 기능상 문제 없음

### 실제 오류가 나오는 경우 (실행 불가)
```
ModuleNotFoundError: No module named 'cv2'
AttributeError: module 'cv2' has no attribute 'CV_8U'
ValueError: numpy.dtype size changed
```
→ **실험 실행 불가**, 반드시 해결 필요

## 💡 권장 실행 순서

```bash
# 1. 현재 상태 확인
bash test_current_setup.sh

# 만약 테스트가 성공하면
python codes/gemini_main_v2.py --config [config_file]

# 만약 테스트가 실패하면
bash fix_dependency_conflicts.sh

# 그래도 안 되면
bash recreate_venv.sh
```

## 🧪 핵심 테스트 코드
설치 후 이 코드로 정상 작동 확인:
```python
import cv2
import albumentations as A
import numpy as np

# CV_8U 테스트
print(f"CV_8U: {cv2.CV_8U}")

# Albumentations 테스트
transform = A.HorizontalFlip(p=1.0)
test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
result = transform(image=test_img)
print("✅ 모든 기능 정상!")
```

## 🎯 최종 목표
**의존성 경고는 무시하고 실제 기능이 정상 작동하면 실험 진행!**

경고 메시지가 많이 나와도 실험이 정상적으로 실행되면 문제없습니다.
