"""
快速驗證測試 - 驗證強化修補效果
測試 5 期訓練,檢查修改是否生效
"""
from src.incremental_trainer import IncrementalTrainer
import pandas as pd
from pathlib import Path

print("=" * 60)
print("  強化修補驗證測試")
print("=" * 60)
print()

# 載入數據 (使用完整歷史數據)
df = pd.read_csv('data/539_history.csv')
print(f"[OK] 載入歷史資料: {len(df)} 期")

# 初始化訓練器 (從第 50 期開始測試)
initial_periods = min(50, len(df) - 10)
trainer = IncrementalTrainer(initial_periods=initial_periods, use_llm=False, use_enhanced=True)
print(f"[OK] 訓練器已初始化")
print(f"  - 學習率: {trainer.optimizer.learning_rate}")
print(f"  - 觀察窗口: {trainer.optimizer.observation_window} 期")
print(f"  - 初始訓練期數: {initial_periods}")
print()

# 測試 5 期
test_start = initial_periods
test_end = min(initial_periods + 5, len(df))
print(f"開始快速測試 (第 {test_start+1}-{test_end} 期)...")
print("-" * 60)

for i in range(test_start, test_end):
    period_num = i + 1
    print(f"\n[期數 {period_num}] 訓練中...")
    trainer.train_period(df, i)
    
    # 檢查群組選擇情況
    latest_log = trainer.iteration_logger.current_period
    if latest_log and 'groups' in latest_log:
        group_counts = {}
        for group_id, group_data in latest_log['groups'].items():
            count = len(group_data.get('selected_numbers', []))
            group_counts[group_id] = count
        
        print(f"  群組選擇: {group_counts}")
        
        # 檢查是否有群組被忽略
        empty_groups = [g for g, c in group_counts.items() if c == 0]
        if empty_groups:
            print(f"  [!] 空白群組: {empty_groups}")
        else:
            print(f"  [OK] 所有群組都有參與")

# 完成測試
trainer.iteration_logger.finalize()

print()
print("=" * 60)
print("  測試完成!")
print("=" * 60)
print()

# 讀取測試結果
latest_session = sorted(Path("logs/iterations").glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[0]
print(f"[OK] 測試結果已儲存: {latest_session.name}")
print()

# 讀取摘要
import json
summary_file = latest_session / "training_summary.json"
if summary_file.exists():
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    stats = summary['statistics']
    print("測試結果摘要:")
    print(f"  - 總期數: {stats['total_periods']}")
    print(f"  - 平均準確率: {stats['average_accuracy']:.2%}")
    print(f"  - 最佳準確率: {stats['best_accuracy']:.2%}")
    print(f"  - 總命中數: {stats['total_hits']}")
    print()
    
    # 檢查 0% 期數
    zero_periods = sum(1 for it in summary['iterations'] if it['accuracy'] == 0)
    zero_rate = zero_periods / stats['total_periods']
    print(f"  - 0% 期數: {zero_periods}/{stats['total_periods']} ({zero_rate:.0%})")
    
    if zero_rate < 0.3:
        print("  [OK] 0% 期數佔比改善 (< 30%)")
    else:
        print("  [!] 0% 期數仍然偏高")

print()
print("建議:")
print("  1. 檢查 logs/iterations/ 最新日誌")
print("  2. 確認「暫不調整」訊息是否消失")
print("  3. 如效果良好,可執行完整訓練 (python main.py)")
