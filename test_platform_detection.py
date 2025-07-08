#!/usr/bin/env python3
"""
플랫폼 감지 시스템 테스트
현재 Mac에서 MPS 감지가 정상적으로 작동하는지 확인
"""

import sys
import os

# 프로젝트 루트 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from codes.platform_detector import PlatformDetector
    from codes.enhanced_config_manager import EnhancedConfigManager
    
    print("🧪 플랫폼 감지 시스템 테스트")
    print("=" * 50)
    
    # 1. 플랫폼 감지 테스트
    print("1️⃣ 플랫폼 감지 테스트...")
    detector = PlatformDetector()
    detector.print_system_summary()
    
    print("\n" + "=" * 50)
    
    # 2. 설정 관리자 테스트
    print("2️⃣ 설정 관리자 테스트...")
    config_manager = EnhancedConfigManager(detector)
    
    # 빠른 실험용 설정 생성
    quick_config = config_manager.generate_platform_config('quick')
    print(f"✅ 빠른 실험 설정 생성 완료")
    print(f"   디바이스: {quick_config.get('device')}")
    print(f"   배치 크기: {quick_config.get('batch_size')}")
    print(f"   워커 수: {quick_config.get('num_workers')}")
    print(f"   혼합 정밀도: {quick_config.get('mixed_precision')}")
    
    # 플랫폼 요약
    summary = config_manager.get_platform_summary()
    print(f"\n📊 플랫폼 요약:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # 3. HPO 최적화 정보 테스트
    print("3️⃣ HPO 최적화 정보 테스트...")
    hpo_opts = detector.get_hpo_optimization()
    recommended = detector.get_recommended_hpo_method()
    
    print(f"권장 HPO 방법: {recommended.upper()}")
    print(f"HPO 옵션:")
    for method, config in hpo_opts.items():
        status = "✅ 권장" if config.get('recommended') else "⚪ 가능"
        print(f"  {status} {method.replace('_hpo', '').upper()}: 병렬 {config['max_parallel_trials']}개")
    
    print("\n✅ 모든 테스트 완료!")
    print("\n🎯 다음 단계:")
    print("   ./run_experiments.sh 를 실행하여 HPO 시스템을 시작하세요!")
    
except ImportError as e:
    print(f"❌ 모듈 임포트 오류: {e}")
    print("   필요한 패키지가 설치되지 않았을 수 있습니다.")
    print("   pip install torch torchvision pandas numpy matplotlib seaborn psutil")

except Exception as e:
    print(f"❌ 테스트 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
