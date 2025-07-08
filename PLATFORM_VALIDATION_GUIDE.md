# 🚀 Mac OS / Ubuntu 환경별 자동 실험 시스템 완전 가이드

## 🎯 시스템 개요

이 시스템은 **Mac OS (MPS)** 와 **Ubuntu (CUDA)** 환경을 자동으로 감지하여 최적화된 설정으로 실험을 실행합니다.

### 🖥️ 지원 환경
- **🍎 Mac OS (Apple Silicon)**: MPS 가속 활용
- **🐧 Ubuntu + NVIDIA GPU**: CUDA 가속 활용  
- **💻 CPU 전용**: 모든 환경에서 Fallback

## 🔧 사전 검증 시스템 특징

### ✅ 검증 항목
1. **패키지 설치 상태**: 모든 필수 패키지 버전 확인
2. **디바이스 호환성**: MPS/CUDA/CPU 동작 확인
3. **모델 로드 테스트**: 핵심 모델들 정상 동작 확인
4. **실험 조합 검증**: 12개 대표 조합 실제 실행 테스트
5. **메모리 요구사항**: 플랫폼별 메모리 사용량 분석
6. **실행 시간 추정**: 전체 실험 소요 시간 예측

### 🛡️ 오류 방지 기능
- **환경별 최적화**: 플랫폼에 맞는 requirements 자동 선택
- **메모리 부족 예방**: 사전 메모리 요구사항 확인
- **호환성 검증**: 실제 mini-training으로 동작 확인
- **의존성 검증**: 모든 패키지 import 및 버전 확인

## 🚀 완전 자동 설치 및 검증

### 1단계: 원클릭 설치 및 검증
```bash
# 모든 권한 설정
chmod +x set_all_permissions.sh
./set_all_permissions.sh

# 전체 설치 및 검증 (원클릭)
./setup_and_validate_all.sh
```

이 명령어 하나로 다음 작업이 자동으로 수행됩니다:
1. 플랫폼 자동 감지 (Mac MPS / Ubuntu CUDA / CPU)
2. 환경별 최적 requirements 설치
3. 가상환경 생성 및 패키지 설치
4. 12개 핵심 실험 조합 실제 테스트
5. 메모리 및 성능 분석
6. 종합 검증 리포트 생성

### 2단계: 검증 결과 확인
```bash
# 검증 성공시 출력 예시:
# 🎉 모든 검증 완료!
# ✅ 환경 설정: 완료
# ✅ 패키지 설치: 완료  
# ✅ 디바이스 호환성: 완료
# ✅ 모델 검증: 완료
# ✅ 실험 조합 테스트: 완료
```

## 🧪 수동 단계별 검증 (선택사항)

### 환경별 수동 설치
```bash
# Mac OS (Apple Silicon)
pip install -r requirements_macos.txt

# Ubuntu + NVIDIA GPU
pip install -r requirements_ubuntu.txt

# CPU 전용
pip install -r requirements_cpu.txt
```

### 단계별 검증
```bash
# 1. 빠른 환경 체크
python pre_experiment_validator.py --quick-test

# 2. 전체 종합 검증
python pre_experiment_validator.py --save-report

# 3. 플랫폼 정보 확인
python codes/platform_detector.py
```

## 📊 검증 결과 해석

### ✅ 검증 성공 (ready)
```
🎉 검증 완료! 모든 실험을 안전하게 실행할 수 있습니다.
📦 패키지: ✅
🖥️ 디바이스: ✅
🤖 모델: ✅
🧪 실험 조합: 12/12 (100%)
💾 메모리: ✅ 충분
```
**→ 바로 실험 시작 가능**

### ⚠️ 주의사항 있음 (ready_with_warnings)
```
⚠️ 검증 완료 (주의사항 있음). 대부분의 실험은 정상 실행됩니다.
🧪 실험 조합: 10/12 (83%)
💾 메모리: ⚠️ 주의
```
**→ 배치 크기 조정 후 실행 권장**

### ❌ 검증 실패 (not_ready)
```
❌ 검증 실패. 환경 설정 또는 시스템 점검이 필요합니다.
📦 패키지: ❌
🖥️ 디바이스: ❌
```
**→ 환경 재설정 필요**

## 🔧 문제 해결 가이드

### 패키지 설치 실패
```bash
# 가상환경 재생성
rm -rf venv
bash setup_platform_env.sh

# 수동 패키지 설치
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_[macos|ubuntu|cpu].txt
```

### CUDA 관련 문제 (Ubuntu)
```bash
# CUDA 상태 확인
nvidia-smi
nvcc --version

# PyTorch CUDA 호환성 확인
python -c "import torch; print(torch.cuda.is_available())"

# CUDA 재설치 (필요시)
sudo apt update
sudo apt install nvidia-driver-535
sudo reboot
```

### MPS 관련 문제 (Mac OS)
```bash
# MPS 상태 확인
python -c "import torch; print(torch.backends.mps.is_available())"

# 메모리 압박 상태 확인
# Activity Monitor > Memory 탭에서 Memory Pressure 확인

# 배치 크기 감소
# experiment_matrix.yaml에서 batch_size 값들을 50% 감소
```

