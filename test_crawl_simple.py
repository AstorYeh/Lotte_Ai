# -*- coding: utf-8 -*-
"""
簡化版批次爬取腳本 - 先測試單個遊戲
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# 先只爬取 539 測試
print("=" * 80)
print("測試爬取 539 資料")
print("=" * 80)

from src.auzonet_crawler import fetch_auzonet_single_date

results = []
start = datetime(2025, 1, 1)
end = datetime(2026, 2, 9)
current = start

count = 0
while current <= end and count < 10:  # 先測試 10 筆
    if current.weekday() != 6:  # 跳過週日
        date_str = current.strftime('%Y-%m-%d')
        print(f"\n爬取: {date_str}")
        numbers = fetch_auzonet_single_date(date_str)
        
        if numbers and len(numbers) == 5:
            results.append({
                'date': date_str,
                'numbers': ','.join([str(n) for n in sorted(numbers)])
            })
            count += 1
    
    current += timedelta(days=1)

print(f"\n成功爬取 {len(results)} 筆資料")

if results:
    df = pd.DataFrame(results)
    print(df.head())
