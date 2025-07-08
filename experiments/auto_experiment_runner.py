#!/usr/bin/env python3
"""
자동 실험 실행기
생성된 실험 큐를 순차적으로 실행하고 결과를 기록합니다.
"""

import os
import sys
import json
import subprocess
import time
import gc
import psutil
import torch
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback
from tqdm import tqdm

# 실험 격리 유틸리티 추가
from isolation_utils import (
    setup_experiment_isolation,
    cleanup_experiment_temp_dirs,
    validate_system_state,
    deep_cleanup,
    wait_for_system_stability,
    ExperimentIsolationContext
)


class GPUMemoryManager:
    """GPU 메모리 관리 클래스"""
    
    @staticmethod
    def clear_gpu_memory():
        """GPU 메모리 완전 정리"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            gc.collect()
    
    @staticmethod
    def get_gpu_memory_info():
        """GPU 메모리 사용량 정보 반환"""
        if not torch.cuda.is_available():
            return "GPU not available"
        
        device = torch.cuda.current_device()
        total = torch.cuda.get_device_properties(device).total_memory / 1024**3
        allocated = torch.cuda.memory_allocated(device) / 1024**3
        cached = torch.cuda.memory_reserved(device) / 1024**3
        
        return f"GPU Memory - Total: {total:.1f}GB, Allocated: {allocated:.1f}GB, Cached: {cached:.1f}GB"


class ExperimentRunner:
    """자동 실험 실행 관리 클래스"""
    
    def __init__(self, queue_file: str, resume: bool = False):
        self.queue_file = queue_file
        self.base_dir = Path(queue_file).parent.parent
        self.logs_dir = self.base_dir / "experiments" / "logs"
        self.submissions_dir = self.base_dir / "experiments" / "submissions"
        self.resume = resume
        
        # 실험 큐 로드
        self.queue_data = self._load_queue()
        self.experiments = self.queue_data['experiments']
        
        # 진행 상황 추적
        self.completed_experiments = []
        self.failed_experiments = []
        self.current_experiment = None
        self.start_time = None
        
    def _load_queue(self) -> Dict:
        """실험 큐 파일 로드"""
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"실험 큐 파일 로드 실패: {e}")
    
    def _save_queue(self):
        """실험 큐 상태 저장"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.queue_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  큐 상태 저장 실패: {e}")
    
    def _check_resume_status(self) -> int:
        """중단된 실험이 있는지 확인하고 시작 지점 반환"""
        if not self.resume:
            return 0
        
        completed_count = 0
        for i, exp in enumerate(self.experiments):
            if exp['status'] == 'completed':
                completed_count += 1
            elif exp['status'] == 'running':
                # 실행 중이던 실험을 pending으로 되돌림
                exp['status'] = 'pending'
                self._save_queue()
                break
            elif exp['status'] == 'pending':
                break
        
        if completed_count > 0:
            print(f"🔄 Resume 모드: {completed_count}개 실험 완료됨, {completed_count + 1}번째부터 시작")
        
        return completed_count
    
    def _update_experiment_status(self, experiment_id: str, status: str, 
                                additional_info: Dict = None):
        """실험 상태 업데이트"""
        for exp in self.experiments:
            if exp['experiment_id'] == experiment_id:
                exp['status'] = status
                exp['last_updated'] = datetime.now().isoformat()
                
                if additional_info:
                    exp.update(additional_info)
                break
        
        self._save_queue()
    
    def _generate_memo_suggestion(self, model_name: str, technique_name: str, 
                                config_path: str) -> Dict:
        """제출용 메모 자동 생성 (OCR 지원)"""
        
        # 모델명 축약
        model_abbrev = {
            'swin_transformer': 'SwinB384',
            'efficientnet_b4': 'EffNetB4',
            'convnext_base': 'ConvNeXtB',
            'maxvit_base': 'MaxViTB384'
        }.get(model_name, model_name[:10])
        
        # 기법 축약
        technique_abbrev = {
            'baseline': 'Base',
            'focal_loss': 'Focal',
            'mixup_cutmix': 'Mix50%',
            'focal_mixup': 'Focal+Mix50%',
            'label_smooth': 'LabelSmooth',
            'label_mixup': 'LabelSmooth+Mix50%'
        }.get(technique_name, technique_name[:10])
        
        # 기본 메모 생성
        base_memo = f"{model_abbrev}+{technique_abbrev}"
        
        # 설정 파일에서 추가 정보 추출
        ocr_enabled = False
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # OCR 정보 확인
            if 'ocr' in config and config['ocr'].get('enabled', False):
                ocr_enabled = True
                ocr_model = config['ocr'].get('ocr_model', 'OCR')
                if ocr_model == 'OCR':
                    base_memo += "+OCR"
                else:
                    base_memo += f"+{ocr_model}"
            
            # TTA 정보 추가
            if config.get('test_TTA', False):
                base_memo += "+TTA"
            
            # Focal Loss 파라미터 추가
            if 'focal' in technique_name and 'focal_loss' in config:
                alpha = config['focal_loss'].get('alpha', 1.0)
                gamma = config['focal_loss'].get('gamma', 2.0)
                if alpha != 1.0 or gamma != 2.0:
                    base_memo += f"(α{alpha},γ{gamma})"
                    
        except Exception:
            pass
        
        # 50자 제한 확인
        if len(base_memo) > 50:
            # 지능적 축약
            if "+TTA" in base_memo:
                base_memo = base_memo.replace("+TTA", "")
            if len(base_memo) > 50:
                base_memo = base_memo[:47] + "..."
        
        # 대안 메모들 생성
        ocr_suffix = " OCR" if ocr_enabled else ""
        alternatives = [
            f"{model_abbrev} {technique_abbrev}{ocr_suffix}",
            f"{model_name.split('_')[0]} + {technique_name}{ocr_suffix}",
            f"Auto: {model_abbrev}+{technique_abbrev}{ocr_suffix}"
        ]
        
        alternatives = [alt for alt in alternatives if len(alt) <= 50 and alt != base_memo]
        
        return {
            'auto_generated': base_memo,
            'character_count': len(base_memo),
            'alternatives': alternatives[:3]
        }
    
    def _create_experiment_result_log(self, experiment: Dict, 
                                    success: bool, error_msg: str = None, 
                                    actual_results: Dict = None) -> str:
        """실험 결과 JSON 로그 생성 (실제 결과 파싱 지원)"""
        experiment_id = experiment['experiment_id']
        log_file = self.logs_dir / f"{experiment_id}.json"
        
        # 기본 결과 구조
        result_data = {
            "experiment_id": experiment_id,
            "timestamp": datetime.now().isoformat(),
            "model": experiment['model_name'],
            "technique": experiment['technique_name'],
            "config_path": experiment['config_path'],
            "description": experiment['description'],
            "success": success
        }
        
        if success:
            # 성공적인 실험 결과 처리
            try:
                # 실제 결과가 전달된 경우 사용, 없으면 파싱 시도
                if actual_results:
                    local_results = actual_results
                else:
                    local_results = self._parse_experiment_results(experiment_id)
                
                result_data.update({
                    "local_results": local_results,
                    "submission": {
                        "csv_path": str(self.submissions_dir / f"{experiment_id}_submission.csv"),
                        "submission_ready": True,
                        "file_size_mb": 2.5,  # placeholder
                        "created_at": datetime.now().isoformat()
                    },
                    "memo_suggestion": self._generate_memo_suggestion(
                        experiment['model_name'], 
                        experiment['technique_name'],
                        experiment['config_path']
                    ),
                    "server_evaluation": {
                        "submitted": False,
                        "submission_date": None,
                        "server_score": None,
                        "server_rank": None,
                        "notes": "",
                        "performance_gap": None
                    }
                })
            except Exception as e:
                print(f"⚠️  결과 파싱 중 오류: {e}")
                result_data["parsing_error"] = str(e)
        else:
            # 실패한 실험 처리
            result_data.update({
                "error_message": error_msg,
                "local_results": None,
                "submission": {
                    "csv_path": None,
                    "submission_ready": False,
                    "file_size_mb": 0,
                    "created_at": None
                },
                "memo_suggestion": None,
                "server_evaluation": None
            })
        
        # JSON 파일 저장
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        return str(log_file)
    
    def _parse_experiment_results(self, experiment_id: str) -> Dict:
        """실험 결과 파싱 (다양한 소스에서 실제 결과 추출)"""
        try:
            # 1. W&B 로그에서 결과 추출 시도
            wandb_results = self._parse_wandb_results(experiment_id)
            if wandb_results:
                return wandb_results
            
            # 2. 제출 파일 CSV에서 메타데이터 추출
            submission_results = self._parse_submission_metadata(experiment_id)
            if submission_results:
                return submission_results
            
            # 3. 로그 파일에서 추출
            log_results = self._parse_console_logs(experiment_id)
            if log_results:
                return log_results
            
            # 4. 모델 체크포인트 메타데이터에서 추출
            checkpoint_results = self._parse_checkpoint_metadata(experiment_id)
            if checkpoint_results:
                return checkpoint_results
            
            print(f"⚠️ 경고: {experiment_id}의 실제 결과를 찾을 수 없습니다. 기본값 사용.")
            
        except Exception as e:
            print(f"⚠️ 결과 파싱 오류: {e}")
        
        # 기본값 반환 (파싱 실패 시)
        return {
            "validation_f1": None,
            "validation_acc": None,
            "training_time_minutes": None,
            "total_epochs": None,
            "early_stopped": None,
            "parsing_failed": True,
            "note": "Results parsing failed - may need manual verification"
        }
    
    def _parse_wandb_results(self, experiment_id: str) -> Dict:
        """웹드앤비 로그에서 결과 추출"""
        try:
            import wandb
            api = wandb.Api()
            
            # 실험 ID로 W&B 런 찾기
            runs = api.runs(f"auto-exp-ocr-{experiment_id}", 
                          filters={"state": "finished"})
            
            if runs:
                run = runs[0]  # 가장 최근 런
                
                # 메트릭 추출
                summary = run.summary
                history = run.history()
                
                validation_f1 = summary.get('val_f1', summary.get('validation_f1', None))
                validation_acc = summary.get('val_acc', summary.get('validation_acc', None))
                
                # 학습 시간 계산
                if run.created_at and run.updated_at:
                    training_time = (run.updated_at - run.created_at).total_seconds() / 60
                else:
                    training_time = None
                
                return {
                    "validation_f1": float(validation_f1) if validation_f1 else None,
                    "validation_acc": float(validation_acc) if validation_acc else None,
                    "training_time_minutes": int(training_time) if training_time else None,
                    "total_epochs": summary.get('epoch', None),
                    "early_stopped": summary.get('early_stopped', None),
                    "wandb_run_id": run.id,
                    "source": "wandb"
                }
                
        except Exception as e:
            print(f"🔍 W&B 파싱 오류: {e}")
            return None
    
    def _parse_submission_metadata(self, experiment_id: str) -> Dict:
        """제출 파일 CSV 메타데이터에서 결과 추출"""
        try:
            submission_file = self.submissions_dir / f"{experiment_id}_submission.csv"
            if submission_file.exists():
                # CSV 파일 메타데이터 또는 동반 JSON 파일 확인
                metadata_file = submission_file.with_suffix('.json')
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        return {
                            "validation_f1": metadata.get('validation_f1'),
                            "validation_acc": metadata.get('validation_acc'),
                            "training_time_minutes": metadata.get('training_time_minutes'),
                            "total_epochs": metadata.get('total_epochs'),
                            "early_stopped": metadata.get('early_stopped'),
                            "source": "submission_metadata"
                        }
        except Exception as e:
            print(f"🔍 제출 메타데이터 파싱 오류: {e}")
            return None
    
    def _parse_console_logs(self, experiment_id: str) -> Dict:
        """콘솔 로그에서 결과 추출"""
        try:
            # 체크포인트나 로그 파일에서 최종 결과 찾기
            possible_log_files = [
                self.base_dir / "models" / f"{experiment_id}_best.pth",
                self.base_dir / "logs" / f"{experiment_id}.log",
                self.base_dir / f"{experiment_id}_results.txt"
            ]
            
            for log_file in possible_log_files:
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 정규 표현식으로 결과 추출
                        import re
                        
                        f1_match = re.search(r'(?:val_f1|validation_f1|f1[_\s]*score)[:\s]*([0-9.]+)', content, re.IGNORECASE)
                        acc_match = re.search(r'(?:val_acc|validation_acc|accuracy)[:\s]*([0-9.]+)', content, re.IGNORECASE)
                        epoch_match = re.search(r'(?:epoch|epochs)[:\s]*([0-9]+)', content, re.IGNORECASE)
                        
                        if f1_match or acc_match:
                            return {
                                "validation_f1": float(f1_match.group(1)) if f1_match else None,
                                "validation_acc": float(acc_match.group(1)) if acc_match else None,
                                "training_time_minutes": None,
                                "total_epochs": int(epoch_match.group(1)) if epoch_match else None,
                                "early_stopped": "early" in content.lower(),
                                "source": f"log_file_{log_file.name}"
                            }
                            
        except Exception as e:
            print(f"🔍 로그 파싱 오류: {e}")
            return None
    
    def _parse_checkpoint_metadata(self, experiment_id: str) -> Dict:
        """모델 체크포인트 메타데이터에서 결과 추출"""
        try:
            # PyTorch 모델 체크포인트에서 메타데이터 추출
            checkpoint_paths = [
                self.base_dir / "models" / f"{experiment_id}_best.pth",
                self.base_dir / "checkpoints" / f"{experiment_id}.pth",
                self.base_dir / f"best_model_{experiment_id}.pth"
            ]
            
            for checkpoint_path in checkpoint_paths:
                if checkpoint_path.exists():
                    try:
                        checkpoint = torch.load(checkpoint_path, map_location='cpu')
                        
                        if isinstance(checkpoint, dict):
                            return {
                                "validation_f1": checkpoint.get('val_f1', checkpoint.get('best_f1')),
                                "validation_acc": checkpoint.get('val_acc', checkpoint.get('best_acc')),
                                "training_time_minutes": checkpoint.get('training_time'),
                                "total_epochs": checkpoint.get('epoch'),
                                "early_stopped": checkpoint.get('early_stopped'),
                                "source": f"checkpoint_{checkpoint_path.name}"
                            }
                    except Exception:
                        continue  # 다음 체크포인트 시도
                        
        except Exception as e:
            print(f"🔍 체크포인트 파싱 오류: {e}")
            return None
    
    def _execute_experiment(self, experiment: Dict) -> bool:
        """개선된 단일 실험 실행 (완전 격리)"""
        experiment_id = experiment['experiment_id']
        config_path = experiment['config_path']
        
        print(f"🚀 실험 시작: {experiment_id}")
        print(f"   📄 설정: {config_path}")
        print(f"   📝 설명: {experiment['description']}")
        print(f"   ⏱️  예상 시간: {experiment['estimated_time_minutes']}분")
        
        # 격리된 환경에서 실험 실행
        with ExperimentIsolationContext(experiment_id):
            return self._run_isolated_experiment(experiment)
        
    def _run_isolated_experiment(self, experiment: Dict) -> bool:
        """격리된 환경에서 실험 실행"""
        experiment_id = experiment['experiment_id']
        config_path = experiment['config_path']
        
        # 실험 상태 업데이트
        self._update_experiment_status(experiment_id, 'running', {
            'started_at': datetime.now().isoformat()
        })
        
        try:
            # 격리된 환경 변수 생성
            isolated_env = self._create_isolated_environment(experiment_id)
            
            # gemini_main_v2.py 실행
            main_script = "codes/gemini_main_v2.py"
            cmd = [
                sys.executable, main_script, 
                "--config", config_path,
                "--experiment-id", experiment_id,
                "--isolated-mode"
            ]
            
            print(f"   💻 실행 명령어: {' '.join(cmd)}")
            print(f"   🔒 격리 모드로 실행")
            
            # 실험 실행 (격리된 환경)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=self.base_dir,
                env=isolated_env  # 격리된 환경 적용
            )
            
            # 실시간 출력 및 로그 수집
            output_lines = []
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(f"   📤 {output.strip()}")
                    output_lines.append(output.strip())
            
            # 프로세스 종료 대기
            return_code = process.poll()
            
            if return_code == 0:
                print(f"✅ 실험 성공: {experiment_id}")
                
                # 성공 로그 생성
                log_file = self._create_experiment_result_log(experiment, True)
                print(f"   📊 결과 로그: {log_file}")
                
                # 실험 상태 업데이트
                self._update_experiment_status(experiment_id, 'completed', {
                    'completed_at': datetime.now().isoformat(),
                    'success': True,
                    'log_file': log_file
                })
                
                self.completed_experiments.append(experiment_id)
                return True
            else:
                error_msg = f"프로세스 종료 코드: {return_code}"
                print(f"❌ 실험 실패: {experiment_id} - {error_msg}")
                
                # 실패 로그 생성
                log_file = self._create_experiment_result_log(experiment, False, error_msg)
                print(f"   📋 오류 로그: {log_file}")
                
                # 실험 상태 업데이트
                self._update_experiment_status(experiment_id, 'failed', {
                    'failed_at': datetime.now().isoformat(),
                    'error_message': error_msg,
                    'log_file': log_file
                })
                
                self.failed_experiments.append(experiment_id)
                return False
                
        except Exception as e:
            error_msg = f"실행 중 예외 발생: {str(e)}"
            print(f"❌ 실험 실패: {experiment_id} - {error_msg}")
            print(f"   🔍 상세 오류:\\n{traceback.format_exc()}")
            
            # 실패 로그 생성
            log_file = self._create_experiment_result_log(experiment, False, error_msg)
            
            # 실험 상태 업데이트
            self._update_experiment_status(experiment_id, 'failed', {
                'failed_at': datetime.now().isoformat(),
                'error_message': error_msg,
                'log_file': log_file
            })
            
            self.failed_experiments.append(experiment_id)
            return False
        
        finally:
            # 실험 후 철저한 정리는 ExperimentIsolationContext에서 처리
            pass
    
    def _create_isolated_environment(self, experiment_id: str) -> dict:
        """격리된 환경 변수 생성"""
        env = os.environ.copy()
        
        # 실험별 고유 환경 설정
        env.update({
            'EXPERIMENT_ID': experiment_id,
            'PYTHONHASHSEED': str(hash(experiment_id) % 2**32),
            'CUDA_CACHE_PATH': f"/tmp/cv_experiments/{experiment_id}/cuda_cache",
            'TORCH_HOME': f"/tmp/cv_experiments/{experiment_id}/torch_home",
            'WANDB_DIR': f"/tmp/cv_experiments/{experiment_id}/wandb",
        })
        
        return env
    
    def _calculate_remaining_time(self, completed_count: int) -> str:
        """남은 실험 예상 완료 시간 계산"""
        if not self.start_time or completed_count == 0:
            return "계산 중..."
        
        elapsed_time = datetime.now() - self.start_time
        avg_time_per_experiment = elapsed_time / completed_count
        
        remaining_experiments = len(self.experiments) - completed_count
        remaining_time = avg_time_per_experiment * remaining_experiments
        
        eta = datetime.now() + remaining_time
        return f"{eta.strftime('%Y-%m-%d %H:%M:%S')} (약 {remaining_time})"
    
    def run_all_experiments(self):
        """모든 실험 순차 실행"""
        print("🎯 자동 실험 시스템 시작")
        print("=" * 80)
        
        # Resume 모드 확인
        start_index = self._check_resume_status()
        
        total_experiments = len(self.experiments)
        pending_experiments = [exp for exp in self.experiments[start_index:] if exp['status'] == 'pending']
        
        print(f"📊 총 실험 수: {total_experiments}개")
        print(f"✅ 완료된 실험: {start_index}개")
        print(f"⏳ 대기 중인 실험: {len(pending_experiments)}개")
        print(f"⏱️  예상 총 소요시간: {self.queue_data.get('estimated_total_time_hours', 0):.1f}시간")
        print()
        
        if not pending_experiments:
            print("🎉 모든 실험이 이미 완료되었습니다!")
            return
        
        # 시작 시간 기록
        self.start_time = datetime.now()
        
        # 진행률 표시를 위한 tqdm 설정
        progress_bar = tqdm(
            total=len(pending_experiments),
            desc="실험 진행",
            unit="exp",
            position=0,
            leave=True
        )
        
        success_count = 0
        failure_count = 0
        
        try:
            for i, experiment in enumerate(pending_experiments):
                current_position = start_index + i + 1
                
                print(f"\\n{'='*80}")
                print(f"🧪 실험 {current_position}/{total_experiments}: {experiment['experiment_id']}")
                print(f"⭐ 우선순위: {experiment['priority_score']:.3f}")
                
                # 남은 시간 계산
                remaining_time = self._calculate_remaining_time(success_count + failure_count)
                print(f"⏰ 예상 완료: {remaining_time}")
                print("=" * 80)
                
                # 현재 실험 설정
                self.current_experiment = experiment
                
                # 실험 실행
                success = self._execute_experiment(experiment)
                
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                
                # 진행률 업데이트
                progress_bar.update(1)
                progress_bar.set_postfix({
                    'Success': success_count,
                    'Failed': failure_count,
                    'Current': experiment['experiment_id']
                })
                
                # 실험 간 간격
                print(f"\\n⏸️  다음 실험 준비 중... (5초 대기)")
                time.sleep(5)
        
        except KeyboardInterrupt:
            print(f"\\n\\n⛔ 사용자에 의해 중단됨")
            print(f"✅ 완료된 실험: {success_count}개")
            print(f"❌ 실패한 실험: {failure_count}개")
            print(f"⏸️  중단된 지점에서 재개하려면 --resume 옵션을 사용하세요")
            
        finally:
            progress_bar.close()
            self._print_final_summary(success_count, failure_count)
    
    def _print_final_summary(self, success_count: int, failure_count: int):
        """최종 요약 출력"""
        total_time = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        print("\\n" + "=" * 80)
        print("🏁 자동 실험 시스템 완료!")
        print("=" * 80)
        print(f"⏱️  총 실행 시간: {total_time}")
        print(f"✅ 성공한 실험: {success_count}개")
        print(f"❌ 실패한 실험: {failure_count}개")
        print(f"📊 성공률: {success_count/(success_count+failure_count)*100:.1f}%" if (success_count+failure_count) > 0 else "📊 성공률: 0%")
        print()
        
        if self.completed_experiments:
            print("🎯 완료된 실험들:")
            for exp_id in self.completed_experiments:
                print(f"   ✅ {exp_id}")
            print()
        
        if self.failed_experiments:
            print("⚠️  실패한 실험들:")
            for exp_id in self.failed_experiments:
                print(f"   ❌ {exp_id}")
            print()
        
        print("📋 다음 단계:")
        print("   1. 결과 분석: python experiments/results_analyzer.py")
        print("   2. 제출 관리: python experiments/submission_manager.py --list-pending")
        print("   3. 실시간 모니터링: python experiments/experiment_monitor.py")


def main():
    parser = argparse.ArgumentParser(description='자동 실험 실행기')
    parser.add_argument('--queue', '-q',
                       default='experiments/experiment_queue.json',
                       help='실험 큐 JSON 파일 경로')
    parser.add_argument('--resume', '-r', action='store_true',
                       help='중단된 지점부터 실험 재개')
    parser.add_argument('--dry-run', action='store_true',
                       help='실제 실험 실행 없이 시뮬레이션만 실행')
    
    args = parser.parse_args()
    
    try:
        # 실험 실행기 초기화
        runner = ExperimentRunner(args.queue, args.resume)
        
        if args.dry_run:
            print("🧪 DRY RUN 모드: 실제 실험을 실행하지 않습니다.")
            print(f"📋 총 {len(runner.experiments)}개 실험이 준비되어 있습니다.")
            return
        
        # 자동 실험 시작
        runner.run_all_experiments()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print(f"🔍 상세 오류:\\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
