#!/bin/bash
# ConvNeXt-Base 에러 수정 및 재실행

cd 

echo "🔧 ConvNeXt 에러 수정 중..."

# 1. 기존 증강 이미지 정리 (만약 있다면)
echo "📁 증강 이미지 파일 정리 중..."
find data/train -name "aug_*" -type f -delete 2>/dev/null || echo "증강 파일 없음"

# 2. 이전 실험 결과 정리
echo "🗑️ 이전 ConvNeXt 실험 결과 정리..."
rm -rf data/submissions/*convnext* 2>/dev/null || echo "이전 ConvNeXt 결과 없음"
rm -rf models/*convnext* 2>/dev/null || echo "이전 ConvNeXt 모델 없음"

# 3. WandB 캐시 정리 (선택사항)
echo "🧹 WandB 캐시 정리..."
find wandb -name "*convnext*" -type d -exec rm -rf {} + 2>/dev/null || echo "WandB ConvNeXt 캐시 없음"

# 4. 메모리 상태 확인
echo "💾 메모리 상태 확인..."
echo "사용 가능한 메모리: $(vm_stat | grep free | awk '{print $3}' | sed 's/\.//')"

# 5. ConvNeXt 재실행
echo "🎯 ConvNeXt-Base 재실행 시작..."
echo "⚙️ Device: mps"
echo "⌚ 실험 시간: $(date +%y%m%d%H%M)"

# 절대 경로로 재실행
venv/bin/python codes/gemini_main.py --config codes/practice/exp_golden_convnext_base_202507051902.yaml

echo "✅ ConvNeXt 재실행 완료!"
