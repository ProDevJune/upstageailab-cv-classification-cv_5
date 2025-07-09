# CV_8U AttributeError 해결 가이드

## 문제 상황
AIStages 서버에서 다음과 같은 오류가 발생:
```
AttributeError: module 'cv2' has no attribute 'CV_8U'
```

## 원인
- `albumentations==1.4.18`과 `opencv-python==4.10.0.84` 버전 조합의 호환성 문제
- OpenCV 4.10.x에서 일부 상수명이 변경되어 albumentations와 충돌

## 해결 방법

### 방법 1: 자동 수정 스크립트 (권장)
```bash
# 서버에서 실행 (강화 버전)
bash fix_cv_8u_error_robust.sh

# 또는 간단 버전
bash fix_cv_8u_simple.sh
```

### 방법 2: 수동 설치 (pip 캐시 오류 대응)
```bash
# 1. 기존 패키지 제거
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python albumentations

# 2. 호환 버전 설치 (캐시 비활성화 대응)
pip install --no-cache-dir opencv-python==4.8.1.78
pip install --no-cache-dir albumentations==1.4.0

# 3. 확인
python -c "import cv2; import albumentations as A; print('✅ 문제 해결됨')"
```

### 방법 3: requirements 파일 업데이트
```bash
# 새로운 requirements 파일 사용
pip install -r requirements_ubuntu_fixed.txt
```

## 검증된 호환 버전 조합
- `opencv-python==4.8.1.78` + `albumentations==1.4.0`
- `opencv-python==4.7.1.72` + `albumentations==1.3.1`
- `opencv-python==4.6.0.66` + `albumentations==1.3.0`

## 주의사항
1. **가상환경 활성화**: 먼저 `source venv/bin/activate` 실행
2. **pip 캐시 오류**: `pip cache purge` 실패 시 `--no-cache-dir` 옵션 사용
3. **버전 확인**: 설치 후 반드시 버전 확인
4. **시스템 재시작**: 필요시 컨테이너/세션 재시작

## 일반적인 오류 대응

### "pip cache commands can not function since cache is disabled"
```bash
# 캐시 비활성화 환경에서는 --no-cache-dir 옵션 사용
pip install --no-cache-dir opencv-python==4.8.1.78
pip install --no-cache-dir albumentations==1.4.0
```

### 설치 실패 시 대안 버전
```bash
# 대안 1: 더 안정적인 버전
pip install --no-cache-dir opencv-python==4.7.1.72
pip install --no-cache-dir albumentations==1.3.1

# 대안 2: 최소 호환 버전
pip install --no-cache-dir opencv-python==4.6.0.66
pip install --no-cache-dir albumentations==1.3.0
```

## 설치 후 확인 명령어
```python
import cv2
import albumentations as A
print(f'OpenCV: {cv2.__version__}')
print(f'Albumentations: {A.__version__}')

# CV_8U 속성 확인
try:
    print(f'CV_8U 상수 확인: {cv2.CV_8U}')
    print('✅ 모든 속성이 정상적으로 접근 가능합니다.')
except AttributeError as e:
    print(f'❌ 여전히 문제가 있습니다: {e}')
```

## Git 동기화
로컬에서 파일 수정 후:
```bash
git add .
git commit -m "Fix CV_8U AttributeError - update opencv & albumentations versions"
git push origin main
```

서버에서:
```bash
git pull origin main
bash fix_cv_8u_error.sh
```

## 추가 정보
- 이 오류는 OpenCV 4.10.x의 API 변경으로 인한 것입니다
- albumentations 팀에서도 인지하고 있는 문제입니다
- 향후 albumentations 새 버전에서 수정될 예정입니다

## 문제 지속시 대안
1. **AlbumentationsX 사용**: 차세대 라이브러리로 마이그레이션
2. **Docker 환경**: 검증된 환경 이미지 사용
3. **버전 고정**: requirements.txt에 정확한 버전 명시
