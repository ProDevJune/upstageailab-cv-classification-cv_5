#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# ML 프로젝트 호환성 체크 스크립트
echo "🤖 ML 프로젝트 호환성 체크"
echo "========================="
echo "⏰ 체크 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. GPU 메모리 상세 체크
echo "🎮 1. GPU 메모리 상세 분석"
echo "-------------------------"
if command -v nvidia-smi &> /dev/null; then
    echo "GPU 메모리 현황:"
    nvidia-smi --query-gpu=index,name,memory.total,memory.free,memory.used --format=csv
    echo ""
    
    echo "프로젝트 모델별 예상 메모리 요구사항:"
    echo "  📊 ConvNeXt-V2 Base (batch=32): ~8-10GB"
    echo "  📊 ConvNeXt-V2 Large (batch=16): ~16-20GB" 
    echo "  📊 EfficientNet-V2 L (batch=8): ~20-24GB"
    echo "  📊 ResNet50 (batch=64): ~6-8GB"
    echo "  📊 V3 계층적 (2모델): ~12-16GB"
    echo ""
else
    echo "❌ GPU 정보를 확인할 수 없습니다."
    echo ""
fi

# 2. 배치 크기 추천
echo "📦 2. 권장 배치 크기 계산"
echo "------------------------"
python -c "
import torch
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        total_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f'GPU {i} ({torch.cuda.get_device_name(i)}):')
        print(f'  총 메모리: {total_memory:.1f} GB')
        
        # 배치 크기 추천
        if total_memory >= 24:
            print('  권장: ConvNeXt-V2 Large (batch 16-24), EfficientNet-V2 L (batch 8-12)')
        elif total_memory >= 16:
            print('  권장: ConvNeXt-V2 Base (batch 32-48), V3 계층적 시스템')
        elif total_memory >= 12:
            print('  권장: ResNet50 (batch 64), EfficientNet-B4 (batch 48)')
        elif total_memory >= 8:
            print('  권장: ResNet50 (batch 32), V2_2 시스템')
        else:
            print('  권장: 작은 모델만 사용, 배치 크기 16 이하')
        print()
else:
    print('CUDA를 사용할 수 없습니다.')
" 2>/dev/null || echo "GPU 분석 실패"

# 3. 프로젝트 의존성 체크
echo "📋 3. 프로젝트 의존성 상세 체크"
echo "------------------------------"
python -c "
import sys
print(f'Python 버전: {sys.version}')

# 필수 라이브러리 버전 체크
required_libs = {
    'torch': '>=1.12.0',
    'torchvision': '>=0.13.0', 
    'timm': '>=0.6.0',
    'albumentations': '>=1.0.0',
    'opencv-python': '>=4.5.0',
    'pandas': '>=1.3.0',
    'numpy': '>=1.21.0',
    'scikit-learn': '>=1.0.0',
    'matplotlib': '>=3.5.0',
    'seaborn': '>=0.11.0',
    'wandb': 'any',
    'tqdm': 'any',
    'pyyaml': 'any'
}

print('\\n필수 라이브러리 설치 상태:')
missing_libs = []
for lib, min_version in required_libs.items():
    try:
        if lib == 'opencv-python':
            import cv2 as module
            lib_name = 'cv2'
        else:
            module = __import__(lib)
            lib_name = lib
            
        version = getattr(module, '__version__', 'Unknown')
        print(f'  ✅ {lib_name}: {version}')
    except ImportError:
        print(f'  ❌ {lib}: Not installed')
        missing_libs.append(lib)

if missing_libs:
    print(f'\\n❌ 누락된 라이브러리: {missing_libs}')
    print('설치 명령어:')
    print(f'pip install {\" \".join(missing_libs)}')
else:
    print('\\n✅ 모든 필수 라이브러리가 설치되어 있습니다!')
" 2>/dev/null || echo "의존성 체크 실패"
echo ""

# 4. 데이터 경로 체크
echo "📁 4. 데이터 경로 및 권한 체크"
echo "-----------------------------"
echo "현재 디렉토리 구조:"
ls -la | head -10
echo ""

echo "용량 체크:"
echo "  현재 디렉토리: $(du -sh . 2>/dev/null | cut -f1)"
echo "  사용 가능 공간: $(df -h . | tail -1 | awk '{print $4}')"
echo ""

echo "권한 체크:"
if [ -w . ]; then
    echo "  ✅ 현재 디렉토리 쓰기 권한 있음"
else
    echo "  ❌ 현재 디렉토리 쓰기 권한 없음"
fi

# 5. 프로젝트별 시스템 요구사항 체크
echo "🎯 5. 프로젝트 시스템별 호환성"
echo "-----------------------------"
python -c "
import torch

