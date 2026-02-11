# -*- coding: utf-8 -*-
"""
批次爬取所有遊戲的 2025 年完整歷史資料
優化版 - 使用並行處理加速
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 導入爬蟲
from src.auzonet_crawler import fetch_auzonet_single_date
from src.crawlers.lotto_crawler import fetch_lotto_single_date
from src.crawlers.power_crawler import fetch_power_single_date
from src.crawlers.star3_crawler import fetch_star3_single_date
from src.crawlers.star4_crawler import fetch_star4_single_date


def crawl_539_history():
    """爬取 539 歷史資料"""
    print("\n" + "=" * 80)
    print("[1/5] 爬取 539 歷史資料")
    print("=" * 80)
    
    results = []
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 9)
    current = start
    
    dates_to_crawl = []
    while current <= end:
        if current.weekday() != 6:  # 跳過週日
            dates_to_crawl.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    print(f"預計爬取 {len(dates_to_crawl)} 天的資料...")
    
    # 並行爬取
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {
            executor.submit(fetch_auzonet_single_date, date): date 
            for date in dates_to_crawl
        }
        
        for i, future in enumerate(as_completed(future_to_date), 1):
            date = future_to_date[future]
            try:
                numbers = future.result()
                if numbers and len(numbers) == 5:
                    results.append({
                        'date': date,
                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                    })
                
                if i % 50 == 0:
                    print(f"  進度: {i}/{len(dates_to_crawl)} ({i*100//len(dates_to_crawl)}%)")
            except Exception as e:
                print(f"  錯誤 {date}: {e}")
    
    # 儲存
    df = pd.DataFrame(results)
    df = df.sort_values('date')
    df.to_csv("data/539_history.csv", index=False)
    print(f"\n[OK] 539 完成: {len(df)} 筆資料")
    return len(df)


def crawl_lotto_history():
    """爬取大樂透歷史資料"""
    print("\n" + "=" * 80)
    print("[2/5] 爬取大樂透歷史資料")
    print("=" * 80)
    
    results = []
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 9)
    current = start
    
    dates_to_crawl = []
    while current <= end:
        if current.weekday() in [1, 4]:  # 週二、週五
            dates_to_crawl.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    print(f"預計爬取 {len(dates_to_crawl)} 天的資料...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {
            executor.submit(fetch_lotto_single_date, date): date 
            for date in dates_to_crawl
        }
        
        for i, future in enumerate(as_completed(future_to_date), 1):
            date = future_to_date[future]
            try:
                numbers = future.result()
                if numbers and len(numbers) == 6:
                    results.append({
                        'date': date,
                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                    })
                
                if i % 20 == 0:
                    print(f"  進度: {i}/{len(dates_to_crawl)} ({i*100//len(dates_to_crawl)}%)")
            except Exception as e:
                print(f"  錯誤 {date}: {e}")
    
    Path("data/lotto").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df = df.sort_values('date')
    df.to_csv("data/lotto/lotto_history.csv", index=False)
    print(f"\n[OK] 大樂透完成: {len(df)} 筆資料")
    return len(df)


def crawl_power_history():
    """爬取威力彩歷史資料"""
    print("\n" + "=" * 80)
    print("[3/5] 爬取威力彩歷史資料")
    print("=" * 80)
    
    results = []
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 9)
    current = start
    
    dates_to_crawl = []
    while current <= end:
        if current.weekday() in [0, 3]:  # 週一、週四
            dates_to_crawl.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    print(f"預計爬取 {len(dates_to_crawl)} 天的資料...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {
            executor.submit(fetch_power_single_date, date): date 
            for date in dates_to_crawl
        }
        
        for i, future in enumerate(as_completed(future_to_date), 1):
            date = future_to_date[future]
            try:
                data = future.result()
                if data and 'zone1' in data and 'zone2' in data:
                    results.append({
                        'date': date,
                        'zone1': str(data['zone1']),
                        'zone2': data['zone2']
                    })
                
                if i % 20 == 0:
                    print(f"  進度: {i}/{len(dates_to_crawl)} ({i*100//len(dates_to_crawl)}%)")
            except Exception as e:
                print(f"  錯誤 {date}: {e}")
    
    Path("data/power").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df = df.sort_values('date')
    df.to_csv("data/power/power_history.csv", index=False)
    print(f"\n[OK] 威力彩完成: {len(df)} 筆資料")
    return len(df)


def crawl_star3_history():
    """爬取 3星彩歷史資料"""
    print("\n" + "=" * 80)
    print("[4/5] 爬取 3星彩歷史資料")
    print("=" * 80)
    
    results = []
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 9)
    current = start
    
    dates_to_crawl = []
    while current <= end:
        if current.weekday() != 6:  # 週一~週六
            dates_to_crawl.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    print(f"預計爬取 {len(dates_to_crawl)} 天的資料...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {
            executor.submit(fetch_star3_single_date, date): date 
            for date in dates_to_crawl
        }
        
        for i, future in enumerate(as_completed(future_to_date), 1):
            date = future_to_date[future]
            try:
                number = future.result()
                if number:
                    results.append({
                        'date': date,
                        'number': number
                    })
                
                if i % 50 == 0:
                    print(f"  進度: {i}/{len(dates_to_crawl)} ({i*100//len(dates_to_crawl)}%)")
            except Exception as e:
                print(f"  錯誤 {date}: {e}")
    
    Path("data/star3").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df = df.sort_values('date')
    df.to_csv("data/star3/star3_history.csv", index=False)
    print(f"\n[OK] 3星彩完成: {len(df)} 筆資料")
    return len(df)


def crawl_star4_history():
    """爬取 4星彩歷史資料"""
    print("\n" + "=" * 80)
    print("[5/5] 爬取 4星彩歷史資料")
    print("=" * 80)
    
    results = []
    start = datetime(2025, 1, 1)
    end = datetime(2026, 2, 9)
    current = start
    
    dates_to_crawl = []
    while current <= end:
        if current.weekday() != 6:  # 週一~週六
            dates_to_crawl.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    print(f"預計爬取 {len(dates_to_crawl)} 天的資料...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_date = {
            executor.submit(fetch_star4_single_date, date): date 
            for date in dates_to_crawl
        }
        
        for i, future in enumerate(as_completed(future_to_date), 1):
            date = future_to_date[future]
            try:
                number = future.result()
                if number:
                    results.append({
                        'date': date,
                        'number': number
                    })
                
                if i % 50 == 0:
                    print(f"  進度: {i}/{len(dates_to_crawl)} ({i*100//len(dates_to_crawl)}%)")
            except Exception as e:
                print(f"  錯誤 {date}: {e}")
    
    Path("data/star4").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df = df.sort_values('date')
    df.to_csv("data/star4/star4_history.csv", index=False)
    print(f"\n[OK] 4星彩完成: {len(df)} 筆資料")
    return len(df)


if __name__ == "__main__":
    print("=" * 80)
    print("批次爬取 2025 年完整歷史資料")
    print("=" * 80)
    
    start_time = time.time()
    
    total_records = 0
    
    # 依序爬取各遊戲
    total_records += crawl_539_history()
    total_records += crawl_lotto_history()
    total_records += crawl_power_history()
    total_records += crawl_star3_history()
    total_records += crawl_star4_history()
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("爬取完成!")
    print("=" * 80)
    print(f"總筆數: {total_records}")
    print(f"耗時: {elapsed:.1f} 秒")
    print("=" * 80)
