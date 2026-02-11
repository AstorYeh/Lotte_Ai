# -*- coding: utf-8 -*-
"""
補齊 2026 年 2 月份資料
從 auzonet.com 爬取 2026-02-01 ~ 2026-02-10
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

# 導入現有爬蟲
from src.auzonet_crawler import fetch_auzonet_single_date
from src.crawlers.lotto_crawler import fetch_lotto_single_date
from src.crawlers.power_crawler import fetch_power_single_date


def update_539_february():
    """補齊 539 2月資料"""
    print("\n" + "=" * 80)
    print("[1/3] 補齊 539 2月資料")
    print("=" * 80)
    
    # 載入現有資料
    file_path = "data/539_history.csv"
    if Path(file_path).exists():
        existing_df = pd.read_csv(file_path)
        print(f"  現有資料: {len(existing_df)} 筆")
    else:
        existing_df = pd.DataFrame()
    
    # 爬取 2 月份資料
    results = []
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 10)
    current = start_date
    
    while current <= end_date:
        if current.weekday() != 6:  # 跳過週日
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                numbers = fetch_auzonet_single_date(date_str)
                if numbers and len(numbers) == 5:
                    results.append({
                        'date': date_str,
                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                    })
                    print(f"  [OK] {date_str}: {sorted(numbers)}")
                else:
                    print(f"  [SKIP] {date_str}: 無資料")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ✗ {date_str}: {e}")
        
        current += timedelta(days=1)
    
    # 合併並儲存
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'])
        combined_df = combined_df.sort_values('date')
        combined_df.to_csv(file_path, index=False)
        
        print(f"\n[OK] 539: 新增 {len(results)} 筆,總共 {len(combined_df)} 筆")
        return len(results)
    else:
        print(f"\n[WARNING] 539: 無新資料")
        return 0


def update_lotto_february():
    """補齊大樂透 2月資料"""
    print("\n" + "=" * 80)
    print("[2/3] 補齊大樂透 2月資料")
    print("=" * 80)
    
    file_path = "data/lotto/lotto_history.csv"
    if Path(file_path).exists():
        existing_df = pd.read_csv(file_path)
        print(f"  現有資料: {len(existing_df)} 筆")
    else:
        existing_df = pd.DataFrame()
    
    results = []
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 10)
    current = start_date
    
    while current <= end_date:
        if current.weekday() in [1, 4]:  # 週二、週五
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                data = fetch_lotto_single_date(date_str)
                if data and 'numbers' in data:
                    results.append({
                        'date': date_str,
                        'numbers': ','.join([str(n) for n in data['numbers']])
                    })
                    print(f"  ✓ {date_str}: {data['numbers']}")
                else:
                    print(f"  ✗ {date_str}: 無資料")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ✗ {date_str}: {e}")
        
        current += timedelta(days=1)
    
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'])
        combined_df = combined_df.sort_values('date')
        
        Path("data/lotto").mkdir(parents=True, exist_ok=True)
        combined_df.to_csv(file_path, index=False)
        
        print(f"\n[OK] 大樂透: 新增 {len(results)} 筆,總共 {len(combined_df)} 筆")
        return len(results)
    else:
        print(f"\n[WARNING] 大樂透: 無新資料")
        return 0


def update_power_february():
    """補齊威力彩 2月資料"""
    print("\n" + "=" * 80)
    print("[3/3] 補齊威力彩 2月資料")
    print("=" * 80)
    
    file_path = "data/power/power_history.csv"
    if Path(file_path).exists():
        existing_df = pd.read_csv(file_path)
        print(f"  現有資料: {len(existing_df)} 筆")
    else:
        existing_df = pd.DataFrame()
    
    results = []
    start_date = datetime(2026, 2, 1)
    end_date = datetime(2026, 2, 10)
    current = start_date
    
    while current <= end_date:
        if current.weekday() in [0, 3]:  # 週一、週四
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                data = fetch_power_single_date(date_str)
                if data and 'zone1' in data and 'zone2' in data:
                    results.append({
                        'date': date_str,
                        'zone1': str(data['zone1']),
                        'zone2': data['zone2']
                    })
                    print(f"  ✓ {date_str}: 第一區 {data['zone1']} + 第二區 {data['zone2']}")
                else:
                    print(f"  ✗ {date_str}: 無資料")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ✗ {date_str}: {e}")
        
        current += timedelta(days=1)
    
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'])
        combined_df = combined_df.sort_values('date')
        
        Path("data/power").mkdir(parents=True, exist_ok=True)
        combined_df.to_csv(file_path, index=False)
        
        print(f"\n[OK] 威力彩: 新增 {len(results)} 筆,總共 {len(combined_df)} 筆")
        return len(results)
    else:
        print(f"\n[WARNING] 威力彩: 無新資料")
        return 0


if __name__ == "__main__":
    print("=" * 80)
    print("補齊 2026 年 2 月份資料")
    print("日期範圍: 2026-02-01 ~ 2026-02-10")
    print("=" * 80)
    
    total = 0
    total += update_539_february()
    total += update_lotto_february()
    total += update_power_february()
    
    print("\n" + "=" * 80)
    print("補齊完成!")
    print("=" * 80)
    print(f"總共新增: {total} 筆")
    print("=" * 80)
