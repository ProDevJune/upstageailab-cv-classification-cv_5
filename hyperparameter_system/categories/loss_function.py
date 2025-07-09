"""
손실 함수 실험 카테고리 (누락된 부분 구현)
"""

from typing import Dict, Any
from .base_category import ExperimentCategory

class LossFunctionCategory(ExperimentCategory):
    """손실 함수 실험 카테고리"""
    
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """손실 함수 설정 적용"""
        config = base_config.copy()
        
        config['criterion'] = option['name']
        
        # 손실 함수별 특별 파라미터 설정
        if option['name'] == 'FocalLoss':
            config['focal_alpha'] = option.get('alpha', 2)
            config['focal_gamma'] = option.get('gamma', 1)
            
        elif option['name'] == 'LabelSmoothingLoss':
            config['label_smooth'] = option.get('smoothing', 0.1)
            
        elif option['name'] == 'CrossEntropyLoss':
            # 클래스 가중치 설정 가능
            if 'class_weighting' in option:
                config['class_weighting'] = option['class_weighting']
        
        return config
    
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """손실 함수 run 이름 생성"""
        name = f"loss_{option['name']}"
        
        if option['name'] == 'FocalLoss':
            if 'alpha' in option:
                name += f"_alpha{option['alpha']}"
            if 'gamma' in option:
                name += f"_gamma{option['gamma']}"
                
        elif option['name'] == 'LabelSmoothingLoss':
            if 'smoothing' in option:
                name += f"_smooth{option['smoothing']}"
                
        return f"{name}_{timestamp}"
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """손실 함수 옵션 유효성 검증"""
        if 'name' not in option:
            return False
        
        loss_name = option['name']
        
        # 지원하는 손실 함수 목록
        supported_losses = ['CrossEntropyLoss', 'FocalLoss', 'LabelSmoothingLoss']
        if loss_name not in supported_losses:
            return False
        
        # 손실 함수별 파라미터 검증
        if loss_name == 'FocalLoss':
            if 'alpha' in option and option['alpha'] <= 0:
                return False
            if 'gamma' in option and option['gamma'] < 0:
                return False
                
        elif loss_name == 'LabelSmoothingLoss':
            if 'smoothing' in option:
                smoothing = option['smoothing']
                if not (0.0 <= smoothing <= 1.0):
                    return False
                    
        return True
    
    def get_option_summary(self, option: Dict[str, Any]) -> str:
        """손실 함수 옵션 요약"""
        summary = option['name']
        
        if option['name'] == 'FocalLoss':
            alpha = option.get('alpha', 2)
            gamma = option.get('gamma', 1)
            summary += f" (α={alpha}, γ={gamma})"
            
        elif option['name'] == 'LabelSmoothingLoss':
            smoothing = option.get('smoothing', 0.1)
            summary += f" (smoothing={smoothing})"
            
        return summary
