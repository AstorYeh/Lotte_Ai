# -*- coding: utf-8 -*-
"""
準確率追蹤系統
記錄預測結果並計算準確率
"""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from src.timezone_utils import get_taiwan_datetime_str


class AccuracyTracker:
    """準確率追蹤器"""
    
    def __init__(self, game='539'):
        self.game = game
        self.tracking_file = f"data/accuracy/{game}_tracking.csv"
        Path("data/accuracy").mkdir(parents=True, exist_ok=True)
    
    def record_prediction(self, date: str, predicted_numbers: List, actual_numbers: List = None):
        """
        記錄預測結果
        
        Args:
            date: 預測日期
            predicted_numbers: 預測號碼 (可以是多組)
            actual_numbers: 實際開獎號碼 (可選)
        """
        # 載入現有記錄
        df = self._load_tracking()
        
        # 準備新記錄
        record = {
            'date': date,
            'predicted': json.dumps(predicted_numbers),
            'actual': json.dumps(actual_numbers) if actual_numbers else None,
            'recorded_at': get_taiwan_datetime_str()
        }
        
        # 如果有實際號碼,計算準確率
        if actual_numbers:
            record['accuracy'] = self._calculate_accuracy(predicted_numbers, actual_numbers)
            record['hits'] = self._calculate_hits(predicted_numbers, actual_numbers)
        
        # 添加記錄
        new_df = pd.DataFrame([record])
        df = pd.concat([df, new_df], ignore_index=True)
        
        # 去重 (保留最新)
        df = df.drop_duplicates(subset=['date'], keep='last')
        df = df.sort_values('date')
        
        # 儲存
        df.to_csv(self.tracking_file, index=False)
    
    def update_actual_result(self, date: str, actual_numbers: List):
        """
        更新實際開獎結果
        
        Args:
            date: 開獎日期
            actual_numbers: 實際開獎號碼
        """
        df = self._load_tracking()
        
        # 找到對應日期的記錄
        mask = df['date'] == date
        if mask.any():
            # 更新實際號碼
            df.loc[mask, 'actual'] = json.dumps(actual_numbers)
            
            # 重新計算準確率
            predicted = json.loads(df.loc[mask, 'predicted'].iloc[0])
            df.loc[mask, 'accuracy'] = self._calculate_accuracy(predicted, actual_numbers)
            df.loc[mask, 'hits'] = self._calculate_hits(predicted, actual_numbers)
            
            # 儲存
            df.to_csv(self.tracking_file, index=False)
            return True
        
        return False
    
    def get_accuracy_stats(self, days=30) -> Dict:
        """
        獲取準確率統計
        
        Args:
            days: 統計天數
        
        Returns:
            Dict: 統計資料
        """
        df = self._load_tracking()
        
        # 過濾有實際結果的記錄
        df = df[df['actual'].notna()]
        
        if df.empty:
            return {
                'total_predictions': 0,
                'avg_accuracy': 0,
                'avg_hits': 0,
                'best_accuracy': 0,
                'worst_accuracy': 0
            }
        
        # 最近 N 天
        df = df.tail(days)
        
        return {
            'total_predictions': len(df),
            'avg_accuracy': df['accuracy'].mean() if 'accuracy' in df.columns else 0,
            'avg_hits': df['hits'].mean() if 'hits' in df.columns else 0,
            'best_accuracy': df['accuracy'].max() if 'accuracy' in df.columns else 0,
            'worst_accuracy': df['accuracy'].min() if 'accuracy' in df.columns else 0,
            'recent_trend': self._calculate_trend(df)
        }
    
    def get_history(self, limit=50) -> pd.DataFrame:
        """獲取歷史記錄"""
        df = self._load_tracking()
        return df.tail(limit)
    
    def _load_tracking(self) -> pd.DataFrame:
        """載入追蹤資料"""
        if Path(self.tracking_file).exists():
            return pd.read_csv(self.tracking_file)
        return pd.DataFrame(columns=['date', 'predicted', 'actual', 'accuracy', 'hits', 'recorded_at'])
    
    def _calculate_accuracy(self, predicted: List, actual: List) -> float:
        """
        計算準確率
        
        對於多組預測,取最佳結果
        """
        if not predicted or not actual:
            return 0.0
        
        # 如果是多組預測
        if isinstance(predicted[0], list):
            accuracies = []
            for pred_set in predicted:
                hits = len(set(pred_set) & set(actual))
                accuracies.append(hits / len(actual) * 100)
            return max(accuracies)
        
        # 單組預測
        hits = len(set(predicted) & set(actual))
        return hits / len(actual) * 100
    
    def _calculate_hits(self, predicted: List, actual: List) -> int:
        """
        計算命中數
        
        對於多組預測,取最佳結果
        """
        if not predicted or not actual:
            return 0
        
        # 如果是多組預測
        if isinstance(predicted[0], list):
            hits_list = []
            for pred_set in predicted:
                hits = len(set(pred_set) & set(actual))
                hits_list.append(hits)
            return max(hits_list)
        
        # 單組預測
        return len(set(predicted) & set(actual))
    
    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """計算趨勢"""
        if len(df) < 5 or 'accuracy' not in df.columns:
            return "insufficient_data"
        
        recent = df.tail(5)['accuracy'].mean()
        previous = df.head(len(df) - 5).tail(5)['accuracy'].mean() if len(df) >= 10 else recent
        
        if recent > previous + 5:
            return "improving"
        elif recent < previous - 5:
            return "declining"
        else:
            return "stable"


if __name__ == "__main__":
    # 測試
    tracker = AccuracyTracker('539')
    
    # 記錄預測
    tracker.record_prediction(
        date='2026-02-10',
        predicted_numbers=[[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
        actual_numbers=None
    )
    
    # 更新實際結果
    tracker.update_actual_result(
        date='2026-02-10',
        actual_numbers=[1, 2, 3, 11, 12]
    )
    
    # 獲取統計
    stats = tracker.get_accuracy_stats()
    print("準確率統計:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # 獲取歷史
    history = tracker.get_history(10)
    print("\n歷史記錄:")
    print(history)
