#!/usr/bin/env python3
"""
🔧 수정된 플랫폼 호환성 테스트 스크립트
Mac OS (MPS) / Ubuntu (CUDA) / CPU 자동 감지 및 Mixed Precision 테스트
"""

import sys
import os
import torch

# cv-classification 프로젝트 루트 경로 설정
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_device_detection():
    """Device 자동 감지 테스트"""
    
    print("🖥️ Device 자동 감지 테스트...")
    print("=" * 50)
    
    # gemini_main_v2.py와 동일한 로직
    device = 'cpu'
    if torch.backends.mps.is_available():
        device = torch.device('mps')
        print("✅ MPS (Mac OS Metal) 감지됨")
    elif torch.cuda.is_available():
        device = torch.device('cuda')
        print(f"✅ CUDA 감지됨 - GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("✅ CPU 모드로 실행")
    
    print(f"🎯 선택된 Device: {device}")
    return device

def test_mixed_precision_compatibility(device):
    """Mixed Precision 호환성 테스트"""
    
    print("\n🔧 Mixed Precision 호환성 테스트...")
    print("=" * 50)
    
    device_str = str(device)
    is_cuda = device_str.startswith('cuda')
    is_mps = device_str.startswith('mps')
    is_cpu = device_str == 'cpu'
    
    print(f"📱 Device Type: {device_str}")
    print(f"🔸 CUDA: {is_cuda}")
    print(f"🔸 MPS: {is_mps}")
    print(f"🔸 CPU: {is_cpu}")
    
    # Mixed Precision 설정 테스트
    use_mixed_precision = True and is_cuda  # CUDA에서만 활성화
    autocast_device_type = 'cuda' if is_cuda else None
    
    print(f"⚡ Mixed Precision 사용: {'Yes' if use_mixed_precision else 'No'}")
    print(f"⚡ AutoCast Device Type: {autocast_device_type}")
    
    # GradScaler 테스트
    try:
        scaler = torch.amp.GradScaler(enabled=use_mixed_precision)
        print("✅ GradScaler 초기화 성공")
    except Exception as e:
        print(f"❌ GradScaler 초기화 실패: {e}")
        return False
    
    # AutoCast 테스트
    try:
        if use_mixed_precision and autocast_device_type:
            with torch.amp.autocast(device_type=autocast_device_type, enabled=True):
                # 간단한 텐서 연산 테스트
                x = torch.randn(2, 3).to(device)
                y = torch.randn(3, 2).to(device)
                z = torch.mm(x, y)
            print("✅ Mixed Precision AutoCast 테스트 성공")
        else:
            # 일반 연산 테스트
            x = torch.randn(2, 3).to(device)
            y = torch.randn(3, 2).to(device)
            z = torch.mm(x, y)
            print("✅ 일반 연산 테스트 성공")
    except Exception as e:
        print(f"❌ 연산 테스트 실패: {e}")
        return False
    
    return True

def test_cache_management(device):
    """캐시 관리 함수 테스트"""
    
    print("\n🧹 캐시 관리 테스트...")
    print("=" * 50)
    
    device_str = str(device)
    
    def _clear_device_cache(device):
        """gemini_train_v2.py와 동일한 함수"""
        device_str = str(device)
        if device_str.startswith('cuda'):
            torch.cuda.empty_cache()
            return "CUDA 캐시 비우기"
        elif device_str.startswith('mps'):
            try:
                torch.mps.empty_cache()
                return "MPS 캐시 비우기"
            except AttributeError:
                return "MPS 캐시 비우기 (torch.mps.empty_cache 미지원)"
        return "CPU (캐시 비우기 불필요)"
    
    try:
        result = _clear_device_cache(device)
        print(f"✅ {result} 성공")
        return True
    except Exception as e:
        print(f"❌ 캐시 관리 실패: {e}")
        return False

def test_imports():
    """수정된 v2 파일들의 import 테스트"""
    
    print("\n📦 Import 호환성 테스트...")
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
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_train_module_initialization():
    """TrainModule 초기화 테스트 (플랫폼별 설정 확인)"""
    
    print("\n🏋️ TrainModule 플랫폼 호환성 테스트...")
    print("=" * 50)
    
    try:
        from codes.gemini_utils_v2 import load_config
        from codes.gemini_train_v2 import TrainModule
        
        # Config 로드
        config_path = os.path.join(project_root, 'codes', 'config_v2.yaml')
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return False
            
        cfg = load_config(config_path)
        
        # Device 설정
        device = 'cpu'
        if torch.backends.mps.is_available():
            device = torch.device('mps')
        elif torch.cuda.is_available():
            device = torch.device('cuda')
        cfg.device = device
        
        # 간단한 모델 생성 (테스트용)
        import torch.nn as nn
        model = nn.Sequential(
            nn.Linear(10, 5),
            nn.ReLU(),
            nn.Linear(5, 3)
        )
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10)
        
        # 더미 데이터로더 (실제로는 사용하지 않음)
        from torch.utils.data import TensorDataset, DataLoader
        dummy_data = TensorDataset(torch.randn(10, 10), torch.randint(0, 3, (10,)))
        dummy_loader = DataLoader(dummy_data, batch_size=2)
        
        # TrainModule 초기화 테스트
        trainer = TrainModule(
            model=model,
            criterion=criterion,
            optimizer=optimizer,
            scheduler=scheduler,
            train_loader=dummy_loader,
            valid_loader=dummy_loader,
            cfg=cfg,
            verbose=1,
            run=None
        )
        
        print("✅ TrainModule 초기화 성공")
        print(f"✅ Device 설정: {trainer.device_str}")
        print(f"✅ Mixed Precision: {'Enabled' if trainer.use_mixed_precision else 'Disabled'}")
        print(f"✅ AutoCast Device Type: {trainer.autocast_device_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ TrainModule 초기화 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 플랫폼 호환성 테스트 시작")
    print(f"📂 Project root: {project_root}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🔥 PyTorch version: {torch.__version__}")
    print()
    
    # 테스트 실행
    device = test_device_detection()
    mixed_precision_ok = test_mixed_precision_compatibility(device)
    cache_ok = test_cache_management(device)
    import_ok = test_imports()
    train_module_ok = test_train_module_initialization()
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    print(f"🖥️ Device 감지: {'✅ 성공' if device else '❌ 실패'}")
    print(f"⚡ Mixed Precision: {'✅ 성공' if mixed_precision_ok else '❌ 실패'}")
    print(f"🧹 캐시 관리: {'✅ 성공' if cache_ok else '❌ 실패'}")
    print(f"📦 Import 호환성: {'✅ 성공' if import_ok else '❌ 실패'}")
    print(f"🏋️ TrainModule 호환성: {'✅ 성공' if train_module_ok else '❌ 실패'}")
    
    all_passed = all([mixed_precision_ok, cache_ok, import_ok, train_module_ok])
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎊 모든 테스트 통과! 플랫폼 호환성 수정 완료!")
        print("🚀 이제 Mac OS/Ubuntu 모든 환경에서 안전하게 실행할 수 있습니다.")
        if str(device).startswith('mps'):
            print("🍎 Mac OS (MPS) 환경 최적화 완료")
        elif str(device).startswith('cuda'):
            print("🐧 Ubuntu (CUDA) 환경 최적화 완료")
        else:
            print("💻 CPU 환경 호환성 확인 완료")
    else:
        print("⚠️ 일부 테스트 실패. 문제를 해결한 후 다시 시도하세요.")
    print("=" * 50)
