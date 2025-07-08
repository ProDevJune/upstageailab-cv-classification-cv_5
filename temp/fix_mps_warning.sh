#!/bin/bash

echo "🔧 MPS pin_memory 경고 해결!"
echo "============================"

echo "📝 DataLoader에서 MPS 사용 시 pin_memory=False로 설정..."

python3 << 'EOF'
import re

# gemini_train_v2.py에서 DataLoader 설정 수정
files_to_check = [
    'codes/gemini_train_v2.py',
    'codes/gemini_main_v2.py',
    'codes/gemini_evalute_v2.py'
]

for file_path in files_to_check:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # DataLoader에서 pin_memory 설정을 MPS 감지하여 조정
        pin_memory_pattern = r'(DataLoader\([^)]*?)pin_memory\s*=\s*True([^)]*?\))'
        
        def replace_pin_memory(match):
            before = match.group(1)
            after = match.group(2)
            
            # MPS 감지 코드 추가
            new_pin_memory = """pin_memory=False if torch.backends.mps.is_available() else True"""
            
            return f"{before}{new_pin_memory}{after}"
        
        new_content = re.sub(pin_memory_pattern, replace_pin_memory, content)
        
        if new_content != content:
            with open(file_path, 'w') as f:
                f.write(new_content)
            print(f"✅ {file_path} - pin_memory 설정 수정 완료")
        else:
            print(f"🔍 {file_path} - 수정할 DataLoader 없음")
            
    except FileNotFoundError:
        print(f"⚠️ {file_path} - 파일 없음")
        continue

print("\n🎉 MPS pin_memory 경고 해결 완료!")
EOF

echo ""
echo "🚀 이제 MPS 경고 없이 실행됩니다:"
echo "./run_code_v2.sh"
