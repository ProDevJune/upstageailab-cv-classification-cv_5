"""
실험 카테고리 베이스 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import copy

class ExperimentCategory(ABC):
    """실험 카테고리 베이스 클래스"""
    
    def __init__(self, name: str, options: List[Dict], enabled: bool = True, description: str = ""):
        self.name = name
        self.options = options
        self.enabled = enabled
        self.description = description
    
    @abstractmethod
    def apply_to_config(self, base_config: Dict[str, Any], option: Dict[str, Any]) -> Dict[str, Any]:
        """
        베이스 설정에 실험 옵션을 적용
        
        Args:
            base_config: 기본 설정 딕셔너리
            option: 적용할 옵션
            
        Returns:
            수정된 설정 딕셔너리
        """
        pass
    
    @abstractmethod
    def generate_run_name(self, option: Dict[str, Any], timestamp: str) -> str:
        """
        실험 옵션에 따른 WandB run 이름 생성
        
        Args:
            option: 실험 옵션
            timestamp: 타임스탬프
            
        Returns:
            생성된 run 이름
        """
        pass
    
    def validate_option(self, option: Dict[str, Any]) -> bool:
        """
        옵션 유효성 검증
        
        Args:
            option: 검증할 옵션
            
        Returns:
            유효성 여부
        """
        return True
    
    def get_option_summary(self, option: Dict[str, Any]) -> str:
        """
        옵션 요약 문자열 생성
        
        Args:
            option: 요약할 옵션
            
        Returns:
            요약 문자열
        """
        return option.get('description', str(option))
