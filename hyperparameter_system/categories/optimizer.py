"""
옵티마이저 실험 카테고리
"""

from typing import Dict, Any
from .base_category import ExperimentCategory

class OptimizerCategory(ExperimentCategory):
    """옵티마이저 실험 카테고리"""
    
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """옵티마이저 설정 적용"""
        config = base_config.copy()
        
        config['optimizer_name'] = option['name']
        config['lr'] = option['lr']
        
        if 'weight_decay' in option:
            config['weight_decay'] = option['weight_decay']
        if 'momentum' in option:
            config['momentum'] = option['momentum']
        
        return config
    
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """옵티마이저 run 이름 생성"""
        name = f"opt_{option['name']}_lr{option['lr']}"
        
        if 'weight_decay' in option:
            name += f"_wd{option['weight_decay']}"
        if 'momentum' in option:
            name += f"_mom{option['momentum']}"
            
        return f"{name}_{timestamp}"
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """옵티마이저 옵션 유효성 검증"""
        required_fields = ['name', 'lr']
        
        for field in required_fields:
            if field not in option:
                return False
        
        # 학습률 범위 검증
        if not (1e-6 <= option['lr'] <= 1.0):
            return False
            
        return True
