#!/usr/bin/env python3
"""
🧪 Import 호환성 테스트 스크립트
코드 v2 파일들의 import 구문이 올바르게 작동하는지 검증
"""

import sys
import os

# cv-classification 프로젝트 루트 경로 설정
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_imports():
    """v2 파일들의 import 테스트"""
    
    print("🧪 Starting Import Compatibility Test...")
    print("=" * 50)
    
    try:
        print("📦 Testing gemini_utils_v2 import...")
        from codes.gemini_utils_v2 import load_config, set_seed, ImageDataset
        print("✅ gemini_utils_v2 import successful")
        
        print("📦 Testing gemini_augmentation_v2 import...")
        from codes.gemini_augmentation_v2 import get_augmentation
        print("✅ gemini_augmentation_v2 import successful")
        
        print("📦 Testing gemini_train_v2 import...")
        from codes.gemini_train_v2 import EarlyStopping, TrainModule
        print("✅ gemini_train_v2 import successful")
        
        print("📦 Testing gemini_evalute_v2 import...")
        from codes.gemini_evalute_v2 import tta_predict, predict, do_validation
        print("✅ gemini_evalute_v2 import successful")
        
        print("=" * 50)
        print("🎉 All imports successful!")
        print("✅ 코드 v2 시스템 import 호환성 검증 완료")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_config_loading():
    """config_v2.yaml 로딩 테스트"""
    
    print("\n🔧 Testing config_v2.yaml loading...")
    
    try:
        from codes.gemini_utils_v2 import load_config
        config_path = os.path.join(project_root, 'codes', 'config_v2.yaml')
        
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return False
            
        cfg = load_config(config_path)
        
        print(f"✅ Config loaded successfully")
        print(f"📊 Model: {cfg.model_name}")
        print(f"📁 Data dir: {cfg.data_dir}")
        print(f"🎨 Dynamic augmentation: {cfg.dynamic_augmentation['enabled']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Code v2 Import Compatibility Test")
    print(f"📂 Project root: {project_root}")
    print()
    
    # Import 테스트
    import_success = test_imports()
    
    # Config 로딩 테스트
    config_success = test_config_loading()
    
    print("\n" + "=" * 50)
    if import_success and config_success:
        print("🎊 전체 테스트 성공! 코드 v2 시스템 사용 준비 완료!")
        print("🚀 이제 './run_code_v2.sh'로 새 시스템을 실행할 수 있습니다.")
    else:
        print("⚠️ 일부 테스트 실패. 문제를 해결한 후 다시 시도하세요.")
    print("=" * 50)
