# -*- coding: utf-8 -*-
"""
批次爬取所有遊戲資料
2025-01-01 ~ 2026-02-09
"""
import pandas as pd
from pathlib import Path
from src.crawlers.lotto_crawler import fetch_lotto_range
from src.crawlers.power_crawler import fetch_power_range
from src.crawlers.star3_crawler import fetch_star3_range
from src.crawlers.star4_crawler import fetch_star4_range
from src.auzonet_crawler import fetch_auzonet_range

print("=" * 80)
print("批次爬取所有遊戲資料 (2025-01-01 ~ 2026-02-09)")
print("=" * 80)

start_date = "2025-01-01"
end_date = "2026-02-09"

# 1. 今彩539
print("\n[1/5] 爬取今彩539...")
print("-" * 80)
data_539 = fetch_auzonet_range(start_date, end_date)
if data_539:
    df_539 = pd.DataFrame(data_539)
    df_539.to_csv("data/539_train.csv", index=False)
    df_539.to_csv("data/539_history.csv", index=False)
    print(f"✓ 539 資料已儲存: {len(df_539)} 筆")

# 2. 大樂透
print("\n[2/5] 爬取大樂透...")
print("-" * 80)
data_lotto = fetch_lotto_range(start_date, end_date)
if data_lotto:
    df_lotto = pd.DataFrame(data_lotto)
    df_lotto.to_csv("data/lotto/lotto_train.csv", index=False)
    df_lotto.to_csv("data/lotto/lotto_history.csv", index=False)
    print(f"✓ 大樂透資料已儲存: {len(df_lotto)} 筆")

# 3. 威力彩
print("\n[3/5] 爬取威力彩...")
print("-" * 80)
data_power = fetch_power_range(start_date, end_date)
if data_power:
    df_power = pd.DataFrame(data_power)
    df_power.to_csv("data/power/power_train.csv", index=False)
    df_power.to_csv("data/power/power_history.csv", index=False)
    print(f"✓ 威力彩資料已儲存: {len(df_power)} 筆")

# 4. 3星彩
print("\n[4/5] 爬取3星彩...")
print("-" * 80)
data_star3 = fetch_star3_range(start_date, end_date)
if data_star3:
    df_star3 = pd.DataFrame(data_star3)
    df_star3.to_csv("data/star3/star3_train.csv", index=False)
    df_star3.to_csv("data/star3/star3_history.csv", index=False)
    print(f"✓ 3星彩資料已儲存: {len(df_star3)} 筆")

# 5. 4星彩
print("\n[5/5] 爬取4星彩...")
print("-" * 80)
data_star4 = fetch_star4_range(start_date, end_date)
if data_star4:
    df_star4 = pd.DataFrame(data_star4)
    df_star4.to_csv("data/star4/star4_train.csv", index=False)
    df_star4.to_csv("data/star4/star4_history.csv", index=False)
    print(f"✓ 4星彩資料已儲存: {len(df_star4)} 筆")

print("\n" + "=" * 80)
print("所有資料爬取完成!")
print("=" * 80)
print(f"539:    {len(data_539) if data_539 else 0} 筆")
print(f"大樂透: {len(data_lotto) if data_lotto else 0} 筆")
print(f"威力彩: {len(data_power) if data_power else 0} 筆")
print(f"3星彩:  {len(data_star3) if data_star3 else 0} 筆")
print(f"4星彩:  {len(data_star4) if data_star4 else 0} 筆")
