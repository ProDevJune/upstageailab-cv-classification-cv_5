#!/bin/bash

# 🔥 Phase 1: cv-classification v3 시스템 실행 스크립트
# Focal Loss, Label Smoothing, CutMix/MixUp 고급 기법 통합

echo "🔥 Phase 1: cv-classification v3 시스템 시작"
echo "🏆 고급 기법: Focal Loss + Label Smoothing + CutMix/MixUp"
echo "⚙️ 시작 시간: $(date)"

# 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

# 현재 경로 확인
echo "📂 현재 작업 디렉토리: $(pwd)"

# Python 환경 확인
echo "🐍 Python 버전: $(python --version)"
echo "🔧 PyTorch 버전: $(python -c "import torch; print(torch.__version__)")"

# 디바이스 정보 확인
echo "💻 사용 가능한 디바이스:"
python -c "
import torch
print(f'  - CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  - CUDA 디바이스 수: {torch.cuda.device_count()}')
    print(f'  - 현재 CUDA 디바이스: {torch.cuda.current_device()}')
print(f'  - MPS: {torch.backends.mps.is_available()}')
"

# v3 설정 파일 확인
if [ ! -f "config_v3.yaml" ]; then
    echo "❌ config_v3.yaml 파일이 없습니다!"
    echo "   다음 파일이 필요합니다:"
    echo "   - config_v3.yaml (Phase 1 고급 설정)"
    exit 1
fi

echo "✅ 설정 파일 확인 완료: config_v3.yaml"

# v3 시스템 파일들 확인
echo "🔍 v3 시스템 파일 확인:"
required_files=(
    "gemini_main_v3.py"
    "gemini_utils_v3.py" 
    "gemini_train_v3.py"
    "gemini_augmentation_v3.py"
    "gemini_evalute_v3.py"
    "config_v3.yaml"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (누락)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ 필수 파일이 누락되었습니다:"
    printf '   - %s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ 모든 v3 시스템 파일 확인 완료"

# 메모리 사용량 체크
echo "📊 시스템 메모리 상태:"
if command -v free >/dev/null 2>&1; then
    free -h
elif command -v vm_stat >/dev/null 2>&1; then
    vm_stat | head -5
fi

# 🔥 Phase 1: v3 시스템 실행
echo ""
echo "🚀 Phase 1 고급 기법 통합 훈련 시작..."
echo "🔥 적용 기법: Focal Loss + Label Smoothing + CutMix/MixUp"
echo ""

# 시작 시간 기록
start_time=$(date +%s)

# v3 시스템 실행 (config_v3.yaml 사용)
python gemini_main_v3.py --config config_v3.yaml

# 실행 결과 확인
exit_code=$?
end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "⏱️ 실행 시간: ${duration}초 ($((duration/60))분 $((duration%60))초)"

if [ $exit_code -eq 0 ]; then
    echo "🎉 Phase 1 훈련 성공적으로 완료!"
    echo "🏆 고급 기법 통합 완료: Focal Loss + Label Smoothing + CutMix/MixUp"
    echo "📊 결과는 data/submissions/ 디렉토리에서 확인하세요"
    
    # 최신 submission 디렉토리 찾기
    latest_dir=$(ls -td /Users/jayden/Developer/Projects/cv-classification/data/submissions/*v3* 2>/dev/null | head -1)
    if [ -n "$latest_dir" ]; then
        echo "📁 최신 결과 디렉토리: $latest_dir"
        echo "📄 포함 파일들:"
        ls -la "$latest_dir" 2>/dev/null | head -10
    fi
else
    echo "❌ 훈련 실패 (종료 코드: $exit_code)"
    echo "🔍 로그를 확인하여 문제를 진단하세요"
fi

echo "🏁 Phase 1 실행 완료 ($(date))"
exit $exit_code
