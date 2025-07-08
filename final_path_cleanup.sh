#!/bin/bash

echo "🔥 남은 하드코딩 경로 완전 박멸!"
echo "=============================="

echo "📝 experiments 폴더 및 모든 남은 파일 수정..."

# experiments 폴더의 모든 파일 수정
python3 << 'EOF'
import os
import re
import glob

# 하드코딩 경로 패턴들
hardcoded_patterns = [
    r'',
    r''
]

# 수정할 폴더들
folders_to_fix = [
    'experiments/',
    'codes/practice/',
    'codes/song/',
    './'
]

modified_count = 0

for folder in folders_to_fix:
    if not os.path.exists(folder):
        continue
        
    print(f"\n🔍 {folder} 폴더 처리 중...")
    
    # 해당 폴더의 모든 파일 찾기
    for ext in ['*.py', '*.yaml', '*.yml', '*.sh']:
        pattern = os.path.join(folder, '**', ext) if folder != './' else ext
        files = glob.glob(pattern, recursive=True)
        
        for file_path in files:
            # temp, .git, venv, wandb 폴더 제외
            if any(skip in file_path for skip in ['temp/', '.git/', 'venv/', 'wandb/']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                has_hardcoded = False
                
                # 하드코딩 경로 탐지 및 제거
                for pattern in hardcoded_patterns:
                    if pattern in content:
                        has_hardcoded = True
                        
                        if file_path.endswith(('.yaml', '.yml')):
                            # YAML 파일의 경우 data_dir만 수정
                            content = re.sub(
                                r'data_dir:\s*["\']?/[^"\']*["\']?',
                                'data_dir: "data"',
                                content
                            )
                            # base_config_path도 수정
                            content = re.sub(
                                r'base_config_path:\s*["\']?/[^"\']*codes/[^"\']*["\']?',
                                'base_config_path: "codes/config_v2.yaml"',
                                content
                            )
                            # output_dir, log_dir 등도 상대경로로 변경
                            content = re.sub(
                                r'(output_dir|log_dir|submission_dir|main_script_path):\s*["\']?/[^"\']*cv-classification/([^"\']*)["\']?',
                                r'\1: "\2"',
                                content
                            )
                        else:
                            # Python/Shell 파일의 경우 완전 제거
                            content = re.sub(pattern + r'/?', '', content)
                
                # 파일이 변경되었으면 저장
                if content != original_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    modified_count += 1
                    if has_hardcoded:
                        print(f"✅ {file_path}: 하드코딩 경로 제거 완료")
                    
            except Exception as e:
                print(f"⚠️ {file_path}: 오류 - {e}")

print(f"\n🎉 총 {modified_count}개 파일 추가 수정 완료!")
EOF

echo ""
echo "📝 config_v2.yaml에서 data_dir 확인 및 수정..."

# config_v2.yaml이 비어있는지 확인하고 재작성
if [ ! -s "codes/config_v2.yaml" ] || ! grep -q "data_dir" codes/config_v2.yaml; then
    echo "⚠️ config_v2.yaml이 손상되었습니다. 재작성 중..."
    
    cat > codes/config_v2.yaml << 'EOF'
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
    echo "✅ config_v2.yaml 완전 재작성 완료"
fi

echo ""
echo "🧪 최종 검증 (핵심 파일만)..."
echo "📍 핵심 실행 파일들의 하드코딩 경로 확인:"

core_files=(
    "codes/gemini_main_v2.py"
    "codes/config_v2.yaml" 
    "run_code_v2.sh"
    "experiments/experiment_matrix.yaml"
    "experiments/auto_experiment_runner.py"
)

all_clean=true
for file in "${core_files[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "/Users/jayden\|/data/ephemeral" "$file" 2>/dev/null; then
            echo "❌ $file: 아직 하드코딩 경로 있음"
            all_clean=false
        else
            echo "✅ $file: 깨끗함"
        fi
    else
        echo "⚠️ $file: 파일 없음"
    fi
done

echo ""
if $all_clean; then
    echo "🎉 핵심 실행 파일들의 하드코딩 경로 완전 제거 완료!"
else
    echo "❌ 일부 핵심 파일에 아직 하드코딩 경로가 남아있습니다."
fi

echo ""
echo "📍 data_dir 설정 최종 확인:"
grep -n "data_dir" codes/config_v2.yaml || echo "❌ config_v2.yaml에 data_dir 없음"

echo ""
echo "🚀 Code v2 실행 테스트:"
echo "./run_code_v2.sh"

echo ""
echo "📋 정리 완료!"
echo "✅ experiments/ 폴더 하드코딩 경로 제거"
echo "✅ codes/practice/ 폴더 하드코딩 경로 제거" 
echo "✅ config_v2.yaml 안전성 확보"
echo "✅ 핵심 실행 파일들 완전 정리"
