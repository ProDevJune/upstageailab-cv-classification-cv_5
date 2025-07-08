#!/usr/bin/env python3
"""
DataLoader 설정 수정으로 "Too many open files" 오류 해결
"""

import re
import os

def fix_dataloader_in_file(file_path):
    """파일에서 DataLoader 설정 수정"""
    if not os.path.exists(file_path):
        print(f"⚠️ 파일이 없습니다: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. pin_memory=True를 False로 변경
        content = re.sub(r'pin_memory\s*=\s*True', 'pin_memory=False', content)
        
        # 2. num_workers 값을 0으로 변경
        content = re.sub(r'num_workers\s*=\s*\d+', 'num_workers=0', content)
        
        # 3. DataLoader에 명시적으로 안전한 설정 추가 (없는 경우)
        if 'num_workers=0' not in content:
            # DataLoader 호출 부분 찾아서 수정
            dataloader_pattern = r'DataLoader\s*\([^)]*\)'
            def add_safe_params(match):
                dataloader_call = match.group(0)
                if 'num_workers' not in dataloader_call:
                    # ) 앞에 파라미터 추가
                    dataloader_call = dataloader_call[:-1] + ', num_workers=0, pin_memory=False)'
                return dataloader_call
            
            content = re.sub(dataloader_pattern, add_safe_params, content)
        
        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 수정 완료: {file_path}")
            return True
        else:
            print(f"📋 변경사항 없음: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {file_path} - {e}")
        return False

def main():
    """메인 실행"""
    print("🔧 DataLoader 설정 수정 시작")
    
    # 수정할 파일 목록
    files_to_fix = [
        'codes/gemini_main.py',
        'codes/gemini_train.py', 
        'codes/gemini_evalute.py',
    ]
    
    success_count = 0
    for file_path in files_to_fix:
        if fix_dataloader_in_file(file_path):
            success_count += 1
    
    print(f"\n📊 수정 완료: {success_count}/{len(files_to_fix)} 파일")
    
    # 시스템 설정도 확인
    print(f"\n🔍 현재 파일 한계: {os.popen('ulimit -n').read().strip()}")
    print("💡 파일 한계를 증가시키려면: ulimit -n 4096")

if __name__ == "__main__":
    main()
