#!/usr/bin/env python3
"""
현재 환경의 albumentations 버전과 API 확인 스크립트
"""

def check_environment():
    print("🔍 현재 환경 확인 중...")
    
    # 패키지 버전 확인
    packages = ['albumentations', 'opencv-python', 'numpy']
    for package in packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✅ {package}: {cv2.__version__}")
            else:
                module = __import__(package)
                print(f"✅ {package}: {module.__version__}")
        except ImportError:
            print(f"❌ {package}: 설치되지 않음")
        except Exception as e:
            print(f"⚠️ {package}: {e}")
    
    print("\n🧪 Albumentations API 테스트...")
    
    try:
        import albumentations as A
        import inspect
        
        # Affine 클래스의 __init__ 파라미터 확인
        affine_params = inspect.signature(A.Affine.__init__).parameters
        print(f"📋 A.Affine 파라미터: {list(affine_params.keys())}")
        
        if 'fill' in affine_params:
            print("✅ A.Affine에 fill 파라미터 있음")
        else:
            print("❌ A.Affine에 fill 파라미터 없음")
        
        # 간단한 Affine 테스트
        try:
            transform = A.Affine(scale=(0.8, 1.2), fill=255, p=1.0)
            print("✅ A.Affine(fill=255) 생성 성공")
        except Exception as e:
            print(f"❌ A.Affine(fill=255) 실패: {e}")
            
        try:
            transform = A.Affine(scale=(0.8, 1.2), fill=(255, 255, 255), p=1.0)
            print("✅ A.Affine(fill=(255,255,255)) 생성 성공")
        except Exception as e:
            print(f"❌ A.Affine(fill=(255,255,255)) 실패: {e}")
            
    except Exception as e:
        print(f"❌ Albumentations 테스트 실패: {e}")

def check_current_file():
    print("\n📄 현재 gemini_augmentation_v2.py 파일 확인...")
    
    augmentation_file = "codes/gemini_augmentation_v2.py"
    if not os.path.exists(augmentation_file):
        print(f"❌ {augmentation_file} 파일을 찾을 수 없습니다.")
        return
    
    with open(augmentation_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fill_lines = []
    for i, line in enumerate(lines, 1):
        if 'fill=' in line:
            fill_lines.append(f"  줄 {i}: {line.strip()}")
    
    if fill_lines:
        print("📋 파일에서 발견된 fill 파라미터들:")
        for line in fill_lines[:10]:  # 최대 10개만 표시
            print(line)
        if len(fill_lines) > 10:
            print(f"  ... 총 {len(fill_lines)}개 발견")
    else:
        print("ℹ️ fill 파라미터를 찾을 수 없습니다.")

if __name__ == "__main__":
    import os
    
    check_environment()
    check_current_file()
    
    print("\n💡 다음 단계:")
    print("  1. python fix_augmentation_immediate.py")
    print("  2. python quick_test_experiments.py")
