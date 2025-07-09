"""
gemini_main_v2.py WandB 초기화 수정
기존 파일을 수정하여 모델별 프로젝트 구조 적용
"""

def init_wandb_for_experiment_v2(cfg, experiment_type="automated"):
    """
    확장 가능한 실험 시스템용 WandB 초기화
    모델명을 프로젝트명으로 사용하는 새로운 구조
    """
    if not (hasattr(cfg, 'wandb') and cfg.wandb['log']):
        return None
    
    # 모델명을 프로젝트명으로 설정 (핵심 변경)
    project_name = cfg.model_name.replace('.', '_').replace('-', '_')
    
    # 실험 ID 기반 run 이름 생성
    if hasattr(cfg, 'experiment_id'):
        run_name = cfg.experiment_id
    else:
        # 기존 방식 fallback
        from datetime import datetime
        from zoneinfo import ZoneInfo
        timestamp = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%y%m%d%H%M")
        run_name = f"{timestamp}_{cfg.model_name}_{experiment_type}"
    
    # 태그 생성
    tags = [cfg.model_name, experiment_type, "hyperparameter_system"]
    if hasattr(cfg, 'category_type'):
        tags.append(cfg.category_type)
    
    print(f"🎯 WandB 초기화:")
    print(f"   프로젝트: {project_name}")
    print(f"   Run: {run_name}")
    print(f"   태그: {tags}")
    
    # WandB 초기화
    import wandb
    run = wandb.init(
        project=project_name,  # ← 핵심: 모델명이 프로젝트명
        name=run_name,         # ← 실험별 체계화된 이름
        config=vars(cfg),
        tags=tags
    )
    
    return run

# 기존 gemini_main_v2.py에서 WandB 초기화 부분을 다음과 같이 수정:
"""
기존 코드:
if hasattr(cfg, 'wandb') and cfg.wandb['log']:
    run = wandb.init(
        project=cfg.wandb['project'],
        name=next_run_name,
        config=vars(cfg),
    )

수정 후:
run = init_wandb_for_experiment_v2(cfg, experiment_type="automated")
"""
