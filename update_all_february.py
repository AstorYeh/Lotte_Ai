# -*- coding: utf-8 -*-
"""
補齊所有遊戲 2026 年 2 月份資料
從 auzonet.com 爬取 2026-02-01 ~ 2026-02-10
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
import sys

# 設置輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 導入現有爬蟲
from src.auzonet_crawler import fetch_auzonet_single_date
from src.crawlers.lotto_crawler import fetch_lotto_single_date
from src.crawlers.power_crawler import fetch_power_single_date
from src.crawlers.star3_crawler import fetch_star3_single_date
from src.crawlers.star4_crawler import fetch_star4_single_date


def update_539_february():
    """補齊 539 2月資料"""
    print("\n" + "=" * 80)
    print("[1/5] 補齊 539 2月資料")
    print("=" * 80)
    
    file_path = "data/539_history.csv"
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
        if current.weekday() != 6:
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                numbers = fetch_auzonet_single_date(date_str)
                if numbers and len(numbers) == 5:
                    results.append({
                        'date': date_str,
                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                    })
                    print(f"  [OK] {date_str}: {sorted(numbers)}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  [SKIP] {date_str}: {str(e)[:50]}")
        
        current += timedelta(days=1)
    
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'])
        combined_df = combined_df.sort_values('date')
        combined_df.to_csv(file_path, index=False)
        
        print(f"\n[OK] 539: 新增 {len(results)} 筆,總共 {len(combined_df)} 筆")
        return len(results)
    else:
        print(f"\n[INFO] 539: 無新資料")
        return 0


def update_lotto_february():
    """補齊大樂透 2月資料"""
    print("\n" + "=" * 80)
    print("[2/5] 補齊大樂透 2月資料")
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
                    print(f"  [OK] {date_str}: {data['numbers']}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  [SKIP] {date_str}: {str(e)[:50]}")
        
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
        print(f"\n[INFO] 大樂透: 無新資料")
        return 0


def update_power_february():
    """補齊威力彩 2月資料"""
    print("\n" + "=" * 80)
    print("[3/5] 補齊威力彩 2月資料")
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
                    print(f"  [OK] {date_str}: 第一區 {data['zone1']} + 第二區 {data['zone2']}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  [SKIP] {date_str}: {str(e)[:50]}")
        
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
        print(f"\n[INFO] 威力彩: 無新資料")
        return 0


def update_star3_february():
    """補齊 3星彩 2月資料"""
    print("\n" + "=" * 80)
    print("[4/5] 補齊 3星彩 2月資料")
    print("=" * 80)
    
    file_path = "data/star3/star3_history.csv"
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
        if current.weekday() != 6:  # 週一~週六
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                number = fetch_star3_single_date(date_str)
                if number:
                    results.append({
                        'date': date_str,
                        'number': number
                    })
                    print(f"  [OK] {date_str}: {number}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  [SKIP] {date_str}: {str(e)[:50]}")
        
        current += timedelta(days=1)
    
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'])
        combined_df = combined_df.sort_values('date')
        
        Path("data/star3").mkdir(parents=True, exist_ok=True)
        combined_df.to_csv(file_path, index=False)
        
        print(f"\n[OK] 3星彩: 新增 {len(results)} 筆,總共 {len(combined_df)} 筆")
        return len(results)
    else:
        print(f"\n[INFO] 3星彩: 無新資料")
        return 0


def update_star4_february():
    """補齊 4星彩 2月資料"""
    print("\n" + "=" * 80)
    print("[5/5] 補齊 4星彩 2月資料")
    print("=" * 80)
    
    file_path = "data/star4/star4_history.csv"
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
        if current.weekday() != 6:  # 週一~週六
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                number = fetch_star4_single_date(date_str)
                if number:
                    results.append({
                        'date': date_str,
                        'number': number
                    })
                    print(f"  [OK] {date_str}: {number}")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  [SKIP] {date_str}: {str(e)[:50]}")
        
        current += timedelta(days=1)
    
    if results:
        new_df = pd.DataFrame(results)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['date'])
        combined_df = combined_df.sort_values('date')
        
        Path("data/star4").mkdir(parents=True, exist_ok=True)
        combined_df.to_csv(file_path, index=False)
        
        print(f"\n[OK] 4星彩: 新增 {len(results)} 筆,總共 {len(combined_df)} 筆")
        return len(results)
    else:
        print(f"\n[INFO] 4星彩: 無新資料")
        return 0


if __name__ == "__main__":
    print("=" * 80)
    print("補齊所有遊戲 2026 年 2 月份資料")
    print("日期範圍: 2026-02-01 ~ 2026-02-10")
    print("=" * 80)
    
    total = 0
    total += update_539_february()
    total += update_lotto_february()
    total += update_power_february()
    total += update_star3_february()
    total += update_star4_february()
    
    print("\n" + "=" * 80)
    print("補齊完成!")
    print("=" * 80)
    print(f"總共新增: {total} 筆")
    print("=" * 80)
