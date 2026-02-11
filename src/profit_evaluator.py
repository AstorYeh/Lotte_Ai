# -*- coding: utf-8 -*-
"""
Profit Evaluator - Money-Making Rate Evaluator
Focus on 3+ hits rate (profitable) instead of average hit rate

Scoring System:
- 0-1 hits: Loss (score = -1)
- 2 hits: Break even (score = 0)
- 3 hits: Profit (score = 1)
- 4 hits: Profit (score = 2)
- 5 hits: Profit (score = 3)
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime


class ProfitEvaluator:
    """Money-Making Rate Evaluator"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, period, predicted, actual, hits):
        """
        Record single period result
        
        Args:
            period: Period number
            predicted: Predicted numbers (list)
            actual: Actual winning numbers (list)
            hits: Number of hits
        """
        # Determine economic benefit
        if hits >= 3:
            profit_status = 'profit'  # Profitable
            score = hits - 2  # 3 hits=1, 4 hits=2, 5 hits=3
        elif hits == 2:
            profit_status = 'break_even'  # Break even
            score = 0
        else:  # 0-1 hits
            profit_status = 'loss'  # Loss
            score = -1
        
        self.results.append({
            'period': period,
            'predicted': predicted,
            'actual': actual,
            'hits': hits,
            'profit_status': profit_status,
            'score': score
        })
    
    def get_profit_rate(self):
        """Calculate profit rate (3+ hits period ratio)"""
        if not self.results:
            return 0.0
        
        profit_periods = sum(1 for r in self.results if r['profit_status'] == 'profit')
        return profit_periods / len(self.results)
    
    def get_loss_rate(self):
        """Calculate loss rate (0-1 hits period ratio)"""
        if not self.results:
            return 0.0
        
        loss_periods = sum(1 for r in self.results if r['profit_status'] == 'loss')
        return loss_periods / len(self.results)
    
    def get_break_even_rate(self):
        """Calculate break-even rate (2 hits period ratio)"""
        if not self.results:
            return 0.0
        
        break_even_periods = sum(1 for r in self.results if r['profit_status'] == 'break_even')
        return break_even_periods / len(self.results)
    
    def get_total_score(self):
        """Calculate total score"""
        return sum(r['score'] for r in self.results)
    
    def get_avg_hits(self):
        """Calculate average hits per period"""
        if not self.results:
            return 0.0
        return sum(r['hits'] for r in self.results) / len(self.results)
    
    def get_summary(self):
        """Get summary statistics"""
        total = len(self.results)
        
        # Group by hits count
        hits_distribution = {}
        for i in range(6):
            count = sum(1 for r in self.results if r['hits'] == i)
            hits_distribution[i] = {
                'count': count,
                'percentage': count / total if total > 0 else 0
            }
        
        return {
            'total_periods': total,
            'profit_rate': self.get_profit_rate(),
            'loss_rate': self.get_loss_rate(),
            'break_even_rate': self.get_break_even_rate(),
            'total_score': self.get_total_score(),
            'avg_score_per_period': self.get_total_score() / total if total > 0 else 0,
            'avg_hits': self.get_avg_hits(),
            'hits_distribution': hits_distribution
        }
    
    def print_summary(self):
        """Display summary report"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("PROFIT RATE EVALUATION REPORT")
        print("="*60)
        print(f"Total Periods: {summary['total_periods']}")
        print(f"\nEconomic Benefit Analysis:")
        print(f"  Profit Rate (3+ hits):   {summary['profit_rate']*100:6.2f}%  [TARGET: 30%+]")
        print(f"  Break-Even Rate (2 hits): {summary['break_even_rate']*100:6.2f}%")
        print(f"  Loss Rate (0-1 hits):    {summary['loss_rate']*100:6.2f}%  [TARGET: <50%]")
        print(f"\nScoring:")
        print(f"  Total Score: {summary['total_score']:+d}")
        print(f"  Avg Score/Period: {summary['avg_score_per_period']:+.2f}")
        print(f"  Avg Hits/Period: {summary['avg_hits']:.2f}")
        
        print(f"\nHits Distribution:")
        for hits in range(6):
            dist = summary['hits_distribution'][hits]
            bar = "#" * int(dist['percentage'] * 50)
            
            # Add status indicator
            if hits >= 3:
                status = "[PROFIT]"
            elif hits == 2:
                status = "[BREAK-EVEN]"
            else:
                status = "[LOSS]"
            
            print(f"  {hits} hits: {dist['count']:3d} ({dist['percentage']*100:5.2f}%) {bar} {status}")
        
        print("="*60 + "\n")
        
        # Performance evaluation
        self._print_performance_evaluation(summary)
    
    def _print_performance_evaluation(self, summary):
        """Print performance evaluation"""
        print("Performance Evaluation:")
        print("-" * 60)
        
        # Profit rate evaluation
        profit_rate = summary['profit_rate']
        if profit_rate >= 0.30:
            profit_grade = "EXCELLENT"
        elif profit_rate >= 0.25:
            profit_grade = "GOOD"
        elif profit_rate >= 0.20:
            profit_grade = "FAIR"
        else:
            profit_grade = "POOR"
        
        print(f"  Profit Rate: {profit_rate*100:.2f}% - {profit_grade}")
        
        # Loss rate evaluation
        loss_rate = summary['loss_rate']
        if loss_rate < 0.40:
            loss_grade = "EXCELLENT"
        elif loss_rate < 0.50:
            loss_grade = "GOOD"
        elif loss_rate < 0.60:
            loss_grade = "FAIR"
        else:
            loss_grade = "POOR"
        
        print(f"  Loss Rate: {loss_rate*100:.2f}% - {loss_grade}")
        
        # Overall score evaluation
        avg_score = summary['avg_score_per_period']
        if avg_score > 0.2:
            overall_grade = "EXCELLENT"
        elif avg_score > 0:
            overall_grade = "GOOD"
        elif avg_score > -0.2:
            overall_grade = "FAIR"
        else:
            overall_grade = "POOR"
        
        print(f"  Overall Score: {avg_score:+.2f} - {overall_grade}")
        print("-" * 60 + "\n")
    
    def save_to_file(self, filepath):
        """Save results to JSON file"""
        summary = self.get_summary()
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'results': self.results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Results saved to: {filepath}")
    
    def load_from_file(self, filepath):
        """Load results from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.results = data['results']
        print(f"[OK] Results loaded from: {filepath}")
        print(f"     Total periods: {len(self.results)}")


if __name__ == "__main__":
    # Test
    print("Testing Profit Evaluator...")
    
    evaluator = ProfitEvaluator()
    
    # Simulate some results
    test_data = [
        (1, [1,2,3,4,5], [1,2,6,7,8], 2),  # Break even
        (2, [1,2,3,4,5], [1,2,3,7,8], 3),  # Profit
        (3, [1,2,3,4,5], [6,7,8,9,10], 0), # Loss
        (4, [1,2,3,4,5], [1,7,8,9,10], 1), # Loss
        (5, [1,2,3,4,5], [1,2,3,4,8], 4),  # Profit
        (6, [1,2,3,4,5], [1,2,3,4,5], 5),  # Profit (jackpot!)
    ]
    
    for period, pred, actual, hits in test_data:
        evaluator.add_result(period, pred, actual, hits)
    
    # Display summary
    evaluator.print_summary()
    
    print("\n[OK] Profit Evaluator test completed!")
