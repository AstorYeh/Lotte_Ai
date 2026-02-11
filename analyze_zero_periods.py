"""
分析 0% 期數特徵
找出共同失敗模式
"""
import json
import pandas as pd
from pathlib import Path
from collections import Counter

# 載入訓練摘要
session_dir = Path("logs/iterations/20260127_214212")
with open(session_dir / "training_summary.json", 'r', encoding='utf-8') as f:
    summary = json.load(f)

# 提取 0% 期數
zero_periods = [it for it in summary['iterations'] if it['accuracy'] == 0]
non_zero_periods = [it for it in summary['iterations'] if it['accuracy'] > 0]

print("=" * 70)
print("  0% 期數分析報告")
print("=" * 70)
print()

print(f"[基本統計]")
print(f"  - 0% 期數: {len(zero_periods)} / {len(summary['iterations'])} ({len(zero_periods)/len(summary['iterations']):.1%})")
print(f"  - 非0% 期數: {len(non_zero_periods)} / {len(summary['iterations'])} ({len(non_zero_periods)/len(summary['iterations']):.1%})")
print()

# 分析 0% 期數的詳細資料
print(f"[0% 期數詳細分析]")
print(f"  載入詳細日誌...")

zero_details = []
for period_info in zero_periods[:20]:  # 分析前 20 個
    period_file = session_dir / period_info['file']
    if period_file.exists():
        with open(period_file, 'r', encoding='utf-8') as f:
            detail = json.load(f)
            zero_details.append({
                'period': period_info['period'],
                'predicted': detail.get('final_prediction', []),
                'actual': detail.get('actual_numbers', []),
                'groups': detail.get('groups', {})
            })

print(f"  已載入 {len(zero_details)} 個 0% 期數的詳細資料")
print()

# 分析群組選擇模式
print(f"[群組選擇模式]")
group_counts = {'group1': [], 'group2': [], 'group3': [], 'group4': []}

for detail in zero_details:
    for group_id, group_data in detail['groups'].items():
        selected = group_data.get('selected_numbers', [])
        group_counts[group_id].append(len(selected))

for group_id, counts in group_counts.items():
    if counts:
        avg = sum(counts) / len(counts)
        print(f"  {group_id}: 平均選擇 {avg:.1f} 顆")

print()

# 分析候選號碼數量
print(f"[候選號碼數量]")
candidate_counts = [len(detail['predicted']) for detail in zero_details]
if candidate_counts:
    avg_candidates = sum(candidate_counts) / len(candidate_counts)
    print(f"  - 平均候選數: {avg_candidates:.1f} 顆")
    print(f"  - 最少: {min(candidate_counts)} 顆")
    print(f"  - 最多: {max(candidate_counts)} 顆")
    
    # 統計分布
    count_dist = Counter(candidate_counts)
    print(f"\n  候選數分布:")
    for count in sorted(count_dist.keys()):
        print(f"    {count} 顆: {count_dist[count]} 期")

print()

# 顯示幾個具體案例
print(f"[具體案例 (前5個)]")
for i, detail in enumerate(zero_details[:5], 1):
    print(f"\n  案例 {i}: 第 {detail['period']} 期")
    print(f"    預測: {detail['predicted']}")
    print(f"    實際: {detail['actual']}")
    print(f"    候選數: {len(detail['predicted'])} 顆")

print()
print("=" * 70)
print("  分析完成")
print("=" * 70)
