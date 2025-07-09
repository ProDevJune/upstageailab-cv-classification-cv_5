#!/usr/bin/env python3
"""
서버에서 즉시 Albumentations API 수정하는 Python 스크립트
gemini_augmentation_v2.py 파일의 fill 파라미터를 정확히 수정
"""

import os
import re
import shutil
from datetime import datetime

def fix_augmentation_file():
    augmentation_file = "codes/gemini_augmentation_v2.py"
    
    if not os.path.exists(augmentation_file):
        print(f"❌ {augmentation_file} 파일을 찾을 수 없습니다.")
        return False
    
    # 백업 생성
    backup_file = f"{augmentation_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(augmentation_file, backup_file)
    print(f"📄 백업 생성: {backup_file}")
    
    # 파일 읽기
    with open(augmentation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔄 API 파라미터 수정 중...")
    
    # 수정 내용들
    fixes = [
        # 1. fill=(255,255,255) -> fill=255
        (r'fill=\(255,\s*255,\s*255\)', 'fill=255'),
        
        # 2. fill=(0,0,0) -> fill=0  
        (r'fill=\(0,\s*0,\s*0\)', 'fill=0'),
        
        # 3. PadIfNeeded의 fill -> value
        (r'(\s+)fill=\(255,\s*255,\s*255\)', r'\1value=(255, 255, 255)'),
        
        # 4. Rotate에 border_mode 추가가 필요한 경우
        (r'A\.Rotate\(\s*limit=', 'A.Rotate(\n            border_mode=cv2.BORDER_CONSTANT,\n            limit='),
    ]
    
    original_content = content
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # 변경사항이 있는지 확인
    if content != original_content:
        # 파일 쓰기
        with open(augmentation_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 파일 수정 완료!")
        return True
    else:
        print("ℹ️ 수정할 내용이 없습니다. (이미 수정되었거나 다른 형식)")
        return True

def test_import():
    """수정된 파일 import 테스트"""
    print("\n🧪 import 테스트 중...")
    try:
        import sys
        sys.path.insert(0, 'codes')
        
        # 기존 모듈 삭제 (재로드를 위해)
        if 'gemini_augmentation_v2' in sys.modules:
            del sys.modules['gemini_augmentation_v2']
        
        from gemini_augmentation_v2 import AUG
        print("✅ gemini_augmentation_v2.py import 성공!")
        
        # 간단한 변환 테스트
        import albumentations as A
        import numpy as np
        
        transform = AUG['basic']
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = transform(image=test_img)
        print("✅ Augmentation 변환 테스트 성공!")
        print("🎉 API 호환성 문제 해결 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print("💡 파일을 수동으로 확인해주세요.")
        return False

if __name__ == "__main__":
    print("🔧 Albumentations API 즉시 수정 시작...")
    
    if fix_augmentation_file():
        if test_import():
            print("\n🚀 수정 완료! 이제 실험을 실행하세요:")
            print("  python quick_test_experiments.py")
        else:
            print("\n⚠️ import 테스트 실패. 수동 확인이 필요합니다.")
    else:
        print("\n❌ 파일 수정에 실패했습니다.")
