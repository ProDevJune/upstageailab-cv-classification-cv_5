"""
AIStages 서버와 통합된 확장 HPO 실험 추적 시스템
기존 experiment_tracker.py를 확장하여 대회 서버 점수까지 추적
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class EnhancedExperimentTracker:
    """AIStages 서버 점수 추적이 포함된 확장 실험 추적기"""
    
    def __init__(self, results_path: str = "experiment_results.csv"):
        self.results_path = Path(results_path)
        self.analysis_dir = Path("analysis_results")
        self.analysis_dir.mkdir(exist_ok=True)
        
        # 확장된 결과 파일 (기존 + AIStages 점수)
        self.enhanced_results_path = Path("enhanced_experiment_results.csv")
        self._initialize_enhanced_results()
        
        print(f"📊 확장 실험 추적기 초기화: {self.results_path}")
    
    def _initialize_enhanced_results(self):
        """확장된 실험 결과 파일 초기화"""
        if not self.enhanced_results_path.exists():
            # 기존 컬럼 + AIStages 관련 컬럼
            columns = [
                # 기존 HPO 결과 컬럼들
                'experiment_id', 'timestamp', 'platform', 'device', 'status',
                'model_name', 'image_size', 'lr', 'batch_size', 'augmentation_level',
                'TTA', 'epochs_run', 'final_f1', 'val_accuracy', 'training_time_min',
                'config_path', 'model_path', 'submission_path', 'error_message',
                
                # AIStages 관련 컬럼들
                'aistages_submitted', 'submission_date', 'submission_time',
                'aistages_public_score', 'aistages_private_score', 
                'public_rank', 'private_rank',
                'score_difference_public', 'score_difference_private',
                'submission_notes', 'leaderboard_screenshot_path',
                
                # 분석 컬럼들
                'local_server_correlation', 'overfitting_risk', 'recommended_for_ensemble'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.enhanced_results_path, index=False)
            print(f"📊 확장 실험 결과 파일 생성: {self.enhanced_results_path}")

    def sync_from_basic_results(self):
        """기존 experiment_results.csv에서 데이터 동기화"""
        if not self.results_path.exists():
            print("⚠️ 기본 실험 결과 파일이 없습니다.")
            return
        
        basic_df = pd.read_csv(self.results_path)
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        
        # 새로운 실험들만 추가
        new_experiments = []
        for _, row in basic_df.iterrows():
            if row['experiment_id'] not in enhanced_df['experiment_id'].values:
                # 기본 데이터 + 빈 AIStages 컬럼들
                enhanced_row = row.to_dict()
                enhanced_row.update({
                    'aistages_submitted': False,
                    'submission_date': None,
                    'submission_time': None,
                    'aistages_public_score': None,
                    'aistages_private_score': None,
                    'public_rank': None,
                    'private_rank': None,
                    'score_difference_public': None,
                    'score_difference_private': None,
                    'submission_notes': None,
                    'leaderboard_screenshot_path': None,
                    'local_server_correlation': None,
                    'overfitting_risk': 'unknown',
                    'recommended_for_ensemble': False
                })
                new_experiments.append(enhanced_row)
        
        if new_experiments:
            new_df = pd.DataFrame(new_experiments)
            enhanced_df = pd.concat([enhanced_df, new_df], ignore_index=True)
            enhanced_df.to_csv(self.enhanced_results_path, index=False)
            print(f"✅ {len(new_experiments)}개 새 실험 동기화 완료")

    def submit_to_aistages(self, experiment_id: str, submission_notes: str = "") -> str:
        """AIStages 제출을 위한 준비 및 안내"""
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        experiment = enhanced_df[enhanced_df['experiment_id'] == experiment_id]
        
        if experiment.empty:
            return f"❌ 실험 ID '{experiment_id}'를 찾을 수 없습니다."
        
        exp = experiment.iloc[0]
        submission_file = exp['submission_path']
        
        if pd.isna(submission_file) or not Path(submission_file).exists():
            return f"❌ 제출 파일이 없습니다: {submission_file}"
        
        # 제출 준비 상태로 마킹
        enhanced_df.loc[enhanced_df['experiment_id'] == experiment_id, 'submission_notes'] = submission_notes
        enhanced_df.to_csv(self.enhanced_results_path, index=False)
        
        instructions = f"""
