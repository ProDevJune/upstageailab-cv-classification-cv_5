#!/bin/bash
# AIStages Server v2 System Execution Script (English Version)

echo "🚀 AIStages Server - Code v2 System"
echo "================================"
echo "📂 Data: train.csv v1 (original data with best performance)"
echo "💻 Code: gemini_main_v2.py (swin_base based)"
echo "⚙️ Config: config_v2.yaml"
echo "🆕 Features: Enhanced augmentation, dynamic augmentation, improved model"
echo ""

# Virtual Environment Check
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual Environment: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️  Please activate virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# GPU Check
if command -v nvidia-smi &> /dev/null; then
    echo "✅ GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
else
    echo "⚠️  Cannot detect GPU."
fi

echo ""
echo "🎯 Running v2 system..."

# Execute v2 system (explicit python3)
python3 codes/gemini_main_v2.py --config codes/config_v2.yaml

echo ""
echo "✅ v2 system execution completed!"
echo ""
echo "📊 Check results:"
echo "  • Experiment results: tail experiment_results.csv"
echo "  • Submission files: ls -la data/submissions/"
echo "  • Model files: ls -la models/"
