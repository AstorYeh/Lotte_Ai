# -*- coding: utf-8 -*-
"""
生成測試歷史資料
用於測試預測器功能
"""
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path
from src.timezone_utils import get_taiwan_now


def generate_lotto_test_data(days=30):
    """生成大樂透測試資料"""
    print("生成大樂透測試資料...")
    
    data = []
    current = get_taiwan_now() - timedelta(days=days)
    
    while current <= get_taiwan_now():
        if current.weekday() in [1, 4]:  # 週二、週五
            numbers = sorted(random.sample(range(1, 50), 6))
            data.append({
                'date': current.strftime('%Y-%m-%d'),
                'numbers': ','.join([str(n) for n in numbers])
            })
        current += timedelta(days=1)
    
    Path("data/lotto").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/lotto/lotto_history.csv", index=False)
    print(f"[OK] 大樂透: {len(df)} 筆")
    return len(df)


def generate_power_test_data(days=30):
    """生成威力彩測試資料"""
    print("生成威力彩測試資料...")
    
    data = []
    current = get_taiwan_now() - timedelta(days=days)
    
    while current <= get_taiwan_now():
        if current.weekday() in [0, 3]:  # 週一、週四
            zone1 = sorted(random.sample(range(1, 39), 6))
            zone2 = random.randint(1, 8)
            data.append({
                'date': current.strftime('%Y-%m-%d'),
                'zone1': str(zone1),
                'zone2': zone2
            })
        current += timedelta(days=1)
    
    Path("data/power").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/power/power_history.csv", index=False)
    print(f"[OK] 威力彩: {len(df)} 筆")
    return len(df)


def generate_star3_test_data(days=30):
    """生成3星彩測試資料"""
    print("生成3星彩測試資料...")
    
    data = []
    current = get_taiwan_now() - timedelta(days=days)
    
    while current <= get_taiwan_now():
        if current.weekday() != 6:  # 週一~週六
            number = str(random.randint(0, 999)).zfill(3)
            data.append({
                'date': current.strftime('%Y-%m-%d'),
                'number': number
            })
        current += timedelta(days=1)
    
    Path("data/star3").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/star3/star3_history.csv", index=False)
    print(f"[OK] 3星彩: {len(df)} 筆")
    return len(df)


def generate_star4_test_data(days=30):
    """生成4星彩測試資料"""
    print("生成4星彩測試資料...")
    
    data = []
    current = get_taiwan_now() - timedelta(days=days)
    
    while current <= get_taiwan_now():
        if current.weekday() != 6:  # 週一~週六
            number = str(random.randint(0, 9999)).zfill(4)
            data.append({
                'date': current.strftime('%Y-%m-%d'),
                'number': number
            })
        current += timedelta(days=1)
    
    Path("data/star4").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_csv("data/star4/star4_history.csv", index=False)
    print(f"[OK] 4星彩: {len(df)} 筆")
    return len(df)


if __name__ == "__main__":
    print("=" * 60)
    print("生成測試歷史資料")
    print("=" * 60)
    print()
    
    total = 0
    total += generate_lotto_test_data(90)  # 最近90天
    total += generate_power_test_data(90)
    total += generate_star3_test_data(90)
    total += generate_star4_test_data(90)
    
    print()
    print("=" * 60)
    print(f"完成! 總共生成 {total} 筆測試資料")
    print("=" * 60)
