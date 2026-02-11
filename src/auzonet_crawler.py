# -*- coding: utf-8 -*-
"""
Auzonet 539 爬蟲模組
從 https://lotto.auzonet.com/daily539 抓取開獎資料
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def fetch_auzonet_single_date(target_date):
    """
    從 auzonet 抓取指定日期的開獎號碼
    
    Args:
        target_date: 目標日期 (datetime 或 str, 格式: YYYY-MM-DD)
    
    Returns:
        list: 開獎號碼列表 [n1, n2, n3, n4, n5] 或 None (找不到)
    """
    # 轉換日期格式
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
    
    target_str = target_date.strftime("%Y-%m-%d")
    year = target_date.year
    month = target_date.month
    
    # 構建 URL - 使用月份列表頁
    url = f"https://lotto.auzonet.com/daily539/list_{year}_{month}.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"[INFO] 查詢日期: {target_str}")
        print(f"[INFO] 目標網址: {url}")
        
        r = requests.get(url, headers=headers, timeout=30)  # 增加超時到 30 秒
        r.encoding = 'utf-8'
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 查找包含目標日期的文本
        date_elements = soup.find_all(string=re.compile(target_str))
        
        if not date_elements:
            print(f"[WARNING] 找不到 {target_str} 的開獎記錄")
            return None
        
        # 找到日期後,查找附近的號碼連結
        for date_elem in date_elements:
            # 向上查找包含號碼的父元素
            parent = date_elem.parent
            for _ in range(10):  # 最多向上查找 10 層
                if parent:
                    # 查找號碼連結
                    ball_links = parent.find_all('a', href=re.compile(r'lotto_ballview_daily539_(\d+)'))
                    
                    if len(ball_links) >= 5:
                        # 提取號碼
                        numbers = []
                        for link in ball_links[:5]:  # 只取前 5 個
                            match = re.search(r'lotto_ballview_daily539_(\d+)', link.get('href'))
                            if match:
                                numbers.append(int(match.group(1)))
                        
                        if len(numbers) == 5:
                            print(f"[SUCCESS] 找到 {target_str} 的開獎號碼: {numbers}")
                            return numbers
                    
                    parent = parent.parent
                else:
                    break
        
        print(f"[WARNING] 找不到 {target_str} 的完整號碼")
        return None
        
    except requests.exceptions.Timeout:
        print("[ERROR] 請求超時 (30秒),請檢查網路連線")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 請求失敗: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] 未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 測試
    test_dates = [
        "2026-01-28",
        "2026-01-27",
        "2025-02-04"
    ]
    
    for date in test_dates:
        print(f"\n{'='*50}")
        result = fetch_auzonet_single_date(date)
        if result:
            print(f"SUCCESS {date}: {result}")
        else:
            print(f"FAILED {date}: Query failed")
