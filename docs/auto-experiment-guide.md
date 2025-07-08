# 🤖 자동화 실험 시스템 구축 가이드

## 📋 개요

이 가이드는 CV 분류 프로젝트에서 **모든 하이퍼파라미터 조합을 자동으로 실험**하고 **최적 설정을 찾는 시스템**을 구축하는 방법을 설명합니다.

**핵심 원칙**: 기존 파일(`gemini_main.py`, `config.yaml`)은 수정하지 않고, 새로운 파일들을 생성하여 병렬로 운영

---

## 📁 추가/수정해야 할 파일 목록

### 🆕 새로 생성할 파일들

```
codes/
├── auto_main.py              # 🆕 자동화용 메인 실행 파일 (gemini_main.py 기반)
├── config_auto.yaml          # 🆕 자동화용 설정 템플릿
├── auto_experiment.py        # 🆕 자동화 실험 스크립트
├── experiment_tracker.py     # 🆕 결과 분석 및 추적 스크립트
├── run_experiments.sh        # 🆕 통합 실행 스크립트
└── practice/                 # 📁 자동 생성 설정 파일들 저장소
    ├── exp_quick_001.yaml
    ├── exp_quick_002.yaml
    └── ...

docs/
└── auto-experiment-guide.md  # 📄 이 가이드 문서

# 결과 파일들 (자동 생성)
experiment_results.csv         # 모든 실험 결과 통합 관리
experiment_analysis.png        # 결과 시각화 그래프
```

### 🔒 기존 파일들 (수정하지 않음)

```
codes/
├── gemini_main.py            # 🔒 기존 메인 파일 (보존)
├── config.yaml               # 🔒 기존 설정 파일 (보존)
├── gemini_*.py               # 🔒 기존 모듈들 (보존)
└── ...
```

---

## 🛠️ 각 파일별 구현 내용

### **1. auto_main.py**
```python
# gemini_main.py 기반으로 생성, 추가 기능:
# - 실험 결과 자동 저장 (JSON, CSV)
# - experiment_id 기반 추적
# - WandB 통합 로깅
# - 에러 핸들링 강화

if __name__ == "__main__":
    # 기존 gemini_main.py 로직 + 결과 저장
    experiment_results = save_experiment_results(cfg, trainer, val_f1, submission_path)
    update_experiment_csv(experiment_results)
```

### **2. config_auto.yaml**
```yaml
# 확장된 설정 템플릿, 실험 변수들:
experiment_id: "manual_experiment"
model_name: 'resnet50.tv2_in1k'  # 실험 대상 모델들
image_size: 224                   # [224, 320, 384]
lr: 0.0001                       # [0.001, 0.0001, 0.00001]
augmentation_strength: "moderate" # [minimal, moderate, strong]
TTA: True                        # [True, False]
n_folds: 0                       # [0, 5, 10]

# 자동 실험에서 조정되는 변수들
# - batch_size: [16, 32, 64]
# - optimizer_name: ['Adam', 'AdamW']  
# - scheduler_name: ['CosineAnnealingLR', 'OneCycleLR']
```

### **3. auto_experiment.py**
```python
# 자동화 실험 관리 클래스
class AutoExperiment:
    def __init__(self, base_config_path="config_auto.yaml")
    
    def define_experiment_space(self, experiment_type="quick"):
        # quick: 30분/실험, 20개 조합
        # full: 3시간/실험, 100개 조합  
        # targeted: 특정 가설 검증
    
    def generate_experiments(self, experiment_type, max_experiments):
        # 모든 하이퍼파라미터 조합 생성
    
    def run_experiments(self, experiments):
        # 순차적으로 실험 실행 및 결과 기록

# 실행: python auto_experiment.py --type quick --max 20
```

