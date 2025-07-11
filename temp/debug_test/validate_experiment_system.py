#!/usr/bin/env python3
"""
확장 가능한 하이퍼파라미터 실험 시스템 사전 검증 스크립트
Mac/Ubuntu 환경을 자동 인식하여 MPS/CUDA 사용 가능성과 모든 요구사항을 검증
"""

import sys
import os
import platform
import subprocess
import importlib
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class ExperimentSystemValidator:
    """실험 시스템 사전 검증기"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.validation_results = {
            'system_info': {},
            'python_env': {},
            'packages': {},
            'hardware': {},
            'file_structure': {},
            'configs': {},
            'scripts': {},
            'disk_space': {},
            'memory': {},
            'estimated_runtime': {},
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }
        
    def run_full_validation(self) -> Dict[str, Any]:
        """전체 검증 실행"""
        print("🔍 확장 가능한 하이퍼파라미터 실험 시스템 사전 검증 시작")
        print("=" * 80)
        
        # 1. 시스템 환경 검증
        self._validate_system_environment()
        
        # 2. Python 환경 검증
        self._validate_python_environment()
        
        # 3. 필수 패키지 검증
        self._validate_required_packages()
        
        # 4. 하드웨어 및 성능 검증
        self._validate_hardware_requirements()
        
        # 5. 파일 구조 검증
        self._validate_file_structure()
        
        # 6. 설정 파일 검증
        self._validate_config_files()
        
        # 7. 실행 스크립트 검증
        self._validate_execution_scripts()
        
        # 8. 디스크 공간 검증
        self._validate_disk_space()
        
        # 9. 메모리 요구사항 검증
        self._validate_memory_requirements()
        
        # 10. 실행 시간 추정
        self._estimate_execution_time()
        
        # 11. 최종 검증 결과
        self._generate_final_report()
        
        return self.validation_results
    
    def _validate_system_environment(self):
        """시스템 환경 검증"""
        print("\n🖥️  시스템 환경 검증")
        print("-" * 40)
        
        # OS 정보
        os_info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'platform': platform.platform(),
            'python_version': platform.python_version()
        }
        
        self.validation_results['system_info'] = os_info
        
        print(f"   OS: {os_info['system']} ({os_info['machine']})")
        print(f"   Python: {os_info['python_version']}")
        
        # Mac/Ubuntu 자동 인식
        if os_info['system'] == 'Darwin':
            print("   ✅ macOS 환경 감지")
            self.validation_results['system_info']['environment'] = 'macOS'
            self.validation_results['system_info']['expected_device'] = 'MPS'
        elif os_info['system'] == 'Linux':
            print("   ✅ Linux 환경 감지")
            self.validation_results['system_info']['environment'] = 'Linux'
            self.validation_results['system_info']['expected_device'] = 'CUDA'
        else:
            print("   ⚠️ 지원되지 않는 OS")
            self.validation_results['warnings'].append("지원되지 않는 운영체제")
    
    def _validate_python_environment(self):
        """Python 환경 검증"""
        print("\n🐍 Python 환경 검증")
        print("-" * 40)
        
        # Python 버전 확인
        python_version = sys.version_info
        if python_version >= (3, 8):
            print(f"   ✅ Python 버전: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print(f"   ❌ Python 버전 부족: {python_version.major}.{python_version.minor}.{python_version.micro}")
            self.validation_results['critical_issues'].append("Python 3.8+ 필요")
        
        # 가상환경 확인
        venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        if venv_active:
            print("   ✅ 가상환경 활성화됨")
        else:
            print("   ⚠️ 가상환경이 활성화되지 않음")
            self.validation_results['warnings'].append("가상환경 사용 권장")
        
        self.validation_results['python_env'] = {
            'version': f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            'venv_active': venv_active,
            'executable': sys.executable
        }
    
    def _validate_required_packages(self):
        """필수 패키지 검증"""
        print("\n📦 필수 패키지 검증")
        print("-" * 40)
        
        # 필수 패키지 목록
        required_packages = {
            'torch': '1.9.0',
            'torchvision': '0.10.0',
            'timm': '0.6.0',
            'albumentations': '1.0.0',
            'opencv-python': '4.5.0',
            'pandas': '1.3.0',
            'numpy': '1.20.0',
            'scikit-learn': '1.0.0',
            'matplotlib': '3.3.0',
            'seaborn': '0.11.0',
            'tqdm': '4.60.0',
            'wandb': '0.12.0',
            'yaml': None,  # PyYAML
            'PIL': None,   # Pillow
        }
        
        package_status = {}
        missing_packages = []
        
        for package, min_version in required_packages.items():
            try:
                if package == 'yaml':
                    import yaml as pkg
                elif package == 'PIL':
                    from PIL import Image as pkg
                elif package == 'opencv-python':
                    import cv2 as pkg
                elif package == 'scikit-learn':
                    import sklearn as pkg
                else:
                    pkg = importlib.import_module(package)
                
                # 버전 확인
                version = getattr(pkg, '__version__', 'unknown')
                package_status[package] = {'installed': True, 'version': version}
                print(f"   ✅ {package}: {version}")
                
            except ImportError:
                package_status[package] = {'installed': False, 'version': None}
                missing_packages.append(package)
                print(f"   ❌ {package}: 설치되지 않음")
        
        self.validation_results['packages'] = {
            'status': package_status,
            'missing': missing_packages,
            'total_required': len(required_packages),
            'installed': len(required_packages) - len(missing_packages)
        }
        
        if missing_packages:
            self.validation_results['critical_issues'].append(f"누락된 패키지: {missing_packages}")
    
    def _validate_hardware_requirements(self):
        """하드웨어 및 성능 검증"""
        print("\n🔧 하드웨어 및 성능 검증")
        print("-" * 40)
        
        # PyTorch 디바이스 확인
        try:
            import torch
            
            # CPU 확인
            print(f"   CPU: {platform.processor()}")
            
            # GPU 확인
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                print(f"   ✅ CUDA 사용 가능: {gpu_count}개 GPU")
                
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                    print(f"     GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
                
                device_type = 'CUDA'
                
            elif torch.backends.mps.is_available():
                print("   ✅ Apple MPS 사용 가능")
                device_type = 'MPS'
                
            else:
                print("   ⚠️ CPU만 사용 가능")
                device_type = 'CPU'
                self.validation_results['warnings'].append("GPU 가속 불가능")
            
            # 간단한 성능 테스트
            device = torch.device(device_type.lower() if device_type != 'CPU' else 'cpu')
            
            print(f"   🧪 성능 테스트 중... (디바이스: {device})")
            start_time = __import__('time').time()
            
            # 간단한 연산 테스트
            x = torch.randn(1000, 1000, device=device)
            y = torch.mm(x, x.t())
            
            test_time = __import__('time').time() - start_time
            print(f"   ⏱️ 연산 테스트: {test_time:.3f}초")
            
            self.validation_results['hardware'] = {
                'device_type': device_type,
                'device_available': True,
                'performance_test_time': test_time,
                'gpu_count': gpu_count if device_type == 'CUDA' else 0,
                'estimated_speed': 'fast' if test_time < 0.1 else 'medium' if test_time < 0.5 else 'slow'
            }
            
        except Exception as e:
            print(f"   ❌ 하드웨어 검증 실패: {e}")
            self.validation_results['critical_issues'].append(f"하드웨어 검증 실패: {e}")
    
    def _validate_file_structure(self):
        """파일 구조 검증"""
        print("\n📁 파일 구조 검증")
        print("-" * 40)
        
        required_files = {
            'hyperparameter_system/experiment_config.yaml': '마스터 설정 파일',
            'hyperparameter_system/hyperparameter_configs.py': '실험 매트릭스 생성기',
            'hyperparameter_system/experiment_runner.py': '실험 실행기',
            'hyperparameter_system/run_experiments.py': '통합 실행 스크립트',
            'hyperparameter_system/categories/__init__.py': '카테고리 모듈',
            'codes/gemini_main_v2.py': 'V2 메인 실행 파일',
            'codes/config_v2.yaml': 'V2 설정 파일',
            'data/train.csv': '훈련 데이터 (또는 train0705a.csv)',
            'data/test/': '테스트 데이터 디렉토리',
            'data/train/': '훈련 이미지 디렉토리'
        }
        
        file_status = {}
        missing_files = []
        
        for file_path, description in required_files.items():
            full_path = self.project_root / file_path
            
            if full_path.exists():
                file_status[file_path] = {'exists': True, 'description': description}
                print(f"   ✅ {file_path}")
            else:
                file_status[file_path] = {'exists': False, 'description': description}
                missing_files.append(file_path)
                print(f"   ❌ {file_path}")
        
        # 대체 파일 확인
        alternative_train_files = ['data/train0705a.csv', 'data/train.csv']
        train_file_found = False
        for alt_file in alternative_train_files:
            if (self.project_root / alt_file).exists():
                print(f"   ✅ 훈련 데이터 발견: {alt_file}")
                train_file_found = True
                break
        
        if not train_file_found:
            missing_files.append('data/train.csv (또는 대체 파일)')
        
        self.validation_results['file_structure'] = {
            'status': file_status,
            'missing': missing_files,
            'train_data_found': train_file_found
        }
        
        if missing_files:
            self.validation_results['critical_issues'].append(f"누락된 파일: {missing_files}")
    
    def _validate_config_files(self):
        """설정 파일 검증"""
        print("\n⚙️ 설정 파일 검증")
        print("-" * 40)
        
        config_validations = {}
        
        # experiment_config.yaml 검증
        exp_config_path = self.project_root / 'hyperparameter_system/experiment_config.yaml'
        if exp_config_path.exists():
            try:
                with open(exp_config_path, 'r', encoding='utf-8') as f:
                    exp_config = yaml.safe_load(f)
                
                # 필수 섹션 확인
                required_sections = ['system', 'models', 'experiment_categories']
                missing_sections = [s for s in required_sections if s not in exp_config]
                
                if not missing_sections:
                    print("   ✅ experiment_config.yaml 구조 정상")
                    
                    # 활성화된 모델 수 확인
                    enabled_models = [m for m in exp_config['models'] if m.get('enabled', True)]
                    print(f"   ✅ 활성화된 모델: {len(enabled_models)}개")
                    
                    # 활성화된 카테고리 수 확인
                    enabled_categories = [c for c, cfg in exp_config['experiment_categories'].items() if cfg.get('enabled', True)]
                    print(f"   ✅ 활성화된 카테고리: {len(enabled_categories)}개")
                    
                    config_validations['experiment_config'] = {
                        'valid': True,
                        'enabled_models': len(enabled_models),
                        'enabled_categories': len(enabled_categories),
                        'estimated_experiments': len(enabled_models) * sum(len(cfg['options']) for cfg in exp_config['experiment_categories'].values() if cfg.get('enabled', True))
                    }
                    
                else:
                    print(f"   ❌ experiment_config.yaml 구조 오류: 누락된 섹션 {missing_sections}")
                    config_validations['experiment_config'] = {'valid': False, 'missing_sections': missing_sections}
                    
            except Exception as e:
                print(f"   ❌ experiment_config.yaml 파싱 오류: {e}")
                config_validations['experiment_config'] = {'valid': False, 'error': str(e)}
        
        # config_v2.yaml 검증
        v2_config_path = self.project_root / 'codes/config_v2.yaml'
        if v2_config_path.exists():
            try:
                with open(v2_config_path, 'r', encoding='utf-8') as f:
                    v2_config = yaml.safe_load(f)
                
                print("   ✅ config_v2.yaml 파싱 정상")
                config_validations['config_v2'] = {'valid': True}
                
            except Exception as e:
                print(f"   ❌ config_v2.yaml 파싱 오류: {e}")
                config_validations['config_v2'] = {'valid': False, 'error': str(e)}
        
        self.validation_results['configs'] = config_validations
    
    def _validate_execution_scripts(self):
        """실행 스크립트 검증"""
        print("\n🚀 실행 스크립트 검증")
        print("-" * 40)
        
        scripts_to_check = [
            'hyperparameter_system/run_experiments.py',
            'hyperparameter_system/experiment_runner.py',
            'codes/gemini_main_v2.py',
            'run_absolute.sh',
            'run_b3.sh',
            'run_code_v2.sh'
        ]
        
        script_status = {}
        
        for script in scripts_to_check:
            script_path = self.project_root / script
            
            if script_path.exists():
                # 실행 권한 확인 (Unix 계열)
                if hasattr(os, 'access'):
                    executable = os.access(script_path, os.X_OK)
                    if executable or script.endswith('.py'):
                        print(f"   ✅ {script}")
                        script_status[script] = {'exists': True, 'executable': True}
                    else:
                        print(f"   ⚠️ {script} (실행 권한 없음)")
                        script_status[script] = {'exists': True, 'executable': False}
                        self.validation_results['warnings'].append(f"{script} 실행 권한 필요")
                else:
                    print(f"   ✅ {script}")
                    script_status[script] = {'exists': True, 'executable': True}
            else:
                print(f"   ❌ {script}")
                script_status[script] = {'exists': False, 'executable': False}
        
        self.validation_results['scripts'] = script_status
    
    def _validate_disk_space(self):
        """디스크 공간 검증"""
        print("\n💾 디스크 공간 검증")
        print("-" * 40)
        
        try:
            import shutil
            
            # 프로젝트 디렉토리의 여유 공간 확인
            total, used, free = shutil.disk_usage(self.project_root)
            
            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            
            print(f"   총 용량: {total_gb:.1f} GB")
            print(f"   여유 공간: {free_gb:.1f} GB")
            
            # 필요 공간 추정 (모델, 로그, 결과 파일 등)
            required_space_gb = 10  # 최소 10GB 권장
            
            if free_gb >= required_space_gb:
                print(f"   ✅ 충분한 디스크 공간 ({required_space_gb} GB 필요)")
                disk_status = 'sufficient'
            elif free_gb >= required_space_gb * 0.5:
                print(f"   ⚠️ 디스크 공간 부족 경고 ({required_space_gb} GB 권장)")
                disk_status = 'warning'
                self.validation_results['warnings'].append("디스크 공간 부족")
            else:
                print(f"   ❌ 디스크 공간 심각 부족 ({required_space_gb} GB 필요)")
                disk_status = 'critical'
                self.validation_results['critical_issues'].append("디스크 공간 부족")
            
            self.validation_results['disk_space'] = {
                'total_gb': total_gb,
                'free_gb': free_gb,
                'required_gb': required_space_gb,
                'status': disk_status
            }
            
        except Exception as e:
            print(f"   ❌ 디스크 공간 확인 실패: {e}")
    
    def _validate_memory_requirements(self):
        """메모리 요구사항 검증"""
        print("\n🧠 메모리 요구사항 검증")
        print("-" * 40)
        
        try:
            import psutil
            
            # 시스템 메모리 정보
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            
            print(f"   총 메모리: {memory_gb:.1f} GB")
            print(f"   사용 가능 메모리: {available_gb:.1f} GB")
            
            # GPU 메모리 확인 (가능한 경우)
            gpu_memory_gb = 0
            try:
                import torch
                if torch.cuda.is_available():
                    gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    print(f"   GPU 메모리: {gpu_memory_gb:.1f} GB")
            except:
                pass
            
            # 메모리 요구사항 추정
            min_required_gb = 8
            recommended_gb = 16
            
            if available_gb >= recommended_gb:
                print(f"   ✅ 충분한 메모리 ({recommended_gb} GB 권장)")
                memory_status = 'excellent'
            elif available_gb >= min_required_gb:
                print(f"   ✅ 최소 메모리 만족 ({min_required_gb} GB 필요)")
                memory_status = 'sufficient'
            else:
                print(f"   ❌ 메모리 부족 ({min_required_gb} GB 필요)")
                memory_status = 'insufficient'
                self.validation_results['critical_issues'].append("메모리 부족")
            
            self.validation_results['memory'] = {
                'total_gb': memory_gb,
                'available_gb': available_gb,
                'gpu_memory_gb': gpu_memory_gb,
                'status': memory_status
            }
            
        except ImportError:
            print("   ⚠️ psutil 패키지가 없어 메모리 확인 불가")
            self.validation_results['warnings'].append("psutil 패키지 설치 권장")
        except Exception as e:
            print(f"   ❌ 메모리 확인 실패: {e}")
    
    def _estimate_execution_time(self):
        """실행 시간 추정"""
        print("\n⏱️ 실행 시간 추정")
        print("-" * 40)
        
        try:
            # 설정에서 실험 수 계산
            configs = self.validation_results.get('configs', {})
            exp_config = configs.get('experiment_config', {})
            
            if exp_config.get('valid', False):
                total_experiments = exp_config.get('estimated_experiments', 0)
                
                # 디바이스별 실험 시간 추정
                hardware = self.validation_results.get('hardware', {})
                device_type = hardware.get('device_type', 'CPU')
                
                if device_type == 'CUDA':
                    time_per_experiment = 30  # 30분
                elif device_type == 'MPS':
                    time_per_experiment = 45  # 45분
                else:
                    time_per_experiment = 120  # 2시간
                
                total_time_hours = (total_experiments * time_per_experiment) / 60
                total_time_days = total_time_hours / 24
                
                print(f"   예상 실험 수: {total_experiments}개")
                print(f"   실험당 시간: {time_per_experiment}분 ({device_type})")
                print(f"   총 예상 시간: {total_time_hours:.1f}시간 ({total_time_days:.1f}일)")
                
                if total_time_hours > 48:
                    self.validation_results['warnings'].append("실행 시간이 매우 길어질 수 있음")
                
                self.validation_results['estimated_runtime'] = {
                    'total_experiments': total_experiments,
                    'time_per_experiment_minutes': time_per_experiment,
                    'total_hours': total_time_hours,
                    'total_days': total_time_days,
                    'device_type': device_type
                }
            else:
                print("   ⚠️ 설정 파일 문제로 시간 추정 불가")
                
        except Exception as e:
            print(f"   ❌ 실행 시간 추정 실패: {e}")
    
    def _generate_final_report(self):
        """최종 검증 결과 생성"""
        print("\n" + "=" * 80)
        print("📋 최종 검증 결과")
        print("=" * 80)
        
        critical_issues = self.validation_results['critical_issues']
        warnings = self.validation_results['warnings']
        
        if not critical_issues:
            print("🎊 모든 필수 요구사항 만족! 실험 실행 가능")
            overall_status = 'ready'
        else:
            print("❌ 실험 실행 전 해결해야 할 중요 문제들:")
            for issue in critical_issues:
                print(f"   • {issue}")
            overall_status = 'blocked'
        
        if warnings:
            print(f"\n⚠️ 경고 사항 ({len(warnings)}개):")
            for warning in warnings:
                print(f"   • {warning}")
        
        # 추천 사항
        recommendations = self._generate_recommendations()
        if recommendations:
            print(f"\n💡 권장 사항:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        self.validation_results['overall_status'] = overall_status
        self.validation_results['recommendations'] = recommendations
        
        # 실행 명령어 제안
        if overall_status == 'ready':
            print(f"\n🚀 실행 준비 완료! 다음 명령어로 시작하세요:")
            print(f"   python hyperparameter_system/run_experiments.py")
            print(f"\n또는 특정 실험만:")
            print(f"   python hyperparameter_system/experiment_runner.py --models efficientnet_b4.ra2_in1k --categories optimizer")
        
        return overall_status
    
    def _generate_recommendations(self) -> List[str]:
        """추천 사항 생성"""
        recommendations = []
        
        # 패키지 관련
        packages = self.validation_results.get('packages', {})
        if packages.get('missing'):
            recommendations.append(f"누락된 패키지 설치: pip install {' '.join(packages['missing'])}")
        
        # 하드웨어 관련
        hardware = self.validation_results.get('hardware', {})
        if hardware.get('device_type') == 'CPU':
            recommendations.append("GPU 사용 권장 (CUDA 또는 MPS)")
        
        # 메모리 관련
        memory = self.validation_results.get('memory', {})
        if memory.get('status') == 'insufficient':
            recommendations.append("메모리 부족: 다른 프로그램 종료 또는 배치 크기 감소")
        
        # 실행 시간 관련
        runtime = self.validation_results.get('estimated_runtime', {})
        if runtime.get('total_hours', 0) > 24:
            recommendations.append("실행 시간이 길어 특정 모델/카테고리만 먼저 테스트 권장")
        
        # 파일 권한 관련
        scripts = self.validation_results.get('scripts', {})
        non_executable = [script for script, status in scripts.items() if not status.get('executable', True)]
        if non_executable:
            recommendations.append(f"실행 권한 부여: chmod +x {' '.join(non_executable)}")
        
        return recommendations
    
    def save_validation_report(self, filename: str = "validation_report.yaml"):
        """검증 결과를 파일로 저장"""
        report_path = self.project_root / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.validation_results, f, default_flow_style=False, allow_unicode=True)
        
        print(f"\n📄 상세 검증 결과 저장: {report_path}")

def main():
    """메인 실행 함수"""
    validator = ExperimentSystemValidator()
    
    try:
        # 전체 검증 실행
        results = validator.run_full_validation()
        
        # 결과 저장
        validator.save_validation_report()
        
        # 종료 코드 반환
        if results['overall_status'] == 'ready':
            print(f"\n✅ 검증 완료: 실험 실행 준비됨")
            return 0
        else:
            print(f"\n❌ 검증 실패: 문제 해결 후 재시도")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n👋 사용자가 검증을 중단했습니다.")
        return 1
    except Exception as e:
        print(f"\n❌ 검증 중 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
