"""
배치 크기 실험 카테고리
"""

from typing import Dict, Any
from .base_category import ExperimentCategory

class BatchSizeCategory(ExperimentCategory):
    """배치 크기 실험 카테고리"""
    
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """배치 크기 설정 적용"""
        config = base_config.copy()
        
        config['batch_size'] = option['batch_size']
        
        if 'mixed_precision' in option:
            config['mixed_precision'] = option['mixed_precision']
            
        return config
    
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """배치 크기 run 이름 생성"""
        name = f"batch{option['batch_size']}"
        
        if option.get('mixed_precision', False):
            name += "_MP"
            
        return f"{name}_{timestamp}"
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """배치 크기 옵션 유효성 검증"""
        if 'batch_size' not in option:
            return False
        
        # 배치 크기 범위 검증
        if not (1 <= option['batch_size'] <= 512):
            return False
            
        return True
    
    def get_option_summary(self, option: Dict[str, Any]) -> str:
        """배치 크기 옵션 요약"""
        summary = f"batch_size: {option['batch_size']}"
        
        if option.get('mixed_precision', False):
            summary += " + Mixed Precision"
            
        return summary
