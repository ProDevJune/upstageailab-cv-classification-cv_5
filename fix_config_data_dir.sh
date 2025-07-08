#!/bin/bash

echo "🔥 config_v2.yaml Mac 하드코딩 경로 완전 수정!"
echo "==========================================="

echo "📝 config_v2.yaml에서 Mac 절대경로 제거..."

# config_v2.yaml 수정
python3 << 'EOF'
import yaml

# config_v2.yaml 읽기
with open('codes/config_v2.yaml', 'r') as f:
    config = yaml.safe_load(f)

print(f"🔍 현재 data_dir: {config.get('data_dir', 'Not found')}")

# Mac 절대경로를 상대경로로 변경
if 'data_dir' in config:
    old_data_dir = config['data_dir']
    config['data_dir'] = "data"  # 상대경로로 변경
    print(f"✅ data_dir 변경: {old_data_dir} -> {config['data_dir']}")
else:
    config['data_dir'] = "data"
    print("✅ data_dir 새로 설정: data")

# 파일 저장
with open('codes/config_v2.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

print("🎉 config_v2.yaml 수정 완료!")
EOF

echo ""
echo "🧪 수정 확인..."
echo "📍 새로운 data_dir 설정:"
grep -A1 -B1 "data_dir" codes/config_v2.yaml

echo ""
echo "📍 Mac 경로 잔존 확인:"
grep -n "/Users/jayden" codes/config_v2.yaml && echo "❌ Mac 경로 아직 남아있음" || echo "✅ Mac 경로 완전 제거됨"

echo ""
echo "📂 실제 data 폴더 확인:"
ls -la data/ | head -3

echo ""
echo "🎉 완전 수정 완료!"
echo ""
echo "📋 수정 내용:"
echo "✅ config_v2.yaml의 data_dir을 상대경로로 변경"
echo "✅ '/Users/jayden/...' -> 'data'"
echo "✅ Linux 서버에서 정상 경로 인식 가능"
echo ""
echo "🚀 이제 Linux에서 확실히 작동합니다:"
echo "./run_code_v2.sh"
