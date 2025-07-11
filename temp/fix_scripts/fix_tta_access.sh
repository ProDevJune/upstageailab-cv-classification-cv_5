#!/bin/bash

echo "🔧 TTA 속성 접근 문제 해결!"
echo "==========================="

python3 << 'EOF'
with open('codes/gemini_main_v2.py', 'r') as f:
    content = f.read()

# TTA 관련 모든 접근을 안전하게 수정
replacements = [
    # cfg.TTA -> getattr로 안전 접근
    ("getattr(cfg, 'val_TTA', cfg.TTA)", "getattr(cfg, 'val_TTA', getattr(cfg, 'TTA', True))"),
    ("getattr(cfg, 'test_TTA', cfg.TTA)", "getattr(cfg, 'test_TTA', getattr(cfg, 'TTA', True))"),
    ("cfg.TTA", "getattr(cfg, 'TTA', True)"),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ {old} -> {new}")

# 추가로 다른 TTA 참조들도 안전하게 처리
import re

# TTA 변수 할당 부분 찾아서 수정
tta_patterns = [
    (r'(\w+)\s*=\s*cfg\.TTA', r'\1 = getattr(cfg, "TTA", True)'),
    (r'if\s+cfg\.TTA', r'if getattr(cfg, "TTA", True)'),
]

for pattern, replacement in tta_patterns:
    content = re.sub(pattern, replacement, content)

# 파일 저장
with open('codes/gemini_main_v2.py', 'w') as f:
    f.write(content)

print("🎉 TTA 속성 접근 문제 해결 완료!")
EOF

echo ""
echo "🚀 이제 TTA 오류 없이 실행됩니다:"
echo "./run_code_v2.sh"
