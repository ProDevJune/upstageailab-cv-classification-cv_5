#!/bin/bash
# 개선된 train.csv 파일 교체 스크립트

cd 

echo "📋 개선된 train.csv 파일 교체 작업"
echo "=" * 50

# 1. 기존 파일 확인
echo "🔍 Step 1: 기존 파일 확인"
if [ -f "data/train.csv" ]; then
    echo "✅ 기존 train.csv 존재"
    echo "   크기: $(wc -l < data/train.csv) lines"
    echo "   수정: $(stat -f "%Sm" data/train.csv)"
else
    echo "❌ 기존 train.csv 없음"
fi

# 2. 새 파일 확인  
echo ""
echo "🔍 Step 2: 새 파일 확인"
if [ -f "/Users/jayden/Downloads/train.csv" ]; then
    echo "✅ 새 train.csv 존재"
    echo "   크기: $(wc -l < /Users/jayden/Downloads/train.csv) lines"
    echo "   수정: $(stat -f "%Sm" /Users/jayden/Downloads/train.csv)"
else
    echo "❌ 새 train.csv 없음"
    exit 1
fi

# 3. 백업 생성
echo ""
echo "💾 Step 3: 기존 파일 백업"
BACKUP_FILE="data/train_backup_$(date +%Y%m%d_%H%M%S).csv"
cp data/train.csv "$BACKUP_FILE"
echo "✅ 백업 완료: $BACKUP_FILE"

# 4. 새 파일로 교체
echo ""
echo "🔄 Step 4: 새 파일로 교체"
cp /Users/jayden/Downloads/train.csv data/train.csv
echo "✅ 파일 교체 완료"

# 5. 검증
echo ""
echo "🔍 Step 5: 교체 결과 검증"
echo "새 파일 정보:"
echo "   경로: data/train.csv"
echo "   크기: $(wc -l < data/train.csv) lines"
echo "   처음 5줄:"
head -5 data/train.csv

echo ""
echo "✅ train.csv 교체 완료!"
echo "📁 백업 파일: $BACKUP_FILE"
echo "📈 이제 개선된 데이터로 학습할 수 있습니다."

echo ""
echo "🔄 다음 작업 권장:"
echo "1. 새 데이터로 실험 재실행"
echo "2. 성능 비교 분석"
echo "3. 필요시 앙상블 재구성"
