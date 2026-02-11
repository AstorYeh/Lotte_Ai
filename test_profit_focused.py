# -*- coding: utf-8 -*-
"""
Profit-Focused Strategy Test
Test the new "focused fire" strategy with 10 periods
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.incremental_trainer import IncrementalTrainer
from src.profit_evaluator import ProfitEvaluator

def test_profit_focused_strategy():
    """Test the profit-focused strategy"""
    
    print("="*60)
    print("OPTIMIZED STRATEGY TEST - 基礎模型 + 6 顆選號")
    print("="*60)
    print("\nStrategy Changes:")
    print("  1. Disable enhanced models (XGBoost/RF scores are 0)")
    print("  2. Focus on 7 base models")
    print("  3. Increase selection: 5 -> 6 numbers")
    print("  4. Pure Top-N selection (no group balance)")
    print("\nGoal: Stable 2+ hits rate at 30%+")
    print("="*60 + "\n")
    
    # Create trainer with enhanced models
    trainer = IncrementalTrainer(
        initial_periods=30,
        use_enhanced=False  # 🔥 禁用增強模型,專注基礎 7 個模型
    )
    
    # Create profit evaluator
    profit_eval = ProfitEvaluator()
    
    # Load data (use full history)
    import pandas as pd
    df = pd.read_csv("data/539_history.csv")
    
    print(f"Loaded {len(df)} periods of historical data\n")
    
    # Test with 10 periods
    test_periods = 10
    print(f"Testing with {test_periods} periods...\n")
    
    # Train
    for i in range(test_periods):
        period_idx = trainer.initial_periods + i
        
        if period_idx >= len(df):
            print(f"\n[WARNING] Not enough data for period {period_idx}")
            break
        
        print(f"\nPeriod {i+1}/{test_periods} (Index: {period_idx})")
        print("-" * 40)
        
        result = trainer.train_period(df, period_idx)
        
        if result:
            # Add to profit evaluator
            profit_eval.add_result(
                period=result['period'],
                predicted=result['predicted_numbers'],
                actual=result['actual_numbers'],
                hits=result['hits']
            )
            
            print(f"  Predicted: {result['predicted_numbers']}")
            print(f"  Actual: {result['actual_numbers']}")
            print(f"  Hits: {result['hits']}/5")
            
            # Economic status
            if result['hits'] >= 3:
                status = "[PROFIT]"
            elif result['hits'] == 2:
                status = "[BREAK-EVEN]"
            else:
                status = "[LOSS]"
            
            print(f"  Status: {status}")
    
    # Display summary
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    profit_eval.print_summary()
    
    # Save results
    output_file = Path("logs") / "profit_focused_test.json"
    output_file.parent.mkdir(exist_ok=True)
    profit_eval.save_to_file(output_file)
    
    # Compare with baseline
    print("\nComparison with Baseline (305 periods):")
    print("-" * 60)
    print(f"{'Metric':<30} {'Baseline':<15} {'Test':<15}")
    print("-" * 60)
    
    summary = profit_eval.get_summary()
    
    print(f"{'Profit Rate (3+ hits)':<30} {'2.62%':<15} {summary['profit_rate']*100:>6.2f}%")
    print(f"{'Loss Rate (0-1 hits)':<30} {'79.34%':<15} {summary['loss_rate']*100:>6.2f}%")
    print(f"{'Avg Score/Period':<30} {'-0.77':<15} {summary['avg_score_per_period']:>+6.2f}")
    print("-" * 60)
    
    # Evaluation
    if summary['profit_rate'] > 0.10:
        print("\n[EXCELLENT] Profit rate significantly improved!")
    elif summary['profit_rate'] > 0.05:
        print("\n[GOOD] Profit rate improved!")
    else:
        print("\n[POOR] Profit rate still low, need further optimization")
    
    return profit_eval


if __name__ == "__main__":
    try:
        evaluator = test_profit_focused_strategy()
        print("\n[OK] Test completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
