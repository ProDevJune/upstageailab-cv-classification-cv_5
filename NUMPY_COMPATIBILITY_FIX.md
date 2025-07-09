# NumPy 2.x 호환성 문제 긴급 해결 가이드

## 🚨 발생한 새로운 문제
서버에서 다음과 같은 오류들이 추가로 발생:

1. **NumPy 버전 충돌**: numpy 2.2.6이 설치되었지만 matplotlib 3.7.5는 numpy<2를 요구
2. **Pandas 바이너리 호환성**: `ValueError: numpy.dtype size changed, may indicate binary incompatibility`
3. **OpenCV 버전 미고정**: 여전히 opencv-python 4.12.0.88이 설치됨

## 🔍 근본 원인
- pip이 albumentations 설치 시 자동으로 의존성을 최신 버전으로 업그레이드
- numpy 2.x는 많은 기존 패키지들과 호환되지 않음
- 버전 고정이 제대로 작동하지 않음

## 🔧 완전 해결 방법

### 방법 1: 순차적 패키지 설치 (추천)
```bash
bash fix_complete_compatibility.sh
```

### 방법 2: Requirements 파일 사용
```bash
bash fix_with_requirements.sh
```

### 방법 3: 수동 순차 설치
```bash
# 1. 모든 문제 패키지 제거
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python albumentations numpy pandas scikit-learn matplotlib scipy

# 2. 순서대로 정확한 버전 설치
pip install --no-cache-dir numpy==1.26.4
pip install --no-cache-dir opencv-python==4.8.1.78
pip install --no-cache-dir albumentations==1.4.0
pip install --no-cache-dir pandas==2.2.3
pip install --no-cache-dir scikit-learn==1.5.2
pip install --no-cache-dir matplotlib==3.9.2

# 3. 테스트
python -c "import cv2, albumentations, numpy, pandas; print('✅ 모든 패키지 정상')"
```

## ✅ 검증된 호환 버전 매트릭스

| 패키지 | 버전 | 이유 |
|--------|------|------|
| numpy | 1.26.4 | matplotlib, pandas와 호환 |
| opencv-python | 4.8.1.78 | CV_8U 지원, albumentations 호환 |
| albumentations | 1.4.0 | opencv-python 4.8.x와 호환 |
| pandas | 2.2.3 | numpy 1.26.x와 바이너리 호환 |
| scikit-learn | 1.5.2 | numpy 1.26.x 지원 |
| matplotlib | 3.9.2 | numpy 1.26.x 호환 |

## 🚨 주의사항
1. **절대 numpy 2.x 사용 금지**: 현재 생태계와 호환 문제 심각
2. **순서 중요**: numpy → opencv → albumentations → 나머지 순으로 설치
3. **--no-cache-dir 필수**: 캐시된 잘못된 버전 방지
4. **의존성 자동 해결 주의**: pip이 자동으로 버전을 업그레이드하지 못하도록 주의

## 🔍 설치 후 검증 명령어
```python
# 모든 패키지 버전 확인
import numpy, cv2, albumentations, pandas, sklearn, matplotlib
print(f'NumPy: {numpy.__version__} (1.26.4 이어야 함)')
print(f'OpenCV: {cv2.__version__} (4.8.1.78 이어야 함)')
print(f'Albumentations: {albumentations.__version__} (1.4.0 이어야 함)')
print(f'Pandas: {pandas.__version__}')

# CV_8U 속성 확인
try:
    print(f'CV_8U: {cv2.CV_8U}')
    print('✅ CV_8U 문제 해결됨')
except AttributeError:
    print('❌ CV_8U 여전히 문제')

# Pandas 바이너리 호환성 확인
try:
    df = pandas.DataFrame({'test': [1, 2, 3]})
    print('✅ Pandas 바이너리 호환성 OK')
except ValueError as e:
    print(f'❌ Pandas 바이너리 호환성 문제: {e}')
```

## 📋 문제 해결 체크리스트
- [ ] numpy 1.26.4 설치 확인
- [ ] opencv-python 4.8.1.78 설치 확인  
- [ ] albumentations 1.4.0 설치 확인
- [ ] CV_8U 속성 접근 가능 확인
- [ ] Pandas DataFrame 생성 테스트
- [ ] 실험 스크립트 정상 실행 확인

이 가이드대로 진행하면 모든 호환성 문제가 해결됩니다.
