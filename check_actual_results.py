#!/usr/bin/env python3
"""
실제 실험 결과 확인 스크립트
W&B에서 진짜 결과들을 가져와서 비교
"""

import json
import yaml
from pathlib import Path

def check_wandb_results():
    """W&B에서 실제 결과들 확인"""
    try:
        import wandb
        api = wandb.Api()
        
        print("🔍 W&B에서 실제 실험 결과 확인")
        print("=" * 60)
        
        # 완료된 실험들 목록
        completed_experiments = [
            "exp_efficientnet_b4_focal_mixup_noocr_010",
            "exp_efficientnet_b4_label_mixup_noocr_012", 
            "exp_swin_transformer_focal_mixup_noocr_004",
            "exp_efficientnet_b4_mixup_cutmix_noocr_009",
            "exp_swin_transformer_label_mixup_noocr_006",
            "exp_convnext_base_focal_mixup_noocr_016",
            "exp_efficientnet_b4_focal_loss_noocr_008",
            "exp_swin_transformer_mixup_cutmix_noocr_003",
            "exp_convnext_base_label_mixup_noocr_018",
            "exp_efficientnet_b4_label_smooth_noocr_011",
            "exp_swin_transformer_focal_loss_noocr_002",
            "exp_convnext_base_mixup_cutmix_noocr_015",
            "exp_efficientnet_b4_baseline_noocr_007",
            "exp_swin_transformer_label_smooth_noocr_005"
        ]
        
        results = []
        
        for exp_id in completed_experiments:
            print(f"\n📊 {exp_id}")
            
            # config 파일에서 W&B 프로젝트명 확인
            config_path = f"experiments/configs/{exp_id}.yaml"
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    project_name = config.get('wandb', {}).get('project')
                    
                if project_name:
                    print(f"   W&B 프로젝트: {project_name}")
                    
                    try:
                        # W&B에서 런 찾기
                        runs = api.runs(project_name)
                        
                        if runs:
                            run = runs[0]  # 가장 최근 런
                            summary = run.summary
                            
                            f1 = summary.get('val_f1', summary.get('validation_f1'))
                            acc = summary.get('val_acc', summary.get('validation_acc'))
                            
                            if f1 is not None and acc is not None:
                                print(f"   ✅ 실제 결과: F1={f1:.4f}, Acc={acc:.4f}")
                                print(f"   📅 실행 시간: {run.created_at}")
                                
                                results.append({
                                    'experiment_id': exp_id,
                                    'validation_f1': float(f1),
                                    'validation_acc': float(acc),
                                    'wandb_run_id': run.id,
                                    'model': config.get('model_name'),
                                    'criterion': config.get('criterion')
                                })
                            else:
                                print(f"   ⚠️ W&B에서 메트릭을 찾을 수 없음")
                        else:
                            print(f"   ⚠️ W&B에서 런을 찾을 수 없음")
                            
                    except Exception as e:
                        print(f"   ❌ W&B API 오류: {e}")
                else:
                    print(f"   ❌ Config에서 W&B 프로젝트명을 찾을 수 없음")
            else:
                print(f"   ❌ Config 파일을 찾을 수 없음")
        
        # 결과 분석
        if results:
            print(f"\n🎯 실제 결과 분석 (총 {len(results)}개)")
            print("=" * 60)
            
            # F1 score 분포
            f1_scores = [r['validation_f1'] for r in results]
            acc_scores = [r['validation_acc'] for r in results]
            
            print(f"F1 Score 범위: {min(f1_scores):.4f} ~ {max(f1_scores):.4f}")
            print(f"Accuracy 범위: {min(acc_scores):.4f} ~ {max(acc_scores):.4f}")
            
            # 동일한 값들이 있는지 확인
            unique_f1 = len(set(f'{f:.4f}' for f in f1_scores))
            unique_acc = len(set(f'{a:.4f}' for a in acc_scores))
            
            print(f"고유한 F1 값: {unique_f1}개")
            print(f"고유한 Accuracy 값: {unique_acc}개")
            
            if unique_f1 == 1 and unique_acc == 1:
                print("⚠️ 모든 실험이 정말로 동일한 성능을 보임!")
            else:
                print("✅ 실험들이 서로 다른 성능을 보임 - 정상!")
            
            # 상위 성능 실험들
            print(f"\n🏆 상위 성능 실험들:")
            sorted_results = sorted(results, key=lambda x: x['validation_f1'], reverse=True)
            for i, result in enumerate(sorted_results[:5]):
                print(f"   {i+1}. {result['experiment_id']}")
                print(f"      F1: {result['validation_f1']:.4f}, Acc: {result['validation_acc']:.4f}")
                print(f"      모델: {result['model']}, 손실: {result['criterion']}")
            
            # 결과를 JSON으로 저장
            with open('actual_experiment_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 결과가 actual_experiment_results.json에 저장됨")
        
        else:
            print("\n❌ W&B에서 실제 결과를 찾을 수 없습니다.")
            print("   다른 방법으로 확인해보겠습니다...")
            
            # W&B 프로젝트 목록 확인
            try:
                entity = api.default_entity
                projects = api.projects(entity)
                print(f"\n📋 {entity}의 W&B 프로젝트들:")
                for project in projects[:10]:  # 최근 10개만
                    print(f"   - {project.name}")
            except:
                pass
                
    except ImportError:
        print("❌ W&B가 설치되지 않았습니다.")
        print("   설치: pip install wandb")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def check_log_files():
    """기존 로그 파일들에서 패턴 확인"""
    print(f"\n📋 기존 로그 파일 패턴 확인")
    print("=" * 40)
    
    logs_dir = Path("experiments/logs")
    if not logs_dir.exists():
        print("❌ logs 디렉토리를 찾을 수 없습니다.")
        return
    
    hardcoded_pattern = {"f1": 0.85, "acc": 0.87, "epochs": 30}
    hardcoded_count = 0
    different_count = 0
    
    for log_file in logs_dir.glob("*.json"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('success') and 'local_results' in data:
                results = data['local_results']
                
                f1 = results.get('validation_f1')
                acc = results.get('validation_acc') 
                epochs = results.get('total_epochs')
                
                if (f1 == hardcoded_pattern["f1"] and 
                    acc == hardcoded_pattern["acc"] and
                    epochs == hardcoded_pattern["epochs"]):
                    hardcoded_count += 1
                    print(f"🚫 하드코딩: {log_file.name}")
                else:
                    different_count += 1
                    print(f"✅ 다른 값: {log_file.name} (F1:{f1}, Acc:{acc})")
                    
        except Exception as e:
            print(f"❌ {log_file.name} 읽기 실패: {e}")
    
    print(f"\n📊 로그 파일 분석:")
    print(f"   하드코딩된 로그: {hardcoded_count}개")
    print(f"   다른 값의 로그: {different_count}개")

if __name__ == "__main__":
    check_wandb_results()
    check_log_files()
    
    print(f"\n🎯 다음 단계:")
    print("1. W&B 대시보드에서 직접 확인")
    print("2. 수정된 auto_experiment_runner.py로 새 실험 실행")
    print("3. 실제 결과가 다르게 나오는지 검증")
