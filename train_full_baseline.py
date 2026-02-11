# -*- coding: utf-8 -*-
"""
完整訓練腳本 - 建立可靠基準線
執行 305 期完整訓練,使用最佳配置
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.incremental_trainer import IncrementalTrainer
from src.profit_evaluator import ProfitEvaluator
import pandas as pd

def main():
    """執行完整訓練"""
    
    print("="*80)
    print("完整訓練 - 建立可靠基準線")
    print("="*80)
    print("\n配置:")
    print("  - 訓練期數: 305 期 (完整歷史資料)")
    print("  - 選號數量: 5 顆 (集中火力)")
    print("  - 群組平衡: 移除 (純粹 Top-5)")
    print("  - 增強模型: 禁用 (避免 0 分干擾)")
    print("  - 初始訓練: 30 期")
    print("\n目標:")
    print("  - 建立可靠的基準線")
    print("  - 2+ 顆命中率目標: 25-30%")
    print("  - 平均命中數目標: 1.0+ 顆/期")
    print("="*80 + "\n")
    
    # 載入完整資料
    df = pd.read_csv("data/539_history.csv")
    print(f"[OK] 載入資料: {len(df)} 期\n")
    
    # 創建訓練器
    trainer = IncrementalTrainer(
        initial_periods=30,
        use_enhanced=False  # 禁用增強模型
    )
    
    # 創建評估器
    profit_eval = ProfitEvaluator()
    
    # 執行完整訓練
    print("開始訓練...\n")
    total_periods = len(df) - trainer.initial_periods
    
    for i in range(total_periods):
        period_idx = trainer.initial_periods + i
        
        if (i + 1) % 10 == 0 or i == 0:
            print(f"\n進度: {i+1}/{total_periods} ({(i+1)/total_periods*100:.1f}%)")
            print("-" * 60)
        
        # 訓練單期
        result = trainer.train_period(df, period_idx)
        
        if result:
            # 添加到評估器
            profit_eval.add_result(
                period=result['period'],
                predicted=result['predicted_numbers'],
                actual=result['actual_numbers'],
                hits=result['hits']
            )
            
            # 簡要輸出
            status = "💰" if result['hits'] >= 3 else ("➖" if result['hits'] == 2 else "💸")
            print(f"  期數 {result['period']:3d}: {result['hits']}/5 命中 {status}")
    
    # 完成訓練
    print("\n" + "="*80)
    print("訓練完成!")
    print("="*80 + "\n")
    
    # 顯示摘要
    profit_eval.print_summary()
    
    # 儲存結果
    output_file = Path("logs") / "full_training_baseline.json"
    output_file.parent.mkdir(exist_ok=True)
    profit_eval.save_to_file(output_file)
    
    print(f"\n[OK] 結果已儲存: {output_file}")
    
    # 與原始基準線比較
    print("\n" + "="*80)
    print("與原始基準線比較")
    print("="*80)
    
    summary = profit_eval.get_summary()
    
    print(f"\n{'指標':<30} {'原始基準':<15} {'新基準':<15} {'變化':<15}")
    print("-" * 80)
    print(f"{'賺錢率 (3+ 顆)':<30} {'2.62%':<15} {summary['profit_rate']*100:>6.2f}% {(summary['profit_rate']-0.0262)*100:>+6.2f}%")
    print(f"{'2+ 顆命中率':<30} {'20.65%':<15} {(summary['profit_rate']+summary['break_even_rate'])*100:>6.2f}% {(summary['profit_rate']+summary['break_even_rate']-0.2065)*100:>+6.2f}%")
    print(f"{'虧損率 (0-1 顆)':<30} {'79.34%':<15} {summary['loss_rate']*100:>6.2f}% {(summary['loss_rate']-0.7934)*100:>+6.2f}%")
    print(f"{'平均命中數/期':<30} {'0.88':<15} {summary['avg_hits']:>6.2f} {summary['avg_hits']-0.88:>+6.2f}")
    print(f"{'平均分數/期':<30} {'-0.77':<15} {summary['avg_score_per_period']:>+6.2f} {summary['avg_score_per_period']+0.77:>+6.2f}")
    print("-" * 80)
    
    # 評估
    if summary['profit_rate'] + summary['break_even_rate'] >= 0.25:
        print("\n[GOOD] 2+ 顆命中率達到目標 (25%+)! ✅")
    else:
        print(f"\n[POOR] 2+ 顆命中率未達目標: {(summary['profit_rate']+summary['break_even_rate'])*100:.2f}% < 25%")
    
    if summary['avg_hits'] >= 1.0:
        print("[GOOD] 平均命中數達到目標 (1.0+)! ✅")
    else:
        print(f"[POOR] 平均命中數未達目標: {summary['avg_hits']:.2f} < 1.0")
    
    return profit_eval


if __name__ == "__main__":
    try:
        evaluator = main()
        print("\n[OK] 完整訓練成功完成!")
    except Exception as e:
        print(f"\n[ERROR] 訓練失敗: {e}")
        import traceback
        traceback.print_exc()
