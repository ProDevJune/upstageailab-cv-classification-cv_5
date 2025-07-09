"""
조기 종료 실험 카테고리
"""

from typing import Dict, Any
from .base_category import ExperimentCategory

class EarlyStoppingCategory(ExperimentCategory):
    """조기 종료 실험 카테고리"""
    
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """조기 종료 설정 적용"""
        config = base_config.copy()
        
        config['patience'] = option['patience']
        
        return config
    
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """조기 종료 run 이름 생성"""
        return f"es_patience{option['patience']}_{timestamp}"
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """조기 종료 옵션 유효성 검증"""
        if 'patience' not in option:
            return False
        
        # patience 범위 검증
        if not (1 <= option['patience'] <= 100):
            return False
            
        return True
    
    def get_option_summary(self, option: Dict[str, Any]) -> str:
        """조기 종료 옵션 요약"""
        return f"patience: {option['patience']}"