### **4. experiment_tracker.py**
```python
# 실험 결과 분석 및 추적
class ExperimentTracker:
    def get_summary(self):
        # 실험 현황 요약 (완료/실행중/실패)
    
    def get_top_experiments(self, n=10):
        # 상위 N개 실험 조회
    
    def analyze_hyperparameters(self):
        # 하이퍼파라미터별 성능 영향 분석
    
    def create_visualizations(self):
        # 결과 시각화 그래프 생성
    
    def generate_recommendations(self):
        # 최적 설정 추천

# 실행: python experiment_tracker.py --action summary
```

### **5. run_experiments.sh**
```bash
#!/bin/bash
# 통합 실험 관리 스크립트

show_menu() {
    echo "1) 빠른 스크리닝 실험 (⚡ 20개, 30분/실험)"
    echo "2) 전체 실험 (🔬 50개, 3시간/실험)"
    echo "3) 타겟 실험 (🎯 특정 가설 검증)"
    echo "4) 실험 결과 분석 (📊)"
    echo "5) 최고 성능 모델 내보내기 (💾)"
}

# 실행: ./run_experiments.sh
```

---

## 🚀 실행 방법

### **1. 초기 설정**
```bash
# 실행 권한 부여
chmod +x run_experiments.sh

# 필요한 폴더 생성
mkdir -p practice
mkdir -p data/submissions
```

### **2. 실험 실행 방법**

#### **방법 1: 통합 메뉴 사용 (추천)**
```bash
./run_experiments.sh
# 대화형 메뉴에서 선택
```

#### **방법 2: 직접 명령어 실행**
```bash
# 빠른 스크리닝 (30분/실험)
python auto_experiment.py --type quick --max 20

# 전체 실험 (3시간/실험)
python auto_experiment.py --type full --max 50

# 타겟 실험 (특정 가설)
python auto_experiment.py --type targeted
```

#### **방법 3: 수동 실험**
```bash
# 새로운 시스템으로 수동 실험
python auto_main.py --config config_auto.yaml

# 기존 시스템 (변경 없음)
python gemini_main.py --config config.yaml
```

### **3. 결과 분석**
```bash
# 실험 요약 확인
python experiment_tracker.py --action summary

# 상위 10개 실험 조회
python experiment_tracker.py --action top --n 10

# 하이퍼파라미터 영향 분석
python experiment_tracker.py --action analyze

# 시각화 생성
python experiment_tracker.py --action visualize

# 최적 설정 추천
python experiment_tracker.py --action recommend

# 최고 성능 모델 내보내기
python experiment_tracker.py --action export --n 5
```

---

## 📊 실험 전략

### **Phase 1: 빠른 스크리닝 (1-2일)**
- **목적**: 유망한 모델/설정 조합 식별
- **설정**: 20-30개 조합, 50 epochs, 30분/실험
- **변수**: model, image_size, lr, augmentation 기본 조합

### **Phase 2: 집중 실험 (3-5일)**
- **목적**: 상위 설정들로 심화 학습
- **설정**: 상위 10개 조합, 1000 epochs, 3시간/실험
- **추가**: K-fold 교차검증, TTA 적용

### **Phase 3: 최종 최적화 (1-2일)**
- **목적**: 최고 성능 달성
- **설정**: 최고 3-5개 모델 앙상블
- **검증**: 서버 제출 및 점수 확인

---

## 🔍 경우의 수 분석

### **실험 변수들**
```yaml
# 주요 실험 변수 (경우의 수)
models: [4개]          # resnet34, resnet50, efficientnet_b3, convnext_tiny
image_sizes: [3개]     # 224, 320, 384  
learning_rates: [3개]  # 0.001, 0.0001, 0.00001
augmentation: [3개]    # minimal, moderate, strong
TTA: [2개]            # True, False
k_folds: [3개]        # 0, 5, 10

# 기본 조합: 4 × 3 × 3 × 3 × 2 × 3 = 648가지
# 빠른 실험: 20개 선별 (30분 × 20 = 10시간)
# 전체 실험: 100개 선별 (3시간 × 100 = 12.5일)
```

### **스마트 실험 전략**
- **1단계**: Quick 모드로 유망한 조합 발견
- **2단계**: Top 10 조합으로 긴 학습
- **3단계**: 최종 앙상블로 성능 극대화

