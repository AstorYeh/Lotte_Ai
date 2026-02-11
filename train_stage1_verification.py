# -*- coding: utf-8 -*-
"""
階段 1 驗證訓練 - 修復後的增強模型
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
    print("階段 1 驗證訓練 - 修復後的增強模型")
    print("="*80)
    print("\n配置:")
    print("  - 訓練期數: 305 期")
    print("  - 選號數量: 5 顆")
    print("  - 群組平衡: 移除")
    print("  - 增強模型: 啟用 (已修復默認值策略)")
    print("  - 默認值: 0.15 (從未出現) / 0.85 (每期出現)")
    print("\n目標:")
    print("  - 驗證修復效果")
    print("  - 2+ 顆命中率目標: 18-19%")
    print("  - 對比修復前: 15.74%")
    print("="*80 + "\n")
    
    # Create trainer with fixed enhanced models
    trainer = IncrementalTrainer(
        initial_periods=30,
        use_enhanced=True  # 啟用修復後的增強模型
    )
    
    # Load data
    print("載入歷史資料...")
    trainer.load_data('data/539_history.csv')
    
    # Train on all periods
    print(f"\n開始訓練 {len(trainer.df)} 期...")
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
    print("階段 1 驗證結果")
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
    print(f"\n對比修復前 (15.74%):")
    improvement = ((results['hit_2plus_rate'] - 15.74) / 15.74) * 100
    print(f"  提升幅度: {improvement:+.1f}%")
    
    if results['hit_2plus_rate'] >= 18.0:
        print(f"\n[OK] 階段 1 成功! 達到目標 18-19%")
        print(f"準備進入階段 2: 恢復原始配置")
    elif results['hit_2plus_rate'] >= 17.0:
        print(f"\n[WARNING] 接近目標,但未完全達成")
        print(f"仍可進入階段 2")
    else:
        print(f"\n[ERROR] 未達目標,需要重新評估策略")
    
    # Save results
    result_file = Path("logs") / "stage1_verification.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'session_id': latest_session.name,
            'config': {
                'num_select': 5,
                'use_balance': False,
                'use_enhanced': True,
                'enhanced_default': '0.15/0.85'
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果已保存: {result_file}")

if __name__ == "__main__":
    main()
