#!/bin/bash

echo "🔧 Albumentations 경고 완전 제거!"
echo "==============================="

echo "📝 gemini_augmentation_v2.py 완전 수정..."

python3 << 'EOF'
with open('codes/gemini_augmentation_v2.py', 'r') as f:
    content = f.read()

# Affine에서 value 파라미터 완전 제거 (지원 안됨)
import re

# Affine의 value 파라미터 제거
content = re.sub(
    r'A\.Affine\(([^)]*?)value=\([^)]*?\),?\s*([^)]*?)\)',
    r'A.Affine(\1\2)',
    content
)

# Perspective의 value 파라미터 제거
content = re.sub(
    r'A\.Perspective\(([^)]*?)value=\([^)]*?\),?\s*([^)]*?)\)',
    r'A.Perspective(\1\2)',
    content
)

# CoarseDropout의 value 파라미터 제거
content = re.sub(
    r'A\.CoarseDropout\(([^)]*?)value=\([^)]*?\),?\s*([^)]*?)\)',
    r'A.CoarseDropout(\1\2)',
    content
)

# 불필요한 쉼표 정리
content = re.sub(r',\s*,', ',', content)
content = re.sub(r',\s*\)', ')', content)

# 파일 저장
with open('codes/gemini_augmentation_v2.py', 'w') as f:
    f.write(content)

print("✅ Albumentations 경고 제거 완료!")
EOF

echo ""
echo "📝 Albumentations 업데이트 경고 비활성화..."

# run_code_v2.sh에 환경변수 추가
cat > run_code_v2.sh << 'EOF'
#!/bin/bash

# 🔧 코드 v2 실행 스크립트 (Linux 호환)
# 사용법: ./run_code_v2.sh

echo "🚀 Starting Code v2 System (새 시스템)"
echo "📂 Data: train.csv v1 (최고 성능 달성했던 원본 데이터)"
echo "💻 Code: gemini_main_v2.py (swin_base 기반)"
echo "⚙️ Config: config_v2.yaml"
echo "🆕 Features: 개선된 augmentation, dynamic augmentation, 향상된 모델"
echo ""

# 현재 디렉토리 확인
echo "📍 Current directory: $(pwd)"
echo "📍 Python path: $(which python3 || which python)"

# Albumentations 업데이트 체크 비활성화
export NO_ALBUMENTATIONS_UPDATE=1

# Python 경로 설정하여 실행 (Linux 호환)
export PYTHONPATH="$PWD:$PWD/codes:$PYTHONPATH"

# 실행 (config 파일명만 전달)
python3 codes/gemini_main_v2.py --config config_v2.yaml || python codes/gemini_main_v2.py --config config_v2.yaml

echo ""
echo "✅ Code v2 실행 완료!"
EOF

chmod +x run_code_v2.sh

echo ""
echo "🎉 모든 경고 제거 완료!"
echo ""
echo "📋 수정 내용:"
echo "✅ Affine, Perspective, CoarseDropout에서 value 파라미터 제거"
echo "✅ NO_ALBUMENTATIONS_UPDATE=1 환경변수 설정"
echo "✅ 깔끔한 실행 환경 구성"
echo ""
echo "🚀 즉시 커밋 후 Linux에서 테스트:"
echo "git add codes/gemini_augmentation_v2.py run_code_v2.sh"
echo "git commit -m 'fix: Albumentations 경고 완전 제거'"
echo "git push origin main"
