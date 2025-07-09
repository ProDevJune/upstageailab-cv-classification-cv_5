#!/bin/bash

# Enhanced v2 시스템 파일 권한 설정 스크립트

echo "🔧 Setting up file permissions for Enhanced v2 System..."

# 프로젝트 루트로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

# Python 파일들 실행 권한 부여
chmod +x codes/gemini_main_v2_enhanced.py
chmod +x codes/gemini_main_v2_1_style.py
chmod +x codes/gemini_main_v2.py

# Shell 스크립트들 실행 권한 부여
chmod +x test_enhanced_v2.sh
chmod +x *.sh

# Config 파일들 읽기 권한 확인
chmod 644 codes/config_*.yaml

echo "✅ File permissions set successfully!"
echo ""
echo "📋 Available commands:"
echo "  1. v2_1 style: python codes/gemini_main_v2_1_style.py --config config_v2_1.yaml"
echo "  2. v2_2 style: python codes/gemini_main_v2_enhanced.py --config config_v2_2.yaml"  
echo "  3. Mixup test: python codes/gemini_main_v2_enhanced.py --config config_mixup_example.yaml"
echo "  4. CutMix test: python codes/gemini_main_v2_enhanced.py --config config_cutmix_example.yaml"
echo "  5. 2-stage: python codes/gemini_main_v2_enhanced.py --config config_2stage_1.yaml --config2 config_2stage_2.yaml"
echo "  6. Full test: ./test_enhanced_v2.sh"
echo ""
echo "🎯 All v2_1 and v2_2 features are now fully implemented!"