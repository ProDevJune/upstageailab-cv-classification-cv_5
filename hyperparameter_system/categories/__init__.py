"""
카테고리 초기화 파일
"""

from .base_category import ExperimentCategory
from .optimizer import OptimizerCategory
from .scheduler import SchedulerCategory
from .loss_function import LossFunctionCategory
from .image_size import ImageSizeCategory
from .batch_size import BatchSizeCategory
from .early_stopping import EarlyStoppingCategory

# 카테고리 매핑
CATEGORY_MAPPING = {
    'optimizer': OptimizerCategory,
    'scheduler': SchedulerCategory,
    'loss_function': LossFunctionCategory,
    'image_size': ImageSizeCategory,
    'batch_size': BatchSizeCategory,
    'early_stopping': EarlyStoppingCategory,
}

def create_category(category_name: str, options: list, enabled: bool = True, description: str = "") -> ExperimentCategory:
    """
    카테고리 팩토리 함수
    
    Args:
        category_name: 카테고리 이름
        options: 카테고리 옵션들
        enabled: 활성화 여부
        description: 설명
        
    Returns:
        생성된 카테고리 인스턴스
    """
    if category_name not in CATEGORY_MAPPING:
        raise ValueError(f"Unknown category: {category_name}. Available: {list(CATEGORY_MAPPING.keys())}")
    
    category_class = CATEGORY_MAPPING[category_name]
    return category_class(category_name, options, enabled, description)

__all__ = [
    'ExperimentCategory',
    'OptimizerCategory', 
    'SchedulerCategory',
    'LossFunctionCategory',
    'ImageSizeCategory',
    'BatchSizeCategory',
    'EarlyStoppingCategory',
    'CATEGORY_MAPPING',
    'create_category'
]
