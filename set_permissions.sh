#!/bin/bash

# 🔧 실행 스크립트 권한 설정
echo "🔑 Setting executable permissions for run scripts..."

chmod +x run_code_v1.sh
chmod +x run_code_v2.sh
chmod +x install_aistages.sh
chmod +x run_aistages_v2.sh
chmod +x ubuntu_setup.sh

echo "✅ Permissions set successfully!"
echo ""
echo "📋 사용 가능한 실행 스크립트:"
echo "  🔸 ./run_code_v1.sh  - 기존 시스템 (resnet50)"
echo "  🔸 ./run_code_v2.sh  - 새 시스템 (swin_base)"
