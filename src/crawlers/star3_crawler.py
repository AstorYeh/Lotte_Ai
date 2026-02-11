# -*- coding: utf-8 -*-
"""
3星彩爬蟲
從 Auzonet 爬取3星彩開獎資料
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional


def fetch_star3_single_date(date_str: str) -> Optional[dict]:
    """
    爬取指定日期的3星彩開獎號碼
    
    Args:
        date_str: 日期字串 (YYYY-MM-DD)
    
    Returns:
        dict: {'date': str, 'number': str} 或 None (number 為三位數字字串,如 "123")
    """
    try:
        # 解析日期
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        year = dt.year
        month = dt.month
        
        # 3星彩網址格式: https://lotto.auzonet.com/3star/list_YYYY_M.html
        url = f"https://lotto.auzonet.com/3star/list_{year}_{month}.html"
        
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
                # 找號碼球 (3個數字)
                balls = row.find_all('div', class_='ball_tx')
                
                if len(balls) >= 3:
                    digits = []
                    for i in range(3):
                        digit = balls[i].get_text(strip=True)
                        digits.append(digit)
                    
                    number = ''.join(digits)
                    
                    result = {
                        'date': date_str,
                        'number': number
                    }
                    
                    print(f"[SUCCESS] 3星彩 {date_str} 開獎: {number}")
                    return result
        
        print(f"[WARNING] 未找到 {date_str} 的開獎資料")
        return None
        
    except Exception as e:
        print(f"[ERROR] 爬取失敗: {e}")
        return None


def fetch_star3_range(start_date: str, end_date: str) -> List[dict]:
    """
    爬取日期範圍內的3星彩開獎號碼
    
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
    
    while current <= end:
        # 跳過週日
        if current.weekday() != 6:
            date_str = current.strftime('%Y-%m-%d')
            result = fetch_star3_single_date(date_str)
            
            if result:
                results.append(result)
        
        current += timedelta(days=1)
    
    print(f"\n[SUMMARY] 共爬取 {len(results)} 筆3星彩資料")
    return results


if __name__ == "__main__":
    # 測試爬蟲
    print("=" * 60)
    print("3星彩爬蟲測試")
    print("=" * 60)
    
    # 測試單日爬取
    result = fetch_star3_single_date("2026-02-08")  # 週六
    
    if result:
        print(f"\n開獎號碼: {result['number']}")
