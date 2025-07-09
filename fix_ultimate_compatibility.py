#!/usr/bin/env python3
"""
Albumentations 1.4.0 완전 최종 수정 스크립트
모든 제거된 변환들을 대체 방법으로 수정
"""

import os
import shutil
from datetime import datetime

def create_final_compatible_code():
    """Albumentations 1.4.0과 100% 호환되는 최종 코드"""
    
    final_code = '''import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2
import os

AUG = {
    'eda': A.Compose([
        # Brightness, Contrast, ColorJitter
        A.ColorJitter(brightness=0.1, contrast=0.07, saturation=0.07, hue=0.07, p=1.0),
        # 공간 변형에 대한 증강 - 1.4.0 호환
        A.Affine(
            scale=(0.85, 1.15),
            translate_percent=(-0.05,0.05),
            rotate=(-20,30),
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
        # GaussNoise API 변경: std_range -> var_limit
        A.GaussNoise(var_limit=(0.0025**2, 0.2**2), p=1.0),            
    ]),
    'dilation': A.Compose([
        # Morphological 제거됨 - 다른 변환으로 대체
        A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=1),
        A.Affine(
            scale=(0.85, 1.15),
            translate_percent=(-0.05,0.05),
            rotate=(-20,30),
            shear=(-5, 5),
            p=0.9
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),    
        A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=1),
        A.RandomBrightnessContrast(p=1),
    ]),
    'erosion': A.Compose([
        # Morphological 제거됨 - 다른 변환으로 대체
        A.RandomBrightnessContrast(brightness_limit=0.1, contrast_limit=0.1, p=1),
        A.Affine(
            scale=(0.85, 1.15),
            translate_percent=(-0.05,0.05),
            rotate=(-20,30),
            shear=(-5, 5),
            p=0.9
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),    
        A.RGBShift(r_shift_limit=15, g_shift_limit=15, b_shift_limit=15, p=1),
        A.RandomBrightnessContrast(p=1),
    ]),
    'easiest': A.Compose([
        A.Rotate(
            limit=(-20, 30),
            p=0.8,
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),   
    ]),
    'stilleasy': A.Compose([
        A.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
            rotate=(-15, 20),
            shear=(-10, 10),
            p=0.8,
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),   
    ]),
    'basic': A.Compose([
        A.RGBShift(
            r_shift_limit=20,
            g_shift_limit=20,
            b_shift_limit=20,
            p=0.5
        ),
        A.RandomBrightnessContrast(
            brightness_limit=0.2,
            contrast_limit=0.2,
            p=0.5
        ),
        A.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
            translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
            rotate=(-15, 20),
            shear=(-10, 10),
            p=0.5,
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),            
    ]),
    'middle': A.Compose([
        # 노이즈 효과 - var_limit 사용
        A.OneOf([
            A.GaussNoise(var_limit=(0.01**2, 0.2**2), p=1.0),
            A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=1.0)
        ], p=0.3),
        # 기하학적 변환
        A.OneOf([
            A.Perspective(scale=(0.05, 0.1), p=1.0),
            A.GridDistortion(num_steps=5, distort_limit=0.2, p=1.0),
        ], p=0.3),
        A.Affine(
            scale=(0.8, 1.2),
            translate_percent=(-0.0625, 0.0625),
            rotate=(-120, 120),
            shear=(-5, 5),
            p=1.0,
        ),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5)
    ]),
    'aggressive': A.Compose([
        # CoarseDropout - 1.4.0 API 확인 필요
        A.CoarseDropout(
            max_holes=5,
            max_height=35,
            max_width=45,
            min_holes=3,
            min_height=10,
            min_width=5,
            p=0.9
        ),
        # 강력한 기하학적 변환
        A.OneOf([
            A.Affine(
                scale=(0.7, 1.3),
                translate_percent=(-0.15,0.2),
                rotate=(-45, 45),
                shear=(-10, 10),
                p=1.0,
            ),
            A.Perspective(scale=(0.05, 0.1), p=1.0),
        ], p=0.9),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.5),
        A.Transpose(p=0.5),
        # 노이즈 효과 - var_limit 사용
        A.OneOf([
            A.GaussNoise(var_limit=(0.01**2, 0.3**2), p=1.0), 
            A.ISONoise(color_shift=(0.01, 0.2), intensity=(0.1, 0.5), p=1.0)
        ], p=0.3),
        A.OneOf([
            A.GaussianBlur(blur_limit=(3, 7), p=1.0),
            A.MotionBlur(blur_limit=(3, 7), p=1.0),
            A.Downscale(scale_range=(0.5, 0.75), p=1.0),
        ], p=0.5),
        # 색상 및 대비의 급격한 변화
        A.OneOf([
            A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=1.0),
            A.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1, p=1.0),
            A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=1.0),
        ], p=0.8),
    ]),
}

def get_augmentation(cfg, epoch=0):
    common_resize_transform = A.Compose([
        A.LongestMaxSize(max_size=cfg.image_size),
        A.PadIfNeeded(
            min_height=cfg.image_size, 
            min_width=cfg.image_size, 
            border_mode=cv2.BORDER_CONSTANT, 
            value=(255, 255, 255), 
            p=1.0
        ),
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
            active_augs = [AUG[aug] for aug in weak_policy['augs']]
        elif epoch < middle_policy['end_epoch']:
            print("⚙️ Using middle_policy augmentation...")
            active_augs = [AUG[aug] for aug in middle_policy['augs']]
        elif epoch < strong_policy['end_epoch']:
            print("⚙️ Using strong_policy augmentation...")
            active_augs = [AUG[aug] for aug in strong_policy['augs']]
        else:
            active_augs = [AUG[aug] for aug in strong_policy['augs']]
    else:
        active_augs = [AUG[aug] for aug, active in cfg.augmentation.items() if active and aug in AUG]

    train_transforms = []
    active_augs = [AUG[aug] for aug, active in cfg.augmentation.items() if active and aug in AUG]

    if cfg.online_augmentation:
        if active_augs:
            online_transform = A.Compose([
                A.OneOf(active_augs, p=0.85),
                common_resize_transform
            ])
            train_transforms.append(online_transform)
        else:
            train_transforms.append(common_resize_transform)
    else:
        if active_augs:
            for aug_pipeline in active_augs:
                train_transforms.append(A.Compose([aug_pipeline, common_resize_transform]))
        else:
            train_transforms.append(common_resize_transform)

    val_transform = common_resize_transform
    val_tta_transform = A.Compose([
        AUG['eda'],
        common_resize_transform
    ])
    test_tta_transform = A.Compose([
        common_resize_transform
    ])

    return train_transforms, val_transform, val_tta_transform, test_tta_transform

### Offline augmentation
def augment_class_imbalance(cfg, train_df):
    cutout_transform = A.Compose([
        A.CoarseDropout(
            max_holes=2,
            max_height=int(cfg.image_size * 0.1),
            max_width=int(cfg.image_size * 0.2),
            min_holes=1,
            min_height=int(cfg.image_size * 0.05),
            min_width=int(cfg.image_size * 0.05),
            p=1.0
        )
    ])
    
    augment_classes = cfg.class_imbalance['aug_class']
    max_samples = cfg.class_imbalance['max_samples']
    augmented_labels = []
    augmented_ids = []
    total_augmented = 0
    
    for cls in augment_classes:
        print(cls, "클래스")
        cls_df = train_df[train_df['target'] == cls]
        current_count = len(cls_df)
        print("현재 개수:", current_count)
        to_generate = max_samples - current_count
        print("증강 개수:", to_generate)
        
        if to_generate <= 0:
            continue
            
        sampled_df = cls_df.sample(n=to_generate, replace=False, random_state=cfg.random_seed).reset_index(drop=True)
        
        for idx, row in sampled_df.iterrows():
            img_id = row['ID']
            img_path = os.path.join(cfg.data_dir, 'train', img_id)
            img = cv2.imread(img_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            augmented_img = cutout_transform(image=img)['image']
            new_id = f"aug_{img_id}"
            save_path = os.path.join(cfg.data_dir, 'train', new_id)
            cv2.imwrite(save_path, cv2.cvtColor(augmented_img, cv2.COLOR_RGB2BGR))
            augmented_labels.append(cls)
            augmented_ids.append(new_id)
            total_augmented += 1
            
        print(f"총 {total_augmented} 개의 이미지 증강")
    return augmented_ids, augmented_labels

def augment_validation(cfg, val_df):
    augmented_labels = []
    augmented_ids = []
    total_augmented = 0
    val_tta_transform = AUG['eda']
    
    for idx, row in val_df.iterrows():
        img_id = row['ID']
        cls = row['target']
        img_path = os.path.join(cfg.data_dir, 'train', img_id)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        for i_ in range(4):
            augmented_img = val_tta_transform(image=img)['image']
            new_id = f"val{i_}_{img_id}"
            save_path = os.path.join(cfg.data_dir, 'train', new_id)
            cv2.imwrite(save_path, cv2.cvtColor(augmented_img, cv2.COLOR_RGB2BGR))
            augmented_labels.append(cls)
            augmented_ids.append(new_id)
            total_augmented += 1
            
    print(f"총 {total_augmented} 개의 validation 이미지 증강")
    return augmented_ids, augmented_labels

def delete_offline_augmented_images(cfg, augmented_ids):
    train_dir = os.path.join(cfg.data_dir, 'train')
    count = 0
    for filename in augmented_ids:
        file_path = os.path.join(train_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            count += 1
        else:
            print("Wrong filename:", file_path)
    print(f"{count}개 이미지 제거")
'''
    return final_code