---

## 📈 결과 추적 시스템

### **experiment_results.csv 구조**
```csv
experiment_id,model_name,image_size,lr,augmentation_strength,TTA,final_f1,training_time_min,status
exp_quick_001,resnet34,224,0.0001,moderate,True,0.8234,28.5,completed
exp_quick_002,efficientnet_b3,320,0.001,strong,True,0.8456,45.2,completed
...
```

### **자동 시각화**
- 모델별 성능 비교 막대 그래프
- 학습률별 성능 영향 분석
- 학습 시간 vs 성능 산점도
- 증강 전략별 효과 비교

### **최적 설정 추천**
- 최고 성능 실험 정보
- 변수별 최적값 조합
- 추천 config 파일 자동 생성

---

## 💡 주요 장점

### **1. 기존 시스템 보존**
- `gemini_main.py`, `config.yaml` 수정 없음
- 언제든지 기존 방식으로 복귀 가능
- 팀 다른 멤버들에게 영향 없음

### **2. 체계적 실험 관리**
- 모든 실험 결과 자동 기록 및 추적
- 실험 재현성 보장
- 최적 설정 자동 발견

### **3. 효율적 리소스 사용**
- 빠른 스크리닝으로 시간 절약
- 유망한 조합에 집중 투자
- 자동화로 수동 작업 최소화

### **4. 확장성**
- 새로운 모델, 기법 쉽게 추가
- 실험 타입 커스터마이징 가능
- 결과 분석 도구 지속 개선

---

## 🚨 주의사항

### **1. 디스크 공간 관리**
```bash
# 정기적으로 확인 필요
du -sh practice/        # 설정 파일들
du -sh data/submissions/  # 제출 파일들
du -sh logs/            # 로그 파일들
```

### **2. GPU 메모리 관리**
- 큰 모델 + 큰 이미지 = OOM 위험
- batch_size 자동 조정 필요
- 실험별 메모리 사용량 모니터링

### **3. 시간 관리**
- Quick 모드: 30분/실험 × 20개 = 10시간
- Full 모드: 3시간/실험 × 100개 = 12.5일
- 우선순위 기반 실험 권장

---

## 🔧 트러블슈팅

### **실험 실패시**
```bash
# 실패한 실험 확인
python experiment_tracker.py --action summary

# 특정 실험부터 재시작
python auto_experiment.py --type quick --start 5
```

### **디스크 공간 부족시**
```bash
# 오래된 실험 결과 정리
find practice/ -name "*.yaml" -mtime +7 -delete
find data/submissions/ -name "*.csv" -mtime +7 -delete
```

### **성능 최적화**
```bash
# 병렬 실행 (GPU 여러 개인 경우)
CUDA_VISIBLE_DEVICES=0 python auto_main.py --config exp_001.yaml &
CUDA_VISIBLE_DEVICES=1 python auto_main.py --config exp_002.yaml &
```

---

## 📞 도움말

### **기본 명령어**
```bash
# 도움말 보기
python auto_experiment.py --help
python experiment_tracker.py --help
./run_experiments.sh --help

# 실험 상태 확인
./run_experiments.sh --status

# 결과 빠른 확인
./run_experiments.sh --analyze
```

### **문제 발생시**
1. 기존 시스템으로 복귀: `python gemini_main.py --config config.yaml`
2. 로그 확인: `tail -f logs/training.log`
3. 메모리 사용량: `nvidia-smi` 또는 `htop`
4. 디스크 공간: `df -h`

---

**🎯 이 시스템을 통해 체계적이고 효율적으로 최적의 하이퍼파라미터 조합을 찾을 수 있습니다!**

---

*📅 작성일: 2025년 7월 4일*  
*✍️ 작성자: AI Assistant*  
*📁 파일 위치: `/docs/auto-experiment-guide.md`*  
*🔄 최종 수정: 프로젝트 진행에 맞춰 지속 업데이트*
