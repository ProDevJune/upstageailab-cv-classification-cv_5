# 🚀 코드 v2 시스템 사용 가이드

## 🎯 Option A 구현 완료!

**cv-classification 시스템에 코드 v2 파일들이 성공적으로 추가되었습니다.**

### 📂 현재 시스템 구성

#### 🔵 코드 v1 시스템 (기존)
- **모델**: resnet50
- **메인 파일**: `codes/gemini_main.py`
- **설정 파일**: `codes/config.yaml`
- **데이터**: train.csv v1 (최고 성능 달성)

#### 🟢 코드 v2 시스템 (새로 추가)
- **모델**: swin_base_patch4_window12_384.ms_in1k
- **메인 파일**: `codes/gemini_main_v2.py`
- **설정 파일**: `codes/config_v2.yaml`
- **데이터**: train.csv v1 (동일한 데이터 사용)

---

## 🛠️ 시작하기

### 1단계: 권한 설정
```bash
cd /Users/jayden/Developer/Projects/cv-classification
chmod +x set_permissions.sh
./set_permissions.sh
```

### 2단계: Import 테스트 (선택사항)
```bash
python test_v2_imports.py
```

---

## 🎮 시스템 실행 방법

### 🔵 기존 시스템 (코드 v1) 실행
```bash
# 방법 1: 실행 스크립트 사용
./run_code_v1.sh

# 방법 2: 직접 실행
python codes/gemini_main.py --config codes/config.yaml
```

### 🟢 새 시스템 (코드 v2) 실행
```bash
# 방법 1: 실행 스크립트 사용
./run_code_v2.sh

# 방법 2: 직접 실행
python codes/gemini_main_v2.py --config codes/config_v2.yaml
```

---

## 🔍 주요 차이점

| 구분 | 코드 v1 | 코드 v2 |
|------|---------|---------|
| **모델** | resnet50 | swin_base_patch4_window12_384 |
| **증강** | 기본 증강 | Dynamic Augmentation |
| **TTA** | 기본 TTA | 향상된 offline TTA |
| **파일 크기** | 작음 | 큼 (더 많은 기능) |
| **성능** | 검증됨 | 잠재적으로 더 높음 |

---

## 🎨 코드 v2의 새로운 기능

### 🔄 Dynamic Augmentation
- **Weak Policy** (0-5 epoch): 기본 증강
- **Middle Policy** (5-15 epoch): 중간 강도 증강  
- **Strong Policy** (15+ epoch): 강력한 증강

### 🎯 향상된 모델
- **Vision Transformer**: Swin Transformer 기반
- **더 큰 입력 크기**: 384x384
- **향상된 성능**: 잠재적으로 더 높은 정확도

### 📊 개선된 평가
- **Offline TTA**: validation에서 더 정확한 평가
- **시각화**: 잘못 분류된 이미지 자동 저장
- **상세한 분석**: 더 많은 메트릭과 그래프

---

## 💡 사용 팁

### 🔄 시스템 전환
- **빠른 실험**: 코드 v1으로 빠르게 테스트
- **정확한 평가**: 코드 v2로 상세한 분석
- **성능 비교**: 두 시스템 결과 비교

### 📈 성능 최적화
- **batch_size 조정**: GPU 메모리에 맞게 설정
- **epochs 조정**: early stopping 활용
- **증강 강도 조정**: config_v2.yaml에서 설정

### 🔧 문제 해결
- **Import 오류**: `test_v2_imports.py` 실행
- **경로 오류**: data_dir 설정 확인
- **메모리 부족**: batch_size 감소

---

## 📊 예상 결과

### 🔵 코드 v1 (검증된 성능)
- **안정적**: 이미 검증된 결과
- **빠름**: 상대적으로 빠른 학습
- **신뢰성**: EfficientNet-B4에서 최고 성능 달성

### 🟢 코드 v2 (향상된 성능 기대)
- **잠재력**: Vision Transformer의 강력한 성능
- **정확도**: 더 세밀한 증강과 평가
- **미래지향**: 최신 기술 적용

---

## 🎊 결론

**이제 두 가지 강력한 시스템을 모두 사용할 수 있습니다!**

- ✅ **안전성**: 기존 최고 성능 시스템 보존
- ✅ **혁신성**: 새로운 모델과 기법 적용
- ✅ **선택권**: 상황에 맞는 최적 시스템 선택
- ✅ **확장성**: 두 시스템 모두 지속적 개선 가능

### 🚀 다음 단계
1. 두 시스템 모두 테스트 실행
2. 성능 비교 및 분석
3. 최적의 하이퍼파라미터 탐색
4. 앙상블 기법 적용 고려

**Happy Training! 🎯**
