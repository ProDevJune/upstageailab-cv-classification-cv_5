#!/usr/bin/env python3
"""
실험 결과 분석기
완료된 모든 실험 결과를 종합 분석하고 리포트를 생성합니다.
"""

import os
import sys
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import matplotlib.pyplot as plt
import seaborn as sns


@dataclass
class ExperimentResult:
    """실험 결과를 담는 데이터 클래스"""
    experiment_id: str
    model: str
    technique: str
    local_f1: float
    local_acc: float
    training_time: float
    success: bool
    server_score: Optional[float] = None
    server_rank: Optional[int] = None
    performance_gap: Optional[float] = None


class ResultsAnalyzer:
    """실험 결과 분석 클래스"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / "experiments" / "logs"
        self.results = self._load_all_results()
        
    def _load_all_results(self) -> List[ExperimentResult]:
        """모든 실험 결과를 로드"""
        results = []
        
        if not self.logs_dir.exists():
            print("⚠️  로그 디렉토리가 존재하지 않습니다.")
            return results
        
        for log_file in self.logs_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                local_results = data.get('local_results', {})
                server_eval = data.get('server_evaluation', {})
                
                result = ExperimentResult(
                    experiment_id=data['experiment_id'],
                    model=data['model'],
                    technique=data['technique'],
                    local_f1=local_results.get('validation_f1', 0.0),
                    local_acc=local_results.get('validation_acc', 0.0),
                    training_time=local_results.get('training_time_minutes', 0.0),
                    success=data.get('success', False),
                    server_score=server_eval.get('server_score'),
                    server_rank=server_eval.get('server_rank'),
                    performance_gap=server_eval.get('performance_gap')
                )
                
                results.append(result)
                
            except Exception as e:
                print(f"⚠️  로그 파일 로드 실패 {log_file}: {e}")
        
        return results
    
    def get_success_results(self) -> List[ExperimentResult]:
        """성공한 실험들만 반환"""
        return [r for r in self.results if r.success]
    
    def generate_model_technique_matrix(self) -> pd.DataFrame:
        """모델별 기법 효과성 매트릭스 생성"""
        success_results = self.get_success_results()
        
        if not success_results:
            return pd.DataFrame()
        
        # 데이터 준비
        data = []
        for result in success_results:
            data.append({
                'model': result.model,
                'technique': result.technique,
                'f1_score': result.local_f1,
                'accuracy': result.local_acc,
                'training_time': result.training_time
            })
        
        df = pd.DataFrame(data)
        
        # 피벗 테이블 생성 (모델 × 기법 with F1 점수)
        matrix = df.pivot_table(
            index='model',
            columns='technique', 
            values='f1_score',
            aggfunc='mean'
        )
        
        return matrix
    
    def get_top_performers(self, top_k: int = 5) -> List[ExperimentResult]:
        """최고 성능 조합 TOP K 추출"""
        success_results = self.get_success_results()
        
        # F1 점수 기준으로 정렬
        success_results.sort(key=lambda x: x.local_f1, reverse=True)
        
        return success_results[:top_k]
    
    def analyze_performance_gaps(self) -> Dict:
        """로컬 vs 서버 성능 차이 패턴 분석"""
        submitted_results = [r for r in self.results if r.server_score is not None]
        
        if not submitted_results:
            return {'message': '서버 결과가 없습니다.'}
        
        gaps = [r.performance_gap for r in submitted_results if r.performance_gap is not None]
        
        if not gaps:
            return {'message': '성능 차이 데이터가 없습니다.'}
        
        return {
            'total_count': len(submitted_results),
            'mean_gap': np.mean(gaps),
            'std_gap': np.std(gaps),
            'median_gap': np.median(gaps),
            'min_gap': np.min(gaps),
            'max_gap': np.max(gaps),
            'positive_ratio': len([g for g in gaps if g > 0]) / len(gaps),
            'model_gaps': self._analyze_gaps_by_model(submitted_results),
            'technique_gaps': self._analyze_gaps_by_technique(submitted_results)
        }
    
    def _analyze_gaps_by_model(self, results: List[ExperimentResult]) -> Dict:
        """모델별 성능 차이 분석"""
        model_gaps = {}
        
        for result in results:
            if result.performance_gap is None:
                continue
                
            if result.model not in model_gaps:
                model_gaps[result.model] = []
            model_gaps[result.model].append(result.performance_gap)
        
        # 평균 계산
        for model in model_gaps:
            gaps = model_gaps[model]
            model_gaps[model] = {
                'mean_gap': np.mean(gaps),
                'count': len(gaps),
                'std_gap': np.std(gaps) if len(gaps) > 1 else 0
            }
        
        return model_gaps
    
    def _analyze_gaps_by_technique(self, results: List[ExperimentResult]) -> Dict:
        """기법별 성능 차이 분석"""
        technique_gaps = {}
        
        for result in results:
            if result.performance_gap is None:
                continue
                
            if result.technique not in technique_gaps:
                technique_gaps[result.technique] = []
            technique_gaps[result.technique].append(result.performance_gap)
        
        # 평균 계산
        for technique in technique_gaps:
            gaps = technique_gaps[technique]
            technique_gaps[technique] = {
                'mean_gap': np.mean(gaps),
                'count': len(gaps),
                'std_gap': np.std(gaps) if len(gaps) > 1 else 0
            }
        
        return technique_gaps
    
    def calculate_roi_analysis(self) -> List[Dict]:
        """ROI (시간 대비 성능) 분석"""
        success_results = self.get_success_results()
        
        roi_data = []
        for result in success_results:
            if result.training_time > 0:
                roi = result.local_f1 / (result.training_time / 60)  # 시간당 F1 점수
                roi_data.append({
                    'experiment_id': result.experiment_id,
                    'model': result.model,
                    'technique': result.technique,
                    'f1_score': result.local_f1,
                    'training_hours': result.training_time / 60,
                    'roi': roi
                })
        
        # ROI 순으로 정렬
        roi_data.sort(key=lambda x: x['roi'], reverse=True)
        
        return roi_data
    
    def recommend_ensemble_candidates(self) -> Dict:
        """앙상블 후보 추천"""
        success_results = self.get_success_results()
        
        if len(success_results) < 2:
            return {'message': '앙상블을 위한 충분한 결과가 없습니다.'}
        
        # 성능 기반 추천 (상위 성능)
        performance_based = sorted(success_results, key=lambda x: x.local_f1, reverse=True)[:5]
        
        # 다양성 기반 추천 (서로 다른 모델/기법 조합)
        diversity_based = []
        used_models = set()
        used_techniques = set()
        
        for result in performance_based:
            if result.model not in used_models or result.technique not in used_techniques:
                diversity_based.append(result)
                used_models.add(result.model)
                used_techniques.add(result.technique)
                
                if len(diversity_based) >= 3:
                    break
        
        return {
            'performance_based': [
                {
                    'experiment_id': r.experiment_id,
                    'model': r.model,
                    'technique': r.technique,
                    'f1_score': r.local_f1
                } for r in performance_based
            ],
            'diversity_based': [
                {
                    'experiment_id': r.experiment_id,
                    'model': r.model,
                    'technique': r.technique,
                    'f1_score': r.local_f1
                } for r in diversity_based
            ]
        }
    
    def generate_markdown_report(self) -> str:
        """마크다운 리포트 생성"""
        report = []
        
        # 헤더
        report.append("# 🔬 자동 실험 시스템 결과 분석 리포트")
        report.append(f"")
        report.append(f"생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"")
        
        # 전체 요약
        total_experiments = len(self.results)
        success_experiments = len(self.get_success_results())
        success_rate = (success_experiments / total_experiments * 100) if total_experiments > 0 else 0
        
        report.append("## 📊 전체 요약")
        report.append(f"")
        report.append(f"- **총 실험 수**: {total_experiments}개")
        report.append(f"- **성공한 실험**: {success_experiments}개")
        report.append(f"- **성공률**: {success_rate:.1f}%")
        report.append(f"")
        
        # 최고 성능 결과
        top_performers = self.get_top_performers(5)
        if top_performers:
            report.append("## 🏆 TOP 5 최고 성능 조합")
            report.append(f"")
            for i, result in enumerate(top_performers, 1):
                report.append(f"{i}. **{result.experiment_id}**")
                report.append(f"   - 모델: {result.model}")
                report.append(f"   - 기법: {result.technique}")
                report.append(f"   - F1 점수: {result.local_f1:.4f}")
                report.append(f"   - 정확도: {result.local_acc:.4f}")
                report.append(f"   - 학습 시간: {result.training_time:.1f}분")
                report.append(f"")
        
        # 모델별 기법 효과성 매트릭스
        matrix = self.generate_model_technique_matrix()
        if not matrix.empty:
            report.append("## 📈 모델별 기법 효과성 매트릭스 (F1 점수)")
            report.append(f"")
            report.append(matrix.to_markdown())
            report.append(f"")
        
        # 성능 차이 분석
        gap_analysis = self.analyze_performance_gaps()
        if 'message' not in gap_analysis:
            report.append("## 📊 로컬 vs 서버 성능 차이 분석")
            report.append(f"")
            report.append(f"- **제출된 실험 수**: {gap_analysis['total_count']}개")
            report.append(f"- **평균 성능 차이**: {gap_analysis['mean_gap']:+.4f}")
            report.append(f"- **성능 향상 비율**: {gap_analysis['positive_ratio']:.1%}")
            report.append(f"- **최대 향상**: {gap_analysis['max_gap']:+.4f}")
            report.append(f"- **최대 하락**: {gap_analysis['min_gap']:+.4f}")
            report.append(f"")
            
            # 모델별 성능 차이
            if gap_analysis['model_gaps']:
                report.append("### 모델별 성능 차이")
                report.append(f"")
                for model, data in gap_analysis['model_gaps'].items():
                    report.append(f"- **{model}**: {data['mean_gap']:+.4f} (n={data['count']})")
                report.append(f"")
            
            # 기법별 성능 차이
            if gap_analysis['technique_gaps']:
                report.append("### 기법별 성능 차이")
                report.append(f"")
                for technique, data in gap_analysis['technique_gaps'].items():
                    report.append(f"- **{technique}**: {data['mean_gap']:+.4f} (n={data['count']})")
                report.append(f"")
        
        # ROI 분석
        roi_analysis = self.calculate_roi_analysis()
        if roi_analysis:
            report.append("## ⚡ ROI 분석 (시간 대비 성능)")
            report.append(f"")
            report.append("상위 5개 효율적인 실험:")
            report.append(f"")
            for i, roi_data in enumerate(roi_analysis[:5], 1):
                report.append(f"{i}. **{roi_data['experiment_id']}**")
                report.append(f"   - 모델: {roi_data['model']}")
                report.append(f"   - 기법: {roi_data['technique']}")
                report.append(f"   - F1 점수: {roi_data['f1_score']:.4f}")
                report.append(f"   - 학습 시간: {roi_data['training_hours']:.1f}시간")
                report.append(f"   - ROI: {roi_data['roi']:.3f}")
                report.append(f"")
        
        # 앙상블 추천
        ensemble_candidates = self.recommend_ensemble_candidates()
        if 'message' not in ensemble_candidates:
            report.append("## 🤝 앙상블 후보 추천")
            report.append(f"")
            
            report.append("### 성능 기반 추천")
            report.append(f"")
            for i, candidate in enumerate(ensemble_candidates['performance_based'], 1):
                report.append(f"{i}. {candidate['experiment_id']} - {candidate['model']} + {candidate['technique']} (F1: {candidate['f1_score']:.4f})")
            report.append(f"")
            
            report.append("### 다양성 기반 추천")
            report.append(f"")
            for i, candidate in enumerate(ensemble_candidates['diversity_based'], 1):
                report.append(f"{i}. {candidate['experiment_id']} - {candidate['model']} + {candidate['technique']} (F1: {candidate['f1_score']:.4f})")
            report.append(f"")
        
        # 결론 및 제안
        report.append("## 💡 결론 및 제안")
        report.append(f"")
        
        if top_performers:
            best_result = top_performers[0]
            report.append(f"- **최고 성능 조합**: {best_result.model} + {best_result.technique} (F1: {best_result.local_f1:.4f})")
        
        if roi_analysis:
            best_roi = roi_analysis[0]
            report.append(f"- **최고 효율 조합**: {best_roi['model']} + {best_roi['technique']} (ROI: {best_roi['roi']:.3f})")
        
        if 'message' not in gap_analysis and gap_analysis['positive_ratio'] > 0.5:
            report.append(f"- **서버 성능**: 대부분의 실험에서 로컬 대비 성능 향상 확인")
        
        report.append(f"- **다음 단계**: 최고 성능 조합들로 앙상블 구성 권장")
        report.append(f"")
        
        return "\n".join(report)
    
    def save_report(self, output_path: str = None) -> str:
        """리포트를 파일로 저장"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.base_dir / "experiments" / f"analysis_report_{timestamp}.md"
        
        report_content = self.generate_markdown_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(output_path)
    
    def print_summary(self):
        """요약 정보 출력"""
        total_experiments = len(self.results)
        success_experiments = len(self.get_success_results())
        
        print("🔬 실험 결과 분석 요약")
        print("=" * 60)
        print(f"📊 총 실험 수: {total_experiments}개")
        print(f"✅ 성공한 실험: {success_experiments}개")
        print(f"❌ 실패한 실험: {total_experiments - success_experiments}개")
        print(f"📈 성공률: {(success_experiments/total_experiments*100):.1f}%" if total_experiments > 0 else "📈 성공률: 0%")
        print()
        
        # 최고 성능 결과
        top_performers = self.get_top_performers(3)
        if top_performers:
            print("🏆 TOP 3 최고 성능:")
            for i, result in enumerate(top_performers, 1):
                print(f"   {i}. {result.experiment_id}")
                print(f"      {result.model} + {result.technique}")
                print(f"      F1: {result.local_f1:.4f}, 정확도: {result.local_acc:.4f}")
            print()
        
        # ROI 분석
        roi_analysis = self.calculate_roi_analysis()
        if roi_analysis:
            print("⚡ 최고 효율 실험:")
            best_roi = roi_analysis[0]
            print(f"   {best_roi['experiment_id']}")
            print(f"   {best_roi['model']} + {best_roi['technique']}")
            print(f"   ROI: {best_roi['roi']:.3f} (F1: {best_roi['f1_score']:.4f}, 시간: {best_roi['training_hours']:.1f}h)")
            print()


def main():
    parser = argparse.ArgumentParser(description='실험 결과 분석기')
    parser.add_argument('--base-dir', '-d',
                       default='',
                       help='프로젝트 기본 디렉토리')
    parser.add_argument('--generate-report', '-r', action='store_true',
                       help='마크다운 리포트 생성')
    parser.add_argument('--output', '-o',
                       help='리포트 출력 파일 경로')
    parser.add_argument('--summary-only', '-s', action='store_true',
                       help='요약 정보만 출력')
    
    args = parser.parse_args()
    
    try:
        # 분석기 초기화
        analyzer = ResultsAnalyzer(args.base_dir)
        
        if args.summary_only:
            analyzer.print_summary()
            return
        
        if args.generate_report:
            output_path = analyzer.save_report(args.output)
            print(f"📋 분석 리포트가 생성되었습니다: {output_path}")
        else:
            # 콘솔에 리포트 출력
            report = analyzer.generate_markdown_report()
            print(report)
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
