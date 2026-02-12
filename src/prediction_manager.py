# -*- coding: utf-8 -*-
"""
預測管理器 - 統一管理所有遊戲的預測歷史
"""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.timezone_utils import get_taiwan_now, get_taiwan_isoformat


class PredictionManager:
    """預測管理器 - 管理所有遊戲的預測記錄"""
    
    def __init__(self):
        self.predictions_dir = Path('data/predictions')
        self.predictions_dir.mkdir(parents=True, exist_ok=True)
        
        self.games = ['539', 'lotto', 'power', 'star3', 'star4']
    
    def save_prediction(self, game: str, prediction_date: str, numbers: List[int], 
                       metadata: Optional[Dict] = None) -> bool:
        """
        儲存預測記錄
        
        Args:
            game: 遊戲名稱
            prediction_date: 預測日期 (YYYY-MM-DD)
            numbers: 預測號碼
            metadata: 額外資訊 (策略、信心度等)
        """
        try:
            csv_file = self.predictions_dir / f"{game}_predictions.csv"
            
            # 準備資料
            record = {
                'prediction_date': prediction_date,
                'predicted_numbers': ','.join(map(str, numbers)),
                'actual_numbers': '',
                'hits': None,
                'accuracy': None,
                'verified': False,
                'created_at': get_taiwan_isoformat()
            }
            
            # 添加 metadata
            if metadata:
                record.update(metadata)
            
            # 讀取現有資料
            if csv_file.exists():
                df = pd.read_csv(csv_file)
            else:
                df = pd.DataFrame()
            
            # 檢查是否已存在
            if not df.empty and prediction_date in df['prediction_date'].values:
                print(f"[WARNING] Prediction for {game} on {prediction_date} already exists")
                return False
            
            # 新增記錄
            new_df = pd.DataFrame([record])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # 儲存
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"[SUCCESS] Saved prediction for {game} on {prediction_date}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save prediction: {e}")
            return False
    
    def get_pending_predictions(self, game: str, days: int = 7) -> pd.DataFrame:
        """
        取得待驗證的預測
        
        Args:
            game: 遊戲名稱
            days: 查詢最近幾天的預測
        """
        csv_file = self.predictions_dir / f"{game}_predictions.csv"
        
        if not csv_file.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(csv_file)
        
        # 篩選未驗證的預測
        pending = df[df['verified'] == False].copy()
        
        # 篩選最近 N 天
        if not pending.empty:
            pending['prediction_date'] = pd.to_datetime(pending['prediction_date']).dt.tz_localize(None)
            cutoff_date = (get_taiwan_now() - timedelta(days=days)).replace(tzinfo=None)
            pending = pending[pending['prediction_date'] >= cutoff_date]
        
        return pending
    
    def update_verification(self, game: str, prediction_date: str, 
                           actual_numbers: List[int]) -> Dict:
        """
        更新驗證結果
        
        Args:
            game: 遊戲名稱
            prediction_date: 預測日期
            actual_numbers: 實際開獎號碼
        
        Returns:
            驗證結果 (命中數、準確率等)
        """
        try:
            csv_file = self.predictions_dir / f"{game}_predictions.csv"
            
            if not csv_file.exists():
                return {'error': 'No predictions file found'}
            
            df = pd.read_csv(csv_file)
            
            # 找到對應的預測
            mask = df['prediction_date'] == prediction_date
            if not mask.any():
                return {'error': f'No prediction found for {prediction_date}'}
            
            # 取得預測號碼
            predicted_str = df.loc[mask, 'predicted_numbers'].iloc[0]
            predicted_numbers = [int(n) for n in predicted_str.split(',')]
            
            # 計算命中數
            hits = len(set(predicted_numbers) & set(actual_numbers))
            accuracy = hits / len(predicted_numbers)
            
            # 更新記錄
            df.loc[mask, 'actual_numbers'] = ','.join(map(str, actual_numbers))
            df.loc[mask, 'hits'] = hits
            df.loc[mask, 'accuracy'] = accuracy
            df.loc[mask, 'verified'] = True
            df.loc[mask, 'verified_at'] = get_taiwan_isoformat()
            
            # 儲存
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            result = {
                'game': game,
                'date': prediction_date,
                'predicted': predicted_numbers,
                'actual': actual_numbers,
                'hits': hits,
                'accuracy': accuracy
            }
            
            print(f"[SUCCESS] Verified {game} prediction: {hits} hits ({accuracy:.1%})")
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to update verification: {e}")
            return {'error': str(e)}
    
    def get_accuracy_stats(self, game: str, days: int = 30) -> Dict:
        """
        取得準確率統計
        
        Args:
            game: 遊戲名稱
            days: 統計最近幾天
        """
        csv_file = self.predictions_dir / f"{game}_predictions.csv"
        
        if not csv_file.exists():
            return {'total': 0, 'verified': 0, 'avg_accuracy': 0}
        
        df = pd.read_csv(csv_file)
        
        # 篩選已驗證的預測
        verified = df[df['verified'] == True].copy()
        
        if verified.empty:
            return {'total': 0, 'verified': 0, 'avg_accuracy': 0}
        
        # 篩選最近 N 天
        verified['prediction_date'] = pd.to_datetime(verified['prediction_date']).dt.tz_localize(None)
        cutoff_date = (get_taiwan_now() - timedelta(days=days)).replace(tzinfo=None)
        recent = verified[verified['prediction_date'] >= cutoff_date]
        
        if recent.empty:
            return {'total': 0, 'verified': 0, 'avg_accuracy': 0}
        
        stats = {
            'total': len(df),
            'verified': len(recent),
            'avg_accuracy': recent['accuracy'].mean(),
            'avg_hits': recent['hits'].mean(),
            'max_hits': int(recent['hits'].max()),
            'min_hits': int(recent['hits'].min()),
            'date_range': f"{recent['prediction_date'].min().date()} ~ {recent['prediction_date'].max().date()}"
        }
        
        return stats
    
    def get_all_stats(self, days: int = 30) -> Dict:
        """取得所有遊戲的統計"""
        all_stats = {}
        
        for game in self.games:
            all_stats[game] = self.get_accuracy_stats(game, days)
        
        return all_stats


# 全域實例
prediction_manager = PredictionManager()


if __name__ == "__main__":
    # 測試
    manager = PredictionManager()
    
    print("=" * 60)
    print("預測管理器測試")
    print("=" * 60)
    
    # 測試儲存預測
    test_date = "2026-02-13"
    test_numbers = [5, 12, 18, 25, 33]
    
    manager.save_prediction('539', test_date, test_numbers, {
        'strategy': 'ensemble',
        'confidence': 0.75
    })
    
    # 測試取得待驗證預測
    pending = manager.get_pending_predictions('539')
    print(f"\n待驗證預測: {len(pending)} 筆")
    
    # 測試更新驗證
    actual_numbers = [5, 12, 20, 28, 35]
    result = manager.update_verification('539', test_date, actual_numbers)
    print(f"\n驗證結果: {result}")
    
    # 測試統計
    stats = manager.get_accuracy_stats('539', days=30)
    print(f"\n準確率統計: {stats}")
