# -*- coding: utf-8 -*-
"""
從台灣彩券官網補齊最新資料
爬取各遊戲的最新開獎號碼
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
import urllib3

# 抑制 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_latest_power():
    """爬取威力彩最新資料"""
    print("\n" + "=" * 80)
    print("爬取威力彩最新資料")
    print("=" * 80)
    
    url = "https://www.taiwanlottery.com/lotto/result/super_lotto638"
    
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到開獎號碼區域
        results = []
        
        # 查找所有包含開獎資訊的元素
        # 台灣彩券網站通常使用特定的 class 或 id
        date_elements = soup.find_all(string=re.compile(r'\d{4}/\d{2}/\d{2}'))
        
        for date_elem in date_elements[:5]:  # 只取最近5期
            try:
                # 解析日期
                date_text = date_elem.strip()
                date_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    
                    # 找到號碼 (通常在附近的元素中)
                    parent = date_elem.parent
                    for _ in range(5):  # 向上查找5層
                        if parent:
                            # 查找號碼球
                            balls = parent.find_all('div', class_=re.compile(r'ball'))
                            
                            if len(balls) >= 7:
                                zone1 = []
                                zone2 = None
                                
                                for i, ball in enumerate(balls[:7]):
                                    num_text = ball.get_text(strip=True)
                                    if num_text.isdigit():
                                        num = int(num_text)
                                        if i < 6:
                                            zone1.append(num)
                                        else:
                                            zone2 = num
                                
                                if len(zone1) == 6 and zone2 is not None:
                                    results.append({
                                        'date': date_str,
                                        'zone1': str(sorted(zone1)),
                                        'zone2': zone2
                                    })
                                    print(f"  {date_str}: 第一區 {sorted(zone1)} + 第二區 {zone2}")
                                    break
                            
                            parent = parent.parent
                        else:
                            break
            except Exception as e:
                pass
        
        # 載入現有資料
        file_path = "data/power/power_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
        else:
            existing_df = pd.DataFrame()
        
        # 合併新資料
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
            
    except Exception as e:
        print(f"[ERROR] 威力彩爬取失敗: {e}")
        return 0


def fetch_latest_lotto():
    """爬取大樂透最新資料"""
    print("\n" + "=" * 80)
    print("爬取大樂透最新資料")
    print("=" * 80)
    
    url = "https://www.taiwanlottery.com/lotto/result/lotto649"
    
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        date_elements = soup.find_all(string=re.compile(r'\d{4}/\d{2}/\d{2}'))
        
        for date_elem in date_elements[:5]:
            try:
                date_text = date_elem.strip()
                date_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    
                    parent = date_elem.parent
                    for _ in range(5):
                        if parent:
                            balls = parent.find_all('div', class_=re.compile(r'ball'))
                            
                            if len(balls) >= 6:
                                numbers = []
                                
                                for ball in balls[:6]:
                                    num_text = ball.get_text(strip=True)
                                    if num_text.isdigit():
                                        numbers.append(int(num_text))
                                
                                if len(numbers) == 6:
                                    results.append({
                                        'date': date_str,
                                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                                    })
                                    print(f"  {date_str}: {sorted(numbers)}")
                                    break
                            
                            parent = parent.parent
                        else:
                            break
            except:
                pass
        
        file_path = "data/lotto/lotto_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
        else:
            existing_df = pd.DataFrame()
        
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
            
    except Exception as e:
        print(f"[ERROR] 大樂透爬取失敗: {e}")
        return 0


def fetch_latest_539():
    """爬取 539 最新資料"""
    print("\n" + "=" * 80)
    print("爬取 539 最新資料")
    print("=" * 80)
    
    url = "https://www.taiwanlottery.com/lotto/result/daily539"
    
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        date_elements = soup.find_all(string=re.compile(r'\d{4}/\d{2}/\d{2}'))
        
        for date_elem in date_elements[:5]:
            try:
                date_text = date_elem.strip()
                date_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', date_text)
                
                if date_match:
                    date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                    
                    parent = date_elem.parent
                    for _ in range(5):
                        if parent:
                            balls = parent.find_all('div', class_=re.compile(r'ball'))
                            
                            if len(balls) >= 5:
                                numbers = []
                                
                                for ball in balls[:5]:
                                    num_text = ball.get_text(strip=True)
                                    if num_text.isdigit():
                                        numbers.append(int(num_text))
                                
                                if len(numbers) == 5:
                                    results.append({
                                        'date': date_str,
                                        'numbers': ','.join([str(n) for n in sorted(numbers)])
                                    })
                                    print(f"  {date_str}: {sorted(numbers)}")
                                    break
                            
                            parent = parent.parent
                        else:
                            break
            except:
                pass
        
        file_path = "data/539_history.csv"
        if Path(file_path).exists():
            existing_df = pd.read_csv(file_path)
        else:
            existing_df = pd.DataFrame()
        
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
            
    except Exception as e:
        print(f"[ERROR] 539 爬取失敗: {e}")
        return 0


if __name__ == "__main__":
    print("=" * 80)
    print("從台灣彩券官網補齊最新資料")
    print("=" * 80)
    
    total = 0
    total += fetch_latest_539()
    total += fetch_latest_lotto()
    total += fetch_latest_power()
    
    print("\n" + "=" * 80)
    print("完成!")
    print("=" * 80)
    print(f"總共新增: {total} 筆")
    print("=" * 80)
