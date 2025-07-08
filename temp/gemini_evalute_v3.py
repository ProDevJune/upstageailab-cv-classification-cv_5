import os
from tqdm import tqdm
import torch
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, confusion_matrix
import wandb
import albumentations as A
import matplotlib.image as mpimg

def _clear_device_cache(device):
    """플랫폼별 GPU/MPS 캐시 비우기 헬퍼 함수"""
    device_str = str(device)
    if device_str.startswith('cuda'):
        torch.cuda.empty_cache()
    elif device_str.startswith('mps'):
        # MPS는 PyTorch 2.0+에서 torch.mps.empty_cache() 지원
        try:
            torch.mps.empty_cache()
        except AttributeError:
            # torch.mps.empty_cache()가 없는 경우 (이전 버전)
            pass
    # CPU는 캐시 비울 필요 없음

def tta_predict(model, dataset, tta_transform, device, cfg, flag='val'):
    if cfg.tta_dropout:
        model.train()
    else:
        model.eval()
    predictions = []
    with torch.no_grad():
        if flag=='val':
            for image, _ in tqdm(dataset, desc="validation TTA Prediction"): # load batch
                # read raw images from dataset_raw
                tta_preds = []
                image = image.clamp(0, 255).to(torch.uint8) 
                image = image.permute(1, 2, 0).cpu().numpy() # H,W,C 로 변형
                for _ in range(5): # 5 TTA iterations
                    augmented_image = tta_transform(image=image)['image']
                    augmented_image = augmented_image.to(device)
                    augmented_image = augmented_image.unsqueeze(0) # batch, H,W,C 로 변형
                    outputs = model(augmented_image) # inference
                    tta_preds.append(outputs.softmax(1).cpu().numpy()) # append inference result
                avg_preds = np.mean(tta_preds, axis=0) # 5 TTA 예측 결과 확률값을 평균 낸다.
                predictions.extend(avg_preds.argmax(1))
        else: # inference time transform
            for image, _ in tqdm(dataset, desc="test TTA Prediction"): # load batch
                tta_preds = []
                image = image.clamp(0, 255).to(torch.uint8) 
                image = image.permute(1, 2, 0).cpu().numpy() # H,W,C 로 변형
                augs = []
                a1 = A.Compose([A.Compose(A.HorizontalFlip(p=1.0)),tta_transform]) # 수평 반전
                augs.append(a1)
                a2 = A.Compose([A.Compose(A.VerticalFlip(p=1.0)),tta_transform]) # 수직 반전
                augs.append(a2)
                a3 = A.Compose([A.Compose(A.Transpose(p=1.0)),tta_transform]) # 대칭
                augs.append(a3)
                a4 = A.Compose([A.Compose(A.Rotate(limit=(-10, 10), p=1.0)),tta_transform]) # 미세한 회전 변환
                augs.append(a4)
                augs.append(tta_transform) # 증강 안 하는 버전
                for transform_func in augs:
                    augmented_image = transform_func(image=image)['image']
                    augmented_image = augmented_image.to(device)
                    augmented_image = augmented_image.unsqueeze(0) # batch, H,W,C 로 변형
                    outputs = model(augmented_image) # inference
                    tta_preds.append(outputs.softmax(1).cpu().numpy()) # append inference result
                    del augmented_image
                    # 🔧 플랫폼별 메모리 캐시 비우기
                    _clear_device_cache(device)
                avg_preds = np.mean(tta_preds, axis=0) # 5 TTA 예측 결과 확률값을 평균 낸다.
                predictions.extend(avg_preds.argmax(1))
    return predictions

def predict(model, loader, device):
    model.eval()
    predictions = []
    with torch.no_grad():
        for images, _ in tqdm(loader, desc="Prediction"):
            images = images.to(device)
            outputs = model(images)
            predictions.extend(outputs.argmax(1).cpu().numpy())
    return predictions

