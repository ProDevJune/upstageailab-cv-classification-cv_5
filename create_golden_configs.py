#!/usr/bin/env python3
"""
황금 조합(320px + Moderate 증강 + No TTA)을 다양한 모델에 적용한 설정 파일 생성기
기존 성공한 exp_full_024 설정을 기반으로 모델만 변경하여 새 실험 설정 생성
"""

import yaml
import os
from datetime import datetime
from pathlib import Path

def load_golden_template():
    """최고 성능 모델(exp_full_024)의 설정을 템플릿으로 로드"""
    template_path = "codes/practice/exp_full_024_2507041730.yaml"
    with open(template_path, 'r') as f:
        return yaml.safe_load(f)

def create_experiment_config(model_name, model_family, config_template):
    """새로운 실험 설정 생성"""
    config = config_template.copy()
    
    # 고유한 실험 ID 생성
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    experiment_id = f"exp_golden_{model_family}_{timestamp}"
    
    # 모델 설정 업데이트
    config['model_name'] = model_name
    config['experiment_id'] = experiment_id
    
    # 황금 조합 설정 확정
    config['image_size'] = 320  # 핵심: 320px
    config['TTA'] = False       # 핵심: No TTA
    config['augmentation_level'] = 'minimal'  # 핵심: Moderate = minimal
    config['lr'] = 0.0001       # 검증된 학습률
    
    # 증강 설정 최적화
    config['augmentation'] = {
        'eda': True,      # 기본 증강만
        'dilation': False,
        'erosion': False,
        'mixup': False,
        'cutmix': False
    }
    
    # 배치 크기 모델별 조정
    batch_sizes = {
        'efficientnet': 20,  # 더 큰 모델이므로 작게
        'convnext': 18,      # 메모리 많이 사용
        'regnet': 22,        # 중간 크기
        'resnext': 20,       # ResNet보다 약간 크게
        'densenet': 24,      # 상대적으로 가벼움
        'mobilenet': 32,     # 매우 가벼움
        'vit': 16           # Transformer는 메모리 많이 사용
    }
    
    for family, batch_size in batch_sizes.items():
        if family in model_family.lower():
            config['batch_size'] = batch_size
            break
    
    return config, experiment_id

def main():
    """황금 조합 기반 다양한 모델 설정 생성"""
    
    print("🏆 황금 조합 기반 새 모델 설정 생성기")
    print("=" * 60)
    
    # 템플릿 로드
    template = load_golden_template()
    print(f"✅ 템플릿 로드 완료: exp_full_024 (0.8239점 모델)")
    
    # 실험할 모델들 정의 (timm 모델명)
    models_to_test = [
        # EfficientNet 패밀리 (고성능 기대)
        ('efficientnet_b3.ra2_in1k', 'efficientnet_b3'),
        ('efficientnet_b4.ra2_in1k', 'efficientnet_b4'), 
        ('efficientnet_b5.sw_in12k', 'efficientnet_b5'),
        
        # ConvNeXt 패밀리 (최신 아키텍처)
        ('convnext_base.fb_in22k_ft_in1k', 'convnext_base'),
        ('convnext_small.fb_in22k_ft_in1k', 'convnext_small'),
        
        # RegNet 패밀리 (효율적)
        ('regnetv_040.ra3_in1k', 'regnet_v040'),
        ('regnetv_064.ra3_in1k', 'regnet_v064'),
        
        # ResNeXt 패밀리 (ResNet 향상)
        ('resnext50_32x4d.ra_in1k', 'resnext50'),
        ('resnext101_32x8d.fb_wsl_ig1b_ft_in1k', 'resnext101'),
        
        # DenseNet 패밀리 (다양성)
        ('densenet169.tv_in1k', 'densenet169'),
        ('densenet201.tv_in1k', 'densenet201'),
        
        # 정규화 강화 ResNet50 변형
        ('resnet50.tv2_in1k', 'resnet50_reg_strong'),
        ('resnet50.tv2_in1k', 'resnet50_reg_medium'),
    ]
    
    practice_dir = Path("codes/practice")
    created_configs = []
    
    for model_name, model_family in models_to_test:
        try:
            config, experiment_id = create_experiment_config(model_name, model_family, template)
            
            # 정규화 강화 변형 처리
            if 'reg_strong' in model_family:
                config['weight_decay'] = 0.01  # 10배 증가
                config['patience'] = 15        # 조기 종료 빠르게
                config['lr'] = 0.00005         # 학습률 낮춤
                
            elif 'reg_medium' in model_family:
                config['weight_decay'] = 0.001 # 10배 증가
                config['patience'] = 18        # 약간 빠르게
                config['lr'] = 0.00007         # 학습률 약간 낮춤
            
            # 설정 파일 저장
            config_filename = f"{experiment_id}.yaml"
            config_path = practice_dir / config_filename
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            created_configs.append({
                'file': config_filename,
                'model': model_name,
                'family': model_family,
                'batch_size': config['batch_size'],
                'experiment_id': experiment_id
            })
            
            print(f"✅ 생성: {config_filename}")
            print(f"   📱 모델: {model_name}")
            print(f"   🔢 배치: {config['batch_size']}")
            
        except Exception as e:
            print(f"❌ 실패: {model_family} - {e}")
    
    print(f"\n🎯 생성 완료: {len(created_configs)}개 설정 파일")
    print("=" * 60)
    
    # 실행 가이드 생성
    print("\n🚀 실행 방법:")
    print("다음 명령어들을 순차적으로 실행하세요:\n")
    
    # 우선순위별 실행 순서 제안
    priority_order = [
        'efficientnet_b4', 'efficientnet_b3', 'convnext_base', 
        'regnet_v040', 'resnext50', 'resnet50_reg_strong'
    ]
    
    for i, family in enumerate(priority_order, 1):
        matching_configs = [c for c in created_configs if family in c['family']]
        if matching_configs:
            config = matching_configs[0]
            print(f"{i}. python codes/gemini_main.py --config codes/practice/{config['file']}")
            print(f"   # {config['model']} - 예상 소요시간: 15-30분")
            print()
    
    # 나머지 실험들
    remaining_configs = [c for c in created_configs 
                        if not any(family in c['family'] for family in priority_order)]
    
    if remaining_configs:
        print("\n📊 추가 실험들 (시간 여유시 실행):")
        for config in remaining_configs:
            print(f"python codes/gemini_main.py --config codes/practice/{config['file']}")
        print()
    
    # 예상 결과 및 다음 단계
    print("🎯 예상 결과:")
    print("- EfficientNet-B4: 0.82+ (최고 기대)")
    print("- ConvNeXt-Base: 0.81+ (새 아키텍처)")
    print("- 정규화 강화: 0.80+ (안정성)")
    print()
    print("📈 다음 단계:")
    print("1. 상위 3-4개 모델로 앙상블 구성")
    print("2. 0.85+ 목표 달성")
    print("3. 최종 제출 전략 수립")

if __name__ == "__main__":
    main()
