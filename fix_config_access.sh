#!/bin/bash

echo "🔧 config_v2.yaml 속성 접근 문제 해결!"
echo "======================================"

echo "📝 gemini_main_v2.py에서 속성 접근 방식 수정..."

python3 << 'EOF'
with open('codes/gemini_main_v2.py', 'r') as f:
    content = f.read()

# dynamic_augmentation 속성 접근 방식 수정
replacements = [
    # hasattr()를 사용한 안전한 속성 접근
    ("cfg.dynamic_augmentation", "getattr(cfg, 'dynamic_augmentation', None)"),
    ("cfg.mixup_cutmix", "getattr(cfg, 'mixup_cutmix', None)"),
    ("cfg.focal_loss", "getattr(cfg, 'focal_loss', None)"),
    ("cfg.label_smoothing", "getattr(cfg, 'label_smoothing', None)"),
    ("cfg.val_TTA", "getattr(cfg, 'val_TTA', cfg.TTA)"),
    ("cfg.test_TTA", "getattr(cfg, 'test_TTA', cfg.TTA)"),
]

for old, new in replacements:
    content = content.replace(old, new)
    print(f"✅ {old} -> {new}")

# getattr을 사용한 동적 augmentation 체크 로직 추가
dynamic_check = '''
        # Dynamic augmentation 설정 확인
        dynamic_aug = getattr(cfg, 'dynamic_augmentation', None)
        if dynamic_aug and getattr(dynamic_aug, 'enabled', False):
            print("🔄 Dynamic Augmentation 활성화됨")
        else:
            print("📷 일반 Augmentation 사용")
'''

# device 설정 후에 dynamic augmentation 체크 추가
if "print(f\"🔥 Using device: {device}\")" in content:
    content = content.replace(
        "print(f\"🔥 Using device: {device}\")",
        "print(f\"🔥 Using device: {device}\")" + dynamic_check
    )

# 파일 저장
with open('codes/gemini_main_v2.py', 'w') as f:
    f.write(content)

print("🎉 속성 접근 방식 수정 완료!")
EOF

echo ""
echo "🧪 수정된 코드 테스트..."
python codes/gemini_main_v2.py --config codes/config_v2.yaml --help 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Help 출력 성공 - 기본 구문 오류 없음"
else
    echo "❌ 여전히 문제가 있습니다"
fi

echo ""
echo "🚀 이제 실행해보세요:"
echo "./run_code_v2.sh"
