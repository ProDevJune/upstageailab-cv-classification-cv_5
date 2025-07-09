"""
동적 실험 매트릭스 생성기
확장 가능한 하이퍼파라미터 실험 시스템의 핵심
"""

import yaml
import copy
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from categories import create_category, CATEGORY_MAPPING

class DynamicExperimentMatrix:
    """동적으로 확장 가능한 실험 매트릭스 생성기"""
    
    def __init__(self, config_path: str = "hyperparameter_system/experiment_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.models = self.load_enabled_models()
        self.categories = self.load_enabled_categories()
        
        # 임시 설정 디렉토리 생성
        self.temp_config_dir = Path(self.config['system']['temp_config_dir'])
        self.temp_config_dir.mkdir(exist_ok=True)
        
        print(f"🎯 동적 실험 매트릭스 초기화 완료")
        print(f"📊 활성화된 모델: {len(self.models)}개")
        print(f"⚙️ 활성화된 카테고리: {len(self.categories)}개")
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 파싱 오류: {e}")
    
    def load_enabled_models(self) -> List[Dict[str, Any]]:
        """활성화된 모델들 로드"""
        models = []
        for model_config in self.config['models']:
            if model_config.get('enabled', True):
                models.append(model_config)
        return models
    
    def load_enabled_categories(self) -> List:
        """활성화된 카테고리들 로드"""
        categories = []
        
        for category_name, category_config in self.config['experiment_categories'].items():
            if category_config.get('enabled', True):
                try:
                    category = create_category(
                        category_name=category_name,
                        options=category_config['options'],
                        enabled=True,
                        description=category_config.get('description', '')
                    )
                    categories.append(category)
                except Exception as e:
                    print(f"⚠️ 카테고리 '{category_name}' 로드 실패: {e}")
        
        return categories
    
    def load_base_config(self, config_path: str) -> Dict[str, Any]:
        """베이스 설정 파일 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️ 베이스 설정 파일을 찾을 수 없습니다: {config_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"⚠️ 베이스 설정 파일 파싱 오류: {e}")
            return {}
    
    def generate_all_experiments(self) -> List[Dict[str, Any]]:
        """모든 활성화된 모델×카테고리 실험 생성"""
        experiments = []
        experiment_id = 1
        
        print(f"\n🚀 실험 매트릭스 생성 중...")
        print(f"📊 예상 실험 수: {len(self.models)} 모델 × {len(self.categories)} 카테고리 × 평균 옵션 수")
        
        for model in self.models:
            model_experiments = 0
            
            for category in self.categories:
                for option in category.options:
                    # 옵션 유효성 검증
                    if not category.validate_option(option):
                        print(f"⚠️ 유효하지 않은 옵션 스킵: {category.name} - {option}")
                        continue
                    
                    experiment = {
                        'id': experiment_id,
                        'model': model,
                        'category': category,
                        'option': option,
                        'config': self.create_dynamic_config(model, category, option),
                        'timestamp': datetime.now().strftime("%y%m%d%H%M")
                    }
                    
                    experiments.append(experiment)
                    experiment_id += 1
                    model_experiments += 1
            
            print(f"✅ {model['name']}: {model_experiments}개 실험 생성")
        
        print(f"🎊 총 {len(experiments)}개 실험 생성 완료!")
        return experiments
    
    def generate_selective_experiments(self, 
                                     model_filter: Optional[List[str]] = None,
                                     category_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """선택적 실험 생성"""
        experiments = self.generate_all_experiments()
        
        if model_filter:
            experiments = [e for e in experiments if e['model']['name'] in model_filter]
            print(f"📊 모델 필터 적용: {len(experiments)}개 실험")
        
        if category_filter:
            experiments = [e for e in experiments if e['category'].name in category_filter]
            print(f"⚙️ 카테고리 필터 적용: {len(experiments)}개 실험")
        
        return experiments
    
    def create_dynamic_config(self, model: Dict[str, Any], category, option: Dict[str, Any]) -> Dict[str, Any]:
        """동적 설정 생성"""
        # 베이스 설정 로드
        base_config = self.load_base_config(model['base_config'])
        
        # 모델 설정 적용
        base_config['model_name'] = model['name']
        
        # 카테고리별 설정 적용
        config = category.apply_to_config(base_config, option)
        
        # 실험 ID 추가
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        experiment_id = f"{timestamp}_{model['name'].replace('.', '_')}_{category.name}"
        config['experiment_id'] = experiment_id
        
        # WandB 프로젝트 설정 (모델명 기반)
        if 'wandb' in config:
            project_name = model['name'].replace('.', '_').replace('-', '_')
            config['wandb']['project'] = project_name
        
        return config
    
    def create_temp_config_file(self, experiment: Dict[str, Any]) -> str:
        """임시 설정 파일 생성"""
        config = experiment['config']
        category = experiment['category']
        option = experiment['option']
        timestamp = experiment['timestamp']
        
        # Run 이름 생성
        run_name = category.generate_run_name(option, timestamp)
        
        # 임시 설정 파일 경로
        temp_config_filename = f"{experiment['id']:03d}_{run_name}.yaml"
        temp_config_path = self.temp_config_dir / temp_config_filename
        
        # YAML 파일 저장
        with open(temp_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return str(temp_config_path)
    
    def add_model(self, name: str, enabled: bool = True, base_config: Optional[str] = None, 
                  script: Optional[str] = None, description: str = "") -> None:
        """런타임에 새 모델 추가"""
        new_model = {
            'name': name,
            'enabled': enabled,
            'base_config': base_config or self.config['system']['base_config_template'],
            'script': script or "python codes/gemini_main_v2.py",
            'description': description
        }
        
        self.config['models'].append(new_model)
        self.models = self.load_enabled_models()
        
        print(f"✅ 새 모델 추가: {name}")
    
    def add_category(self, name: str, options: List[Dict], enabled: bool = True, description: str = "") -> None:
        """런타임에 새 카테고리 추가"""
        if name in CATEGORY_MAPPING:
            self.config['experiment_categories'][name] = {
                'enabled': enabled,
                'options': options,
                'description': description
            }
            
            self.categories = self.load_enabled_categories()
            print(f"✅ 새 카테고리 추가: {name}")
        else:
            print(f"⚠️ 지원하지 않는 카테고리: {name}")
            print(f"   지원 카테고리: {list(CATEGORY_MAPPING.keys())}")
    
    def get_experiment_summary(self) -> Dict[str, Any]:
        """실험 요약 정보"""
        total_experiments = 0
        category_counts = {}
        
        for category in self.categories:
            option_count = len(category.options)
            category_counts[category.name] = option_count
            total_experiments += len(self.models) * option_count
        
        return {
            'total_models': len(self.models),
            'total_categories': len(self.categories),
            'total_experiments': total_experiments,
            'models': [m['name'] for m in self.models],
            'categories': list(category_counts.keys()),
            'category_option_counts': category_counts
        }
    
    def print_experiment_matrix(self) -> None:
        """실험 매트릭스 출력"""
        summary = self.get_experiment_summary()
        
        print("\n🎯 확장 가능한 하이퍼파라미터 실험 매트릭스")
        print("=" * 70)
        
        print(f"\n📊 전체 통계:")
        print(f"   모델 수: {summary['total_models']}개")
        print(f"   카테고리 수: {summary['total_categories']}개")
        print(f"   총 실험 수: {summary['total_experiments']}개")
        
        print(f"\n🤖 활성화된 모델들:")
        for i, model in enumerate(self.models, 1):
            print(f"   {i}. {model['name']} - {model.get('description', '')}")
        
        print(f"\n⚙️ 활성화된 카테고리들:")
        for i, category in enumerate(self.categories, 1):
            option_count = len(category.options)
            print(f"   {i}. {category.name}: {option_count}개 옵션 - {category.description}")
        
        print(f"\n🔧 예상 WandB 프로젝트 구조:")
        for model in self.models:
            project_name = model['name'].replace('.', '_').replace('-', '_')
            experiments_per_model = sum(len(cat.options) for cat in self.categories)
            print(f"   Project: {project_name} ({experiments_per_model}개 runs)")

if __name__ == "__main__":
    # 테스트 실행
    matrix = DynamicExperimentMatrix()
    matrix.print_experiment_matrix()
    
    # 샘플 실험 생성
    print(f"\n🚀 샘플 실험 생성 테스트:")
    experiments = matrix.generate_selective_experiments(
        model_filter=["resnet50.tv2_in1k"],
        category_filter=["optimizer", "loss_function"]
    )
    
    print(f"✅ {len(experiments)}개 샘플 실험 생성됨")
    for exp in experiments[:3]:  # 처음 3개만 출력
        print(f"   {exp['id']:2d}. {exp['model']['name']} + {exp['category'].name}")
