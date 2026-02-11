# -*- coding: utf-8 -*-
"""
階段 2 驗證訓練 - 恢復原始配置優勢
"""
import sys
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.incremental_trainer import IncrementalTrainer
from src.profit_evaluator import ProfitEvaluator
import json

def main():
    print("="*80)
    print("階段 2 驗證訓練 - 恢復原始配置優勢")
    print("="*80)
    print("\n配置:")
    print("  - 訓練期數: 305 期")
    print("  - 選號數量: 6-7 顆 (恢復原始)")
    print("  - 群組平衡: 啟用 (恢復原始)")
    print("  - 增強模型: 啟用 (修復後 0.15/0.85)")
    print("\n目標:")
    print("  - 結合原始配置優勢 + 修復後的增強模型")
    print("  - 2+ 顆命中率目標: 21-22%")
    print("  - 對比原始基準: 20.65%")
    print("  - 對比階段 1: 16.73%")
    print("="*80 + "\n")
    
    # Create trainer
    trainer = IncrementalTrainer(
        initial_periods=30,
        use_enhanced=True  # 啟用修復後的增強模型
    )
    
    # Train on all periods
    print(f"開始訓練...")
    trainer.train_all_periods()
    
    # Analyze results
    print("\n分析結果...")
    evaluator = ProfitEvaluator()
    
    # Find latest session
    import os
    iterations_dir = Path("logs/iterations")
    sessions = [d for d in iterations_dir.iterdir() if d.is_dir()]
    latest_session = max(sessions, key=lambda x: x.name)
    
    print(f"最新 session: {latest_session.name}")
    
    # Load training summary
    summary_file = latest_session / "training_summary.json"
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    # Evaluate
    results = evaluator.evaluate_iterations(summary['iterations'])
    
    # Print results
    print("\n" + "="*80)
    print("階段 2 驗證結果")
    print("="*80)
    print(f"\n總期數: {results['total_periods']}")
    print(f"\n經濟效益:")
    print(f"  賺錢率 (3+ 顆): {results['profit_rate']:.2f}%")
    print(f"  打平率 (2 顆):  {results['break_even_rate']:.2f}%")
    print(f"  虧損率 (0-1 顆): {results['loss_rate']:.2f}%")
    print(f"\n核心指標:")
    print(f"  2+ 顆命中率: {results['hit_2plus_rate']:.2f}%")
    print(f"  平均命中數: {results['avg_hits']:.2f}")
    print(f"  平均分數: {results['avg_score']:.2f}")
    
    # Compare with previous
    print(f"\n對比:")
    print(f"  vs 原始基準 (20.65%): {results['hit_2plus_rate'] - 20.65:+.2f}%")
    print(f"  vs 階段 1 (16.73%): {results['hit_2plus_rate'] - 16.73:+.2f}%")
    
    if results['hit_2plus_rate'] >= 21.0:
        print(f"\n[OK] 階段 2 成功! 達到目標 21-22%")
        if results['hit_2plus_rate'] > 20.65:
            print(f"[EXCELLENT] 超越原始基準線!")
        print(f"準備進入階段 3: 添加時間序列特徵")
    elif results['hit_2plus_rate'] >= 19.0:
        print(f"\n[WARNING] 接近目標,但未完全達成")
        print(f"仍可進入階段 3")
    else:
        print(f"\n[ERROR] 未達目標,需要重新評估策略")
    
    # Save results
    result_file = Path("logs") / "stage2_verification.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'session_id': latest_session.name,
            'config': {
                'num_select': '6-7',
                'use_balance': True,
                'use_enhanced': True,
                'enhanced_default': '0.15/0.85'
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果已保存: {result_file}")

if __name__ == "__main__":
    main()
