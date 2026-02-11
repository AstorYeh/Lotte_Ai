# -*- coding: utf-8 -*-
"""
3星彩增強預測器
使用位數頻率分析和序列模式識別
"""
import pandas as pd
import random
from typing import List
from datetime import datetime, timedelta
from collections import Counter
from pathlib import Path
from src.timezone_utils import get_taiwan_now


class Star3Predictor:
    """3星彩預測器 - 增強版"""
    
    def __init__(self):
        self.history_file = "data/star3/star3_history.csv"
    
    def _load_history(self) -> pd.DataFrame:
        """載入歷史資料"""
        try:
            if Path(self.history_file).exists():
                return pd.read_csv(self.history_file)
            return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def _analyze_digit_frequency(self) -> dict:
        """分析各位數的數字頻率"""
        df = self._load_history()
        
        hundreds = Counter()
        tens = Counter()
        ones = Counter()
        
        if df.empty:
             for i in range(10):
                hundreds[str(i)] = 1
                tens[str(i)] = 1
                ones[str(i)] = 1
             return {'hundreds': hundreds, 'tens': tens, 'ones': ones}

        for _, row in df.iterrows():
            # Try flattened columns '1', '2', '3'
            if '1' in row and '2' in row and '3' in row:
                try:
                    hundreds[str(int(row['1']))] += 1
                    tens[str(int(row['2']))] += 1
                    ones[str(int(row['3']))] += 1
                except ValueError:
                    continue
            elif 'number' in row:
                 # Fallback
                 num_str = str(row['number']).zfill(3)
                 if len(num_str) >= 3:
                    hundreds[num_str[0]] += 1
                    tens[num_str[1]] += 1
                    ones[num_str[2]] += 1
        
        return {
            'hundreds': hundreds,
            'tens': tens,
            'ones': ones
        }
    
    def generate_predictions(self, num_sets=5) -> List[str]:
        """
        生成多組預測號碼
        """
        predictions = []
        used_numbers = set()
        
        # 分析頻率
        freq = self._analyze_digit_frequency()
        
        # 取得各位數的熱門數字
        hot_hundreds = [d for d, _ in freq['hundreds'].most_common(5)]
        hot_tens = [d for d, _ in freq['tens'].most_common(5)]
        hot_ones = [d for d, _ in freq['ones'].most_common(5)]
        
        # Fallbacks if empty
        if not hot_hundreds: hot_hundreds = [str(i) for i in range(10)]
        if not hot_tens: hot_tens = [str(i) for i in range(10)]
        if not hot_ones: hot_ones = [str(i) for i in range(10)]
        
        for i in range(num_sets):
            while True:
                if i == 0:
                    # 策略1: 高頻組合
                    h = random.choice(hot_hundreds)
                    t = random.choice(hot_tens)
                    o = random.choice(hot_ones)
                    number = h + t + o
                
                elif i == 1:
                    # 策略2: 平衡分布 (小-中-大)
                    h = str(random.randint(0, 3))
                    t = str(random.randint(4, 6))
                    o = str(random.randint(7, 9))
                    number = h + t + o
                
                elif i == 2:
                    # 策略3: 序列模式 (連號)
                    start = random.randint(0, 7)
                    number = ''.join([str((start + j) % 10) for j in range(3)])
                
                elif i == 3:
                    # 策略4: 對稱模式
                    d = str(random.randint(0, 9))
                    m = str(random.randint(0, 9))
                    number = d + m + d
                
                else:
                    # 策略5: 完全隨機
                    number = str(random.randint(0, 999)).zfill(3)
                
                if number not in used_numbers:
                    predictions.append(number)
                    used_numbers.add(number)
                    break
        
        return predictions
    
    def get_next_draw_date(self) -> str:
        """取得下次開獎日期 (週一~週六)"""
        today = get_taiwan_now()
        days_ahead = 0
        
        while True:
            next_date = today + timedelta(days=days_ahead)
            if next_date.weekday() != 6:  # 不是週日
                if days_ahead > 0 or next_date.hour < 20:
                    return next_date.strftime('%Y-%m-%d')
            days_ahead += 1
            
            if days_ahead > 7:
                break
        
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')


if __name__ == "__main__":
    predictor = Star3Predictor()
    
    print("=" * 60)
    print("3星彩增強預測測試")
    print("=" * 60)
    
    # 分析頻率
    freq = predictor._analyze_digit_frequency()
    print("\n位數頻率分析:")
    print(f"百位熱門: {[d for d, _ in freq['hundreds'].most_common(5)]}")
    print(f"十位熱門: {[d for d, _ in freq['tens'].most_common(5)]}")
    print(f"個位熱門: {[d for d, _ in freq['ones'].most_common(5)]}")
    
    # 生成預測
    predictions = predictor.generate_predictions(5)
    next_date = predictor.get_next_draw_date()
    
    print(f"\n預測日期: {next_date}")
    print("\n預測號碼:")
    for i, num in enumerate(predictions, 1):
        print(f"  第 {i} 組: {num}")