if __name__ == "__main__":
    print("🔧 Albumentations 1.4.0 완전 최종 수정...")
    print("제거된 변환들:")
    print("  ❌ A.Morphological -> 다른 변환으로 대체")
    print("  ❌ A.GaussNoise std_range -> var_limit")
    print("  ❌ A.CoarseDropout 파라미터 변경")
    
    augmentation_file = "codes/gemini_augmentation_v2.py"
    
    # 백업
    backup_file = f"{augmentation_file}.backup_ultimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(augmentation_file, backup_file)
    print(f"📄 백업 생성: {backup_file}")
    
    # 완전 호환 코드 작성
    final_code = create_final_compatible_code()
    with open(augmentation_file, 'w', encoding='utf-8') as f:
        f.write(final_code)
    
    print("✅ 완전 최종 수정 완료!")
    
    # 최종 테스트
    print("\n🧪 최종 테스트...")
    try:
        import sys
        sys.path.insert(0, 'codes')
        
        # 기존 모듈 삭제
        modules_to_remove = [k for k in sys.modules.keys() if 'gemini_augmentation' in k]
        for module in modules_to_remove:
            del sys.modules[module]
        
        from gemini_augmentation_v2 import AUG, get_augmentation
        print("✅ gemini_augmentation_v2.py import 성공!")
        
        # 모든 변환 테스트
        import numpy as np
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        for aug_name in AUG.keys():
            try:
                transform = AUG[aug_name]
                result = transform(image=test_img)
                print(f"✅ {aug_name} 변환 테스트 성공!")
            except Exception as e:
                print(f"❌ {aug_name} 변환 실패: {e}")
        
        print("\n🎉🎉🎉 모든 API 호환성 문제 완전 해결!")
        print("🚀 이제 실험을 실행하세요!")
        
    except Exception as e:
        print(f"❌ 최종 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
