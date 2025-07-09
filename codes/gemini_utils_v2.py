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
import torch.nn.functional as F
import math
from torch.optim.lr_scheduler import _LRScheduler
import matplotlib.pyplot as plt

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

def get_generator(cfg):
    g = torch.Generator()
    g.manual_seed(cfg.random_seed)
    return g

class ImageDataset(Dataset):
    """커스텀 데이터셋 클래스

    :param _type_ Dataset: _description_
    """
    def __init__(self, df:pd.DataFrame, path, transform=None):
        self.df = df
        self.path = path
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        name, target = self.df.iloc[idx]
        # img = np.array(Image.open(os.path.join(self.path, name)))
        img = Image.open(os.path.join(self.path, name))
        if self.transform:
            # img = self.transform(image=img)['image']
            img = self.transform(image=np.array(img))['image']
        return img, target
    
### Getters
def get_activation(activation_option):
    ACTIVATIONS = {
        'None': None,
        'ReLU': nn.ReLU, # 음수는 0으로, 양수는 선형함수
        'LeakyReLU': nn.LeakyReLU, # 음수도 일부 통과 -> Dead ReLU 방지
        'ELU': nn.ELU, # 음수도 일부 통과 → 출력 평균이 0에 가깝도록 함으로써 학습 안정화 도움
        'SELU': nn.SELU, # ELU에 스케일링 계수를 곱해 신경망을 자기 정규화, 특정 조건 (예: fully connected, 특정 초기화, 특정 구조)에서만 자기 정규화 효과가 잘 발휘
        'GELU': nn.GELU, # 더 부드러운 비선형성, Transformer, BERT류
        'Tanh': nn.Tanh, # 완만한 sigmoid
        'PReLU': nn.PReLU, # 음수도 일부 통과 -> Dead ReLU 방지, 기울기를 학습함.
        'SiLU': nn.SiLU, # 더 부드러운 비선형성, EfficientNet, Swin Transformer 등
    }
    return ACTIVATIONS[activation_option]

class TimmWrapper(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        additional_options = {} # dropout 관련 옵션이 있는 모델의 경우
        for key in self.cfg.timm.keys():
            if key != "activation":
                additional_options[key] = self.cfg.timm[key]
        self.backbone = timm.create_model(
            model_name=cfg.model_name,
            pretrained=cfg.pretrained,
            num_classes=0, global_pool='avg',
            act_layer=get_activation(cfg.timm['activation']),
            **additional_options
        )
        # custom_layer 설정 안전하게 접근
        custom_layer = getattr(cfg, 'custom_layer', {})
        self.dropout = nn.Dropout(p=custom_layer.get('drop', 0.2))
        activation_name = custom_layer.get('activation', 'ReLU')
        activation_class = get_activation(activation_name)
        self.activation = activation_class() if activation_class is not None else nn.ReLU()
        head_type = custom_layer.get('head_type', 'complex')
        
        if head_type == "simple_dropout":
            self.classifier = nn.Sequential(
                self.dropout,
                nn.Linear(self.backbone.num_features, 17)
            )
        else :
            self.classifier = nn.Sequential(
                nn.Linear(self.backbone.num_features, 512),
                nn.BatchNorm1d(512),
                self.activation,
                self.dropout,
                nn.Linear(512, 17)
            )
        
        def weight_init(m):
            if isinstance(m, nn.Conv2d) or isinstance(m, nn.Linear):
                if cfg.timm['activation'] in ['Tanh']:
                    # Xavier 초기화
                    init.xavier_uniform_(m.weight)
                else:
                    # He 초기화
                    init.kaiming_uniform_(m.weight, nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm1d) or isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
        if cfg.fine_tuning == 'head':
            # backbone 파라미터를 freeze
            for param in self.backbone.parameters():
                param.requires_grad = False
            # classifier는 가중치 초기화
            self.classifier.apply(weight_init)
        elif cfg.fine_tuning == 'custom':
            # 직접 커스터마이징
            pass
        elif cfg.fine_tuning == 'scratch':
            self.apply(weight_init)

    def forward(self, x):
        x = self.backbone(x)
        x = self.dropout(x)
        x = self.classifier(x)
        return x

def get_timm_model(cfg):
    if hasattr(cfg, 'custom_layer') and cfg.custom_layer:
        return TimmWrapper(cfg).to(cfg.device)

    else: # timm 모델 구조 사용
        additional_options = {} # dropout 관련 옵션이 있는 모델의 경우
        for key in cfg.timm.keys():
            if key != "activation":
                additional_options[key] = cfg.timm[key]
        model = timm.create_model(
            model_name=cfg.model_name,
            pretrained=cfg.pretrained,
            num_classes=17,
            act_layer=get_activation(cfg.timm['activation']),
            **additional_options
        )
        return model.to(cfg.device)
    
class FocalLoss(nn.Module):
    def __init__(self, alpha=1, gamma=2, reduction='mean', weight=None):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction
        self.weight = weight

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none', weight=self.weight)
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1-pt)**self.gamma * ce_loss
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss

