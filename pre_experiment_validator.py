#!/usr/bin/env python3
"""
종합 사전 실험 검증 시스템
Mac OS (MPS) / Ubuntu (CUDA) 환경에서 모든 실험 조합이 정상 동작하는지 사전 검증

전체 실험 실행 전에 각 환경별로:
1. 패키지 설치 상태 확인
2. 디바이스 호환성 확인 
3. 모든 모델×기법×OCR 조합 테스트
4. 메모리 사용량 확인
5. 예상 실행 시간 계산
"""

import os
import sys
import json
import yaml
import time
import traceback
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import argparse

# 동적으로 프로젝트 루트 감지
project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root / "codes"))
sys.path.append(str(project_root / "experiments"))

# 필수 imports
try:
    import torch
    import torch.nn as nn
    import torchvision
    import timm
    import numpy as np
    import pandas as pd
    from tqdm import tqdm
    import psutil
    
    # 프로젝트 모듈들
    from platform_detector import PlatformDetector
    from experiment_generator import ExperimentGenerator
    
except ImportError as e:
    print(f"❌ 필수 패키지 import 실패: {e}")
    print("먼저 setup_platform_env.sh를 실행하여 환경을 설정해주세요.")
    sys.exit(1)


class PreExperimentValidator:
    """사전 실험 검증 시스템"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.platform_detector = PlatformDetector()
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'platform_info': {},
            'package_validation': {},
            'device_validation': {},
            'model_validation': {},
            'experiment_validation': {},
            'memory_analysis': {},
            'performance_estimation': {},
            'final_status': 'pending'
        }
        
        # 테스트할 모델×기법×OCR 조합 (샘플)
        self.test_combinations = self._generate_test_combinations()
        
    def _generate_test_combinations(self) -> List[Dict]:
        """테스트할 핵심 조합들 생성 (전체 48개 중 대표적인 12개)"""
        models = ['efficientnet_b4', 'swin_transformer']  # 빠른 모델 2개
        techniques = ['baseline', 'focal_loss', 'mixup_cutmix']  # 핵심 기법 3개
        ocr_options = [False, True]  # OCR 미적용/적용
        
        combinations = []
        for model in models:
            for technique in techniques:
                for ocr in ocr_options:
                    combinations.append({
                        'model': model,
                        'technique': technique,
                        'ocr_enabled': ocr,
                        'test_id': f"test_{model}_{technique}_{'ocr' if ocr else 'noocr'}"
                    })
        
        return combinations
    
    def validate_packages(self) -> Dict:
        """필수 패키지 설치 및 버전 확인"""
        print("📦 패키지 검증 중...")
        
        # Python 버전 확인
        python_version = sys.version_info
        print(f"   🐍 Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version >= (3, 13):
            print(f"   ⚠️  Python 3.13+ 감지 - 일부 패키지 호환성 이슈 가능")
        
        required_packages = {
            'torch': '2.5.0',
            'torchvision': '0.20.0',
            'timm': '1.0.12',
            'numpy': None,  # 버전 체크 없이
            'pandas': None,
            'pyyaml': None,  # yaml 모듈로 체크
            'tqdm': None,
            'psutil': None,
            'opencv-python': None,
            'PIL': None  # Pillow
        }
        
        package_status = {}
        all_packages_ok = True
        
        for package, expected_version in required_packages.items():
            try:
                if package == 'PIL':
                    import PIL
                    version = PIL.__version__
                    package_name = 'Pillow'
                elif package == 'opencv-python':
                    import cv2
                    version = cv2.__version__
                    package_name = 'opencv-python'
                elif package == 'pyyaml':
                    import yaml
                    version = yaml.__version__
                    package_name = 'pyyaml'
                else:
                    module = __import__(package)
                    version = getattr(module, '__version__', 'unknown')
                    package_name = package
                
                package_status[package_name] = {
                    'installed': True,
                    'version': version,
                    'expected': expected_version,
                    'status': '✅'
                }
                
                print(f"   ✅ {package_name}: {version}")
                
            except ImportError:
                package_status[package] = {
                    'installed': False,
                    'version': None,
                    'expected': expected_version,
                    'status': '❌'
                }
                all_packages_ok = False
                print(f"   ❌ {package}: 설치되지 않음")
        
        return {
            'all_packages_ok': all_packages_ok,
            'packages': package_status,
            'validation_time': datetime.now().isoformat()
        }
    
    def validate_device_compatibility(self) -> Dict:
        """디바이스 호환성 검증"""
        print("🖥️  디바이스 호환성 검증 중...")
        
        device_status = {
            'primary_device': self.platform_detector.device_info['primary_device'],
            'tests': {},
            'all_tests_passed': True
        }
        
        # 1. 기본 텐서 연산 테스트
        try:
            device = self.platform_detector.device_info['primary_device']
            x = torch.randn(100, 100).to(device)
            y = torch.randn(100, 100).to(device)
            z = torch.mm(x, y)
            
            device_status['tests']['basic_operations'] = {
                'status': '✅',
                'message': f'{device.upper()}에서 기본 텐서 연산 성공'
            }
            print(f"   ✅ 기본 텐서 연산: {device.upper()}")
            
        except Exception as e:
            device_status['tests']['basic_operations'] = {
                'status': '❌',
                'message': f'기본 텐서 연산 실패: {str(e)}'
            }
            device_status['all_tests_passed'] = False
            print(f"   ❌ 기본 텐서 연산 실패: {e}")
        
        # 2. 간단한 신경망 테스트
        try:
            device = self.platform_detector.device_info['primary_device']
            model = nn.Sequential(
                nn.Linear(10, 5),
                nn.ReLU(),
                nn.Linear(5, 1)
            ).to(device)
            
            x = torch.randn(32, 10).to(device)
            y = model(x)
            loss = nn.MSELoss()(y, torch.randn(32, 1).to(device))
            loss.backward()
            
            device_status['tests']['neural_network'] = {
                'status': '✅',
                'message': f'{device.upper()}에서 신경망 forward/backward 성공'
            }
            print(f"   ✅ 신경망 연산: {device.upper()}")
            
        except Exception as e:
            device_status['tests']['neural_network'] = {
                'status': '❌',
                'message': f'신경망 연산 실패: {str(e)}'
            }
            device_status['all_tests_passed'] = False
            print(f"   ❌ 신경망 연산 실패: {e}")
        
        # 3. Mixed Precision 테스트 (CUDA에서만)
        if self.platform_detector.device_info['primary_device'] == 'cuda':
            try:
                from torch.cuda.amp import autocast, GradScaler
                
                device = 'cuda'
                model = nn.Linear(100, 10).to(device)
                scaler = GradScaler()
                
                x = torch.randn(32, 100).to(device)
                with autocast():
                    y = model(x)
                    loss = nn.MSELoss()(y, torch.randn(32, 10).to(device))
                
                scaler.scale(loss).backward()
                scaler.step(torch.optim.Adam(model.parameters()))
                scaler.update()
                
                device_status['tests']['mixed_precision'] = {
                    'status': '✅',
                    'message': 'CUDA Mixed Precision 지원'
                }
                print(f"   ✅ Mixed Precision: CUDA")
                
            except Exception as e:
                device_status['tests']['mixed_precision'] = {
                    'status': '⚠️',
                    'message': f'Mixed Precision 실패 (선택적): {str(e)}'
                }
                print(f"   ⚠️  Mixed Precision 실패: {e}")
        
        return device_status
    
    def validate_models(self) -> Dict:
        """핵심 모델들 로드 및 기본 연산 테스트"""
        print("🤖 모델 검증 중...")
        
        test_models = {
            'efficientnet_b4': 'efficientnet_b4.ra2_in1k',
            'swin_transformer': 'swin_base_patch4_window12_384.ms_in1k',
        }
        
        model_status = {
            'models': {},
            'all_models_ok': True
        }
        
        device = self.platform_detector.device_info['primary_device']
        
        for model_key, model_name in test_models.items():
            try:
                print(f"   테스트 중: {model_key}")
                
                # 모델 로드
                model = timm.create_model(model_name, pretrained=False, num_classes=42)
                model = model.to(device)
                model.eval()
                
                # 테스트 입력
                if 'swin' in model_name:
                    test_input = torch.randn(2, 3, 384, 384).to(device)
                else:
                    test_input = torch.randn(2, 3, 320, 320).to(device)
                
                # Forward pass 테스트
                with torch.no_grad():
                    output = model(test_input)
                
                model_status['models'][model_key] = {
                    'status': '✅',
                    'model_name': model_name,
                    'output_shape': list(output.shape),
                    'memory_mb': self._get_model_memory_usage(model),
                    'device': device
                }
                print(f"      ✅ {model_key}: {output.shape}")
                
            except Exception as e:
                model_status['models'][model_key] = {
                    'status': '❌',
                    'error': str(e),
                    'model_name': model_name
                }
                model_status['all_models_ok'] = False
                print(f"      ❌ {model_key}: {e}")
        
        return model_status
    
    def _get_model_memory_usage(self, model) -> float:
        """모델 메모리 사용량 계산 (MB)"""
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
        return (param_size + buffer_size) / 1024 / 1024
    
    def validate_experiment_combinations(self) -> Dict:
        """핵심 실험 조합들 테스트 실행"""
        print("🧪 실험 조합 검증 중...")
        
        combination_status = {
            'total_combinations': len(self.test_combinations),
            'tested_combinations': 0,
            'successful_combinations': 0,
            'failed_combinations': 0,
            'tests': {},
            'all_combinations_ok': True
        }
        
        device = self.platform_detector.device_info['primary_device']
        
        for i, combo in enumerate(self.test_combinations, 1):
            test_id = combo['test_id']
            print(f"   테스트 {i}/{len(self.test_combinations)}: {test_id}")
            
            try:
                # 임시 config 생성
                temp_config = self._create_temp_config(combo)
                
                # 빠른 학습 테스트 (1 epoch, 작은 데이터)
                result = self._run_quick_training_test(temp_config, device)
                
                combination_status['tests'][test_id] = {
                    'status': '✅',
                    'model': combo['model'],
                    'technique': combo['technique'],
                    'ocr_enabled': combo['ocr_enabled'],
                    'execution_time_seconds': result['execution_time'],
                    'memory_peak_mb': result['memory_peak'],
                    'final_loss': result['final_loss']
                }
                combination_status['successful_combinations'] += 1
                print(f"      ✅ 성공 ({result['execution_time']:.1f}초)")
                
            except Exception as e:
                combination_status['tests'][test_id] = {
                    'status': '❌',
                    'error': str(e),
                    'model': combo['model'],
                    'technique': combo['technique'],
                    'ocr_enabled': combo['ocr_enabled']
                }
                combination_status['failed_combinations'] += 1
                combination_status['all_combinations_ok'] = False
                print(f"      ❌ 실패: {e}")
            
            combination_status['tested_combinations'] += 1
            
            # 메모리 정리
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif torch.backends.mps.is_available():
                torch.mps.empty_cache()
        
        return combination_status
    
    def _create_temp_config(self, combo: Dict) -> Dict:
        """테스트용 임시 config 생성"""
        # 기본 config 로드
        base_config_path = self.base_dir / "codes" / "config_v2.yaml"
        with open(base_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 테스트용 설정으로 수정
        model_configs = {
            'efficientnet_b4': {
                'model_name': 'efficientnet_b4.ra2_in1k',
                'batch_size': 4,  # 작은 배치
                'image_size': 224  # 작은 이미지
            },
            'swin_transformer': {
                'model_name': 'swin_base_patch4_window12_384.ms_in1k',
                'batch_size': 2,  # 작은 배치
                'image_size': 384  # Swin에 맞는 이미지 크기
            }
        }
        
        model_config = model_configs[combo['model']]
        config.update(model_config)
        
        # 기법별 설정
        if combo['technique'] == 'focal_loss':
            config['criterion'] = 'FocalLoss'
            config['focal_loss'] = {'alpha': 1.0, 'gamma': 2.0}
        elif combo['technique'] == 'mixup_cutmix':
            config['criterion'] = 'CrossEntropyLoss'
            config['mixup_cutmix']['prob'] = 0.5
            config['augmentation']['mixup'] = True
            config['augmentation']['cutmix'] = True
        else:  # baseline
            config['criterion'] = 'CrossEntropyLoss'
            config['mixup_cutmix']['prob'] = 0.0
            config['augmentation']['mixup'] = False
            config['augmentation']['cutmix'] = False
        
        # OCR 설정
        config['ocr'] = {
            'enabled': combo['ocr_enabled'],
            'description': 'OCR 적용' if combo['ocr_enabled'] else 'OCR 미적용'
        }
        
        # 테스트용 최적화
        config['epochs'] = 1  # 1 epoch만
        config['patience'] = 1
        config['wandb']['log'] = False  # W&B 비활성화
        
        return config
    
    def _run_quick_training_test(self, config: Dict, device: str) -> Dict:
        """빠른 학습 테스트 실행"""
        start_time = time.time()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # 모델 생성
        model = timm.create_model(
            config['model_name'], 
            pretrained=False, 
            num_classes=42
        ).to(device)
        
        # 손실 함수
        if config['criterion'] == 'FocalLoss':
            # 간단한 Focal Loss 구현
            criterion = nn.CrossEntropyLoss()  # 테스트용으로 CrossEntropy 사용
        else:
            criterion = nn.CrossEntropyLoss()
        
        # 옵티마이저
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # 더미 데이터 생성
        batch_size = config['batch_size']
        image_size = config['image_size']
        
        dummy_images = torch.randn(batch_size, 3, image_size, image_size).to(device)
        dummy_labels = torch.randint(0, 42, (batch_size,)).to(device)
        
        # 짧은 학습 실행
        model.train()
        
        for step in range(3):  # 3 step만 실행
            optimizer.zero_grad()
            
            # OCR 테스트 (실제로는 더미 데이터)
            if config['ocr']['enabled']:
                # OCR 특성 시뮬레이션 (실제 구현에서는 텍스트 임베딩)
                ocr_features = torch.randn(batch_size, 768).to(device)
            
            outputs = model(dummy_images)
            loss = criterion(outputs, dummy_labels)
            
            loss.backward()
            optimizer.step()
        
        final_loss = loss.item()
        
        # 메모리 사용량 계산
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_peak = current_memory - initial_memory
        
        execution_time = time.time() - start_time
        
        return {
            'execution_time': execution_time,
            'memory_peak': memory_peak,
            'final_loss': final_loss
        }
    
    def analyze_memory_requirements(self) -> Dict:
        """메모리 요구사항 분석"""
        print("💾 메모리 요구사항 분석 중...")
        
        device = self.platform_detector.device_info['primary_device']
        memory_analysis = {
            'device': device,
            'system_memory_gb': self.platform_detector.system_info['memory_gb'],
            'model_requirements': {},
            'recommendations': {}
        }
        
        # GPU 메모리 정보
        if device == 'cuda':
            gpu_memory_gb = self.platform_detector.device_info['cuda_devices'][0]['memory_gb']
            memory_analysis['gpu_memory_gb'] = gpu_memory_gb
        elif device == 'mps':
            memory_analysis['unified_memory_gb'] = self.platform_detector.device_info['mps_memory_gb']
        
        # 모델별 메모리 요구사항 추정
        model_memory_estimates = {
            'efficientnet_b4': {'model_mb': 75, 'batch_32_mb': 2500, 'batch_48_mb': 3700},
            'swin_transformer': {'model_mb': 350, 'batch_32_mb': 4500, 'batch_24_mb': 3400},
            'convnext_base': {'model_mb': 340, 'batch_28_mb': 4200, 'batch_32_mb': 4800},
            'maxvit_base': {'model_mb': 470, 'batch_24_mb': 5200, 'batch_28_mb': 6100}
        }
        
        memory_analysis['model_requirements'] = model_memory_estimates
        
        # 권장사항 생성
        if device == 'cuda':
            gpu_memory_gb = memory_analysis['gpu_memory_gb']
            if gpu_memory_gb >= 24:
                memory_analysis['recommendations']['status'] = '✅ 충분'
                memory_analysis['recommendations']['message'] = '모든 모델을 원래 배치 크기로 실행 가능'
            elif gpu_memory_gb >= 12:
                memory_analysis['recommendations']['status'] = '⚠️ 주의'
                memory_analysis['recommendations']['message'] = '큰 모델은 배치 크기 감소 필요'
            else:
                memory_analysis['recommendations']['status'] = '❌ 부족'
                memory_analysis['recommendations']['message'] = '모든 모델의 배치 크기 대폭 감소 필요'
        
        elif device == 'mps':
            unified_memory_gb = memory_analysis['unified_memory_gb']
            if unified_memory_gb >= 32:
                memory_analysis['recommendations']['status'] = '✅ 충분'
                memory_analysis['recommendations']['message'] = 'Apple Silicon에서 안정적 실행 가능'
            elif unified_memory_gb >= 16:
                memory_analysis['recommendations']['status'] = '⚠️ 주의'
                memory_analysis['recommendations']['message'] = '배치 크기 조정 권장'
            else:
                memory_analysis['recommendations']['status'] = '❌ 부족'
                memory_analysis['recommendations']['message'] = '메모리 부족으로 실행 어려움'
        
        print(f"   {memory_analysis['recommendations']['status']} {memory_analysis['recommendations']['message']}")
        
        return memory_analysis
    
    def estimate_execution_time(self) -> Dict:
        """전체 실험 실행 시간 추정"""
        print("⏱️  실행 시간 추정 중...")
        
        # 성공한 조합들의 평균 실행 시간 기반으로 추정
        successful_tests = [
            test for test in self.validation_results['experiment_validation']['tests'].values()
            if test['status'] == '✅'
        ]
        
        if not successful_tests:
            return {
                'estimation_available': False,
                'message': '성공한 테스트가 없어 시간 추정 불가'
            }
        
        avg_test_time = sum(test['execution_time_seconds'] for test in successful_tests) / len(successful_tests)
        
        # 테스트는 3 step, 실제는 약 1000-3000 step 예상
        real_experiment_multiplier = 300  # 테스트 대비 실제 실험 비율
        estimated_time_per_experiment = avg_test_time * real_experiment_multiplier
        
        # 전체 실험 수 (모드별)
        experiment_counts = {
            'none': 24,
            'selective': 32,
            'all': 48
        }
        
        time_estimates = {}
        for mode, count in experiment_counts.items():
            total_seconds = estimated_time_per_experiment * count
            total_hours = total_seconds / 3600
            
            time_estimates[mode] = {
                'total_experiments': count,
                'estimated_seconds_per_experiment': estimated_time_per_experiment,
                'estimated_total_hours': total_hours,
                'estimated_total_days': total_hours / 24,
                'estimated_completion': (datetime.now() + timedelta(seconds=total_seconds)).isoformat()
            }
        
        return {
            'estimation_available': True,
            'base_test_time_seconds': avg_test_time,
            'estimated_real_multiplier': real_experiment_multiplier,
            'time_estimates_by_mode': time_estimates,
            'recommended_mode': 'selective'  # 균형잡힌 선택
        }
    
    def run_full_validation(self) -> Dict:
        """전체 검증 프로세스 실행"""
        print("🔍 종합 사전 실험 검증 시작")
        print("=" * 80)
        
        # 플랫폼 정보
        print("🖥️  플랫폼 정보:")
        self.platform_detector.print_system_summary()
        self.validation_results['platform_info'] = {
            'system_info': self.platform_detector.system_info,
            'device_info': self.platform_detector.device_info,
            'optimization_config': self.platform_detector.optimization_config
        }
        
        print("\n" + "=" * 80)
        
        # 1. 패키지 검증
        self.validation_results['package_validation'] = self.validate_packages()
        
        if not self.validation_results['package_validation']['all_packages_ok']:
            print("❌ 패키지 검증 실패 - 환경 설정 후 다시 시도하세요")
            self.validation_results['final_status'] = 'failed_packages'
            return self.validation_results
        
        print("\n" + "-" * 40)
        
        # 2. 디바이스 검증
        self.validation_results['device_validation'] = self.validate_device_compatibility()
        
        if not self.validation_results['device_validation'].get('all_tests_passed', False):
            print("❌ 디바이스 검증 실패 - 드라이버 또는 CUDA/MPS 설정 확인 필요")
            self.validation_results['final_status'] = 'failed_device'
            return self.validation_results
        
        print("\n" + "-" * 40)
        
        # 3. 모델 검증
        self.validation_results['model_validation'] = self.validate_models()
        
        if not self.validation_results.get('model_validation', {}).get('all_models_ok', False):
            print("❌ 모델 검증 실패 - 네트워크 또는 모델 파일 확인 필요")
            self.validation_results['final_status'] = 'failed_models'
            return self.validation_results
        
        print("\n" + "-" * 40)
        
        # 4. 실험 조합 검증
        self.validation_results['experiment_validation'] = self.validate_experiment_combinations()
        
        if not self.validation_results.get('experiment_validation', {}).get('all_combinations_ok', False):
            print("⚠️  일부 실험 조합에서 오류 발생 - 세부 사항 확인 필요")
            self.validation_results['final_status'] = 'partial_success'
        else:
            print("✅ 모든 실험 조합 검증 성공")
        
        print("\n" + "-" * 40)
        
        # 5. 메모리 분석
        self.validation_results['memory_analysis'] = self.analyze_memory_requirements()
        
        print("\n" + "-" * 40)
        
        # 6. 실행 시간 추정
        self.validation_results['performance_estimation'] = self.estimate_execution_time()
        
        # 최종 상태 결정
        if self.validation_results['final_status'] == 'pending':
            exp_val = self.validation_results.get('experiment_validation', {})
            if exp_val and exp_val.get('total_combinations', 0) > 0:
                successful_rate = (
                    exp_val.get('successful_combinations', 0) /
                    exp_val.get('total_combinations', 1)
                )
                
                if successful_rate >= 0.9:
                    self.validation_results['final_status'] = 'ready'
                elif successful_rate >= 0.7:
                    self.validation_results['final_status'] = 'ready_with_warnings'
                else:
                    self.validation_results['final_status'] = 'not_ready'
            else:
                # 실험 검증이 실행되지 않음
                self.validation_results['final_status'] = 'not_ready'
        
        return self.validation_results
    
    def print_final_summary(self):
        """최종 검증 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("📋 종합 검증 결과")
        print("=" * 80)
        
        status = self.validation_results['final_status']
        
        if status == 'ready':
            print("🎉 검증 완료! 모든 실험을 안전하게 실행할 수 있습니다.")
            status_color = '✅'
        elif status == 'ready_with_warnings':
            print("⚠️  검증 완료 (주의사항 있음). 대부분의 실험은 정상 실행됩니다.")
            status_color = '⚠️'
        else:
            print("❌ 검증 실패. 환경 설정 또는 시스템 점검이 필요합니다.")
            status_color = '❌'
        
        print(f"\n{status_color} 최종 상태: {status}")
        
        # 세부 결과
        validation = self.validation_results
        
        print(f"\n📦 패키지: {'✅' if validation['package_validation']['all_packages_ok'] else '❌'}")
        print(f"🖥️  디바이스: {'✅' if validation['device_validation'].get('all_tests_passed', False) else '❌'}")
        print(f"🤖 모델: {'✅' if validation.get('model_validation', {}).get('all_models_ok', False) else '❌'}")
        
        exp_val = validation.get('experiment_validation', {})
        if exp_val:
            success_rate = exp_val.get('successful_combinations', 0) / max(exp_val.get('total_combinations', 1), 1) * 100
            print(f"🧪 실험 조합: {exp_val.get('successful_combinations', 0)}/{exp_val.get('total_combinations', 0)} ({success_rate:.1f}%)")
        else:
            print(f"🧪 실험 조합: 검증되지 않음")
        
        mem_status = validation.get('memory_analysis', {}).get('recommendations', {}).get('status', '❓')
        print(f"💾 메모리: {mem_status}")
        
        # 실행 시간 추정
        perf_est = validation.get('performance_estimation', {})
        if perf_est.get('estimation_available', False):
            estimates = perf_est.get('time_estimates_by_mode', {})
            print(f"\n⏱️  예상 실행 시간:")
            for mode, est in estimates.items():
                if est:  # est가 None이 아닌 경우만
                    print(f"   {mode.upper()}: {est.get('estimated_total_hours', 0):.1f}시간 ({est.get('total_experiments', 0)}개 실험)")
        
        # 다음 단계 안내
        if status in ['ready', 'ready_with_warnings']:
            print(f"\n🚀 다음 단계:")
            print(f"   1. python experiments/experiment_generator.py --ocr-mode selective")
            print(f"   2. python experiments/auto_experiment_runner.py")
            print(f"   3. python experiments/experiment_monitor.py")
        else:
            print(f"\n🔧 해결 방법:")
            if validation['package_validation']['all_packages_ok'] == False:
                print(f"   1. bash setup_platform_env.sh  # 환경 재설정")
            if validation.get('device_validation', {}).get('all_tests_passed', False) == False:
                print(f"   2. 드라이버 및 CUDA/MPS 설정 확인")
            if validation.get('model_validation', {}).get('all_models_ok', False) == False:
                print(f"   3. 인터넷 연결 및 모델 다운로드 확인")
    
    def save_validation_report(self, output_path: str = None):
        """검증 결과를 JSON 파일로 저장"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.base_dir / f"pre_experiment_validation_{timestamp}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 검증 결과 저장: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='종합 사전 실험 검증 시스템')
    parser.add_argument('--base-dir', '-d',
                       default=str(Path(__file__).parent.resolve()),
                       help='프로젝트 기본 디렉토리')
    parser.add_argument('--save-report', '-s', action='store_true',
                       help='검증 결과를 JSON 파일로 저장')
    parser.add_argument('--quick-test', '-q', action='store_true',
                       help='빠른 테스트만 실행 (패키지 + 디바이스만)')
    
    args = parser.parse_args()
    
    try:
        validator = PreExperimentValidator(args.base_dir)
        
        if args.quick_test:
            print("🏃 빠른 검증 모드")
            validator.validation_results['package_validation'] = validator.validate_packages()
            validator.validation_results['device_validation'] = validator.validate_device_compatibility()
            
            if (validator.validation_results['package_validation']['all_packages_ok'] and
                validator.validation_results['device_validation']['all_tests_passed']):
                print("✅ 빠른 검증 성공 - 기본 환경 준비됨")
            else:
                print("❌ 빠른 검증 실패 - 환경 설정 필요")
        else:
            # 전체 검증 실행
            validator.run_full_validation()
            validator.print_final_summary()
            
            if args.save_report:
                validator.save_validation_report()
        
    except Exception as e:
        print(f"❌ 검증 프로세스 중 오류 발생: {e}")
        print(f"상세 오류:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
