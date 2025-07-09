#!/bin/bash

# 실행 권한 부여
chmod +x "$0"

# v2_1, v2_2 기능들이 구현된 새로운 시스템 테스트 스크립트

echo "🚀 Enhanced v2 System Test Script"
echo "=================================="

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

echo "📁 Current directory: $(pwd)"

# 1. v2_1 스타일 단순화된 학습 테스트
echo ""
echo "1️⃣ Testing v2_1 Style Training (ConvNeXt + Warmup Scheduler)..."
python codes/gemini_main_v2_1_style.py --config config_v2_1.yaml

# 2. v2_2 스타일 확장된 학습 테스트 (run_training_cycle 사용)
echo ""
echo "2️⃣ Testing v2_2 Style Training (Enhanced with run_training_cycle)..."
python codes/gemini_main_v2_enhanced.py --config config_v2_2.yaml

# 3. Mixup 증강 테스트
echo ""
echo "3️⃣ Testing Mixup Augmentation..."
python codes/gemini_main_v2_enhanced.py --config config_mixup_example.yaml

# 4. CutMix 증강 테스트
echo ""
echo "4️⃣ Testing CutMix Augmentation..."
python codes/gemini_main_v2_enhanced.py --config config_cutmix_example.yaml

# 5. 2-stage 학습 테스트
echo ""
echo "5️⃣ Testing 2-stage Training..."
python codes/gemini_main_v2_enhanced.py --config config_2stage_1.yaml --config2 config_2stage_2.yaml

echo ""
echo "✅ All tests completed!"
echo "Check the data/submissions/ folder for results."