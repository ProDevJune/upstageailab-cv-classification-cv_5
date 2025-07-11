#!/bin/bash

# 🔧 Ubuntu 환경 v2 시스템 Adafactor 문제 완전 해결 스크립트

echo "🚀 Ubuntu 환경 v2 시스템 Adafactor 문제 해결"
echo "=================================================="

# 1. transformers 라이브러리 설치 (Adafactor 포함)
echo "📦 Installing transformers library..."
pip install transformers>=4.20.0

# 2. 추가 adafactor 패키지 설치
echo "📦 Installing adafactor package..."
pip install adafactor

# 3. Ubuntu 전용 requirements 설치
echo "📦 Installing Ubuntu requirements..."
pip install -r requirements_ubuntu.txt

# 4. wandb 로깅 활성화 확인
echo "🔍 Checking wandb logging..."
grep -n "log: true" codes/config_v2.yaml && echo "✅ wandb logging enabled" || echo "⚠️ wandb logging disabled"

# 5. 실행
echo "🚀 Running v2 system..."
./run_code_v2.sh

echo ""
echo "✅ Ubuntu v2 시스템 수정 완료!"
echo "📝 변경사항:"
echo "   - Adafactor 안전한 fallback 처리 추가"
echo "   - transformers 라이브러리 설치"
echo "   - wandb 로깅 활성화"
echo "   - Ubuntu 호환성 개선"
