#!/usr/bin/env python3
"""
실행 중인 실험을 방해하지 않고 격리 시스템 준비
"""

import os
import json
import shutil
from pathlib import Path
import subprocess

def backup_current_system():
    """현재 시스템 백업"""
    print("🔄 현재 시스템 백업 중...")
    
    # 현재 auto_experiment_runner.py 백업
    original = "experiments/auto_experiment_runner.py"
    backup = "experiments/auto_experiment_runner_backup.py"
    
    if os.path.exists(original):
        shutil.copy2(original, backup)
        print(f"✅ {original} -> {backup}")
    
    # 현재 실험 큐 백업
    queue_file = "experiments/experiment_queue.json"
    if os.path.exists(queue_file):
        backup_queue = f"experiments/experiment_queue_backup_{int(time.time())}.json"
        shutil.copy2(queue_file, backup_queue)
        print(f"✅ {queue_file} -> {backup_queue}")

def prepare_enhanced_system():
    """향상된 시스템 준비 (실행 중인 실험에 영향 없음)"""
    print("🛠️ 향상된 격리 시스템 준비 중...")
    
    # isolation_utils.py가 이미 생성되었는지 확인
    isolation_file = "experiments/isolation_utils.py"
    if os.path.exists(isolation_file):
        print(f"✅ {isolation_file} 이미 준비됨")
    else:
        print(f"❌ {isolation_file} 없음 - 수동으로 생성 필요")
    
    # 테스트 스크립트 확인
    test_file = "test_isolation.py"
    if os.path.exists(test_file):
        print(f"✅ {test_file} 준비됨")
    else:
        print(f"❌ {test_file} 없음 - 수동으로 생성 필요")

def check_running_experiments():
    """실행 중인 실험 상태 확인"""
    print("🔍 실행 중인 실험 확인...")
    
    # 프로세스 확인
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        running_exp = []
        for line in lines:
            if 'auto_experiment_runner' in line or 'gemini_main_v2' in line:
                running_exp.append(line.strip())
        
        if running_exp:
            print("🏃 실행 중인 프로세스:")
            for proc in running_exp:
                print(f"   {proc}")
        else:
            print("❌ 실행 중인 실험을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"⚠️ 프로세스 확인 실패: {e}")

def analyze_experiment_queue():
    """실험 큐 분석"""
    print("📊 실험 큐 분석...")
    
    queue_file = "experiments/experiment_queue.json"
    if not os.path.exists(queue_file):
        print(f"❌ {queue_file} 없음")
        return
    
    try:
        with open(queue_file, 'r') as f:
            queue_data = json.load(f)
        
        experiments = queue_data.get('experiments', [])
        
        completed = [exp for exp in experiments if exp['status'] == 'completed']
        running = [exp for exp in experiments if exp['status'] == 'running']
        pending = [exp for exp in experiments if exp['status'] == 'pending']
        failed = [exp for exp in experiments if exp['status'] == 'failed']
        
        print(f"   📈 완료: {len(completed)}개")
        print(f"   🏃 실행 중: {len(running)}개")
        print(f"   ⏳ 대기: {len(pending)}개")
        print(f"   ❌ 실패: {len(failed)}개")
        
        if running:
            print(f"   🔄 현재 실행: {running[0]['experiment_id']}")
        
        return {
            'total': len(experiments),
            'completed': len(completed),
            'running': len(running),
            'pending': len(pending),
            'failed': len(failed)
        }
        
    except Exception as e:
        print(f"⚠️ 큐 분석 실패: {e}")

def recommend_action():
    """권장 행동 제시"""
    print("\n💡 권장 행동:")
    
    stats = analyze_experiment_queue()
    if not stats:
        return
    
    if stats['running'] > 0:
        print("✅ 현재 실험이 실행 중입니다.")
        print("   🔸 실험이 완료될 때까지 기다리세요")
        print("   🔸 병렬로 다음 실험을 위한 개선 작업을 진행하세요")
        print("   🔸 --resume 옵션으로 나중에 개선된 시스템을 적용하세요")
    
    if stats['pending'] > 0:
        print(f"⏳ {stats['pending']}개 실험이 대기 중입니다.")
        print("   🔸 다음 실험부터 개선된 격리 시스템이 적용됩니다")
    
    completion_rate = stats['completed'] / stats['total'] * 100
    print(f"📊 진행률: {completion_rate:.1f}% ({stats['completed']}/{stats['total']})")

if __name__ == "__main__":
    print("🔍 현재 실험 상황 분석")
    print("=" * 50)
    
    check_running_experiments()
    print()
    
    analyze_experiment_queue()
    print()
    
    backup_current_system()
    print()
    
    prepare_enhanced_system()
    print()
    
    recommend_action()
