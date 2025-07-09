# 🔍 환경별 사전 검증 및 모니터링 시스템

Mac/Ubuntu 환경을 자동 인식하여 MPS/CUDA 사용 가능성과 모든 요구사항을 사전 검증하고, 장시간 실행되는 실험을 모니터링하는 시스템입니다.

## 🎯 핵심 기능

### ✅ **완벽한 사전 검증**
- **환경 자동 인식**: Mac MPS / Ubuntu CUDA 자동 감지
- **필수 패키지 검증**: 모든 의존성 패키지 설치 확인
- **하드웨어 검증**: GPU/CPU 성능 테스트
- **파일 구조 검증**: 필요한 모든 파일 존재 확인
- **설정 파일 검증**: YAML 파일 파싱 및 구조 확인
- **실행 시간 추정**: 전체 실험 소요 시간 계산

### ✅ **실시간 모니터링**
- **시스템 리소스 감시**: CPU, 메모리, 디스크, GPU 사용률
- **프로세스 상태 추적**: 실험 프로세스 실행 상태 및 실행 시간
- **장애 감지**: 리소스 부족, 프로세스 실패 등 자동 감지
- **실시간 알림**: 문제 발생 시 즉시 알림

### ✅ **빠른 테스트 시스템**
- **1-3분 테스트**: 실제 긴 실험 전 빠른 검증
- **컴포넌트 검증**: 모든 시스템이 정상 작동하는지 확인
- **실행 시간 추정**: 테스트 결과로 전체 실험 시간 예측

## 📂 시스템 구성

```
validation_system/
├── validate_experiment_system.py    # 완전한 사전 검증 시스템
├── quick_test_experiments.py        # 빠른 테스트 실험 실행기
├── experiment_monitor.py            # 실시간 모니터링 시스템
├── validate_complete_system.sh      # 통합 검증 스크립트
└── validation_report.yaml           # 상세 검증 결과 (자동 생성)
```

## 🚀 사용 방법

### 1단계: 전체 시스템 검증

#### **통합 검증 스크립트 (추천)**
```bash
# 권한 설정
chmod +x validate_complete_system.sh

# 전체 검증 실행
./validate_complete_system.sh
```

#### **개별 검증 실행**
```bash
# 시스템 환경 검증
python validate_experiment_system.py

# 빠른 테스트 실험
python quick_test_experiments.py
```

### 2단계: 실제 실험 실행 + 모니터링

#### **모니터링과 함께 실험 실행 (장시간 실험 시 권장)**
```bash
# 터미널 1: 모니터링 시작
python experiment_monitor.py --start

# 터미널 2: 실험 실행
python hyperparameter_system/run_experiments.py
```

#### **일반 실험 실행**
```bash
python hyperparameter_system/run_experiments.py
```

## 📊 검증 항목

### 🖥️ **시스템 환경**
- ✅ **OS 감지**: macOS (MPS) / Linux (CUDA) 자동 인식
- ✅ **Python 버전**: 3.8+ 확인
- ✅ **가상환경**: 활성화 상태 확인

### 📦 **필수 패키지**
- ✅ **PyTorch**: torch, torchvision (MPS/CUDA 지원)
- ✅ **ML 라이브러리**: timm, albumentations, scikit-learn
- ✅ **데이터 처리**: pandas, numpy, opencv-python
- ✅ **시각화**: matplotlib, seaborn
- ✅ **기타**: wandb, PyYAML, Pillow, psutil, tqdm

### 🔧 **하드웨어 성능**
- ✅ **GPU 감지**: CUDA/MPS 사용 가능성
- ✅ **성능 테스트**: 간단한 연산으로 속도 측정
- ✅ **메모리 확인**: 시스템/GPU 메모리 용량

### 📁 **파일 구조**
- ✅ **핵심 파일**: gemini_main_v2.py, config_v2.yaml
- ✅ **데이터**: train.csv, train/, test/ 디렉토리
- ✅ **실험 시스템**: hyperparameter_system/ 전체 구조
- ✅ **실행 스크립트**: 권한 설정 확인

### ⚙️ **설정 파일**
- ✅ **YAML 파싱**: 모든 설정 파일 문법 확인
- ✅ **필수 섹션**: 모델, 카테고리, 옵션 구조 검증
- ✅ **실험 수 계산**: 총 예상 실험 개수

### 💾 **리소스 요구사항**
- ✅ **디스크 공간**: 최소 10GB 여유 공간
- ✅ **메모리**: 최소 8GB, 권장 16GB
- ✅ **실행 시간**: 전체 실험 소요 시간 추정

## 📋 검증 결과 예시

### ✅ **성공 사례**
```
🎊 모든 필수 요구사항 만족! 실험 실행 가능

🖥️ 시스템 정보:
   OS: macOS (arm64)
   Python: 3.11.5
   디바이스: 🍎 MPS

📦 패키지 상태:
   ✅ torch: 2.1.0
   ✅ timm: 0.9.2
   ✅ wandb: 0.15.12

🔧 하드웨어:
   ✅ Apple MPS 사용 가능
   ⏱️ 연산 테스트: 0.045초 (fast)

📊 예상 실험:
   실험 수: 60개
   총 시간: 45시간 (1.9일)
   실험당: 45분 (MPS)

🚀 실행 준비 완료!
```

