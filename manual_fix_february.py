# -*- coding: utf-8 -*-
"""
根據用戶提供的正確資料手動補齊 2 月份資料
"""
import pandas as pd
from pathlib import Path

# 威力彩 2 月份正確資料 (根據截圖)
power_february = [
    {'date': '2026-02-05', 'zone1': '[7, 22, 28, 34, 36, 37]', 'zone2': 7},
    {'date': '2026-02-09', 'zone1': '[13, 14, 16, 33, 34, 37]', 'zone2': 2}
]

# 大樂透 2 月份資料 (需要用戶確認)
lotto_february = [
    # 請用戶提供正確的大樂透 2 月份資料
]

# 3星彩 2 月份資料 (需要用戶確認)
star3_february = [
    # 請用戶提供正確的 3星彩 2 月份資料
]

# 4星彩 2 月份資料 (需要用戶確認)
star4_february = [
    # 請用戶提供正確的 4星彩 2 月份資料
]

print("=" * 80)
print("手動補齊 2 月份正確資料")
print("=" * 80)

# 更新威力彩
print("\n[1/4] 更新威力彩資料")
power_file = "data/power/power_history.csv"
if Path(power_file).exists():
    df = pd.read_csv(power_file)
    # 移除所有 2 月份的舊資料
    df = df[~df['date'].str.startswith('2026-02')]
    print(f"  清除舊資料後: {len(df)} 筆")
    
    # 新增正確的 2 月份資料
    new_df = pd.DataFrame(power_february)
    combined_df = pd.concat([df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('date')
    combined_df.to_csv(power_file, index=False)
    
    print(f"  新增 {len(power_february)} 筆 2 月份資料")
    print(f"  總計: {len(combined_df)} 筆")
    for item in power_february:
        print(f"    {item['date']}: 第一區 {item['zone1']} + 第二區 {item['zone2']}")

print("\n" + "=" * 80)
print("威力彩資料已更新!")
print("=" * 80)
print("\n請提供以下遊戲的正確 2 月份資料:")
print("1. 大樂透")
print("2. 3星彩")
print("3. 4星彩")
print("=" * 80)
