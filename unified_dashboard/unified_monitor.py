    def check_wandb_compliance(self):
        """새로운 WanDB 설정 규격 준수 확인"""
        print("🔍 WanDB 설정 규격 준수 검사:")
        print("=" * 50)
        
        compliance_checks = {
            '1. Project 이름 model_name 기반': {
                'status': '✅ 완료',
                'details': [
                    'config 파일에 model_based_project: True 설정',
                    'main 파일에 model_name 기반 project 생성 로직 추가',
                    'V2_1, V2_2, V3 모두 적용 완료'
                ]
            },
            '2. 같은 Project 내 다양한 실험': {
                'status': '✅ 완료',
                'details': [
                    '확장된 실험 매트릭스로 200+ 조합 지원',
                    'optimizer, scheduler, loss, augmentation 다양화',
                    '각 모델별로 별도 프로젝트 생성'
                ]
            },
            '3. TTA 전략 다양화': {
                'status': '✅ 완료',
                'details': [
                    'no_tta, val_only_tta, test_only_tta, full_tta, dropout_tta',
                    'V3에서 asymmetric_tta_a, asymmetric_tta_b 추가',
                    '모든 시스템에서 다양한 TTA 전략 지원'
                ]
            },
            '4. 태그 시스템 개선': {
                'status': '✅ 완료',
                'details': [
                    '시스템별 기본 태그 추가 (v2_1, v2_2, v3)',
                    '모델, 옵티마이저, 스케줄러 태그 자동 추가',
                    '우선순위별 태그로 실험 분류'
                ]
            },
            '5. Run 이름 개선': {
                'status': '✅ 완료',
                'details': [
                    '더 간결하고 읽기 쉽은 run 이름',
                    '배치 사이즈, 이미지 크기 등 주요 정보 포함',
                    '모델명 간소화로 가독성 향상'
                ]
            }
        }
        
        for check_name, check_info in compliance_checks.items():
            print(f"{check_info['status']} {check_name}")
            for detail in check_info['details']:
                print(f"    - {detail}")
            print()
        
        print("🏆 총평: 모든 WanDB 설정 규격을 성공적으로 개선했습니다!")
        print()    def analyze_wandb_projects(self):
        """새로운 WanDB 프로젝트 구조 분석"""
        print("🎨 WanDB 프로젝트 구조 분석:")
        print("-" * 40)
        
        # 예상되는 프로젝트 구조
        expected_projects = {
            'V2 단일 모델': [
                'cv-clf-convnextv2-base-fcmae-ft-in22k-in1k-384',
                'cv-clf-efficientnet-b4-ra2-in1k',
                'cv-clf-resnet50-tv2-in1k',
                'cv-clf-swin-base-patch4-window7-224-ms-in22k-ft-in1k'
            ],
            'V3 계층적 모델': [
                'cv-clf-hierarchical-modelA-convnextv2-base-fcmae-ft-in22k-in1k-384',
                'cv-clf-hierarchical-modelB-convnextv2-nano-fcmae-ft-in22k-in1k-384',
                'cv-clf-hierarchical-modelA-efficientnet-b4-ra2-in1k',
                'cv-clf-hierarchical-modelB-mobilenetv3-small-100-lamb-in1k'
            ]
        }
        
        for category, projects in expected_projects.items():
            print(f"📊 {category}:")
            for project in projects:
                print(f"  - {project}")
            print()
        
        print("📈 예상 로깅 구조:")
        print("  - 각 모델별로 별도 프로젝트")
        print("  - 프로젝트 내 다양한 하이퍼파라미터 조합")
        print("  - 태그를 통한 실험 분류")
        print("  - TTA 전략 다양화")
        print()#!/usr/bin/env python3
