#!/bin/bash

# 🚀 증강 데이터 긴급 적용 스크립트 (3시간 마감용)
echo "⚡ 증강 데이터 긴급 적용 시작"
echo "=========================="

# 1. 현재 위치 확인
echo "📁 현재 위치: $(pwd)"

# 2. data 디렉토리로 이동
cd data

# 3. aug_data.tar.gz 파일 확인
if [ -f "aug_data.tar.gz" ]; then
    echo "✅ aug_data.tar.gz 파일 발견"
    
    # 4. 압축 해제
    echo "📦 압축 해제 중..."
    tar -xzvf aug_data.tar.gz
    
    # 5. 해제된 폴더 확인
    echo "📊 압축 해제 완료. 폴더 내용:"
    ls -la aug_data*/
    
    # 6. test 폴더 복사 (필수 작업)
    echo "📋 test 폴더 복사 중..."
    for dir in aug_data*/; do
        if [ ! -d "$dir/test" ]; then
            cp -r test "$dir/"
            echo "✅ $dir 에 test 폴더 복사 완료"
        fi
    done
    
else
    echo "❌ aug_data.tar.gz 파일이 없습니다!"
    echo "   상현님 서버에서 다운로드 필요"
    exit 1
fi

# 7. 상위 디렉토리로 복귀
cd ..

echo ""
echo "🎯 사용 가능한 증강 데이터셋:"
ls -la data/aug_data*/

echo ""
echo "⚡ 긴급 적용 방법:"
echo "1. 가장 유망한 aug_data_500 사용 권장"
echo "2. config 파일 data_dir 수정 필요"
echo "3. 오프라인 증강 코드 주석 처리 필요"

echo ""
echo "🚀 즉시 실행 명령어:"
echo "   sed -i 's|data_dir: \"./data\"|data_dir: \"./data/aug_data_500\"|' codes/config_v2_1.yaml"
echo "   sed -i 's|data_dir: \"./data\"|data_dir: \"./data/aug_data_500\"|' codes/config_v2_2.yaml"
echo ""
echo "✅ 증강 데이터 준비 완료!"