### ❌ **문제 발견 사례**
```
❌ 실험 실행 전 해결해야 할 중요 문제들:
   • 누락된 패키지: ['torch', 'timm', 'wandb']
   • 하드웨어 검증 실패: GPU not available
   • 누락된 파일: ['data/train.csv']

⚠️ 경고 사항:
   • 가상환경이 활성화되지 않음
   • 디스크 공간 부족

💡 권장 사항:
   • 누락된 패키지 설치: pip install torch timm wandb
   • GPU 사용 권장 (CUDA 또는 MPS)
```

## 🔍 빠른 테스트 시스템

### 📋 **테스트 내용**
실제 긴 실험 전에 1-3분의 빠른 테스트로 모든 컴포넌트 검증:

1. **ResNet50 + Optimizer 테스트** (1 에포크)
2. **EfficientNet-B4 + Loss Function 테스트** (1 에포크)  
3. **EfficientNet-B3 + Scheduler 테스트** (1 에포크)

### 📊 **테스트 결과**
```
🧪 빠른 테스트 실험 결과 요약
========================================

   성공: 3/3개
   평균 실행 시간: 127.3초

🎊 모든 테스트 통과! 본격적인 실험 실행 가능

⏱️ 전체 실험 시간 추정:
   실험당 예상 시간: 106.1분
   총 실험 수: 60개
   총 예상 시간: 106.1시간 (4.4일)
```

## 📡 실시간 모니터링

### 🔍 **모니터링 항목**
- **시스템 리소스**: CPU 95%, 메모리 90%, 디스크 95% 임계값
- **GPU 상태**: GPU 메모리 95% 임계값
- **프로세스 추적**: 실험 프로세스 실행 시간 모니터링
- **장애 감지**: 2시간 이상 실행, 프로세스 실패 등

### 🚨 **알림 예시**
```
⚠️ [2025-07-09 14:30:15] CPU 사용률 높음: 96.2%
⚠️ [2025-07-09 14:32:20] 장시간 실행 실험 감지: PID 12345 (2.1시간)
⚠️ [2025-07-09 14:35:45] GPU 0 메모리 사용률 높음: 97.3%
```

### 📊 **모니터링 상태 리포트**
```bash
# 현재 상태 확인
python experiment_monitor.py --status

🔍 실험 모니터링 상태 리포트
==================================================
✅ 모니터링 활성화

🖥️ 시스템 상태:
   CPU: 45.2%
   메모리: 67.8%
   디스크: 23.1% (여유: 450.2GB)
   GPU: 2개 사용 가능

✅ 경고 없음
```

## 🎯 환경별 최적화

### 🍎 **macOS + Apple Silicon**
```
✅ 자동 감지된 최적화:
   디바이스: MPS
   실험당 시간: 45분
   배치 크기: 보수적 설정
   Mixed Precision: 비활성화
```

### 🐧 **Ubuntu + NVIDIA GPU**
```
✅ 자동 감지된 최적화:
   디바이스: CUDA
   실험당 시간: 30분
   배치 크기: 적극적 설정
   Mixed Precision: 활성화
```

### 💻 **CPU 전용**
```
⚠️ 자동 감지된 제한:
   디바이스: CPU
   실험당 시간: 120분
   배치 크기: 최소 설정
   권장: GPU 환경 사용
```

## 🛠️ 문제 해결

### 📦 **패키지 설치 오류**
```bash
# macOS Apple Silicon
pip install torch torchvision torchaudio

# Ubuntu CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 기타 패키지
pip install timm albumentations opencv-python pandas numpy scikit-learn matplotlib seaborn tqdm wandb PyYAML Pillow psutil
```

### 📁 **파일 구조 문제**
```bash
# 필수 파일 확인
ls codes/gemini_main_v2.py
ls codes/config_v2.yaml  
ls data/train.csv         # 또는 train0705a.csv
ls -d data/train/
ls -d data/test/

# 권한 설정
chmod +x setup_hyperparameter_system.sh
./setup_hyperparameter_system.sh
```

### 🔧 **하드웨어 문제**
```bash
# CUDA 설치 확인 (Ubuntu)
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# MPS 확인 (macOS)
python -c "import torch; print(torch.backends.mps.is_available())"
```

## 📋 체크리스트

### ✅ **실험 실행 전 필수 체크**
- [ ] `./validate_complete_system.sh` 실행하여 모든 검증 통과
- [ ] 빠른 테스트 성공 확인
- [ ] 충분한 디스크 공간 (10GB+) 확보
- [ ] 실험 시간 계획 수립 (예상 시간 확인)
- [ ] 장시간 실험 시 모니터링 시스템 준비

### ✅ **실험 실행 중 권장사항**
- [ ] 모니터링 시스템 병행 실행
- [ ] 주기적인 결과 확인
- [ ] 시스템 리소스 상태 체크
- [ ] 필요시 중간 결과 백업

---

**이 검증 및 모니터링 시스템으로 장시간 실행되는 하이퍼파라미터 실험을 안전하고 효율적으로 수행할 수 있습니다!** 🎯
