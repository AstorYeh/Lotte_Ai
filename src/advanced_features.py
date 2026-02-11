# -*- coding: utf-8 -*-
"""
高級特徵工程 - 時間序列特徵
"""
import pandas as pd
import numpy as np
from typing import Dict

class TimeSeriesFeatures:
    """時間序列特徵計算"""
    
    def __init__(self, feature_engine):
        """
        初始化時間序列特徵引擎
        
        Args:
            feature_engine: FeatureEngine 實例
        """
        self.eng = feature_engine
        self.df = feature_engine.df
        self.numbers_series = feature_engine.numbers_series
        self.total_numbers = feature_engine.total_numbers
    
    def calc_days_since_last_appearance(self) -> pd.Series:
        """
        距離上次出現的期數
        
        理論: 距離越近的號碼,下次出現的機率可能越高 (熱號理論)
        
        Returns:
            pd.Series: 每個號碼的評分 (0-1)
        """
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            # 找出最後一次出現的位置
            last_appear = -1
            for i in range(len(self.numbers_series) - 1, -1, -1):
                if num in self.numbers_series[i]:
                    last_appear = i
                    break
            
            if last_appear >= 0:
                # 計算距離
                days_since = len(self.numbers_series) - last_appear
                
                # 轉換為評分: 距離越近,分數越高
                # 使用指數衰減: score = exp(-days_since / decay_factor)
                decay_factor = 10  # 10 期為半衰期
                score = np.exp(-days_since / decay_factor)
                scores[num] = score
            else:
                # 從未出現過
                scores[num] = 0.0
        
        return pd.Series(scores)
    
    def calc_consecutive_absence(self) -> pd.Series:
        """
        連續未出現次數
        
        理論: 物極必反 - 連續未出現越久的號碼,下次出現的機率可能越高
        
        Returns:
            pd.Series: 每個號碼的評分 (0-1)
        """
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            # 計算連續未出現次數
            consecutive = 0
            for i in range(len(self.numbers_series) - 1, -1, -1):
                if num in self.numbers_series[i]:
                    break
                consecutive += 1
            
            # 轉換為評分: 連續未出現越久,分數越高
            # 使用 sigmoid 函數: score = 1 / (1 + exp(-(x - threshold) / scale))
            threshold = 15  # 15 期為中點
            scale = 5  # 控制曲線陡峭度
            score = 1 / (1 + np.exp(-(consecutive - threshold) / scale))
            scores[num] = score
        
        return pd.Series(scores)
    
    def calc_frequency_trend(self, window=30) -> pd.Series:
        """
        出現頻率趨勢 (上升/下降)
        
        理論: 頻率上升的號碼可能繼續上升,頻率下降的號碼可能繼續下降
        
        Args:
            window: 窗口大小 (默認 30 期)
        
        Returns:
            pd.Series: 每個號碼的評分 (0-1)
        """
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            if len(self.numbers_series) < window * 2:
                # 數據不足,使用中性值
                scores[num] = 0.5
                continue
            
            # 計算前半段和後半段的頻率
            mid = len(self.numbers_series) - window
            first_half = self.numbers_series[mid - window:mid]
            second_half = self.numbers_series[mid:]
            
            # 計算頻率
            freq_first = sum(1 for draw in first_half if num in draw) / len(first_half)
            freq_second = sum(1 for draw in second_half if num in draw) / len(second_half)
            
            # 計算趨勢
            trend = freq_second - freq_first
            
            # 轉換為 0-1 評分
            # trend 範圍約 -0.5 到 0.5
            # 使用線性映射: score = 0.5 + trend
            score = 0.5 + trend
            score = max(0.0, min(1.0, score))
            
            scores[num] = score
        
        return pd.Series(scores)
    
    def calc_periodicity(self, periods=[7, 14, 21, 30]) -> pd.Series:
        """
        週期性特徵
        
        理論: 某些號碼可能有固定的出現週期
        
        Args:
            periods: 要檢測的週期列表 (默認 [7, 14, 21, 30])
        
        Returns:
            pd.Series: 每個號碼的評分 (0-1)
        """
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            # 找出所有出現的位置
            appearances = [i for i, draw in enumerate(self.numbers_series) if num in draw]
            
            if len(appearances) < 3:
                # 出現次數太少,無法判斷週期
                scores[num] = 0.5
                continue
            
            # 計算間隔
            intervals = [appearances[i+1] - appearances[i] for i in range(len(appearances)-1)]
            
            if not intervals:
                scores[num] = 0.5
                continue
            
            # 計算平均間隔
            avg_interval = np.mean(intervals)
            std_interval = np.std(intervals) if len(intervals) > 1 else 0
            
            # 檢查是否符合某個週期
            periodicity_score = 0
            
            for period in periods:
                # 如果平均間隔接近某個週期
                if abs(avg_interval - period) < 3:
                    # 計算距離下次出現的期數
                    last_appear = appearances[-1]
                    current_pos = len(self.numbers_series)
                    days_since = current_pos - last_appear
                    
                    # 如果接近週期,分數較高
                    if abs(days_since - period) < 3:
                        # 非常接近週期
                        periodicity_score = max(periodicity_score, 0.9)
                    elif abs(days_since - period) < 5:
                        # 接近週期
                        periodicity_score = max(periodicity_score, 0.7)
                    else:
                        # 有週期性,但當前不在週期點
                        periodicity_score = max(periodicity_score, 0.4)
            
            # 考慮間隔的穩定性 (標準差越小,週期性越強)
            if std_interval > 0:
                stability = 1 / (1 + std_interval / avg_interval)
                periodicity_score *= stability
            
            scores[num] = periodicity_score if periodicity_score > 0 else 0.5
        
        return pd.Series(scores)
    
    def get_all_time_series_features(self) -> Dict[str, pd.Series]:
        """
        獲取所有時間序列特徵
        
        Returns:
            dict: 特徵名稱 -> 評分 Series
        """
        return {
            'days_since': self.calc_days_since_last_appearance(),
            'consecutive_absence': self.calc_consecutive_absence(),
            'frequency_trend': self.calc_frequency_trend(),
            'periodicity': self.calc_periodicity()
        }

if __name__ == "__main__":
    # 測試代碼
    print("時間序列特徵模組")
    print("="*80)
    print("\n功能:")
    print("  1. 距離上次出現的期數 - 熱號理論")
    print("  2. 連續未出現次數 - 物極必反理論")
    print("  3. 出現頻率趨勢 - 趨勢延續理論")
    print("  4. 週期性特徵 - 週期性理論")
    print("\n預期效果:")
    print("  - 新增 4 個特徵")
    print("  - 模型總數: 9 → 13 個")
    print("  - 2+ 命中率: 20.65% → 22-23%")
