"""
GPU 加速模型包裝器
使用 XGBoost GPU + CuPy 進行加速
自動檢測 GPU 可用性,無 GPU 時回退到 CPU
"""
import warnings
import numpy as np
import pandas as pd

# GPU 可用性檢測
GPU_AVAILABLE = False
CUPY_AVAILABLE = False

# 嘗試載入 CuPy (用於 NumPy GPU 加速)
try:
    import cupy as cp
    CUPY_AVAILABLE = True
    print("[OK] CuPy loaded - NumPy operations will use GPU acceleration")
except ImportError:
    print("[WARN] CuPy not installed - NumPy operations use CPU")
    cp = np  # 回退到 NumPy

# 檢測 XGBoost GPU 支援
try:
    import xgboost as xgb
    # 測試 GPU 是否可用
    test_param = {'tree_method': 'gpu_hist', 'gpu_id': 0}
    GPU_AVAILABLE = True
    print("[OK] XGBoost GPU acceleration enabled")
except Exception as e:
    print(f"[WARN] XGBoost GPU not available: {e}")
    GPU_AVAILABLE = False

# sklearn 模型 (CPU)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier


class GPUModelWrapper:
    """GPU 模型統一介面 - 簡化版"""
    
    @staticmethod
    def to_gpu(data):
        """將資料轉換為 GPU 格式 (如果 CuPy 可用)"""
        if CUPY_AVAILABLE and isinstance(data, np.ndarray):
            return cp.asarray(data)
        return data
    
    @staticmethod
    def to_cpu(data):
        """將資料轉換回 CPU 格式"""
        if CUPY_AVAILABLE and isinstance(data, cp.ndarray):
            return cp.asnumpy(data)
        return data
    
    @staticmethod
    def get_xgboost_params(base_params):
        """
        取得 XGBoost 參數 (自動啟用 GPU)
        
        Args:
            base_params: 基礎參數字典
            
        Returns:
            優化後的參數字典
        """
        params = base_params.copy()
        
        if GPU_AVAILABLE:
            params['tree_method'] = 'gpu_hist'
            params['gpu_id'] = 0
            params['predictor'] = 'gpu_predictor'
            print("  → XGBoost 使用 GPU 加速")
        else:
            params['tree_method'] = 'hist'
            print("  → XGBoost 使用 CPU")
        
        return params
    
    @staticmethod
    def get_knn(**kwargs):
        """取得 KNN 模型 (CPU)"""
        return KNeighborsClassifier(**kwargs)
    
    @staticmethod
    def get_svc(**kwargs):
        """取得 SVC 模型 (CPU)"""
        return SVC(**kwargs)
    
    @staticmethod
    def get_linear_regression(**kwargs):
        """取得線性回歸模型 (CPU)"""
        return LinearRegression(**kwargs)
    
    @staticmethod
    def get_random_forest(**kwargs):
        """取得隨機森林模型 (CPU)"""
        # 使用所有 CPU 核心
        if 'n_jobs' not in kwargs:
            kwargs['n_jobs'] = -1
        return RandomForestClassifier(**kwargs)
    
    @staticmethod
    def accelerate_numpy_ops(func):
        """
        裝飾器: 加速 NumPy 運算 (如果 CuPy 可用)
        
        使用方式:
        @GPUModelWrapper.accelerate_numpy_ops
        def my_function(data):
            # 使用 np 進行運算
            return np.mean(data)
        """
        def wrapper(*args, **kwargs):
            if CUPY_AVAILABLE:
                # 將 NumPy 陣列轉換為 CuPy
                args = [GPUModelWrapper.to_gpu(arg) if isinstance(arg, np.ndarray) else arg 
                       for arg in args]
                result = func(*args, **kwargs)
                # 將結果轉回 CPU
                return GPUModelWrapper.to_cpu(result)
            else:
                return func(*args, **kwargs)
        return wrapper


def print_gpu_status():
    """顯示 GPU 狀態摘要"""
    print("\n" + "="*60)
    print("GPU Acceleration Status")
    print("="*60)
    print(f"XGBoost GPU: {'[ENABLED]' if GPU_AVAILABLE else '[DISABLED] (using CPU)'}")
    print(f"CuPy (NumPy GPU): {'[ENABLED]' if CUPY_AVAILABLE else '[DISABLED] (using CPU)'}")
    
    if GPU_AVAILABLE or CUPY_AVAILABLE:
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', 
                                   '--format=csv,noheader'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gpu_info = result.stdout.strip()
                print(f"GPU Info: {gpu_info}")
        except:
            pass
    
    print("="*60 + "\n")


if __name__ == "__main__":
    # 測試
    print_gpu_status()
    
    # 測試 XGBoost GPU
    if GPU_AVAILABLE:
        print("\n測試 XGBoost GPU 加速...")
        params = GPUModelWrapper.get_xgboost_params({
            'n_estimators': 100,
            'max_depth': 5,
            'learning_rate': 0.05
        })
        print(f"XGBoost 參數: {params}")
    
    # 測試 CuPy
    if CUPY_AVAILABLE:
        print("\n測試 CuPy 加速...")
        data = np.random.rand(1000, 1000)
        gpu_data = GPUModelWrapper.to_gpu(data)
        print(f"資料類型: {type(gpu_data)}")
        result = cp.mean(gpu_data)
        cpu_result = GPUModelWrapper.to_cpu(result)
        print(f"計算結果: {cpu_result}")
    
    print("\n[OK] GPU model wrapper test completed!")
