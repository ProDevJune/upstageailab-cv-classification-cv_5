"""
실험 결과 추적 및 분석 도구
HPO 실험 결과를 체계적으로 분석하고 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정 (macOS)
plt.rcParams['font.family'] = ['Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ExperimentTracker:
    """실험 결과 추적 및 분석 클래스"""
    
    def __init__(self, results_path: str = "experiment_results.csv"):
        self.results_path = Path(results_path)
        self.analysis_dir = Path("analysis_results")
        self.analysis_dir.mkdir(exist_ok=True)
        
        print(f"📊 실험 추적기 초기화: {self.results_path}")
    
    def load_results(self) -> pd.DataFrame:
        """실험 결과 로드"""
        if not self.results_path.exists():
            print(f"⚠️  결과 파일이 없습니다: {self.results_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(self.results_path)
        print(f"📈 총 {len(df)}개 실험 결과 로드")
        return df
    
    def get_summary(self) -> Dict:
        """실험 현황 요약"""
        df = self.load_results()
        
        if df.empty:
            return {
                'total': 0,
                'completed': 0,
                'failed': 0,
                'running': 0,
                'platforms': [],
                'success_rate': 0
            }
        
        summary = {
            'total': len(df),
            'completed': len(df[df['status'] == 'completed']),
            'failed': len(df[df['status'] == 'failed']),
            'running': len(df[df['status'] == 'running']),
            'platforms': df['platform'].unique().tolist(),
            'success_rate': len(df[df['status'] == 'completed']) / len(df) * 100 if len(df) > 0 else 0
        }
        
        # 완료된 실험들의 통계
        completed_df = df[df['status'] == 'completed']
        if not completed_df.empty and 'final_f1' in completed_df.columns:
            summary.update({
                'best_f1': completed_df['final_f1'].max(),
                'avg_f1': completed_df['final_f1'].mean(),
                'std_f1': completed_df['final_f1'].std(),
                'avg_training_time': completed_df['training_time_min'].mean() if 'training_time_min' in completed_df.columns else 0
            })
        
        return summary
    
    def print_summary(self):
        """실험 요약 출력"""
        summary = self.get_summary()
        
        print("\n📊 실험 현황 요약")
        print("=" * 50)
        print(f"총 실험 수: {summary['total']}")
        print(f"완료: {summary['completed']}")
        print(f"실패: {summary['failed']}")
        print(f"실행 중: {summary['running']}")
        print(f"성공률: {summary['success_rate']:.1f}%")
        
        if 'best_f1' in summary:
            print(f"\n🏆 성능 통계")
            print(f"최고 F1: {summary['best_f1']:.4f}")
            print(f"평균 F1: {summary['avg_f1']:.4f}")
            print(f"표준편차: {summary['std_f1']:.4f}")
            print(f"평균 훈련 시간: {summary['avg_training_time']:.1f}분")
        
        if summary['platforms']:
            print(f"\n🖥️  사용된 플랫폼: {', '.join(summary['platforms'])}")
    
    def get_top_experiments(self, n: int = 10, metric: str = 'final_f1') -> pd.DataFrame:
        """상위 N개 실험 조회"""
        df = self.load_results()
        completed_df = df[df['status'] == 'completed']
        
        if completed_df.empty or metric not in completed_df.columns:
            print(f"⚠️  완료된 실험이 없거나 {metric} 컬럼이 없습니다.")
            return pd.DataFrame()
        
        top_experiments = completed_df.nlargest(n, metric)
        
        # 중요한 컬럼만 선택
        important_cols = ['experiment_id', 'model_name', 'image_size', 'lr', 
                         'batch_size', 'augmentation_level', 'TTA', metric, 'training_time_min']
        available_cols = [col for col in important_cols if col in top_experiments.columns]
        
        return top_experiments[available_cols]
    
    def analyze_hyperparameters(self) -> Dict:
        """하이퍼파라미터별 성능 영향 분석"""
        df = self.load_results()
        completed_df = df[df['status'] == 'completed']
        
        if completed_df.empty or 'final_f1' not in completed_df.columns:
            print("⚠️  분석할 완료된 실험 데이터가 없습니다.")
            return {}
        
        analysis = {}
        
        # 모델별 성능 분석
        if 'model_name' in completed_df.columns:
            model_performance = completed_df.groupby('model_name')['final_f1'].agg(['mean', 'std', 'count'])
            analysis['model_performance'] = model_performance.to_dict('index')
        
        # 이미지 크기별 성능 분석
        if 'image_size' in completed_df.columns:
            size_performance = completed_df.groupby('image_size')['final_f1'].agg(['mean', 'std', 'count'])
            analysis['image_size_performance'] = size_performance.to_dict('index')
        
        # 학습률별 성능 분석
        if 'lr' in completed_df.columns:
            lr_performance = completed_df.groupby('lr')['final_f1'].agg(['mean', 'std', 'count'])
            analysis['lr_performance'] = lr_performance.to_dict('index')
        
        # 증강 레벨별 성능 분석
        if 'augmentation_level' in completed_df.columns:
            aug_performance = completed_df.groupby('augmentation_level')['final_f1'].agg(['mean', 'std', 'count'])
            analysis['augmentation_performance'] = aug_performance.to_dict('index')
        
        # TTA 효과 분석
        if 'TTA' in completed_df.columns:
            tta_performance = completed_df.groupby('TTA')['final_f1'].agg(['mean', 'std', 'count'])
            analysis['tta_performance'] = tta_performance.to_dict('index')
        
        return analysis
    
    def create_visualizations(self, save_plots: bool = True) -> List[str]:
        """결과 시각화 그래프 생성"""
        df = self.load_results()
        completed_df = df[df['status'] == 'completed']
        
        if completed_df.empty:
            print("⚠️  시각화할 완료된 실험 데이터가 없습니다.")
            return []
        
        plot_files = []
        
        # 1. 실험 상태 파이 차트
        fig, ax = plt.subplots(figsize=(8, 6))
        status_counts = df['status'].value_counts()
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=colors)
        ax.set_title('실험 상태 분포', fontsize=16, fontweight='bold')
        
        if save_plots:
            plot_path = self.analysis_dir / 'experiment_status.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plot_files.append(str(plot_path))
        
        plt.close()
        
        # 2. 모델별 성능 비교
        if 'model_name' in completed_df.columns and 'final_f1' in completed_df.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.boxplot(data=completed_df, x='model_name', y='final_f1', ax=ax)
            ax.set_title('모델별 F1 성능 분포', fontsize=16, fontweight='bold')
            ax.set_xlabel('모델')
            ax.set_ylabel('F1 Score')
            plt.xticks(rotation=45)
            
            if save_plots:
                plot_path = self.analysis_dir / 'model_performance.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plot_files.append(str(plot_path))
            
            plt.close()
        
        # 3. 학습률별 성능 분석
        if 'lr' in completed_df.columns and 'final_f1' in completed_df.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            lr_performance = completed_df.groupby('lr')['final_f1'].mean().sort_index()
            ax.plot(range(len(lr_performance)), lr_performance.values, 'o-', linewidth=2, markersize=8)
            ax.set_xticks(range(len(lr_performance)))
            ax.set_xticklabels([f"{lr:.0e}" for lr in lr_performance.index])
            ax.set_title('학습률별 평균 F1 성능', fontsize=16, fontweight='bold')
            ax.set_xlabel('학습률')
            ax.set_ylabel('평균 F1 Score')
            ax.grid(True, alpha=0.3)
            
            if save_plots:
                plot_path = self.analysis_dir / 'lr_performance.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plot_files.append(str(plot_path))
            
            plt.close()
        
        # 4. 훈련 시간 vs 성능 산점도
        if all(col in completed_df.columns for col in ['training_time_min', 'final_f1']):
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(completed_df['training_time_min'], completed_df['final_f1'], 
                               c=completed_df['image_size'] if 'image_size' in completed_df.columns else 'blue',
                               alpha=0.7, s=60)
            ax.set_title('훈련 시간 vs F1 성능', fontsize=16, fontweight='bold')
            ax.set_xlabel('훈련 시간 (분)')
            ax.set_ylabel('F1 Score')
            
            if 'image_size' in completed_df.columns:
                cbar = plt.colorbar(scatter)
                cbar.set_label('이미지 크기')
            
            ax.grid(True, alpha=0.3)
            
            if save_plots:
                plot_path = self.analysis_dir / 'time_vs_performance.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plot_files.append(str(plot_path))
            
            plt.close()
        
        # 5. 플랫폼별 성능 비교
        if 'platform' in completed_df.columns and len(completed_df['platform'].unique()) > 1:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.boxplot(data=completed_df, x='platform', y='final_f1', ax=ax)
            ax.set_title('플랫폼별 F1 성능 분포', fontsize=16, fontweight='bold')
            ax.set_xlabel('플랫폼')
            ax.set_ylabel('F1 Score')
            plt.xticks(rotation=45)
            
            if save_plots:
                plot_path = self.analysis_dir / 'platform_performance.png'
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plot_files.append(str(plot_path))
            
            plt.close()
        
        if plot_files:
            print(f"📈 {len(plot_files)}개 시각화 파일 생성 완료:")
            for file in plot_files:
                print(f"   📊 {file}")
        
        return plot_files
    
    def generate_recommendations(self) -> Dict:
        """최적 설정 추천"""
        df = self.load_results()
        completed_df = df[df['status'] == 'completed']
        
        if completed_df.empty or 'final_f1' not in completed_df.columns:
            return {'message': '추천할 충분한 데이터가 없습니다.'}
        
        recommendations = {}
        
        # 최고 성능 실험
        best_experiment = completed_df.loc[completed_df['final_f1'].idxmax()]
        recommendations['best_experiment'] = {
            'experiment_id': best_experiment.get('experiment_id'),
            'f1_score': best_experiment.get('final_f1'),
            'model': best_experiment.get('model_name'),
            'image_size': best_experiment.get('image_size'),
            'lr': best_experiment.get('lr'),
            'augmentation': best_experiment.get('augmentation_level'),
            'TTA': best_experiment.get('TTA')
        }
        
        # 하이퍼파라미터별 최적값
        hyperparams = {}
        
        for param in ['model_name', 'image_size', 'lr', 'augmentation_level']:
            if param in completed_df.columns:
                best_value = completed_df.groupby(param)['final_f1'].mean().idxmax()
                hyperparams[param] = best_value
        
        recommendations['optimal_hyperparameters'] = hyperparams
        
        # 효율성 기준 추천 (성능 대비 빠른 훈련)
        if 'training_time_min' in completed_df.columns:
            # 성능/시간 비율 계산
            completed_df['efficiency'] = completed_df['final_f1'] / completed_df['training_time_min']
            most_efficient = completed_df.loc[completed_df['efficiency'].idxmax()]
            
            recommendations['most_efficient'] = {
                'experiment_id': most_efficient.get('experiment_id'),
                'f1_score': most_efficient.get('final_f1'),
                'training_time': most_efficient.get('training_time_min'),
                'efficiency_ratio': most_efficient.get('efficiency'),
                'model': most_efficient.get('model_name')
            }
        
        # 상위 5개 실험의 공통점 분석
        top_5 = completed_df.nlargest(5, 'final_f1')
        
        if len(top_5) >= 3:
            common_patterns = {}
            
            for param in ['model_name', 'augmentation_level', 'TTA']:
                if param in top_5.columns:
                    most_common = top_5[param].mode().iloc[0] if not top_5[param].mode().empty else None
                    if most_common is not None:
                        common_patterns[param] = most_common
            
            recommendations['top_experiments_patterns'] = common_patterns
        
        return recommendations
    
    def export_analysis_report(self, filename: str = None) -> str:
        """분석 리포트 생성 및 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hpo_analysis_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'top_experiments': self.get_top_experiments(10).to_dict('records'),
            'hyperparameter_analysis': self.analyze_hyperparameters(),
            'recommendations': self.generate_recommendations()
        }
        
        report_path = self.analysis_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 분석 리포트 저장: {report_path}")
        return str(report_path)
    
    def cleanup_old_experiments(self, days: int = 7):
        """오래된 실험 데이터 정리"""
        df = self.load_results()
        
        if df.empty or 'timestamp' not in df.columns:
            print("⚠️  정리할 데이터가 없습니다.")
            return
        
        # 타임스탬프를 datetime으로 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        old_experiments = df[df['timestamp'] < cutoff_date]
        
        if old_experiments.empty:
            print(f"🗑️  {days}일 이전 실험이 없습니다.")
            return
        
        print(f"🗑️  {len(old_experiments)}개 오래된 실험 발견 (기준: {days}일 전)")
        
        # 사용자 확인
        response = input("정말로 삭제하시겠습니까? (y/N): ")
        
        if response.lower() == 'y':
            # 새로운 데이터프레임으로 저장
            new_df = df[df['timestamp'] >= cutoff_date]
            new_df.to_csv(self.results_path, index=False)
            print(f"✅ {len(old_experiments)}개 실험 데이터 삭제 완료")
        else:
            print("❌ 삭제 취소")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="실험 결과 분석")
    parser.add_argument('--action', choices=['summary', 'top', 'analyze', 'visualize', 'recommend', 'report', 'cleanup'],
                        default='summary', help='실행할 작업')
    parser.add_argument('--n', type=int, default=10, help='상위 N개 실험 (top 작업용)')
    parser.add_argument('--days', type=int, default=7, help='정리할 일수 (cleanup 작업용)')
    
    args = parser.parse_args()
    
    tracker = ExperimentTracker()
    
    if args.action == 'summary':
        tracker.print_summary()
    
    elif args.action == 'top':
        top_experiments = tracker.get_top_experiments(args.n)
        if not top_experiments.empty:
            print(f"\n🏆 상위 {args.n}개 실험:")
            print(top_experiments.to_string(index=False))
        else:
            print("⚠️  표시할 실험 결과가 없습니다.")
    
    elif args.action == 'analyze':
        analysis = tracker.analyze_hyperparameters()
        if analysis:
            print("\n📊 하이퍼파라미터 분석:")
            for category, data in analysis.items():
                print(f"\n{category}:")
                for item, stats in data.items():
                    print(f"  {item}: 평균={stats['mean']:.4f}, 표준편차={stats['std']:.4f}, 개수={stats['count']}")
    
    elif args.action == 'visualize':
        plot_files = tracker.create_visualizations()
        if plot_files:
            print("✅ 시각화 완료")
        else:
            print("⚠️  시각화할 데이터가 없습니다.")
    
    elif args.action == 'recommend':
        recommendations = tracker.generate_recommendations()
        if 'message' in recommendations:
            print(f"⚠️  {recommendations['message']}")
        else:
            print("\n🎯 추천 설정:")
            for category, data in recommendations.items():
                print(f"\n{category}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  {key}: {value}")
    
    elif args.action == 'report':
        report_path = tracker.export_analysis_report()
        print("✅ 분석 리포트 생성 완료")
    
    elif args.action == 'cleanup':
        tracker.cleanup_old_experiments(args.days)

if __name__ == "__main__":
    main()
