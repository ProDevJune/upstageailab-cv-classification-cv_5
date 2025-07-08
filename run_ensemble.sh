#!/bin/bash
# 앙상블 실행 스크립트

cd 

echo "🎪 황금조합 3개 모델 앙상블 시작"
echo "=" * 50

# 1. 서버 점수 업데이트
echo "🔄 Step 1: 서버 점수 업데이트"
venv/bin/python update_server_scores.py

echo ""
echo "🎯 Step 2: 앙상블 생성"
venv/bin/python ensemble_3models.py

echo ""
echo "✅ 앙상블 완료!"
echo "📁 생성된 파일을 AIStages에 제출하세요."