if torch.cuda.is_available():
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    gpu_count = torch.cuda.device_count()
    
    print('시스템별 실행 가능성:')
    print(f'현재 GPU 메모리: {gpu_memory:.1f} GB, GPU 개수: {gpu_count}')
    print()
    
    # V2_1 시스템
    if gpu_memory >= 16:
        print('✅ V2_1 시스템: 실행 가능')
        print('   - ConvNeXt-V2 Base/Large 모델 지원')
        print('   - 권장 배치 크기: 16-32')
    else:
        print('⚠️  V2_1 시스템: 제한적 실행')
        print('   - 작은 모델만 가능')
        print('   - 배치 크기 축소 필요')
    print()
    
    # V2_2 시스템  
    if gpu_memory >= 8:
        print('✅ V2_2 시스템: 실행 가능')
        print('   - ResNet50, EfficientNet-B4 지원')
        print('   - 모든 기법 조합 가능')
    else:
        print('⚠️  V2_2 시스템: 배치 크기 조정 필요')
    print()
    
    # V3 시스템
    if gpu_memory >= 12:
        print('✅ V3 계층적 시스템: 실행 가능')
        print('   - 2모델 동시 실행 지원')
        print('   - 계층적 분류 전략 활용 가능')
    else:
        print('⚠️  V3 계층적 시스템: 순차 실행 권장')
        print('   - 모델 A, B 따로 학습 후 추론')
    print()
    
    # 전체 실험 자동화
    if gpu_memory >= 16 and gpu_count >= 1:
        print('🚀 전체 자동화 실험: 완전 지원')
        print('   - 모든 시스템 동시 실행 가능')
        print('   - Phase별 대규모 실험 가능')
    elif gpu_memory >= 8:
        print('⚡ 선택적 자동화: 시스템별 순차 실행')
        print('   - V2_2 우선 추천')
        print('   - 배치 크기 조정 필요')
    else:
        print('⚠️  제한적 실행: 수동 설정 필요')
        print('   - 작은 모델 위주')
        print('   - 배치 크기 16 이하')
        
else:
    print('❌ CUDA 사용 불가 - CPU 모드로 실행')
    print('   - 실험 시간 대폭 증가 예상')
    print('   - 작은 모델 및 배치 크기 권장')
" 2>/dev/null || echo "호환성 체크 실패"
echo ""

# 6. 성능 벤치마크
echo "⚡ 6. 간단한 성능 벤치마크"
echo "-------------------------"
python -c "
import torch
import time

if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f'GPU 벤치마크 시작 ({torch.cuda.get_device_name(0)})')
    
    # 간단한 행렬 연산 벤치마크
    sizes = [1000, 2000, 4000]
    for size in sizes:
        x = torch.randn(size, size, device=device)
        y = torch.randn(size, size, device=device)
        
        start_time = time.time()
        for _ in range(10):
            z = torch.mm(x, y)
        torch.cuda.synchronize()
        end_time = time.time()
        
        duration = (end_time - start_time) / 10
        gflops = (2 * size**3) / (duration * 1e9)
        print(f'  {size}x{size} 행렬곱: {duration:.3f}초, {gflops:.1f} GFLOPS')
    
    # 메모리 할당 테스트
    print('\\nGPU 메모리 할당 테스트:')
    try:
        test_tensor = torch.randn(10000, 10000, device=device)
        memory_used = torch.cuda.memory_allocated() / 1024**3
        print(f'  대용량 텐서 할당 성공: {memory_used:.2f} GB 사용중')
        del test_tensor
        torch.cuda.empty_cache()
    except RuntimeError as e:
        print(f'  메모리 할당 실패: {e}')
        
else:
    print('CPU 벤치마크')
    import numpy as np
    x = np.random.randn(1000, 1000)
    y = np.random.randn(1000, 1000)
    
    start_time = time.time()
    for _ in range(10):
        z = np.dot(x, y)
    end_time = time.time()
    
    duration = (end_time - start_time) / 10
    print(f'  1000x1000 행렬곱: {duration:.3f}초')
    print('  ⚠️  GPU 권장: 학습 시간이 매우 오래 걸릴 수 있습니다.')
" 2>/dev/null || echo "벤치마크 실행 실패"
echo ""

# 7. 추천 설정
echo "💡 7. AIStages 환경 최적화 추천"
echo "-------------------------------"
python -c "
import torch

if torch.cuda.is_available():
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    print('🎯 추천 실행 전략:')
    print()
    
    if gpu_memory >= 20:
        print('💎 Premium GPU 환경:')
        print('  1. V2_1 시스템부터 시작 (최고 성능)')
        print('  2. ConvNeXt-V2 Large 모델 실험')
        print('  3. 배치 크기 16-24 사용')
        print('  4. 전체 자동화 실험 가능')
    elif gpu_memory >= 12:
        print('🥇 고급 GPU 환경:')
        print('  1. V3 계층적 시스템 추천 (혁신적)')
        print('  2. V2_2 시스템 병행 (효율적)')
        print('  3. ConvNeXt-V2 Base + EfficientNet-B4')
        print('  4. 배치 크기 32-48 사용')
    elif gpu_memory >= 8:
        print('🥈 표준 GPU 환경:')
        print('  1. V2_2 시스템 우선 추천')
        print('  2. ResNet50 + EfficientNet-B4')
        print('  3. 배치 크기 32-64 사용')
        print('  4. 기법별 순차 실험')
    else:
        print('🥉 제한적 GPU 환경:')
        print('  1. 작은 모델 위주 (ResNet50)')
        print('  2. 배치 크기 16 이하')
        print('  3. 단일 모델 순차 실험')
        print('  4. Mixed Precision 필수 사용')
    
    print()
    print('🔧 공통 최적화 설정:')
    print('  - mixed_precision: True')
    print('  - num_workers: 4-8')
    print('  - pin_memory: True')
    print('  - 정기적인 torch.cuda.empty_cache()')
    
else:
    print('💻 CPU 전용 환경:')
    print('  - 매우 작은 모델만 사용')
    print('  - 배치 크기 4-8')
    print('  - epochs 대폭 축소')
    print('  - 프로토타이핑 목적으로만 사용')
" 2>/dev/null

echo ""
echo "✅ ML 프로젝트 호환성 체크 완료!"
echo "================================"
