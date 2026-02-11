# -*- coding: utf-8 -*-
"""
智能批次爬取歷史資料
自動從 auzonet.com 爬取所有遊戲的歷史資料
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

# 導入爬蟲
from src.auzonet_crawler import fetch_auzonet_single_date
from src.crawlers.lotto_crawler import fetch_lotto_single_date
from src.crawlers.power_crawler import fetch_power_single_date
from src.crawlers.star3_crawler import fetch_star3_single_date
from src.crawlers.star4_crawler import fetch_star4_single_date


def crawl_539_history(start_date="2024-01-01", end_date="2026-01-31"):
    """爬取 539 歷史資料"""
    print("\n" + "=" * 80)
    print("[1/5] 爬取 539 歷史資料")
    print("=" * 80)
    
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    total_days = (end - current).days + 1
    processed = 0
    
    while current <= end:
        if current.weekday() != 6:  # 跳過週日
            date_str = current.strftime('%Y-%m-%d')
            
            try:
                numbers = fetch_auzonet_single_date(date_str)
                if numbers and len(numbers) == 5:
                    results.append({
                        'date': date_str,
                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                    })
                    print(f"  [OK] {date_str}: {numbers}")
                
                time.sleep(0.5)  # 避免請求過快
                
            except Exception as e:
                print(f"  [ERROR] {date_str}: {e}")
        
        processed += 1
        if processed % 30 == 0:
            print(f"  進度: {processed}/{total_days} ({processed*100//total_days}%)")
        
        current += timedelta(days=1)
    
    # 儲存
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('date')
        df.to_csv("data/539_history.csv", index=False)
        print(f"\n[OK] 539 完成: {len(df)} 筆資料")
    else:
        print(f"\n[WARNING] 539 無資料")
    
    return len(results)


def crawl_lotto_history(start_date="2024-01-01", end_date="2026-01-31"):
    """爬取大樂透歷史資料"""
    print("\n" + "=" * 80)
    print("[2/5] 爬取大樂透歷史資料")
    print("=" * 80)
    
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current <= end:
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
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  [ERROR] {date_str}: {e}")
        
        current += timedelta(days=1)
    
    # 儲存
    if results:
        Path("data/lotto").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.sort_values('date')
        df.to_csv("data/lotto/lotto_history.csv", index=False)
        print(f"\n[OK] 大樂透完成: {len(df)} 筆資料")
    else:
        print(f"\n[WARNING] 大樂透無資料")
    
    return len(results)


def crawl_power_history(start_date="2024-01-01", end_date="2026-01-31"):
    """爬取威力彩歷史資料"""
    print("\n" + "=" * 80)
    print("[3/5] 爬取威力彩歷史資料")
    print("=" * 80)
    
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current <= end:
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
                    print(f"  [OK] {date_str}: {data['zone1']} + {data['zone2']}")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  [ERROR] {date_str}: {e}")
        
        current += timedelta(days=1)
    
    # 儲存
    if results:
        Path("data/power").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.sort_values('date')
        df.to_csv("data/power/power_history.csv", index=False)
        print(f"\n[OK] 威力彩完成: {len(df)} 筆資料")
    else:
        print(f"\n[WARNING] 威力彩無資料")
    
    return len(results)


def crawl_star3_history(start_date="2024-01-01", end_date="2026-01-31"):
    """爬取 3星彩歷史資料"""
    print("\n" + "=" * 80)
    print("[4/5] 爬取 3星彩歷史資料")
    print("=" * 80)
    
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current <= end:
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
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  [ERROR] {date_str}: {e}")
        
        current += timedelta(days=1)
    
    # 儲存
    if results:
        Path("data/star3").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.sort_values('date')
        df.to_csv("data/star3/star3_history.csv", index=False)
        print(f"\n[OK] 3星彩完成: {len(df)} 筆資料")
    else:
        print(f"\n[WARNING] 3星彩無資料")
    
    return len(results)


def crawl_star4_history(start_date="2024-01-01", end_date="2026-01-31"):
    """爬取 4星彩歷史資料"""
    print("\n" + "=" * 80)
    print("[5/5] 爬取 4星彩歷史資料")
    print("=" * 80)
    
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current <= end:
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
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  [ERROR] {date_str}: {e}")
        
        current += timedelta(days=1)
    
    # 儲存
    if results:
        Path("data/star4").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.sort_values('date')
        df.to_csv("data/star4/star4_history.csv", index=False)
        print(f"\n[OK] 4星彩完成: {len(df)} 筆資料")
    else:
        print(f"\n[WARNING] 4星彩無資料")
    
    return len(results)


if __name__ == "__main__":
    print("=" * 80)
    print("智能批次爬取歷史資料")
    print("從 auzonet.com 爬取真實開獎資料")
    print("=" * 80)
    
    # 設定日期範圍 (從 2024 年開始)
    start = "2024-01-01"
    end = "2026-01-31"
    
    print(f"\n日期範圍: {start} ~ {end}")
    print("注意: 2026 年資料可能尚未上線,會自動跳過")
    print()
    
    start_time = time.time()
    total_records = 0
    
    # 依序爬取各遊戲
    total_records += crawl_539_history(start, end)
    total_records += crawl_lotto_history(start, end)
    total_records += crawl_power_history(start, end)
    total_records += crawl_star3_history(start, end)
    total_records += crawl_star4_history(start, end)
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("爬取完成!")
    print("=" * 80)
    print(f"總筆數: {total_records}")
    print(f"耗時: {elapsed/60:.1f} 分鐘")
    print("=" * 80)
