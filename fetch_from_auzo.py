# -*- coding: utf-8 -*-
"""
從 lotto.auzo.tw 補齊所有遊戲的 2 月份資料
新的資料來源,更新更即時
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
import time
import sys

# 設置輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def fetch_lotto_from_auzo():
    """從 auzo.tw 爬取大樂透最新資料"""
    print("\n" + "=" * 80)
    print("[1/4] 從 auzo.tw 爬取大樂透資料")
    print("=" * 80)
    
    url = "https://lotto.auzo.tw/biglotto"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 載入現有資料
        file_path = "data/lotto/lotto_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
            print(f"  現有資料: {len(existing_df)} 筆")
            existing_dates = set(existing_df['date'].values)
        else:
            existing_df = pd.DataFrame()
            existing_dates = set()
        
        results = []
        
        # 查找所有開獎記錄
        # 通常在表格中
        rows = soup.find_all('tr')
        
        for row in rows[:20]:  # 只取最近20期
            try:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                
                # 提取日期
                date_text = cols[0].get_text(strip=True)
                date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                    
                    # 跳過已存在的日期
                    if date_str in existing_dates:
                        continue
                    
                    # 提取號碼
                    numbers = []
                    for col in cols:
                        text = col.get_text(strip=True)
                        if text.isdigit():
                            num = int(text)
                            if 1 <= num <= 49 and len(numbers) < 6:
                                numbers.append(num)
                    
                    if len(numbers) == 6:
                        results.append({
                            'date': date_str,
                            'numbers': ','.join([str(n) for n in sorted(numbers)])
                        })
                        print(f"  [OK] {date_str}: {sorted(numbers)}")
            except:
                pass
        
        # 合併並儲存
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
            
    except Exception as e:
        print(f"[ERROR] 大樂透爬取失敗: {e}")
        return 0


def fetch_power_from_auzo():
    """從 auzo.tw 爬取威力彩最新資料"""
    print("\n" + "=" * 80)
    print("[2/4] 從 auzo.tw 爬取威力彩資料")
    print("=" * 80)
    
    url = "https://lotto.auzo.tw/power"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        file_path = "data/power/power_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
            print(f"  現有資料: {len(existing_df)} 筆")
            existing_dates = set(existing_df['date'].values)
        else:
            existing_df = pd.DataFrame()
            existing_dates = set()
        
        results = []
        rows = soup.find_all('tr')
        
        for row in rows[:20]:
            try:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue
                
                date_text = cols[0].get_text(strip=True)
                date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                    
                    if date_str in existing_dates:
                        continue
                    
                    # 威力彩: 前6個是第一區,第7個是第二區
                    zone1 = []
                    zone2 = None
                    
                    for col in cols:
                        text = col.get_text(strip=True)
                        if text.isdigit():
                            num = int(text)
                            if len(zone1) < 6 and 1 <= num <= 38:
                                zone1.append(num)
                            elif len(zone1) == 6 and 1 <= num <= 8:
                                zone2 = num
                                break
                    
                    if len(zone1) == 6 and zone2 is not None:
                        results.append({
                            'date': date_str,
                            'zone1': str(sorted(zone1)),
                            'zone2': zone2
                        })
                        print(f"  [OK] {date_str}: 第一區 {sorted(zone1)} + 第二區 {zone2}")
            except:
                pass
        
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
            
    except Exception as e:
        print(f"[ERROR] 威力彩爬取失敗: {e}")
        return 0


def fetch_star3_from_auzo():
    """從 auzo.tw 爬取 3星彩最新資料"""
    print("\n" + "=" * 80)
    print("[3/4] 從 auzo.tw 爬取 3星彩資料")
    print("=" * 80)
    
    url = "https://lotto.auzo.tw/lotto_historylist_three-star.html"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        file_path = "data/star3/star3_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
            print(f"  現有資料: {len(existing_df)} 筆")
            existing_dates = set(existing_df['date'].values)
        else:
            existing_df = pd.DataFrame()
            existing_dates = set()
        
        results = []
        rows = soup.find_all('tr')
        
        for row in rows[:20]:
            try:
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue
                
                date_text = cols[0].get_text(strip=True)
                date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                    
                    if date_str in existing_dates:
                        continue
                    
                    # 3星彩是3位數字
                    for col in cols[1:]:
                        text = col.get_text(strip=True)
                        if len(text) == 3 and text.isdigit():
                            results.append({
                                'date': date_str,
                                'number': text
                            })
                            print(f"  [OK] {date_str}: {text}")
                            break
            except:
                pass
        
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
            
    except Exception as e:
        print(f"[ERROR] 3星彩爬取失敗: {e}")
        return 0


def fetch_star4_from_auzo():
    """從 auzo.tw 爬取 4星彩最新資料"""
    print("\n" + "=" * 80)
    print("[4/4] 從 auzo.tw 爬取 4星彩資料")
    print("=" * 80)
    
    url = "https://lotto.auzo.tw/lotto_historylist_four-star.html"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        file_path = "data/star4/star4_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
            print(f"  現有資料: {len(existing_df)} 筆")
            existing_dates = set(existing_df['date'].values)
        else:
            existing_df = pd.DataFrame()
            existing_dates = set()
        
        results = []
        rows = soup.find_all('tr')
        
        for row in rows[:20]:
            try:
                cols = row.find_all('td')
                if len(cols) < 2:
                    continue
                
                date_text = cols[0].get_text(strip=True)
                date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                    
                    if date_str in existing_dates:
                        continue
                    
                    # 4星彩是4位數字
                    for col in cols[1:]:
                        text = col.get_text(strip=True)
                        if len(text) == 4 and text.isdigit():
                            results.append({
                                'date': date_str,
                                'number': text
                            })
                            print(f"  [OK] {date_str}: {text}")
                            break
            except:
                pass
        
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
            
    except Exception as e:
        print(f"[ERROR] 4星彩爬取失敗: {e}")
        return 0


if __name__ == "__main__":
    print("=" * 80)
    print("從 lotto.auzo.tw 補齊所有遊戲資料")
    print("=" * 80)
    
    total = 0
    total += fetch_lotto_from_auzo()
    total += fetch_power_from_auzo()
    total += fetch_star3_from_auzo()
    total += fetch_star4_from_auzo()
    
    print("\n" + "=" * 80)
    print("補齊完成!")
    print("=" * 80)
    print(f"總共新增: {total} 筆")
    print("=" * 80)
