# -*- coding: utf-8 -*-
"""
大樂透增強預測器
使用統計分析 + 頻率分析生成預測
"""
import pandas as pd
import random
from typing import List
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
from src.timezone_utils import get_taiwan_now


class LottoPredictor:
    """大樂透預測器 (49選6) - 增強版"""
    
    def __init__(self):
        self.num_range = 49
        self.select_count = 6
        self.history_file = "data/lotto/lotto_history.csv"
    
    def _load_history(self) -> pd.DataFrame:
        """載入歷史資料"""
        try:
            if Path(self.history_file).exists():
                return pd.read_csv(self.history_file)
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def _calculate_frequency(self) -> dict:
        """計算號碼出現頻率"""
        df = self._load_history()
        
        if df.empty:
            # 無歷史資料,返回均等頻率
            return {i: 1 for i in range(1, self.num_range + 1)}
        
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
            elif 'numbers' in row and isinstance(row['numbers'], str):
                # Fallback for old format
                try:
                    nums = [int(n) for n in str(row['numbers']).split(',')]
                    frequency.update(nums)
                except:
                    pass
        
        # 確保所有號碼都有頻率
        for i in range(1, self.num_range + 1):
            if i not in frequency:
                frequency[i] = 0
        
        return dict(frequency)
    
    def _calculate_hot_cold(self, frequency: dict) -> tuple:
        """計算冷熱號"""
        sorted_nums = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        
        hot_nums = [num for num, _ in sorted_nums[:15]]  # 前15個熱號
        cold_nums = [num for num, _ in sorted_nums[-15:]]  # 後15個冷號
        warm_nums = [num for num, _ in sorted_nums[15:34]]  # 中間號碼
        
        return hot_nums, warm_nums, cold_nums
    
    def generate_predictions(self, num_sets=5) -> List[List[int]]:
        """
        生成多組預測號碼 (使用統計分析)
        """
        predictions = []
        used_combinations = set()
        
        # 計算頻率
        frequency = self._calculate_frequency()
        hot_nums, warm_nums, cold_nums = self._calculate_hot_cold(frequency)
        
        # 定義區間
        ranges = [
            (1, 10),
            (11, 20),
            (21, 30),
            (31, 40),
            (41, 49)
        ]
        
        for i in range(num_sets):
            while True:
                numbers = []
                
                if i == 0:
                    # 策略1: 熱號優先
                    numbers.extend(random.sample(hot_nums, min(3, len(hot_nums))))
                    numbers.extend(random.sample(warm_nums, min(2, len(warm_nums))))
                    remaining = self.select_count - len(numbers)
                    if remaining > 0:
                        pool = [n for n in range(1, self.num_range + 1) if n not in numbers]
                        numbers.extend(random.sample(pool, remaining))
                
                elif i == 1:
                    # 策略2: 平衡分布
                    numbers.extend(random.sample(hot_nums, min(2, len(hot_nums))))
                    numbers.extend(random.sample(warm_nums, min(3, len(warm_nums))))
                    numbers.extend(random.sample(cold_nums, min(1, len(cold_nums))))
                
                elif i == 2:
                    # 策略3: 區間分散
                    for start, end in ranges:
                        if len(numbers) >= self.select_count:
                            break
                        num = random.randint(start, end)
                        if num not in numbers:
                            numbers.append(num)
                    
                    while len(numbers) < self.select_count:
                        num = random.randint(1, self.num_range)
                        if num not in numbers:
                            numbers.append(num)
                
                elif i == 3:
                    # 策略4: 冷號翻身
                    numbers.extend(random.sample(cold_nums, min(3, len(cold_nums))))
                    numbers.extend(random.sample(warm_nums, min(2, len(warm_nums))))
                    remaining = self.select_count - len(numbers)
                    if remaining > 0:
                        pool = [n for n in range(1, self.num_range + 1) if n not in numbers]
                        numbers.extend(random.sample(pool, remaining))
                
                else:
                    # 策略5: 混合策略
                    numbers.extend(random.sample(hot_nums, min(2, len(hot_nums))))
                    numbers.extend(random.sample(warm_nums, min(2, len(warm_nums))))
                    numbers.extend(random.sample(cold_nums, min(1, len(cold_nums))))
                    remaining = self.select_count - len(numbers)
                    if remaining > 0:
                        pool = [n for n in range(1, self.num_range + 1) if n not in numbers]
                        numbers.extend(random.sample(pool, remaining))
                
                numbers = sorted(list(set(numbers))[:self.select_count])
                
                # 確保有6個號碼
                while len(numbers) < self.select_count:
                    num = random.randint(1, self.num_range)
                    if num not in numbers:
                        numbers.append(num)
                
                numbers = sorted(numbers[:self.select_count])
                combo = tuple(numbers)
                
                if combo not in used_combinations:
                    predictions.append(numbers)
                    used_combinations.add(combo)
                    break
        
        return predictions
    
    def get_next_draw_date(self) -> str:
        """取得下次開獎日期 (週二、週五)"""
        today = get_taiwan_now()
        days_ahead = 0
        
        while True:
            next_date = today + timedelta(days=days_ahead)
            if next_date.weekday() in [1, 4]:  # 週二或週五
                if days_ahead > 0 or next_date.hour < 20:
                    return next_date.strftime('%Y-%m-%d')
            days_ahead += 1
            
            if days_ahead > 7:
                break
        
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')


if __name__ == "__main__":
    predictor = LottoPredictor()
    
    print("=" * 60)
    print("大樂透增強預測測試")
    print("=" * 60)
    
    # 測試頻率計算
    freq = predictor._calculate_frequency()
    hot, warm, cold = predictor._calculate_hot_cold(freq)
    
    print(f"\n熱號 (前15): {hot[:10]}...")
    print(f"冷號 (後15): {cold[:10]}...")
    
    # 生成預測
    predictions = predictor.generate_predictions(5)
    next_date = predictor.get_next_draw_date()
    
    print(f"\n預測日期: {next_date}")
    print("\n預測號碼:")
    for i, nums in enumerate(predictions, 1):
        print(f"  第 {i} 組: {nums}")
