# 📋 Ubuntu 서버 환경 구축 완료 가이드

## 🎯 생성된 파일들

### 1. `requirements_ubuntu_final.txt`
- 실제 소스 코드 분석 기반으로 작성된 정확한 패키지 목록
- 모든 버전 호환성 검증 완료
- CUDA 12.1 환경 최적화

### 2. `ubuntu_setup_final.sh`
- 완전 자동화된 설치 스크립트
- 시스템 정보 자동 감지
- 단계별 설치 및 검증

## 🚀 Ubuntu 서버에서 실행 방법

### 즉시 실행 (권장)
```bash
# 1. 서버 접속 후 프로젝트 디렉토리로 이동
cd /data/ephemeral/home/upstageailab-cv-classification-cv_5

# 2. 최신 코드 동기화 (Mac에서 push 후)
git pull origin main

# 3. 가상환경 생성 (한 번만)
sudo apt install python3.11-venv python3.11-dev
python3.11 -m venv venv
source venv/bin/activate

# 4. 자동 설치 스크립트 실행
chmod +x ubuntu_setup_final.sh
./ubuntu_setup_final.sh
```

### 수동 설치 (문제 발생시)
```bash
# 가상환경 활성화 후
source venv/bin/activate

# 정확한 requirements로 설치
pip install -r requirements_ubuntu_final.txt
```

## ✅ 설치 검증
스크립트 실행 후 다음과 같은 출력이 나와야 합니다:
```
🎉 모든 핵심 패키지 임포트 성공!
✅ PyTorch: 2.4.1+cu121
✅ CUDA 사용 가능: True
✅ GPU 개수: 1
✅ GPU 이름: NVIDIA A100-SXM4-40GB
✅ timm: 0.9.16
✅ albumentations: 1.4.13
```

## 🎯 바로 실험 시작
```bash
# HPO + AIStages 통합 시스템
python aistages_manager.py
# → 메뉴 1번 선택 → quick (5개 실험, ~10분)

# 또는 단일 실험 테스트
python codes/gemini_main_v2.py --config codes/config.yaml
```

## 🔧 문제 해결

### timm 버전 문제
```bash
pip install --no-deps timm==0.9.16
```

### CUDA 문제
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### 메모리 부족
```bash
# config.yaml에서 batch_size 조정
# batch_size: 32 → 16 또는 8
```

## 📊 주요 특징

### 정밀 분석 기반
- ✅ 실제 소스 코드에서 사용하는 모든 패키지 추출
- ✅ 버전 호환성 철저 검증
- ✅ timm==1.0.12 → 0.9.16 호환 문제 해결

### 완전 자동화
- ✅ 시스템 정보 자동 감지
- ✅ GPU/CPU 환경 자동 최적화
- ✅ 설치 후 자동 검증

### 즉시 사용 가능
- ✅ 바로 실험 시작 가능
- ✅ HPO 시스템 완전 호환
- ✅ AIStages 제출 시스템 준비

이제 Ubuntu 서버에서 `./ubuntu_setup_final.sh` 만 실행하면 모든 환경이 완벽하게 구축됩니다! 🚀
