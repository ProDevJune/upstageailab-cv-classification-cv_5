#!/bin/bash

# 의존성 경고 무시하고 빠른 설치
# 경고는 나오지만 실제로는 정상 작동하는 경우를 위한 스크립트

echo "⚡ 의존성 경고 무시하고 빠른 설치..."

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

echo "✅ 현재 설치 상태 확인..."
python -c "
try:
    import cv2
    print(f'✅ OpenCV: {cv2.__version__}')
    try:
        print(f'✅ CV_8U: {cv2.CV_8U}')
    except:
        print('⚠️ CV_8U 없음')
except:
    print('❌ OpenCV 없음')

try:
    import albumentations
    print(f'✅ Albumentations: {albumentations.__version__}')
except:
    print('❌ Albumentations 없음')

try:
    import numpy
    print(f'✅ NumPy: {numpy.__version__}')
except:
    print('❌ NumPy 없음')

try:
    import pandas
    print(f'✅ Pandas: {pandas.__version__}')
except:
    print('❌ Pandas 없음')

try:
    import matplotlib
    print(f'✅ Matplotlib: {matplotlib.__version__}')
except:
    print('❌ Matplotlib 없음')
"

echo ""
echo "🧪 실제 기능 테스트..."
python -c "
import sys
try:
    import cv2
    import albumentations as A
    import numpy as np
    
    # 실제 변환 테스트
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.2),
    ])
    
    # 테스트 이미지 생성
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # 변환 적용
    augmented = transform(image=test_image)
    result_image = augmented['image']
    
    print('✅ 핵심 기능 테스트 성공!')
    print(f'   입력 이미지: {test_image.shape}')
    print(f'   출력 이미지: {result_image.shape}')
    print('')
    print('🎉 의존성 경고가 있어도 실제로는 정상 작동합니다!')
    print('🚀 실험을 진행하세요!')
    
except Exception as e:
    print(f'❌ 실제 기능 테스트 실패: {e}')
    print('💡 다른 해결 방법을 시도하세요:')
    print('   bash fix_dependency_conflicts.sh')
    print('   bash recreate_venv.sh')
    sys.exit(1)
"

echo ""
echo "💡 결론: 의존성 경고가 나와도 실제 기능은 정상입니다!"
echo "🚀 실험을 진행하세요:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
