# 🚀 크로스 플랫폼 HPO 자동화 시스템

Mac MPS와 Ubuntu CUDA를 자동으로 감지하여 최적화된 하이퍼파라미터 최적화(HPO)를 수행하는 시스템입니다.

## 📋 주요 특징

### 🖥️ 크로스 플랫폼 지원
- **macOS + Apple Silicon MPS**: 통합 메모리 최적화
- **Linux + NVIDIA CUDA**: 고성능 GPU 최적화  
- **CPU 전용**: 메모리 효율적 최적화
- **자동 감지**: 플랫폼과 디바이스를 자동으로 감지하여 최적 설정 적용

### 🤖 지능형 HPO
- **3단계 HPO**: Basic (Grid/Random) → Advanced (Optuna) → Expert (Ray Tune)
- **스마트 탐색**: 중요한 하이퍼파라미터 우선 탐색
- **플랫폼별 제한**: 각 환경에 맞는 실험 공간 자동 조정
- **효율적 실험**: 빠른 스크리닝 → 집중 최적화 → 최종 미세조정

### 📊 체계적 분석
- **실시간 추적**: 모든 실험 자동 기록 및 상태 관리
- **시각화**: 성능 분포, 하이퍼파라미터 영향도 분석
- **자동 추천**: 최적 설정 및 효율적 조합 추천
- **리포트 생성**: JSON 형태의 상세 분석 리포트

## 🏗️ 시스템 구조

```
cv-classification/
├── 🔒 기존 Gemini 시스템 (보존)
│   ├── gemini_main.py
│   ├── gemini_utils.py
│   └── config.yaml
│
├── 🆕 새로운 GPT 시스템  
│   ├── gpt_main.py
│   ├── gpt_utils.py
│   └── config_gpt.yaml
│
├── 🤖 자동화 HPO 시스템
│   ├── platform_detector.py       # 플랫폼 자동 감지
│   ├── enhanced_config_manager.py # 플랫폼별 설정 관리
│   ├── auto_experiment_basic.py   # 기본 HPO 엔진
│   ├── experiment_tracker.py      # 결과 분석 도구
│   └── practice/                  # 자동 생성 설정들
│
├── 📊 결과 및 분석
│   ├── experiment_results.csv     # 실험 결과 DB
│   ├── analysis_results/          # 시각화 결과
│   └── run_experiments.sh         # 통합 실행 스크립트
```

## 🚀 빠른 시작

### 1. 설치 및 설정
```bash
# 시스템 설치
chmod +x setup_hpo_system.sh
./setup_hpo_system.sh

# 플랫폼 감지 테스트
python test_platform_detection.py
```

### 2. HPO 실행
```bash
# 🎮 대화형 모드 (추천)
./run_experiments.sh

# ⚡ 빠른 실험 (20개, 30분/실험)
./run_experiments.sh quick 20

# 🔬 전체 실험 (50개, 1시간/실험)
./run_experiments.sh full 50

# 📊 시스템 정보 확인
./run_experiments.sh info
```

### 3. 결과 분석
```bash
# 실험 요약
python codes/experiment_tracker.py --action summary

# 상위 10개 실험
python codes/experiment_tracker.py --action top --n 10

# 시각화 생성
python codes/experiment_tracker.py --action visualize

# 설정 추천
python codes/experiment_tracker.py --action recommend
```

## 🖥️ 플랫폼별 최적화

### 🍎 macOS + Apple Silicon MPS
```yaml
# 자동 적용되는 최적화
mixed_precision: false      # MPS FP16 제한 고려
pin_memory: false          # 통합 메모리 환경
batch_size_multiplier: 0.8 # 메모리 효율성 우선
memory_efficient: true     # 보수적 메모리 사용
max_parallel_trials: 1     # 단일 실험 권장
```

### 🐧 Linux + NVIDIA CUDA
```yaml
# 자동 적용되는 최적화  
mixed_precision: true       # FP16으로 메모리 절약
compile_model: true        # torch.compile 사용
batch_size_multiplier: 1.5 # 큰 배치 크기 활용
max_parallel_trials: 4     # 다중 실험 병렬 실행
```

### 💻 CPU 전용
```yaml
# 자동 적용되는 최적화
batch_size_multiplier: 0.5 # 작은 배치로 안정성
use_channels_last: true    # CPU 최적화
memory_strategy: minimal   # 최소 메모리 사용
max_experiments: 10        # 제한된 실험 수
```

## 📊 HPO 전략

