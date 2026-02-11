# -*- coding: utf-8 -*-
"""
精確分析 auzonet 網站的日期和號碼格式
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

url = "https://lotto.auzonet.com/daily539"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

r = requests.get(url, headers=headers)
r.encoding = 'utf-8'

soup = BeautifulSoup(r.text, 'html.parser')

# 查找包含期號的元素 (例如: 115000012)
print("=== 查找期號模式 ===")
period_pattern = re.compile(r'11500\d{4}')
periods = soup.find_all(text=period_pattern)
print(f"找到 {len(periods)} 個期號")
for i, period in enumerate(periods[:5]):
    print(f"  {i+1}. {period.strip()}")

# 查找「大小順序」後面的號碼
print("\n=== 查找開獎號碼 ===")
# 尋找包含 "大小順序" 的文本
size_order_texts = soup.find_all(text=re.compile(r'大小順序'))
print(f"找到 {len(size_order_texts)} 個「大小順序」標記")

for i, text in enumerate(size_order_texts[:3]):
    print(f"\n第 {i+1} 筆:")
    # 找到父元素
    parent = text.parent
    # 找到所有號碼連結
    ball_links = parent.find_all('a', href=re.compile(r'lotto_ballview_daily539_(\d+)'))
    if ball_links:
        numbers = []
        for link in ball_links:
            # 從 href 提取號碼
            match = re.search(r'lotto_ballview_daily539_(\d+)', link.get('href'))
            if match:
                numbers.append(int(match.group(1)))
        print(f"  號碼: {numbers}")

# 嘗試找到日期
print("\n=== 查找日期格式 ===")
# 查找所有可能的日期格式
date_patterns = [
    r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2026/01/28
    r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2026-01-28
    r'(\d{3})/(\d{1,2})/(\d{1,2})',  # 115/01/28 (民國年)
]

for pattern in date_patterns:
    dates = soup.find_all(text=re.compile(pattern))
    if dates:
        print(f"模式 {pattern}: 找到 {len(dates)} 個")
        for date in dates[:3]:
            print(f"  - {date.strip()[:50]}")

print("\n=== 完整測試: 提取第一筆開獎資料 ===")
# 嘗試提取第一筆完整的開獎資料
if size_order_texts:
    first_text = size_order_texts[0]
    parent = first_text.parent
    
    # 提取號碼
    ball_links = parent.find_all('a', href=re.compile(r'lotto_ballview_daily539_(\d+)'))
    numbers = []
    for link in ball_links:
        match = re.search(r'lotto_ballview_daily539_(\d+)', link.get('href'))
        if match:
            numbers.append(int(match.group(1)))
    
    print(f"號碼: {numbers}")
    
    # 嘗試找到對應的期號和日期
    # 向上查找包含期號的元素
    current = parent
    for _ in range(10):  # 最多向上查找 10 層
        if current:
            period_text = current.find(text=period_pattern)
            if period_text:
                print(f"期號: {period_text.strip()}")
                break
            current = current.parent
