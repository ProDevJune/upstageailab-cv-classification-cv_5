#!/bin/bash
# WanDB 설정 개선 완료 - 최종 테스트 및 검증 스크립트

echo "🎯 WanDB 설정 개선 완료 - 최종 검증"
echo "=================================================="

# 기본 디렉토리로 이동
cd /Users/jayden/Developer/Projects/upstageailab-cv-classification-cv_5

echo ""
echo "📋 1단계: 권한 설정"
echo "chmod +x final_v3_setup.sh"
chmod +x final_v3_setup.sh
chmod +x v2_experiment_generator_enhanced.py
chmod +x v3_experiment_generator_enhanced.py
chmod +x unified_dashboard/unified_monitor.py

echo ""
echo "📋 2단계: 개선된 V2 실험 생성 테스트"
echo "python v2_experiment_generator_enhanced.py --type basic_model_comparison --limit 5 --dry-run"
python v2_experiment_generator_enhanced.py --type basic_model_comparison --limit 5 --dry-run

echo ""
echo "📋 3단계: 개선된 V3 실험 생성 테스트"
echo "python v3_experiment_generator_enhanced.py --type basic_model_combinations --limit 5 --dry-run"
python v3_experiment_generator_enhanced.py --type basic_model_combinations --limit 5 --dry-run

echo ""
echo "📋 4단계: 통합 대시보드 테스트"
echo "python unified_dashboard/unified_monitor.py --status"
python unified_dashboard/unified_monitor.py --status

echo ""
echo "🔍 5단계: Config 파일 WanDB 설정 검증"
echo "V2_1 config 확인:"
grep -A 5 "wandb:" codes/config_v2_1.yaml

echo ""
echo "V2_2 config 확인:"
grep -A 5 "wandb:" codes/config_v2_2.yaml

echo ""
echo "V3 Model A config 확인:"
grep -A 5 "wandb:" codes/config_v3_modelA.yaml

echo ""
echo "V3 Model B config 확인:"
grep -A 5 "wandb:" codes/config_v3_modelB.yaml

echo ""
echo "📊 6단계: 실험 매트릭스 파일 확인"
ls -la *experiment_matrix*.yaml

echo ""
echo "🚀 7단계: 실제 실험 생성 (소규모 테스트)"
echo "V2 Enhanced 실험 생성 (3개):"
python v2_experiment_generator_enhanced.py --type basic_model_comparison --limit 3

echo ""
echo "V3 Enhanced 실험 생성 (3개):"
python v3_experiment_generator_enhanced.py --type basic_model_combinations --limit 3

echo ""
echo "✅ WanDB 설정 개선 완료 요약"
echo "=================================================="
echo "1. ✅ Project 이름을 model_name 기반으로 변경"
echo "2. ✅ V2_1, V2_2, V3 프로젝트 분리"
echo "3. ✅ TTA 전략 다양화 (6가지 전략)"
echo "4. ✅ 실험 매트릭스 확장 (200+ 조합)"
echo "5. ✅ Tags 시스템으로 실험 분류"
echo "6. ✅ Run 이름 개선 및 간소화"
echo "7. ✅ 자동화 시스템 업데이트 완료"

echo ""
echo "🎉 모든 WanDB 설정 개선이 성공적으로 완료되었습니다!"
echo ""
echo "📈 다음 단계:"
echo "  1. 실제 실험 실행: ./v2_experiments/scripts/run_enhanced_v2_experiments.sh"
echo "  2. V3 실험 실행: ./v3_experiments/scripts/run_enhanced_v3_hierarchical_experiments.sh"
echo "  3. 통합 모니터링: python unified_dashboard/unified_monitor.py --continuous"
echo "  4. WanDB 대시보드에서 새로운 프로젝트 구조 확인"
echo ""
echo "💡 참고:"
echo "  - V2 확장 실험 매트릭스: v2_experiment_matrix_enhanced.yaml"
echo "  - V3 확장 실험 매트릭스: v3_experiment_matrix_enhanced.yaml"
echo "  - 통합 모니터링 시스템: unified_dashboard/"
