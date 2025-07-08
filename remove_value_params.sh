#!/bin/bash

echo "🔥 Albumentations value 파라미터 완전 박멸!"
echo "======================================"

echo "📝 gemini_augmentation_v2.py 라인별 수정..."

python3 << 'EOF'
with open('codes/gemini_augmentation_v2.py', 'r') as f:
    lines = f.readlines()

print("🔍 value 파라미터가 있는 라인들 찾아서 수정...")

modified_lines = []
for i, line in enumerate(lines):
    original_line = line
    
    # value=(255,255,255) 또는 value=(...) 패턴 제거
    if 'value=' in line and ('A.Affine' in line or 'A.CoarseDropout' in line or 'A.Perspective' in line):
        print(f"📍 라인 {i+1}: {line.strip()}")
        
        # value 파라미터와 그 값 완전 제거
        import re
        
        # value=(...) 패턴 제거
        line = re.sub(r',?\s*value=\([^)]*\)', '', line)
        
        # 남은 불필요한 쉼표 정리
        line = re.sub(r',\s*,', ',', line)
        line = re.sub(r',\s*\)', ')', line)
        line = re.sub(r'\(\s*,', '(', line)
        
        print(f"✅ 수정됨: {line.strip()}")
    
    modified_lines.append(line)

# 파일 저장
with open('codes/gemini_augmentation_v2.py', 'w') as f:
    f.writelines(modified_lines)

print("\n🎉 모든 value 파라미터 완전 제거 완료!")

# 확인
with open('codes/gemini_augmentation_v2.py', 'r') as f:
    content = f.read()
    
import re
value_matches = re.findall(r'.*value=.*', content)
if value_matches:
    print(f"❌ 아직 남은 value 파라미터: {len(value_matches)}개")
    for match in value_matches[:5]:  # 처음 5개만 표시
        print(f"  - {match.strip()}")
else:
    print("✅ 모든 value 파라미터 완전 제거됨!")
EOF

echo ""
echo "🧪 수정 확인..."
echo "📍 value 파라미터 잔존 여부:"
grep -n "value=" codes/gemini_augmentation_v2.py || echo "✅ value 파라미터 완전 제거됨!"

echo ""
echo "🚀 즉시 커밋 후 테스트:"
echo "git add codes/gemini_augmentation_v2.py"
echo "git commit -m 'fix: value 파라미터 완전 제거 (라인별 정밀 수정)'"
echo "git push origin main"

echo ""
echo "💡 Linux에서 git pull 후 ./run_code_v2.sh 실행하면"
echo "   더 이상 value 관련 경고가 없을 것입니다!"
