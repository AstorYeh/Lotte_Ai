# -*- coding: utf-8 -*-
"""
威力彩增強預測器
兩區選號: 第一區 38選6 + 第二區 8選1
使用統計分析優化
"""
import pandas as pd
import random
from typing import List, Dict
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
from src.timezone_utils import get_taiwan_now


class PowerPredictor:
    """威力彩預測器 - 增強版"""
    
    def __init__(self):
        self.zone1_range = 38
        self.zone1_count = 6
        self.zone2_range = 8
        self.history_file = "data/power/power_history.csv"
    
    def _load_history(self) -> pd.DataFrame:
        """載入歷史資料"""
        try:
            if Path(self.history_file).exists():
                return pd.read_csv(self.history_file)
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def _calculate_zone1_frequency(self) -> dict:
        """計算第一區號碼頻率"""
        df = self._load_history()
        
        if df.empty:
            return {i: 1 for i in range(1, self.zone1_range + 1)}
        
        frequency = Counter()
        
        for _, row in df.iterrows():
            nums = []
            # Handle flattened columns '1' to '6'
            for col in ['1', '2', '3', '4', '5', '6']:
                if col in row and pd.notna(row[col]):
                    try:
                        nums.append(int(row[col]))
                    except ValueError:
                        continue
            
            if nums:
                frequency.update(nums)
            elif 'zone1' in row:
                # Fallback for old format
                try:
                    numbers = eval(row['zone1']) if isinstance(row['zone1'], str) else row['zone1']
                    if isinstance(numbers, list):
                        frequency.update(numbers)
                except:
                    pass
        
        for i in range(1, self.zone1_range + 1):
            if i not in frequency:
                frequency[i] = 0
        
        return dict(frequency)
    
    def _calculate_zone2_frequency(self) -> dict:
        """計算第二區號碼頻率"""
        df = self._load_history()
        
        if df.empty:
            return {i: 1 for i in range(1, self.zone2_range + 1)}
        
        frequency = Counter()
        
        for _, row in df.iterrows():
            if 'zone2' in row and pd.notna(row['zone2']):
                try:
                    frequency[int(row['zone2'])] += 1
                except ValueError:
                    continue
        
        for i in range(1, self.zone2_range + 1):
            if i not in frequency:
                frequency[i] = 0
        
        return dict(frequency)
    
    def generate_predictions(self, num_sets=5) -> List[Dict]:
        """
        生成多組預測號碼
        """
        predictions = []
        used_combinations = set()
        
        # 計算頻率
        zone1_freq = self._calculate_zone1_frequency()
        zone2_freq = self._calculate_zone2_frequency()
        
        # 第一區冷熱號
        sorted_zone1 = sorted(zone1_freq.items(), key=lambda x: x[1], reverse=True)
        hot_zone1 = [num for num, _ in sorted_zone1[:12]]
        cold_zone1 = [num for num, _ in sorted_zone1[-12:]]
        warm_zone1 = [num for num, _ in sorted_zone1[12:26]]
        
        # 第二區權重
        zone2_weights = list(zone2_freq.values())
        zone2_nums = list(zone2_freq.keys())
        
        for i in range(num_sets):
            while True:
                # 第一區策略
                if i == 0:
                    # 熱號優先
                    zone1 = random.sample(hot_zone1, min(4, len(hot_zone1)))
                    zone1.extend(random.sample(warm_zone1, min(2, len(warm_zone1))))
                    # Fill if needed
                    while len(zone1) < self.zone1_count:
                         pool = [n for n in range(1, self.zone1_range + 1) if n not in zone1]
                         zone1.extend(random.sample(pool, self.zone1_count - len(zone1)))
                elif i == 1:
                    # 平衡策略
                    zone1 = random.sample(hot_zone1, min(3, len(hot_zone1)))
                    zone1.extend(random.sample(warm_zone1, min(2, len(warm_zone1))))
                    zone1.extend(random.sample(cold_zone1, min(1, len(cold_zone1))))
                elif i == 2:
                    # 區間分散
                    ranges = [(1, 10), (11, 20), (21, 30), (31, 38)]
                    zone1 = []
                    for start, end in random.sample(ranges, min(4, len(ranges))):
                        num = random.randint(start, end)
                        if num not in zone1:
                            zone1.append(num)
                    while len(zone1) < self.zone1_count:
                        num = random.randint(1, self.zone1_range)
                        if num not in zone1:
                            zone1.append(num)
                elif i == 3:
                    # 冷號翻身
                    zone1 = random.sample(cold_zone1, min(3, len(cold_zone1)))
                    zone1.extend(random.sample(warm_zone1, min(3, len(warm_zone1))))
                else:
                    # 混合策略
                    zone1 = random.sample(hot_zone1, min(2, len(hot_zone1)))
                    zone1.extend(random.sample(warm_zone1, min(3, len(warm_zone1))))
                    zone1.extend(random.sample(cold_zone1, min(1, len(cold_zone1))))
                
                zone1 = sorted(list(set(zone1))[:self.zone1_count])
                
                # 確保有6個號碼
                while len(zone1) < self.zone1_count:
                    num = random.randint(1, self.zone1_range)
                    if num not in zone1:
                        zone1.append(num)
                
                zone1 = sorted(zone1[:self.zone1_count])
                
                # 第二區: 使用權重選擇
                if sum(zone2_weights) > 0:
                    zone2 = random.choices(zone2_nums, weights=zone2_weights, k=1)[0]
                else:
                    zone2 = random.randint(1, self.zone2_range)
                
                combo = (tuple(zone1), zone2)
                
                if combo not in used_combinations:
                    predictions.append({
                        'zone1': zone1,
                        'zone2': zone2
                    })
                    used_combinations.add(combo)
                    break
        
        return predictions
    
    def get_next_draw_date(self) -> str:
        """取得下次開獎日期 (週一、週四)"""
        today = get_taiwan_now()
        days_ahead = 0
        
        while True:
            next_date = today + timedelta(days=days_ahead)
            if next_date.weekday() in [0, 3]:  # 週一或週四
                if days_ahead > 0 or next_date.hour < 20:
                    return next_date.strftime('%Y-%m-%d')
            days_ahead += 1
            
            if days_ahead > 7:
                break
        
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')


if __name__ == "__main__":
    predictor = PowerPredictor()
    
    print("=" * 60)
    print("威力彩增強預測測試")
    print("=" * 60)
    
    # 測試頻率計算
    zone1_freq = predictor._calculate_zone1_frequency()
    zone2_freq = predictor._calculate_zone2_frequency()
    
    print(f"\n第一區頻率範例: {list(zone1_freq.items())[:5]}")
    print(f"第二區頻率: {zone2_freq}")
    
    # 生成預測
    predictions = predictor.generate_predictions(5)
    next_date = predictor.get_next_draw_date()
    
    print(f"\n預測日期: {next_date}")
    print("\n預測號碼:")
    for i, pred in enumerate(predictions, 1):
        print(f"  第 {i} 組: 第一區 {pred['zone1']} + 第二區 {pred['zone2']}")
