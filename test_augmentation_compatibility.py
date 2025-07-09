#!/usr/bin/env python3
"""
Albumentations 1.4.0 호환성 테스트 스크립트
"""

import sys
import traceback
import numpy as np
import cv2

def test_augmentation_import():
    """augmentation 모듈 import 테스트"""
    try:
        # 현재 디렉토리에서 codes 모듈을 import할 수 있도록 path 추가
        sys.path.insert(0, './codes')
        from gemini_augmentation_v2 import AUG, get_augmentation
        print("✅ 모듈 import 성공")
        return True
    except Exception as e:
        print(f"❌ 모듈 import 실패: {e}")
        print(traceback.format_exc())
        return False

def test_augmentation_execution():
    """각 augmentation 실행 테스트"""
    try:
        sys.path.insert(0, './codes')
        from gemini_augmentation_v2 import AUG
        
        # 테스트용 더미 이미지 생성
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        success_count = 0
        total_count = len(AUG)
        
        for aug_name, aug_transform in AUG.items():
            try:
                print(f"🧪 테스트 중: {aug_name}")
                result = aug_transform(image=test_image)
                augmented_image = result['image']
                print(f"  ✅ {aug_name} 성공 - 출력 shape: {augmented_image.shape}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {aug_name} 실패: {e}")
                print(f"     {traceback.format_exc()}")
        
        print(f"\n📊 테스트 결과: {success_count}/{total_count} 성공")
        
        if success_count == total_count:
            print("🎉 모든 augmentation이 정상 작동합니다!")
            return True
        else:
            print("⚠️ 일부 augmentation에서 오류가 발생했습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        print(traceback.format_exc())
        return False

def test_get_augmentation_function():
    """get_augmentation 함수 테스트"""
    try:
        sys.path.insert(0, './codes')
        from gemini_augmentation_v2 import get_augmentation
        
        # 다양한 파라미터로 테스트
        test_cases = [
            {'aug_name': 'basic', 'config': None},
            {'aug_name': 'middle', 'config': None},
            {'aug_name': 'aggressive', 'config': None},
        ]
        
        test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        for test_case in test_cases:
            try:
                print(f"🧪 get_augmentation 테스트: {test_case['aug_name']}")
                transform = get_augmentation(test_case['aug_name'], test_case['config'])
                result = transform(image=test_image)
                print(f"  ✅ {test_case['aug_name']} 성공")
            except Exception as e:
                print(f"  ❌ {test_case['aug_name']} 실패: {e}")
                return False
        
        print("✅ get_augmentation 함수 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ get_augmentation 테스트 실패: {e}")
        print(traceback.format_exc())
        return False

def main():
    """메인 테스트 실행"""
    print("🚀 Albumentations 1.4.0 호환성 테스트 시작")
    print("=" * 50)
    
    # 1. Import 테스트
    print("\n1️⃣ 모듈 import 테스트")
    if not test_augmentation_import():
        print("💥 import 테스트 실패로 테스트 중단")
        return False
    
    # 2. 실행 테스트
    print("\n2️⃣ Augmentation 실행 테스트")
    execution_success = test_augmentation_execution()
    
    # 3. get_augmentation 함수 테스트
    print("\n3️⃣ get_augmentation 함수 테스트")
    function_success = test_get_augmentation_function()
    
    # 최종 결과
    print("\n" + "=" * 50)
    if execution_success and function_success:
        print("🎉 모든 테스트 통과! Albumentations 1.4.0 호환성 확인됨")
        return True
    else:
        print("💥 일부 테스트 실패")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
