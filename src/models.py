import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import NearestNeighbors
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
import warnings

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings('ignore')

class FeatureEngine:
    def __init__(self, data_df=None, data_path='data/539_train.csv'):
        """
        初始化特徵引擎
        
        Args:
            data_df: 直接傳入 DataFrame (優先使用,用於漸進式訓練)
            data_path: 資料檔案路徑 (當 data_df 為 None 時使用)
        """
        self.data_path = data_path
        
        # 優先使用傳入的 DataFrame
        if data_df is not None:
            self.df = data_df.copy()
            # 確保日期格式正確
            if 'date' in self.df.columns:
                self.df['date'] = pd.to_datetime(self.df['date'])
                self.df = self.df.sort_values(by='date').reset_index(drop=True)
            print(f"[OK] 使用傳入資料: {len(self.df)} 筆")
        else:
            # 從檔案載入
            self.df = self.load_data()
        
        self.numbers_series = self.df['numbers'].apply(lambda x: [int(n) for n in x.split(',')]).tolist()
        self.total_numbers = 39

    def load_data(self):
        """載入資料,若訓練集不存在則降級使用完整資料"""
        # 嘗試載入指定路徑
        if pd.io.common.file_exists(self.data_path):
            print(f"[OK] 載入資料: {self.data_path}")
        else:
            # 降級處理:嘗試使用完整資料
            fallback_path = 'data/539_history.csv'
            if pd.io.common.file_exists(fallback_path):
                print(f"[WARNING] {self.data_path} 不存在,使用備援資料: {fallback_path}")
                self.data_path = fallback_path
            else:
                raise FileNotFoundError(
                    f"找不到資料檔案: {self.data_path}\n"
                    f"請先執行爬蟲程式: python -m src.crawler"
                )
        
        df = pd.read_csv(self.data_path)
        # Sort ascending (oldest to newest)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date').reset_index(drop=True)
        print(f"[INFO] 資料筆數: {len(df)} 筆 (日期範圍: {df['date'].min()} ~ {df['date'].max()})")
        return df

    def get_binary_matrix(self):
        """Convert list of numbers to binary matrix (rows=draws, cols=1-39)"""
        matrix = np.zeros((len(self.df), 39), dtype=int)
        for i, nums in enumerate(self.numbers_series):
            for n in nums:
                matrix[i, n-1] = 1
        return pd.DataFrame(matrix, columns=range(1, 40))

    def calc_freq(self, window=100):
        print("Calculating Frequency...")
        matrix = self.get_binary_matrix()
        # Sum of last N rows
        recent = matrix.tail(window)
        freq = recent.sum() / window
        return freq

    def calc_rsi(self, window=14):
        print("Calculating RSI-like indicator...")
        # Concept: Treat "appearance" as price gain
        # We calculate a rolling mean of appearance frequency as a proxy for 'price'
        matrix = self.get_binary_matrix()
        
        # Calculate Rolling Count (Availability Momentum)
        # Using a shorter window to capture immediate trends for RSI input
        rolling_counts = matrix.rolling(window=5).sum()
        
        # Calculate RSI on this rolling count series
        # Standard RSI formula
        delta = rolling_counts.diff()
        
        rsi_scores = {}
        for col in matrix.columns:
            d = delta[col]
            gain = d.where(d > 0, 0)
            loss = -d.where(d < 0, 0)
            
            avg_gain = gain.rolling(window=window).mean().iloc[-1]
            avg_loss = loss.rolling(window=window).mean().iloc[-1]
            
            if avg_loss == 0:
                rsi = 1.0
            else:
                rs = avg_gain / avg_loss
                rsi = 1 - (1 / (1 + rs))
            rsi_scores[col] = rsi
            
        return pd.Series(rsi_scores)

    def calc_linear_regression(self, window=75):
        print("Calculating Linear Regression trends...")
        matrix = self.get_binary_matrix()
        
        # 動態調整窗口大小,不超過實際資料筆數
        actual_window = min(window, len(matrix))
        subset = matrix.tail(actual_window)
        
        slopes = {}
        X = np.arange(actual_window).reshape(-1, 1)  # 使用實際窗口大小
        
        for col in matrix.columns:
            # We want to see if the frequency is increasing or decreasing
            # Let's fit on the cumulative sum (trend)
            y = subset[col].cumsum().values
            
            model = LinearRegression()
            model.fit(X, y)
            # Slope indicates rate of appearance. 
            # Steep positive slope = frequent. 
            # We want the acceleration? 
            # Or just regression on binary 0/1? (Too noisy)
            # Regression on rolling sum seems stable.
            slopes[col] = model.coef_[0]
            
        return pd.Series(slopes)

    def calc_knn(self, k=5):
        print(f"Calculating KNN (k={k})...")
        # Find historical draws most similar to the LAST draw
        matrix = self.get_binary_matrix().values
        if len(matrix) < k + 1:
            return pd.Series(0, index=range(1, 40))
            
        target = matrix[-1].reshape(1, -1)
        history = matrix[:-1] # Exclude the last specific one to avoid self-match if doing loo, but here we compare target to history
        
        nbrs = NearestNeighbors(n_neighbors=k, metric='jaccard') # Jaccard is good for binary
        nbrs.fit(history)
        
        distances, indices = nbrs.kneighbors(target)
        
        # Look at the 'next' draw for these neighbors
        # If history[i] is similar to target, then history[i+1] is a prediction candidate
        
        prediction_counts = np.zeros(39)
        
        for idx in indices[0]:
            if idx + 1 < len(matrix):
                next_draw_binary = matrix[idx + 1]
                prediction_counts += next_draw_binary
                
        return pd.Series(prediction_counts / k, index=range(1, 40))

    def calc_svm(self, window=50):
        print("Calculating SVM probabilities...")
        # Train a light SVM for each number
        matrix = self.get_binary_matrix()
        
        # Use last N records for training to keep it fast
        train_size = 200
        if len(matrix) < train_size + 1:
            train_size = len(matrix) - 1
            
        dataset = matrix.tail(train_size + 1)
        X = dataset.iloc[:-1].values # Features: Draw t
        
        scores = {}
        
        # This can be slow if we train 39 models.
        # Strategy: Input is [0..38] binary.
        # Label is "Will number N appear in t+1?"
        
        for col in matrix.columns:
            y = dataset[col].iloc[1:].values # Target: Draw t+1
            
            # Only train if we have both classes
            if len(np.unique(y)) < 2:
                scores[col] = 0.0
                continue
                
            clf = SVC(probability=True, kernel='rbf', C=1.0)
            clf.fit(X, y)
            
            # Predict for the unknown next draw (which is based on the REAL last draw)
            last_draw = matrix.iloc[-1].values.reshape(1, -1)
            prob = clf.predict_proba(last_draw)[0][1] # Probability of class 1
            scores[col] = prob
            
        return pd.Series(scores)

    def calc_markov(self):
        print("Calculating Markov Chain transition matrix...")
        matrix = self.get_binary_matrix().values
        transitions = np.zeros((39, 39))
        
        # For each draw t and t+1
        for t in range(len(matrix) - 1):
            current_draw = np.where(matrix[t] == 1)[0]
            next_draw = np.where(matrix[t+1] == 1)[0]
            
            for curr_num in current_draw:
                for next_num in next_draw:
                    transitions[curr_num, next_num] += 1
                    
        # Normalize rows to probabilities
        row_sums = transitions.sum(axis=1)
        # Avoid division by zero
        row_sums[row_sums == 0] = 1
        probs = transitions / row_sums[:, np.newaxis]
        
        # Prediction: Based on LAST draw
        last_draw_indices = np.where(matrix[-1] == 1)[0]
        future_probs = np.zeros(39)
        
        for idx in last_draw_indices:
            future_probs += probs[idx]
            
        # Normalize future probs
        if future_probs.max() > 0:
            future_probs = future_probs / future_probs.sum()
            
        return pd.Series(future_probs, index=range(1, 40))

    def calc_pca(self):
        print("Calculating Interval Variance (PCA-proxy)...")
        # Analyze stability of intervals
        matrix = self.get_binary_matrix()
        
        stability_scores = {}
        for col in matrix.columns:
            # Get indices where number appeared
            indices = matrix.index[matrix[col] == 1].tolist()
            if len(indices) < 2:
                stability_scores[col] = 0
                continue
                
            intervals = np.diff(indices)
            variance = np.var(intervals)
            
            # Low variance = High stability = Good?
            # Or High variance = Cold/Due to correct?
            # Usually we prefer stable patterns. 
            # Let's inverse variance: 1 / (1 + var)
            score = 100 / (1 + variance)
            stability_scores[col] = score
            
        return pd.Series(stability_scores)

    def get_all_scores(self, use_enhanced=False, use_time_series=False, enabled_models=None):
        """
        計算所有模型的評分
        
        Args:
            use_enhanced: 是否使用增強模型 (XGBoost, Random Forest)
            use_time_series: 是否使用時間序列特徵
            enabled_models: 啟用的模型列表 (None = 全部啟用)
        
        Returns:
            DataFrame: 每個號碼在各模型的評分
        """
        scores = pd.DataFrame(index=range(1, 40))
        
        # 基礎 7 個模型
        base_models = {
            'freq': self.calc_freq,
            'rsi': self.calc_rsi,
            'slope': self.calc_linear_regression,
            'knn': self.calc_knn,
            'svm': self.calc_svm,
            'markov': self.calc_markov,
            'pca': self.calc_pca
        }
        
        # 計算基礎模型
        for model_name, model_func in base_models.items():
            if enabled_models is None or model_name in enabled_models:
                scores[model_name] = model_func()
        
        # 增強模型 (如果啟用)
        if use_enhanced:
            try:
                from src.enhanced_models import EnhancedFeatureEngine
                enhanced = EnhancedFeatureEngine(self)
                
                if enabled_models is None or 'xgboost' in enabled_models:
                    scores['xgboost'] = enhanced.calc_xgboost(n_estimators=50)
                
                if enabled_models is None or 'random_forest' in enabled_models:
                    scores['random_forest'] = enhanced.calc_random_forest(n_estimators=50)
                
                print("[INFO] 已啟用增強模型 (XGBoost, Random Forest)")
            except Exception as e:
                print(f"[WARNING] 增強模型載入失敗: {e}")
                if enabled_models is None or 'xgboost' in enabled_models:
                    scores['xgboost'] = pd.Series(0.5, index=scores.index)
                if enabled_models is None or 'random_forest' in enabled_models:
                    scores['random_forest'] = pd.Series(0.5, index=scores.index)
        
        # 時間序列特徵 (如果啟用)
        if use_time_series:
            try:
                from src.advanced_features import TimeSeriesFeatures
                ts_features = TimeSeriesFeatures(self)
                
                # 獲取所有時間序列特徵
                ts_scores = ts_features.get_all_time_series_features()
                
                # 添加到評分 DataFrame
                for feature_name, feature_scores in ts_scores.items():
                    if enabled_models is None or feature_name in enabled_models:
                        scores[feature_name] = feature_scores
                
                print(f"[INFO] 已啟用時間序列特徵 ({len(ts_scores)} 個)")
            except Exception as e:
                print(f"[WARNING] 時間序列特徵載入失敗: {e}")
        
        # Normalize each column independently to 0-1
        # 重要: 每個模型獨立正規化,避免不同數值範圍的模型互相影響
        scores_scaled = pd.DataFrame(index=scores.index)
        scaler = MinMaxScaler()
        
        for col in scores.columns:
            # 對每個模型的評分獨立正規化
            col_data = scores[[col]].values
            scores_scaled[col] = scaler.fit_transform(col_data).flatten()
        
        return scores_scaled

if __name__ == "__main__":
    eng = FeatureEngine()
    print(eng.get_all_scores().head())
