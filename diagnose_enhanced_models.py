# -*- coding: utf-8 -*-
"""
診斷增強模型評分為 0 的問題
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
import numpy as np
from src.models import FeatureEngine
from src.enhanced_models import EnhancedFeatureEngine

def diagnose_enhanced_models():
    """診斷增強模型"""
    
    print("="*80)
    print("診斷增強模型評分為 0 的問題")
    print("="*80 + "\n")
    
    # 載入資料
    df = pd.read_csv("data/539_history.csv")
    print(f"[OK] 載入資料: {len(df)} 期\n")
    
    # 使用前 50 期進行測試
    test_df = df.head(50)
    
    # 創建特徵引擎
    print("步驟 1: 創建 FeatureEngine")
    print("-" * 60)
    eng = FeatureEngine(data_df=test_df)
    print(f"  - 資料期數: {len(eng.df)}")
    print(f"  - 號碼總數: {eng.total_numbers}\n")
    
    # 測試 get_binary_matrix
    print("步驟 2: 測試 get_binary_matrix()")
    print("-" * 60)
    binary_matrix = eng.get_binary_matrix()
    print(f"  - 矩陣形狀: {binary_matrix.shape}")
    print(f"  - 矩陣前 5 行:\n{binary_matrix.head()}\n")
    
    # 創建增強特徵引擎
    print("步驟 3: 創建 EnhancedFeatureEngine")
    print("-" * 60)
    enhanced = EnhancedFeatureEngine(eng)
    print(f"  - 增強引擎已創建\n")
    
    # 測試 XGBoost
    print("步驟 4: 測試 XGBoost")
    print("-" * 60)
    try:
        xgb_scores = enhanced.calc_xgboost(n_estimators=30)
        print(f"  - XGBoost 評分:\n{xgb_scores.head(10)}")
        print(f"  - 評分範圍: [{xgb_scores.min():.4f}, {xgb_scores.max():.4f}]")
        print(f"  - 平均評分: {xgb_scores.mean():.4f}")
        print(f"  - 評分為 0 的數量: {(xgb_scores == 0).sum()}")
        print(f"  - 評分為 0.5 的數量: {(xgb_scores == 0.5).sum()}\n")
    except Exception as e:
        print(f"  [ERROR] XGBoost 失敗: {e}\n")
        import traceback
        traceback.print_exc()
    
    # 測試 Random Forest
    print("步驟 5: 測試 Random Forest")
    print("-" * 60)
    try:
        rf_scores = enhanced.calc_random_forest(n_estimators=50)
        print(f"  - Random Forest 評分:\n{rf_scores.head(10)}")
        print(f"  - 評分範圍: [{rf_scores.min():.4f}, {rf_scores.max():.4f}]")
        print(f"  - 平均評分: {rf_scores.mean():.4f}")
        print(f"  - 評分為 0 的數量: {(rf_scores == 0).sum()}")
        print(f"  - 評分為 0.5 的數量: {(rf_scores == 0.5).sum()}\n")
    except Exception as e:
        print(f"  [ERROR] Random Forest 失敗: {e}\n")
        import traceback
        traceback.print_exc()
    
    # 測試正規化後的評分
    print("步驟 6: 測試正規化後的評分")
    print("-" * 60)
    try:
        all_scores = eng.get_all_scores(use_enhanced=True)
        print(f"  - 所有模型評分:\n{all_scores.head(10)}")
        print(f"\n  - XGBoost 正規化後:")
        print(f"    範圍: [{all_scores['xgboost'].min():.4f}, {all_scores['xgboost'].max():.4f}]")
        print(f"    平均: {all_scores['xgboost'].mean():.4f}")
        print(f"    評分為 0 的數量: {(all_scores['xgboost'] == 0).sum()}")
        
        print(f"\n  - Random Forest 正規化後:")
        print(f"    範圍: [{all_scores['random_forest'].min():.4f}, {all_scores['random_forest'].max():.4f}]")
        print(f"    平均: {all_scores['random_forest'].mean():.4f}")
        print(f"    評分為 0 的數量: {(all_scores['random_forest'] == 0).sum()}\n")
    except Exception as e:
        print(f"  [ERROR] 正規化失敗: {e}\n")
        import traceback
        traceback.print_exc()
    
    print("="*80)
    print("診斷完成!")
    print("="*80)

if __name__ == "__main__":
    diagnose_enhanced_models()
