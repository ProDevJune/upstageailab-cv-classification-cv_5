#!/usr/bin/env python3
"""
실험 모니터링 시스템
실행 중인 하이퍼파라미터 실험을 실시간으로 모니터링하고 시스템 리소스를 추적합니다.
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ExperimentMonitor:
    """실험 모니터링 시스템"""
    
    def __init__(self):
        self.monitoring = False
        self.config = {
            'cpu_threshold': 95.0,
            'memory_threshold': 90.0,
            'disk_threshold': 95.0,
            'gpu_memory_threshold': 95.0,
            'long_running_threshold': 7200,  # 2시간
            'check_interval': 30  # 30초마다 체크
        }
        self.system_alerts = []
        self.monitor_thread = None
        
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring:
            print("⚠️ 모니터링이 이미 실행 중입니다.")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ 실험 모니터링이 시작되었습니다.")
        
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("🛑 실험 모니터링이 중지되었습니다.")
        
    def _monitoring_loop(self):
        """모니터링 메인 루프"""
        while self.monitoring:
            try:
                self._check_system_resources()
                self._check_running_experiments()
                time.sleep(self.config['check_interval'])
            except Exception as e:
                self._log_event("monitor_error", f"모니터링 오류: {e}")
                
    def _check_system_resources(self):
        """시스템 리소스 체크"""
        # CPU 체크
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.config['cpu_threshold']:
            self._log_event("cpu_high", f"CPU 사용률 높음: {cpu_percent:.1f}%")
            
        # 메모리 체크
        memory = psutil.virtual_memory()
        if memory.percent > self.config['memory_threshold']:
            self._log_event("memory_high", f"메모리 사용률 높음: {memory.percent:.1f}%")
            
        # 디스크 체크
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > self.config['disk_threshold']:
            self._log_event("disk_high", f"디스크 사용률 높음: {disk_percent:.1f}%")
            
        # GPU 체크 (가능한 경우)
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    allocated = torch.cuda.memory_allocated(i) / torch.cuda.max_memory_allocated(i) * 100
                    if allocated > self.config['gpu_memory_threshold']:
                        self._log_event("gpu_memory_high", f"GPU {i} 메모리 사용률 높음: {allocated:.1f}%")
        except ImportError:
            pass
            
    def _check_running_experiments(self):
        """실행 중인 실험 프로세스 체크"""
        long_running_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['name'] in ['python', 'python3']:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    
                    # 실험 관련 프로세스 감지
                    if any(keyword in cmdline for keyword in ['gemini_main_v2.py', 'run_experiments.py', 'experiment_runner.py']):
                        # 실행 시간 체크
                        runtime = time.time() - proc.info['create_time']
                        
                        if runtime > self.config['long_running_threshold']:
                            long_running_processes.append({
                                'pid': proc.info['pid'],
                                'runtime_hours': runtime / 3600,
                                'cmdline': cmdline[:100] + "..." if len(cmdline) > 100 else cmdline
                            })
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        # 장시간 실행 프로세스 알림
        for proc in long_running_processes:
            self._log_event("long_running", f"장시간 실행 실험: PID {proc['pid']} ({proc['runtime_hours']:.1f}시간)")
            
    def _log_event(self, event_type: str, message: str):
        """이벤트 로깅"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert = {
            'timestamp': timestamp,
            'type': event_type,
            'message': message
        }
        
        self.system_alerts.append(alert)
        
        # 최근 100개만 유지
        if len(self.system_alerts) > 100:
            self.system_alerts = self.system_alerts[-100:]
            
        # 콘솔 출력
        print(f"⚠️ [{timestamp}] {message}")
        
    def get_monitoring_status(self) -> Dict[str, Any]:
        """현재 모니터링 상태 반환"""
        try:
            # 시스템 정보
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # GPU 정보
            gpu_info = {'available': False, 'count': 0}
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_info = {
                        'available': True,
                        'count': torch.cuda.device_count(),
                        'devices': []
                    }
                    for i in range(torch.cuda.device_count()):
                        gpu_info['devices'].append({
                            'id': i,
                            'name': torch.cuda.get_device_name(i),
                            'memory_allocated': torch.cuda.memory_allocated(i) / (1024**3),
                            'memory_total': torch.cuda.get_device_properties(i).total_memory / (1024**3)
                        })
            except ImportError:
                pass
                
            return {
                'monitoring_active': self.monitoring,
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': (disk.used / disk.total) * 100,
                    'disk_total_gb': disk.total / (1024**3),
                    'free_space_gb': disk.free / (1024**3)
                },
                'gpu': gpu_info,
                'alerts_count': len(self.system_alerts),
                'recent_alerts': self.system_alerts[-10:] if self.system_alerts else []
            }
            
        except Exception as e:
            self._log_event("status_error", f"상태 조회 오류: {e}")
            return {'error': str(e)}
    
    def print_status_report(self):
        """상태 리포트 출력"""
        status = self.get_monitoring_status()
        
        if 'error' in status:
            print(f"❌ 상태 조회 오류: {status['error']}")
            return
        
        print("\n🔍 실험 모니터링 상태 리포트")
        print("=" * 50)
        
        # 모니터링 상태
        if status['monitoring_active']:
            print("✅ 모니터링 활성화")
        else:
            print("⚠️ 모니터링 비활성화")
        
        # 시스템 상태
        sys_info = status['system']
        print(f"\n🖥️ 시스템 상태:")
        print(f"   CPU: {sys_info['cpu_percent']:.1f}%")
        print(f"   메모리: {sys_info['memory_percent']:.1f}%")
        print(f"   디스크: {sys_info['disk_percent']:.1f}% (여유: {sys_info['free_space_gb']:.1f}GB)")
        
        # GPU 상태
        gpu_info = status['gpu']
        if gpu_info['available']:
            print(f"   GPU: {gpu_info['count']}개 사용 가능")
            for device in gpu_info.get('devices', []):
                usage = (device['memory_allocated'] / device['memory_total']) * 100 if device['memory_total'] > 0 else 0
                print(f"     GPU {device['id']}: {device['name']} ({usage:.1f}% 사용)")
        else:
            print("   GPU: 사용 불가")
        
        # 경고 상태
        alert_count = status['alerts_count']
        if alert_count > 0:
            print(f"\n⚠️ 경고: {alert_count}개")
            recent_alerts = status['recent_alerts']
            for alert in recent_alerts:
                print(f"   • [{alert['timestamp']}] {alert['message']}")
        else:
            print("\n✅ 경고 없음")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="실험 모니터링 시스템")
    parser.add_argument('--start', action='store_true', help='모니터링 시작')
    parser.add_argument('--status', action='store_true', help='현재 상태 출력')
    parser.add_argument('--config', type=str, help='설정 파일 경로')
    
    args = parser.parse_args()
    
    monitor = ExperimentMonitor()
    
    if args.config:
        # 설정 업데이트
        try:
            import yaml
            with open(args.config, 'r') as f:
                config_update = yaml.safe_load(f)
            monitor.config.update(config_update)
            print(f"✅ 설정 업데이트: {args.config}")
        except Exception as e:
            print(f"⚠️ 설정 파일 로드 실패: {e}")
    
    if args.status:
        # 상태만 출력하고 종료
        monitor.print_status_report()
        return
    
    if args.start:
        # 모니터링 시작
        monitor.start_monitoring()
        try:
            print("🔍 모니터링 실행 중... (Ctrl+C로 중지)")
            while monitor.monitoring:
                time.sleep(5)
                # 주기적으로 상태 출력 (선택사항)
                if len(monitor.system_alerts) > 0:
                    # 새로운 경고가 있으면 상태 출력
                    pass
        except KeyboardInterrupt:
            print("\n🛑 사용자가 모니터링을 중지했습니다.")
        finally:
            monitor.stop_monitoring()
        return
    
    # 대화형 모드
    print("🔍 실험 모니터링 시스템")
    print("=" * 40)
    print("📋 옵션:")
    print("1. 모니터링 시작")
    print("2. 현재 상태 확인")
    print("3. 설정 확인")
    print("0. 종료")
    
    while True:
        try:
            choice = input("\n선택하세요 (0-3): ").strip()
            
            if choice == '0':
                print("👋 모니터링 시스템을 종료합니다.")
                monitor.stop_monitoring()
                break
            elif choice == '1':
                monitor.start_monitoring()
                print("🔍 모니터링이 시작되었습니다. 'Ctrl+C'로 중지할 수 있습니다.")
                try:
                    while monitor.monitoring:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 모니터링을 중지합니다.")
                    monitor.stop_monitoring()
            elif choice == '2':
                monitor.print_status_report()
            elif choice == '3':
                print("\n⚙️ 현재 설정:")
                for key, value in monitor.config.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ 잘못된 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n👋 사용자가 중단했습니다.")
            monitor.stop_monitoring()
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
