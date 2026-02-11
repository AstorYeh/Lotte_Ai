# -*- coding: utf-8 -*-
"""
Pilio 網站爬蟲 - 修正版
根據實際網頁結構重新編寫
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.timezone_utils import get_taiwan_now
import time
import re


def parse_pilio_date(date_str):
    """解析 Pilio 的日期格式 (MM/DD)"""
    try:
        # 假設是當年或去年的資料
        current_year = get_taiwan_now().year
        month_day = date_str.strip()
        
        # 嘗試解析 MM/DD 格式
        if '/' in month_day:
            parts = month_day.split('/')
            if len(parts) == 2:
                month = int(parts[0])
                day = int(parts[1])
                
                # 先嘗試當年
                try:
                    date = datetime(current_year, month, day)
                    if date > get_taiwan_now():
                        # 如果日期在未來,使用去年
                        date = datetime(current_year - 1, month, day)
                    return date.strftime('%Y-%m-%d')
                except:
                    # 如果當年無效,嘗試去年
                    try:
                        date = datetime(current_year - 1, month, day)
                        return date.strftime('%Y-%m-%d')
                    except:
                        pass
    except:
        pass
    return None


def fetch_539_from_pilio_v2(max_pages=200):
    """從 Pilio 爬取 539 歷史資料 - 修正版"""
    print("\n" + "=" * 80)
    print("[1/5] 從 Pilio 爬取 539 歷史資料")
    print("=" * 80)
    
    results = []
    base_url = "https://www.pilio.idv.tw/lto539/list.asp"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?indexpage={page}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'big5'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 找到所有包含號碼的文字
            page_text = soup.get_text()
            
            # 使用正則表達式找到日期和號碼模式
            # 格式: MM/DD 後面跟著 5 個號碼
            lines = page_text.split('\n')
            
            page_count = 0
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # 檢查是否為日期行 (MM/DD)
                if re.match(r'^\d{2}/\d{2}$', line):
                    date_str = parse_pilio_date(line)
                    
                    # 往下找號碼行
                    if i + 2 < len(lines):
                        number_line = lines[i + 2].strip()
                        
                        # 提取號碼 (格式: 10, 11, 17, 22, 36)
                        numbers = re.findall(r'\d+', number_line)
                        numbers = [int(n) for n in numbers if 1 <= int(n) <= 39]
                        
                        if len(numbers) == 5 and date_str:
                            results.append({
                                'date': date_str,
                                'numbers': ','.join([str(n) for n in sorted(numbers)])
                            })
                            page_count += 1
                
                i += 1
            
            print(f"  頁面 {page}: 找到 {page_count} 筆")
            
            if page_count == 0 and page > 5:
                print(f"  連續無資料,停止爬取")
                break
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  [ERROR] 頁面 {page}: {e}")
            if page > 5:
                break
    
    # 儲存
    if results:
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/539_history.csv", index=False)
        print(f"\n[OK] 539 完成: {len(df)} 筆資料")
        print(f"  日期範圍: {df['date'].min()} ~ {df['date'].max()}")
    else:
        print(f"\n[WARNING] 539 無資料")
    
    return len(results) if results else 0


def fetch_lotto_from_pilio_v2(max_pages=200):
    """從 Pilio 爬取大樂透歷史資料 - 修正版"""
    print("\n" + "=" * 80)
    print("[2/5] 從 Pilio 爬取大樂透歷史資料")
    print("=" * 80)
    
    results = []
    base_url = "https://www.pilio.idv.tw/ltobig/list.asp"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?indexpage={page}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'big5'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            lines = page_text.split('\n')
            
            page_count = 0
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if re.match(r'^\d{2}/\d{2}$', line):
                    date_str = parse_pilio_date(line)
                    
                    if i + 2 < len(lines):
                        number_line = lines[i + 2].strip()
                        numbers = re.findall(r'\d+', number_line)
                        numbers = [int(n) for n in numbers if 1 <= int(n) <= 49]
                        
                        if len(numbers) >= 6 and date_str:
                            results.append({
                                'date': date_str,
                                'numbers': ','.join([str(n) for n in sorted(numbers[:6])])
                            })
                            page_count += 1
                
                i += 1
            
            print(f"  頁面 {page}: 找到 {page_count} 筆")
            
            if page_count == 0 and page > 5:
                break
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  [ERROR] 頁面 {page}: {e}")
            if page > 5:
                break
    
    if results:
        Path("data/lotto").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/lotto/lotto_history.csv", index=False)
        print(f"\n[OK] 大樂透完成: {len(df)} 筆資料")
        print(f"  日期範圍: {df['date'].min()} ~ {df['date'].max()}")
    else:
        print(f"\n[WARNING] 大樂透無資料")
    
    return len(results) if results else 0


def fetch_power_from_pilio_v2(max_pages=200):
    """從 Pilio 爬取威力彩歷史資料 - 修正版"""
    print("\n" + "=" * 80)
    print("[3/5] 從 Pilio 爬取威力彩歷史資料")
    print("=" * 80)
    
    results = []
    base_url = "https://www.pilio.idv.tw/lto/list.asp"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?indexpage={page}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'big5'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            lines = page_text.split('\n')
            
            page_count = 0
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if re.match(r'^\d{2}/\d{2}$', line):
                    date_str = parse_pilio_date(line)
                    
                    if i + 2 < len(lines):
                        number_line = lines[i + 2].strip()
                        numbers = re.findall(r'\d+', number_line)
                        numbers = [int(n) for n in numbers]
                        
                        # 威力彩: 前6個是第一區 (1-38), 第7個是第二區 (1-8)
                        if len(numbers) >= 7 and date_str:
                            zone1 = [n for n in numbers[:6] if 1 <= n <= 38]
                            zone2_candidates = [n for n in numbers[6:7] if 1 <= n <= 8]
                            
                            if len(zone1) == 6 and len(zone2_candidates) == 1:
                                results.append({
                                    'date': date_str,
                                    'zone1': str(sorted(zone1)),
                                    'zone2': zone2_candidates[0]
                                })
                                page_count += 1
                
                i += 1
            
            print(f"  頁面 {page}: 找到 {page_count} 筆")
            
            if page_count == 0 and page > 5:
                break
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  [ERROR] 頁面 {page}: {e}")
            if page > 5:
                break
    
    if results:
        Path("data/power").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/power/power_history.csv", index=False)
        print(f"\n[OK] 威力彩完成: {len(df)} 筆資料")
        print(f"  日期範圍: {df['date'].min()} ~ {df['date'].max()}")
    else:
        print(f"\n[WARNING] 威力彩無資料")
    
    return len(results) if results else 0


def fetch_star3_from_pilio_v2(max_pages=200):
    """從 Pilio 爬取 3星彩歷史資料 - 修正版"""
    print("\n" + "=" * 80)
    print("[4/5] 從 Pilio 爬取 3星彩歷史資料")
    print("=" * 80)
    
    results = []
    base_url = "https://www.pilio.idv.tw/lto/list3.asp"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?indexpage={page}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'big5'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            lines = page_text.split('\n')
            
            page_count = 0
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if re.match(r'^\d{2}/\d{2}$', line):
                    date_str = parse_pilio_date(line)
                    
                    if i + 2 < len(lines):
                        number_line = lines[i + 2].strip()
                        # 3星彩是3位數字
                        match = re.search(r'\b(\d{3})\b', number_line)
                        
                        if match and date_str:
                            results.append({
                                'date': date_str,
                                'number': match.group(1)
                            })
                            page_count += 1
                
                i += 1
            
            print(f"  頁面 {page}: 找到 {page_count} 筆")
            
            if page_count == 0 and page > 5:
                break
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  [ERROR] 頁面 {page}: {e}")
            if page > 5:
                break
    
    if results:
        Path("data/star3").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/star3/star3_history.csv", index=False)
        print(f"\n[OK] 3星彩完成: {len(df)} 筆資料")
        print(f"  日期範圍: {df['date'].min()} ~ {df['date'].max()}")
    else:
        print(f"\n[WARNING] 3星彩無資料")
    
    return len(results) if results else 0


def fetch_star4_from_pilio_v2(max_pages=200):
    """從 Pilio 爬取 4星彩歷史資料 - 修正版"""
    print("\n" + "=" * 80)
    print("[5/5] 從 Pilio 爬取 4星彩歷史資料")
    print("=" * 80)
    
    results = []
    base_url = "https://www.pilio.idv.tw/lto/list4.asp"
    
    for page in range(1, max_pages + 1):
        try:
            url = f"{base_url}?indexpage={page}"
            
            response = requests.get(url, timeout=10)
            response.encoding = 'big5'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            lines = page_text.split('\n')
            
            page_count = 0
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if re.match(r'^\d{2}/\d{2}$', line):
                    date_str = parse_pilio_date(line)
                    
                    if i + 2 < len(lines):
                        number_line = lines[i + 2].strip()
                        # 4星彩是4位數字
                        match = re.search(r'\b(\d{4})\b', number_line)
                        
                        if match and date_str:
                            results.append({
                                'date': date_str,
                                'number': match.group(1)
                            })
                            page_count += 1
                
                i += 1
            
            print(f"  頁面 {page}: 找到 {page_count} 筆")
            
            if page_count == 0 and page > 5:
                break
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"  [ERROR] 頁面 {page}: {e}")
            if page > 5:
                break
    
    if results:
        Path("data/star4").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(results)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/star4/star4_history.csv", index=False)
        print(f"\n[OK] 4星彩完成: {len(df)} 筆資料")
        print(f"  日期範圍: {df['date'].min()} ~ {df['date'].max()}")
    else:
        print(f"\n[WARNING] 4星彩無資料")
    
    return len(results) if results else 0


if __name__ == "__main__":
    print("=" * 80)
    print("從 Pilio 網站爬取歷史資料 - 修正版")
    print("資料來源: https://www.pilio.idv.tw/")
    print("=" * 80)
    
    start_time = time.time()
    total_records = 0
    
    # 依序爬取各遊戲 (每個遊戲最多200頁)
    total_records += fetch_539_from_pilio_v2(200)
    total_records += fetch_lotto_from_pilio_v2(200)
    total_records += fetch_power_from_pilio_v2(200)
    total_records += fetch_star3_from_pilio_v2(200)
    total_records += fetch_star4_from_pilio_v2(200)
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("爬取完成!")
    print("=" * 80)
    print(f"總筆數: {total_records}")
    print(f"耗時: {elapsed/60:.1f} 分鐘")
    print("=" * 80)
