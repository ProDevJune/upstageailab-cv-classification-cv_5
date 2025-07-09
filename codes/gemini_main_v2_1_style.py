import sys
import os
import yaml
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
import torch.nn.init as init
from torch.utils.data import Dataset, DataLoader, ConcatDataset
from torchvision import transforms
import timm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import wandb
from types import SimpleNamespace
import cv2
import albumentations as A
from albumentations.pytorch import ToTensorV2
from tqdm import tqdm
import copy
import time
from PIL import Image
from zoneinfo import ZoneInfo
from datetime import datetime
import argparse

#📢 크로스 플랫폼 상대 경로 설정
# 현재 파일 위치를 기준으로 프로젝트 루트를 찾기
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_file_dir)  # codes/ 의 상위 디렉토리
sys.path.insert(0, project_root)  # 최우선으로 프로젝트 루트 추가

# 상대 경로로 모듈 import
try:
    from codes.gemini_utils_v2 import *
    from codes.gemini_train_v2 import *
    from codes.gemini_augmentation_v2 import *
    from codes.gemini_evalute_v2 import *
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print(f"현재 디렉토리: {os.getcwd()}")
    print(f"프로젝트 루트: {project_root}")
    print(f"Python 경로: {sys.path[:3]}")
    raise

if __name__ == "__main__":
    run = None
    augmented_ids, val_augmented_ids = [], []
    
    try:
        # python 파일 실행할 때 config.yaml 파일 이름을 입력받아서 설정 파일을 지정한다.
        parser = argparse.ArgumentParser(description="Run deep learning training with specified configuration.")
        parser.add_argument(
            '--config',
            type=str,
            default='config_v2_1.yaml', # 기본값 설정
            help='Name of the configuration YAML file (e.g., config.yaml, experiment_A.yaml)'
        )
        
        args = parser.parse_args()

        # Yaml 파일 읽기 - 상대 경로 처리
        config_path = args.config
        if not os.path.isabs(config_path):
            # 상대 경로인 경우 codes/ 디렉토리 기준으로 결합
            config_path = os.path.join(current_file_dir, config_path)
        
        cfg = load_config(config_path=config_path)
        
        # 작업 디렉토리를 프로젝트 루트로 변경 (상대 경로 정상 작동)
        original_cwd = os.getcwd()
        os.chdir(project_root)
        print(f"📁 작업 디렉토리: {os.getcwd()}")
        # 랜덤성 제어
        set_seed(cfg.random_seed)

        # device 설정
        device = 'cpu'
        if torch.backends.mps.is_available():
            device = torch.device('mps')
        elif torch.cuda.is_available():
            device = torch.device('cuda')
        print("⚙️ Device :",device)
        cfg.device = device
        CURRENT_TIME = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%y%m%d%H%M")
        print(f"⌚ 실험 시간: {CURRENT_TIME}")

        # W&B 설정
        # 증강 기법 문자열 생성 로직 개선
        aug_str_parts = ""
        if cfg.online_augmentation:
            aug_str_parts += "on"
            # Mixup/CutMix 정보 추가
            if hasattr(cfg, 'online_aug'):
                if getattr(cfg.online_aug, 'mixup', False):
                    aug_str_parts += "_mixup"
                elif getattr(cfg.online_aug, 'cutmix', False):
                    aug_str_parts += "_cutmix"
            elif hasattr(cfg, 'augmentation'):
                if getattr(cfg.augmentation, 'mixup', False):
                    aug_str_parts += "_mixup"
                elif getattr(cfg.augmentation, 'cutmix', False):
                    aug_str_parts += "_cutmix"
            
            if hasattr(cfg, 'dynamic_augmentation') and cfg.dynamic_augmentation and cfg.dynamic_augmentation.get('enabled', False):
                aug_str_parts += "daug"                
            else:
                # 일반 augmentation 기법들만 나열
                aug_str_parts += "aug"
        else:
            aug_str_parts += "offaug"

        # 개선된 run name 생성 (더 간결하고 읽기 쉽게)
        next_run_name = (
            f"{CURRENT_TIME}-"
            f"{cfg.model_name.split('.')[0]}-"  # 모델명 간소화
            f"opt{cfg.optimizer_name}-"
            f"sch{cfg.scheduler_name}-"
            f"img{cfg.image_size}-"
            f"es{cfg.patience}-"
            f"{aug_str_parts}-"
            f"bs{cfg.batch_size}-"  # 배치사이즈 추가
            f"vTTA{1 if getattr(cfg, 'val_TTA', False) else 0}-"
            f"tTTA{1 if getattr(cfg, 'test_TTA', False) else 0}-"
            f"MP{1 if cfg.mixed_precision else 0}"
        )
 
        # WanDB 프로젝트명을 model_name 기반으로 설정
        if hasattr(cfg, 'wandb') and cfg.wandb['log']:
            # model_name 기반 프로젝트명 생성
            if getattr(cfg.wandb, 'model_based_project', True):
                model_name_clean = cfg.model_name.replace('.', '-').replace('_', '-')
                project_name = f"{cfg.wandb['project']}-{model_name_clean}"
            else:
                project_name = cfg.wandb['project']
            
            # 태그 설정
            tags = getattr(cfg.wandb, 'tags', [])
            tags.extend([cfg.model_name, cfg.optimizer_name, cfg.scheduler_name, f"img{cfg.image_size}"])
            
            run = wandb.init(
                project=project_name,
                name=next_run_name,
                config=vars(cfg),
                tags=tags
            )

        ### submission 폴더 생성
        # 모델 저장, 시각화 그래프 저장, submission 파일 등등 저장 용도
        submission_dir = os.path.join(cfg.data_dir, 'submissions', next_run_name)
        try:
            os.makedirs(submission_dir, exist_ok=False)
            # cfg에 추가 
            cfg.submission_dir = submission_dir
        except:
            raise ValueError("같은 이름의 submission 폴더가 있습니다.", submission_dir)

        ### Data Load
        if hasattr(cfg, 'train_data'):
            df = pd.read_csv(os.path.join(cfg.data_dir, cfg.train_data))
        else:
            df = pd.read_csv(os.path.join(cfg.data_dir, "train.csv"))
            
        # Train-validation 분할
        train_df, val_df = train_test_split(df, test_size=cfg.val_split_ratio, random_state=cfg.random_seed, stratify=df['target'] if cfg.stratify else None)

        ### Dataset & DataLoader 
        # Augmentation 설정    
        train_transforms, val_transform, val_tta_transform, test_tta_transform = get_augmentation(cfg, epoch=0)

        # train augmentation
        if cfg.online_augmentation:
            train_dataset = ImageDataset(train_df, os.path.join(cfg.data_dir, "train"), transform=train_transforms[0])
        else:
            datasets = [ImageDataset(train_df, os.path.join(cfg.data_dir, "train"), transform=t) for t in train_transforms]
            train_dataset = ConcatDataset(datasets)

        val_dataset = ImageDataset(val_df, os.path.join(cfg.data_dir, "train"), transform=val_transform)

        # 🔥 Mixup/CutMix 지원을 위한 collate_fn 설정
        train_collate = None
        if hasattr(cfg, 'online_aug'):
            alpha = getattr(cfg.online_aug, 'alpha', 0.4)
            num_classes = getattr(cfg, 'num_classes', 17)
            
            if getattr(cfg.online_aug, 'mixup', False):
                print(f"🎯 Mixup 온라인 증강 활성화됨! (alpha={alpha})")
                train_collate = lambda batch: mixup_collate_fn(batch, num_classes=num_classes, alpha=alpha)
            elif getattr(cfg.online_aug, 'cutmix', False):
                print(f"🎯 CutMix 온라인 증강 활성화됨! (alpha={alpha})")
                train_collate = lambda batch: cutmix_collate_fn(batch, num_classes=num_classes, alpha=alpha)
        elif hasattr(cfg, 'augmentation'):
            # 레거시 augmentation 설정 지원
            if getattr(cfg.augmentation, 'mixup', False):
                print("🎯 Mixup 증강 활성화됨! (레거시 모드, alpha=0.4)")
                train_collate = lambda batch: mixup_collate_fn(batch, num_classes=cfg.num_classes, alpha=0.4)
            elif getattr(cfg.augmentation, 'cutmix', False):
                print("🎯 CutMix 증강 활성화됨! (레거시 모드, alpha=0.4)")
                train_collate = lambda batch: cutmix_collate_fn(batch, num_classes=cfg.num_classes, alpha=0.4)
        
        train_loader = DataLoader(
            train_dataset, 
            batch_size=cfg.batch_size, 
            shuffle=True, 
            num_workers=4, 
            pin_memory=True,
            collate_fn=train_collate  # 🔥 Mixup/CutMix 지원
        )
        val_loader = DataLoader(val_dataset, batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)

        # For TTA, we need a loader with raw images
        raw_transform = A.Compose([
            ToTensorV2()
        ])
        val_dataset_raw = ImageDataset(val_df, os.path.join(cfg.data_dir, "train"), transform=raw_transform)
        val_loader_raw = DataLoader(val_dataset_raw, batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)

        ### Define TrainModule
        # Model
        model = get_timm_model(cfg)
        criterion = get_criterion(cfg)
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

        ### Train
        train_result = trainer.training_loop()
        if not train_result:
            raise ValueError("Failed to train model...")

        ### Save Model
        trainer.save_experiments(savepath=os.path.join(cfg.submission_dir, f'{next_run_name}.pth'))
        ## 학습 결과 시각화 저장.
        trainer.plot_loss(
            show=False,
            savewandb=cfg.wandb['log'],
            savedir=cfg.submission_dir
        )

        ### Evaluate
        val_preds, val_f1 = do_validation(
            df=val_df, 
            model=trainer.model, 
            # data=val_dataset_raw if cfg.val_TTA else val_loader, # online validation TTA
            data = val_loader, # offline validation TTA
            transform_func=val_tta_transform, 
            cfg=cfg, 
            run=run, 
            show=False, 
            savepath=os.path.join(cfg.submission_dir, f"val_confusion_matrix{'_TTA' if getattr(cfg, 'val_TTA', False) else ''}.png")
        )
        print("📢 Validation F1-score:",val_f1)

        # Save incorrect validation results
        try:
            save_validation_images(val_df, val_preds, cfg, images_per_row=5, show=False)
        except:
            print("⚠️Saving incorrect validation results Failed...")

        # Inference
        test_df = pd.read_csv(os.path.join(cfg.data_dir, "sample_submission.csv"))

        if getattr(cfg, 'test_TTA', False):
            test_dataset_raw = ImageDataset(test_df, os.path.join(cfg.data_dir, "test"), transform=raw_transform)
            test_loader_raw = DataLoader(test_dataset_raw, batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)
            print("Running TTA on test set...")
            test_preds = tta_predict(trainer.model, test_dataset_raw, test_tta_transform, device, cfg, flag='test')
        else:
            test_dataset = ImageDataset(test_df, os.path.join(cfg.data_dir, "test"), transform=val_transform)
            test_loader = DataLoader(test_dataset, batch_size=cfg.batch_size, shuffle=False, num_workers=4, pin_memory=True)
            print("Running inference on test set...")
            test_preds = predict(trainer.model, test_loader, device)

        pred_df = pd.read_csv(os.path.join(cfg.data_dir, "sample_submission.csv"))
        pred_df['target'] = test_preds

        # Submission
        sample_submission_df = pd.read_csv(os.path.join(cfg.data_dir, "sample_submission.csv"))
        assert (sample_submission_df['ID'] == pred_df['ID']).all(), "pred_df에서 test 이미지가 아닌 데이터가 존재합니다."
        assert set(pred_df['target']).issubset(set(range(cfg.num_classes))), "target 컬럼에 0~16 외의 값이 있습니다."

        submission_path = os.path.join(cfg.submission_dir, f"{next_run_name}.csv")
        pred_df.to_csv(submission_path, index=False)
        print(f"📢Submission file saved to {submission_path}")

        if run:
            # Log submission artifact
            artifact = wandb.Artifact(f'submission-{next_run_name}', type='submission')
            artifact.add_file(submission_path)
            run.log_artifact(artifact)
            run.finish()

    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if 'run' in locals() and run:
            run.finish()
        raise

    finally:
        # 작업 디렉토리 복원
        if 'original_cwd' in locals():
            os.chdir(original_cwd)
            
        if 'run' in locals() and run:
            run.finish()
        if 'augmented_ids' in locals() and augmented_ids:
            ### Offline Augmentation 파일 삭제
            delete_offline_augmented_images(cfg=cfg, augmented_ids=augmented_ids)
        if 'val_augmented_ids' in locals() and val_augmented_ids:
            delete_offline_augmented_images(cfg=cfg, augmented_ids=val_augmented_ids)