class LabelSmoothingLoss(nn.Module):
    def __init__(self, classes, smoothing=0.1, dim=-1, weight=None):
        super(LabelSmoothingLoss, self).__init__()
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.cls = classes
        self.dim = dim
        self.weight = weight

    def forward(self, pred, target):
        pred = pred.log_softmax(dim=self.dim)
        with torch.no_grad():
            true_dist = torch.zeros_like(pred)
            true_dist.fill_(self.smoothing / (self.cls - 1))
            true_dist.scatter_(1, target.data.unsqueeze(1), self.confidence)
        
        per_sample_loss = torch.sum(-true_dist * pred, dim=self.dim)

        if self.weight is not None:
            sample_weights = self.weight[target]
            per_sample_loss = per_sample_loss * sample_weights

        return torch.mean(per_sample_loss)

def get_criterion(cfg, class_weights=None):
    CRITERIONS = {
        "CrossEntropyLoss" : nn.CrossEntropyLoss(label_smoothing=getattr(cfg, 'label_smooth', 0.0), weight=class_weights),
        "FocalLoss": FocalLoss(weight=class_weights),
        "LabelSmoothingLoss": LabelSmoothingLoss(classes=17, smoothing=getattr(cfg, 'label_smooth', 0.1), weight=class_weights)
    }
    return CRITERIONS[cfg.criterion]

def get_optimizer(model, cfg):
    # SGD, RMSprop, Momentum, NAG, Adam, AdamW, NAdam, RAdam, Adafactor
    # optimizer_params = {k: v for k, v in vars(cfg.optimizer_params).items()}
    OPTIMIZERS = {
        'SGD': optim.SGD(model.parameters(), lr=cfg.lr),
        'RMSprop': optim.RMSprop(model.parameters(), lr=cfg.lr, alpha=0.99, weight_decay=cfg.weight_decay),
        'Momentum': optim.SGD(model.parameters(), lr=cfg.lr, momentum=0.9),
        'NAG' : optim.SGD(model.parameters(), lr=cfg.lr, momentum=0.9, nesterov=True),
        'Adam' : optim.Adam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay),
        'AdamW': optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay),
        'NAdam': optim.NAdam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, momentum_decay=4e-3),
        'RAdam': optim.RAdam(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay),
        'Adafactor': optim.Adafactor(model.parameters(), lr=cfg.lr, beta2_decay=-0.8, d=1.0, weight_decay=cfg.weight_decay, maximize=False)
    }
    return OPTIMIZERS[cfg.optimizer_name]

