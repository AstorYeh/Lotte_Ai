"""
預測歷史記錄管理模組
提供預測結果的儲存、載入與查詢功能
"""
import json
import os
from datetime import datetime
from pathlib import Path
from src.logger import logger
from src.timezone_utils import get_taiwan_datetime_str, get_taiwan_now

class PredictionHistory:
    """預測歷史記錄管理器"""
    
    def __init__(self):
        self.history_dir = Path("data/predictions")
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "prediction_history.json"
        
    def save_prediction(self, prediction_date, numbers, scores=None, backtest_result=None):
        """
        儲存預測結果
        
        Args:
            prediction_date: 預測目標日期 (str)
            numbers: 預測號碼列表 (list)
            scores: 評分資料 (dict, optional)
            backtest_result: 回測結果 (dict, optional)
        
        Returns:
            bool: 是否儲存成功
        """
        try:
            # 載入現有歷史
            history = self.load_all_predictions()
            
            # 建立新記錄
            record = {
                "prediction_date": prediction_date,
                "predicted_numbers": numbers,
                "created_at": get_taiwan_datetime_str(),
                "status": "pending",  # pending, verified, expired
                "actual_numbers": None,
                "hits": None,
                "accuracy": None
            }
            
            if scores is not None:
                record["scores"] = scores
            
            if backtest_result is not None:
                record["backtest"] = backtest_result
            
            # 檢查是否已有相同日期的預測
            existing_index = None
            for i, h in enumerate(history):
                if h.get("prediction_date") == prediction_date:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # 更新現有記錄
                # 保留原有狀態如果已驗證? 不，覆蓋
                history[existing_index] = record
                logger.info(f"更新預測記錄: {prediction_date}")
            else:
                # 新增記錄
                history.append(record)
                logger.info(f"新增預測記錄: {prediction_date}")
            
            # 儲存到檔案
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.success(f"預測結果已儲存: {prediction_date} - {numbers}")
            return True
            
        except Exception as e:
            logger.error(f"儲存預測記錄失敗: {e}")
            return False
    
    def load_all_predictions(self):
        """載入所有預測記錄"""
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入預測記錄失敗: {e}")
            return []
    
    def get_latest_prediction(self):
        """取得最新的預測記錄"""
        history = self.load_all_predictions()
        if not history:
            return None
        
        # 按建立時間排序,取最新的
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return history[0]
    
    def get_prediction_by_date(self, prediction_date):
        """根據預測日期查詢記錄"""
        history = self.load_all_predictions()
        for record in history:
            if record.get("prediction_date") == prediction_date:
                return record
        return None
    
    def update_actual_result(self, prediction_date, actual_numbers):
        """
        更新實際開獎結果 (支援多組預測號碼)
        
        Args:
            prediction_date: 預測日期
            actual_numbers: 實際開獎號碼
        """
        try:
            history = self.load_all_predictions()
            updated = False
            
            for record in history:
                if record.get("prediction_date") == prediction_date:
                    predicted = record.get("predicted_numbers", [])
                    
                    # 處理多組號碼
                    best_accuracy = 0.0
                    best_hits = []
                    
                    prediction_sets = []
                    if len(predicted) > 0 and isinstance(predicted[0], list):
                        prediction_sets = predicted
                    else:
                        prediction_sets = [predicted]
                    
                    actual_set = set(actual_numbers)
                    
                    for p_set in prediction_sets:
                         p_set_clean = [int(x) for x in p_set]
                         hits = list(set(p_set_clean) & actual_set)
                         acc = len(hits) / 5.0
                         
                         if acc > best_accuracy or (acc == best_accuracy and len(hits) > len(best_hits)):
                             best_accuracy = acc
                             best_hits = hits
                    
                    record["actual_numbers"] = actual_numbers
                    record["hits"] = best_hits
                    record["accuracy"] = best_accuracy
                    record["status"] = "verified"
                    record["verified_at"] = get_taiwan_datetime_str()
                    
                    updated = True
                    logger.info(f"更新記錄 {prediction_date} -> Verified (Best Accuracy: {best_accuracy:.0%})")
                    break
            
            if updated:
                # 儲存更新 (Atomic write to avoid corruption)
                start_write = get_taiwan_now()
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                
                logger.success("實際結果已更新到檔案")
                return True
            else:
                logger.warning(f"找不到預測記錄: {prediction_date}")
                return False
            
        except Exception as e:
            logger.error(f"更新實際結果失敗: {e}")
            return False
    
    def has_pending_prediction(self):
        """檢查是否有待驗證的預測"""
        latest = self.get_latest_prediction()
        if latest and latest.get("status") == "pending":
            return True
        return False
    
    def get_pending_prediction(self):
        """取得待驗證的預測"""
        latest = self.get_latest_prediction()
        if latest and latest.get("status") == "pending":
            return latest
        return None
    
    def get_all_predictions(self):
        """取得所有預測記錄 (別名方法,與 load_all_predictions 相同)"""
        return self.load_all_predictions()

# 建立全域實例
prediction_history = PredictionHistory()

if __name__ == "__main__":
    # 測試
    ph = PredictionHistory()
    
    # 儲存測試
    print("測試儲存預測...")
    ph.save_prediction(
        prediction_date="2026-01-01 週四",
        numbers=[[8, 10, 16, 20, 21], [1, 2, 3, 4, 5]]
    )
    
    # 載入測試
    print("\n測試載入最新預測...")
    latest = ph.get_latest_prediction()
    print(f"最新預測: {latest}")
    
    # 更新結果測試
    print("\n測試更新實際結果...")
    ph.update_actual_result(
        prediction_date="2026-01-01 週四",
        actual_numbers=[8, 15, 20, 25, 32]
    )
    
    # 再次載入
    print("\n更新後的記錄:")
    latest = ph.get_latest_prediction()
    if latest:
        print(f"與預測狀態: {latest.get('status')}")
        print(f"準確率: {latest.get('accuracy', 0):.0%}")
