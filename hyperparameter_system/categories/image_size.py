"""
이미지 크기 실험 카테고리
"""

from typing import Dict, Any
from .base_category import ExperimentCategory

class ImageSizeCategory(ExperimentCategory):
    """이미지 크기 실험 카테고리"""
    
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """이미지 크기 설정 적용"""
        config = base_config.copy()
        
        config['image_size'] = option['size']
        config['batch_size'] = option['batch_size']
        
        return config
    
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """이미지 크기 run 이름 생성"""
        return f"img{option['size']}_batch{option['batch_size']}_{timestamp}"
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """이미지 크기 옵션 유효성 검증"""
        required_fields = ['size', 'batch_size']
        
        for field in required_fields:
            if field not in option:
                return False
        
        # 이미지 크기 범위 검증
        if not (32 <= option['size'] <= 1024):
            return False
        
        # 배치 크기 범위 검증
        if not (1 <= option['batch_size'] <= 512):
            return False
            
        return True
    
    def get_option_summary(self, option: Dict[str, Any]) -> str:
        """이미지 크기 옵션 요약"""
        return f"{option['size']}px (batch: {option['batch_size']})"