### 메모리 부족 문제
```bash
# 1. 배치 크기 조정
# experiment_matrix.yaml 수정:
# efficientnet_b4: batch_size: 32 → 16
# swin_transformer: batch_size: 24 → 12

# 2. 이미지 크기 감소
# image_size: 384 → 224

# 3. Mixed Precision 활성화 (CUDA만)
mixed_precision: True
```

## 🎯 실험 실행 시나리오

### 시나리오 1: 완전 자동 실행
```bash
# 검증 성공 후
python experiments/experiment_generator.py --ocr-mode selective
python experiments/auto_experiment_runner.py &
python experiments/experiment_monitor.py
```

### 시나리오 2: 단계적 실행
```bash
# 1. 소규모 테스트
python experiments/experiment_generator.py --ocr-mode none
python experiments/auto_experiment_runner.py --dry-run

# 2. 실제 실행
python experiments/auto_experiment_runner.py

# 3. 결과 확인
python experiments/submission_manager.py list-pending
```

### 시나리오 3: 메모리 제한 환경
```bash
# 배치 크기 50% 감소된 실험
# experiment_matrix.yaml 수정 후
python experiments/experiment_generator.py --ocr-mode selective
python experiments/auto_experiment_runner.py
```

## 📈 성능 최적화 팁

### 🍎 Apple Silicon (MPS) 최적화
```yaml
# 최적 설정
batch_size: 16-24  # 통합 메모리 고려
num_workers: 4  # CPU 코어의 절반
pin_memory: false  # MPS에서 불필요
mixed_precision: false  # MPS 제한적 지원
```

### 🐧 Ubuntu (CUDA) 최적화
```yaml
# 최적 설정
batch_size: 32-48  # GPU 메모리에 따라
num_workers: 8  # 충분한 CPU 코어 활용
pin_memory: true  # CUDA 성능 향상
mixed_precision: true  # 메모리 효율성
```

### 💻 CPU 전용 최적화
```yaml
# 최적 설정
batch_size: 8-16  # 시스템 메모리 고려
num_workers: CPU_COUNT  # 모든 코어 활용
mixed_precision: false  # CPU에서 불필요
```

## 📊 예상 실행 시간

### Mac OS (Apple Silicon)
| 모드 | 실험 수 | 예상 시간 | 권장도 |
|------|---------|-----------|--------|
| None | 24개 | 40-50시간 | ⭐⭐⭐ |
| Selective | 32개 | 55-65시간 | ⭐⭐⭐⭐⭐ |
| All | 48개 | 80-95시간 | ⭐⭐ |

### Ubuntu (CUDA)
| 모드 | 실험 수 | 예상 시간 | 권장도 |
|------|---------|-----------|--------|
| None | 24개 | 30-40시간 | ⭐⭐⭐ |
| Selective | 32개 | 45-55시간 | ⭐⭐⭐⭐⭐ |
| All | 48개 | 65-80시간 | ⭐⭐⭐⭐ |

## 🔍 모니터링 및 디버깅

### 실시간 모니터링
```bash
# 시스템 리소스
htop  # CPU/메모리 사용률

# GPU 모니터링 (CUDA)
watch -n 1 nvidia-smi

# 실험 진행 상황
python experiments/experiment_monitor.py

# 로그 확인
tail -f experiments/logs/exp_*.json
```

### 로그 파일 위치
- **검증 결과**: `pre_experiment_validation_*.json`
- **플랫폼 정보**: `platform_info.json`
- **실험 로그**: `experiments/logs/*.json`
- **실험 큐**: `experiments/experiment_queue.json`

## 🚨 긴급 상황 대응

### 실험 중단 방법
```bash
# 안전한 중단
Ctrl+C  # 현재 실험 완료 후 중단

# 강제 중단
pkill -f "python experiments/auto_experiment_runner.py"

# 재개
python experiments/auto_experiment_runner.py --resume
```

### 메모리 부족 대응
```bash
# 즉시 메모리 정리
python -c "import torch; torch.cuda.empty_cache() if torch.cuda.is_available() else None"

# 시스템 재부팅
sudo reboot

# 배치 크기 감소 후 재시작
# experiment_matrix.yaml 수정 → 재생성
```

## 📞 지원 및 문의

### 자가 진단 명령어
```bash
# 종합 상태 확인
python pre_experiment_validator.py --quick-test

# 플랫폼 정보
python codes/platform_detector.py

# 실험 현황
python experiments/experiment_monitor.py --once
```

### 로그 수집 (문의시 첨부)
```bash
# 검증 리포트
cat pre_experiment_validation_*.json

# 플랫폼 정보
cat platform_info.json

# 최근 실험 로그
ls -la experiments/logs/
```

---

**🎉 이제 Mac OS와 Ubuntu 환경에서 안전하고 최적화된 자동 실험을 즐기세요!**
