#!/usr/bin/env python3
"""
Unified Experiment Runner
V2와 V3 실험 시스템을 통합 실행하는 시스템
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import concurrent.futures
import threading

# 기본 경로 설정
sys.path.append('/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5')

class UnifiedExperimentRunner:
    def __init__(self):
        self.base_dir = Path('/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5')
        self.logs_dir = self.base_dir / 'unified_dashboard' / 'logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 실행 스크립트 경로
        self.v2_1_script = self.base_dir / 'run_v2_1_only.sh'
        self.v2_2_script = self.base_dir / 'run_v2_2_only.sh'
        self.v3_script = self.base_dir / 'v3_experiments' / 'scripts' / 'run_v3_experiments.sh'
        
        # 실행 상태 추적
        self.execution_status = {
            'v2_1': {'status': 'pending', 'start_time': None, 'end_time': None, 'pid': None},
            'v2_2': {'status': 'pending', 'start_time': None, 'end_time': None, 'pid': None},
            'v3': {'status': 'pending', 'start_time': None, 'end_time': None, 'pid': None}
        }
    
    def check_script_existence(self):
        """실행 스크립트 존재 확인"""
        print("🔍 Checking experiment scripts...")
        
        scripts = {
            'V2_1': self.v2_1_script,
            'V2_2': self.v2_2_script,
            'V3': self.v3_script
        }
        
        missing_scripts = []
        for name, script_path in scripts.items():
            if script_path.exists():
                print(f"  ✅ {name}: {script_path}")
            else:
                print(f"  ❌ {name}: {script_path} (NOT FOUND)")
                missing_scripts.append(name)
        
        if missing_scripts:
            print(f"\n⚠️ Missing scripts: {', '.join(missing_scripts)}")
            return False
        
        print("✅ All scripts found!")
        return True
    
    def run_system(self, system_name, script_path, log_suffix=""):
        """개별 시스템 실행"""
        print(f"🚀 Starting {system_name} experiments...")
        
        # 상태 업데이트
        self.execution_status[system_name.lower()]['status'] = 'running'
        self.execution_status[system_name.lower()]['start_time'] = datetime.now()
        
        # 로그 파일 설정
        log_file = self.logs_dir / f"{system_name.lower()}_unified_run{log_suffix}.log"
        error_file = self.logs_dir / f"{system_name.lower()}_unified_error{log_suffix}.log"
        
        try:
            # 스크립트 실행
            with open(log_file, 'w') as log_f, open(error_file, 'w') as error_f:
                process = subprocess.Popen(
                    ['bash', str(script_path)],
                    stdout=log_f,
                    stderr=error_f,
                    cwd=str(self.base_dir)
                )
                
                # PID 저장
                self.execution_status[system_name.lower()]['pid'] = process.pid
                
                # 프로세스 대기
                return_code = process.wait()
                
                # 상태 업데이트
                self.execution_status[system_name.lower()]['end_time'] = datetime.now()
                
                if return_code == 0:
                    self.execution_status[system_name.lower()]['status'] = 'completed'
                    print(f"✅ {system_name} experiments completed successfully")
                else:
                    self.execution_status[system_name.lower()]['status'] = 'failed'
                    print(f"❌ {system_name} experiments failed with return code {return_code}")
                
                return return_code
                
        except Exception as e:
            self.execution_status[system_name.lower()]['status'] = 'failed'
            self.execution_status[system_name.lower()]['end_time'] = datetime.now()
            print(f"❌ {system_name} execution failed: {e}")
            return -1
    
    def run_sequential(self, systems=['v2_1', 'v2_2', 'v3']):
        """순차적 실행"""
        print("🔄 Starting sequential experiment execution...")
        print(f"📋 Systems to run: {', '.join(systems)}")
        
        start_time = datetime.now()
        results = {}
        
        for system in systems:
            if system == 'v2_1' and self.v2_1_script.exists():
                results['v2_1'] = self.run_system('V2_1', self.v2_1_script)
            elif system == 'v2_2' and self.v2_2_script.exists():
                results['v2_2'] = self.run_system('V2_2', self.v2_2_script)
            elif system == 'v3' and self.v3_script.exists():
                results['v3'] = self.run_system('V3', self.v3_script)
            else:
                print(f"⚠️ Skipping {system} - script not found")
                results[system] = -1
        
        end_time = datetime.now()
        total_time = end_time - start_time
        
        # 결과 요약
        self.print_execution_summary(results, total_time)
        
        return results
    
    def run_parallel(self, systems=['v2_1', 'v2_2', 'v3'], max_workers=2):
        """병렬 실행"""
        print("🚀 Starting parallel experiment execution...")
        print(f"📋 Systems to run: {', '.join(systems)}")
        print(f"👥 Max workers: {max_workers}")
        
        start_time = datetime.now()
        results = {}
        
        # 실행할 작업 준비
        tasks = []
        for system in systems:
            if system == 'v2_1' and self.v2_1_script.exists():
                tasks.append(('V2_1', self.v2_1_script))
            elif system == 'v2_2' and self.v2_2_script.exists():
                tasks.append(('V2_2', self.v2_2_script))
            elif system == 'v3' and self.v3_script.exists():
                tasks.append(('V3', self.v3_script))
        
        # 병렬 실행
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_system = {
                executor.submit(self.run_system, system_name, script_path, f"_parallel_{i}"): system_name
                for i, (system_name, script_path) in enumerate(tasks)
            }
            
            for future in concurrent.futures.as_completed(future_to_system):
                system_name = future_to_system[future]
                try:
                    return_code = future.result()
                    results[system_name.lower()] = return_code
                except Exception as e:
                    print(f"❌ {system_name} execution failed: {e}")
                    results[system_name.lower()] = -1
        
        end_time = datetime.now()
        total_time = end_time - start_time
        
        # 결과 요약
        self.print_execution_summary(results, total_time)
        
        return results
    
    def run_specific_experiments(self, experiment_configs):
        """특정 실험 설정으로 실행"""
        print("🎯 Running specific experiment configurations...")
        
        for config in experiment_configs:
            system = config.get('system')
            params = config.get('params', {})
            
            print(f"🔬 Running {system} with params: {params}")
            
            if system == 'v2_1':
                self.run_v2_1_with_params(params)
            elif system == 'v2_2':
                self.run_v2_2_with_params(params)
            elif system == 'v3':
                self.run_v3_with_params(params)
    
    def run_v2_1_with_params(self, params):
        """V2_1 파라미터로 실행"""
        # V2_1 특정 실험 실행 로직
        print(f"📊 Running V2_1 with custom parameters...")
        # 실제 구현에서는 params를 사용하여 설정 파일 생성 및 실행
        pass
    
    def run_v2_2_with_params(self, params):
        """V2_2 파라미터로 실행"""
        # V2_2 특정 실험 실행 로직
        print(f"📊 Running V2_2 with custom parameters...")
        # 실제 구현에서는 params를 사용하여 설정 파일 생성 및 실행
        pass
    
    def run_v3_with_params(self, params):
        """V3 파라미터로 실행"""
        # V3 특정 실험 실행 로직
        print(f"📊 Running V3 with custom parameters...")
        # 실제 구현에서는 params를 사용하여 설정 파일 생성 및 실행
        pass
    
    def print_execution_summary(self, results, total_time):
        """실행 요약 출력"""
        print("\n" + "="*80)
        print("🎯 Unified Experiment Execution Summary")
        print("="*80)
        print(f"⏱️  Total execution time: {total_time}")
        print()
        
        # 시스템별 상태
        for system, status_info in self.execution_status.items():
            status = status_info['status']
            start_time = status_info['start_time']
            end_time = status_info['end_time']
            
            if start_time and end_time:
                duration = end_time - start_time
                print(f"📊 {system.upper()}:")
                print(f"   Status: {self.get_status_emoji(status)} {status}")
                print(f"   Duration: {duration}")
                print(f"   Return Code: {results.get(system, 'N/A')}")
            else:
                print(f"📊 {system.upper()}: {self.get_status_emoji(status)} {status}")
            print()
        
        # 전체 결과
        successful = sum(1 for code in results.values() if code == 0)
        failed = sum(1 for code in results.values() if code != 0)
        
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {successful/(successful+failed)*100:.1f}%" if (successful+failed) > 0 else "N/A")
        print()
        
        # 로그 파일 위치
        print("📄 Log files:")
        for log_file in self.logs_dir.glob("*_unified_*.log"):
            print(f"   {log_file}")
    
    def get_status_emoji(self, status):
        """상태 이모지 반환"""
        emoji_map = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }
        return emoji_map.get(status, '❓')
    
    def monitor_execution(self, interval=10):
        """실행 모니터링"""
        print("🔄 Starting execution monitoring...")
        
        def monitor_loop():
            while True:
                # 실행 중인 시스템 확인
                running_systems = [
                    system for system, info in self.execution_status.items()
                    if info['status'] == 'running'
                ]
                
                if not running_systems:
                    print("📊 No systems currently running")
                    break
                
                print(f"🔄 Running systems: {', '.join(running_systems)}")
                
                # 각 시스템의 상태 출력
                for system in running_systems:
                    info = self.execution_status[system]
                    if info['start_time']:
                        duration = datetime.now() - info['start_time']
                        print(f"   {system.upper()}: {duration}")
                
                time.sleep(interval)
        
        # 모니터링 스레드 시작
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def save_execution_log(self, results, filename=None):
        """실행 로그 저장"""
        if filename is None:
            filename = f"unified_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'execution_status': self.execution_status,
            'results': results,
            'summary': {
                'total_systems': len(results),
                'successful': sum(1 for code in results.values() if code == 0),
                'failed': sum(1 for code in results.values() if code != 0)
            }
        }
        
        log_path = self.logs_dir / filename
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2, default=str)
        
        print(f"📄 Execution log saved to: {log_path}")
        return log_path


def main():
    parser = argparse.ArgumentParser(description='Unified Experiment Runner')
    parser.add_argument('--systems', nargs='+', default=['v2_1', 'v2_2', 'v3'],
                       choices=['v2_1', 'v2_2', 'v3'],
                       help='Systems to run')
    parser.add_argument('--parallel', action='store_true',
                       help='Run experiments in parallel')
    parser.add_argument('--max-workers', type=int, default=2,
                       help='Max workers for parallel execution')
    parser.add_argument('--check-scripts', action='store_true',
                       help='Check if experiment scripts exist')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor execution progress')
    parser.add_argument('--monitor-interval', type=int, default=10,
                       help='Monitor update interval in seconds')
    
    args = parser.parse_args()
    
    runner = UnifiedExperimentRunner()
    
    # 스크립트 존재 확인
    if args.check_scripts:
        runner.check_script_existence()
        return
    
    # 스크립트 존재 확인
    if not runner.check_script_existence():
        print("❌ Cannot proceed without required scripts")
        return
    
    # 모니터링 시작 (필요시)
    if args.monitor:
        runner.monitor_execution(args.monitor_interval)
    
    # 실험 실행
    if args.parallel:
        results = runner.run_parallel(args.systems, args.max_workers)
    else:
        results = runner.run_sequential(args.systems)
    
    # 실행 로그 저장
    runner.save_execution_log(results)
    
    print("\n🎉 Unified experiment execution completed!")


if __name__ == "__main__":
    main()
