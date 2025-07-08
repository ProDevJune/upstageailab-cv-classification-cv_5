"""
GPT 버전 유틸리티 모듈 (gemini_utils.py 기반)
플랫폼별 최적화 기능 추가
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
import torch.nn.init as init
import timm
from torch.utils.data import Dataset
from types import SimpleNamespace
import yaml
import random
import numpy as np
import pandas as pd
from PIL import Image
import torch.backends.cudnn as cudnn

def load_config(config_path='./config.yaml'):
    """.yaml 설정 파일 읽기

    :param str config_path: _description_, defaults to './config.yaml'
    :return _type_: _description_
    """
    with open(config_path, 'r') as file:
        cfg = yaml.safe_load(file)
    return SimpleNamespace(**cfg)

def set_seed(seed: int = 256):
    """랜덤성 제어 함수

    :param int seed: _description_, defaults to 256
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def setup_platform_optimization(device_type: str):
    """플랫폼별 PyTorch 최적화 설정"""
    
    if device_type == 'cuda':
        print("🚀 CUDA 최적화 설정 중...")
        cudnn.benchmark = True  # 입력 크기가 일정한 경우 성능 향상
        cudnn.deterministic = False  # 성능 우선, 재현성 약간 포기
        if hasattr(torch.backends.cuda.matmul, 'allow_tf32'):
            torch.backends.cuda.matmul.allow_tf32 = True  # Ampere GPU에서 성능 향상
        
        device = torch.device('cuda')
        
    elif device_type == 'mps':
        print("🍎 Apple Silicon MPS 최적화 설정 중...")
        device = torch.device('mps')
        
    else:
        print("💻 CPU 최적화 설정 중...")
        # CPU 스레드 수 최적화는 platform_detector에서 처리
        device = torch.device('cpu')
    
    return device

class ImageDataset(Dataset):
    """커스텀 데이터셋 클래스 (개선된 버전)"""
    
    def __init__(self, df: pd.DataFrame, path, transform=None):
        self.df = df
        self.path = path
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        name, target = self.df.iloc[idx]
        
        try:
            img = Image.open(os.path.join(self.path, name))
            img = img.convert('RGB')  # 확실히 RGB로 변환
            
            if self.transform:
                img = self.transform(image=np.array(img))['image']
            
            return img, target
            
        except Exception as e:
            print(f"❌ 이미지 로드 실패: {name}, 오류: {e}")
            # 기본 이미지 반환 (또는 다른 처리)
            default_img = np.zeros((224, 224, 3), dtype=np.uint8)
            if self.transform:
                default_img = self.transform(image=default_img)['image']
            return default_img, target
    
### Getters
def get_activation(activation_option):
    ACTIVATIONS = {
        'None': None,
        'ReLU': nn.ReLU,
        'LeakyReLU': nn.LeakyReLU,
        'ELU': nn.ELU,
        'SELU': nn.SELU,
        'GELU': nn.GELU,
        'Tanh': nn.Tanh,
        'PReLU': nn.PReLU,
        'SiLU': nn.SiLU,
    }
    return ACTIVATIONS[activation_option]

class TimmWrapper(nn.Module):
    """개선된 Timm 래퍼 (플랫폼별 최적화 포함)"""
    
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        
        # 백본 모델 생성
        self.backbone = timm.create_model(
            model_name=cfg.model_name,
            pretrained=cfg.pretrained,
            num_classes=0, 
            global_pool='avg',
            act_layer=get_activation(cfg.timm.get('activation', 'None'))
        )
        
        # 사용자 정의 헤드
        if hasattr(cfg, 'custom_layer') and cfg.custom_layer:
            self.dropout = nn.Dropout(p=cfg.custom_layer['drop'])
            self.activation = get_activation(cfg.custom_layer['activation'])()
            self.classifier = nn.Sequential(
                nn.Linear(self.backbone.num_features, 1024),
                nn.BatchNorm1d(1024),
                self.activation,
                self.dropout,
                nn.Linear(1024, 17)
            )
        else:
            # 기본 분류 헤드
            self.classifier = nn.Linear(self.backbone.num_features, 17)
        
        # 가중치 초기화
        self._initialize_weights()
        
        # Fine-tuning 설정
        self._setup_fine_tuning()
    
    def _initialize_weights(self):
        """가중치 초기화"""
        def weight_init(m):
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
                if hasattr(self.cfg, 'timm') and self.cfg.timm.get('activation') in ['Tanh']:
                    init.xavier_uniform_(m.weight)
                else:
                    init.kaiming_uniform_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm1d) or isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
        
        if self.cfg.fine_tuning == 'scratch':
            self.apply(weight_init)
        elif hasattr(self.cfg, 'custom_layer') and self.cfg.custom_layer:
            self.classifier.apply(weight_init)
    
    def _setup_fine_tuning(self):
        """Fine-tuning 설정"""
        if self.cfg.fine_tuning == 'head':
            # 백본 파라미터 freeze
            for param in self.backbone.parameters():
                param.requires_grad = False
        elif self.cfg.fine_tuning == 'custom':
            # 사용자 정의 freeze (구현 필요)
            pass

    def forward(self, x):
        # 플랫폼별 최적화된 forward
        if hasattr(self.cfg, 'use_channels_last') and self.cfg.use_channels_last:
            x = x.to(memory_format=torch.channels_last)
        
        x = self.backbone(x)
        
        if hasattr(self.cfg, 'custom_layer') and self.cfg.custom_layer:
            x = self.dropout(x)
        
        x = self.classifier(x)
        return x