def do_validation(df, model, data, transform_func, cfg, run=None, show=False, savepath=None):
    if cfg.val_TTA:
        print("Running TTA on validation set...")
        # offline 증강을 수행했을 때는 tta_predict() 호출할 필요가 없다.
        # val_preds = tta_predict(model, data, transform_func, cfg.device, flag='val')
        # offline TTA 증강 시에는 predict 호출
        val_preds = predict(model, data, cfg.device)
    else:
        print("Running Normal Validation...")
        val_preds = predict(model, data, cfg.device)
    val_targets = df['target'].values
    val_f1 = f1_score(val_targets, val_preds, average='macro')
    # 메타데이터 로드
    meta = pd.read_csv(os.path.join(cfg.data_dir, 'meta.csv'))
    meta_dict = zip(meta['target'], meta['class_name'])
    meta_dict = dict(meta_dict)
    # meta_dict[-1] = "None"
    val_targets_class = list(map(lambda x: meta_dict[x], val_targets))
    val_preds_class = list(map(lambda x: meta_dict[x], val_preds))
    all_classes = sorted(list(set(val_targets_class + val_preds_class)))
    cm = confusion_matrix(val_targets_class, val_preds_class, labels=all_classes)
    plt.figure(figsize=(10, 8), dpi=100)
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=all_classes, yticklabels=all_classes)
    plt.title(f"Validation Confusion Matrix - F1: {val_f1:.4f}")
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    if run:
        run.log({"tta_val_confusion_matrix": wandb.Image(plt)})
    if savepath is not None:
        plt.savefig(savepath)
    if show:
        plt.show()
    else:
        plt.clf()
    return val_preds, val_f1

def save_validation_images(val_df, val_preds, cfg, images_per_row=5, show=False):
    # 1. 예측값과 실제값을 포함하는 새로운 DataFrame 생성
    # val_df의 'ID'와 'target'을 그대로 사용하고, 'predicted_target' 컬럼 추가
    results_df = val_df[['ID', 'target']].copy()
    results_df['predicted_target'] = val_preds
    # 2. 예측이 틀린 데이터 필터링
    # 'target' 컬럼과 'predicted_target' 컬럼이 다른 경우를 찾습니다.
    misclassified_df = results_df[results_df['target'] != results_df['predicted_target']].copy()
    if misclassified_df.empty:
        print("No misclassified images to visualize.")
        return None

    # 3. 가독성을 위해 클래스 이름 추가 (선택 사항)
    # 실제 클래스 이름과 예측된 클래스 이름을 매핑하여 컬럼 추가
    # 메타데이터 로드
    meta = pd.read_csv(os.path.join(cfg.data_dir, 'meta.csv'))
    meta_dict = zip(meta['target'], meta['class_name'])
    meta_dict = dict(meta_dict)
    misclassified_df['actual_class_name'] = misclassified_df['target'].map(meta_dict)
    misclassified_df['predicted_class_name'] = misclassified_df['predicted_target'].map(meta_dict)

    # 시각화 및 결과 저장.
    # 1. target으로 오름차순 정렬
    misclassified_df = misclassified_df.sort_values(by='target', ascending=True)

    # 2. 시각화
    num_images = len(misclassified_df)
    num_rows = (num_images + images_per_row - 1) // images_per_row # 올림 계산
    
    plt.figure(figsize=(6 * images_per_row, 6 * num_rows), dpi=200) # 각 이미지 당 3x3 인치 할당

    for i, row in tqdm(enumerate(misclassified_df.itertuples()), desc="Visualizing Wrong Validation Results..."):
        # 이미지 파일 경로 구성
        # 만약 이미지가 data_dir/images/ 에 있다면, os.path.join(data_dir, 'images', row.ID)
        image_path = os.path.join(cfg.data_dir, 'train', row.ID)

        if not os.path.exists(image_path):
            print(f"Warning: Image file not found at {image_path}. Skipping.")
            continue

        try:
            img = mpimg.imread(image_path)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}. Skipping.")
            continue

        ax = plt.subplot(num_rows, images_per_row, i + 1)
        ax.imshow(img)

        # 타이틀 설정: A-{actual_class_name}_P-{predicted_class_name}
        title = f"ID-{row.ID}\nA-{row.actual_class_name}\nP-{row.predicted_class_name}"
        ax.set_title(title, fontsize=10) # 폰트 크기 조정

        ax.axis('off') # 축 정보 숨기기

    plt.tight_layout() # 서브플롯 간격 자동 조절
    plt.suptitle("Misclassified Images", fontsize=16, y=1.02) # 전체 제목
    if os.path.exists(cfg.submission_dir):
        val_wrong_img_dir = os.path.join(cfg.submission_dir, 'val_img')
        os.makedirs(val_wrong_img_dir, exist_ok=True)
        plt.savefig(os.path.join(val_wrong_img_dir,"validation_wrong_images.png"))
    if show:
        plt.show()
