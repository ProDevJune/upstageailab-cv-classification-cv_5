"""
플랫폼별 최적화된 설정 관리 모듈
Mac MPS / Ubuntu CUDA에 맞춘 자동 설정 생성
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import os
import copy

class EnhancedConfigManager:
    """플랫폼별 최적화된 설정 관리"""
    
    def __init__(self, platform_detector):
        self.detector = platform_detector
        self.base_configs = self._load_base_configs()
        self.practice_dir = Path("codes/practice")
        self.practice_dir.mkdir(exist_ok=True)
    
    def _load_base_configs(self) -> Dict:
        """기본 설정 템플릿들 로드"""
        return {
            'cuda_optimized': {
                'mixed_precision': True,
                'pin_memory': True,
                'num_workers': 8,
                'persistent_workers': True,
                'prefetch_factor': 2,
                'compile_model': True,
                'memory_strategy': 'performance'
            },
            'mps_optimized': {
                'mixed_precision': False,  # MPS FP16 제한적 지원
                'pin_memory': False,
                'num_workers': 4,
                'persistent_workers': False,
                'memory_efficient_attention': True,
                'reduce_memory_usage': True,
                'memory_strategy': 'conservative'
            },
            'cpu_optimized': {
                'mixed_precision': False,
                'pin_memory': False,
                'num_workers': 'auto',  # CPU 코어 수에 따라 자동
                'memory_efficient': True,
                'use_channels_last': True,
                'memory_strategy': 'minimal'
            }
        }
    
    def _load_original_config(self) -> Dict:
        """기존 config.yaml 로드"""
        config_path = Path("codes/config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # 기본 설정 제공
            return {
                'model_name': 'resnet50.tv2_in1k',
                'pretrained': True,
                'fine_tuning': 'full',
                'criterion': 'CrossEntropyLoss',
                'optimizer_name': 'AdamW',
                'lr': 0.0001,
                'weight_decay': 0.00001,
                'scheduler_name': 'CosineAnnealingLR',
                'random_seed': 256,
                'n_folds': 0,
                'val_split_ratio': 0.15,
                'stratify': True,
                'image_size': 224,
                'norm_mean': [0.5, 0.5, 0.5],
                'norm_std': [0.5, 0.5, 0.5],
                'epochs': 1000,
                'patience': 20,
                'wandb': {'project': 'upstage-img-clf', 'log': True},
                'data_dir': '/data/ephemeral/home/upstageailab-cv-classification-cv_5/data'
            }
    
    def generate_platform_config(self, experiment_type: str = 'quick', config_name: str = None) -> Dict[str, Any]:
        """플랫폼별 최적화된 설정 생성"""
        
        # 기존 config.yaml을 기반으로 시작
        config = copy.deepcopy(self._load_original_config())
        
        # 플랫폼 정보 추가
        config.update({
            'experiment_type': experiment_type,
            'platform_info': {
                'os': self.detector.system_info['os'],
                'device': self.detector.device_info['primary_device'],
                'cpu_count': self.detector.system_info['cpu_count'],
                'memory_gb': self.detector.system_info['memory_gb']
            }
        })
        
        # 플랫폼별 최적화 설정 적용
        config.update(self.detector.optimization_config)
        
        # 배치 크기 설정
        batch_sizes = self.detector.get_recommended_batch_sizes(config.get('batch_size', 32))
        config['batch_size'] = batch_sizes['train']
        config['val_batch_size'] = batch_sizes.get('val', batch_sizes['train'])
        
        # 디바이스별 세부 설정
        device = self.detector.device_info['primary_device']
        if device == 'cuda':
            config.update(self.base_configs['cuda_optimized'])
        elif device == 'mps':
            config.update(self.base_configs['mps_optimized'])
        else:
            config.update(self.base_configs['cpu_optimized'])
            config['num_workers'] = self.detector.system_info['cpu_count']
        
        # 실험 타입별 설정
        if experiment_type == 'quick':
            config.update({
                'epochs': 50,
                'patience': 10,
                'max_experiments': 20,
                'early_stopping_min_delta': 1e-4
            })
        elif experiment_type == 'full':
            config.update({
                'epochs': 1000,
                'patience': 20,
                'max_experiments': 100,
                'early_stopping_min_delta': 1e-6
            })
        elif experiment_type == 'targeted':
            config.update({
                'epochs': 200,
                'patience': 15,
                'max_experiments': 50,
                'early_stopping_min_delta': 1e-5
            })
        
        # HPO 설정 추가
        config['hpo_settings'] = self.detector.get_hpo_optimization()
        config['recommended_hpo_method'] = self.detector.get_recommended_hpo_method()
        
        # 설정 이름 생성
        if config_name is None:
            device_name = device.upper()
            config_name = f"platform_{device_name}_{experiment_type}_auto.yaml"
        
        config['config_name'] = config_name
        
        return config
    
    def generate_hpo_experiment_configs(self, experiment_type: str = 'quick', max_configs: int = 20) -> List[str]:
        """HPO용 실험 설정들 자동 생성"""
        
        # 하이퍼파라미터 공간 정의
        hyperparameter_space = {
            'models': ['resnet34.tv_in1k', 'resnet50.tv2_in1k', 'efficientnet_b3.ra2_in1k'],
            'image_sizes': [224, 320] if self.detector.device_info['primary_device'] == 'mps' else [224, 320, 384],
            'learning_rates': [0.001, 0.0001, 0.00001],
            'augmentation_levels': ['minimal', 'moderate', 'strong'],
            'TTA': [True, False]
        }
        
        # 플랫폼별 제한 적용
        if self.detector.device_info['primary_device'] == 'cpu':
            hyperparameter_space['models'] = ['resnet34.tv_in1k']  # 가벼운 모델만
            hyperparameter_space['image_sizes'] = [224]  # 작은 이미지만
        elif self.detector.device_info['primary_device'] == 'mps':
            hyperparameter_space['image_sizes'] = [224, 320]  # MPS 메모리 제한
        
        config_files = []
        
        # 조합 생성 (제한된 수만)
        import itertools
        import random
        
        # 모든 조합 생성
        keys, values = zip(*hyperparameter_space.items())
        all_combinations = list(itertools.product(*values))
        
        # 랜덤 샘플링으로 제한
        selected_combinations = random.sample(
            all_combinations, 
            min(max_configs, len(all_combinations))
        )
        
        for i, combination in enumerate(selected_combinations):
            # 기본 설정 로드
            config = self.generate_platform_config(experiment_type)
            
            # 하이퍼파라미터 적용
            config['model_name'] = combination[0]
            config['image_size'] = combination[1]
            config['lr'] = combination[2]
            config['augmentation_level'] = combination[3]
            config['TTA'] = combination[4]
            
            # 증강 설정 적용
            config['augmentation'] = self._get_augmentation_config(combination[3])
            
            # 실험 ID 생성
            experiment_id = f"exp_{experiment_type}_{i+1:03d}"
            config['experiment_id'] = experiment_id
            
            # 파일명 생성
            filename = f"{experiment_id}.yaml"
            config_path = self.practice_dir / filename
            
            # 설정 저장
            self.save_config(config, str(config_path))
            config_files.append(str(config_path))
        
        return config_files
    
    def _get_augmentation_config(self, level: str) -> Dict:
        """증강 레벨에 따른 설정"""
        if level == 'minimal':
            return {
                'eda': True,
                'dilation': False,
                'erosion': False,
                'mixup': False,
                'cutmix': False
            }
        elif level == 'moderate':
            return {
                'eda': True,
                'dilation': True,
                'erosion': False,
                'mixup': False,
                'cutmix': False
            }
        else:  # strong
            return {
                'eda': True,
                'dilation': True,
                'erosion': True,
                'mixup': True,
                'cutmix': False
            }
    
    def save_config(self, config: Dict, filepath: str):
        """설정을 YAML 파일로 저장"""
        config_path = Path(filepath)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        return str(config_path)
    
    def save_platform_config(self, config: Dict, filename: str = None):
        """플랫폼별 설정을 저장"""
        if filename is None:
            device = self.detector.device_info['primary_device']
            filename = f"config_platform_{device}.yaml"
        
        config_path = self.practice_dir / filename
        return self.save_config(config, str(config_path))
    
    def load_config(self, filepath: str) -> Dict:
        """YAML 설정 파일 로드"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def get_platform_summary(self) -> Dict:
        """플랫폼 요약 정보"""
        return {
            'platform': f"{self.detector.system_info['os']} + {self.detector.device_info['primary_device'].upper()}",
            'recommended_hpo': self.detector.get_recommended_hpo_method(),
            'max_parallel_trials': self.detector.get_hpo_optimization()[f"{self.detector.get_recommended_hpo_method()}_hpo"]['max_parallel_trials'],
            'recommended_batch_size': self.detector.get_recommended_batch_sizes()['train'],
            'memory_strategy': self.detector.optimization_config.get('memory_strategy', 'balanced')
        }

if __name__ == "__main__":
    from platform_detector import PlatformDetector
    
    detector = PlatformDetector()
    config_manager = EnhancedConfigManager(detector)
    
    # 플랫폼별 기본 설정 생성
    config = config_manager.generate_platform_config('quick')
    saved_path = config_manager.save_platform_config(config)
    
    print(f"✅ 플랫폼별 설정 생성 완료: {saved_path}")
    print("\n📊 플랫폼 요약:")
    summary = config_manager.get_platform_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