class CosineAnnealingWarmupRestarts(_LRScheduler):
    # ref : https://github.com/katsura-jp/pytorch-cosine-annealing-with-warmup/blob/master/cosine_annealing_warmup/scheduler.py
    def __init__(self, optimizer, first_cycle_steps, cycle_mult=1.0, max_lr=0.1, min_lr=0.001, warmup_steps=0, gamma=1.0, last_epoch=-1):
        assert warmup_steps < first_cycle_steps
        
        self.first_cycle_steps = first_cycle_steps # first cycle step size
        self.cycle_mult = cycle_mult # cycle steps magnification
        self.base_max_lr = max_lr # first max learning rate
        self.max_lr = max_lr # max learning rate in the current cycle
        self.min_lr = min_lr # min learning rate
        self.warmup_steps = warmup_steps # warmup step size
        self.gamma = gamma # decrease rate of max learning rate by cycle
        
        self.cur_cycle_steps = first_cycle_steps # first cycle step size
        self.cycle = 0 # cycle count
        self.step_in_cycle = last_epoch # step size of the current cycle
        
        super(CosineAnnealingWarmupRestarts, self).__init__(optimizer, last_epoch)
        
        # set learning rate min_lr
        self.init_lr()
    
    def init_lr(self):
        self.base_lrs = []
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.min_lr
            self.base_lrs.append(self.min_lr)
    
    def get_lr(self):
        if self.step_in_cycle == -1: # 초기 상태
            return self.base_lrs
        elif self.step_in_cycle < self.warmup_steps:
            # 웜업 단계: 학습률이 min_lr에서 max_lr로 선형적으로 증가합니다.
            return [(self.max_lr - base_lr) * self.step_in_cycle / self.warmup_steps + base_lr for base_lr in self.base_lrs]
        else:
            # 코사인 어닐링 단계: 학습률이 max_lr에서 min_lr로 코사인 함수 형태로 감소합니다.
            return [base_lr + (self.max_lr - base_lr) * \
                    (1 + math.cos(math.pi * (self.step_in_cycle - self.warmup_steps) / \
                                  (self.cur_cycle_steps - self.warmup_steps))) / 2 
                    for base_lr in self.base_lrs]
        
    def step(self, epoch=None):
        if epoch is None:
            epoch = self.last_epoch + 1
            self.step_in_cycle = self.step_in_cycle + 1
            if self.step_in_cycle >= self.cur_cycle_steps:
                self.cycle += 1
                self.step_in_cycle = self.step_in_cycle - self.cur_cycle_steps
                self.cur_cycle_steps = int((self.cur_cycle_steps - self.warmup_steps) * self.cycle_mult) + self.warmup_steps
        else:
            if epoch >= self.first_cycle_steps:
                if self.cycle_mult == 1.:
                    self.step_in_cycle = epoch % self.first_cycle_steps
                    self.cycle = epoch // self.first_cycle_steps
                else:
                    n = int(math.log((epoch / self.first_cycle_steps * (self.cycle_mult - 1) + 1), self.cycle_mult))
                    self.cycle = n
                    self.step_in_cycle = epoch - int(self.first_cycle_steps * (self.cycle_mult ** n - 1) / (self.cycle_mult - 1))
                    self.cur_cycle_steps = self.first_cycle_steps * self.cycle_mult ** (n)
            else:
                self.cur_cycle_steps = self.first_cycle_steps
                self.step_in_cycle = epoch
                
        self.max_lr = self.base_max_lr * (self.gamma**self.cycle)
        self.last_epoch = math.floor(epoch)
        for param_group, lr in zip(self.optimizer.param_groups, self.get_lr()):
            param_group['lr'] = lr

def get_scheduler(optimizer, cfg, steps_per_epoch):
    # scheduler_params 안전하게 접근
    scheduler_params = getattr(cfg, 'scheduler_params', {})
    
    # StepLR, ExponentialLR, CosineAnnealingLR, OneCycleLR, ReduceLROnPlateau
    SCHEDULERS = {
        'StepLR': lr_scheduler.StepLR(optimizer, step_size=scheduler_params.get('step_size', 50), gamma=scheduler_params.get('gamma', 0.1)),
        'ExponentialLR': lr_scheduler.ExponentialLR(optimizer, gamma=scheduler_params.get('gamma', 0.1)),
        'CosineAnnealingLR': lr_scheduler.CosineAnnealingLR(optimizer, T_max=scheduler_params.get('T_max', 1000), eta_min=scheduler_params.get('min_lr', 0)),
        'OneCycleLR': lr_scheduler.OneCycleLR(optimizer, max_lr=scheduler_params.get('max_lr', 0.01), steps_per_epoch=steps_per_epoch, epochs=cfg.epochs),
        'ReduceLROnPlateau': lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=scheduler_params.get('factor', 0.1), patience=cfg.patience-5, min_lr=scheduler_params.get('min_lr', 0)),
        'CosineAnnealingWarmupRestarts': CosineAnnealingWarmupRestarts(optimizer, first_cycle_steps=scheduler_params.get('T_max', 1000), cycle_mult=1.0, max_lr=scheduler_params.get('max_lr', 0.01), min_lr=scheduler_params.get('min_lr', 0), warmup_steps=3, gamma=0.9)
    }
    return SCHEDULERS[cfg.scheduler_name]

