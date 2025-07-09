#!/bin/bash

# CV_8U + NumPy 호환성 문제 완전 해결 스크립트
# numpy 2.x -> 1.x 다운그레이드 + 정확한 버전 고정

echo "🔧 CV_8U + NumPy 호환성 문제 완전 해결 시작..."

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

echo "🗑️ 모든 관련 패키지 완전 제거..."
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python albumentations numpy pandas scikit-learn matplotlib scipy

echo "📥 Step 1: NumPy 안정 버전 설치..."
pip install --no-cache-dir numpy==1.26.4

echo "📥 Step 2: OpenCV 호환 버전 설치..."
pip install --no-cache-dir opencv-python==4.8.1.78

echo "📥 Step 3: Albumentations 호환 버전 설치..."
pip install --no-cache-dir albumentations==1.4.0

echo "📥 Step 4: 핵심 데이터 과학 패키지 호환 버전 설치..."
pip install --no-cache-dir pandas==2.2.3
pip install --no-cache-dir scikit-learn==1.5.2
pip install --no-cache-dir matplotlib==3.9.2
pip install --no-cache-dir scipy==1.14.1

echo "✅ 설치 확인 및 테스트..."
python -c "
import sys
print('🔍 설치된 버전 확인:')

packages = ['numpy', 'opencv-python', 'albumentations', 'pandas', 'scikit-learn', 'matplotlib', 'scipy']
for pkg in packages:
    try:
        if pkg == 'opencv-python':
            import cv2
            print(f'✅ {pkg}: {cv2.__version__}')
        elif pkg == 'scikit-learn':
            import sklearn
            print(f'✅ {pkg}: {sklearn.__version__}')
        else:
            module = __import__(pkg)
            print(f'✅ {pkg}: {module.__version__}')
    except ImportError as e:
        print(f'❌ {pkg}: Import 실패 - {e}')
    except Exception as e:
        print(f'⚠️ {pkg}: 오류 - {e}')

print('\\n🧪 기능 테스트:')

# NumPy 테스트
try:
    import numpy as np
    arr = np.array([1, 2, 3])
    print(f'✅ NumPy 배열 생성: {arr}')
except Exception as e:
    print(f'❌ NumPy 테스트 실패: {e}')

# OpenCV CV_8U 테스트
try:
    import cv2
    cv_8u = getattr(cv2, 'CV_8U', None)
    if cv_8u is not None:
        print(f'✅ CV_8U 상수: {cv_8u}')
    else:
        print('⚠️ CV_8U 없음 (대체 방식 사용 가능)')
except Exception as e:
    print(f'❌ OpenCV 테스트 실패: {e}')

# Albumentations 테스트
try:
    import albumentations as A
    transform = A.HorizontalFlip(p=1.0)
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = transform(image=test_img)
    print('✅ Albumentations 변환 테스트 성공')
except Exception as e:
    print(f'❌ Albumentations 테스트 실패: {e}')

# Pandas 테스트
try:
    import pandas as pd
    df = pd.DataFrame({'test': [1, 2, 3]})
    print(f'✅ Pandas DataFrame 생성: {len(df)} rows')
except Exception as e:
    print(f'❌ Pandas 테스트 실패: {e}')

print('\\n🎉 모든 패키지 설치 및 테스트 완료!')
"

echo ""
echo "🚀 이제 실험을 다시 실행하세요:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