### Phase 1: 빠른 스크리닝 (1-2일)
- **목적**: 유망한 모델/설정 조합 식별
- **설정**: 20개 조합, 50 epochs, 30분/실험
- **방법**: Smart Grid Search

### Phase 2: 집중 실험 (3-5일)  
- **목적**: 상위 설정들로 심화 학습
- **설정**: 50개 조합, 200 epochs, 1시간/실험
- **방법**: Optuna 베이지안 최적화

### Phase 3: 최종 최적화 (1-2일)
- **목적**: 최고 성능 달성
- **설정**: 상위 5개 모델 앙상블
- **방법**: 수동 미세조정

## 🎯 사용 예시

### 시나리오 1: 개발 단계 (MacBook Pro M3)
```bash
./run_experiments.sh quick 10
# → MPS 최적화, 10개 실험, 5시간 소요
# → 유망한 모델 발견 후 다음 단계 진행
```

### 시나리오 2: 본격 최적화 (Linux + RTX 4090)
```bash
./run_experiments.sh full 100  
# → CUDA 최적화, 4개 병렬 실험
# → 베이지안 최적화로 효율적 탐색
```

### 시나리오 3: 결과 분석 및 추천
```bash
# 상위 실험 조회
python codes/experiment_tracker.py --action top --n 5

# 시각화 생성
python codes/experiment_tracker.py --action visualize

# 최적 설정 추천
python codes/experiment_tracker.py --action recommend
```

## 📈 성능 비교 (예상)

| 플랫폼 | 디바이스 | 실험 시간 | 병렬 수 | 권장 HPO |
|--------|----------|----------|---------|----------|
| **MacBook Pro M3** | MPS | 30분 | 1개 | Basic/Optuna |
| **Linux + RTX 4090** | CUDA | 15분 | 4개 | Ray Tune |
| **Linux + RTX 3080** | CUDA | 25분 | 2개 | Optuna |
| **CPU (16코어)** | CPU | 2시간 | 1개 | Basic |

## 🔧 고급 사용법

### 커스텀 실험 설정
```python
# codes/practice/my_experiment.yaml 편집
python codes/auto_experiment_basic.py --config codes/practice/my_experiment.yaml
```

### 플랫폼별 설정 생성
```bash
python -c "
from codes.platform_detector import PlatformDetector
from codes.enhanced_config_manager import EnhancedConfigManager

detector = PlatformDetector()
config_manager = EnhancedConfigManager(detector)
config = config_manager.generate_platform_config('full')
config_manager.save_platform_config(config, 'my_optimized_config.yaml')
"
```

### 실험 데이터 정리
```bash
python codes/experiment_tracker.py --action cleanup --days 7
```

## 🤝 기존 시스템과의 호환성

- **완전 보존**: 기존 `gemini_*.py` 파일들은 수정되지 않음
- **병렬 운영**: 기존 워크플로우와 새 시스템 동시 사용 가능
- **언제든 복귀**: 기존 시스템으로 즉시 복귀 가능
- **점진적 도입**: 팀원별로 선택적 사용 가능

## 🆘 문제 해결

### 일반적인 문제들

1. **PyTorch 설치 오류**
   ```bash
   # macOS Apple Silicon
   pip install torch torchvision torchaudio
   
   # Linux CUDA
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

2. **메모리 부족 오류**
   - 배치 크기가 자동으로 조정되지만, 수동으로 더 줄일 수 있습니다
   - `codes/practice/config_*.yaml`에서 `batch_size` 값을 줄여보세요

3. **실험 실패**
   ```bash
   # 실험 상태 확인
   python codes/experiment_tracker.py --action summary
   
   # 실패한 실험 재시작
   ./run_experiments.sh quick 5
   ```

### 디버깅
```bash
# 플랫폼 감지 확인
python test_platform_detection.py

# 상세 로그 확인
tail -f logs/training.log

# 시스템 리소스 확인 (macOS)
activity monitor

# 시스템 리소스 확인 (Linux)  
nvidia-smi  # GPU
htop        # CPU/Memory
```

## 📞 지원

- **문서**: `docs/auto-experiment-guide.md` 참조
- **이슈**: 실험 실패시 `experiment_results.csv`의 `error_message` 컬럼 확인
- **로그**: `logs/` 디렉토리의 로그 파일들 확인
- **시스템 정보**: `./run_experiments.sh info` 실행

---

**🎯 이 시스템을 통해 어떤 환경에서든 최적화된 CV 분류 모델을 효율적으로 개발할 수 있습니다!**
