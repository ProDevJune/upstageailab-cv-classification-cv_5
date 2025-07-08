#!/usr/bin/env python3
"""
패키지 자동 설치 + HPO 실행
"""

import sys
import os
import subprocess

def install_package(package):
    """패키지 자동 설치"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except:
        return False

def ensure_packages():
    """필수 패키지들 확인 및 설치"""
    required_packages = {
        'yaml': 'PyYAML',
        'torch': 'torch',
        'pandas': 'pandas', 
        'numpy': 'numpy',
        'psutil': 'psutil'
    }
    
    missing = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {module} OK")
        except ImportError:
            print(f"❌ {module} 누락")
            missing.append(package)
    
    if missing:
        print(f"\n📦 누락된 패키지 설치 중: {missing}")
        for package in missing:
            print(f"  설치 중: {package}")
            if install_package(package):
                print(f"  ✅ {package} 설치 완료")
            else:
                print(f"  ❌ {package} 설치 실패")
    
    # 최종 확인
    try:
        import yaml, torch, pandas, numpy, psutil
        print("✅ 모든 필수 패키지 준비 완료")
        return True
    except ImportError as e:
        print(f"❌ 여전히 누락: {e}")
        return False

def run_hpo_simulation():
    """HPO 시뮬레이션 실행"""
    print("\n🚀 HPO 시뮬레이션 시작")
    print("=" * 50)
    
    import random
    import time
    from datetime import datetime
    
    # 시스템 정보
    try:
        import torch
        import platform
        import psutil
        
        print(f"플랫폼: {platform.system()} {platform.machine()}")
        print(f"메모리: {round(psutil.virtual_memory().total / (1024**3), 1)} GB")
        
        if torch.backends.mps.is_available():
            device = "🍎 MPS"
            batch_size = 25
        elif torch.cuda.is_available():
            device = "🚀 CUDA"  
            batch_size = 48
        else:
            device = "💻 CPU"
            batch_size = 16
            
        print(f"디바이스: {device}")
        print(f"권장 배치 크기: {batch_size}")
        
    except Exception as e:
        print(f"시스템 정보 수집 실패: {e}")
        device = "Unknown"
        batch_size = 32
    
    # 실험 설정
    experiments = [
        {'model': 'resnet34', 'lr': 0.001, 'augment': 'minimal'},
        {'model': 'resnet50', 'lr': 0.0001, 'augment': 'moderate'},
        {'model': 'efficientnet_b3', 'lr': 0.00001, 'augment': 'strong'},
        {'model': 'resnet34', 'lr': 0.0001, 'augment': 'moderate'},
        {'model': 'resnet50', 'lr': 0.001, 'augment': 'minimal'},
    ]
    
    results = []
    
    print(f"\n🎯 {len(experiments)}개 실험 시작")
    
    for i, exp in enumerate(experiments, 1):
        print(f"\n📊 실험 {i}/{len(experiments)}")
        print(f"   모델: {exp['model']}")
        print(f"   학습률: {exp['lr']}")
        print(f"   증강: {exp['augment']}")
        print(f"   배치 크기: {batch_size}")
        
        # 시뮬레이션 (실제로는 훈련)
        print("   ⏳ 훈련 중...")
        time.sleep(2)  # 실제로는 수십 분
        
        # 랜덤 결과 생성 (실제로는 실제 훈련 결과)
        f1_score = random.uniform(0.75, 0.93)
        accuracy = random.uniform(78, 95)
        training_time = random.uniform(15, 45)
        
        result = {
            'experiment_id': f"sim_{i:03d}",
            'model': exp['model'],
            'lr': exp['lr'],
            'augment': exp['augment'],
            'batch_size': batch_size,
            'f1_score': f1_score,
            'accuracy': accuracy,
            'training_time': training_time,
            'device': device
        }
        
        results.append(result)
        
        print(f"   ✅ 완료: F1={f1_score:.4f}, Acc={accuracy:.1f}%, 시간={training_time:.1f}분")
    
    # 결과 분석
    print(f"\n📊 실험 결과 분석")
    print("=" * 50)
    
    # 최고 성능
    best = max(results, key=lambda x: x['f1_score'])
    print(f"🏆 최고 성능:")
    print(f"   실험: {best['experiment_id']}")
    print(f"   모델: {best['model']}")
    print(f"   F1: {best['f1_score']:.4f}")
    print(f"   정확도: {best['accuracy']:.1f}%")
    
    # 평균 성능
    avg_f1 = sum(r['f1_score'] for r in results) / len(results)
    avg_acc = sum(r['accuracy'] for r in results) / len(results)
    total_time = sum(r['training_time'] for r in results)
    
    print(f"\n📈 전체 통계:")
    print(f"   평균 F1: {avg_f1:.4f}")
    print(f"   평균 정확도: {avg_acc:.1f}%")
    print(f"   총 훈련 시간: {total_time:.1f}분")
    
    # 모델별 성능
    models = {}
    for r in results:
        model = r['model']
        if model not in models:
            models[model] = []
        models[model].append(r['f1_score'])
    
    print(f"\n🔬 모델별 평균 성능:")
    for model, scores in models.items():
        avg_score = sum(scores) / len(scores)
        print(f"   {model}: {avg_score:.4f} ({len(scores)}개 실험)")
    
    # 결과 저장
    try:
        import yaml
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'device': device,
            'total_experiments': len(results),
            'best_f1': best['f1_score'],
            'avg_f1': avg_f1,
            'experiments': results
        }
        
        with open('hpo_simulation_results.yaml', 'w') as f:
            yaml.dump(summary, f, default_flow_style=False)
        
        print(f"\n📝 결과 저장: hpo_simulation_results.yaml")
        
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")
    
    print(f"\n✅ HPO 시뮬레이션 완료!")
    print(f"🎯 실제 데이터로 훈련하면 더 정확한 결과를 얻을 수 있습니다.")

def main():
    print("🔧 자동 패키지 설치 + HPO 시스템")
    print("=" * 50)
    
    # 1. 패키지 확인 및 설치
    if not ensure_packages():
        print("❌ 패키지 설치 실패. 수동으로 설치해주세요:")
        print("pip install PyYAML torch pandas numpy psutil")
        return
    
    # 2. HPO 실행
    print("\n🚀 HPO 실험을 시작하시겠습니까?")
    print("(실제 훈련 대신 시뮬레이션이 실행됩니다)")
    
    choice = input("시작하시겠습니까? (y/N): ").strip().lower()
    
    if choice == 'y':
        run_hpo_simulation()
    else:
        print("👋 실행 취소됨")

if __name__ == "__main__":
    main()
