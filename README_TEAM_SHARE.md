# 🚀 CV Classification 프로젝트 팀 공유용

## 📋 설정 방법

### 1. 환경 설정
```bash
# .env 파일 생성
cp .env.template .env

# .env 파일에서 개인 정보 입력
# - WANDB_API_KEY: 본인의 WandB API 키
# - WANDB_PROJECT: 팀 프로젝트명 (선택)
```

### 2. 필수 패키지 설치
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 3. 시스템 실행
```bash
# v1 시스템 (ResNet 기반)
./run_code_v1.sh

# v2 시스템 (Swin Transformer 기반) 
./run_code_v2.sh
```

## 🔍 원본 정보
- **원본 서버**: AIStages 환경
- **백업 날짜**: 2025-07-08 18:43
- **정리 작업**: 개인정보 제거, 불필요 파일 정리 완료

## ⚠️ 주의사항
- `.env` 파일에 개인 API 키 입력 필수
- `data/` 폴더의 훈련 데이터는 별도 다운로드 필요
- 실험 결과는 각자의 WandB 계정에 기록됨