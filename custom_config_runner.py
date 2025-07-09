#!/usr/bin/env python3
"""
Custom Config Sequential Runner
사용자가 직접 만든 여러 개의 YAML 파일들을 순차적으로 실행하는 시스템
"""

import os
import yaml
import argparse
import subprocess
import json
from pathlib import Path
import time
from datetime import datetime

class CustomConfigRunner:
    def __init__(self, config_dir="my_configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 실행 로그 디렉토리
        self.logs_dir = self.config_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # 결과 디렉토리
        self.results_dir = self.config_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    def scan_configs(self, pattern="*.yaml"):
        """사용자 정의 config 파일들 스캔"""
        config_files = list(self.config_dir.glob(pattern))
        config_files = [f for f in config_files if f.name not in ['execution_order.txt', 'results.json']]
        
        print(f"🔍 Found {len(config_files)} config files:")
        for i, config_file in enumerate(config_files, 1):
            print(f"  {i}. {config_file.name}")
        
        return config_files
    
    def detect_experiment_type(self, config_file):
        """Config 내용을 분석해서 실험 타입 자동 감지"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # v2_1 특징 감지
            v2_1_indicators = [
                'convnext' in config.get('model_name', '').lower(),
                config.get('scheduler_name') == 'CosineAnnealingWarmupRestarts',
                config.get('epochs', 0) > 5000,
                config.get('lr', 0) < 0.0001
            ]
            
            # v2_2 특징 감지  
            v2_2_indicators = [
                config.get('criterion') == 'FocalLoss',
                config.get('two_stage', False),
                'online_aug' in config and any(config['online_aug'].values()),
                'dynamic_augmentation' in config and config['dynamic_augmentation'].get('enabled', False)
            ]
            
            if sum(v2_1_indicators) >= 2:
                return 'v2_1'
            elif sum(v2_2_indicators) >= 1:
                return 'v2_2'
            else:
                # 기본적으로 v2_2 (더 범용적)
                return 'v2_2'
                
        except Exception as e:
            print(f"⚠️  Error detecting type for {config_file}: {e}")
            return 'v2_2'
    
    def get_execution_order(self):
        """실행 순서 파일 로드 (있으면)"""
        order_file = self.config_dir / "execution_order.txt"
        if order_file.exists():
            with open(order_file, 'r') as f:
                order = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return order
        return None
    
    def create_execution_order_template(self, config_files):
        """실행 순서 템플릿 생성"""
        order_file = self.config_dir / "execution_order.txt"
        
        with open(order_file, 'w') as f:
            f.write("# 실행 순서 파일\n")
            f.write("# 원하는 순서대로 config 파일명을 나열하세요\n")
            f.write("# '#'으로 시작하는 줄은 주석입니다\n")
            f.write("# 파일명만 적으면 됩니다 (확장자 포함)\n\n")
            
            for config_file in config_files:
                f.write(f"{config_file.name}\n")
        
        print(f"📝 Created execution order template: {order_file}")
        print("   Edit this file to customize execution order")
        
    def run_single_experiment(self, config_file, exp_type):
        """단일 실험 실행"""
        print(f"\n🔬 Starting experiment: {config_file.name}")
        print(f"   Type: {exp_type}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 적절한 main 스크립트 선택
        if exp_type == 'v2_1':
            main_script = "codes/gemini_main_v2_1_style.py"
        else:
            main_script = "codes/gemini_main_v2_enhanced.py"
        
        # 로그 파일 설정
        log_file = self.logs_dir / f"{config_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # 실행 명령 구성
        cmd = ['python', main_script, '--config', str(config_file)]
        
        # 2-stage 학습 감지 (config2 파일이 있는지 확인)
        config2_file = self.config_dir / f"{config_file.stem}_stage2.yaml"
        if config2_file.exists():
            cmd.extend(['--config2', str(config2_file)])
            print(f"   🎯 2-stage learning detected: {config2_file.name}")
        
        try:
            # 실험 실행
            start_time = time.time()
            
            with open(log_file, 'w') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )\n                
                # 실시간 출력 및 로그 기록
                for line in process.stdout:
                    print(line, end='')
                    f.write(line)
                    f.flush()
                
                process.wait()
            
            end_time = time.time()
            duration = end_time - start_time
            
            if process.returncode == 0:
                print(f"✅ Experiment completed successfully")
                print(f"   Duration: {duration/3600:.2f} hours")
                status = "success"
            else:
                print(f"❌ Experiment failed with return code: {process.returncode}")
                status = "failed"
                
        except Exception as e:
            print(f"❌ Error running experiment: {e}")
            status = "error"
            duration = 0
        
        # 결과 기록
        result = {
            'config_file': config_file.name,
            'experiment_type': exp_type,
            'status': status,
            'duration_hours': duration / 3600,
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'log_file': str(log_file)
        }
        
        return result
    
    def run_all_experiments(self, config_files, respect_order=True):
        """모든 실험 순차 실행"""
        print(f"🚀 Starting sequential execution of {len(config_files)} experiments")
        print("=" * 60)
        
        # 실행 순서 결정
        if respect_order:
            order = self.get_execution_order()
            if order:
                print("📋 Using custom execution order")
                # 순서에 따라 config 파일 정렬
                ordered_configs = []
                for filename in order:
                    config_file = self.config_dir / filename
                    if config_file.exists():
                        ordered_configs.append(config_file)
                    else:
                        print(f"⚠️  Warning: {filename} not found")
                config_files = ordered_configs
        
        results = []
        failed_experiments = []
        
        for i, config_file in enumerate(config_files, 1):
            print(f"\n📊 Progress: {i}/{len(config_files)}")
            
            # 실험 타입 감지
            exp_type = self.detect_experiment_type(config_file)
            
            # 실험 실행
            result = self.run_single_experiment(config_file, exp_type)
            results.append(result)
            
            if result['status'] != 'success':
                failed_experiments.append(config_file.name)
            
            # 결과 저장 (실시간)
            self.save_results(results)
            
            print("-" * 60)
        
        # 최종 결과 출력
        print(f"\n🎉 All experiments completed!")
        print(f"   Total: {len(results)}")
        print(f"   Successful: {len([r for r in results if r['status'] == 'success'])}")
        print(f"   Failed: {len(failed_experiments)}")
        
        if failed_experiments:
            print(f"\n❌ Failed experiments:")
            for exp in failed_experiments:
                print(f"   - {exp}")
        
        return results
    
    def save_results(self, results):
        """결과 저장"""
        results_file = self.results_dir / "experiment_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def create_sample_configs(self):
        """샘플 config 파일들 생성"""
        print("📝 Creating sample config files...")
        
        # 샘플 1: V2_1 스타일
        sample_v2_1 = {
            'model_name': 'convnextv2_base.fcmae_ft_in22k_in1k_384',
            'criterion': 'CrossEntropyLoss',
            'optimizer_name': 'AdamW',
            'lr': 0.0001,
            'scheduler_name': 'CosineAnnealingWarmupRestarts',
            'scheduler_params': {
                'T_max': 5000,
                'max_lr': 0.0001,
                'min_lr': 0.00001,
                'warmup_steps': 5
            },
            'epochs': 8000,
            'batch_size': 32,
            'image_size': 384,
            'random_seed': 256,
            'n_folds': 0,
            'val_split_ratio': 0.15,
            'online_augmentation': True,
            'augmentation': {
                'eda': True,
                'dilation': True,
                'erosion': True
            },
            'dynamic_augmentation': {'enabled': False},
            'val_TTA': True,
            'test_TTA': True,
            'mixed_precision': True,
            'patience': 10,
            'norm_mean': [0.5, 0.5, 0.5],
            'norm_std': [0.5, 0.5, 0.5],
            'timm': {'activation': None},
            'wandb': {'project': 'my-experiments', 'log': True},
            'data_dir': './data',
            'train_data': 'train0705a.csv'
        }
        
        # 샘플 2: V2_2 스타일 (Mixup)
        sample_v2_2_mixup = {
            'model_name': 'resnet50.tv2_in1k',
            'criterion': 'FocalLoss',
            'optimizer_name': 'AdamW',
            'lr': 0.001,
            'scheduler_name': 'CosineAnnealingLR',
            'scheduler_params': {'T_max': 50, 'max_lr': 0.001, 'min_lr': 0.00001},
            'epochs': 100,
            'batch_size': 32,
            'image_size': 384,
            'random_seed': 256,
            'n_folds': 0,
            'val_split_ratio': 0.15,
            'online_augmentation': True,
            'augmentation': {'eda': True},
            'online_aug': {'mixup': True, 'cutmix': False},
            'dynamic_augmentation': {'enabled': False},
            'val_TTA': False,
            'test_TTA': False,
            'mixed_precision': True,
            'patience': 10,
            'norm_mean': [0.5, 0.5, 0.5],
            'norm_std': [0.5, 0.5, 0.5],
            'timm': {'activation': None},
            'wandb': {'project': 'my-experiments', 'log': True},
            'data_dir': './data',
            'train_data': 'train0705a.csv'
        }
        
        # 샘플 3: V2_2 스타일 (2-stage)
        sample_v2_2_2stage = {
            'model_name': 'efficientnet_b4.ra2_in1k',
            'criterion': 'CrossEntropyLoss',
            'optimizer_name': 'AdamW',
            'lr': 0.001,
            'scheduler_name': 'CosineAnnealingLR',
            'scheduler_params': {'T_max': 30, 'max_lr': 0.001, 'min_lr': 0.0001},
            'epochs': 30,
            'batch_size': 64,
            'image_size': 384,
            'random_seed': 256,
            'n_folds': 0,
            'val_split_ratio': 0.15,
            'two_stage': True,
            'online_augmentation': True,
            'augmentation': {'eda': False, 'easiest': True},
            'dynamic_augmentation': {'enabled': False},
            'val_TTA': False,
            'test_TTA': True,
            'mixed_precision': True,
            'patience': 5,
            'norm_mean': [0.5, 0.5, 0.5],
            'norm_std': [0.5, 0.5, 0.5],
            'timm': {'activation': None},
            'wandb': {'project': 'my-experiments', 'log': True},
            'data_dir': './data',
            'train_data': 'train0705a.csv'
        }
        
        # Stage 2 config for 2-stage learning
        sample_stage2 = {
            'model_name': 'efficientnet_b4.ra2_in1k',
            'criterion': 'FocalLoss',
            'optimizer_name': 'AdamW',
            'lr': 0.0001,
            'scheduler_name': 'CosineAnnealingLR',
            'scheduler_params': {'T_max': 20, 'max_lr': 0.0001, 'min_lr': 0.00001},
            'epochs': 20,
            'batch_size': 32,
            'image_size': 384,
            'random_seed': 256,
            'n_folds': 0,
            'val_split_ratio': 0.15,
            'two_stage': False,
            'online_augmentation': True,
            'augmentation': {'eda': False, 'middle': True},
            'online_aug': {'mixup': True, 'cutmix': False},
            'dynamic_augmentation': {'enabled': False},
            'val_TTA': True,
            'test_TTA': True,
            'mixed_precision': True,
            'patience': 5,
            'norm_mean': [0.5, 0.5, 0.5],
            'norm_std': [0.5, 0.5, 0.5],
            'timm': {'activation': None},
            'wandb': {'project': 'my-experiments', 'log': True},
            'data_dir': './data',
            'train_data': 'train0705a.csv'
        }
        
        # 파일 저장
        configs = [
            ('sample_v2_1_convnext.yaml', sample_v2_1),
            ('sample_v2_2_resnet_mixup.yaml', sample_v2_2_mixup),
            ('sample_v2_2_efficient_2stage.yaml', sample_v2_2_2stage),
            ('sample_v2_2_efficient_2stage_stage2.yaml', sample_stage2)
        ]
        
        for filename, config in configs:
            config_file = self.config_dir / filename
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            print(f"   ✅ Created: {filename}")
        
        print(f"\n📂 Sample configs created in: {self.config_dir}")
        print("   Edit these files to customize your experiments!")

def main():
    parser = argparse.ArgumentParser(description="Custom Config Sequential Runner")
    parser.add_argument('--config-dir', default='my_configs', help='Directory containing config files')
    parser.add_argument('--pattern', default='*.yaml', help='Pattern to match config files')
    parser.add_argument('--create-samples', action='store_true', help='Create sample config files')
    parser.add_argument('--create-order', action='store_true', help='Create execution order template')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be executed')
    parser.add_argument('--single', help='Run single config file')
    
    args = parser.parse_args()
    
    runner = CustomConfigRunner(args.config_dir)
    
    if args.create_samples:
        runner.create_sample_configs()
        return
    
    if args.single:
        config_file = Path(args.config_dir) / args.single
        if config_file.exists():
            exp_type = runner.detect_experiment_type(config_file)
            runner.run_single_experiment(config_file, exp_type)
        else:
            print(f"❌ Config file not found: {config_file}")
        return
    
    # Config 파일 스캔
    config_files = runner.scan_configs(args.pattern)
    
    if not config_files:
        print("❌ No config files found")
        print("💡 Use --create-samples to create sample config files")
        return
    
    if args.create_order:
        runner.create_execution_order_template(config_files)
        return
    
    if args.dry_run:
        print("\n🔍 Dry run - would execute:")
        for i, config_file in enumerate(config_files, 1):
            exp_type = runner.detect_experiment_type(config_file)
            print(f"   {i}. {config_file.name} ({exp_type})")
        return
    
    # 실제 실행
    results = runner.run_all_experiments(config_files)
    print(f"\n📊 Results saved to: {runner.results_dir / 'experiment_results.json'}")

if __name__ == "__main__":
    main()
