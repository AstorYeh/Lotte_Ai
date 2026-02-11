# -*- coding: utf-8 -*-
"""
新增模型: XGBoost 和 Random Forest
擴展特徵引擎以支援更多強大的模型
🔧 已修復: 處理單類別訓練問題
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler

class EnhancedFeatureEngine:
    """增強版特徵引擎 - 新增 XGBoost 和 Random Forest"""
    
    def __init__(self, feature_engine):
        """
        Args:
            feature_engine: 原始的 FeatureEngine 實例
        """
        self.eng = feature_engine
        self.df = feature_engine.df
        self.numbers_series = feature_engine.numbers_series
        self.total_numbers = feature_engine.total_numbers
    
    def calc_xgboost(self, n_estimators=100):
        """使用 XGBoost 預測每個號碼的出現機率"""
        print("Calculating XGBoost predictions...")
        
        # 準備訓練資料
        binary_matrix = self.eng.get_binary_matrix()
        
        # 動態調整窗口:至少 20 期,最多 30 期
        window = min(max(20, len(binary_matrix) // 3), 30)
        
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            col_idx = num - 1
            
            # 準備特徵和標籤
            X = []
            y = []
            
            for i in range(window, len(binary_matrix)):
                features = binary_matrix.iloc[i-window:i, col_idx].values
                X.append(features)
                y.append(binary_matrix.iloc[i, col_idx])
            
            if len(X) > 10:
                X = np.array(X)
                y = np.array(y)
                
                try:
                    # 🔧 修復: 檢查標籤是否只有一個類別
                    unique_labels = np.unique(y)
                    
                    if len(unique_labels) < 2:
                        # 🧪 測試: 使用默認值 0.5 (原始值)
                        if unique_labels[0] == 0:
                            # 從未出現 → 使用中性值 0.5
                            scores[num] = 0.5
                        else:
                            # 每期都出現 → 使用大的值 (0.85)
                            scores[num] = 0.85
                    else:
                        # 正常訓練 XGBoost
                        model = xgb.XGBClassifier(
                            n_estimators=30,
                            max_depth=3,
                            learning_rate=0.1,
                            min_child_weight=5,
                            subsample=0.7,
                            colsample_bytree=0.7,
                            random_state=42,
                            use_label_encoder=False,
                            eval_metric='logloss'
                        )
                        
                        model.fit(X, y)
                        
                        # 預測下一期
                        last_features = binary_matrix.iloc[-window:, col_idx].values.reshape(1, -1)
                        prob = model.predict_proba(last_features)[0][1]
                        
                        scores[num] = prob
                except Exception as e:
                    # 🔧 修復: 使用歷史頻率作為默認值
                    print(f"Warning: XGBoost failed for number {num}: {e}")
                    scores[num] = float(y.mean()) if len(y) > 0 else 0.5
            else:
                # 🔧 修復: 使用歷史頻率作為默認值
                scores[num] = float(y.mean()) if len(y) > 0 else 0.5
        
        return pd.Series(scores)
    
    def calc_random_forest(self, n_estimators=100):
        """使用 Random Forest 預測每個號碼的出現機率"""
        print("Calculating Random Forest predictions...")
        
        binary_matrix = self.eng.get_binary_matrix()
        window = min(max(20, len(binary_matrix) // 3), 30)
        
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            col_idx = num - 1
            
            X = []
            y = []
            
            for i in range(window, len(binary_matrix)):
                features = binary_matrix.iloc[i-window:i, col_idx].values
                X.append(features)
                y.append(binary_matrix.iloc[i, col_idx])
            
            if len(X) > 10:
                X = np.array(X)
                y = np.array(y)
                
                try:
                    # 🔧 修復: 檢查標籤是否只有一個類別
                    unique_labels = np.unique(y)
                    
                    if len(unique_labels) < 2:
                        # 🧪 測試: 使用默認值 0.5 (原始值)
                        if unique_labels[0] == 0:
                            # 從未出現 → 使用中性值 0.5
                            scores[num] = 0.5
                        else:
                            # 每期都出現 → 使用大的值 (0.85)
                            scores[num] = 0.85
                    else:
                        # 正常訓練 Random Forest
                        model = RandomForestClassifier(
                            n_estimators=50,
                            max_depth=5,
                            min_samples_split=10,
                            min_samples_leaf=5,
                            max_features='sqrt',
                            random_state=42,
                            n_jobs=-1
                        )
                        
                        model.fit(X, y)
                        
                        # 預測
                        last_features = binary_matrix.iloc[-window:, col_idx].values.reshape(1, -1)
                        prob = model.predict_proba(last_features)[0][1]
                        
                        scores[num] = prob
                except Exception as e:
                    # 🔧 修復: 使用歷史頻率作為默認值
                    print(f"Warning: Random Forest failed for number {num}: {e}")
                    scores[num] = float(y.mean()) if len(y) > 0 else 0.5
            else:
                # 🔧 修復: 使用歷史頻率作為默認值
                scores[num] = float(y.mean()) if len(y) > 0 else 0.5
        
        return pd.Series(scores)
    
    def calc_enhanced_features(self):
        """計算增強特徵"""
        print("Calculating enhanced features...")
        
        features = {}
        
        # 1. 號碼間隔分析
        features['interval'] = self._calc_interval_score()
        
        # 2. 奇偶比例
        features['odd_even'] = self._calc_odd_even_score()
        
        # 3. 大小比例
        features['size'] = self._calc_size_score()
        
        # 4. 歷史相似度
        features['similarity'] = self._calc_similarity_score()
        
        return features
    
    def _calc_interval_score(self):
        """計算號碼間隔評分"""
        scores = {}
        
        for num in range(1, self.total_numbers + 1):
            # 計算該號碼最近一次出現的間隔
            intervals = []
            last_appear = -1
            
            for i, draw in enumerate(self.numbers_series):
                if num in draw:
                    if last_appear >= 0:
                        intervals.append(i - last_appear)
                    last_appear = i
            
            if intervals:
                avg_interval = np.mean(intervals)
                current_interval = len(self.numbers_series) - last_appear if last_appear >= 0 else 999
                
                # 如果當前間隔接近平均間隔,分數較高
                score = 1.0 - min(abs(current_interval - avg_interval) / avg_interval, 1.0)
                scores[num] = score
            else:
                scores[num] = 0.5
        
        return pd.Series(scores)
    
    def _calc_odd_even_score(self):
        """計算奇偶評分"""
        # 分析最近幾期的奇偶比例
        recent_draws = self.numbers_series[-10:]
        odd_counts = [sum(1 for n in draw if n % 2 == 1) for draw in recent_draws]
        avg_odd = np.mean(odd_counts)
        
        scores = {}
        for num in range(1, self.total_numbers + 1):
            if num % 2 == 1:  # 奇數
                scores[num] = avg_odd / 5.0
            else:  # 偶數
                scores[num] = (5 - avg_odd) / 5.0
        
        return pd.Series(scores)
    
    def _calc_size_score(self):
        """計算大小評分 (1-19 小, 20-39 大)"""
        recent_draws = self.numbers_series[-10:]
        small_counts = [sum(1 for n in draw if n <= 19) for draw in recent_draws]
        avg_small = np.mean(small_counts)
        
        scores = {}
        for num in range(1, self.total_numbers + 1):
            if num <= 19:  # 小號
                scores[num] = avg_small / 5.0
            else:  # 大號
                scores[num] = (5 - avg_small) / 5.0
        
        return pd.Series(scores)
    
    def _calc_similarity_score(self):
        """計算與歷史的相似度評分"""
        if len(self.numbers_series) < 2:
            return pd.Series({i: 0.5 for i in range(1, self.total_numbers + 1)})
        
        # 最近一期
        last_draw = set(self.numbers_series[-1])
        
        # 計算每個號碼與最近一期的關聯
        scores = {}
        for num in range(1, self.total_numbers + 1):
            # 如果號碼在最近一期出現,給予較低分數 (避免重複)
            if num in last_draw:
                scores[num] = 0.3
            else:
                scores[num] = 0.7
        
        return pd.Series(scores)

if __name__ == "__main__":
    # 測試
    from src.models import FeatureEngine
    
    print("測試增強特徵引擎...")
    
    eng = FeatureEngine()
    enhanced = EnhancedFeatureEngine(eng)
    
    # 測試 XGBoost
    xgb_scores = enhanced.calc_xgboost(n_estimators=50)
    print(f"XGBoost 評分範圍: {xgb_scores.min():.3f} - {xgb_scores.max():.3f}")
    
    # 測試 Random Forest
    rf_scores = enhanced.calc_random_forest(n_estimators=50)
    print(f"Random Forest 評分範圍: {rf_scores.min():.3f} - {rf_scores.max():.3f}")
    
    # 測試增強特徵
    enhanced_features = enhanced.calc_enhanced_features()
    print(f"增強特徵數量: {len(enhanced_features)}")
    
    print("\n測試完成!")
