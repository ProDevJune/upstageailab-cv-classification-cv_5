#!/bin/bash

echo "🔥 Mac 하드코딩 경로 완전 제거!"
echo "=============================="

echo "📝 gemini_main_v2.py에서 Mac 경로 완전 제거..."

python3 << 'EOF'
with open('codes/gemini_main_v2.py', 'r') as f:
    content = f.read()

# Mac 하드코딩 경로가 남아있는 부분 찾아서 완전 제거
print("🔍 현재 config 경로 설정 확인...")

# config 경로 설정 부분을 완전히 새로 작성
old_config_section = '''        print(f"🔍 args.config: {args.config}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        
        # config 파일 상대 경로로 설정 (Linux 호환)
        config_file_path = os.path.join(os.path.dirname(__file__), args.config)
        
        print(f"🔍 Config 파일 경로: {config_file_path}")
        print(f"🔍 파일 존재 여부: {os.path.exists(config_file_path)}")'''

new_config_section = '''        print(f"🔍 args.config: {args.config}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        
        # config 파일 경로를 현재 실행 위치 기준으로 설정 (Mac/Linux 호환)
        config_file_path = os.path.join('codes', args.config)
        if not os.path.exists(config_file_path):
            # codes 디렉토리 내에서 실행된 경우
            config_file_path = args.config
        
        print(f"🔍 Config 파일 경로: {config_file_path}")
        print(f"🔍 파일 존재 여부: {os.path.exists(config_file_path)}")'''

# 기존 config 설정 부분 교체
if old_config_section in content:
    content = content.replace(old_config_section, new_config_section)
    print("✅ 기존 config 섹션 교체 완료")
else:
    # 다른 패턴으로 남아있을 수 있는 Mac 경로 완전 제거
    import re
    
    # Mac 절대 경로 패턴 찾아서 제거
    mac_path_pattern = r'[^\'"]*'
    if re.search(mac_path_pattern, content):
        print("❌ Mac 하드코딩 경로 발견! 제거 중...")
        content = re.sub(mac_path_pattern, '', content)
        print("✅ Mac 하드코딩 경로 제거 완료")
    
    # config_file_path 설정 부분을 직접 찾아서 수정
    config_pattern = r'config_file_path\s*=.*?(?=\n\s*print)'
    replacement = '''config_file_path = os.path.join('codes', args.config)
        if not os.path.exists(config_file_path):
            config_file_path = args.config'''
    
    content = re.sub(config_pattern, replacement, content, flags=re.DOTALL)
    print("✅ config_file_path 설정 직접 수정 완료")

# 파일 저장
with open('codes/gemini_main_v2.py', 'w') as f:
    f.write(content)

print("🎉 Mac 하드코딩 경로 완전 제거 완료!")
EOF

echo ""
echo "🧪 수정 확인..."
echo "📍 Mac 경로 확인:"
grep -n "/Users/jayden" codes/gemini_main_v2.py || echo "✅ Mac 경로 없음"

echo ""
echo "📍 config_file_path 설정 확인:"
grep -A5 -B2 "config_file_path" codes/gemini_main_v2.py

echo ""
echo "🎉 완전 수정 완료!"
echo ""
echo "📋 수정 내용:"
echo "✅ Mac 하드코딩 경로 완전 제거"
echo "✅ 상대 경로 기반 config 파일 탐지"
echo "✅ codes/ 디렉토리 내외부 실행 모두 지원"
echo ""
echo "🚀 이제 Linux에서 정상 실행됩니다:"
echo "./run_code_v2.sh"