def plot_cross_validation(
    train_metrics_list, val_metrics_list, title, cfg, show=False
    ):
    """_summary_

    :param _type_ train_metrics_list: train_losses_for_plot 같은 list
    :param _type_ val_metrics_list: val_losses_for_plot 같은 list
    :param _type_ title: Loss, Accuracy, F1-score 중 하나
    :param _type_ cfg: 설정 namespace
    """
    plt.figure(figsize=(10,6))
    for i in range(cfg.n_folds):
        train_losses = train_metrics_list[i]
        val_losses = val_metrics_list[i]
        plt.plot(x=range(1, len(train_losses)+1), y=train_losses, label=f"Fold-{i+1} Train {title}")
        plt.plot(x=range(1, len(train_losses)+1), y=train_losses, label=f"Fold-{i+1} Val {title}")

    plt.title(f"Cross Validation - {title} Plot")
    plt.xlabel("Epoch")
    plt.ylabel(title)
    plt.legend()
    plt.grid(True, linetyle="--", alpha=0.6)
    if title == "Loss":
        plt.axhline(y=0.001, color='red', linestyle='--', label='(0.001)')
    else:
        plt.axhline(y=0.99, color='red', linestyle='--', label='(0.99)')
    plt.tight_layout()
    savepath = os.path.join(cfg.submission_dir, f"cross-validation_{title}-plot.png")
    plt.savefig(savepath)
    print(f"⚙️ cross validation {title} plot saved in {savepath}")
    if show:
        plt.show()
    plt.clf()

def mixup_data(x, y, alpha=0.4, use_cuda=True):
    """Returns mixed inputs, pairs of targets, and lambda"""
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size(0)
    if use_cuda:
        index = torch.randperm(batch_size).cuda()
    else:
        index = torch.randperm(batch_size)

    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

def cutmix_data(x, y, alpha=0.4):
    """Returns mixed inputs and pairs of targets"""
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size(0)
    index = torch.randperm(batch_size)
    
    # Generate random bounding box
    W, H = x.size(2), x.size(3)
    cut_rat = np.sqrt(1. - lam)
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)
    
    # Uniform sampling
    cx = np.random.randint(W)
    cy = np.random.randint(H)
    
    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)
    
    # Apply cutmix to images
    x[:, :, bbx1:bbx2, bby1:bby2] = x[index, :, bbx1:bbx2, bby1:bby2]
    
    # Adjust lambda to exactly match pixel ratio
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
    
    y_a, y_b = y, y[index]
    return x, y_a, y_b, lam

def mixup_collate_fn(batch, num_classes=17, alpha=0.4):
    """Collate function for mixup augmentation"""
    images, targets = zip(*batch)
    images = torch.stack(images)
    targets = torch.tensor(targets, dtype=torch.long)
    
    # Apply mixup
    mixed_images, targets_a, targets_b, lam = mixup_data(images, targets, alpha)
    
    # Convert to one-hot encoding for soft labels
    targets_a_onehot = F.one_hot(targets_a, num_classes=num_classes).float()
    targets_b_onehot = F.one_hot(targets_b, num_classes=num_classes).float()
    mixed_targets = lam * targets_a_onehot + (1 - lam) * targets_b_onehot
    
    return mixed_images, mixed_targets

def cutmix_collate_fn(batch, num_classes=17, alpha=0.4):
    """Collate function for cutmix augmentation"""
    images, targets = zip(*batch)
    images = torch.stack(images)
    targets = torch.tensor(targets, dtype=torch.long)
    
    # Apply cutmix
    mixed_images, targets_a, targets_b, lam = cutmix_data(images, targets, alpha)
    
    # Convert to one-hot encoding for soft labels
    targets_a_onehot = F.one_hot(targets_a, num_classes=num_classes).float()
    targets_b_onehot = F.one_hot(targets_b, num_classes=num_classes).float()
    mixed_targets = lam * targets_a_onehot + (1 - lam) * targets_b_onehot
    
    return mixed_images, mixed_targets

