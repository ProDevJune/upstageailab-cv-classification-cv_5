#!/bin/bash

# 실행 권한 자동 부여
chmod +x "$0" 2>/dev/null

# AIStages 서버 경로 호환성 체크
echo "🔍 AIStages 서버 경로 호환성 체크"
echo "================================="
echo "⏰ 체크 시간: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 현재 경로 정보
CURRENT_PATH=$(pwd)
TARGET_PATH="/data/ephemeral/home/upstageailab-cv-classification-cv_5"

echo "📁 경로 정보:"
echo "  현재 경로: $CURRENT_PATH"
echo "  예상 경로: $TARGET_PATH"
echo ""

# 1. 경로 일치 확인
echo "🎯 1. 경로 일치 확인"
echo "-------------------"

if [ "$CURRENT_PATH" = "$TARGET_PATH" ]; then
    echo "✅ 경로 일치: 문제없음"
    PATH_MATCH=true
else
    echo "⚠️  경로 불일치 감지"
    echo "  현재: $CURRENT_PATH"
    echo "  예상: $TARGET_PATH"
    PATH_MATCH=false
fi

echo ""

# 2. 스크립트 내 하드코딩된 경로 체크
echo "🔍 2. 스크립트 내 경로 의존성 체크"
echo "--------------------------------"

echo "주요 스크립트들의 경로 의존성 분석:"

# 상대 경로 사용 확인
relative_path_files=(
    "run_optimal_performance.sh"
    "run_v2_1_only.sh"
    "run_v2_2_only.sh"
    "v2_experiment_generator.py"
    "v3_experiment_generator.py"
)

problematic_paths=()

for file in "${relative_path_files[@]}"; do
    if [ -f "$file" ]; then
        echo -n "  $file: "
        
        # 절대 경로 패턴 체크
        absolute_paths=$(grep -n "/Users/jayden\|/home/\|/data/" "$file" 2>/dev/null | grep -v "ephemeral" || true)
        
        if [ -n "$absolute_paths" ]; then
            echo "⚠️  절대 경로 발견"
            problematic_paths+=("$file")
        else
            echo "✅ 상대 경로 사용"
        fi
    else
        echo "  $file: ❌ 파일 없음"
    fi
done

echo ""

# 3. 데이터 경로 확인
echo "📊 3. 데이터 디렉토리 존재 확인"
echo "------------------------------"

data_dirs=(
    "data"
    "data/train"
    "data/test"
    "codes"
)

for dir in "${data_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir 존재"
    else
        echo "  ❌ $dir 없음"
    fi
done

echo ""

# 4. 설정 파일들의 경로 체크
echo "⚙️  4. 설정 파일 경로 체크"
echo "-------------------------"

config_files=(
    "codes/config_v2_1.yaml"
    "codes/config_v2_2.yaml"
    "codes/config_v3_modelA.yaml"
    "codes/config_v3_modelB.yaml"
)

echo "설정 파일들의 data_dir 설정 확인:"

for config in "${config_files[@]}"; do
    if [ -f "$config" ]; then
        echo -n "  $config: "
        
        # data_dir 설정 확인
        data_dir_setting=$(grep "data_dir:" "$config" 2>/dev/null || true)
        
        if echo "$data_dir_setting" | grep -q "^\s*data_dir:\s*[\"']\./data[\"']\|^\s*data_dir:\s*\./data"; then
            echo "✅ 상대 경로 사용"
        elif echo "$data_dir_setting" | grep -q "/data/ephemeral/home/upstageailab-cv-classification-cv_5/data"; then
            echo "✅ AIStages 경로 사용"
        elif echo "$data_dir_setting" | grep -q "/Users/jayden"; then
            echo "⚠️  Mac 경로 하드코딩됨"
            problematic_paths+=("$config")
        else
            echo "🟡 확인 필요: $data_dir_setting"
        fi
    else
        echo "  $config: ❌ 파일 없음"
    fi
done

echo ""

# 5. Python 스크립트 내 경로 의존성 체크
echo "🐍 5. Python 스크립트 경로 의존성"
echo "--------------------------------"

python_files=(
    "v2_experiment_generator.py"
    "v3_experiment_generator.py"
)

