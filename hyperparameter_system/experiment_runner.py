#!/usr/bin/env python3
"""
확장 가능한 하이퍼파라미터 실험 자동 실행 시스템
기존 V2 시스템과 완전 호환
"""

import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import yaml

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from hyperparameter_system.hyperparameter_configs import DynamicExperimentMatrix

class ExtensibleExperimentRunner:
    """확장 가능한 실험 자동 실행기"""
    
    def __init__(self, config_path: str = "hyperparameter_system/experiment_config.yaml"):
        self.project_root = Path(__file__).parent.parent
        self.matrix = DynamicExperimentMatrix(config_path)
        self.results_log = self.project_root / "experiment_results_extended.csv"
        
        # enhanced_experiment_tracker와 연동
        try:
            from enhanced_experiment_tracker import EnhancedExperimentTracker
            self.tracker = EnhancedExperimentTracker()
            print("✅ Enhanced Experiment Tracker 연동 완료")
        except ImportError:
            self.tracker = None
            print("⚠️ Enhanced Experiment Tracker를 찾을 수 없습니다")
        
        print(f"🎯 확장 가능한 실험 실행기 초기화 완료")
        print(f"📁 프로젝트 루트: {self.project_root}")
    
    def run_all_experiments(self) -> List[Dict[str, Any]]:
        """모든 활성화된 모델×카테고리 실험 실행"""
        experiments = self.matrix.generate_all_experiments()
        
        print(f"\n🚀 전체 실험 시작!")
        print(f"📊 총 실험 수: {len(experiments)}개")
        print(f"⏱️ 예상 소요 시간: {len(experiments) * 45}분 (실험당 45분 가정)")
        
        return self.execute_experiments(experiments)
    
    def run_model_experiments(self, model_names: List[str]) -> List[Dict[str, Any]]:
        """특정 모델들만 실험"""
        experiments = self.matrix.generate_selective_experiments(model_filter=model_names)
        
        print(f"\n🎯 특정 모델 실험 시작!")
        print(f"📊 대상 모델: {model_names}")
        print(f"📊 실험 수: {len(experiments)}개")
        
        return self.execute_experiments(experiments)
    
    def run_category_experiments(self, category_names: List[str]) -> List[Dict[str, Any]]:
        """특정 카테고리들만 실험"""
        experiments = self.matrix.generate_selective_experiments(category_filter=category_names)
        
        print(f"\n⚙️ 특정 카테고리 실험 시작!")
        print(f"📊 대상 카테고리: {category_names}")
        print(f"📊 실험 수: {len(experiments)}개")
        
        return self.execute_experiments(experiments)
    
    def run_custom_experiments(self, model_names: List[str], category_names: List[str]) -> List[Dict[str, Any]]:
        """특정 모델×카테고리 조합만 실험"""
        experiments = self.matrix.generate_selective_experiments(
            model_filter=model_names,
            category_filter=category_names
        )
        
        print(f"\n🎯 맞춤형 실험 시작!")
        print(f"📊 대상 모델: {model_names}")
        print(f"📊 대상 카테고리: {category_names}")
        print(f"📊 실험 수: {len(experiments)}개")
        
        return self.execute_experiments(experiments)
    
    def execute_experiments(self, experiments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """실험들 순차 실행"""
        results = []
        successful_runs = 0
        
        for i, experiment in enumerate(experiments, 1):
            print(f"\n📊 진행률: {i}/{len(experiments)}")
            
            result = self.run_single_experiment(experiment)
            results.append(result)
            
            if result['status'] == 'completed':
                successful_runs += 1
            
            # 성공률 출력
            success_rate = successful_runs / i * 100
            print(f"   현재 성공률: {success_rate:.1f}% ({successful_runs}/{i})")
            
            # 실험 간 대기
            if i < len(experiments):
                print(f"   ⏳ 다음 실험까지 2초 대기...")
                time.sleep(2)
        
        print(f"\n🎊 모든 실험 완료!")
        print(f"📊 최종 결과: {successful_runs}/{len(experiments)} 성공 ({successful_runs/len(experiments)*100:.1f}%)")
        
        return results
    
    def run_single_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        """단일 실험 실행"""
        model = experiment['model']
        category = experiment['category']
        option = experiment['option']
        experiment_id = experiment['config']['experiment_id']
        
        print(f"\n🚀 실험 {experiment['id']}/{len(experiment)} 시작")
        print(f"   ID: {experiment_id}")
        print(f"   모델: {model['name']}")
        print(f"   카테고리: {category.name}")
        print(f"   옵션: {category.get_option_summary(option)}")
        
        # 결과 초기화
        result = {
            'experiment_id': experiment_id,
            'model_name': model['name'],
            'category': category.name,
            'option': option,
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'error_message': None,
            'config_path': None,
            'execution_time': 0
        }
        
        try:
            # 임시 설정 파일 생성
            temp_config_path = self.matrix.create_temp_config_file(experiment)
            result['config_path'] = temp_config_path
            
            print(f"   📄 설정 파일: {temp_config_path}")
            
            # 실행 명령 결정
            if model['script'].endswith('.sh'):
                # 쉘 스크립트 실행 (기존 V2 시스템 스크립트들)
                cmd = [model['script']]
                # 설정 파일을 환경변수로 전달
                env = os.environ.copy()
                env['EXPERIMENT_CONFIG'] = temp_config_path
            else:
                # Python 스크립트 실행
                cmd = model['script'].split() + ['--config', temp_config_path]
                env = None
            
            print(f"   🔧 실행 명령: {' '.join(cmd)}")
            
            # 실험 실행
            start_time = time.time()
            process = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=self.matrix.config['execution'].get('experiment_timeout', 3600),
                env=env
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            result['execution_time'] = execution_time
            
            if process.returncode == 0:
                print(f"   ✅ 실험 완료! ({execution_time:.1f}초)")
                
                # 출력에서 성능 메트릭 추출
                f1_score = self._extract_f1_score(process.stdout)
                accuracy = self._extract_accuracy(process.stdout)
                
                result.update({
                    'status': 'completed',
                    'f1_score': f1_score,
                    'accuracy': accuracy,
                    'stdout_sample': process.stdout[-200:] if process.stdout else None
                })
                
                print(f"   📊 F1: {f1_score:.4f}, 정확도: {accuracy:.2f}%")
                
                # Enhanced Tracker와 연동
                if self.tracker:
                    try:
                        # 기존 추적 시스템에 결과 기록
                        pass  # 구체적인 연동 로직은 추후 구현
                    except Exception as e:
                        print(f"   ⚠️ Tracker 연동 실패: {e}")
                
            else:
                print(f"   ❌ 실험 실패 (코드: {process.returncode})")
                result.update({
                    'status': 'failed',
                    'error_message': process.stderr[-500:] if process.stderr else "Unknown error"
                })
                print(f"   🚨 오류: {result['error_message'][:100]}...")
            
            # 임시 파일 정리
            try:
                os.remove(temp_config_path)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            result.update({
                'status': 'timeout',
                'execution_time': self.matrix.config['execution'].get('experiment_timeout', 3600),
                'error_message': "실험 시간 초과"
            })
            print(f"   ⏰ 실험 시간 초과")
            
        except Exception as e:
            result.update({
                'status': 'error',
                'execution_time': time.time() - start_time if 'start_time' in locals() else 0,
                'error_message': str(e)
            })
            print(f"   ❌ 실험 오류: {e}")
        
        # 결과 기록
        self._save_experiment_result(result)
        
        return result
    
    def _extract_f1_score(self, output: str) -> float:
        """출력에서 F1 점수 추출"""
        try:
            import re
            f1_pattern = r'f1[\s:=]+(\d+\.\d+)'
            matches = re.findall(f1_pattern, output, re.IGNORECASE)
            if matches:
                return float(matches[-1])
            return 0.0
        except:
            return 0.0
    
    def _extract_accuracy(self, output: str) -> float:
        """출력에서 정확도 추출"""
        try:
            import re
            acc_pattern = r'acc[uracy]*[\s:=]+(\d+\.\d+)'
            matches = re.findall(acc_pattern, output, re.IGNORECASE)
            if matches:
                return float(matches[-1])
            return 0.0
        except:
            return 0.0
    
    def _save_experiment_result(self, result: Dict[str, Any]) -> None:
        """실험 결과 저장"""
        try:
            import pandas as pd
            
            # CSV 파일에 결과 추가
            if self.results_log.exists():
                df = pd.read_csv(self.results_log)
                new_row = pd.DataFrame([result])
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = pd.DataFrame([result])
            
            df.to_csv(self.results_log, index=False)
            
        except Exception as e:
            print(f"   ⚠️ 결과 저장 실패: {e}")
    
    def get_experiment_summary(self) -> Dict[str, Any]:
        """실험 결과 요약"""
        try:
            import pandas as pd
            
            if not self.results_log.exists():
                return {'message': '실험 결과가 없습니다.'}
            
            df = pd.read_csv(self.results_log)
            
            if df.empty:
                return {'message': '실험 결과가 없습니다.'}
            
            summary = {
                'total_experiments': len(df),
                'completed': len(df[df['status'] == 'completed']),
                'failed': len(df[df['status'] == 'failed']),
                'timeout': len(df[df['status'] == 'timeout']),
                'error': len(df[df['status'] == 'error']),
            }
            
            completed_df = df[df['status'] == 'completed']
            if not completed_df.empty:
                summary.update({
                    'best_f1': completed_df['f1_score'].max(),
                    'avg_f1': completed_df['f1_score'].mean(),
                    'best_accuracy': completed_df['accuracy'].max(),
                    'avg_execution_time': completed_df['execution_time'].mean() / 60  # 분 단위
                })
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="확장 가능한 하이퍼파라미터 실험 실행")
    parser.add_argument('--models', nargs='+', help='실험할 모델들 (예: resnet50.tv2_in1k efficientnet_b4)')
    parser.add_argument('--categories', nargs='+', help='실험할 카테고리들 (예: optimizer loss_function)')
    parser.add_argument('--all', action='store_true', help='모든 실험 실행')
    parser.add_argument('--summary', action='store_true', help='실험 결과 요약만 출력')
    parser.add_argument('--matrix', action='store_true', help='실험 매트릭스만 출력')
    
    args = parser.parse_args()
    
    # 실험 실행기 초기화
    runner = ExtensibleExperimentRunner()
    
    if args.summary:
        # 실험 결과 요약 출력
        summary = runner.get_experiment_summary()
        print("\n📊 실험 결과 요약:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        return
    
    if args.matrix:
        # 실험 매트릭스만 출력
        runner.matrix.print_experiment_matrix()
        return
    
    # 실험 실행
    if args.all:
        # 모든 실험 실행
        results = runner.run_all_experiments()
    elif args.models and args.categories:
        # 특정 모델×카테고리 실험
        results = runner.run_custom_experiments(args.models, args.categories)
    elif args.models:
        # 특정 모델 실험
        results = runner.run_model_experiments(args.models)
    elif args.categories:
        # 특정 카테고리 실험
        results = runner.run_category_experiments(args.categories)
    else:
        # 대화형 모드
        runner.matrix.print_experiment_matrix()
        
        print(f"\n🎯 실험 실행 옵션:")
        print(f"1. 모든 실험 실행")
        print(f"2. 특정 모델만 실험")
        print(f"3. 특정 카테고리만 실험")
        print(f"4. 맞춤형 실험")
        print(f"0. 종료")
        
        choice = input("\n선택하세요 (0-4): ").strip()
        
        if choice == '1':
            results = runner.run_all_experiments()
        elif choice == '2':
            models = input("모델 이름들 (공백으로 구분): ").strip().split()
            results = runner.run_model_experiments(models)
        elif choice == '3':
            categories = input("카테고리 이름들 (공백으로 구분): ").strip().split()
            results = runner.run_category_experiments(categories)
        elif choice == '4':
            models = input("모델 이름들 (공백으로 구분): ").strip().split()
            categories = input("카테고리 이름들 (공백으로 구분): ").strip().split()
            results = runner.run_custom_experiments(models, categories)
        else:
            print("👋 종료합니다.")
            return
    
    # 최종 요약
    summary = runner.get_experiment_summary()
    print(f"\n📊 최종 실험 요약:")
    for key, value in summary.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    main()
