# AIStages 통합 실험 관리 시스템

HPO(Hyperparameter Optimization) 실험과 AIStages 서버 점수를 통합 관리하는 시스템입니다.

## 🚀 주요 기능

### 1️⃣ HPO 실험 관리
- 자동 하이퍼파라미터 최적화
- 다양한 모델 및 설정 조합
- 실험 결과 자동 추적

### 2️⃣ AIStages 통합
- 제출 후보 자동 추천
- 서버 점수 기록 및 분석
- 로컬 vs 서버 성능 상관관계 분석

### 3️⃣ 분석 및 최적화
- 과적합 위험도 평가
- 앙상블 후보 추천
- 전략 분석 및 리포트 생성

## 📋 시스템 구성

```
cv-classification/
├── enhanced_experiment_tracker.py  # 확장된 실험 추적기
├── aistages_manager.py             # Python 인터페이스 (메인)
├── run_aistages.py                 # 빠른 실행 스크립트
├── hpo_aistages_integration.sh     # Shell 스크립트
├── experiment_results.csv          # 기본 실험 결과
└── enhanced_experiment_results.csv # 확장된 결과 (AIStages 포함)
```

## 🎯 사용법

### 기본 실행 (대화형 메뉴)
```bash
python aistages_manager.py
```

### 빠른 명령어
```bash
# 빠른 HPO 실험
python aistages_manager.py quick

# 실험 결과 확인
python aistages_manager.py check

# 도움말
python aistages_manager.py --help
```

### 메뉴 구성
```
🚀 HPO + AIStages 통합 실험 시스템
============================================================
1️⃣  새 HPO 실험 실행
2️⃣  기존 실험 결과 확인
3️⃣  AIStages 제출 후보 추천
4️⃣  AIStages 제출 준비
5️⃣  AIStages 결과 기록 ⭐ (중요!)
6️⃣  로컬 vs 서버 분석
7️⃣  앙상블 후보 추천
8️⃣  전체 리포트 생성
0️⃣  종료
```

## 🔥 핵심 워크플로우

### 1. HPO 실험 실행
```bash
# 메뉴 1번 → quick/medium/full 선택
```

### 2. 제출 후보 선택
```bash
# 메뉴 3번 → 전략 선택:
# - best_local: 로컬 성능 우선
# - diverse: 다양한 설정 조합
# - conservative: 과적합 위험 최소화
```

### 3. AIStages 제출
```bash
# 메뉴 4번 → 실험 ID 입력
# → 제출 파일 경로 확인
```

### 4. ⭐ 서버 점수 기록 (필수!)
```bash
# 메뉴 5번 → AIStages 점수 입력
# → 자동 과적합 위험도 평가
# → 상관관계 분석 업데이트
```

### 5. 분석 및 최적화
```bash
# 메뉴 6번: 로컬 vs 서버 상관관계 분석
# 메뉴 7번: 앙상블 후보 추천
# 메뉴 8번: 종합 리포트 생성
```

## 📊 분석 기능

### 로컬 vs 서버 상관관계
- 상관계수 계산
- 점수 차이 분석
- 과적합 패턴 감지
- 시각화 그래프 생성

### 과적합 위험도 평가
- **High**: 서버 점수가 로컬보다 0.05 이상 낮음
- **Medium**: 서버 점수가 로컬보다 0.02~0.05 낮음  
- **Low**: 안정적인 성능

### 앙상블 추천
- 높은 서버 점수 + 낮은 과적합 위험
- 모델 다양성 고려
- 최고 성과 전략 분석

## 📈 실제 사용 예시

```bash
# 1. 시스템 시작
python aistages_manager.py

# 2. 기존 실험 확인
메뉴 2번 선택

# 3. 제출 후보 추천
메뉴 3번 → diverse 전략 선택

# 4. 제출 준비
메뉴 4번 → exp_quick_003_2507041446 입력

# 5. AIStages 제출 후 점수 기록
메뉴 5번 → 
  실험 ID: exp_quick_003_2507041446
  Public Score: 0.8756
  Public Rank: 15

# 6. 분석 확인
메뉴 6번 → 상관관계 분석 및 시각화
```

## 🎯 주요 이점

### 1. 체계적인 실험 관리
- 로컬 실험부터 서버 제출까지 일원화
- 모든 실험의 추적 가능성 보장

### 2. 데이터 기반 의사결정
- 로컬 validation 신뢰도 평가
- 과적합 패턴 조기 발견
- 최고 성과 전략 학습

### 3. 효율적인 제출 전략
- 제한된 제출 횟수 최적 활용
- 앙상블을 위한 다양성 확보
- 위험도 기반 우선순위 결정

## 📂 생성되는 파일들

- `enhanced_experiment_results.csv` - 통합 실험 결과
- `submission_report.html` - 제출용 리포트
- `full_analysis_report.html` - 전체 분석 리포트
- `analysis_results/local_vs_server_correlation.png` - 상관관계 시각화

## ⚠️ 중요 사항

### 반드시 해야 할 일:
1. **AIStages 제출 후 점수 기록** - 메뉴 5번으로 서버 점수 입력
2. **상관관계 분석** - 5-10개 제출 후 validation 전략 검토
3. **과적합 패턴 학습** - 높은 위험도 실험들의 공통점 파악

### 권장 사항:
- 첫 5개 제출: 다양한 전략으로 상관관계 파악
- 이후 제출: 분석 결과 기반 최적화
- 앙상블: 안정적인 성능의 다양한 모델 조합

## 🔧 문제 해결

### 모듈 임포트 오류
```bash
pip install pandas matplotlib seaborn numpy
```

### 실험 결과 파일 없음
```bash
# 먼저 HPO 실험 실행
python start_hpo.py
```

### 권한 오류
```bash
chmod +x run_aistages.py
chmod +x hpo_aistages_integration.sh
```

---

💡 **이 시스템으로 로컬 실험과 서버 성능 간의 gap을 분석하고, 더 나은 대회 전략을 수립할 수 있습니다!**