for py_file in "${python_files[@]}"; do
    if [ -f "$py_file" ]; then
        echo -n "  $py_file: "
        
        # project_root 설정 확인
        project_root_line=$(grep -n "project_root\|os.path.dirname\|sys.path" "$py_file" 2>/dev/null | head -1 || true)
        
        if [ -n "$project_root_line" ]; then
            if echo "$project_root_line" | grep -q "os.path.dirname\|os.path.abspath"; then
                echo "✅ 동적 경로 설정"
            else
                echo "🟡 경로 설정 확인 필요"
            fi
        else
            echo "✅ 경로 의존성 없음"
        fi
    else
        echo "  $py_file: ❌ 파일 없음"
    fi
done

echo ""

# 6. 문제 해결 방안 제시
echo "🔧 6. 문제 해결 방안"
echo "-------------------"

if [ ${#problematic_paths[@]} -gt 0 ]; then
    echo "⚠️  경로 수정이 필요한 파일들:"
    for file in "${problematic_paths[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "🛠️  자동 수정 방법:"
    echo "  1. 절대 경로 → 상대 경로 변환"
    echo "  2. AIStages 경로로 업데이트"
    echo "  3. 동적 경로 설정 적용"
    echo ""
    
    # 자동 수정 옵션 제공
    echo "자동 수정을 실행하시겠습니까? (y/N): "
    read -r fix_confirm
    
    if [[ $fix_confirm == "y" || $fix_confirm == "Y" ]]; then
        echo "🔧 자동 경로 수정 실행 중..."
        
        for file in "${problematic_paths[@]}"; do
            echo "  수정 중: $file"
            
            # Mac 경로를 상대 경로로 변경
            sed -i.bak 's|/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5|.|g' "$file" 2>/dev/null || true
            
            # 절대 경로를 AIStages 경로로 변경 (백업용)
            sed -i.bak2 "s|/Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5|$TARGET_PATH|g" "$file" 2>/dev/null || true
            
            echo "    ✅ $file 수정 완료"
        done
        
        echo "✅ 자동 경로 수정 완료!"
    fi
    
else
    echo "✅ 경로 관련 문제 없음!"
fi

echo ""

# 7. AIStages 환경 특화 확인
echo "🚀 7. AIStages 환경 특화 확인"
echo "----------------------------"

echo "AIStages 환경 특성:"

# /data/ephemeral 특성 확인
if echo "$CURRENT_PATH" | grep -q "/data/ephemeral"; then
    echo "  ✅ ephemeral 저장소 사용 중"
    echo "    → 재시작 시 데이터 손실 가능성 있음"
    echo "    → 중요 결과는 persistent 저장소에 백업 권장"
else
    echo "  🟡 ephemeral 저장소가 아님"
fi

# 권한 확인
if [ -w "$CURRENT_PATH" ]; then
    echo "  ✅ 쓰기 권한 있음"
else
    echo "  ❌ 쓰기 권한 없음"
fi

# Docker 환경 확인
if [ -f "/.dockerenv" ]; then
    echo "  ✅ Docker 컨테이너 환경"
else
    echo "  🟡 일반 리눅스 환경"
fi

echo ""

# 8. 최종 호환성 결과
echo "📋 8. 최종 호환성 결과"
echo "----------------------"

compatible=true

if [ "$PATH_MATCH" = true ] && [ ${#problematic_paths[@]} -eq 0 ]; then
    echo "🎉 완벽 호환!"
    echo "  ✅ 경로 일치"
    echo "  ✅ 상대 경로 사용"
    echo "  ✅ 설정 파일 정상"
    echo ""
    echo "🚀 바로 실험 실행 가능:"
    echo "  ./run_optimal_performance.sh"
    
elif [ ${#problematic_paths[@]} -eq 0 ]; then
    echo "✅ 호환 가능 (경로 불일치는 문제없음)"
    echo "  🟡 현재 경로와 다르지만 상대 경로 사용으로 문제없음"
    echo ""
    echo "🚀 실험 실행 가능:"
    echo "  ./run_optimal_performance.sh"
    
else
    echo "⚠️  부분 호환 (수정 권장)"
    echo "  🔧 일부 파일의 경로 수정 필요"
    echo ""
    echo "권장 조치:"
    echo "  1. 위에서 제안한 자동 수정 실행"
    echo "  2. 또는 수동으로 절대 경로를 상대 경로로 변경"
    echo "  3. 수정 후 실험 실행"
fi

echo ""
echo "✅ AIStages 서버 경로 호환성 체크 완료!"
echo "======================================="
echo "⏰ 완료 시간: $(date '+%Y-%m-%d %H:%M:%S')"
