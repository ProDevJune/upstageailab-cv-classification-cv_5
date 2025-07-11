#!/bin/bash

echo "🔧 절대 경로를 상대 경로로 변경 (Linux 서버 호환성)"
echo "=============================================="

echo "📝 모든 하드코딩된 절대 경로 수정 중..."

python3 << 'EOF'
import re

# 수정할 파일들
files_to_fix = [
    'codes/gemini_main_v2.py',
    'codes/config_v2.yaml',
    'run_code_v2.sh'
]

for file_path in files_to_fix:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        print(f"\n🔍 {file_path} 수정 중...")
        
        # 1. gemini_main_v2.py 수정
        if file_path == 'codes/gemini_main_v2.py':
            # project_root를 동적으로 설정
            content = re.sub(
                r"project_root = ''",
                "project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
                content
            )
            
            # config 파일 경로를 상대 경로로 수정
            old_config_block = '''        print(f"🔍 args.config: {args.config}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        
        # config 파일 절대 경로 직접 설정
        if args.config == 'config_v2.yaml':
            config_file_path = 'codes/config_v2.yaml'
        else:
            config_file_path = f'codes/{args.config}' '''
            
            new_config_block = '''        print(f"🔍 args.config: {args.config}")
        print(f"🔍 Current working directory: {os.getcwd()}")
        
        # config 파일 상대 경로로 설정 (Linux 호환)
        config_file_path = os.path.join(os.path.dirname(__file__), args.config)'''
            
            content = content.replace(old_config_block, new_config_block)
            
        # 2. config_v2.yaml 수정
        elif file_path == 'codes/config_v2.yaml':
            # data_dir을 상대 경로로 수정
            content = re.sub(
                r'data_dir: "data"',
                'data_dir: "data"  # 상대 경로 (Linux 호환)',
                content
            )
            
        # 3. run_code_v2.sh는 이미 상대 경로이므로 수정 불필요
        
        # 파일이 변경되었으면 저장
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ {file_path} 수정 완료")
        else:
            print(f"🔍 {file_path} 수정할 내용 없음")
            
    except FileNotFoundError:
        print(f"⚠️ {file_path} 파일 없음")
        continue

print("\n🎉 모든 절대 경로를 상대 경로로 변경 완료!")
print("\n📋 변경 내용:")
print("✅ project_root: 동적 경로 설정")
print("✅ config_file_path: 스크립트 기준 상대 경로")  
print("✅ data_dir: 프로젝트 루트 기준 상대 경로")
EOF

echo ""
echo "🧪 수정 확인..."
echo "📍 project_root 설정:"
grep -n "project_root =" codes/gemini_main_v2.py || echo "❌ project_root 설정 없음"

echo ""
echo "📍 data_dir 설정:"
grep -n "data_dir:" codes/config_v2.yaml || echo "❌ data_dir 설정 없음"

echo ""
echo "🚀 Linux 서버에서도 정상 작동할 것입니다:"
echo "./run_code_v2.sh"

echo ""
echo "🐧 Linux 서버 배포 시 주의사항:"
echo "1. 프로젝트 루트에서 실행하세요"
echo "2. data/ 폴더가 프로젝트 루트에 있는지 확인하세요"
echo "3. 모든 스크립트는 프로젝트 루트에서 실행하세요"
