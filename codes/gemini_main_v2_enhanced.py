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
from torch.utils.data import Dataset, DataLoader, ConcatDataset, WeightedRandomSampler
from torchvision import transforms
import timm
from sklearn.model_selection import train_test_split, StratifiedKFold
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
    # run 변수를 전역 스코프에서 초기화
    run = None
    
    try:
        # python 파일 실행할 때 config.yaml 파일 이름을 입력받아서 설정 파일을 지정한다.
        parser = argparse.ArgumentParser(description="Run deep learning training with specified configuration.")
        parser.add_argument(
            '--config',
            type=str,
            default='config_v2.yaml', # 기본값 설정
            help='Name of the configuration YAML file (e.g., config.yaml, experiment_A.yaml)'
        )
        parser.add_argument(
            '--config2', # 2-stage 모델을 위한 config
            type=str,
            default='config_v2_2.yaml', # 기본값 설정
            help='Name of the second configuration YAML file for 2-stage training'
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
            if hasattr(cfg, 'dynamic_augmentation') and cfg.dynamic_augmentation and cfg.dynamic_augmentation.get('enabled', False):
                aug_str_parts += "daug"                
            else:
                # 일반 augmentation 기법들만 나열
                aug_str_parts += "aug"
        else:
            aug_str_parts += "offaug"

        next_run_name = (
            f"{CURRENT_TIME}-"
            f"{cfg.model_name}-"
            f"opt_{cfg.optimizer_name}-"
            f"sch_{cfg.scheduler_name}-"
            f"img{cfg.image_size}-"
            f"es{cfg.patience}-"
            f"{aug_str_parts}-"  # 개선된 증강 문자열
            f"cv{cfg.n_folds}-"
            f"2stage_{1 if getattr(cfg, 'two_stage', False) else 0}-" # 2-stage 모델 사용 여부
            f"clsaug_{1 if getattr(cfg, 'class_imbalance', False) else 0}-"
            f"vTTA_{1 if getattr(cfg, 'val_TTA', False) else 0}-"
            f"tTTA_{1 if getattr(cfg, 'test_TTA', False) else 0}-"
            f"MP_{1 if cfg.mixed_precision else 0}"
        )

        run = None 
        if hasattr(cfg, 'wandb') and cfg.wandb['log']:
            run = wandb.init(
                project=cfg.wandb['project'],
                name=next_run_name,
                config=vars(cfg),
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
            
        # Augmentation 설정
        train_transforms, val_transform, val_tta_transform, test_tta_transform = get_augmentation(cfg, epoch=0)
        val_augmented_ids = []
        
        # Cross validation if n_folds >= 3
        if cfg.n_folds >= 3:            
            folds_es, folds_val_f1 = [], []

            skf = StratifiedKFold(n_splits=cfg.n_folds, shuffle=True, random_state=cfg.random_seed)
            for fold, (train_idx, val_idx) in enumerate(skf.split(df, df['target'])):
                try:
                    train_losses_for_plot, val_losses_for_plot = [], []
                    train_acc_for_plot, val_acc_for_plot = [], []
                    train_f1_for_plot, val_f1_for_plot = [], []

                    print(f"===== FOLD {fold+1} =====")
                    print("="*20)
                    train_df, val_df = df.iloc[train_idx], df.iloc[val_idx]

                    trainer, fold_augmented_ids, fold_val_augmented_ids, val_df, val_loader = run_training_cycle(
                        train_df, val_df, cfg, run=None, train_transforms=train_transforms, val_transform=val_transform
                    ) # cross validation 시에는 wandb에 기록하지 않는다.

                    # save fold results
                    train_losses_for_plot.append(trainer.train_losses_for_plot)
                    train_acc_for_plot.append(trainer.train_acc_for_plot)
                    train_f1_for_plot.append(trainer.train_f1_for_plot)
                    val_losses_for_plot.append(trainer.val_losses_for_plot)
                    val_acc_for_plot.append(trainer.val_acc_for_plot)
                    val_f1_for_plot.append(trainer.val_f1_for_plot)

                    # fold early stopped moment
                    folds_es.append(trainer.es.best_loss_epoch)

                    # evaluate
                    val_preds, val_f1 = do_validation(
                        df=val_df,
                        model=trainer.model,
                        data=val_loader,
                        transform_func=val_tta_transform,
                        cfg=cfg,
                        run=None,
                        show=False,
                        savepath=os.path.join(cfg.submission_dir, f"val_confusion_matrix{'_TTA' if getattr(cfg, 'val_TTA', False) else ''}_Fold{fold}.png")
                    )
                    folds_val_f1.append(val_f1)
                finally:
                    delete_offline_augmented_images(cfg=cfg, augmented_ids=fold_augmented_ids)
                    delete_offline_augmented_images(cfg=cfg, augmented_ids=fold_val_augmented_ids)
                
                print("="*20)
                print("="*20)

            # out of cross-validation
            # 1. plot
            # 2. print average val f1
            # 3. set epoch
            # 4. train whole dataset & make final model
            plot_cross_validation(train_losses_for_plot, val_losses_for_plot, "Loss", cfg, show=False)
            plot_cross_validation(train_acc_for_plot, val_acc_for_plot, "Accuracy", cfg, show=False)
            plot_cross_validation(train_f1_for_plot, val_f1_for_plot, "F1-score", cfg, show=False)
            best_epoch = int(np.mean(folds_es))
            print(f"📢  Avg F1: {np.mean(folds_val_f1):.5f}, Best Epoch: {best_epoch}")
            # 전체 학습.
            trainer, _, _, _, _ = run_training_cycle(
                df, None, cfg, run, train_transforms=train_transforms, val_transform=val_transform
            ) # 전체 train 데이터를 사용해 학습. val_df 없음.
            trainer.save_experiments(savepath=os.path.join(cfg.submission_dir, f'{next_run_name}.pth'))
            

        # No Cross Validation
        else:
            try:
                # Train-validation 분할
                train_df, val_df = train_test_split(df, test_size=cfg.val_split_ratio, random_state=cfg.random_seed, stratify=df['target'] if cfg.stratify else None)
                
                trainer, augmented_ids, val_augmented_ids, val_df, val_loader = run_training_cycle(
                    train_df, val_df, cfg, run, train_transforms=train_transforms, val_transform=val_transform
                )

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
                
            finally:
                delete_offline_augmented_images(cfg=cfg, augmented_ids=augmented_ids)
                delete_offline_augmented_images(cfg=cfg, augmented_ids=val_augmented_ids)

            # Save incorrect validation results
            try:
                save_validation_images(val_df, val_preds, cfg, images_per_row=5, show=False)
            except:
                print("⚠️Saving incorrect validation results Failed...")

        # 2-stage 학습 지원
        if getattr(cfg, 'two_stage', False):
            print("🚀 Starting 2-stage training...")
            
            # Load second config
            config2_path = args.config2
            if not os.path.isabs(config2_path):
                config2_path = os.path.join(current_file_dir, config2_path)
            
            cfg2 = load_config(config_path=config2_path)
            cfg2.device = device
            cfg2.submission_dir = submission_dir
            
            # Use the trained model as starting point for stage 2
            print("📢 Stage 2: Fine-tuning with different configuration...")
            
            # Reload data with new augmentation
            train_transforms2, val_transform2, val_tta_transform2, test_tta_transform2 = get_augmentation(cfg2, epoch=0)
            
            if cfg.n_folds >= 3:
                # For CV, train on full dataset for stage 2
                trainer_stage2, _, _, _, _ = run_training_cycle(
                    df, None, cfg2, run, train_transforms=train_transforms2, val_transform=val_transform2
                )
            else:
                # For single train/val split
                trainer_stage2, augmented_ids2, val_augmented_ids2, val_df2, val_loader2 = run_training_cycle(
                    train_df, val_df, cfg2, run, train_transforms=train_transforms2, val_transform=val_transform2
                )
                delete_offline_augmented_images(cfg=cfg2, augmented_ids=augmented_ids2)
                delete_offline_augmented_images(cfg=cfg2, augmented_ids=val_augmented_ids2)
            
            # Use stage 2 model for final inference
            trainer = trainer_stage2
            test_tta_transform = test_tta_transform2
            val_transform = val_transform2
            cfg = cfg2  # Use stage 2 config for final inference settings

        # Inference
        test_df = pd.read_csv(os.path.join(cfg.data_dir, "sample_submission.csv"))

        if getattr(cfg, 'test_TTA', getattr(cfg, 'TTA', False)):
            # For TTA, we need a loader with raw images
            raw_transform = A.Compose([
                ToTensorV2()
            ])
            test_dataset_raw = ImageDataset(test_df, os.path.join(cfg.data_dir, "test"), transform=raw_transform)
            test_loader_raw = DataLoader(test_dataset_raw, batch_size=cfg.batch_size, shuffle=False, num_workers=8, pin_memory=True)
            print("Running TTA on test set...")
            test_preds = tta_predict(trainer.model, test_dataset_raw, test_tta_transform, device, cfg, flag='test')
        else:
            test_dataset = ImageDataset(test_df, os.path.join(cfg.data_dir, "test"), transform=val_transform)
            test_loader = DataLoader(test_dataset, batch_size=cfg.batch_size, shuffle=False, num_workers=8, pin_memory=True)
            print("Running inference on test set...")
            test_preds = predict(trainer.model, test_loader, device)

        print(pd.Series(test_preds).value_counts())
        pred_df = pd.read_csv(os.path.join(cfg.data_dir, "sample_submission.csv"))
        pred_df['target'] = test_preds

        # Submission
        sample_submission_df = pd.read_csv(os.path.join(cfg.data_dir, "sample_submission.csv"))
        assert (sample_submission_df['ID'] == pred_df['ID']).all(), "pred_df에서 test 이미지가 아닌 데이터가 존재합니다."
        assert set(pred_df['target']).issubset(set(range(17))), "target 컬럼에 0~16 외의 값이 있습니다."

        submission_path = os.path.join(cfg.submission_dir, f"{next_run_name}.csv")
        pred_df.to_csv(submission_path, index=False)
        print(f"📢Submission file saved to {submission_path}")

        ### prediction class별 개수
        try:
            class_counts = pred_df['target'].value_counts().sort_index()
            class_counts = class_counts.reset_index(drop=False)
            meta = pd.read_csv(os.path.join(cfg.data_dir, "meta.csv"))
            meta_dict = zip(meta['target'], meta['class_name'])
            meta_dict = dict(meta_dict)
            targets_class = list(map(lambda x: meta_dict[x], class_counts['target']))
            class_counts['meta'] = targets_class
            class_counts.to_csv(os.path.join(cfg.submission_dir, "submission_class_distribution.csv"), index=False)
        except Exception as e:
            print(e)

        if run:
            # Log submission artifact
            artifact = wandb.Artifact(f'submission-{next_run_name[:60]}...', type='submission')
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
        # augmented_ids가 정의된 경우에만 삭제
        if 'augmented_ids' in locals() and augmented_ids:
            ### Offline Augmentation 파일 삭제
            delete_offline_augmented_images(cfg=cfg, augmented_ids=augmented_ids)
        if 'val_augmented_ids' in locals() and val_augmented_ids:
            delete_offline_augmented_images(cfg=cfg, augmented_ids=val_augmented_ids)
