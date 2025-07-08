#!/usr/bin/env python3
"""
개선된 train.csv 기반 실험 추적 시스템 v2
전체 실행 과정을 체계적으로 관리하고 기록
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import subprocess
import json
import os

class ExperimentTrackerV2:
    def __init__(self):
        self.base_dir = Path("")
        self.results_file = self.base_dir / "experiment_results_v2.json"
        self.csv_log = self.base_dir / "submission_paths_v2.csv"
        self.phase = 1
        self.step = 1
        
        # 기존 점수 (참고용)
        self.baseline_scores = {
            'EfficientNet-B4': {'local': 0.9419, 'server': 0.8619, 'exp_id': '2507051934'},
            'EfficientNet-B3': {'local': 0.9187, 'server': 0.8526, 'exp_id': '2507052111'},
            'ConvNeXt-Base': {'local': 0.9346, 'server': 0.8158, 'exp_id': '2507052151'}
        }
        
        self.load_existing_results()
    
    def load_existing_results(self):
        """기존 결과 로드"""
        if self.results_file.exists():
            with open(self.results_file, 'r', encoding='utf-8') as f:
                self.results = json.load(f)
        else:
            self.results = {
                'start_time': datetime.now().isoformat(),
                'train_csv_version': 'improved_v2',
                'baseline_comparison': self.baseline_scores,
                'experiments': {},
                'ensembles': {}
            }
    
    def save_results(self):
        """결과 저장"""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    def print_phase_header(self, phase_num, phase_name):
        """단계별 헤더 출력"""
        print("\\n" + "="*70)
        print(f"🚀 Phase {phase_num}: {phase_name}")
        print("="*70)
        self.phase = phase_num
        self.step = 1
    
    def print_step_header(self, step_name):
        """스텝별 헤더 출력"""
        print(f"\\n📋 Phase {self.phase}.{self.step}: {step_name}")
        print("-" * 50)
        self.step += 1
    
    def record_experiment(self, model_name, exp_id, local_score=None, server_score=None, csv_path=None):
        """실험 결과 기록"""
        self.results['experiments'][model_name] = {
            'exp_id': exp_id,
            'local_score': local_score,
            'server_score': server_score,
            'csv_path': str(csv_path) if csv_path else None,
            'timestamp': datetime.now().isoformat(),
            'baseline_comparison': {
                'local_diff': (local_score - self.baseline_scores[model_name]['local']) if local_score else None,
                'server_diff': (server_score - self.baseline_scores[model_name]['server']) if server_score else None
            }
        }
        self.save_results()
    
    def record_ensemble(self, ensemble_name, csv_path, models_used, expected_score=None):
        """앙상블 결과 기록"""
        self.results['ensembles'][ensemble_name] = {
            'csv_path': str(csv_path),
            'models_used': models_used,
            'expected_score': expected_score,
            'timestamp': datetime.now().isoformat()
        }
        self.save_results()
    
    def generate_submission_memo(self, model_name, is_ensemble=False, ensemble_type=None):
        """대회 제출용 메모 생성"""
        if is_ensemble:
            if ensemble_type == "2models":
                return f"{ensemble_type.upper()} 앙상블 B4+B3 - 320px + Minimal aug - No TTA (개선된 데이터v2)"
            elif ensemble_type == "3models":
                return f"{ensemble_type.upper()} 앙상블 B4+B3+ConvNeXt - 320px + Minimal aug - No TTA (개선된 데이터v2)"
        else:
            return f"{model_name} - 320px + Minimal aug - No TTA (개선된 데이터v2)"
    
    def print_submission_info(self, csv_path, memo):
        """제출 정보 출력"""
        print(f"\\n📤 제출 정보:")
        print(f"   📁 파일: {csv_path}")
        print(f"   📝 메모: {memo}")
        print(f"   ⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # CSV 로그에 기록
        log_entry = pd.DataFrame([{
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_path': csv_path,
            'submission_memo': memo,
            'phase': f"Phase{self.phase}",
            'status': 'ready_for_submission'
        }])
        
        if self.csv_log.exists():
            existing_log = pd.read_csv(self.csv_log)
            updated_log = pd.concat([existing_log, log_entry], ignore_index=True)
        else:
            updated_log = log_entry
        
        updated_log.to_csv(self.csv_log, index=False)
    
    def find_experiment_results(self, model_pattern):
        """실험 결과 파일 찾기"""
        submissions_dir = self.base_dir / "data" / "submissions"
        
        if not submissions_dir.exists():
            return None
        
        # 최신 결과 찾기
        latest_dir = None
        latest_time = None
        
        for item in submissions_dir.iterdir():
            if item.is_dir() and model_pattern in item.name:
                # 타임스탬프 추출
                try:
                    timestamp_str = item.name.split('-')[0]
                    timestamp = datetime.strptime(timestamp_str, '%y%m%d%H%M')
                    
                    if latest_time is None or timestamp > latest_time:
                        latest_time = timestamp
                        latest_dir = item
                except:
                    continue
        
        if latest_dir:
            csv_files = list(latest_dir.glob("*.csv"))
            if csv_files:
                return {
                    'exp_id': latest_dir.name.split('-')[0],
                    'csv_path': csv_files[0],
                    'dir_name': latest_dir.name
                }
        
        return None
    
    def print_comparison_table(self):
        """기존 결과 대비 비교표 출력"""
        print("\\n📊 성능 비교 (기존 vs 개선 데이터v2)")
        print("="*80)
        print(f"{'모델명':<20} {'기존 로컬':<12} {'기존 서버':<12} {'새 로컬':<12} {'새 서버':<12} {'개선량':<12}")
        print("-"*80)
        
        for model_name in ['EfficientNet-B4', 'EfficientNet-B3', 'ConvNeXt-Base']:
            baseline = self.baseline_scores[model_name]
            new_result = self.results['experiments'].get(model_name, {})
            
            new_local = new_result.get('local_score', 'TBD')
            new_server = new_result.get('server_score', 'TBD')
            
            if isinstance(new_server, (int, float)) and baseline['server']:
                improvement = f"{new_server - baseline['server']:+.4f}"
            else:
                improvement = "TBD"
            
            print(f"{model_name:<20} {baseline['local']:<12.4f} {baseline['server']:<12.4f} {new_local if isinstance(new_local, str) else f'{new_local:.4f}':<12} {new_server if isinstance(new_server, str) else f'{new_server:.4f}':<12} {improvement:<12}")

def create_execution_guide():
    """체계적인 실행 가이드 생성"""
    tracker = ExperimentTrackerV2()
    
    print("🎯 개선된 train.csv 기반 CV Classification 완전 재실행 가이드")
    print("="*80)
    print("📝 이 가이드는 새로운 train.csv 데이터로 전체 파이프라인을 재실행합니다.")
    print("⚠️ 기존 결과와 혼동을 방지하기 위해 모든 결과에 'v2' 태그가 붙습니다.")
    
    # Phase 1: 개별 모델 재학습
    tracker.print_phase_header(1, "개별 모델 재학습")
    
    print("🎯 황금조합 설정:")
    print("   • 이미지 크기: 320px")
    print("   • 증강: Minimal (eda=true, 나머지 false)")
    print("   • TTA: False (No TTA)")
    print("   • 데이터: 개선된 train.csv v2")
    
    # 1.1 EfficientNet-B4
    tracker.print_step_header("EfficientNet-B4 재학습")
    print("🔧 실행 명령:")
    print("   ./run_absolute.sh")
    print()
    
    memo_b4 = tracker.generate_submission_memo("EfficientNet-B4")
    print(f"📝 예상 제출 메모: '{memo_b4}'")
    print(f"📊 기준 성능: 로컬 0.9419 / 서버 0.8619")
    print(f"🎯 목표: 서버 0.865+ (개선 +0.003)")
    
    # 1.2 EfficientNet-B3
    tracker.print_step_header("EfficientNet-B3 재학습")
    print("🔧 실행 명령:")
    print("   ./run_b3.sh")
    print()
    
    memo_b3 = tracker.generate_submission_memo("EfficientNet-B3")
    print(f"📝 예상 제출 메모: '{memo_b3}'")
    print(f"📊 기준 성능: 로컬 0.9187 / 서버 0.8526")
    print(f"🎯 목표: 서버 0.855+ (개선 +0.002)")
    
    # 1.3 ConvNeXt-Base
    tracker.print_step_header("ConvNeXt-Base 재학습")
    print("🔧 실행 명령:")
    print("   ./run_convnext.sh")
    print()
    
    memo_convnext = tracker.generate_submission_memo("ConvNeXt-Base")
    print(f"📝 예상 제출 메모: '{memo_convnext}'")
    print(f"📊 기준 성능: 로컬 0.9346 / 서버 0.8158")
    print(f"🎯 목표: 서버 0.820+ (개선 +0.004)")
    
    # Phase 2: 앙상블 구성
    tracker.print_phase_header(2, "앙상블 구성")
    
    # 2.1 B4 단독 제출
    tracker.print_step_header("EfficientNet-B4 단독 제출")
    print("📁 파일: Phase 1.1의 결과 CSV 사용")
    print("📝 메모: EfficientNet-B4 단독 (개선된 데이터v2 최고성능)")
    
    # 2.2 2모델 앙상블
    tracker.print_step_header("2모델 앙상블 (B4+B3)")
    print("🔧 실행 명령:")
    print("   python ensemble_2models_v2.py")
    print()
    
    memo_2models = tracker.generate_submission_memo("", True, "2models")
    print(f"📝 예상 제출 메모: '{memo_2models}'")
    print(f"📊 예상 성능: 서버 0.860+ (vs B4 단독)")
    
    # 2.3 3모델 앙상블
    tracker.print_step_header("3모델 앙상블 (B4+B3+ConvNeXt)")
    print("🔧 실행 명령:")
    print("   python ensemble_3models_v2.py")
    print()
    
    memo_3models = tracker.generate_submission_memo("", True, "3models")
    print(f"📝 예상 제출 메모: '{memo_3models}'")
    print(f"📊 예상 성능: 서버 0.865+ (최종 목표)")
    
    # 실행 체크리스트
    print("\\n" + "="*70)
    print("📋 실행 체크리스트")
    print("="*70)
    
    checklist = [
        "[ ] Phase 1.1: ./run_absolute.sh 실행 (EfficientNet-B4)",
        "[ ] Phase 1.2: ./run_b3.sh 실행 (EfficientNet-B3)",
        "[ ] Phase 1.3: ./run_convnext.sh 실행 (ConvNeXt-Base)",
        "[ ] Phase 2.1: B4 단독 제출",
        "[ ] Phase 2.2: python ensemble_2models_v2.py 실행",
        "[ ] Phase 2.3: python ensemble_3models_v2.py 실행",
        "[ ] 각 단계별 서버 점수 기록",
        "[ ] 기존 결과 대비 개선량 확인"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    # 추적 시스템 안내
    print("\\n📊 추적 시스템:")
    print(f"   • 상세 로그: {tracker.results_file}")
    print(f"   • 제출 기록: {tracker.csv_log}")
    print(f"   • 비교 분석: tracker.print_comparison_table() 호출")
    
    print("\\n🚀 시작하려면 다음 명령을 실행하세요:")
    print("   ./run_absolute.sh")
    
    return tracker

if __name__ == "__main__":
    create_execution_guide()
