# -*- coding: utf-8 -*-
"""
階段一: 完成 539 系統
1. 爬取完整資料
2. 生成預測
3. 推送 Discord
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from src.auzonet_crawler import fetch_auzonet_single_date
from src.auto_predictor import AutoPredictor

print("=" * 80)
print("階段一: 539 系統完整執行")
print("=" * 80)

# Step 1: 爬取完整資料
print("\n[Step 1] 爬取 539 完整資料 (2025-01-01 ~ 2026-02-09)...")
print("-" * 80)

results = []
start = datetime(2025, 1, 1)
end = datetime(2026, 2, 9)
current = start

while current <= end:
    if current.weekday() != 6:  # 跳過週日
        date_str = current.strftime('%Y-%m-%d')
        numbers = fetch_auzonet_single_date(date_str)
        
        if numbers and len(numbers) == 5:
            results.append({
                'date': date_str,
                'numbers': ','.join([str(n) for n in sorted(numbers)])
            })
            
            # 每爬取 50 筆顯示進度
            if len(results) % 50 == 0:
                print(f"  進度: {len(results)} 筆...")
    
    current += timedelta(days=1)

print(f"\n✓ 共爬取 {len(results)} 筆 539 資料")

# Step 2: 儲存資料
print("\n[Step 2] 儲存資料...")
df = pd.DataFrame(results)
df.to_csv("data/539_train.csv", index=False)
df.to_csv("data/539_history.csv", index=False)
print(f"✓ 資料已儲存: {len(df)} 筆")

# Step 3: 生成預測
print("\n[Step 3] 生成今日預測...")
print("-" * 80)
predictor = AutoPredictor()
result = predictor.generate_new_prediction()

if result:
    print("\n✓ 539 預測完成!")
    print(f"  日期: {result['prediction_date']}")
    print(f"  組數: {result['num_sets']}")
    for i, nums in enumerate(result['predicted_numbers'], 1):
        print(f"  第 {i} 組: {nums}")
else:
    print("\n✗ 預測失敗")

print("\n" + "=" * 80)
print("539 系統完成!")
print("=" * 80)
