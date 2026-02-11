# -*- coding: utf-8 -*-
"""
分析 auzonet 網站結構
"""
import requests
from bs4 import BeautifulSoup
import re

url = "https://lotto.auzonet.com/daily539"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

r = requests.get(url, headers=headers)
r.encoding = 'utf-8'

soup = BeautifulSoup(r.text, 'html.parser')

# 查找所有包含日期的元素
print("=== 查找日期模式 ===")
# 查找所有文本中包含 2026 的元素
for tag in soup.find_all(text=re.compile(r'2026')):
    parent = tag.parent
    print(f"Tag: {parent.name}, Class: {parent.get('class')}, Text: {tag.strip()[:100]}")

print("\n=== 查找號碼模式 ===")
# 查找所有包含號碼連結的元素
ball_links = soup.find_all('a', href=re.compile(r'lotto_ballview_daily539_\d+'))
print(f"找到 {len(ball_links)} 個號碼連結")
if ball_links:
    print("前 10 個連結:")
    for link in ball_links[:10]:
        print(f"  - {link.get_text()}: {link.get('href')}")

print("\n=== 查找表格結構 ===")
tables = soup.find_all('table')
print(f"找到 {len(tables)} 個表格")

# 查找包含開獎資料的表格
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    if len(rows) > 2:  # 有多行的表格
        print(f"\n表格 {i+1}: {len(rows)} 行")
        # 顯示前 3 行
        for j, row in enumerate(rows[:3]):
            cells = row.find_all(['td', 'th'])
            if cells:
                cell_texts = [cell.get_text().strip()[:30] for cell in cells]
                print(f"  行 {j+1}: {cell_texts}")
