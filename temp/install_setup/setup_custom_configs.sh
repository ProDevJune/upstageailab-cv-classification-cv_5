#!/bin/bash

# Custom Config Runner 초기 설정 스크립트

echo "🎯 Setting up Custom Config Sequential Runner"
echo "============================================="

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# 실행 권한 부여
chmod +x custom_config_runner.py
chmod +x run_my_configs.sh

# 샘플 config 파일들 생성
echo "📝 Creating sample config files..."
python custom_config_runner.py --create-samples

# 실행 순서 템플릿 생성
echo "📋 Creating execution order template..."
python custom_config_runner.py --create-order

echo ""
echo "✅ Custom Config Sequential Runner is ready!"
echo ""
echo "📁 Directory structure:"
echo "  my_configs/"
echo "  ├── sample_v2_1_convnext.yaml"
echo "  ├── sample_v2_2_resnet_mixup.yaml"
echo "  ├── sample_v2_2_efficient_2stage.yaml"
echo "  ├── sample_v2_2_efficient_2stage_stage2.yaml"
echo "  ├── execution_order.txt"
echo "  ├── logs/"
echo "  └── results/"
echo ""
echo "🎯 Quick Start:"
echo "  1. Edit config files: vi my_configs/sample_*.yaml"
echo "  2. Run experiments: ./run_my_configs.sh"
echo "  3. Check results: cat my_configs/results/experiment_results.json"
echo ""
echo "📚 Full guide: CUSTOM_CONFIG_GUIDE.md"
echo ""
echo "🚀 Ready to run YOUR custom experiments!"
