#!/usr/bin/env python3
"""
개선된 train.csv 기반 2개 모델 앙상블 (v2)
EfficientNet-B4 + B3 최적화 조합
"""
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import os

def find_latest_experiment_results():
    """최신 실험 결과 자동 탐지"""
    submissions_dir = Path("data/submissions")
    
    # 새 실험 결과 패턴 찾기 (v2 태그 또는 최신 타임스탬프)
    experiment_patterns = {
        'efficientnet_b4': None,
        'efficientnet_b3': None
    }
    
    if submissions_dir.exists():
        for item in submissions_dir.iterdir():
            if item.is_dir():
                dir_name = item.name
                # EfficientNet-B4 찾기
                if 'efficientnet_b4' in dir_name and 'img320' in dir_name and 'onaug_eda' in dir_name:
                    csv_files = list(item.glob("*.csv"))
                    if csv_files:
                        experiment_patterns['efficientnet_b4'] = {
                            'path': csv_files[0],
                            'exp_id': dir_name.split('-')[0],
                            'dir_name': dir_name
                        }
                
                # EfficientNet-B3 찾기
                elif 'efficientnet_b3' in dir_name and 'img320' in dir_name and 'onaug_eda' in dir_name:
                    csv_files = list(item.glob("*.csv"))
                    if csv_files:
                        experiment_patterns['efficientnet_b3'] = {
                            'path': csv_files[0],
                            'exp_id': dir_name.split('-')[0],
                            'dir_name': dir_name
                        }
    
    return experiment_patterns

def create_2model_ensemble_v2():
    """개선된 데이터 기반 B4 + B3 앙상블"""
    
    print("🎪 개선된 train.csv 기반 2모델 앙상블 v2")
    print("=" * 60)
    
    # 최신 실험 결과 자동 탐지
    experiments = find_latest_experiment_results()
    
    if not experiments['efficientnet_b4'] or not experiments['efficientnet_b3']:
        print("❌ 필요한 실험 결과를 찾을 수 없습니다.")
        print("   다음을 먼저 실행하세요:")
        print("   1. ./run_absolute.sh (EfficientNet-B4)")
        print("   2. ./run_b3.sh (EfficientNet-B3)")
        return None
    
    # 모델 정보 구성
    models = {
        'EfficientNet-B4': {
            'path': experiments['efficientnet_b4']['path'],
            'exp_id': experiments['efficientnet_b4']['exp_id'],
            'weight': 0.65,  # B4에 더 높은 비중
            'expected_improvement': 0.002  # 예상 개선
        },
        'EfficientNet-B3': {
            'path': experiments['efficientnet_b3']['path'],
            'exp_id': experiments['efficientnet_b3']['exp_id'],
            'weight': 0.35,  # B3 보조 역할
            'expected_improvement': 0.001
        }
    }
    
    print("🔍 발견된 실험 결과:")
    
    # 모델별 예측 로드
    predictions = {}
    
    for model_name, model_info in models.items():
        file_path = Path(model_info['path'])
        
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                if 'ID' in df.columns and 'target' in df.columns:
                    predictions[model_name] = df
                    print(f"✅ {model_name}")
                    print(f"   📁 {file_path.parent.name}")
                    print(f"   🆔 실험ID: {model_info['exp_id']}")
                    print(f"   📊 {len(df)}개 예측 (가중치: {model_info['weight']:.1%})")
                else:
                    print(f"❌ {model_name}: 잘못된 CSV 형식")
                    return None
            except Exception as e:
                print(f"❌ {model_name} 로드 실패: {e}")
                return None
        else:
            print(f"❌ {model_name}: 파일 없음")
            return None
    
    if len(predictions) != 2:
        print("❌ 2개 모델을 모두 로드하지 못했습니다.")
        return None
    
    print(f"\\n🎯 앙상블 구성 (개선된 데이터v2):")
    
    # 기준 DataFrame
    base_df = predictions['EfficientNet-B4'][['ID']].copy()
    ensemble_targets = np.zeros(len(base_df))
    
    for model_name, model_info in models.items():
        if model_name in predictions:
            pred_df = predictions[model_name]
            weight = model_info['weight']
            
            # ID 순서 맞추기
            merged = base_df.merge(pred_df[['ID', 'target']], on='ID', how='left')
            
            if merged['target'].isna().any():
                print(f"⚠️ {model_name}: 누락된 예측 {merged['target'].isna().sum()}개")
                continue
            
            ensemble_targets += merged['target'].values * weight
            
            print(f"   🔹 {model_name}: {weight:.1%} (실험ID: {model_info['exp_id']})")
    
    # 최종 결과
    result_df = pd.DataFrame({
        'ID': base_df['ID'],
        'target': ensemble_targets
    })
    
    # 저장
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"ensemble_2models_v2_{timestamp}.csv"
    result_df.to_csv(output_path, index=False)
    
    # 결과 요약
    print(f"\\n✅ 2모델 앙상블 v2 완료!")
    print(f"📁 출력 파일: {output_path}")
    print(f"🆔 사용 실험: {models['EfficientNet-B4']['exp_id']} + {models['EfficientNet-B3']['exp_id']}")
    print(f"💡 대회 제출 메모: '2모델 앙상블 B4+B3 (개선된 데이터v2)'")
    
    # 실행 정보 기록
    result_info = {
        'file_path': output_path,
        'submission_memo': '2모델 앙상블 B4+B3 (개선된 데이터v2)',
        'models_used': f"B4({models['EfficientNet-B4']['exp_id']}) + B3({models['EfficientNet-B3']['exp_id']})",
        'weights': f"B4:{models['EfficientNet-B4']['weight']:.1%}, B3:{models['EfficientNet-B3']['weight']:.1%}",
        'timestamp': timestamp
    }
    
    print(f"\\n📋 제출 정보:")
    print(f"   파일: {result_info['file_path']}")
    print(f"   메모: {result_info['submission_memo']}")
    print(f"   구성: {result_info['models_used']}")
    print(f"   비율: {result_info['weights']}")
    
    return result_info

if __name__ == "__main__":
    create_2model_ensemble_v2()
