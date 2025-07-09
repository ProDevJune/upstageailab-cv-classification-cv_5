#!/usr/bin/env python3
"""
확장 가능한 하이퍼파라미터 실험 시스템 통합 실행 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """메인 실행 함수"""
    print("🚀 확장 가능한 하이퍼파라미터 실험 시스템")
    print("=" * 60)
    
    print("📋 사용 가능한 옵션:")
    print("1. 🎯 실험 매트릭스 확인")
    print("2. 🚀 모든 실험 실행")
    print("3. 🎨 특정 모델 실험")
    print("4. ⚙️ 특정 카테고리 실험")
    print("5. 🔧 맞춤형 실험")
    print("6. 📊 실험 결과 요약")
    print("0. 🚪 종료")
    
    while True:
        try:
            choice = input("\n선택하세요 (0-6): ").strip()
            
            if choice == '0':
                print("👋 시스템을 종료합니다.")
                break
            elif choice == '1':
                show_experiment_matrix()
            elif choice == '2':
                run_all_experiments()
            elif choice == '3':
                run_model_experiments()
            elif choice == '4':
                run_category_experiments()
            elif choice == '5':
                run_custom_experiments()
            elif choice == '6':
                show_experiment_summary()
            else:
                print("❌ 잘못된 선택입니다. 0-6 사이의 숫자를 입력하세요.")
                
        except KeyboardInterrupt:
            print("\n👋 사용자가 중단했습니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

def show_experiment_matrix():
    """실험 매트릭스 출력"""
    try:
        from hyperparameter_system.hyperparameter_configs import DynamicExperimentMatrix
        matrix = DynamicExperimentMatrix()
        matrix.print_experiment_matrix()
    except Exception as e:
        print(f"❌ 매트릭스 출력 실패: {e}")

def run_all_experiments():
    """모든 실험 실행"""
    print("\n⚠️ 모든 실험을 실행하면 시간이 오래 걸립니다.")
    confirm = input("계속 진행하시겠습니까? (y/N): ").strip().lower()
    
    if confirm == 'y':
        try:
            from hyperparameter_system.experiment_runner import ExtensibleExperimentRunner
            runner = ExtensibleExperimentRunner()
            results = runner.run_all_experiments()
            print(f"✅ 전체 실험 완료: {len(results)}개")
        except Exception as e:
            print(f"❌ 실험 실행 실패: {e}")
    else:
        print("실험을 취소했습니다.")

def run_model_experiments():
    """특정 모델 실험"""
    try:
        from hyperparameter_system.hyperparameter_configs import DynamicExperimentMatrix
        matrix = DynamicExperimentMatrix()
        
        print("\n🤖 사용 가능한 모델들:")
        for i, model in enumerate(matrix.models, 1):
            print(f"   {i}. {model['name']} - {model.get('description', '')}")
        
        model_names = input("\n실험할 모델 이름들 (공백으로 구분): ").strip().split()
        
        if model_names:
            from hyperparameter_system.experiment_runner import ExtensibleExperimentRunner
            runner = ExtensibleExperimentRunner()
            results = runner.run_model_experiments(model_names)
            print(f"✅ 모델 실험 완료: {len(results)}개")
        else:
            print("모델을 선택하지 않았습니다.")
            
    except Exception as e:
        print(f"❌ 모델 실험 실패: {e}")

def run_category_experiments():
    """특정 카테고리 실험"""
    try:
        from hyperparameter_system.hyperparameter_configs import DynamicExperimentMatrix
        matrix = DynamicExperimentMatrix()
        
        print("\n⚙️ 사용 가능한 카테고리들:")
        for i, category in enumerate(matrix.categories, 1):
            print(f"   {i}. {category.name} - {category.description}")
        
        category_names = input("\n실험할 카테고리 이름들 (공백으로 구분): ").strip().split()
        
        if category_names:
            from hyperparameter_system.experiment_runner import ExtensibleExperimentRunner
            runner = ExtensibleExperimentRunner()
            results = runner.run_category_experiments(category_names)
            print(f"✅ 카테고리 실험 완료: {len(results)}개")
        else:
            print("카테고리를 선택하지 않았습니다.")
            
    except Exception as e:
        print(f"❌ 카테고리 실험 실패: {e}")

def run_custom_experiments():
    """맞춤형 실험"""
    try:
        from hyperparameter_system.hyperparameter_configs import DynamicExperimentMatrix
        from hyperparameter_system.experiment_runner import ExtensibleExperimentRunner
        
        matrix = DynamicExperimentMatrix()
        
        print("\n🤖 사용 가능한 모델들:")
        for i, model in enumerate(matrix.models, 1):
            print(f"   {i}. {model['name']}")
        
        model_names = input("\n실험할 모델 이름들 (공백으로 구분): ").strip().split()
        
        print("\n⚙️ 사용 가능한 카테고리들:")
        for i, category in enumerate(matrix.categories, 1):
            print(f"   {i}. {category.name}")
        
        category_names = input("\n실험할 카테고리 이름들 (공백으로 구분): ").strip().split()
        
        if model_names and category_names:
            runner = ExtensibleExperimentRunner()
            results = runner.run_custom_experiments(model_names, category_names)
            print(f"✅ 맞춤형 실험 완료: {len(results)}개")
        else:
            print("모델과 카테고리를 모두 선택해야 합니다.")
            
    except Exception as e:
        print(f"❌ 맞춤형 실험 실패: {e}")

def show_experiment_summary():
    """실험 결과 요약"""
    try:
        from hyperparameter_system.experiment_runner import ExtensibleExperimentRunner
        runner = ExtensibleExperimentRunner()
        summary = runner.get_experiment_summary()
        
        print("\n📊 실험 결과 요약:")
        print("=" * 40)
        
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4f}")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ 요약 출력 실패: {e}")

if __name__ == "__main__":
    main()
