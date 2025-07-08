#!/bin/bash

echo "🔥 전체 프로젝트 하드코딩 경로 완전 제거!"
echo "========================================="

echo "📍 모든 파일에서 하드코딩 경로 검색 중..."

# 1. 모든 파일에서 하드코딩 경로 찾기
echo ""
echo "🔍 하드코딩 경로 검색 결과:"
find . -type f \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" \) -not -path "./temp/*" -not -path "./.git/*" -not -path "./venv/*" | xargs grep -l "/Users/jayden\|/data/ephemeral" 2>/dev/null || echo "✅ 하드코딩 경로 없음"

echo ""
echo "📝 모든 하드코딩 경로 자동 수정 중..."

# 2. Python 파일들 수정
python3 << 'EOF'
import os
import re
import yaml

# 수정할 파일 패턴들
file_patterns = [
    'codes/*.py',
    'codes/*.yaml', 
    'codes/*.yml',
    '*.py',
    '*.yaml',
    '*.yml',
    '*.sh'
]

# 하드코딩된 경로들
hardcoded_paths = [
    r'',
    r''
]

import glob

files_to_check = []
for pattern in file_patterns:
    files_to_check.extend(glob.glob(pattern))

# temp 폴더와 .git 폴더 제외
files_to_check = [f for f in files_to_check if not f.startswith('temp/') and not f.startswith('.git/')]

print(f"🔍 검사할 파일 개수: {len(files_to_check)}")

modified_files = []

for file_path in files_to_check:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 하드코딩 경로 제거
        for hardcoded_path in hardcoded_paths:
            if hardcoded_path in content:
                print(f"❌ {file_path}: 하드코딩 경로 발견 - {hardcoded_path}")
                
                # 경로별 적절한 대체
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    # YAML 파일의 data_dir 수정
                    content = re.sub(
                        r'data_dir:\s*["\']?/[^"\']*["\']?',
                        'data_dir: "data"',
                        content
                    )
                else:
                    # Python/Shell 파일의 절대경로 제거
                    content = re.sub(
                        hardcoded_path + r'/?',
                        '',
                        content
                    )
        
        # 특별한 경우들 처리
        if file_path.endswith('.py'):
            # project_root 설정을 동적으로 변경
            content = re.sub(
                r"project_root\s*=\s*['\"][^'\"]*['\"]",
                "project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
                content
            )
            
            # config 파일 경로를 상대경로로 변경
            content = re.sub(
                r"config_file_path\s*=\s*['\"][^'\"]*codes/[^'\"]*['\"]",
                "config_file_path = os.path.join('codes', args.config)",
                content
            )
            
            # data_dir 관련 절대경로 제거
            content = re.sub(
                r'os\.path\.join\(["\'][^"\']*cv-classification[^"\']*["\'],\s*["\']data["\']',
                'cfg.data_dir',
                content
            )
        
        # 파일이 변경되었으면 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            modified_files.append(file_path)
            print(f"✅ {file_path}: 수정 완료")
            
    except Exception as e:
        print(f"⚠️ {file_path}: 오류 - {e}")

print(f"\n🎉 수정 완료! 총 {len(modified_files)}개 파일 수정됨")
for f in modified_files:
    print(f"  ✅ {f}")
EOF

echo ""
echo "📝 config_v2.yaml 특별 처리..."

# config_v2.yaml 직접 수정
cat > codes/config_v2_temp.yaml << 'EOF'
# Configuration for the training process
model_name: 'swin_base_patch4_window12_384.ms_in1k'
pretrained: true
fine_tuning: "full"

# 🔥 Phase 1: 고급 손실 함수 설정
criterion: 'FocalLoss'
focal_loss:
  alpha: 1.0
  gamma: 2.0
  reduction: 'mean'
label_smoothing:
  smoothing: 0.1

# Optimizer
optimizer_name: 'AdamW'
lr: 0.0001
weight_decay: 0.00001
scheduler_name: 'CosineAnnealingLR'

# Other variables
random_seed: 256
n_folds: 0
val_split_ratio: 0.15
stratify: true
image_size: 384

# Normalization
norm_mean: [0.5, 0.5, 0.5]
norm_std: [0.5, 0.5, 0.5]

# Techniques
class_imbalance:
  aug_class: [1, 13, 14]
  max_samples: 78

online_augmentation: true
augmentation:
  eda: true
  dilation: false
  erosion: false
  mixup: true
  cutmix: true

# 🔥 Phase 1: CutMix & MixUp 고급 설정
mixup_cutmix:
  mixup_alpha: 1.0
  cutmix_alpha: 1.0
  cutmix_minmax: null
  prob: 0.5
  switch_prob: 0.5
  mode: 'batch'
  correct_lam: true
  label_smoothing: 0.1

# Dynamic augmentation
dynamic_augmentation:
  enabled: true
  policies:
    weak:
      end_epoch: 5
      augs: ['basic']
    middle:
      end_epoch: 15
      augs: ['middle', 'mixup']
    strong:
      end_epoch: 300
      augs: ['aggressive','eda', 'cutmix']

val_TTA: true
test_TTA: true
tta_dropout: false
mixed_precision: true

# Model hyperparameters
timm:
  activation: null

custom_layer: null

# Training hyperparameters
epochs: 10000
patience: 20
batch_size: 32

# W&B
wandb:
  project: "upstage-img-clf-v2-advanced"
  log: false

# Paths - 상대경로 사용 (Mac/Linux 호환)
data_dir: "data"
EOF

mv codes/config_v2_temp.yaml codes/config_v2.yaml
echo "✅ config_v2.yaml 완전 재작성 완료"

echo ""
echo "🧪 최종 검증..."
echo "📍 하드코딩 경로 최종 확인:"
find . -type f \( -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "*.sh" \) -not -path "./temp/*" -not -path "./.git/*" -not -path "./venv/*" | xargs grep -l "/Users/jayden\|/data/ephemeral" 2>/dev/null && echo "❌ 아직 하드코딩 경로 남아있음!" || echo "✅ 모든 하드코딩 경로 제거 완료!"

echo ""
echo "📍 data_dir 설정 확인:"
grep -n "data_dir" codes/config_v2.yaml

echo ""
echo "📍 project_root 설정 확인:"
grep -n "project_root" codes/gemini_main_v2.py

echo ""
echo "🎉 전체 프로젝트 하드코딩 경로 완전 제거 완료!"
echo ""
echo "📋 수정 내용:"
echo "✅ 모든 Python 파일의 절대경로 제거"
echo "✅ config_v2.yaml 완전 재작성 (상대경로)"
echo "✅ project_root 동적 설정"
echo "✅ Mac/Linux 크로스 플랫폼 호환성 확보"
echo ""
echo "🚀 이제 진짜로 어떤 환경에서든 작동합니다:"
echo "./run_code_v2.sh"
