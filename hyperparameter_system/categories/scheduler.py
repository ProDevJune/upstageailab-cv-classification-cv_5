"""
스케줄러 실험 카테고리
"""

from typing import Dict, Any
from .base_category import ExperimentCategory

class SchedulerCategory(ExperimentCategory):
    """스케줄러 실험 카테고리"""
    
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """스케줄러 설정 적용"""
        config = base_config.copy()
        
        config['scheduler_name'] = option['name']
        
        # scheduler_params 딕셔너리 초기화
        if 'scheduler_params' not in config:
            config['scheduler_params'] = {}
        
        # 스케줄러별 파라미터 설정
        if option['name'] == 'CosineAnnealingLR':
            config['scheduler_params']['T_max'] = option.get('T_max', 25)
            config['scheduler_params']['eta_min'] = option.get('eta_min', 0.0001)
            
        elif option['name'] == 'OneCycleLR':
            config['scheduler_params']['max_lr'] = option.get('max_lr', 0.01)
            config['scheduler_params']['total_steps'] = option.get('total_steps', 1000)
            
        elif option['name'] == 'StepLR':
            config['scheduler_params']['step_size'] = option.get('step_size', 50)
            config['scheduler_params']['gamma'] = option.get('gamma', 0.1)
            
        # 다른 스케줄러 파라미터들도 추가 가능
        for key, value in option.items():
            if key not in ['name', 'description']:
                config['scheduler_params'][key] = value
        
        return config
    
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """스케줄러 run 이름 생성"""
        name = f"sch_{option['name']}"
        
        if 'T_max' in option:
            name += f"_T{option['T_max']}"
        if 'max_lr' in option:
            name += f"_maxlr{option['max_lr']}"
        if 'step_size' in option:
            name += f"_step{option['step_size']}"
            
        return f"{name}_{timestamp}"
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """스케줄러 옵션 유효성 검증"""
        if 'name' not in option:
            return False
        
        scheduler_name = option['name']
        
        # 스케줄러별 필수 파라미터 검증
        if scheduler_name == 'CosineAnnealingLR':
            if 'T_max' in option and option['T_max'] <= 0:
                return False
                
        elif scheduler_name == 'OneCycleLR':
            if 'max_lr' in option and option['max_lr'] <= 0:
                return False
                
        elif scheduler_name == 'StepLR':
            if 'step_size' in option and option['step_size'] <= 0:
                return False
                
        return True
