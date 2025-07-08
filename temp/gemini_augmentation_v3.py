import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2
import os
import torch
import numpy as np
import random

# 🔥 Phase 1: MixUp 구현
def mixup_data(x, y, alpha=1.0, device='cpu'):
    """MixUp data augmentation
    
    Args:
        x: input images (batch_size, channels, height, width)
        y: input labels (batch_size,)
        alpha: mixup interpolation coefficient
        device: device to perform operations on
    
    Returns:
        mixed_x: mixed images
        y_a, y_b: original labels
        lam: mixing coefficient
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(device)
    
    mixed_x = lam * x + (1 - lam) * x[index, :]
    y_a, y_b = y, y[index]
    
    return mixed_x, y_a, y_b, lam

# 🔥 Phase 1: CutMix 구현
def cutmix_data(x, y, alpha=1.0, device='cpu'):
    """CutMix data augmentation
    
    Args:
        x: input images (batch_size, channels, height, width)
        y: input labels (batch_size,)
        alpha: cutmix interpolation coefficient
        device: device to perform operations on
    
    Returns:
        mixed_x: mixed images
        y_a, y_b: original labels
        lam: mixing coefficient (adjusted)
    """
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(device)
    
    # Generate random bounding box
    _, _, H, W = x.shape
    cut_rat = np.sqrt(1. - lam)  # paper recommendation
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)
    
    # Uniform random location
    cx = np.random.randint(W)
    cy = np.random.randint(H)
    
    bbx1 = np.clip(cx - cut_w // 2, 0, W)
    bby1 = np.clip(cy - cut_h // 2, 0, H)
    bbx2 = np.clip(cx + cut_w // 2, 0, W)
    bby2 = np.clip(cy + cut_h // 2, 0, H)
    
    # Apply cutmix
    mixed_x = x.clone()
    mixed_x[:, :, bby1:bby2, bbx1:bbx2] = x[index, :, bby1:bby2, bbx1:bbx2]
    
    # Adjust lambda to match the actual area ratio
    lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (W * H))
    
    y_a, y_b = y, y[index]
    
    return mixed_x, y_a, y_b, lam

# 🔥 Phase 1: MixUp/CutMix 손실 계산
def mixup_criterion(criterion, pred, y_a, y_b, lam):
    """Calculate mixed loss for MixUp/CutMix"""
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)

# 🔥 Phase 1: MixUp/CutMix 적용 함수
def apply_mixup_cutmix(x, y, cfg, device='cpu'):
    """Apply MixUp or CutMix based on configuration
    
    Args:
        x: input images
        y: input labels  
        cfg: configuration with mixup_cutmix settings
        device: device to perform operations on
    
    Returns:
        mixed_x, y_a, y_b, lam, use_mixup_cutmix
    """
    mixup_cutmix_config = getattr(cfg, 'mixup_cutmix', {})
    
    # Check if we should apply mixup/cutmix
    prob = mixup_cutmix_config.get('prob', 0.0)
    if prob <= 0 or np.random.rand() > prob:
        return x, y, y, 1.0, False
    
    # Choose between MixUp and CutMix
    switch_prob = mixup_cutmix_config.get('switch_prob', 0.5)
    use_cutmix = np.random.rand() < switch_prob
    
    mixup_alpha = mixup_cutmix_config.get('mixup_alpha', 1.0)
    cutmix_alpha = mixup_cutmix_config.get('cutmix_alpha', 1.0)
    
    if use_cutmix:
        mixed_x, y_a, y_b, lam = cutmix_data(x, y, cutmix_alpha, device)
    else:
        mixed_x, y_a, y_b, lam = mixup_data(x, y, mixup_alpha, device)
    
    return mixed_x, y_a, y_b, lam, True

AUG = {
    'eda': A.Compose([
        # Brightness, Contrast, ColorJitter
        A.ColorJitter(brightness=0.1, contrast=0.07, saturation=0.07, hue=0.07, p=1.0),
        # 공간 변형에 대한 증강
        A.Affine(
            scale=(0.85, 1.15),
            translate_percent=(-0.05,0.05),
            rotate=(-20,30),
            fill=(255,255,255),
            shear=(-5, 5),
            p=1.0
        ),
        # x,y 좌표 반전 
        A.HorizontalFlip(p=0.6),
        A.VerticalFlip(p=0.6),
        A.Transpose(p=0.6),    
        # Blur & Noise
        A.OneOf([
            A.GaussianBlur(sigma_limit=(0.5, 2.5), p=1.0),
            A.Blur(blur_limit=(3, 9), p=1.0),
        ], p=1.0),
        A.GaussNoise(std_range=(0.0025, 0.2), p=1.0),            
    ]),
    'dilation': A.Compose([
        A.Morphological(p=1, scale=(1, 3), operation="dilation"),
        # 공간 변형에 대한 증강
        A.Affine(
            scale=(0.85, 1.15),
            translate_percent=(-0.05,0.05),
            rotate=(-20,30),
            fill=(255,255,255),
            shear=(-5, 5),
            p=0.9
        ),
        # x,y 좌표 반전 
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),    
        A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=1),
        A.RandomBrightnessContrast(p=1),
    ]),
    'erosion': A.Compose([
        A.Morphological(p=1, scale=(2, 4), operation="erosion"),
        # 공간 변형에 대한 증강
        A.Affine(
            scale=(0.85, 1.15),
            translate_percent=(-0.05,0.05),
            rotate=(-20,30),
            fill=(255,255,255),
            shear=(-5, 5),
            p=0.9
        ),
        # x,y 좌표 반전 
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),    
        A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=1),
        A.RandomBrightnessContrast(p=1),
    ]),
    'basic': A.Compose([ ### 색조/밝기/대비 변화를 최소화하고 기하학전 변환에 초점을 둔 약한 증강. 노이즈/블러도 없음.
        # 1. 픽셀 값 기반 변환 (이미지 자체의 픽셀 값에 영향을 줌)
        # 이 변환들은 기하학적 변환 전에 적용하는 것이 좋습니다.
        A.RGBShift(
            r_shift_limit=20,  # Red 채널 최대 변화량 (-20 ~ +20)
            g_shift_limit=20,  # Green 채널 최대 변화량 (-20 ~ +20)
            b_shift_limit=20,  # Blue 채널 최대 변화량 (-20 ~ +20)
            p=0.5 # 50% 확률로 적용
        ),
        A.RandomBrightnessContrast(
            brightness_limit=0.2, # 밝기 변화량 (-0.2 ~ +0.2)
            contrast_limit=0.2,   # 대비 변화량 (-0.2 ~ +0.2)
            p=0.5 # 50% 확률로 적용
        ),
        
        # 2. 기하학적 변환 (이미지의 형태, 위치, 크기에 영향을 줌)
        # 이 변환들은 픽셀 기반 변환 이후에 적용하여 일관성을 유지하는 것이 좋습니다.
        # Transpose는 이미지를 전치(transpose)합니다 (행과 열을 바꿉니다).
        # 이는 이미지의 90도 회전과 대칭 조합과 유사하게 작동합니다.
        # ShiftScaleRotate와 함께 사용하면 더 다양한 방향의 변형을 줄 수 있습니다.
        A.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)}, # X, Y 축 개별 스케일
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # X, Y 축 개별 이동
            rotate=(-15, 20), # 회전 각도
            shear=(-10, 10),  # 전단 변환 (이미지를 기울임)
            p=0.5, # 50% 확률로 적용
            fill=(255,255,255) # 이미지 외부 = 흰색으로 채우기
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),            
    ]),
    'middle': A.Compose([ # 노이즈/블러 + 기하학적 변환에 초점을 둔 중간 난이도의 변환
        
        # 노이즈 효과 (둘 중 하나만 적용, 문서 품질 저하를 시뮬레이션)
        A.OneOf([
            A.GaussNoise(std_range=(0.01, 0.3), p=1.0),
            A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=1.0)
        ], p=0.3), # 노이즈도 너무 강하면 인식 어렵기에 적당한 확률 (0.2 유지)

        # 2. 기하학적 변환 및 문서 특화 변형 (형태 왜곡, 시점 변화)
        # Perspective, GridDistortion, ElasticTransform은 강한 비선형 변환이므로
        # OneOf로 묶거나 각자의 확률을 낮춰 과도한 왜곡을 방지합니다.
        # 여기서는 문서의 "찌그러짐/왜곡"을 시뮬레이션하기 위해 OneOf로 묶는 것이 효과적입니다.
        A.OneOf([
            # 문서 원근 변환 (0.05~0.1 스케일은 적절)
            A.Perspective(scale=(0.05, 0.1), p=1.0),
            # 그리드 왜곡 (num_steps=5, distort_limit=0.1 적절)
            A.GridDistortion(num_steps=5, distort_limit=0.2, p=1.0),
        ], p=0.3), # 이 세 가지 강한 왜곡 중 하나를 30% 확률로 적용 (개별 p값이 1.0이므로 OneOf의 p가 중요)
        # 원본에서 각 p=0.3, 0.2, 0.1로 각각 적용되었으나, 이제는 OneOf로 묶어 총 적용 확률을 0.3으로 설정했습니다.
        # 이렇게 하면 세 가지 중복되는 왜곡 효과를 동시에 얻는 경우를 줄여줍니다.
        
        # 기본 기하학적 변환 (Shift, Scale, Rotate)
        # 문서의 경우 회전 제한이 중요 (원본에서 min(config.rotation_limit, 15)로 제한)
        A.Affine(
            scale=(0.8, 1.2),
            translate_percent=(-0.0625, 0.0625),
            rotate=(-120, 120), # 회전 각도
            shear=(-5, 5),  # 전단 변환 (이미지를 기울임)
            p=1.0, 
            fill=(255,255,255) # 이미지 외부 = 흰색으로 채우기
        ),

        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5)
    ]),
    'aggressive': A.Compose([
        # 정보 가리기 및 혼합 (Occlusion & Mixing)
        # Train의 마스킹과 유사한 효과를 주어 모델이 특정 영역에 의존하지 않도록함
        A.CoarseDropout(
            num_holes_range=(3, 5),
            hole_height_range=(10, 35),
            hole_width_range=(5, 45),
            fill=(0,0,0),
            p=0.9
        ),
        # 강력한 기하학적 변환
        A.OneOf([
            # Affine의 범위를 크게 늘리고, Perspective 변환을 추가하여 왜곡 시뮬레이션
            A.Affine(
                scale=(0.7, 1.3),
                translate_percent=(-0.15,0.2),
                rotate=(-45, 45), # 회전 각도
                shear=(-10, 10),  # 전단 변환 (이미지를 기울임)
                p=1.0, # 50% 확률로 적용
                fill=(255,255,255) # 이미지 외부 = 흰색으로 채우기
            ),
            A.Perspective(scale=(0.05, 0.1),fill=(255,255,255),p=1.0),
        ], p=0.9),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),
        # 노이즈 효과 (둘 중 하나만 적용, 문서 품질 저하를 시뮬레이션)
        A.OneOf([
            A.GaussNoise(std_range=(0.01, 0.3), p=1.0), 
            A.ISONoise(color_shift=(0.01, 0.2), intensity=(0.1, 0.5), p=1.0)
        ], p=0.3), # 노이즈도 너무 강하면 인식 어렵기에 적당한 확률 
        A.OneOf([
            # 스캔/촬영 시 발생할 수 있는 블러 효과
            A.GaussianBlur(blur_limit=(3, 7), p=1.0),
            A.MotionBlur(blur_limit=(3, 7), p=1.0),
            # 이미지 품질을 낮춰 압축/해상도 저하 효과 모방
            A.Downscale(scale_range=(0.5, 0.75), p=1.0),
        ], p=0.5),

        # 색상 및 대비의 급격한 변화
        A.OneOf([
            # 문서의 조명, 스캔 품질 변화 모방
            A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=1.0),
            A.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1, p=1.0),
            # 히스토그램 평활화를 통해 대비를 극적으로 변경
            A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=1.0),
        ], p=0.8),
    ]),
    # 🔥 Phase 1: MixUp과 CutMix는 이미 pytorch 레벨에서 구현하므로 여기서는 플레이스홀더만 추가
    'mixup': A.Compose([
        # MixUp은 pytorch 레벨에서 처리되므로 여기서는 일반 증강만
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
    ]),
    'cutmix': A.Compose([
        # CutMix는 pytorch 레벨에서 처리되므로 여기서는 일반 증강만
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
    ]),
}

def get_augmentation(cfg, epoch=0):
    common_resize_transform = A.Compose([
        # 긴 변을 기준으로 종횡비를 유지하며 resize
        A.LongestMaxSize(max_size=cfg.image_size),
        # cfg.image_size 정사각형으로 만들고, 여백은 흰색으로 채움.
        A.PadIfNeeded(min_height=cfg.image_size, min_width=cfg.image_size, border_mode=cv2.BORDER_CONSTANT, fill=(255, 255, 255), p=1.0),
        A.Normalize(mean=cfg.norm_mean, std=cfg.norm_std),
        ToTensorV2(),
    ])

    # epoch에 따라 동적으로 변환하는 증강 기법
    if cfg.dynamic_augmentation['enabled']:
        
        weak_policy = cfg.dynamic_augmentation['policies']['weak']
        middle_policy = cfg.dynamic_augmentation['policies']['middle']
        strong_policy = cfg.dynamic_augmentation['policies']['strong']

        if epoch < weak_policy['end_epoch']:
            print("⚙️ Using weak_policy augmentation...")
            active_augs = [AUG[aug] for aug in weak_policy['augs'] if aug in AUG]
        elif epoch < middle_policy['end_epoch']:
            print("⚙️ Using middle_policy augmentation...")
            active_augs = [AUG[aug] for aug in middle_policy['augs'] if aug in AUG]
        elif epoch < strong_policy['end_epoch']:
            print("⚙️ Using strong_policy augmentation...")
            active_augs = [AUG[aug] for aug in strong_policy['augs'] if aug in AUG]
        else:
            active_augs = [AUG[aug] for aug in strong_policy['augs'] if aug in AUG]
    else:
        active_augs = [AUG[aug] for aug, active in cfg.augmentation.items() if active and aug in AUG]

    train_transforms = []

    if cfg.online_augmentation:
        # online augmentation 학습 : 실시간으로 증강 기법을 적용하여, 더 다양한 증강 형태의 데이터를 학습할 수 있다.
        # 장점 : 무한한 다양성, 과적합 방지 효과 증대, 저장 공간 효율성
        # 단점 : 전처리 과정의 증가로 학습 시간 증가, 재현성이 떨어짐. 너무 많은 증강 기법을 적용하면, 의도치 않은 결과가 나올 수 있다.
        if active_augs:
            online_transform = A.Compose([
                A.OneOf(active_augs, p=0.85), # 85% 확률로 active_augs에 설정된 증강 기법들이 적용된다. 15% 확률로 원본 train 데이터를 사용한다.
                common_resize_transform # Resize 기법은 항상 동일하게.
            ])
            train_transforms.append(online_transform)
        else: # 따로 지정한 증강 기법이 없는 경우, Resize 기법만 사용
            train_transforms.append(common_resize_transform)
    else:
        # offline augmentation 학습 : 개별적으로 dataset을 만들어 ConcatDataset을 최종 생성한다. 모든 증강 기법을 적용 가능하고, 마치 데이터셋 개수 자체가 늘어난 것 같은 효과를 준다. (원래라면, 증강한 데이터를 저장해야 하지만 이건 생략.)
        # 단점 : 다양성 제한
        if active_augs:
            for aug_pipeline in active_augs: # 각각의 aug를 transform_func으로 만든다.
                train_transforms.append(A.Compose([aug_pipeline, common_resize_transform]))
        else:
            train_transforms.append(common_resize_transform)

    # validation 증강은 기본 증강만 사용한다.
    val_transform = common_resize_transform

    # Validation transform with 'eda' augmentation to simulate test conditions
    # tta_transform은 TTA에서도 사용할 증강이다.
    val_tta_transform = A.Compose([
        AUG['eda'],
        common_resize_transform
    ])
    test_tta_transform = A.Compose([
        # inference time transform은 해당 코드에서 직접 구현.
        common_resize_transform
    ])


    return train_transforms, val_transform, val_tta_transform, test_tta_transform

### Offline augmentation
def augment_class_imbalance(cfg, train_df):
    # Cutout 증강 파이프라인 설정
    cutout_transform = A.Compose([
        # 이미지 크기 조정
        A.CoarseDropout(
            num_holes_range=(1, 2), # 마스킹 개수
            hole_height_range=(int(cfg.image_size * 0.05), int(cfg.image_size * 0.1)), # 마스킹의 높이 범위
            hole_width_range=(int(cfg.image_size * 0.05), int(cfg.image_size * 0.2)), # 마스킹의 너비 범위
            fill=(0,0,0), # 검정색 마스킹
            p=1.0
        )
    ])
    # 증강 대상 클래스
    augment_classes = cfg.class_imbalance['aug_class']
    max_samples = cfg.class_imbalance['max_samples']

    # 증강 이미지, 라벨, ID 리스트 초기화
    augmented_labels = []    # 증강된 이미지 라벨
    augmented_ids = []       # 증강된 이미지 ID
    total_augmented = 0
    # 증강 대상 클래스 루프
    for cls in augment_classes:
        print(cls, "클래스")
        cls_df = train_df[train_df['target'] == cls]
        current_count = len(cls_df)
        print("현재 개수:", current_count)
        # 목표 샘플 수에 도달하기 위해 필요한 증강 이미지 개수 계산
        # (current_count가 max_samples보다 많으면 0 또는 음수가 됨)
        to_generate = max_samples - current_count
        print("증강 개수:", to_generate)
        # 만약 현재 이미지 수가 목표치보다 많거나 같으면 증강할 필요 없으므로 다음 클래스로 넘어감
        if to_generate <= 0:
            continue
        # 증강할 이미지들을 원본 데이터프레임에서 샘플링 (중복 허용: replace=True)
        # 목표 샘플 수 (to_generate)만큼 이미지를 샘플링하며,
        # 만약 현재 이미지 개수(current_count)가 to_generate보다 적으면 중복 선택(replace=True)
        # 이 부분은 원래 코드의 `if/else` 조건문을 통합한 것입니다.
        sampled_df = cls_df.sample(n=to_generate, replace=False, random_state=cfg.random_seed).reset_index(drop=True)
        # 샘플링된 각 이미지에 대해 증강 수행 및 저장
        for idx, row in sampled_df.iterrows():
            img_id = row['ID']
            img_path = os.path.join(cfg.data_dir, 'train', img_id)
            # 이미지 로드 (OpenCV는 기본적으로 BGR로 로드)
            img = cv2.imread(img_path)
            # BGR 이미지를 RGB로 변환 (Albumentations는 RGB를 기대)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # 정의된 Cutout 증강 적용
            augmented_img = cutout_transform(image=img)['image']

            # 증강된 이미지의 새로운 ID 생성 (기존 ID 앞에 'aug_' 접두사 추가)
            new_id = f"aug_{img_id}"
            save_path = os.path.join(cfg.data_dir, 'train', new_id)

            # 증강된 RGB 이미지를 다시 BGR로 변환하여 파일로 저장
            cv2.imwrite(save_path, cv2.cvtColor(augmented_img, cv2.COLOR_RGB2BGR))

            # 증강된 이미지의 라벨과 ID를 리스트에 추가
            augmented_labels.append(cls)
            augmented_ids.append(new_id)
            total_augmented += 1
        print(f"총 {total_augmented} 개의 이미지 증강")
    return augmented_ids, augmented_labels

def augment_validation(cfg, val_df):
    # 증강 이미지, 라벨, ID 리스트 초기화
    augmented_labels = []    # 증강된 이미지 라벨
    augmented_ids = []       # 증강된 이미지 ID
    total_augmented = 0
    val_tta_transform = AUG['eda']
    # 증강 대상 클래스 루프
    for idx, row in val_df.iterrows():
        img_id = row['ID']
        cls = row['target']
        img_path = os.path.join(cfg.data_dir, 'train', img_id)
        # 이미지 로드 (OpenCV는 기본적으로 BGR로 로드)
        img = cv2.imread(img_path)
        # BGR 이미지를 RGB로 변환 (Albumentations는 RGB를 기대)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 정의된 Cutout 증강 적용 > 총 4번 적용
        for i_ in range(4):
            augmented_img = val_tta_transform(image=img)['image']

            # 증강된 이미지의 새로운 ID 생성 (기존 ID 앞에 'aug_' 접두사 추가)
            new_id = f"val{i_}_{img_id}"
            save_path = os.path.join(cfg.data_dir, 'train', new_id)

            # 증강된 RGB 이미지를 다시 BGR로 변환하여 파일로 저장
            cv2.imwrite(save_path, cv2.cvtColor(augmented_img, cv2.COLOR_RGB2BGR))

            # 증강된 이미지의 라벨과 ID를 리스트에 추가
            augmented_labels.append(cls)
            augmented_ids.append(new_id)
            total_augmented += 1
    print(f"총 {total_augmented} 개의 validation 이미지 증강")
    return augmented_ids, augmented_labels

def delete_offline_augmented_images(cfg, augmented_ids):
    train_dir = os.path.join(cfg.data_dir, 'train')
    _ = 0
    for filename in augmented_ids:
        file_path = os.path.join(train_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            _ += 1
        else:
            print("Wrong filename:", file_path)
    print(_,"개 이미지 제거")
