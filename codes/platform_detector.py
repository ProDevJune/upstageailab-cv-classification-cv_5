"""
크로스 플랫폼 환경 자동 감지 및 최적화 모듈
Mac MPS / Ubuntu CUDA 자동 감지 및 최적 설정 제공
"""

import platform
import torch
import subprocess
import psutil
import os
from typing import Dict, List, Tuple
import json

class PlatformDetector:
    """크로스 플랫폼 환경 자동 감지 및 최적화"""
    
    def __init__(self):
        self.system_info = self._detect_system()
        self.device_info = self._detect_devices()
        self.optimization_config = self._generate_optimization_config()
    
    def _detect_system(self) -> Dict:
        """시스템 정보 감지"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        return {
            'os': system,
            'architecture': machine,
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(logical=True),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 1)
        }
    
    def _detect_devices(self) -> Dict:
        """사용 가능한 컴퓨팅 디바이스 감지"""
        devices = {
            'cpu': True,
            'cuda': False,
            'mps': False,
            'cuda_devices': [],
            'primary_device': 'cpu'
        }
        
        # CUDA 감지 (NVIDIA GPU - Linux/Windows)
        if torch.cuda.is_available():
            devices['cuda'] = True
            devices['cuda_devices'] = [
                {
                    'id': i,
                    'name': torch.cuda.get_device_name(i),
                    'memory_gb': round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 1)
                }
                for i in range(torch.cuda.device_count())
            ]
            devices['primary_device'] = 'cuda'
        
        # MPS 감지 (Apple Silicon - macOS)
        elif torch.backends.mps.is_available():
            devices['mps'] = True
            devices['primary_device'] = 'mps'
            # Apple Silicon 메모리는 통합 메모리
            devices['mps_memory_gb'] = self.system_info['memory_gb']
        
        return devices
    
    def _generate_optimization_config(self) -> Dict:
        """플랫폼별 최적화 설정 생성"""
        config = {
            'device': self.device_info['primary_device'],
            'batch_size_multiplier': 1.0,
            'num_workers': min(4, self.system_info['cpu_count']),
            'pin_memory': True,
            'mixed_precision': False,
            'compile_model': False,
            'memory_efficient': False
        }
        
        # 🐧 Linux + CUDA 최적화
        if self.system_info['os'] == 'linux' and self.device_info['cuda']:
            config.update({
                'batch_size_multiplier': 1.5,  # CUDA 메모리 효율성
                'num_workers': min(8, self.system_info['cpu_count']),
                'mixed_precision': True,  # CUDA의 강력한 FP16 지원
                'compile_model': True,  # torch.compile 사용
                'memory_efficient': False
            })
        
        # 🍎 macOS + MPS 최적화
        elif self.system_info['os'] == 'darwin' and self.device_info['mps']:
            config.update({
                'batch_size_multiplier': 0.8,  # MPS 메모리 제한 고려
                'num_workers': min(4, self.system_info['cpu_count'] // 2),  # MPS는 CPU와 메모리 공유
                'mixed_precision': False,  # MPS FP16 지원 제한적
                'pin_memory': False,  # MPS에서는 불필요
                'memory_efficient': True  # 통합 메모리 효율적 사용
            })
        
        # 💻 CPU 전용 최적화
        elif self.device_info['primary_device'] == 'cpu':
            config.update({
                'batch_size_multiplier': 0.5,  # CPU 메모리 제한
                'num_workers': self.system_info['cpu_count'],
                'mixed_precision': False,
                'memory_efficient': True
            })
        
        return config
    
    def get_recommended_batch_sizes(self, base_batch_size: int = 32) -> Dict[str, int]:
        """플랫폼별 권장 배치 크기"""
        multiplier = self.optimization_config['batch_size_multiplier']
        base_size = max(1, int(base_batch_size * multiplier))
        
        return {
            'train': base_size,
            'val': base_size * 2,  # 검증은 gradient 계산 안하므로 더 큰 배치 가능
            'test': base_size * 2
        }
    
    def get_hpo_optimization(self) -> Dict:
        """HPO별 플랫폼 최적화 설정"""
        return {
            'basic_hpo': {
                'max_parallel_trials': 1,  # 안전한 설정
                'memory_per_trial': 0.8,
                'recommended': self.device_info['primary_device'] == 'cpu'
            },
            'optuna_hpo': {
                'max_parallel_trials': 2 if self.device_info['cuda'] else 1,
                'memory_per_trial': 0.6 if self.device_info['cuda'] else 0.8,
                'pruning_enabled': True,
                'recommended': self.device_info['primary_device'] in ['mps', 'cuda']
            },
            'ray_tune_hpo': {
                'max_parallel_trials': len(self.device_info.get('cuda_devices', [])) or 1,
                'resources_per_trial': self._get_ray_resources(),
                'memory_per_trial': 0.4 if len(self.device_info.get('cuda_devices', [])) > 1 else 0.8,
                'recommended': len(self.device_info.get('cuda_devices', [])) > 1
            }
        }
    
    def _get_ray_resources(self) -> Dict:
        """Ray Tune용 리소스 설정"""
        if self.device_info['cuda']:
            gpu_count = len(self.device_info['cuda_devices'])
            return {
                'cpu': 2,
                'gpu': 1 if gpu_count > 1 else 0.5
            }
        elif self.device_info['mps']:
            return {
                'cpu': 4,
                'gpu': 0  # Ray Tune이 MPS를 직접 지원하지 않음
            }
        else:
            return {
                'cpu': max(2, self.system_info['cpu_count'] // 2),
                'gpu': 0
            }
    
    def get_recommended_hpo_method(self) -> str:
        """현재 플랫폼에 최적화된 HPO 방법 추천"""
        hpo_opts = self.get_hpo_optimization()
        
        for method, config in hpo_opts.items():
            if config.get('recommended', False):
                return method.replace('_hpo', '')
        
        # 기본값: optuna (가장 범용적)
        return 'optuna'
    
    def print_system_summary(self):
        """시스템 정보 요약 출력"""
        print("🖥️  시스템 정보")
        print("=" * 50)
        print(f"OS: {self.system_info['os'].title()}")
        print(f"아키텍처: {self.system_info['architecture']}")
        print(f"CPU 코어: {self.system_info['cpu_count']}")
        print(f"메모리: {self.system_info['memory_gb']} GB")
        print(f"Python: {self.system_info['python_version']}")
        
        print("\n🚀 컴퓨팅 디바이스")
        print("=" * 50)
        print(f"주 디바이스: {self.device_info['primary_device'].upper()}")
        
        if self.device_info['cuda']:
            print("CUDA 디바이스:")
            for device in self.device_info['cuda_devices']:
                print(f"  - GPU {device['id']}: {device['name']} ({device['memory_gb']} GB)")
        
        if self.device_info['mps']:
            print(f"MPS 디바이스: Apple Silicon ({self.device_info['mps_memory_gb']} GB 통합 메모리)")
        
        print("\n⚙️  최적화 설정")
        print("=" * 50)
        batch_sizes = self.get_recommended_batch_sizes()
        recommended_hpo = self.get_recommended_hpo_method()
        
        print(f"권장 배치 크기: {batch_sizes['train']}")
        print(f"워커 수: {self.optimization_config['num_workers']}")
        print(f"혼합 정밀도: {self.optimization_config['mixed_precision']}")
        print(f"권장 HPO 방법: {recommended_hpo.upper()}")
        
        print("\n📊 HPO 최적화 정보")
        print("=" * 50)
        hpo_opts = self.get_hpo_optimization()
        for method, config in hpo_opts.items():
            status = "✅ 권장" if config.get('recommended') else "⚪ 가능"
            print(f"{status} {method.replace('_hpo', '').upper()}: 병렬 {config['max_parallel_trials']}개")
    
    def save_platform_info(self, filepath: str = "platform_info.json"):
        """플랫폼 정보를 JSON 파일로 저장"""
        platform_data = {
            'system_info': self.system_info,
            'device_info': self.device_info,
            'optimization_config': self.optimization_config,
            'recommended_hpo': self.get_recommended_hpo_method(),
            'recommended_batch_sizes': self.get_recommended_batch_sizes(),
            'hpo_optimization': self.get_hpo_optimization()
        }
        
        with open(filepath, 'w') as f:
            json.dump(platform_data, f, indent=2)
        
        print(f"📝 플랫폼 정보 저장: {filepath}")

if __name__ == "__main__":
    detector = PlatformDetector()
    detector.print_system_summary()
    detector.save_platform_info()
