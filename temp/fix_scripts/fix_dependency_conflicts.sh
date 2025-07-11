#!/bin/bash

# 의존성 충돌 완전 해결 - 강제 재설치 방식
# pip 의존성 해결기 문제를 우회하는 최종 해결책

echo "🔧 의존성 충돌 완전 해결 - 강제 재설치 시작..."

# 가상환경 활성화
[ -d "venv" ] && source venv/bin/activate

echo "🗑️ 모든 관련 패키지 완전 제거..."
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python
pip uninstall -y albumentations albucore qudida
pip uninstall -y numpy pandas scikit-learn matplotlib scipy seaborn
pip uninstall -y scikit-image Pillow imageio

echo "🧹 설치 준비 중..."

echo "📥 1단계: 기본 패키지 설치 (의존성 무시)..."
pip install --no-deps --no-cache-dir numpy==1.26.4
pip install --no-deps --no-cache-dir Pillow==10.4.0

echo "📥 2단계: OpenCV 설치 (의존성 무시)..."
pip install --no-deps --no-cache-dir opencv-python==4.8.1.78

echo "📥 3단계: 데이터 과학 패키지 설치..."
pip install --no-cache-dir matplotlib==3.9.2
pip install --no-cache-dir pandas==2.2.3
pip install --no-cache-dir scipy==1.14.1
pip install --no-cache-dir scikit-learn==1.5.2

echo "📥 4단계: Albumentations 의존성 먼저 설치..."
pip install --no-cache-dir albucore==0.0.9
pip install --no-cache-dir qudida==0.0.4

echo "📥 5단계: Albumentations 설치 (의존성 무시)..."
pip install --no-deps --no-cache-dir albumentations==1.4.0

echo "📥 6단계: 기타 패키지 설치..."
pip install --no-cache-dir seaborn==0.13.2
pip install --no-cache-dir imageio==2.35.1

echo "🔍 설치된 패키지 확인..."
pip list | grep -E "(numpy|opencv|albumentations|pandas|matplotlib|scipy|scikit-learn|seaborn)"

echo "✅ 포괄적 테스트..."
python -c "
import sys
success = True

# 기본 패키지 테스트
test_packages = {
    'numpy': '1.26.4',
    'opencv-python': 'cv2',
    'albumentations': '1.4.0',
    'pandas': '2.2.3',
    'matplotlib': '3.9.2',
    'scipy': '1.14.1',
    'scikit-learn': 'sklearn',
    'seaborn': '0.13.2'
}

for package, import_name in test_packages.items():
    try:
        if import_name == 'cv2':
            import cv2
            version = cv2.__version__
            module_name = 'OpenCV'
        elif import_name == 'sklearn':
            import sklearn
            version = sklearn.__version__
            module_name = 'scikit-learn'
        else:
            module = __import__(import_name)
            version = module.__version__
            module_name = package
            
        print(f'✅ {module_name}: {version}')
    except Exception as e:
        print(f'❌ {package}: {e}')
        success = False

# 기능 테스트
print('\\n🧪 기능 테스트:')

# CV_8U 테스트
try:
    import cv2
    cv_8u = getattr(cv2, 'CV_8U', None)
    if cv_8u is not None:
        print(f'✅ CV_8U 상수: {cv_8u}')
    else:
        print('⚠️ CV_8U 없음')
except Exception as e:
    print(f'❌ OpenCV CV_8U 테스트: {e}')
    success = False

# Albumentations 테스트
try:
    import albumentations as A
    import numpy as np
    transform = A.HorizontalFlip(p=1.0)
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = transform(image=test_img)
    print('✅ Albumentations 변환 성공')
except Exception as e:
    print(f'❌ Albumentations 테스트: {e}')
    success = False

# Pandas 테스트
try:
    import pandas as pd
    df = pd.DataFrame({'test': [1, 2, 3]})
    print(f'✅ Pandas DataFrame: {len(df)} rows')
except Exception as e:
    print(f'❌ Pandas 테스트: {e}')
    success = False

if success:
    print('\\n🎉 모든 의존성 충돌 해결 완료!')
    print('🚀 실험 실행 준비 완료!')
else:
    print('\\n❌ 일부 문제가 남아있습니다.')
    sys.exit(1)
"

echo ""
echo "🎯 실험 재실행:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
