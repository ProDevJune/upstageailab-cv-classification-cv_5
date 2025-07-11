#!/usr/bin/env python3
"""
실험 격리 시스템 테스트 스크립트
"""

import os
import sys
import time
import torch
import numpy as np
import random
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from experiments.isolation_utils import (
    ExperimentIsolationContext,
    setup_experiment_isolation,
    validate_system_state,
    quick_cleanup
)


def test_isolation_quality():
    """격리 품질 테스트"""
    print("🧪 실험 격리 품질 테스트 시작")
    print("=" * 50)
    
    # 테스트 1: 환경 변수 격리
    print("1️⃣ 환경 변수 격리 테스트")
    
    original_env = os.environ.get('TEST_VAR', 'not_set')
    
    with ExperimentIsolationContext('test_exp_001'):
        os.environ['TEST_VAR'] = 'isolated_value'
        inside_value = os.environ.get('TEST_VAR')
        print(f"   격리 내부: {inside_value}")
    
    after_value = os.environ.get('TEST_VAR', 'not_set')
    print(f"   격리 외부: {after_value}")
    
    if after_value == original_env:
        print("   ✅ 환경 변수 격리 성공")
    else:
        print("   ❌ 환경 변수 격리 실패")
    
    print()
    
    # 테스트 2: Random Seed 격리
    print("2️⃣ Random Seed 격리 테스트")
    
    # 첫 번째 실험
    with ExperimentIsolationContext('test_exp_002'):
        setup_experiment_isolation('test_exp_002', 42)
        rand1_py = random.random()
        rand1_np = np.random.random()
        rand1_torch = torch.rand(1).item()
    
    # 두 번째 실험 (같은 시드)
    with ExperimentIsolationContext('test_exp_003'):
        setup_experiment_isolation('test_exp_003', 42)
        rand2_py = random.random()
        rand2_np = np.random.random()
        rand2_torch = torch.rand(1).item()
    
    print(f"   실험 002 - Python: {rand1_py:.6f}, NumPy: {rand1_np:.6f}, Torch: {rand1_torch:.6f}")
    print(f"   실험 003 - Python: {rand2_py:.6f}, NumPy: {rand2_np:.6f}, Torch: {rand2_torch:.6f}")
    
    # 시드가 제대로 격리되었다면 값이 달라야 함
    if (rand1_py != rand2_py or rand1_np != rand2_np or rand1_torch != rand2_torch):
        print("   ✅ Random Seed 격리 성공")
    else:
        print("   ❌ Random Seed 격리 실패")
    
    print()
    
    # 테스트 3: GPU 메모리 정리
    print("3️⃣ GPU 메모리 정리 테스트")
    
    if torch.cuda.is_available():
        initial_memory = torch.cuda.memory_allocated()
        print(f"   초기 GPU 메모리: {initial_memory / 1024**2:.1f} MB")
        
        with ExperimentIsolationContext('test_exp_004'):
            # 큰 텐서 생성
            big_tensor = torch.randn(1000, 1000, device='cuda')
            inside_memory = torch.cuda.memory_allocated()
            print(f"   텐서 생성 후: {inside_memory / 1024**2:.1f} MB")
        
        final_memory = torch.cuda.memory_allocated()
        print(f"   정리 후: {final_memory / 1024**2:.1f} MB")
        
        if final_memory <= initial_memory + 1024*1024:  # 1MB 오차 허용
            print("   ✅ GPU 메모리 정리 성공")
        else:
            print("   ❌ GPU 메모리 정리 실패")
    else:
        print("   ⏭️ GPU 없음, 테스트 건너뜀")
    
    print()
    
    # 테스트 4: 시스템 상태 검증
    print("4️⃣ 시스템 상태 검증 테스트")
    system_healthy = validate_system_state()
    if system_healthy:
        print("   ✅ 시스템 상태 양호")
    else:
        print("   ⚠️ 시스템 상태 주의 필요")
    
    print("\n🏁 격리 품질 테스트 완료!")


def test_multiple_experiments():
    """여러 실험 연속 실행 시뮬레이션"""
    print("\n🔄 연속 실험 격리 테스트")
    print("=" * 50)
    
    experiments = [
        {'id': 'seq_exp_001', 'duration': 2},
        {'id': 'seq_exp_002', 'duration': 1},
        {'id': 'seq_exp_003', 'duration': 3},
    ]
    
    results = []
    
    for exp in experiments:
        print(f"🚀 실험 시작: {exp['id']}")
        
        start_time = time.time()
        
        with ExperimentIsolationContext(exp['id']):
            # 실험별 시드 설정
            setup_experiment_isolation(exp['id'], 42)
            
            # 격리 품질 확인
            env_id = os.environ.get('EXPERIMENT_ID', 'unknown')
            
            # 시뮬레이션된 작업
            time.sleep(exp['duration'])
            
            # 랜덤 값 생성 (격리 확인용)
            rand_val = random.random()
            
            results.append({
                'exp_id': exp['id'],
                'env_id': env_id,
                'rand_val': rand_val,
                'duration': time.time() - start_time
            })
        
        print(f"✅ 실험 완료: {exp['id']}")
        time.sleep(1)  # 실험 간 간격
    
    print("\n📊 실험 결과:")
    for result in results:
        print(f"   {result['exp_id']}: env={result['env_id']}, "
              f"rand={result['rand_val']:.6f}, time={result['duration']:.1f}s")
    
    # 격리 품질 검증
    isolation_success = all(r['env_id'] == r['exp_id'] for r in results)
    randomness_success = len(set(r['rand_val'] for r in results)) == len(results)
    
    print(f"\n격리 성공률:")
    print(f"   환경 변수 격리: {'✅' if isolation_success else '❌'}")
    print(f"   랜덤성 격리: {'✅' if randomness_success else '❌'}")


if __name__ == "__main__":
    print("🧪 실험 격리 시스템 테스트")
    print("=" * 80)
    
    try:
        # 기본 격리 품질 테스트
        test_isolation_quality()
        
        # 연속 실험 테스트
        test_multiple_experiments()
        
        print("\n🎉 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
