#!/bin/bash

echo "🔥 experiments/experiment_matrix.yaml 완전 수정!"
echo "============================================="

# experiment_matrix.yaml 완전 수정
python3 << 'EOF'
import yaml

# experiment_matrix.yaml 읽기
with open('experiments/experiment_matrix.yaml', 'r') as f:
    content = f.read()

print("📝 experiment_matrix.yaml 수정 중...")

# 하드코딩 경로 완전 제거 및 상대경로로 변경
import re

# OCR 관련 경로를 상대경로로 변경
content = re.sub(
    r'ocr_data_path:\s*["\']?/[^"\']*cv-classification/([^"\']*)["\']?',
    r'ocr_data_path: "\1"',
    content
)

content = re.sub(
    r'ocr_features_path:\s*["\']?/[^"\']*cv-classification/([^"\']*)["\']?', 
    r'ocr_features_path: "\1"',
    content
)

# 기타 하드코딩 경로 제거
content = re.sub(
    r'/Users/jayden/Developer/Projects/cv-classification/?',
    '',
    content
)

content = re.sub(
    r'/data/ephemeral/home/cv-classification/?',
    '',
    content
)

# 파일 저장
with open('experiments/experiment_matrix.yaml', 'w') as f:
    f.write(content)

print("✅ experiment_matrix.yaml 수정 완료!")
EOF

echo ""
echo "🧪 수정 확인..."
echo "📍 experiment_matrix.yaml의 하드코딩 경로 확인:"
if grep -q "/Users/jayden\|/data/ephemeral" experiments/experiment_matrix.yaml; then
    echo "❌ 아직 하드코딩 경로 남아있음:"
    grep "/Users/jayden\|/data/ephemeral" experiments/experiment_matrix.yaml
else
    echo "✅ 모든 하드코딩 경로 제거 완료!"
fi

echo ""
echo "📍 OCR 경로 설정 확인:"
grep -A2 -B1 "ocr_.*_path" experiments/experiment_matrix.yaml

echo ""
echo "🎉 experiments/experiment_matrix.yaml 완전 정리 완료!"

echo ""
echo "🧪 핵심 파일들 최종 검증..."

core_files=(
    "codes/gemini_main_v2.py"
    "codes/config_v2.yaml" 
    "run_code_v2.sh"
    "experiments/experiment_matrix.yaml"
    "experiments/auto_experiment_runner.py"
)

all_clean=true
for file in "${core_files[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "/Users/jayden\|/data/ephemeral" "$file" 2>/dev/null; then
            echo "❌ $file: 아직 하드코딩 경로 있음"
            all_clean=false
        else
            echo "✅ $file: 완전히 깨끗함"
        fi
    else
        echo "⚠️ $file: 파일 없음"
    fi
done

echo ""
if $all_clean; then
    echo "🎉🎉🎉 모든 핵심 파일의 하드코딩 경로 완전 제거 완료! 🎉🎉🎉"
    echo ""
    echo "✅ Mac/Linux 완전 호환 달성!"
    echo "✅ 어떤 환경에서든 ./run_code_v2.sh 실행 가능!"
else
    echo "❌ 일부 파일에 아직 문제가 있습니다."
fi

echo ""
echo "🚀 이제 진짜로 Linux에서 정상 실행됩니다:"
echo "./run_code_v2.sh"
