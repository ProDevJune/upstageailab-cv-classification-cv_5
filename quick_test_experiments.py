#!/usr/bin/env python3
"""
간단한 테스트 실험 실행기
실제 긴 실험 전에 빠른 테스트로 모든 것이 정상 작동하는지 확인
"""

import sys
import os
import yaml
import tempfile
import subprocess
import time
from pathlib import Path
from datetime import datetime

class QuickTestRunner:
    """빠른 테스트 실험 실행기"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = []
        
    def create_test_config(self, model_name: str, category: str) -> str:
        """테스트용 설정 파일 생성 (매우 짧은 실행 시간)"""
        
        # 기본 설정 로드
        base_config_path = self.project_root / "codes/config_v2.yaml"
        
        try:
            with open(base_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except:
            # 기본 설정 생성
            config = {
                'data_dir': './data',
                'train_data': 'train0705a.csv',
                'epochs': 1,  # 테스트용: 1 에포크만
                'batch_size': 16,  # 작은 배치
                'image_size': 224,  # 작은 이미지
                'lr': 0.001,
                'patience': 1,
                'wandb': {'log': False},  # WandB 비활성화
                'val_split_ratio': 0.8,  # 작은 validation set
                'mixed_precision': False,  # 안정성 우선
                'test_TTA': False,
                'val_TTA': False
            }
        
        # 테스트용 설정 오버라이드
        test_config = config.copy()
        test_config.update({
            'model_name': model_name,
            'epochs': 2,  # verbose 검증을 위해 2 에포크로 설정
            'batch_size': min(config.get('batch_size', 32), 8),  # 더 작은 배치로 빠른 실행
            'patience': 2,  # epochs와 맞춤
            'wandb': {'log': False},  # WandB 비활성화
            'val_split_ratio': 0.9,  # validation 데이터 더 최소화 (90% train, 10% val)
            'experiment_id': f"test_{category}_{model_name.replace('.', '_')}_{datetime.now().strftime('%H%M%S')}",
            'mixed_precision': False,  # 안정성 우선
            'class_imbalance': False,  # 테스트용: 클래스 불균형 처리 비활성화
            'online_augmentation': False,  # 테스트용: 증강 비활성화
            'dynamic_augmentation': {'enabled': False},  # 동적 증강 비활성화
            'val_TTA': False,  # 테스트용: TTA 비활성화
            'test_TTA': False  # 테스트용: TTA 비활성화
        })
        
        # 카테고리별 테스트 설정
        if category == 'optimizer':
            test_config['optimizer_name'] = 'SGD'
            test_config['lr'] = 0.01
        elif category == 'loss_function':
            test_config['criterion'] = 'CrossEntropyLoss'
        elif category == 'scheduler':
            test_config['scheduler_name'] = 'StepLR'
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f, default_flow_style=False)
            return f.name
    
    def run_quick_test(self, model_name: str, category: str) -> dict:
        """빠른 테스트 실험 실행"""
        
        print(f"\n🧪 테스트 실험: {model_name} + {category}")
        print("-" * 50)
        
        result = {
            'model': model_name,
            'category': category,
            'status': 'running',
            'start_time': datetime.now(),
            'error': None,
            'execution_time': 0
        }
        
        try:
            # 테스트 설정 파일 생성
            test_config_path = self.create_test_config(model_name, category)
            print(f"   📄 테스트 설정: {test_config_path}")
            
            # PYTHONPATH에 프로젝트 루트 추가 (환경변수)
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root) + ':' + env.get('PYTHONPATH', '')
            
            # 실행 명령 결정
            if model_name == 'resnet50.tv2_in1k':
                cmd = ['python', 'codes/gemini_main_v2.py', '--config', test_config_path]
            else:
                # 다른 모델들은 gemini_main_v2.py 사용
                cmd = ['python', 'codes/gemini_main_v2.py', '--config', test_config_path]
            
            print(f"   🔧 실행 명령: {' '.join(cmd)}")
            print(f"   ⏳ 테스트 실행 중... (1-3분 예상)")
            
            # 실험 실행
            start_time = time.time()
            process = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300,  # 5분 타임아웃
                env=env  # 수정된 환경변수 사용
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            result['execution_time'] = execution_time
            
            if process.returncode == 0:
                print(f"   ✅ 테스트 성공! ({execution_time:.1f}초)")
                result['status'] = 'success'
            else:
                print(f"   ❌ 테스트 실패 (코드: {process.returncode})")
                result['status'] = 'failed'
                # 전체 오류 메시지 표시
                full_error = process.stderr if process.stderr else process.stdout
                result['error'] = full_error
                print(f"   🚨 전체 오류 메시지:")
                print(f"   {full_error}")
                
                # 오류를 파일로도 저장
                error_file = f"/tmp/test_error_{model_name.replace('.', '_')}_{category}.log"
                with open(error_file, 'w') as f:
                    f.write(f"명령: {' '.join(cmd)}\n")
                    f.write(f"STDOUT:\n{process.stdout}\n")
                    f.write(f"STDERR:\n{process.stderr}\n")
                print(f"   📄 상세 오류 로그: {error_file}")
            
            # 임시 파일 정리
            try:
                os.unlink(test_config_path)
            except:
                pass
                
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
            result['error'] = '테스트 시간 초과 (5분)'
            print(f"   ⏰ 테스트 시간 초과")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"   ❌ 테스트 오류: {e}")
        
        return result
    
    def run_comprehensive_test(self) -> bool:
        """포괄적인 빠른 테스트"""
        
        print("🧪 빠른 테스트 실험 시스템")
        print("=" * 60)
        print("🧪 빠른 테스트 실험 시작")
        print("=" * 60)
        print("ℹ️ 실제 긴 실험 전에 모든 컴포넌트가 정상 작동하는지 확인합니다.")
        print("⏱️ 각 테스트는 1-3분 소요되며, 전체 테스트는 5-10분 예상됩니다.")
        
        # 테스트할 조합들 (대표적인 것들만)
        test_combinations = [
            ('resnet50.tv2_in1k', 'optimizer'),
            ('efficientnet_b4.ra2_in1k', 'loss_function'),
            ('efficientnet_b3.ra2_in1k', 'scheduler'),
        ]
        
        all_tests_passed = True
        
        for model, category in test_combinations:
            result = self.run_quick_test(model, category)
            self.test_results.append(result)
            
            if result['status'] != 'success':
                all_tests_passed = False
        
        # 결과 요약
        print(f"\n📊 테스트 결과 요약")
        print("=" * 40)
        
        successful_tests = [r for r in self.test_results if r['status'] == 'success']
        failed_tests = [r for r in self.test_results if r['status'] != 'success']
        
        print(f"   성공: {len(successful_tests)}/{len(self.test_results)}개")
        print(f"   평균 실행 시간: {sum(r['execution_time'] for r in successful_tests) / len(successful_tests):.1f}초" if successful_tests else "   평균 실행 시간: N/A")
        
        if failed_tests:
            print(f"\n❌ 실패한 테스트들:")
            for test in failed_tests:
                print(f"   • {test['model']} + {test['category']}: {test['error'][:50]}...")
        
        if all_tests_passed:
            print(f"\n🎊 모든 테스트 통과! 본격적인 실험 실행 가능")
            return True
        else:
            print(f"\n⚠️ 일부 테스트 실패. 문제 해결 후 재시도 필요")
            return False
    
    def estimate_full_experiment_time(self) -> dict:
        """전체 실험 시간 추정"""
        
        if not self.test_results:
            return {'error': '테스트 결과가 없습니다'}
        
        successful_tests = [r for r in self.test_results if r['status'] == 'success']
        if not successful_tests:
            return {'error': '성공한 테스트가 없습니다'}
        
        # 평균 테스트 시간 (1 에포크)
        avg_test_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests)
        
        # 실제 실험 시간 추정 (50 에포크 기준)
        estimated_time_per_experiment = avg_test_time * 50
        
        # 전체 실험 수 추정 (4모델 × 6카테고리 × 평균 2.5옵션)
        total_experiments = 4 * 6 * 2.5
        total_estimated_time = estimated_time_per_experiment * total_experiments
        
        return {
            'test_time_per_epoch': avg_test_time,
            'estimated_time_per_experiment': estimated_time_per_experiment / 60,  # 분
            'total_experiments': total_experiments,
            'total_estimated_hours': total_estimated_time / 3600,
            'total_estimated_days': total_estimated_time / (3600 * 24)
        }

def main():
    """메인 실행 함수"""
    
    print("🧪 빠른 테스트 실험 시스템")
    print("=" * 50)
    
    runner = QuickTestRunner()
    
    # 빠른 테스트 실행
    success = runner.run_comprehensive_test()
    
    if success:
        # 전체 실험 시간 추정
        estimation = runner.estimate_full_experiment_time()
        
        if 'error' not in estimation:
            print(f"\n⏱️ 전체 실험 시간 추정:")
            print(f"   실험당 예상 시간: {estimation['estimated_time_per_experiment']:.1f}분")
            print(f"   총 실험 수: {estimation['total_experiments']:.0f}개")
            print(f"   총 예상 시간: {estimation['total_estimated_hours']:.1f}시간 ({estimation['total_estimated_days']:.1f}일)")
        
        print(f"\n🚀 실제 실험 실행 준비 완료!")
        print(f"   python hyperparameter_system/run_experiments.py")
        
        return 0
    else:
        print(f"\n❌ 테스트 실패. 문제 해결 후 재시도하세요.")
        return 1

if __name__ == "__main__":
    exit(main())