🚀 AIStages 제출 준비 완료!

📋 실험 정보:
  - 실험 ID: {experiment_id}
  - 모델: {exp['model_name']}
  - 로컬 F1: {exp['final_f1']:.4f}
  - 제출 파일: {submission_file}

📤 제출 후 해야 할 일:
  1. AIStages에서 점수 확인
  2. 다음 명령어로 결과 기록:
     tracker.record_aistages_result(
         experiment_id="{experiment_id}",
         public_score=<서버점수>,
         public_rank=<순위>,
         private_score=<최종점수>,  # 선택
         private_rank=<최종순위>   # 선택
     )

💡 기록하지 않으면 로컬-서버 점수 분석이 불가능합니다!
        """
        
        return instructions

    def record_aistages_result(self, experiment_id: str, public_score: float,
                              public_rank: int = None, private_score: float = None,
                              private_rank: int = None, notes: str = None) -> None:
        """AIStages 서버 점수 기록"""
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        exp_idx = enhanced_df[enhanced_df['experiment_id'] == experiment_id].index
        
        if len(exp_idx) == 0:
            print(f"❌ 실험 ID '{experiment_id}'를 찾을 수 없습니다.")
            return
        
        idx = exp_idx[0]
        local_f1 = enhanced_df.loc[idx, 'final_f1']
        
        # AIStages 결과 업데이트
        enhanced_df.loc[idx, 'aistages_submitted'] = True
        enhanced_df.loc[idx, 'submission_date'] = datetime.now().strftime("%Y-%m-%d")
        enhanced_df.loc[idx, 'submission_time'] = datetime.now().strftime("%H:%M:%S")
        enhanced_df.loc[idx, 'aistages_public_score'] = public_score
        enhanced_df.loc[idx, 'public_rank'] = public_rank
        
        if private_score is not None:
            enhanced_df.loc[idx, 'aistages_private_score'] = private_score
            enhanced_df.loc[idx, 'private_rank'] = private_rank
            enhanced_df.loc[idx, 'score_difference_private'] = private_score - local_f1
        
        # 점수 차이 계산
        score_diff = public_score - local_f1
        enhanced_df.loc[idx, 'score_difference_public'] = score_diff
        
        # 과적합 위험도 평가
        if score_diff < -0.05:
            enhanced_df.loc[idx, 'overfitting_risk'] = 'high'
        elif score_diff < -0.02:
            enhanced_df.loc[idx, 'overfitting_risk'] = 'medium'
        else:
            enhanced_df.loc[idx, 'overfitting_risk'] = 'low'
        
        if notes:
            existing_notes = enhanced_df.loc[idx, 'submission_notes']
            if pd.isna(existing_notes):
                enhanced_df.loc[idx, 'submission_notes'] = notes
            else:
                enhanced_df.loc[idx, 'submission_notes'] = f"{existing_notes} | {notes}"
        
        enhanced_df.to_csv(self.enhanced_results_path, index=False)
        
        # 상관관계 업데이트
        self._update_correlation_analysis()
        
        print(f"✅ 실험 {experiment_id} AIStages 결과 기록 완료")
        print(f"   로컬 F1: {local_f1:.4f} → 서버 점수: {public_score:.4f} (차이: {score_diff:+.4f})")
        if public_rank:
            print(f"   순위: {public_rank}위")

    def _update_correlation_analysis(self):
        """전체 실험의 로컬-서버 상관관계 분석"""
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        submitted = enhanced_df[enhanced_df['aistages_submitted'] == True].copy()
        
        if len(submitted) < 2:
            return
        
        # 전체 상관관계 계산
        correlation = submitted['final_f1'].corr(submitted['aistages_public_score'])
        
        # 각 실험의 상관관계 기여도 계산 (간단한 버전)
        for idx in submitted.index:
            enhanced_df.loc[idx, 'local_server_correlation'] = correlation
        
        # 앙상블 추천 업데이트
        self._update_ensemble_recommendations(enhanced_df, submitted)
        
        enhanced_df.to_csv(self.enhanced_results_path, index=False)

    def _update_ensemble_recommendations(self, enhanced_df: pd.DataFrame, submitted: pd.DataFrame):
        """앙상블용 모델 추천 업데이트"""
        if len(submitted) < 3:
            return
        
        # 상위 30% 또는 최소 3개
        top_n = max(3, len(submitted) // 3)
        top_experiments = submitted.nlargest(top_n, 'aistages_public_score')
        
        # 추천 기준: 높은 서버 점수 + 낮은 과적합 위험
        for idx in top_experiments.index:
            overfitting_risk = enhanced_df.loc[idx, 'overfitting_risk']
            if overfitting_risk in ['low', 'medium']:
                enhanced_df.loc[idx, 'recommended_for_ensemble'] = True

    def print_enhanced_summary(self):
        """확장된 실험 요약 출력"""
        self.sync_from_basic_results()  # 최신 데이터 동기화
        
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        submitted = enhanced_df[enhanced_df['aistages_submitted'] == True]
        
        print("\n🎯 HPO + AIStages 통합 실험 요약")
        print("=" * 70)
        
        # 기본 통계
        print(f"📊 전체 HPO 실험: {len(enhanced_df)}개")
        print(f"📤 AIStages 제출: {len(submitted)}개")
        print(f"🏆 완료된 실험: {len(enhanced_df[enhanced_df['status'] == 'completed'])}개")
        
        if len(submitted) > 0:
            print(f"\n🌟 AIStages 서버 성과:")
            print(f"   최고 서버 점수: {submitted['aistages_public_score'].max():.4f}")
            print(f"   평균 서버 점수: {submitted['aistages_public_score'].mean():.4f}")
            best_rank = submitted['public_rank'].min() if 'public_rank' in submitted.columns and not submitted['public_rank'].isna().all() else 'N/A'
            print(f"   최고 순위: {best_rank}")
            
            # 상관관계 분석
            if len(submitted) >= 2:
                correlation = submitted['final_f1'].corr(submitted['aistages_public_score'])
                mean_diff = submitted['score_difference_public'].mean()
                print(f"\n📈 로컬 vs 서버 분석:")
                print(f"   상관관계: {correlation:.3f}")
                print(f"   평균 점수 차이: {mean_diff:+.4f}")
                
                if correlation < 0.7:
                    print("   ⚠️ 상관관계가 낮습니다. Validation 전략을 재검토하세요.")
                if mean_diff < -0.03:
                    print("   ⚠️ 과적합 가능성이 높습니다.")
            
            # 과적합 위험 분석
            high_risk = len(submitted[submitted['overfitting_risk'] == 'high'])
            medium_risk = len(submitted[submitted['overfitting_risk'] == 'medium'])
            low_risk = len(submitted[submitted['overfitting_risk'] == 'low'])
            
            print(f"\n⚠️ 과적합 위험 분석:")
            print(f"   높음: {high_risk}개, 보통: {medium_risk}개, 낮음: {low_risk}개")
            
            # 앙상블 추천
            ensemble_candidates = enhanced_df[enhanced_df['recommended_for_ensemble'] == True]
            if len(ensemble_candidates) > 0:
                print(f"\n🎯 앙상블 추천: {len(ensemble_candidates)}개 모델")
                print("   실험 ID들:", list(ensemble_candidates['experiment_id']))

    def get_submission_candidates(self, strategy: str = "diverse") -> pd.DataFrame:
        """제출 후보 실험들 추천"""
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        completed = enhanced_df[enhanced_df['status'] == 'completed'].copy()
        not_submitted = completed[completed['aistages_submitted'] != True]
        
        if len(not_submitted) == 0:
            print("📭 제출할 수 있는 새로운 실험이 없습니다.")
            return pd.DataFrame()
        
        if strategy == "best_local":
            # 로컬 성능 기준 상위
            candidates = not_submitted.nlargest(5, 'final_f1')
        elif strategy == "diverse":
            # 다양한 설정 조합
            candidates = self._select_diverse_experiments(not_submitted)
        elif strategy == "conservative":
            # 과적합 위험이 낮을 것으로 예상되는 실험들
            candidates = self._select_conservative_experiments(not_submitted)
        else:
            candidates = not_submitted.nlargest(5, 'final_f1')
        
        return candidates[['experiment_id', 'final_f1', 'model_name', 'lr', 
                         'augmentation_level', 'TTA', 'submission_path']]

    def _select_diverse_experiments(self, df: pd.DataFrame) -> pd.DataFrame:
        """다양한 설정 조합 선택"""
        # 모델별로 최고 성능 1개씩
        diverse = []
        for model in df['model_name'].unique():
            model_experiments = df[df['model_name'] == model]
            best = model_experiments.nlargest(1, 'final_f1')
            diverse.append(best)
        
        result = pd.concat(diverse, ignore_index=True) if diverse else pd.DataFrame()
        return result.nlargest(5, 'final_f1')

    def _select_conservative_experiments(self, df: pd.DataFrame) -> pd.DataFrame:
        """보수적 실험 선택 (과적합 위험 최소화)"""
        # 간단한 augmentation, 적절한 에포크 수
        conservative = df[
            (df['augmentation_level'].isin(['minimal', 'moderate'])) &
            (df['epochs_run'] < 70)  # 너무 많이 학습하지 않은 것들
        ]
        return conservative.nlargest(5, 'final_f1')

    def create_submission_report(self, experiment_ids: List[str], 
                               output_path: str = "submission_report.html") -> None:
        """제출용 실험 상세 리포트 생성"""
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        experiments = enhanced_df[enhanced_df['experiment_id'].isin(experiment_ids)]
        
        if len(experiments) == 0:
            print("❌ 해당하는 실험이 없습니다.")
            return
        
        html_content = f"""
        <html>
        <head>
            <title>AIStages 제출용 실험 리포트</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .best {{ background-color: #d4edda; }}
                .warning {{ background-color: #fff3cd; }}
            </style>
        </head>
        <body>
            <h1>🚀 AIStages 제출용 실험 리포트</h1>
            <p>생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h2>📋 선택된 실험들</h2>
            {experiments[['experiment_id', 'final_f1', 'val_accuracy', 'model_name', 
                         'lr', 'augmentation_level', 'TTA', 'epochs_run']].to_html(index=False)}
            
            <h2>🎯 제출 순서 추천</h2>
            <ol>
        """
        
        # 제출 순서 추천 (로컬 성능 기준)
        sorted_experiments = experiments.sort_values('final_f1', ascending=False)
        for idx, (_, exp) in enumerate(sorted_experiments.iterrows(), 1):
            html_content += f"""
                <li>
                    <strong>{exp['experiment_id']}</strong> 
                    (F1: {exp['final_f1']:.4f}, {exp['model_name']})
                    <br>설정: lr={exp['lr']}, aug={exp['augmentation_level']}, TTA={exp['TTA']}
                    <br>제출 파일: {exp['submission_path']}
                </li>
            """
        
        html_content += """
            </ol>
            
            <h2>📝 제출 후 체크리스트</h2>
            <ul>
                <li>✅ AIStages에서 Public Score 확인</li>
                <li>✅ Leaderboard 순위 확인</li>
                <li>✅ Python으로 결과 기록:<br>
                    <code>tracker.record_aistages_result(experiment_id="...", public_score=0.xxxx, public_rank=xx)</code>
                </li>
                <li>✅ 가능하면 리더보드 스크린샷 저장</li>
            </ul>
            
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 제출용 리포트 생성: {output_path}")

    def analyze_best_strategies(self) -> Dict:
        """최고 성과를 낸 전략들 분석"""
        enhanced_df = pd.read_csv(self.enhanced_results_path)
        submitted = enhanced_df[enhanced_df['aistages_submitted'] == True]
        
        if len(submitted) < 3:
            return {"message": "분석을 위한 제출 데이터가 부족합니다."}
        
        # 상위 30% 실험들 분석
        top_30_percent = submitted.nlargest(max(1, len(submitted) // 3), 'aistages_public_score')
        
        analysis = {
            "best_models": top_30_percent['model_name'].value_counts().to_dict(),
            "best_learning_rates": top_30_percent['lr'].value_counts().to_dict(),
            "best_image_sizes": top_30_percent['image_size'].value_counts().to_dict(),
            "best_augmentation": top_30_percent['augmentation_level'].value_counts().to_dict(),
            "best_tta_settings": top_30_percent['TTA'].value_counts().to_dict(),
            "correlation_insights": {
                "local_server_correlation": submitted['final_f1'].corr(submitted['aistages_public_score']),
                "overfitting_rate": len(submitted[submitted['overfitting_risk'] == 'high']) / len(submitted),
                "avg_score_difference": submitted['score_difference_public'].mean()
            }
        }
        
        return analysis

    def create_correlation_plot(self, save_path: str = "analysis_results/local_vs_server_correlation.png") -> None:
        """로컬 vs 서버 점수 상관관계 시각화"""
        try:
            enhanced_df = pd.read_csv(self.enhanced_results_path)
            submitted = enhanced_df[enhanced_df['aistages_submitted'] == True]
            complete_data = submitted.dropna(subset=['final_f1', 'aistages_public_score'])
            
            if len(complete_data) < 2:
                print("📊 시각화를 위한 데이터가 부족합니다.")
                return
            
            plt.figure(figsize=(10, 8))
            
            # 산점도
            plt.scatter(complete_data['final_f1'], complete_data['aistages_public_score'], 
                       alpha=0.7, s=100)
            
            # 실험 ID 라벨
            for idx, row in complete_data.iterrows():
                plt.annotate(row['experiment_id'], 
                           (row['final_f1'], row['aistages_public_score']),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
            
            # 추세선
            z = np.polyfit(complete_data['final_f1'], complete_data['aistages_public_score'], 1)
            p = np.poly1d(z)
            plt.plot(complete_data['final_f1'], p(complete_data['final_f1']), "r--", alpha=0.8)
            
            # 대각선 (완벽한 상관관계)
            min_val = min(complete_data['final_f1'].min(), complete_data['aistages_public_score'].min())
            max_val = max(complete_data['final_f1'].max(), complete_data['aistages_public_score'].max())
            plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect Correlation')
            
            # 상관계수 표시
            correlation = complete_data['final_f1'].corr(complete_data['aistages_public_score'])
            plt.title(f'Local vs AIStages Server Score Correlation\n(r = {correlation:.3f})', fontsize=14)
            plt.xlabel('Local Validation F1 Score', fontsize=12)
            plt.ylabel('AIStages Server Score', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"📊 상관관계 그래프 저장: {save_path}")
            
        except Exception as e:
            print(f"❌ 시각화 생성 실패: {e}")


# 사용 예시 및 통합 가이드
if __name__ == "__main__":
    # 확장 추적기 초기화
    tracker = EnhancedExperimentTracker()
    
    print("🚀 HPO + AIStages 통합 실험 추적 시스템")
    print("=" * 50)
    
    # 기본 사용법 출력
    usage_guide = """
🔧 기본 사용법:

1️⃣ 기존 HPO 실험 결과 동기화:
   tracker.sync_from_basic_results()

2️⃣ 제출 후보 확인:
   candidates = tracker.get_submission_candidates(strategy="diverse")

3️⃣ AIStages 제출 준비:
   instructions = tracker.submit_to_aistages("exp_quick_003_2507041446")

4️⃣ 서버 점수 기록:
   tracker.record_aistages_result(
       experiment_id="exp_quick_003_2507041446",
       public_score=0.8756,
       public_rank=15
   )

5️⃣ 전체 요약 확인:
   tracker.print_enhanced_summary()

6️⃣ 제출용 리포트 생성:
   tracker.create_submission_report(["exp_001", "exp_002"])
    """
    print(usage_guide)
