# 🚀 AIStages 서버 설치 및 실행 가이드

## 📦 1. 빠른 설치 (권장)

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. AIStages 전용 설치 스크립트 실행
chmod +x install_aistages.sh
./install_aistages.sh
```

## 🎯 2. 실행 방법

### v2 시스템 실행 (최신, 권장)
```bash
# 스크립트 실행
chmod +x run_aistages_v2.sh
./run_aistages_v2.sh

# 또는 직접 실행
python3 codes/gemini_main_v2.py --config codes/config_v2.yaml
```

### v1 시스템 실행 (검증된 성능)
```bash
python3 codes/gemini_main.py --config codes/config.yaml
```

## 🔧 3. 수동 설치 (문제 발생시)

```bash
# 1. 가상환경 활성화
source venv/bin/activate

# 2. pip 업그레이드
pip install --upgrade pip setuptools wheel

# 3. PyTorch 설치 (CUDA 12.1)
pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

# 4. 핵심 패키지 설치
pip install timm==1.0.12 transformers==4.44.2
pip install opencv-python==4.10.0.84 albumentations==1.4.18
pip install pandas==2.2.3 numpy==1.26.4 scikit-learn==1.5.2
pip install matplotlib==3.9.2 pyyaml==6.0.2 tqdm==4.66.5
pip install wandb==0.18.3 optuna==4.0.0
```

## 📋 4. 설치 확인

```bash
# 종합 확인
python3 test_v2_imports.py

# 간단 확인
python3 -c "
import torch, timm, transformers
print(f'PyTorch: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
print(f'TIMM: {timm.__version__}')
print('✅ 모든 패키지 정상')
"
```

## 🎯 5. 실행 후 모니터링

```bash
# 실시간 결과 확인 (별도 터미널)
tail -f experiment_results.csv

# GPU 사용률 모니터링
watch -n 1 nvidia-smi

# 제출 파일 확인
ls -la data/submissions/
```

## ⚡ 6. 빠른 시작 (3단계)

```bash
# 1단계: 환경 준비
source venv/bin/activate
chmod +x install_aistages.sh run_aistages_v2.sh

# 2단계: 설치
./install_aistages.sh

# 3단계: 실행
./run_aistages_v2.sh
```

## 🔧 7. 문제 해결

### Python 명령어 문제
```bash
# python 대신 python3 사용
which python3
python3 --version
```

### 패키지 설치 실패
```bash
# 개별 설치
pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cu121
pip install timm transformers
```

### GPU 인식 문제
```bash
# CUDA 확인
nvidia-smi
python3 -c "import torch; print(torch.cuda.is_available())"
```

### 메모리 부족
```bash
# config_v2.yaml에서 batch_size 조정
# batch_size: 32 → 16 또는 8
```

## 📊 8. 예상 성능

- **AIStages 서버**: NVIDIA RTX 3090 (24GB VRAM)
- **v2 시스템**: Swin Transformer + 고급 기법
- **예상 학습 시간**: 60-90분 (384px 해상도)
- **예상 성능**: 0.87-0.90+ (현재 최고 0.8619 대비 향상)

## 💡 9. 팁

- **배치 크기**: GPU 메모리에 맞게 16-32 사용
- **모니터링**: `nvidia-smi`로 GPU 사용률 확인
- **결과 저장**: 제출 파일이 `data/submissions/`에 자동 저장
- **백업**: 중요한 결과는 별도 저장 권장

---

**🎯 이제 AIStages 서버에서 최신 v2 시스템을 정상적으로 실행할 수 있습니다!**
