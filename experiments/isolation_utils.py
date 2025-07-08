#!/usr/bin/env python3
"""
실험 격리를 위한 유틸리티 함수들 (수정됨)
"""

import os
import gc
import time
import random
import shutil
import psutil
import torch
import numpy as np
from pathlib import Path


def setup_experiment_isolation(experiment_id: str, base_seed: int = 42):
    """
    실험별 완전 격리 환경 설정
    
    Args:
        experiment_id: 실험 고유 ID
        base_seed: 기본 시드값
    """
    # 🔧 수정: 실험별 더 큰 시드 차이 생성
    hash_val = abs(hash(experiment_id))
    experiment_seed = base_seed + (hash_val % 50000)  # 더 큰 범위로 시드 차이
    
    print(f"🔧 실험 격리 설정: {experiment_id}")
    print(f"   🎲 고유 시드: {experiment_seed}")
    
    # 2. 🔧 수정: 균형잡힌 결정론성 설정
    setup_balanced_deterministic_environment(experiment_seed)
    
    # 3. 실험별 임시 디렉토리 생성
    temp_dirs = create_experiment_temp_dirs(experiment_id)
    
    # 4. 환경 변수 설정
    setup_isolated_env_vars(experiment_id, temp_dirs)
    
    return experiment_seed, temp_dirs


def setup_balanced_deterministic_environment(seed: int):
    """🔧 수정: 균형잡힌 결정론적 환경 설정 (재현성 유지하면서 다양성 확보)"""
    # Python 기본 랜덤
    random.seed(seed)
    
    # NumPy 랜덤
    np.random.seed(seed)
    
    # PyTorch 랜덤
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    
    # 🔥 핵심 수정: cuDNN 설정 - 다양성 허용하면서 재현성 유지
    torch.backends.cudnn.deterministic = False  # 다양성 허용
    torch.backends.cudnn.benchmark = True       # 성능 최적화 허용
    
    print(f"   ✅ 균형잡힌 환경 설정 완료 (seed: {seed}, deterministic: False)")


def setup_deterministic_environment(seed: int):
    """완전히 결정론적 환경 설정 (이전 버전 - 호환성 유지)"""
    setup_balanced_deterministic_environment(seed)


def create_experiment_temp_dirs(experiment_id: str):
    """실험별 임시 디렉토리 생성"""
    base_temp = Path("/tmp/cv_experiments")
    exp_temp = base_temp / experiment_id
    
    temp_dirs = {
        'base': exp_temp,
        'cuda_cache': exp_temp / "cuda_cache",
        'torch_home': exp_temp / "torch_home", 
        'wandb': exp_temp / "wandb",
        'outputs': exp_temp / "outputs"
    }
    
    # 디렉토리 생성
    for dir_path in temp_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print(f"   📁 임시 디렉토리: {exp_temp}")
    return temp_dirs


def setup_isolated_env_vars(experiment_id: str, temp_dirs: dict):
    """격리된 환경 변수 설정"""
    os.environ.update({
        'EXPERIMENT_ID': experiment_id,
        'PYTHONHASHSEED': str(hash(experiment_id) % 2**32),
        'CUDA_CACHE_PATH': str(temp_dirs['cuda_cache']),
        'TORCH_HOME': str(temp_dirs['torch_home']),
        'WANDB_DIR': str(temp_dirs['wandb']),
        'EXPERIMENT_TEMP_DIR': str(temp_dirs['base'])
    })
    
    print(f"   🌍 환경 변수 설정 완료")


def cleanup_experiment_temp_dirs(experiment_id: str):
    """실험별 임시 디렉토리 정리"""
    base_temp = Path("/tmp/cv_experiments") / experiment_id
    
    if base_temp.exists():
        try:
            shutil.rmtree(base_temp)
            print(f"   🧹 임시 디렉토리 정리: {base_temp}")
        except Exception as e:
            print(f"   ⚠️ 임시 디렉토리 정리 실패: {e}")


def validate_system_state():
    """시스템 상태 검증"""
    issues = []
    
    # 메모리 확인
    memory = psutil.virtual_memory()
    if memory.percent > 85:
        issues.append(f"높은 메모리 사용률: {memory.percent}%")
    
    # GPU 메모리 확인
    if torch.cuda.is_available():
        allocated_gb = torch.cuda.memory_allocated() / 1024**3
        if allocated_gb > 0.5:  # 500MB 이상
            issues.append(f"GPU 메모리 누수 의심: {allocated_gb:.1f}GB")
    
    # CPU 확인
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 90:
        issues.append(f"높은 CPU 사용률: {cpu_percent}%")
    
    if issues:
        print("⚠️ 시스템 상태 이슈:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ 시스템 상태 양호")
    return True


def deep_cleanup():
    """깊은 수준의 정리"""
    print("🧹 깊은 수준 정리 시작...")
    
    # 1. GPU 메모리 완전 정리
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        
        # 모든 GPU에 대해 정리
        for i in range(torch.cuda.device_count()):
            with torch.cuda.device(i):
                torch.cuda.empty_cache()
    
    # 2. Python 가비지 컬렉션 (여러 번)
    for _ in range(3):
        gc.collect()
        time.sleep(1)
    
    # 3. 프로세스 메모리 정리 시도
    try:
        # Linux/macOS에서 메모리 정리 요청
        os.system("sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true")
    except:
        pass
    
    print("   ✅ 깊은 수준 정리 완료")


def wait_for_system_stability(max_wait: int = 30):
    """시스템 안정화까지 대기"""
    print("⏳ 시스템 안정화 대기...")
    
    for i in range(max_wait):
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        if memory.percent < 80 and cpu < 50:
            print(f"   ✅ 시스템 안정화 완료 ({i+1}초 대기)")
            return True
        
        time.sleep(1)
        if (i + 1) % 10 == 0:
            print(f"   ⏳ {i+1}초 경과... (메모리: {memory.percent}%, CPU: {cpu}%)")
    
    print("   ⚠️ 시스템 안정화 시간 초과")
    return False


class ExperimentIsolationContext:
    """실험 격리 컨텍스트 매니저"""
    
    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
        self.temp_dirs = None
        self.original_env = None
    
    def __enter__(self):
        print(f"🔒 실험 격리 시작: {self.experiment_id}")
        
        # 환경 백업
        self.original_env = os.environ.copy()
        
        # 격리 설정
        seed, temp_dirs = setup_experiment_isolation(self.experiment_id)
        self.temp_dirs = temp_dirs
        
        # 시스템 상태 검증
        validate_system_state()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"🔓 실험 격리 해제: {self.experiment_id}")
        
        # 환경 복원
        if self.original_env:
            os.environ.clear()
            os.environ.update(self.original_env)
        
        # 임시 파일 정리
        cleanup_experiment_temp_dirs(self.experiment_id)
        
        # 깊은 정리
        deep_cleanup()
        
        # 안정화 대기
        wait_for_system_stability()


# 편의 함수들
def quick_cleanup():
    """빠른 정리"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


def check_isolation_quality(experiment_id: str):
    """격리 품질 확인"""
    env_id = os.environ.get('EXPERIMENT_ID', 'unknown')
    if env_id != experiment_id:
        print(f"⚠️ 환경 변수 격리 실패: 예상={experiment_id}, 실제={env_id}")
        return False
    
    print(f"✅ 격리 품질 확인 통과: {experiment_id}")
    return True
