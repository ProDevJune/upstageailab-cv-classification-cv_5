#!/usr/bin/env python3
"""
V2_1 & V2_2 Enhanced Experiment Monitor
실시간 실험 모니터링 및 결과 분석
"""

import os
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
from datetime import datetime
import subprocess

class V2ExperimentMonitor:
    def __init__(self, experiment_dir="v2_experiments"):
        self.experiment_dir = Path(experiment_dir)
        self.results_dir = Path("data/submissions")
        self.experiment_list = self.load_experiment_list()
        
    def load_experiment_list(self):
        """실험 리스트 로드"""
        list_file = self.experiment_dir / "experiment_list.json"
        if list_file.exists():
            with open(list_file) as f:
                return json.load(f)
        return []
    
    def monitor_realtime(self, refresh_interval=30):
        """실시간 실험 모니터링"""
        print("🔍 V2_1 & V2_2 Real-time Experiment Monitor")
        print("=" * 50)
        
        while True:
            try:
                self.display_status()
                time.sleep(refresh_interval)
                os.system('clear' if os.name == 'posix' else 'cls')
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
    
    def display_status(self):
        """현재 실험 상태 표시"""
        print(f"📊 Experiment Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        status_summary = self.get_experiment_status()
        
        # 전체 통계
        total = len(self.experiment_list)
        completed = status_summary['completed']
        running = status_summary['running']
        pending = status_summary['pending']
        failed = status_summary['failed']
        
        print(f"📈 Total Experiments: {total}")
        print(f"✅ Completed: {completed} ({completed/total*100:.1f}%)")
        print(f"🔄 Running: {running}")
        print(f"⏳ Pending: {pending}")
        print(f"❌ Failed: {failed}")
        print()
        
        # 타입별 통계
        print("📊 By Experiment Type:")
        type_stats = status_summary['by_type']
        for exp_type, stats in type_stats.items():
            print(f"  {exp_type.upper()}: {stats['completed']}/{stats['total']} completed")
        print()
        
        # 현재 실행 중인 실험
        if status_summary['current_experiment']:
            print(f"🔬 Currently Running: {status_summary['current_experiment']}")
        
        # 최근 완료된 실험
        recent_completed = status_summary['recent_completed'][:3]
        if recent_completed:
            print("🏆 Recently Completed:")
            for exp in recent_completed:
                print(f"  - {exp}")
        
        print("\n" + "=" * 60)
    
    def get_experiment_status(self):
        """실험 상태 정보 수집"""
        completed_experiments = []
        running_experiments = []
        failed_experiments = []
        
        # 완료된 실험 (submission 파일 존재)
        for submission_dir in self.results_dir.glob("*"):
            if submission_dir.is_dir():
                exp_name = submission_dir.name
                # submission CSV 파일이 있으면 완료
                csv_files = list(submission_dir.glob("*.csv"))
                if csv_files:
                    completed_experiments.append(exp_name)
        
        # 실행 중인 실험 (프로세스 확인)
        try:
            result = subprocess.run(['pgrep', '-f', 'gemini_main'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # 실행 중인 프로세스가 있음
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                for line in ps_result.stdout.split('\n'):
                    if 'gemini_main' in line and 'python' in line:
                        # config 파일명에서 실험명 추출
                        for part in line.split():
                            if '.yaml' in part and 'config' in part:
                                config_name = Path(part).stem
                                if config_name not in completed_experiments:
                                    running_experiments.append(config_name)
        except:
            pass
        
        # 타입별 통계
        type_stats = {'v2_1': {'total': 0, 'completed': 0},
                     'v2_2': {'total': 0, 'completed': 0},
                     'cv': {'total': 0, 'completed': 0}}
        
        for exp in self.experiment_list:
            exp_type = exp['type']
            type_stats[exp_type]['total'] += 1
            if exp['name'] in completed_experiments:
                type_stats[exp_type]['completed'] += 1
        
        total_experiments = len(self.experiment_list)
        pending = total_experiments - len(completed_experiments) - len(running_experiments)
        
        return {
            'completed': len(completed_experiments),
            'running': len(running_experiments),
            'pending': max(0, pending),
            'failed': 0,  # 실패 감지 로직 필요시 추가
            'by_type': type_stats,
            'current_experiment': running_experiments[0] if running_experiments else None,
            'recent_completed': sorted(completed_experiments, reverse=True)
        }
    
    def analyze_results(self, save_plots=True):
        """실험 결과 분석"""
        print("📊 Analyzing V2_1 & V2_2 Experiment Results")
        print("=" * 50)
        
        results_data = self.collect_results()
        
        if not results_data:
            print("❌ No experiment results found")
            return
        
        df = pd.DataFrame(results_data)
        
        # 기본 통계
        print(f"📈 Total analyzed experiments: {len(df)}")
        print(f"🏆 Best F1 Score: {df['f1_score'].max():.4f}")
        print(f"📊 Average F1 Score: {df['f1_score'].mean():.4f}")
        print()
        
        # 타입별 성능 비교
        print("🔬 Performance by Experiment Type:")
        type_performance = df.groupby('type')['f1_score'].agg(['count', 'mean', 'max']).round(4)
        print(type_performance)
        print()
        
        # 모델별 성능 비교
        if 'model' in df.columns:
            print("🏗️ Performance by Model:")
            model_performance = df.groupby('model')['f1_score'].agg(['count', 'mean', 'max']).round(4)
            print(model_performance)
            print()
        
        # 시각화
        if save_plots:
            self.create_analysis_plots(df)
        
        # 베스트 실험들
        print("🥇 Top 5 Experiments:")
        top_experiments = df.nlargest(5, 'f1_score')[['name', 'type', 'f1_score']]
        for idx, row in top_experiments.iterrows():
            print(f"  {row['f1_score']:.4f} - {row['name']} ({row['type']})")
    
    def collect_results(self):
        """실험 결과 수집"""
        results = []
        
        for submission_dir in self.results_dir.glob("*"):
            if not submission_dir.is_dir():
                continue
                
            exp_name = submission_dir.name
            
            # 실험 메타데이터 찾기
            exp_meta = None
            for exp in self.experiment_list:
                if exp['name'] in exp_name:
                    exp_meta = exp
                    break
            
            if not exp_meta:
                continue
            
            # F1 스코어 추출 (로그 파일이나 결과 파일에서)
            f1_score = self.extract_f1_score(submission_dir)
            
            if f1_score is not None:
                result = {
                    'name': exp_name,
                    'type': exp_meta['type'],
                    'f1_score': f1_score,
                }
                
                # 모델명 추출
                if 'model_name' in exp_meta['overrides']:
                    model_name = exp_meta['overrides']['model_name']
                    result['model'] = model_name.split('.')[0]  # 간단한 이름만
                
                results.append(result)
        
        return results
    
    def extract_f1_score(self, submission_dir):
        """F1 스코어 추출"""
        # 여러 소스에서 F1 스코어 찾기
        
        # 1. 로그 파일에서 찾기
        log_files = list(submission_dir.glob("*.log"))
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    # "Validation F1-score: 0.xxxx" 패턴 찾기
                    import re
                    match = re.search(r'Validation F1-score:\s*([0-9]+\.?[0-9]*)', content)
                    if match:
                        return float(match.group(1))
            except:
                continue
        
        # 2. 결과 JSON 파일에서 찾기 (있다면)
        json_files = list(submission_dir.glob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'f1_score' in data:
                        return float(data['f1_score'])
            except:
                continue
        
        # 3. 기본값 (임의의 값, 실제로는 더 정교한 추출 필요)
        return None
    
    def create_analysis_plots(self, df):
        """분석 플롯 생성"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 타입별 성능 분포
        sns.boxplot(data=df, x='type', y='f1_score', ax=axes[0,0])
        axes[0,0].set_title('Performance Distribution by Experiment Type')
        axes[0,0].set_ylabel('F1 Score')
        
        # 모델별 성능 (모델 정보가 있는 경우)
        if 'model' in df.columns:
            sns.boxplot(data=df, x='model', y='f1_score', ax=axes[0,1])
            axes[0,1].set_title('Performance Distribution by Model')
            axes[0,1].set_ylabel('F1 Score')
            axes[0,1].tick_params(axis='x', rotation=45)
        
        # 시간순 성능 추이
        df_sorted = df.sort_values('name')  # 이름으로 정렬 (시간순 가정)
        axes[1,0].plot(range(len(df_sorted)), df_sorted['f1_score'], 'o-')
        axes[1,0].set_title('Performance Trend Over Time')
        axes[1,0].set_xlabel('Experiment Order')
        axes[1,0].set_ylabel('F1 Score')
        
        # 성능 히스토그램
        axes[1,1].hist(df['f1_score'], bins=20, alpha=0.7)
        axes[1,1].set_title('F1 Score Distribution')
        axes[1,1].set_xlabel('F1 Score')
        axes[1,1].set_ylabel('Frequency')
        
        plt.tight_layout()
        
        # 플롯 저장
        plot_path = self.experiment_dir / "analysis_plots.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"📊 Analysis plots saved to {plot_path}")
        plt.close()

def main():
    parser = argparse.ArgumentParser(description="V2_1 & V2_2 Experiment Monitor")
    parser.add_argument('--mode', choices=['monitor', 'analyze'], default='monitor',
                      help='Mode: monitor (real-time) or analyze (results)')
    parser.add_argument('--experiment-dir', default='v2_experiments',
                      help='Experiment directory')
    parser.add_argument('--refresh', type=int, default=30,
                      help='Refresh interval for monitoring (seconds)')
    
    args = parser.parse_args()
    
    monitor = V2ExperimentMonitor(args.experiment_dir)
    
    if args.mode == 'monitor':
        monitor.monitor_realtime(args.refresh)
    elif args.mode == 'analyze':
        monitor.analyze_results()

if __name__ == "__main__":
    main()