def get_timm_model(cfg):
    """플랫폼별 최적화된 모델 생성"""
    
    if hasattr(cfg, 'custom_layer') and cfg.custom_layer:
        model = TimmWrapper(cfg)
    else:
        model = timm.create_model(
            cfg.model_name,
            pretrained=cfg.pretrained,
            num_classes=17,
            act_layer=get_activation(cfg.timm.get('activation', 'None'))
        )
        
        # 모델에 따라 'head'가 있는 것도 있고 없는 것도 있다.
        if hasattr(cfg, 'timm') and cfg.timm.get('head', False):
            if cfg.timm['head'].get('drop'):
                model.head.drop.p = cfg.timm['head']['drop']
    
    # 플랫폼별 모델 최적화
    model = optimize_model_for_platform(model, cfg)
    
    return model.to(cfg.device)

def optimize_model_for_platform(model, cfg):
    """플랫폼별 모델 최적화"""
    
    device_type = cfg.device.type if hasattr(cfg.device, 'type') else str(cfg.device)
    
    if device_type == 'cuda':
        # CUDA 최적화
        if hasattr(cfg, 'compile_model') and cfg.compile_model:
            try:
                model = torch.compile(model, mode='reduce-overhead')
                print("⚡ torch.compile 적용 완료")
            except Exception as e:
                print(f"⚠️  torch.compile 실패: {e}")
        
        # 다중 GPU 지원
        if torch.cuda.device_count() > 1 and hasattr(cfg, 'multi_gpu') and cfg.multi_gpu:
            model = nn.DataParallel(model)
            print(f"🔗 DataParallel 적용: {torch.cuda.device_count()}개 GPU")
    
    elif device_type == 'mps':
        # MPS 최적화 (현재 특별한 최적화 없음)
        print("🍎 MPS 모델 준비 완료")
    
    elif device_type == 'cpu':
        # CPU 최적화
        if hasattr(cfg, 'use_channels_last') and cfg.use_channels_last:
            model = model.to(memory_format=torch.channels_last)
            print("⚡ channels_last 메모리 포맷 적용")
    
    return model

def get_criterion(cfg):
    """손실 함수 생성"""
    CRITERIONS = {
        "CrossEntropyLoss": nn.CrossEntropyLoss()
    }
    return CRITERIONS[cfg.criterion]

def get_optimizer(model, cfg):
    """플랫폼별 최적화된 옵티마이저 생성"""
    
    OPTIMIZERS = {
        'SGD': optim.SGD(model.parameters(), lr=cfg.lr),
        'RMSprop': optim.RMSprop(model.parameters(), lr=cfg.lr, alpha=0.99, weight_decay=cfg.weight_decay),
        'Momentum': optim.SGD(model.parameters(), lr=cfg.lr, momentum=0.9),
        'NAG': optim.SGD(model.parameters(), lr=cfg.lr, momentum=0.9, nesterov=True),
        'Adam': optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay),
        'AdamW': optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay),
        'NAdam': optim.NAdam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, momentum_decay=4e-3),
        'RAdam': optim.RAdam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay),
    }
    
    try:
        optimizer = OPTIMIZERS[cfg.optimizer_name]
        
        # 플랫폼별 옵티마이저 최적화
        if hasattr(cfg, 'memory_efficient') and cfg.memory_efficient:
            # 메모리 효율적인 설정
            pass
        
        return optimizer
        
    except KeyError:
        print(f"⚠️  알 수 없는 옵티마이저: {cfg.optimizer_name}, Adam으로 대체")
        return optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)

def get_scheduler(optimizer, cfg, steps_per_epoch):
    """플랫폼별 최적화된 스케줄러 생성"""
    
    SCHEDULERS = {
        'StepLR': lr_scheduler.StepLR(optimizer, step_size=50, gamma=0.1),
        'ExponentialLR': lr_scheduler.ExponentialLR(optimizer, gamma=0.1),
        'CosineAnnealingLR': lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs, eta_min=0),
        'OneCycleLR': lr_scheduler.OneCycleLR(optimizer, max_lr=cfg.lr*10, steps_per_epoch=steps_per_epoch, epochs=cfg.epochs),
        'ReduceLROnPlateau': lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=cfg.patience-5, min_lr=0),
    }
    
    try:
        return SCHEDULERS[cfg.scheduler_name]
    except KeyError:
        print(f"⚠️  알 수 없는 스케줄러: {cfg.scheduler_name}, CosineAnnealingLR으로 대체")
        return lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.epochs, eta_min=0)
