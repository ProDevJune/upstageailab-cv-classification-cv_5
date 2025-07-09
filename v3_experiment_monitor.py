#!/usr/bin/env python3
"""
V3 Hierarchical Classification Experiment Monitor
V3 계층적 분류 실험 모니터링 및 성능 분석 시스템
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
import glob
import yaml
import numpy as np

class V3ExperimentMonitor:
    def __init__(self, experiment_dir="v3_experiments"):
        self.experiment_dir = Path(experiment_dir)
        self.results_dir = Path("data/submissions")
        self.experiment_list = self.load_experiment_list()
        
        # 결과 저장 경로
        self.analysis_dir = self.experiment_dir / "analysis"
        self.analysis_dir.mkdir(exist_ok=True)
        
    def load_experiment_list(self):
        """실험 리스트 로드"""
        list_file = self.experiment_dir / "experiment_list.json"
        if list_file.exists():
            with open(list_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def monitor_realtime(self, refresh_interval=60):
        """실시간 V3 실험 모니터링"""
        print("🎯 V3 Hierarchical Classification Real-time Monitor")
        print("=" * 70)
        
        while True:
            try:
                self.display_v3_status()
                time.sleep(refresh_interval)
                os.system('clear' if os.name == 'posix' else 'cls')
            except KeyboardInterrupt:
                print("\n👋 V3 Monitoring stopped by user")
                break
    
    def display_v3_status(self):
        """V3 실험 상태 표시"""
        print(f"📊 V3 Hierarchical Experiment Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        status_summary = self.get_v3_experiment_status()
        
        # 전체 통계
        total = len(self.experiment_list)
        completed = status_summary['completed']
        running = status_summary['running']
        pending = status_summary['pending']
        failed = status_summary['failed']
        
        print(f"📈 Total V3 Experiments: {total}")
        print(f"✅ Completed: {completed} ({completed/total*100:.1f}%)")
        print(f"🔄 Running: {running}")
        print(f"⏳ Pending: {pending}")
        print(f"❌ Failed: {failed}")
        print()
        
        # 계층적 분류 특화 정보
        print("🎯 Hierarchical Classification Analysis:")
        print(f"📊 Model A Completed: {status_summary['model_a_completed']}")
        print(f"⚡ Model B Completed: {status_summary['model_b_completed']}")
        print(f"🔗 Full Pipeline Completed: {status_summary['pipeline_completed']}")
        print()
        
        # 현재 실행 중인 실험
        if status_summary['current_experiment']:
            print(f"🔬 Currently Running: {status_summary['current_experiment']}")
        
        # 최근 완료된 실험
        recent_completed = status_summary['recent_completed'][:3]
        if recent_completed:
            print("\n🏆 Recently Completed:")
            for exp in recent_completed:
                print(f"  ✅ {exp['name']} - F1: {exp.get('f1_score', 'N/A')}")
        
        # 성능 분석 (완료된 실험이 있는 경우)
        if completed > 0:
            self.display_performance_summary()
    
    def get_v3_experiment_status(self):
        """V3 실험 상태 수집"""
        status = {
            'completed': 0,
            'running': 0,
            'pending': 0,
            'failed': 0,
            'model_a_completed': 0,
            'model_b_completed': 0,
            'pipeline_completed': 0,
            'current_experiment': None,
            'recent_completed': []
        }
        
        # 제출 파일들 확인
        submission_files = list(self.results_dir.glob("**/v3_*.csv"))
        completed_experiments = set()
        
        for file_path in submission_files:
            exp_name = self.extract_experiment_name(file_path.name)
            if exp_name:
                completed_experiments.add(exp_name)
        
        # 로그 파일 확인
        log_files = list(self.experiment_dir.glob("logs/*.log"))
        running_experiments = set()
        
        for log_file in log_files:
            if self.is_experiment_running(log_file):
                running_exp = self.extract_running_experiment(log_file)
                if running_exp:
                    running_experiments.add(running_exp)
        
        # 상태 업데이트
        status['completed'] = len(completed_experiments)
        status['running'] = len(running_experiments)
        status['pending'] = len(self.experiment_list) - status['completed'] - status['running']
        status['pipeline_completed'] = len(completed_experiments)
        
        if running_experiments:
            status['current_experiment'] = list(running_experiments)[0]
        
        # 최근 완료된 실험 정보
        status['recent_completed'] = self.get_recent_completed_experiments(completed_experiments)
        
        return status
    
    def extract_experiment_name(self, filename):
        """파일명에서 실험 이름 추출"""
        if filename.startswith("v3_") and filename.endswith(".csv"):
            # 파일명에서 timestamp 제거하여 실험 이름 추출
            name_parts = filename.replace(".csv", "").split("-")
            if len(name_parts) > 1:
                return name_parts[1]  # timestamp 다음 부분이 실험 이름
        return None
    
    def is_experiment_running(self, log_file):
        """실험 실행 중인지 확인"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return False
            
            # 최근 로그 확인
            recent_lines = lines[-50:]  # 최근 50줄 확인
            
            # 실행 중 표시 찾기
            for line in recent_lines:
                if "Starting V3 Hierarchical" in line or "Training for Model" in line:
                    return True
                if "completed" in line or "failed" in line:
                    return False
            
            return False
        except:
            return False
    
    def extract_running_experiment(self, log_file):
        """실행 중인 실험 이름 추출"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 최근 로그에서 실험 이름 찾기
            for line in reversed(lines[-20:]):
                if "Starting V3 Hierarchical:" in line:
                    return line.split(":")[-1].strip()
            
            return None
        except:
            return None
    
    def get_recent_completed_experiments(self, completed_experiments):
        """최근 완료된 실험 정보 수집"""
        recent = []
        
        for exp_name in completed_experiments:
            # 결과 파일 찾기
            result_files = list(self.results_dir.glob(f"**/v3_*{exp_name}*.csv"))
            
            if result_files:
                result_file = result_files[0]
                exp_info = {
                    'name': exp_name,
                    'completed_time': datetime.fromtimestamp(result_file.stat().st_mtime),
                    'f1_score': self.extract_f1_score(result_file)
                }
                recent.append(exp_info)
        
        # 완료 시간 순으로 정렬
        recent.sort(key=lambda x: x['completed_time'], reverse=True)
        return recent
    
    def extract_f1_score(self, result_file):
        """결과 파일에서 F1 점수 추출 (추후 구현)"""
        # 실제로는 로그 파일이나 별도 결과 파일에서 F1 점수를 추출해야 함
        return "N/A"
    
    def display_performance_summary(self):
        """성능 요약 표시"""
        print("\n🔍 V3 Hierarchical Performance Summary:")
        print("-" * 50)
        
        # 완료된 실험들의 성능 분석
        completed_results = self.collect_v3_results()
        
        if not completed_results:
            print("📊 No completed experiments found")
            return
        
        # 모델별 성능 통계
        model_a_performance = {}
        model_b_performance = {}
        
        for result in completed_results:
            model_a_name = result.get('model_a_name', 'unknown')
            model_b_name = result.get('model_b_name', 'unknown')
            
            if model_a_name not in model_a_performance:
                model_a_performance[model_a_name] = []
            if model_b_name not in model_b_performance:
                model_b_performance[model_b_name] = []
            
            model_a_performance[model_a_name].append(result.get('model_a_f1', 0))
            model_b_performance[model_b_name].append(result.get('model_b_f1', 0))
        
        # 최고 성능 실험
        best_result = max(completed_results, key=lambda x: x.get('final_f1', 0))
        print(f"🏆 Best Performance: {best_result.get('name', 'unknown')}")
        print(f"   Final F1: {best_result.get('final_f1', 0):.4f}")
        print(f"   Model A F1: {best_result.get('model_a_f1', 0):.4f}")
        print(f"   Model B F1: {best_result.get('model_b_f1', 0):.4f}")
        
        # 평균 성능
        avg_f1 = np.mean([r.get('final_f1', 0) for r in completed_results])
        print(f"📊 Average F1: {avg_f1:.4f}")
    
    def collect_v3_results(self):
        """V3 실험 결과 수집"""
        results = []
        
        # 제출 파일들 스캔
        submission_files = list(self.results_dir.glob("**/v3_*.csv"))
        
        for file_path in submission_files:
            exp_name = self.extract_experiment_name(file_path.name)
            if exp_name:
                result = {
                    'name': exp_name,
                    'file_path': str(file_path),
                    'submission_time': datetime.fromtimestamp(file_path.stat().st_mtime),
                    # 추후 로그 파일에서 추출할 성능 지표들
                    'model_a_f1': 0.0,
                    'model_b_f1': 0.0,
                    'final_f1': 0.0,
                    'model_a_name': self.extract_model_name(exp_name, 'A'),
                    'model_b_name': self.extract_model_name(exp_name, 'B')
                }
                results.append(result)
        
        return results
    
    def extract_model_name(self, exp_name, model_type):
        """실험 이름에서 모델 이름 추출"""
        parts = exp_name.split('_')
        if len(parts) >= 3:
            if model_type == 'A':
                return parts[1]  # 두 번째 부분이 model A
            elif model_type == 'B':
                return parts[2]  # 세 번째 부분이 model B
        return 'unknown'
    
    def analyze_hierarchical_performance(self):
        """계층적 분류 성능 분석"""
        print("🔍 V3 Hierarchical Classification Performance Analysis")
        print("=" * 60)
        
        results = self.collect_v3_results()
        
        if not results:
            print("📊 No completed experiments found")
            return
        
        # 성능 분석 리포트 생성
        self.generate_performance_report(results)
        
        # 시각화 생성
        self.create_performance_visualizations(results)
    
    def generate_performance_report(self, results):
        """성능 분석 리포트 생성"""
        print("📊 Generating performance analysis report...")
        
        # 모델별 성능 분석
        model_performance = {}
        
        for result in results:
            model_combo = f"{result['model_a_name']}_+_{result['model_b_name']}"
            if model_combo not in model_performance:
                model_performance[model_combo] = []
            model_performance[model_combo].append(result['final_f1'])
        
        # 리포트 생성
        report = f"""# V3 Hierarchical Classification Performance Report
Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Overall Statistics
- **Total Completed Experiments**: {len(results)}
- **Best Performance**: {max(results, key=lambda x: x['final_f1'])['final_f1']:.4f}
- **Average Performance**: {np.mean([r['final_f1'] for r in results]):.4f}
- **Performance Std**: {np.std([r['final_f1'] for r in results]):.4f}

