"""
AIStages 대회를 위한 간편한 Python 인터페이스
Shell 스크립트 대신 Python으로 모든 기능 사용 가능
"""

from enhanced_experiment_tracker import EnhancedExperimentTracker
import pandas as pd
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

class AIStagesManager:
    """AIStages 대회 관리를 위한 통합 인터페이스"""
    
    def __init__(self):
        self.tracker = EnhancedExperimentTracker()
        self.tracker.sync_from_basic_results()
        print("🎯 AIStages 대회 관리 시스템 시작")
    
    def show_menu(self):
        """메뉴 표시"""
        print("\n" + "="*60)
        print("🚀 HPO + AIStages 통합 실험 시스템")
        print("="*60)
        print("1️⃣  새 HPO 실험 실행")
        print("2️⃣  기존 실험 결과 확인") 
        print("3️⃣  AIStages 제출 후보 추천")
        print("4️⃣  AIStages 제출 준비")
        print("5️⃣  AIStages 결과 기록")
        print("6️⃣  로컬 vs 서버 분석")
        print("7️⃣  앙상블 후보 추천")
        print("8️⃣  전체 리포트 생성")
        print("0️⃣  종료")
        print("="*60)
    
    def run_hpo_experiments(self):
        """HPO 실험 실행"""
        print("\n📋 실험 타입을 선택하세요:")
        print("1) quick (5-10개, 빠른 실험)")
        print("2) medium (20개, 중간 실험)")
        print("3) full (50개, 전체 실험)")
        
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            os.system("python start_hpo.py")
        elif choice == "2":
            os.system("python codes/auto_experiment_basic.py --type quick --max 20")
        elif choice == "3":
            os.system("python codes/auto_experiment_basic.py --type full --max 50")
        else:
            print("❌ 잘못된 선택입니다.")
            return
        
        # 실험 완료 후 자동 동기화
        print("\n🔄 실험 결과 동기화 중...")
        self.tracker.sync_from_basic_results()
        self.tracker.print_enhanced_summary()
    
    def check_results(self):
        """실험 결과 확인"""
        self.tracker.sync_from_basic_results()
        self.tracker.print_enhanced_summary()
        
        try:
            df = pd.read_csv('enhanced_experiment_results.csv')
            completed = df[df['status'] == 'completed']
            
            if len(completed) > 0:
                print("\n🏆 로컬 성능 기준 상위 5개:")
                top_5 = completed.nlargest(5, 'final_f1')[
                    ['experiment_id', 'final_f1', 'model_name', 'lr', 'augmentation_level', 'TTA']
                ]
                print(top_5.to_string(index=False))
            else:
                print("완료된 실험이 없습니다.")
        except FileNotFoundError:
            print("실험 결과 파일이 없습니다.")
    
    def recommend_candidates(self):
        """제출 후보 추천"""
        print("\n📋 추천 전략을 선택하세요:")
        print("1) best_local (로컬 성능 우선)")
        print("2) diverse (다양한 설정 조합)")
        print("3) conservative (과적합 위험 최소화)")
        
        choice = input("선택 (1-3): ").strip()
        
        strategy_map = {"1": "best_local", "2": "diverse", "3": "conservative"}
        strategy = strategy_map.get(choice, "diverse")
        
        candidates = self.tracker.get_submission_candidates(strategy)
        if not candidates.empty:
            print(f"\n🎯 제출 후보 실험들 ({strategy} 전략):")
            print(candidates.to_string(index=False))
            print("\n📝 제출 준비를 원하시면 메뉴 4번을 선택하세요.")
        else:
            print("제출할 수 있는 실험이 없습니다.")
    
    def prepare_submission(self):
        """AIStages 제출 준비"""
        experiment_id = input("\n제출할 실험 ID를 입력하세요: ").strip()
        if not experiment_id:
            print("❌ 실험 ID가 입력되지 않았습니다.")
            return
        
        notes = input("제출 관련 메모 (선택사항): ").strip()
        
        instructions = self.tracker.submit_to_aistages(experiment_id, notes)
        print(instructions)
        print("\n⚠️ 제출 후 반드시 메뉴 5번으로 결과를 기록하세요!")
    
    def record_result(self):
        """AIStages 결과 기록"""
        experiment_id = input("\n제출한 실험 ID를 입력하세요: ").strip()
        if not experiment_id:
            print("❌ 실험 ID가 입력되지 않았습니다.")
            return
        
        try:
            public_score = float(input("AIStages Public Score를 입력하세요: ").strip())
        except ValueError:
            print("❌ 올바른 점수를 입력하세요.")
            return
        
        # 선택사항들
        public_rank = input("Public 순위 (선택사항): ").strip()
        public_rank = int(public_rank) if public_rank else None
        
        private_score = input("Private Score (선택사항): ").strip()
        private_score = float(private_score) if private_score else None
        
        private_rank = input("Private 순위 (선택사항): ").strip()
        private_rank = int(private_rank) if private_rank else None
        
        notes = input("추가 메모 (선택사항): ").strip()
        notes = notes if notes else None
        
        self.tracker.record_aistages_result(
            experiment_id=experiment_id,
            public_score=public_score,
            public_rank=public_rank,
            private_score=private_score,
            private_rank=private_rank,
            notes=notes
        )
        
        print("\n📊 업데이트된 요약:")
        self.tracker.print_enhanced_summary()
    
    def analyze_correlation(self):
        """로컬 vs 서버 분석"""
        try:
            df = pd.read_csv('enhanced_experiment_results.csv')
            submitted = df[df['aistages_submitted'] == True]

            if len(submitted) < 2:
                print(f'분석을 위한 제출 데이터가 부족합니다 (최소 2개 필요, 현재 {len(submitted)}개)')
                return

            print('\n📈 로컬 vs 서버 점수 상관관계 분석')
            print('='*50)
            
            correlation = submitted['final_f1'].corr(submitted['aistages_public_score'])
            mean_diff = submitted['score_difference_public'].mean()
            std_diff = submitted['score_difference_public'].std()
            
            print(f'상관계수: {correlation:.3f}')
            print(f'평균 점수 차이: {mean_diff:+.4f}')
            print(f'점수 차이 표준편차: {std_diff:.4f}')
            
            # 상관관계 해석
            if correlation > 0.8:
                print('✅ 매우 강한 상관관계 - 로컬 validation이 서버 성능을 잘 예측')
            elif correlation > 0.6:
                print('✅ 강한 상관관계 - 로컬 validation이 어느 정도 신뢰할 만함')
            elif correlation > 0.4:
                print('⚠️ 중간 상관관계 - 로컬 validation 개선이 필요할 수 있음')
            else:
                print('❌ 약한 상관관계 - 로컬 validation 전략 재검토 필요')
            
            # 과적합 분석
            overfitting = len(submitted[submitted['overfitting_risk'] == 'high'])
            print(f'\n⚠️ 과적합 위험 높은 실험: {overfitting}개')
            
            if overfitting > 0:
                print('과적합 의심 실험들:')
                high_risk = submitted[submitted['overfitting_risk'] == 'high']
                print(high_risk[['experiment_id', 'final_f1', 'aistages_public_score', 'score_difference_public']].to_string(index=False))
            
            # 시각화 생성
            self.tracker.create_correlation_plot()
            
        except FileNotFoundError:
            print("실험 결과 파일이 없습니다.")
        except Exception as e:
            print(f"분석 실패: {e}")
    
    def recommend_ensemble(self):
        """앙상블 후보 추천"""
        try:
            df = pd.read_csv('enhanced_experiment_results.csv')
            submitted = df[df['aistages_submitted'] == True]

            if len(submitted) < 3:
                print('앙상블 분석을 위한 제출 데이터가 부족합니다 (최소 3개 필요).')
                return

            print('\n🎯 앙상블 후보 추천')
            print('='*40)
            
            # 앙상블 추천 기준
            ensemble_candidates = df[df['recommended_for_ensemble'] == True]
            
            if len(ensemble_candidates) == 0:
                print('추천된 앙상블 후보가 없습니다.')
                print('상위 성능 모델들을 기반으로 추천:')
                top_models = submitted.nlargest(5, 'aistages_public_score')
                print(top_models[['experiment_id', 'aistages_public_score', 'model_name', 'lr', 'augmentation_level']].to_string(index=False))
            else:
                print(f'추천된 앙상블 후보: {len(ensemble_candidates)}개')
                print(ensemble_candidates[['experiment_id', 'aistages_public_score', 'final_f1', 'model_name', 'overfitting_risk']].to_string(index=False))
                
                # 앙상블 전략 추천
                print('\n📋 앙상블 전략 추천:')
                models = ensemble_candidates['model_name'].value_counts()
                print(f'1. 모델 다양성: {len(models)}개 모델 타입')
                print(f'2. 평균 서버 점수: {ensemble_candidates["aistages_public_score"].mean():.4f}')
                low_risk_count = len(ensemble_candidates[ensemble_candidates["overfitting_risk"] == "low"])
                print(f'3. 과적합 위험 낮은 모델: {low_risk_count}개')

            # 최고 성과 전략 분석
            strategies = self.tracker.analyze_best_strategies()
            if 'best_models' in strategies:
                print('\n🏆 최고 성과 전략 분석:')
                print(f'최고 모델: {list(strategies["best_models"].keys())}')
                print(f'최고 학습률: {list(strategies["best_learning_rates"].keys())}')
                print(f'최고 증강 레벨: {list(strategies["best_augmentation"].keys())}')
                
        except FileNotFoundError:
            print("실험 결과 파일이 없습니다.")
        except Exception as e:
            print(f"앙상블 분석 실패: {e}")
    
    def generate_report(self):
        """전체 리포트 생성"""
        print("\n📋 리포트 타입을 선택하세요:")
        print("1) 간단 요약 리포트")
        print("2) 제출용 상세 리포트")
        print("3) 전체 분석 리포트")
        
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            self.tracker.sync_from_basic_results()
            self.tracker.print_enhanced_summary()
        
        elif choice == "2":
            experiment_ids = input("제출할 실험 ID들을 입력하세요 (쉼표로 구분): ").strip()
            if experiment_ids:
                ids = [id.strip() for id in experiment_ids.split(',')]
                self.tracker.create_submission_report(ids, 'submission_report.html')
                print('📄 제출용 리포트 생성: submission_report.html')
            else:
                print('❌ 실험 ID가 입력되지 않았습니다.')
        
        elif choice == "3":
            self._create_full_analysis_report()
        
        else:
            print("❌ 잘못된 선택입니다.")
    
    def _create_full_analysis_report(self):
        """전체 분석 리포트 생성"""
        try:
            self.tracker.sync_from_basic_results()
            df = pd.read_csv('enhanced_experiment_results.csv')
            submitted = df[df['aistages_submitted'] == True]

            html_content = f'''
            <html>
            <head>
                <title>HPO + AIStages 전체 분석 리포트</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .success {{ background-color: #d4edda; }}
                    .warning {{ background-color: #fff3cd; }}
                    .danger {{ background-color: #f8d7da; }}
                </style>
            </head>
            <body>
                <h1>🎯 HPO + AIStages 전체 분석 리포트</h1>
                <p>생성일시: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                
                <h2>📊 실험 현황</h2>
                <ul>
                    <li>전체 HPO 실험: {len(df)}개</li>
                    <li>완료된 실험: {len(df[df["status"] == "completed"])}개</li>
                    <li>AIStages 제출: {len(submitted)}개</li>
                    <li>성공률: {len(df[df["status"] == "completed"]) / len(df) * 100 if len(df) > 0 else 0:.1f}%</li>
                </ul>
            '''

            if len(submitted) > 0:
                correlation = submitted['final_f1'].corr(submitted['aistages_public_score']) if len(submitted) >= 2 else 0
                html_content += f'''
                <h2>🏆 AIStages 성과</h2>
                <ul>
                    <li>최고 서버 점수: {submitted["aistages_public_score"].max():.4f}</li>
                    <li>평균 서버 점수: {submitted["aistages_public_score"].mean():.4f}</li>
                    <li>로컬-서버 상관관계: {correlation:.3f}</li>
                    <li>과적합 위험 높음: {len(submitted[submitted["overfitting_risk"] == "high"])}개</li>
                </ul>
                
                <h2>📈 제출된 실험 결과</h2>
                {submitted[["experiment_id", "aistages_public_score", "final_f1", "score_difference_public", "model_name", "overfitting_risk"]].to_html(index=False)}
                '''

            completed = df[df['status'] == 'completed']
            if len(completed) > 0:
                html_content += f'''
                <h2>🔬 전체 완료 실험</h2>
                {completed[["experiment_id", "final_f1", "val_accuracy", "model_name", "lr", "augmentation_level", "TTA"]].to_html(index=False)}
                '''

            html_content += '''
            </body>
            </html>
            '''

            with open('full_analysis_report.html', 'w', encoding='utf-8') as f:
                f.write(html_content)

            print('📄 전체 분석 리포트 생성: full_analysis_report.html')
            
        except Exception as e:
            print(f"리포트 생성 실패: {e}")
    
    def run(self):
        """메인 실행 루프"""
        print("🎯 AIStages 대회 관리 시스템에 오신 것을 환영합니다!")
        
        # 환경 확인
        if not Path("experiment_results.csv").exists() and not Path("enhanced_experiment_results.csv").exists():
            print("⚠️ 실험 결과 파일이 없습니다. 먼저 HPO 실험을 실행하세요.")
        
        while True:
            self.show_menu()
            choice = input("\n선택하세요 (0-8): ").strip()
            
            try:
                if choice == "1":
                    self.run_hpo_experiments()
                elif choice == "2":
                    self.check_results()
                elif choice == "3":
                    self.recommend_candidates()
                elif choice == "4":
                    self.prepare_submission()
                elif choice == "5":
                    self.record_result()
                elif choice == "6":
                    self.analyze_correlation()
                elif choice == "7":
                    self.recommend_ensemble()
                elif choice == "8":
                    self.generate_report()
                elif choice == "0":
                    print("✅ 시스템 종료")
                    break
                else:
                    print("❌ 잘못된 선택입니다. 0-8 사이의 숫자를 입력하세요.")
            
            except KeyboardInterrupt:
                print("\n\n⚠️ 사용자가 중단했습니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
            
            input("\n계속하려면 Enter를 누르세요...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 명령행 인자 처리
        manager = AIStagesManager()
        
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🎯 HPO + AIStages 통합 실험 시스템")
            print("\n사용법:")
            print("  python aistages_manager.py                # 대화형 메뉴 실행")
            print("  python aistages_manager.py quick          # 빠른 HPO 실험 실행")
            print("  python aistages_manager.py check          # 실험 결과 확인")
            print("  python aistages_manager.py submit <exp_id> # 특정 실험 제출 준비")
            print("\n주요 기능:")
            print("  - HPO 실험 자동 실행")
            print("  - AIStages 제출 후보 추천")
            print("  - 로컬 vs 서버 점수 분석")
            print("  - 과적합 위험도 평가")
            print("  - 앙상블 후보 추천")
            print("  - 종합 리포트 생성")
        
        elif sys.argv[1] == "quick":
            print("🚀 빠른 HPO 실험 실행")
            os.system("python start_hpo.py")
        
        elif sys.argv[1] == "check":
            manager.check_results()
        
        elif sys.argv[1] == "submit" and len(sys.argv) > 2:
            experiment_id = sys.argv[2]
            print(f"🚀 실험 {experiment_id} 제출 준비")
            instructions = manager.tracker.submit_to_aistages(experiment_id)
            print(instructions)
        
        else:
            print("❌ 잘못된 명령입니다. --help를 참조하세요.")
    
    else:
        # 대화형 모드
        manager = AIStagesManager()
        manager.run()
