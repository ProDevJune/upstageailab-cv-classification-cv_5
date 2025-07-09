#!/bin/bash

# AIStages 서버에서 CV_8U 오류 해결을 위한 종합 수정 스크립트
# 사용법: bash fix_cv_8u_error_robust.sh

echo "🔧 CV_8U AttributeError 해결을 위한 강화된 수정 시작..."

# 가상환경 활성화 (venv 폴더가 있다면)
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 현재 버전 확인
echo "📊 현재 설치된 버전 확인:"
python -c "
try:
    import cv2
    print(f'OpenCV: {cv2.__version__}')
except ImportError:
    print('OpenCV: 설치되지 않음')

try:
    import albumentations as A
    print(f'Albumentations: {A.__version__}')
except ImportError:
    print('Albumentations: 설치되지 않음')
" 2>/dev/null

# 문제가 되는 패키지들 제거 (오류 무시)
echo "🗑️ 기존 패키지 제거 중..."
pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python albumentations 2>/dev/null || true

# 설치 준비
echo "🧹 설치 준비 중..."

# 방법 1: 직접 설치 시도
echo "📥 방법 1: 호환 패키지 직접 설치 시도..."
if pip install opencv-python==4.8.1.78 --no-cache-dir && pip install albumentations==1.4.0 --no-cache-dir; then
    echo "✅ 방법 1 성공!"
else
    echo "⚠️ 방법 1 실패, 방법 2 시도..."
    
    # 방법 2: 더 안정적인 버전으로 시도
    echo "📥 방법 2: 더 안정적인 버전으로 설치..."
    if pip install opencv-python==4.7.1.72 --no-cache-dir && pip install albumentations==1.3.1 --no-cache-dir; then
        echo "✅ 방법 2 성공!"
    else
        echo "⚠️ 방법 2 실패, 방법 3 시도..."
        
        # 방법 3: 최소 호환 버전
        echo "📥 방법 3: 최소 호환 버전으로 설치..."
        if pip install opencv-python==4.6.0.66 --no-cache-dir && pip install albumentations==1.3.0 --no-cache-dir; then
            echo "✅ 방법 3 성공!"
        else
            echo "❌ 모든 방법 실패. 수동 설치 필요."
            echo "💡 다음 명령어를 개별적으로 실행해보세요:"
            echo "  pip install --upgrade pip"
            echo "  pip install opencv-python==4.8.1.78"
            echo "  pip install albumentations==1.4.0"
            exit 1
        fi
    fi
fi

# 설치 확인 및 테스트
echo "✅ 설치 확인 중..."
python -c "
import sys
success = True

try:
    import cv2
    print(f'✅ OpenCV 버전: {cv2.__version__}')
    
    # CV_8U 속성 확인
    cv_8u = getattr(cv2, 'CV_8U', None)
    if cv_8u is not None:
        print(f'✅ CV_8U 상수: {cv_8u}')
    else:
        print('⚠️ CV_8U 상수를 찾을 수 없지만 다른 방식으로 작동할 수 있습니다')
        
except ImportError as e:
    print(f'❌ OpenCV import 실패: {e}')
    success = False

try:
    import albumentations as A
    print(f'✅ Albumentations 버전: {A.__version__}')
    
    # 간단한 변환 테스트
    import numpy as np
    transform = A.Compose([A.HorizontalFlip(p=1.0)])
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    result = transform(image=test_image)
    print('✅ Albumentations 변환 테스트 성공')
    
except ImportError as e:
    print(f'❌ Albumentations import 실패: {e}')
    success = False
except Exception as e:
    print(f'⚠️ Albumentations 테스트 중 오류: {e}')

if success:
    print('\\n🎉 CV_8U 오류 해결 완료!')
    print('💡 이제 다시 실험을 실행해보세요.')
else:
    print('\\n❌ 문제가 해결되지 않았습니다.')
    print('📞 추가 지원이 필요합니다.')
    sys.exit(1)
"

echo ""
echo "🚀 실험 재실행 명령어:"
echo "  python codes/gemini_main_v2.py --config [config_file]"
