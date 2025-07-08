#!/bin/bash

echo "🔥 수동으로 정확한 라인 수정!"
echo "========================="

echo "📝 문제 라인들 직접 수정..."

python3 << 'EOF'
# gemini_augmentation_v2.py 파일 읽기
with open('codes/gemini_augmentation_v2.py', 'r') as f:
    lines = f.readlines()

# 문제가 되는 라인 번호들 (130, 152, 170, 205, 240, 256, 266)
problem_lines = [130, 152, 170, 205, 240, 256, 266]

print("🔍 문제 라인들 확인 및 수정:")

for line_num in problem_lines:
    if line_num <= len(lines):
        original = lines[line_num-1].strip()
        print(f"\n라인 {line_num}:")
        print(f"  원본: {original}")
        
        # value 파라미터 제거
        import re
        
        # value=(...) 제거
        modified = re.sub(r'value=\([^)]*\),?\s*', '', original)
        
        # 연속 쉼표 정리
        modified = re.sub(r',\s*,', ',', modified)
        modified = re.sub(r',\s*\)', ')', modified)
        modified = re.sub(r'\(\s*,', '(', modified)
        
        print(f"  수정: {modified}")
        
        lines[line_num-1] = modified + '\n'

# 파일 저장
with open('codes/gemini_augmentation_v2.py', 'w') as f:
    f.writelines(lines)

print("\n✅ 문제 라인들 직접 수정 완료!")

# 최종 확인
print("\n🧪 수정 결과 확인:")
with open('codes/gemini_augmentation_v2.py', 'r') as f:
    lines = f.readlines()

for line_num in problem_lines:
    if line_num <= len(lines):
        line = lines[line_num-1].strip()
        if 'value=' in line:
            print(f"❌ 라인 {line_num}: 아직 value 있음 - {line}")
        else:
            print(f"✅ 라인 {line_num}: value 제거됨")
EOF

echo ""
echo "🚀 즉시 커밋 및 배포:"
echo "git add codes/gemini_augmentation_v2.py"
echo "git commit -m 'fix: 문제 라인 직접 수정으로 value 파라미터 완전 제거'"
echo "git push origin main"