## 🏆 Top 10 Experiments
"""
        
        # 상위 10개 실험
        top_results = sorted(results, key=lambda x: x['final_f1'], reverse=True)[:10]
        for i, result in enumerate(top_results, 1):
            report += f"{i}. **{result['name']}** - F1: {result['final_f1']:.4f}\n"
        
        report += "\n## 🔍 Model Combination Analysis\n"
        for combo, scores in model_performance.items():
            avg_score = np.mean(scores)
            report += f"- **{combo}**: {avg_score:.4f} (±{np.std(scores):.4f})\n"
        
        # 리포트 저장
        report_path = self.analysis_dir / f"v3_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Performance report saved: {report_path}")
    
    def create_performance_visualizations(self, results):
        """성능 시각화 생성"""
        print("📊 Creating performance visualizations...")
        
        if not results:
            return
        
        # 성능 분포 히스토그램
        plt.figure(figsize=(12, 8))
        
        # 1. 전체 성능 분포
        plt.subplot(2, 2, 1)
        f1_scores = [r['final_f1'] for r in results]
        plt.hist(f1_scores, bins=20, alpha=0.7, color='skyblue')
        plt.title('V3 Hierarchical F1 Score Distribution')
        plt.xlabel('F1 Score')
        plt.ylabel('Frequency')
        
        # 2. 모델별 성능 비교
        plt.subplot(2, 2, 2)
        model_a_names = list(set(r['model_a_name'] for r in results))
        model_a_scores = {name: [] for name in model_a_names}
        
        for result in results:
            model_a_scores[result['model_a_name']].append(result['final_f1'])
        
        plt.boxplot([scores for scores in model_a_scores.values()], 
                   labels=model_a_names)
        plt.title('Model A Performance Comparison')
        plt.ylabel('F1 Score')
        plt.xticks(rotation=45)
        
        # 3. 시간에 따른 성능 변화
        plt.subplot(2, 2, 3)
        sorted_results = sorted(results, key=lambda x: x['submission_time'])
        times = [r['submission_time'] for r in sorted_results]
        scores = [r['final_f1'] for r in sorted_results]
        
        plt.plot(times, scores, 'o-', alpha=0.7)
        plt.title('Performance Over Time')
        plt.xlabel('Submission Time')
        plt.ylabel('F1 Score')
        plt.xticks(rotation=45)
        
        # 4. 모델 조합별 성능 히트맵
        plt.subplot(2, 2, 4)
        model_a_names = sorted(set(r['model_a_name'] for r in results))
        model_b_names = sorted(set(r['model_b_name'] for r in results))
        
        heatmap_data = np.zeros((len(model_a_names), len(model_b_names)))
        
        for i, a_name in enumerate(model_a_names):
            for j, b_name in enumerate(model_b_names):
                combo_results = [r for r in results 
                               if r['model_a_name'] == a_name and r['model_b_name'] == b_name]
                if combo_results:
                    heatmap_data[i][j] = np.mean([r['final_f1'] for r in combo_results])
        
        sns.heatmap(heatmap_data, 
                   xticklabels=model_b_names, 
                   yticklabels=model_a_names,
                   annot=True, fmt='.3f', cmap='viridis')
        plt.title('Model Combination Performance Heatmap')
        plt.xlabel('Model B')
        plt.ylabel('Model A')
        
        plt.tight_layout()
        
        # 그래프 저장
        viz_path = self.analysis_dir / f"v3_performance_viz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📊 Visualizations saved: {viz_path}")
    
    def export_results_csv(self):
        """결과를 CSV로 내보내기"""
        print("📊 Exporting results to CSV...")
        
        results = self.collect_v3_results()
        
        if not results:
            print("📊 No results to export")
            return
        
        # DataFrame 생성
        df = pd.DataFrame(results)
        
        # CSV 저장
        csv_path = self.analysis_dir / f"v3_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False)
        
        print(f"📄 Results exported to: {csv_path}")
        return csv_path

def main():
    parser = argparse.ArgumentParser(description="V3 Hierarchical Classification Experiment Monitor")
    parser.add_argument('--realtime', action='store_true', help='Real-time monitoring')
    parser.add_argument('--analyze', action='store_true', help='Analyze completed experiments')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    parser.add_argument('--interval', type=int, default=60, help='Monitoring interval in seconds')
    
    args = parser.parse_args()
    
    try:
        monitor = V3ExperimentMonitor()
        
        if args.realtime:
            monitor.monitor_realtime(args.interval)
        elif args.analyze:
            monitor.analyze_hierarchical_performance()
        elif args.export:
            monitor.export_results_csv()
        else:
            # 기본: 현재 상태 표시
            monitor.display_v3_status()
            
            print("\n🔧 Available commands:")
            print("  --realtime    : Real-time monitoring")
            print("  --analyze     : Performance analysis")
            print("  --export      : Export results to CSV")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
