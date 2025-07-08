#!/usr/bin/env python3
"""
실험 모니터링 대시보드
실행 중인 실험을 실시간으로 모니터링하고 진행 상황을 표시합니다.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psutil
import torch
import subprocess


class ExperimentMonitor:
    """실험 모니터링 클래스"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.queue_file = self.base_dir / "experiments" / "experiment_queue.json"
        self.logs_dir = self.base_dir / "experiments" / "logs"
        
    def _load_queue_data(self) -> Optional[Dict]:
        """실험 큐 데이터 로드"""
        if not self.queue_file.exists():
            return None
        
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  큐 파일 로드 실패: {e}")
            return None
    
    def _get_system_info(self) -> Dict:
        """시스템 정보 수집"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        system_info = {
            'cpu_percent': cpu_percent,
            'memory_total_gb': memory.total / (1024**3),
            'memory_used_gb': memory.used / (1024**3),
            'memory_percent': memory.percent
        }
        
        # GPU 정보 (CUDA 사용 가능한 경우)
        if torch.cuda.is_available():
            device = torch.cuda.current_device()
            gpu_props = torch.cuda.get_device_properties(device)
            total_memory = gpu_props.total_memory / (1024**3)
            allocated_memory = torch.cuda.memory_allocated(device) / (1024**3)
            
            system_info.update({
                'gpu_available': True,
                'gpu_name': gpu_props.name,
                'gpu_total_memory_gb': total_memory,
                'gpu_allocated_memory_gb': allocated_memory,
                'gpu_memory_percent': (allocated_memory / total_memory) * 100
            })
        else:
            system_info['gpu_available'] = False
        
        return system_info
    
    def _check_running_processes(self) -> List[Dict]:
        """실행 중인 Python 프로세스 확인"""
        running_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                    cmdline = proc.info['cmdline']
                    if cmdline and 'gemini_main_v2.py' in ' '.join(cmdline):
                        running_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': ' '.join(cmdline),
                            'start_time': datetime.fromtimestamp(proc.info['create_time']),
                            'running_time': datetime.now() - datetime.fromtimestamp(proc.info['create_time'])
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return running_processes
    
    def _get_experiment_stats(self, queue_data: Dict) -> Dict:
        """실험 통계 계산"""
        if not queue_data:
            return {}
        
        experiments = queue_data.get('experiments', [])
        
        stats = {
            'total': len(experiments),
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0
        }
        
        for exp in experiments:
            status = exp.get('status', 'pending')
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def _get_recent_completions(self, limit: int = 5) -> List[Dict]:
        """최근 완료된 실험들 반환"""
        if not self.logs_dir.exists():
            return []
        
        recent_logs = []
        for log_file in self.logs_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('success', False):
                    local_results = data.get('local_results', {})
                    recent_logs.append({
                        'experiment_id': data['experiment_id'],
                        'model': data['model'],
                        'technique': data['technique'],
                        'f1_score': local_results.get('validation_f1', 0.0),
                        'timestamp': data.get('timestamp', ''),
                        'training_time': local_results.get('training_time_minutes', 0.0)
                    })
            except Exception:
                continue
        
        # 시간순 정렬
        recent_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        return recent_logs[:limit]
    
    def _estimate_completion_time(self, queue_data: Dict, stats: Dict) -> str:
        """예상 완료 시간 계산"""
        if not queue_data or stats['pending'] == 0:
            return "완료됨"
        
        # 평균 실험 시간 계산 (큐 데이터에서)
        experiments = queue_data.get('experiments', [])
        total_estimated_time = 0
        pending_count = 0
        
        for exp in experiments:
            if exp.get('status') == 'pending':
                total_estimated_time += exp.get('estimated_time_minutes', 90)
                pending_count += 1
        
        if pending_count == 0:
            return "완료됨"
        
        avg_time_per_experiment = total_estimated_time / pending_count
        remaining_time_minutes = avg_time_per_experiment * pending_count
        
        eta = datetime.now() + timedelta(minutes=remaining_time_minutes)
        return f"{eta.strftime('%Y-%m-%d %H:%M:%S')} (약 {remaining_time_minutes/60:.1f}시간 후)"
    
    def _get_current_experiment_info(self, queue_data: Dict) -> Optional[Dict]:
        """현재 실행 중인 실험 정보"""
        if not queue_data:
            return None
        
        experiments = queue_data.get('experiments', [])
        
        for exp in experiments:
            if exp.get('status') == 'running':
                return {
                    'experiment_id': exp['experiment_id'],
                    'model_name': exp['model_name'],
                    'technique_name': exp['technique_name'],
                    'description': exp['description'],
                    'started_at': exp.get('started_at'),
                    'estimated_time_minutes': exp.get('estimated_time_minutes', 90)
                }
        
        return None
    
    def _calculate_progress_percentage(self, stats: Dict) -> float:
        """전체 진행률 계산"""
        total = stats['total']
        if total == 0:
            return 100.0
        
        completed = stats['completed'] + stats['failed']
        return (completed / total) * 100
    
    def _clear_screen(self):
        """화면 클리어"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self):
        """헤더 출력"""
        print("🔬 자동 실험 시스템 모니터링 대시보드")
        print("=" * 80)
        print(f"📅 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def _print_system_status(self, system_info: Dict):
        """시스템 상태 출력"""
        print("🖥️  시스템 상태")
        print("-" * 40)
        print(f"CPU 사용률: {system_info['cpu_percent']:.1f}%")
        print(f"메모리 사용률: {system_info['memory_percent']:.1f}% "
              f"({system_info['memory_used_gb']:.1f}GB / {system_info['memory_total_gb']:.1f}GB)")
        
        if system_info['gpu_available']:
            print(f"GPU: {system_info['gpu_name']}")
            print(f"GPU 메모리: {system_info['gpu_memory_percent']:.1f}% "
                  f"({system_info['gpu_allocated_memory_gb']:.1f}GB / {system_info['gpu_total_memory_gb']:.1f}GB)")
        else:
            print("GPU: 사용 불가")
        print()
    
    def _print_experiment_progress(self, stats: Dict, progress: float):
        """실험 진행 상황 출력"""
        print("📊 실험 진행 상황")
        print("-" * 40)
        print(f"전체 진행률: {progress:.1f}%")
        
        # 진행률 바 출력
        bar_length = 50
        filled_length = int(bar_length * progress / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"[{bar}] {progress:.1f}%")
        print()
        
        print(f"총 실험 수: {stats['total']}개")
        print(f"✅ 완료: {stats['completed']}개")
        print(f"❌ 실패: {stats['failed']}개")
        print(f"🔄 실행 중: {stats['running']}개")
        print(f"⏳ 대기 중: {stats['pending']}개")
        print()
    
    def _print_current_experiment(self, current_exp: Optional[Dict], running_processes: List[Dict]):
        """현재 실행 중인 실험 정보 출력"""
        print("🚀 현재 실험")
        print("-" * 40)
        
        if current_exp:
            print(f"실험 ID: {current_exp['experiment_id']}")
            print(f"모델: {current_exp['model_name']}")
            print(f"기법: {current_exp['technique_name']}")
            print(f"설명: {current_exp['description']}")
            
            if current_exp['started_at']:
                start_time = datetime.fromisoformat(current_exp['started_at'].replace('Z', '+00:00'))
                elapsed = datetime.now() - start_time.replace(tzinfo=None)
                estimated_total = timedelta(minutes=current_exp['estimated_time_minutes'])
                
                print(f"시작 시간: {start_time.strftime('%H:%M:%S')}")
                print(f"경과 시간: {str(elapsed).split('.')[0]}")
                print(f"예상 완료: {(start_time.replace(tzinfo=None) + estimated_total).strftime('%H:%M:%S')}")
        else:
            print("현재 실행 중인 실험이 없습니다.")
        
        # 실행 중인 프로세스 정보
        if running_processes:
            print(f"실행 중인 프로세스: {len(running_processes)}개")
            for proc in running_processes:
                elapsed = str(proc['running_time']).split('.')[0]
                print(f"  PID {proc['pid']}: 실행시간 {elapsed}")
        
        print()
    
    def _print_recent_completions(self, recent: List[Dict]):
        """최근 완료된 실험들 출력"""
        print("📋 최근 완료된 실험 (TOP 5)")
        print("-" * 40)
        
        if not recent:
            print("완료된 실험이 없습니다.")
        else:
            for i, exp in enumerate(recent, 1):
                print(f"{i}. {exp['experiment_id']}")
                print(f"   {exp['model']} + {exp['technique']}")
                print(f"   F1: {exp['f1_score']:.4f}, 시간: {exp['training_time']:.1f}분")
        print()
    
    def _print_eta(self, eta: str):
        """예상 완료 시간 출력"""
        print("⏰ 예상 완료 시간")
        print("-" * 40)
        print(f"{eta}")
        print()
    
    def _print_controls(self):
        """조작 방법 출력"""
        print("⌨️  조작 방법")
        print("-" * 40)
        print("Ctrl+C: 모니터링 종료")
        print("자동 갱신: 5초마다")
        print()
    
    def start_monitoring(self, refresh_interval: int = 5):
        """모니터링 시작"""
        print("🚀 실험 모니터링을 시작합니다...")
        print("Ctrl+C를 눌러 종료할 수 있습니다.")
        time.sleep(2)
        
        try:
            while True:
                # 화면 클리어
                self._clear_screen()
                
                # 데이터 수집
                queue_data = self._load_queue_data()
                system_info = self._get_system_info()
                running_processes = self._check_running_processes()
                stats = self._get_experiment_stats(queue_data)
                progress = self._calculate_progress_percentage(stats)
                current_exp = self._get_current_experiment_info(queue_data)
                recent_completions = self._get_recent_completions()
                eta = self._estimate_completion_time(queue_data, stats)
                
                # 정보 출력
                self._print_header()
                self._print_system_status(system_info)
                self._print_experiment_progress(stats, progress)
                self._print_current_experiment(current_exp, running_processes)
                self._print_recent_completions(recent_completions)
                self._print_eta(eta)
                self._print_controls()
                
                # 상태 확인
                if stats['pending'] == 0 and stats['running'] == 0:
                    print("🎉 모든 실험이 완료되었습니다!")
                    break
                
                # 다음 갱신까지 대기
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n⛔ 모니터링이 종료되었습니다.")
        except Exception as e:
            print(f"\n\n❌ 모니터링 중 오류 발생: {e}")


def main():
    parser = argparse.ArgumentParser(description='실험 모니터링 대시보드')
    parser.add_argument('--base-dir', '-d',
                       default='',
                       help='프로젝트 기본 디렉토리')
    parser.add_argument('--interval', '-i', type=int, default=5,
                       help='갱신 간격 (초, 기본값: 5)')
    parser.add_argument('--once', action='store_true',
                       help='한 번만 상태 확인하고 종료')
    
    args = parser.parse_args()
    
    try:
        # 모니터 초기화
        monitor = ExperimentMonitor(args.base_dir)
        
        if args.once:
            # 한 번만 실행
            queue_data = monitor._load_queue_data()
            system_info = monitor._get_system_info()
            stats = monitor._get_experiment_stats(queue_data)
            progress = monitor._calculate_progress_percentage(stats)
            
            print("🔬 실험 시스템 현재 상태")
            print("=" * 50)
            print(f"전체 진행률: {progress:.1f}%")
            print(f"완료: {stats['completed']}개, 실패: {stats['failed']}개")
            print(f"실행 중: {stats['running']}개, 대기: {stats['pending']}개")
            print(f"CPU: {system_info['cpu_percent']:.1f}%, RAM: {system_info['memory_percent']:.1f}%")
            
            if system_info['gpu_available']:
                print(f"GPU: {system_info['gpu_memory_percent']:.1f}%")
        else:
            # 연속 모니터링
            monitor.start_monitoring(args.interval)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
