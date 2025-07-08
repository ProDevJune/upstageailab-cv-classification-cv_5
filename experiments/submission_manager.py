#!/usr/bin/env python3
"""
제출 관리 시스템 (OCR 지원 버전)
실험 결과의 제출 상태를 관리하고 서버 결과를 추적합니다.
"""

import os
import sys
import json
import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd


@dataclass
class SubmissionInfo:
    """제출 정보를 담는 데이터 클래스 (OCR 지원)"""
    experiment_id: str
    model_name: str
    technique_name: str
    ocr_enabled: bool
    local_f1: float
    local_acc: float
    csv_path: str
    memo: str
    submission_ready: bool
    submitted: bool = False
    server_score: Optional[float] = None
    server_rank: Optional[int] = None
    performance_gap: Optional[float] = None


class SubmissionManager:
    """제출 관리 클래스 (OCR 지원)"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "experiments" / "logs"
        self.submissions_dir = self.base_dir / "experiments" / "submissions"
        
        # 모든 실험 결과 로드
        self.experiment_results = self._load_all_experiment_results()
    
    def _load_all_experiment_results(self) -> List[Dict]:
        """모든 실험 결과 JSON 파일들을 로드"""
        results = []
        
        if not self.logs_dir.exists():
            return results
        
        for log_file in self.logs_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    result_data = json.load(f)
                    results.append(result_data)
            except Exception as e:
                print(f"⚠️  로그 파일 로드 실패 {log_file}: {e}")
        
        return results
    
    def _get_submission_info_list(self) -> List[SubmissionInfo]:
        """제출 가능한 실험들의 정보 리스트 생성"""
        submissions = []
        
        for result in self.experiment_results:
            # 성공한 실험만 처리
            if not result.get('success', False):
                continue
            
            local_results = result.get('local_results', {})
            submission_data = result.get('submission', {})
            memo_data = result.get('memo_suggestion', {})
            server_data = result.get('server_evaluation', {})
            
            if not submission_data.get('submission_ready', False):
                continue
            
            # OCR 정보 추출
            ocr_enabled = False
            if 'ocr' in result:
                ocr_enabled = result['ocr'].get('enabled', False)
            elif 'ocr_enabled' in result:
                ocr_enabled = result['ocr_enabled']
            elif '_ocr_' in result['experiment_id']:
                ocr_enabled = True
            
            submission_info = SubmissionInfo(
                experiment_id=result['experiment_id'],
                model_name=result['model'],
                technique_name=result['technique'],
                ocr_enabled=ocr_enabled,
                local_f1=local_results.get('validation_f1', 0.0),
                local_acc=local_results.get('validation_acc', 0.0),
                csv_path=submission_data.get('csv_path', ''),
                memo=memo_data.get('auto_generated', ''),
                submission_ready=submission_data.get('submission_ready', False),
                submitted=server_data.get('submitted', False),
                server_score=server_data.get('server_score'),
                server_rank=server_data.get('server_rank'),
                performance_gap=server_data.get('performance_gap')
            )
            
            submissions.append(submission_info)
        
        return submissions
    
    def list_pending_submissions(self) -> List[SubmissionInfo]:
        """제출 대기 중인 실험들을 F1 점수 순으로 반환"""
        submissions = self._get_submission_info_list()
        
        # 아직 제출하지 않은 것들만 필터링
        pending = [s for s in submissions if not s.submitted]
        
        # F1 점수 순으로 정렬 (내림차순)
        pending.sort(key=lambda x: x.local_f1, reverse=True)
        
        return pending
    
    def list_pending_by_ocr(self) -> Dict[str, List[SubmissionInfo]]:
        """OCR 적용 여부별로 제출 대기 목록 분류"""
        pending = self.list_pending_submissions()
        
        ocr_submissions = [s for s in pending if s.ocr_enabled]
        no_ocr_submissions = [s for s in pending if not s.ocr_enabled]
        
        return {
            'ocr_enabled': ocr_submissions,
            'ocr_disabled': no_ocr_submissions
        }
    
    def get_submission_info(self, experiment_id: str) -> Optional[SubmissionInfo]:
        """특정 실험의 제출 정보 반환"""
        submissions = self._get_submission_info_list()
        
        for submission in submissions:
            if submission.experiment_id == experiment_id:
                return submission
        
        return None
    
    def add_server_result(self, experiment_id: str, score: float, 
                         rank: int, notes: str = "") -> bool:
        """서버 채점 결과 추가"""
        # 해당 실험의 로그 파일 찾기
        log_file = self.logs_dir / f"{experiment_id}.json"
        
        if not log_file.exists():
            print(f"❌ 실험 로그 파일을 찾을 수 없습니다: {experiment_id}")
            return False
        
        try:
            # 기존 결과 로드
            with open(log_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            
            # 서버 결과 업데이트
            server_evaluation = result_data.get('server_evaluation', {})
            server_evaluation.update({
                'submitted': True,
                'submission_date': datetime.now().isoformat(),
                'server_score': score,
                'server_rank': rank,
                'notes': notes
            })
            
            # 성능 차이 계산
            local_f1 = result_data.get('local_results', {}).get('validation_f1', 0.0)
            if local_f1 > 0:
                performance_gap = score - local_f1
                server_evaluation['performance_gap'] = performance_gap
            
            result_data['server_evaluation'] = server_evaluation
            
            # 파일 업데이트
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            # OCR 정보 표시
            ocr_info = ""
            if 'ocr' in result_data and result_data['ocr'].get('enabled', False):
                ocr_info = " (OCR 적용)"
            elif '_ocr_' in experiment_id:
                ocr_info = " (OCR 적용)"
            
            print(f"✅ 서버 결과가 추가되었습니다: {experiment_id}{ocr_info}")
            print(f"   🏆 서버 점수: {score:.4f}")
            print(f"   📊 순위: {rank}")
            if local_f1 > 0:
                gap = score - local_f1
                gap_str = f"+{gap:.4f}" if gap >= 0 else f"{gap:.4f}"
                print(f"   📈 성능 차이: {gap_str} (로컬 대비)")
            
            return True
            
        except Exception as e:
            print(f"❌ 서버 결과 추가 실패: {e}")
            return False
    
    def print_pending_list(self):
        """제출 대기 목록 출력 (OCR 정보 포함)"""
        pending = self.list_pending_submissions()
        
        if not pending:
            print("📭 제출 대기 중인 실험이 없습니다.")
            return
        
        print(f"📋 제출 대기 중인 실험 ({len(pending)}개)")
        print("=" * 110)
        print(f"{'순위':<4} {'실험 ID':<30} {'모델':<15} {'기법':<12} {'OCR':<5} {'F1 점수':<8} {'정확도':<8} {'메모':<25}")
        print("-" * 110)
        
        for i, submission in enumerate(pending, 1):
            ocr_status = "🔤" if submission.ocr_enabled else "📷"
            print(f"{i:<4} {submission.experiment_id:<30} {submission.model_name:<15} "
                  f"{submission.technique_name:<12} {ocr_status:<5} {submission.local_f1:<8.4f} "
                  f"{submission.local_acc:<8.4f} {submission.memo:<25}")
        
        print("-" * 110)
        print(f"🏆 최고 성능: {pending[0].experiment_id} (F1: {pending[0].local_f1:.4f})")
        
        # OCR별 통계
        ocr_pending = [s for s in pending if s.ocr_enabled]
        no_ocr_pending = [s for s in pending if not s.ocr_enabled]
        print(f"🔤 OCR 적용: {len(ocr_pending)}개")
        print(f"📷 OCR 미적용: {len(no_ocr_pending)}개")
    
    def print_pending_by_ocr(self):
        """OCR별 제출 대기 목록 출력"""
        ocr_groups = self.list_pending_by_ocr()
        
        print("🔤 OCR 적용 실험들:")
        print("-" * 80)
        if ocr_groups['ocr_enabled']:
            for i, submission in enumerate(ocr_groups['ocr_enabled'][:5], 1):
                print(f"   {i}. {submission.experiment_id}")
                print(f"      {submission.model_name} + {submission.technique_name}")
                print(f"      F1: {submission.local_f1:.4f}")
        else:
            print("   없음")
        
        print("\n📷 OCR 미적용 실험들:")
        print("-" * 80)
        if ocr_groups['ocr_disabled']:
            for i, submission in enumerate(ocr_groups['ocr_disabled'][:5], 1):
                print(f"   {i}. {submission.experiment_id}")
                print(f"      {submission.model_name} + {submission.technique_name}")
                print(f"      F1: {submission.local_f1:.4f}")
        else:
            print("   없음")
    
    def print_submission_info(self, experiment_id: str):
        """특정 실험의 제출 정보 출력 (OCR 정보 포함)"""
        submission = self.get_submission_info(experiment_id)
        
        if not submission:
            print(f"❌ 실험을 찾을 수 없습니다: {experiment_id}")
            return
        
        ocr_icon = "🔤" if submission.ocr_enabled else "📷"
        print(f"📊 실험 제출 정보: {ocr_icon} {experiment_id}")
        print("=" * 70)
        print(f"🤖 모델: {submission.model_name}")
        print(f"🔧 기법: {submission.technique_name}")
        print(f"🔤 OCR: {'적용됨' if submission.ocr_enabled else '미적용'}")
        print(f"📈 로컬 F1 점수: {submission.local_f1:.4f}")
        print(f"📈 로컬 정확도: {submission.local_acc:.4f}")
        print(f"📄 CSV 파일: {submission.csv_path}")
        print(f"📝 제출 메모: {submission.memo}")
        print(f"📋 제출 준비: {'✅ 완료' if submission.submission_ready else '❌ 미완료'}")
        
        if submission.submitted:
            print(f"🏆 서버 점수: {submission.server_score:.4f}")
            print(f"🥇 서버 순위: {submission.server_rank}")
            if submission.performance_gap is not None:
                gap_str = f"+{submission.performance_gap:.4f}" if submission.performance_gap >= 0 else f"{submission.performance_gap:.4f}"
                print(f"📊 성능 차이: {gap_str}")
        else:
            print(f"📤 제출 상태: 대기 중")
        
        print("=" * 70)
        print("📋 제출 명령어:")
        print(f"   CSV 파일 경로: {submission.csv_path}")
        print(f"   제출 메모: {submission.memo}")


def main():
    parser = argparse.ArgumentParser(description='제출 관리 시스템 (OCR 지원)')
    parser.add_argument('--base-dir', '-d',
                       default='',
                       help='프로젝트 기본 디렉토리')
    
    # 서브커맨드 설정
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # 제출 대기 목록
    subparsers.add_parser('list-pending', help='제출 대기 중인 실험들을 F1 점수 순으로 표시')
    
    # OCR별 제출 대기 목록
    subparsers.add_parser('list-pending-ocr', help='OCR별로 제출 대기 목록 표시')
    
    # 특정 실험 정보
    info_parser = subparsers.add_parser('get-submission-info', help='특정 실험의 CSV 경로와 제출 메모 출력')
    info_parser.add_argument('experiment_id', help='실험 ID')
    
    # 서버 결과 추가
    server_parser = subparsers.add_parser('add-server-result', help='서버 채점 결과 추가')
    server_parser.add_argument('--experiment', required=True, help='실험 ID')
    server_parser.add_argument('--score', type=float, required=True, help='서버 점수')
    server_parser.add_argument('--rank', type=int, required=True, help='서버 순위')
    server_parser.add_argument('--notes', default='', help='추가 메모')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # 제출 관리자 초기화
        manager = SubmissionManager(args.base_dir)
        
        if args.command == 'list-pending':
            manager.print_pending_list()
            
        elif args.command == 'list-pending-ocr':
            manager.print_pending_by_ocr()
            
        elif args.command == 'get-submission-info':
            manager.print_submission_info(args.experiment_id)
            
        elif args.command == 'add-server-result':
            success = manager.add_server_result(
                args.experiment, args.score, args.rank, args.notes
            )
            if not success:
                sys.exit(1)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
