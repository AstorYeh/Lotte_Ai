# -*- coding: utf-8 -*-
"""
修正版:從 lotto.auzo.tw 正確爬取所有遊戲的歷史資料
使用歷史列表頁面而非首頁
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def fetch_power_history():
    """從威力彩歷史列表爬取 2 月份資料"""
    print("\n" + "=" * 80)
    print("爬取威力彩 2 月份歷史資料")
    print("=" * 80)
    
    # 使用歷史列表頁面
    url = "https://lotto.auzo.tw/power/list_2026_2.html"
    
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
        
        # 查找所有表格行
        rows = soup.find_all('tr')
        
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) < 8:
                    continue
                
                # 第一欄是日期
                date_text = cols[0].get_text(strip=True)
                date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_text)
                
                if not date_match:
                    continue
                
                date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                
                if date_str in existing_dates:
                    continue
                
                # 威力彩格式: 第一區6個號碼 + 第二區1個號碼
                zone1 = []
                zone2 = None
                
                # 從第2欄開始提取號碼
                for i in range(1, 8):
                    if i < len(cols):
                        text = cols[i].get_text(strip=True)
                        if text.isdigit():
                            num = int(text)
                            if i <= 6:  # 第一區
                                if 1 <= num <= 38:
                                    zone1.append(num)
                            else:  # 第二區
                                if 1 <= num <= 8:
                                    zone2 = num
                
                if len(zone1) == 6 and zone2 is not None:
                    results.append({
                        'date': date_str,
                        'zone1': str(sorted(zone1)),
                        'zone2': zone2
                    })
                    print(f"  [OK] {date_str}: 第一區 {sorted(zone1)} + 第二區 {zone2}")
                    
            except Exception as e:
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


def fetch_lotto_history():
    """從大樂透歷史列表爬取 2 月份資料"""
    print("\n" + "=" * 80)
    print("爬取大樂透 2 月份歷史資料")
    print("=" * 80)
    
    url = "https://lotto.auzo.tw/biglotto/list_2026_2.html"
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        file_path = "data/lotto/lotto_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
            print(f"  現有資料: {len(existing_df)} 筆")
            existing_dates = set(existing_df['date'].values)
        else:
            existing_df = pd.DataFrame()
            existing_dates = set()
        
        results = []
        rows = soup.find_all('tr')
        
        for row in rows:
            try:
                cols = row.find_all('td')
                if len(cols) < 7:
                    continue
                
                date_text = cols[0].get_text(strip=True)
                date_match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_text)
                
                if not date_match:
                    continue
                
                date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
                
                if date_str in existing_dates:
                    continue
                
                # 大樂透: 6個號碼
                numbers = []
                
                for i in range(1, 7):
                    if i < len(cols):
                        text = cols[i].get_text(strip=True)
                        if text.isdigit():
                            num = int(text)
                            if 1 <= num <= 49:
                                numbers.append(num)
                
                if len(numbers) == 6:
                    results.append({
                        'date': date_str,
                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                    })
                    print(f"  [OK] {date_str}: {sorted(numbers)}")
                    
            except:
                pass
        
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


if __name__ == "__main__":
    print("=" * 80)
    print("修正版:從 lotto.auzo.tw 爬取 2 月份歷史資料")
    print("=" * 80)
    
    # 先清除錯誤的資料
    print("\n清除錯誤的 2 月份資料...")
    
    # 威力彩:移除 2026-02-09 的錯誤資料
    power_file = "data/power/power_history.csv"
    if Path(power_file).exists():
        df = pd.read_csv(power_file)
        df = df[df['date'] != '2026-02-09']
        df.to_csv(power_file, index=False)
        print("  [OK] 已清除威力彩錯誤資料")
    
    # 大樂透:移除 2026-02-06 的錯誤資料
    lotto_file = "data/lotto/lotto_history.csv"
    if Path(lotto_file).exists():
        df = pd.read_csv(lotto_file)
        df = df[df['date'] != '2026-02-06']
        df.to_csv(lotto_file, index=False)
        print("  [OK] 已清除大樂透錯誤資料")
    
    total = 0
    total += fetch_lotto_history()
    total += fetch_power_history()
    
    print("\n" + "=" * 80)
    print("修正完成!")
    print("=" * 80)
    print(f"總共新增: {total} 筆")
    print("=" * 80)