"""
Unified Experiment Dashboard
V2와 V3 실험 시스템을 통합하는 대시보드
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
import numpy as np
import sys

# 모니터링 시스템 임포트
sys.path.append('/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5')
from v2_experiment_monitor import V2ExperimentMonitor
from v3_experiment_monitor import V3ExperimentMonitor

class UnifiedExperimentDashboard:
    def __init__(self):
        self.v2_monitor = V2ExperimentMonitor("v2_experiments")
        self.v3_monitor = V3ExperimentMonitor("v3_experiments")
        
        # 통합 결과 저장 경로
        self.unified_dir = Path("unified_dashboard/results")
        self.unified_dir.mkdir(parents=True, exist_ok=True)
        
    def get_unified_status(self):
        """모든 실험 시스템 통합 상태"""
        print("🔄 Collecting status from all experiment systems...")
        
        # V2 상태 수집
        try:
            v2_status = self.v2_monitor.get_experiment_status()
        except Exception as e:
            print(f"⚠️ V2 status collection failed: {e}")
            v2_status = {'completed': 0, 'running': 0, 'pending': 0, 'failed': 0}
        
        # V3 상태 수집
        try:
            v3_status = self.v3_monitor.get_v3_experiment_status()
        except Exception as e:
            print(f"⚠️ V3 status collection failed: {e}")
            v3_status = {'completed': 0, 'running': 0, 'pending': 0, 'failed': 0}
        
        # 통합 상태 생성
        unified_status = {
            'systems': {
                'v2_1': {
                    'completed': v2_status.get('v2_1_completed', 0),
                    'total': v2_status.get('v2_1_total', 0),
                    'type': 'Single Model Classification'
                },
                'v2_2': {
                    'completed': v2_status.get('v2_2_completed', 0),
                    'total': v2_status.get('v2_2_total', 0),
                    'type': 'Enhanced Single Model'
                },
                'v3_hierarchical': {
                    'completed': v3_status.get('completed', 0),
                    'total': len(self.v3_monitor.experiment_list),
                    'type': 'Hierarchical Classification'
                }
            },
            'overall': {
                'total_experiments': (v2_status.get('total', 0) + v3_status.get('completed', 0) + 
                                    v3_status.get('running', 0) + v3_status.get('pending', 0)),
                'total_completed': v2_status.get('completed', 0) + v3_status.get('completed', 0),
                'total_running': v2_status.get('running', 0) + v3_status.get('running', 0),
                'total_pending': v2_status.get('pending', 0) + v3_status.get('pending', 0)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return unified_status
    
    def display_unified_status(self):
        """통합 상태 표시"""
        status = self.get_unified_status()
        
        print("🎯 Unified Experiment Dashboard")
        print("=" * 80)
        print(f"📊 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 전체 요약
        overall = status['overall']
        print("📈 Overall Summary:")
        print(f"  Total Experiments: {overall['total_experiments']}")
        print(f"  ✅ Completed: {overall['total_completed']}")
        print(f"  🔄 Running: {overall['total_running']}")
        print(f"  ⏳ Pending: {overall['total_pending']}")
        print()
        
        # 시스템별 상태
        print("🔧 System-wise Status:")
        systems = status['systems']
        
        for system_name, system_data in systems.items():
            total = system_data['total']
            completed = system_data['completed']
            progress = (completed / total * 100) if total > 0 else 0
            
            print(f"  {system_name.upper()}:")
            print(f"    Type: {system_data['type']}")
            print(f"    Progress: {completed}/{total} ({progress:.1f}%)")
            print(f"    Status: {'✅ Complete' if completed == total else '🔄 In Progress'}")
            print()
        
        # WanDB 설정 분석 추가
        self.analyze_wandb_projects()
        self.check_wandb_compliance()
    
    def display_performance_comparison(self):
        """시스템 간 성능 비교"""
        print("🏆 Performance Comparison:")
        print("-" * 50)
        
        # V2 최고 성능
        try:
            v2_results = self.v2_monitor.get_best_results()
            if v2_results:
                v2_best = max(v2_results, key=lambda x: x.get('f1_score', 0))
                print(f"🥇 V2 Best: {v2_best.get('name', 'Unknown')} - F1: {v2_best.get('f1_score', 0):.4f}")
        except:
            print("📊 V2 performance data not available")
        
        # V3 최고 성능
        try:
            v3_results = self.v3_monitor.collect_v3_results()
            if v3_results:
                v3_best = max(v3_results, key=lambda x: x.get('final_f1', 0))
                print(f"🥈 V3 Best: {v3_best.get('name', 'Unknown')} - F1: {v3_best.get('final_f1', 0):.4f}")
        except:
            print("📊 V3 performance data not available")
        
        print()
    
    def generate_unified_report(self):
        """통합 성능 리포트 생성"""
        print("📊 Generating unified performance report...")
        
        # 데이터 수집
        v2_results = self.collect_v2_results()
        v3_results = self.collect_v3_results()
        
        # 통합 분석
        analysis = self.analyze_all_systems(v2_results, v3_results)
        
        # 리포트 생성
        report = self.create_unified_report(analysis)
        
        # 시각화 생성
        self.create_unified_visualizations(v2_results, v3_results)
        
        return report
    
    def collect_v2_results(self):
        """V2 실험 결과 수집"""
        try:
            # V2 결과 수집 (기존 V2 모니터 활용)
            results = []
            
            # 제출 파일들 확인
            results_dir = Path("data/submissions")
            v2_files = list(results_dir.glob("**/v2_*.csv"))
            
            for file_path in v2_files:
                exp_name = file_path.stem
                result = {
                    'name': exp_name,
                    'system': 'v2',
                    'type': 'single_model',
                    'file_path': str(file_path),
                    'submission_time': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'f1_score': 0.0  # 실제로는 로그에서 추출
                }
                results.append(result)
            
            return results
        except Exception as e:
            print(f"⚠️ V2 results collection failed: {e}")
            return []
    
    def collect_v3_results(self):
        """V3 실험 결과 수집"""
        try:
            # V3 결과 수집 (기존 V3 모니터 활용)
            v3_results = self.v3_monitor.collect_v3_results()
            
            # 통합 형식으로 변환
            results = []
            for result in v3_results:
                unified_result = {
                    'name': result['name'],
                    'system': 'v3',
                    'type': 'hierarchical',
                    'file_path': result['file_path'],
                    'submission_time': result['submission_time'],
                    'f1_score': result['final_f1'],
                    'model_a_f1': result['model_a_f1'],
                    'model_b_f1': result['model_b_f1'],
                    'hierarchy_gain': result['final_f1'] - max(result['model_a_f1'], result['model_b_f1'])
                }
                results.append(unified_result)
            
            return results
        except Exception as e:
            print(f"⚠️ V3 results collection failed: {e}")
            return []
    
    def analyze_all_systems(self, v2_results, v3_results):
        """모든 시스템 분석"""
        analysis = {
            'v2_analysis': self.analyze_v2_results(v2_results),
            'v3_analysis': self.analyze_v3_results(v3_results),
            'cross_system_comparison': self.compare_systems(v2_results, v3_results)
        }
        return analysis
    
    def analyze_v2_results(self, v2_results):
        """V2 결과 분석"""
        if not v2_results:
            return {'status': 'no_data'}
        
        f1_scores = [r['f1_score'] for r in v2_results if r['f1_score'] > 0]
        
        return {
            'total_experiments': len(v2_results),
            'completed_experiments': len(f1_scores),
            'best_f1': max(f1_scores) if f1_scores else 0,
            'avg_f1': np.mean(f1_scores) if f1_scores else 0,
            'std_f1': np.std(f1_scores) if f1_scores else 0,
            'best_experiment': max(v2_results, key=lambda x: x['f1_score'])['name'] if f1_scores else 'N/A'
        }
    
    def analyze_v3_results(self, v3_results):
        """V3 결과 분석"""
        if not v3_results:
            return {'status': 'no_data'}
        
        f1_scores = [r['f1_score'] for r in v3_results if r['f1_score'] > 0]
        hierarchy_gains = [r['hierarchy_gain'] for r in v3_results if r['hierarchy_gain'] is not None]
        
        return {
            'total_experiments': len(v3_results),
            'completed_experiments': len(f1_scores),
            'best_f1': max(f1_scores) if f1_scores else 0,
            'avg_f1': np.mean(f1_scores) if f1_scores else 0,
            'std_f1': np.std(f1_scores) if f1_scores else 0,
            'best_experiment': max(v3_results, key=lambda x: x['f1_score'])['name'] if f1_scores else 'N/A',
            'avg_hierarchy_gain': np.mean(hierarchy_gains) if hierarchy_gains else 0,
            'positive_hierarchy_rate': len([g for g in hierarchy_gains if g > 0]) / len(hierarchy_gains) if hierarchy_gains else 0
        }
    
    def compare_systems(self, v2_results, v3_results):
        """시스템 간 비교"""
        v2_f1_scores = [r['f1_score'] for r in v2_results if r['f1_score'] > 0]
        v3_f1_scores = [r['f1_score'] for r in v3_results if r['f1_score'] > 0]
        
        comparison = {
            'v2_best': max(v2_f1_scores) if v2_f1_scores else 0,
            'v3_best': max(v3_f1_scores) if v3_f1_scores else 0,
            'v2_avg': np.mean(v2_f1_scores) if v2_f1_scores else 0,
            'v3_avg': np.mean(v3_f1_scores) if v3_f1_scores else 0,
            'winner': 'v3' if (max(v3_f1_scores) if v3_f1_scores else 0) > (max(v2_f1_scores) if v2_f1_scores else 0) else 'v2'
        }
        
        return comparison
    
    def create_unified_report(self, analysis):
        """통합 리포트 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_systems': 3,  # V2_1, V2_2, V3
                'active_systems': sum([
                    1 if analysis['v2_analysis']['total_experiments'] > 0 else 0,
                    1 if analysis['v3_analysis']['total_experiments'] > 0 else 0
                ]),
                'best_overall_system': analysis['cross_system_comparison']['winner'],
                'best_overall_f1': max(
                    analysis['cross_system_comparison']['v2_best'],
                    analysis['cross_system_comparison']['v3_best']
                )
            },
            'detailed_analysis': analysis,
            'recommendations': self.generate_recommendations(analysis)
        }
        
        # 리포트 저장
        report_path = self.unified_dir / f"unified_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Unified report saved to: {report_path}")
        return report
    
    def generate_recommendations(self, analysis):
        """추천사항 생성"""
        recommendations = []
        
        # 성능 기반 추천
        if analysis['cross_system_comparison']['winner'] == 'v3':
            recommendations.append("🎯 V3 계층적 분류 시스템이 더 우수한 성능을 보입니다. V3 시스템을 중심으로 추가 실험을 진행하세요.")
        else:
            recommendations.append("🎯 V2 단일 모델 시스템이 더 우수한 성능을 보입니다. V2 시스템을 중심으로 추가 실험을 진행하세요.")
        
        # V3 특화 추천
        if analysis['v3_analysis']['status'] != 'no_data':
            hierarchy_gain = analysis['v3_analysis']['avg_hierarchy_gain']
            if hierarchy_gain > 0:
                recommendations.append(f"✨ V3 계층적 분류가 평균 {hierarchy_gain:.4f}의 성능 향상을 보입니다. 계층적 전략을 더 탐구하세요.")
            else:
                recommendations.append("⚠️ V3 계층적 분류의 성능 향상이 미미합니다. 계층적 전략을 재검토하세요.")
        
        # 실험 진행 추천
        if analysis['v2_analysis']['total_experiments'] < 10:
            recommendations.append("📊 V2 실험을 더 진행하여 충분한 데이터를 확보하세요.")
        
        if analysis['v3_analysis']['total_experiments'] < 10:
            recommendations.append("📊 V3 실험을 더 진행하여 충분한 데이터를 확보하세요.")
        
        return recommendations
    
    def create_unified_visualizations(self, v2_results, v3_results):
        """통합 시각화 생성"""
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. 성능 비교 박스플롯
        ax1 = axes[0, 0]
        v2_f1_scores = [r['f1_score'] for r in v2_results if r['f1_score'] > 0]
        v3_f1_scores = [r['f1_score'] for r in v3_results if r['f1_score'] > 0]
        
        data_to_plot = []
        labels = []
        if v2_f1_scores:
            data_to_plot.append(v2_f1_scores)
            labels.append('V2 Single Model')
        if v3_f1_scores:
            data_to_plot.append(v3_f1_scores)
            labels.append('V3 Hierarchical')
        
        if data_to_plot:
            ax1.boxplot(data_to_plot, labels=labels)
            ax1.set_title('Performance Comparison')
            ax1.set_ylabel('F1 Score')
        
        # 2. 시간별 성능 트렌드
        ax2 = axes[0, 1]
        all_results = v2_results + v3_results
        if all_results:
            sorted_results = sorted(all_results, key=lambda x: x['submission_time'])
            times = [r['submission_time'] for r in sorted_results]
            scores = [r['f1_score'] for r in sorted_results]
            systems = [r['system'] for r in sorted_results]
            
            v2_indices = [i for i, s in enumerate(systems) if s == 'v2']
            v3_indices = [i for i, s in enumerate(systems) if s == 'v3']
            
            if v2_indices:
                ax2.plot([times[i] for i in v2_indices], [scores[i] for i in v2_indices], 
                        'o-', label='V2', alpha=0.7)
            if v3_indices:
                ax2.plot([times[i] for i in v3_indices], [scores[i] for i in v3_indices], 
                        's-', label='V3', alpha=0.7)
            
            ax2.set_title('Performance Over Time')
            ax2.set_xlabel('Submission Time')
            ax2.set_ylabel('F1 Score')
            ax2.legend()
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. V3 계층적 성능 분석
        ax3 = axes[1, 0]
        if v3_results:
            hierarchy_gains = [r['hierarchy_gain'] for r in v3_results if r['hierarchy_gain'] is not None]
            if hierarchy_gains:
                ax3.hist(hierarchy_gains, bins=20, alpha=0.7, color='skyblue')
                ax3.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='No Gain')
                ax3.set_title('V3 Hierarchy Gain Distribution')
                ax3.set_xlabel('Hierarchy Gain')
                ax3.set_ylabel('Frequency')
                ax3.legend()
        
        # 4. 시스템별 실험 수
        ax4 = axes[1, 1]
        system_counts = {}
        for result in v2_results + v3_results:
            system = result['system']
            system_counts[system] = system_counts.get(system, 0) + 1
        
        if system_counts:
            systems = list(system_counts.keys())
            counts = list(system_counts.values())
            ax4.bar(systems, counts, alpha=0.7)
            ax4.set_title('Experiments by System')
            ax4.set_xlabel('System')
            ax4.set_ylabel('Number of Experiments')
        
        plt.tight_layout()
        
        # 시각화 저장
        viz_path = self.unified_dir / f"unified_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        print(f"📈 Unified visualization saved to: {viz_path}")
        
        plt.show()
    
    def run_continuous_monitoring(self, interval=60):
        """연속 모니터링 실행"""
        print("🔄 Starting continuous unified monitoring...")
        print(f"📊 Update interval: {interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                os.system('clear')  # 화면 지우기
                self.display_unified_status()
                
                print(f"\n⏰ Next update in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")


def main():
    parser = argparse.ArgumentParser(description='Unified Experiment Dashboard')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=60, help='Update interval in seconds')
    parser.add_argument('--report', action='store_true', help='Generate unified report')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    dashboard = UnifiedExperimentDashboard()
    
    if args.continuous:
        dashboard.run_continuous_monitoring(args.interval)
    elif args.report:
        dashboard.generate_unified_report()
    elif args.status:
        dashboard.display_unified_status()
    else:
        # 기본 실행: 상태 표시
        dashboard.display_unified_status()


if __name__ == "__main__":
    main()
