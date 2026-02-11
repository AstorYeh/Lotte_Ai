# -*- coding: utf-8 -*-
"""
威力彩爬蟲
從 Auzonet 爬取威力彩開獎資料
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional


def fetch_power_single_date(date_str: str) -> Optional[dict]:
    """
    爬取指定日期的威力彩開獎號碼
    
    Args:
        date_str: 日期字串 (YYYY-MM-DD)
    
    Returns:
        dict: {'date': str, 'zone1': List[int], 'zone2': int} 或 None
    """
    try:
        # 解析日期
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        year = dt.year
        month = dt.month
        
        # 威力彩網址格式: https://lotto.auzonet.com/pwr/list_YYYY_M.html
        url = f"https://lotto.auzonet.com/pwr/list_{year}_{month}.html"
        
        print(f"[INFO] 查詢日期: {date_str}")
        print(f"[INFO] 目標網址: {url}")
        
        # 發送請求
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"[ERROR] HTTP {response.status_code}")
            return None
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有開獎記錄
        rows = soup.find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            
            # 第一欄是日期
            date_cell = cols[0].get_text(strip=True)
            
            # 檢查是否為目標日期
            if date_str in date_cell or date_str.replace('-', '/') in date_cell:
                # 找號碼球
                balls = row.find_all('div', class_='ball_tx')
                
                if len(balls) >= 7:  # 第一區6個 + 第二區1個
                    zone1 = []
                    for i in range(6):
                        num = int(balls[i].get_text(strip=True))
                        zone1.append(num)
                    
                    zone2 = int(balls[6].get_text(strip=True))
                    
                    result = {
                        'date': date_str,
                        'zone1': sorted(zone1),
                        'zone2': zone2
                    }
                    
                    print(f"[SUCCESS] 威力彩 {date_str} 開獎: 第一區 {zone1} + 第二區 {zone2}")
                    return result
        
        print(f"[WARNING] 未找到 {date_str} 的開獎資料")
        return None
        
    except Exception as e:
        print(f"[ERROR] 爬取失敗: {e}")
        return None


def fetch_power_range(start_date: str, end_date: str) -> List[dict]:
    """
    爬取日期範圍內的威力彩開獎號碼
    
    Args:
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
    
    Returns:
        List[dict]: 開獎記錄列表
    """
    from datetime import timedelta
    
    results = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 威力彩開獎日: 週一(0)、週四(3)
    power_days = [0, 3]
    
    while current <= end:
        # 只在開獎日爬取
        if current.weekday() in power_days:
            date_str = current.strftime('%Y-%m-%d')
            result = fetch_power_single_date(date_str)
            
            if result:
                results.append(result)
        
        current += timedelta(days=1)
    
    print(f"\n[SUMMARY] 共爬取 {len(results)} 筆威力彩資料")
    return results


if __name__ == "__main__":
    # 測試爬蟲
    print("=" * 60)
    print("威力彩爬蟲測試")
    print("=" * 60)
    
    # 測試單日爬取
    result = fetch_power_single_date("2026-02-06")  # 週四
    
    if result:
        print(f"\n第一區: {result['zone1']}")
        print(f"第二區: {result['zone2']}")