def run_training_cycle(train_df, val_df, cfg, run, train_transforms, val_transform):
    """Refactored training cycle function for modularity"""
    from torch.utils.data import DataLoader, ConcatDataset, WeightedRandomSampler
    from codes.gemini_augmentation_v2 import augment_class_imbalance, augment_validation, delete_offline_augmented_images
    from codes.gemini_train_v2 import TrainModule
    
    augmented_ids, val_augmented_ids = [], []
    
    try:
        # 클래스 불균형 해소를 위한 이미지 offline 증강
        if hasattr(cfg, 'class_imbalance') and cfg.class_imbalance:
            new_augmented_ids, augmented_labels = augment_class_imbalance(cfg, train_df)
            augmented_ids.extend(new_augmented_ids)
            imb_aug_df = pd.DataFrame({"ID": new_augmented_ids, "target": augmented_labels})
            train_df = pd.concat([train_df, imb_aug_df], ignore_index=True).reset_index(drop=True)

        # validation 데이터를 offline으로 eda 증강을 적용
        if val_df is not None and getattr(cfg, 'val_TTA', False):
            new_val_augmented_ids, augmented_labels = augment_validation(cfg, val_df)
            val_augmented_ids.extend(new_val_augmented_ids)
            val_aug_df = pd.DataFrame({"ID": new_val_augmented_ids, "target": augmented_labels})
            val_df = pd.concat([val_df, val_aug_df], ignore_index=True).reset_index(drop=True)

        # Sampler 설정
        sampler = None
        shuffle = True
        if getattr(cfg, 'weighted_random_sampler', False):
            targets = train_df['target'].values
            class_counts = np.bincount(targets)
            class_weights = 1. / class_counts
            weights = class_weights[targets]
            g = get_generator(cfg)
            sampler = WeightedRandomSampler(weights, len(weights), generator=g)
            shuffle = False

        # Dataset 생성
        if cfg.online_augmentation:
            train_dataset = ImageDataset(train_df, os.path.join(cfg.data_dir, "train"), transform=train_transforms[0])
        else:
            datasets = [ImageDataset(train_df, os.path.join(cfg.data_dir, "train"), transform=t) for t in train_transforms]
            train_dataset = ConcatDataset(datasets)
        
        val_loader = None
        if val_df is not None:
            val_dataset = ImageDataset(val_df, os.path.join(cfg.data_dir, "train"), transform=val_transform)
            val_loader = DataLoader(val_dataset, batch_size=cfg.batch_size, shuffle=False, num_workers=8, pin_memory=True)

        # Check for mixup/cutmix in online_aug settings
        train_collate = None
        if hasattr(cfg, 'online_aug'):
            if getattr(cfg.online_aug, 'mixup', False):
                train_collate = lambda batch: mixup_collate_fn(batch, num_classes=17, alpha=0.4)
            elif getattr(cfg.online_aug, 'cutmix', False):
                train_collate = lambda batch: cutmix_collate_fn(batch, num_classes=17, alpha=0.4)
        elif hasattr(cfg, 'augmentation'):
            # Fallback to old augmentation settings
            if getattr(cfg.augmentation, 'mixup', False):
                train_collate = lambda batch: mixup_collate_fn(batch, num_classes=17, alpha=0.4)
            elif getattr(cfg.augmentation, 'cutmix', False):
                train_collate = lambda batch: cutmix_collate_fn(batch, num_classes=17, alpha=0.4)
                
        # DataLoader 생성
        train_loader = DataLoader(
            train_dataset, 
            batch_size=cfg.batch_size, 
            sampler=sampler, 
            shuffle=shuffle, 
            num_workers=8, 
            pin_memory=True, 
            collate_fn=train_collate
        )

        # TrainModule 정의
        model = get_timm_model(cfg)
        class_weights = None
        if hasattr(cfg, 'class_weighting') and cfg.class_weighting:
            class_counts = train_df['target'].value_counts().sort_index()
            weights = 1.0 / class_counts
            class_weights = torch.tensor(weights.values, dtype=torch.float32).to(cfg.device)
        
        criterion = get_criterion(cfg, class_weights=class_weights)
        optimizer = get_optimizer(model, cfg)
        scheduler = get_scheduler(optimizer, cfg, steps_per_epoch=len(train_loader))

        trainer = TrainModule(
            model=model,
            criterion=criterion,
            optimizer=optimizer,
            scheduler=scheduler,
            train_loader=train_loader,
            valid_loader=val_loader,
            cfg=cfg,
            verbose=1,
            run=run
        )

        # 학습
        train_result = trainer.training_loop()
        if not train_result:
            raise ValueError("Failed to train model...")

        return trainer, augmented_ids, val_augmented_ids, val_df, val_loader
        
    except Exception as e:
        # 에러 발생 시 정리
        delete_offline_augmented_images(cfg=cfg, augmented_ids=augmented_ids)
        delete_offline_augmented_images(cfg=cfg, augmented_ids=val_augmented_ids)
        raise e