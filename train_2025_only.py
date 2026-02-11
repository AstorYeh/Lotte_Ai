# -*- coding: utf-8 -*-
"""
2025 年資料訓練腳本
只使用 2025 年資料訓練模型,2026 年資料用於驗證
"""
import sys
import pandas as pd
from pathlib import Path
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger

def train_2025_only():
    """只使用 2025 年資料訓練"""
    
    print("=" * 60)
    print("開始訓練 (只使用 2025 年資料)")
    print("=" * 60)
    
    # 檢查資料檔案
    data_file = 'data/539_2025.csv'
    data_path = Path(data_file)
    if not data_path.exists():
        print("[ERROR] 找不到 data/539_2025.csv")
        print("[INFO] 請先執行 split_data_by_year.py")
        return
    
    # 讀取資料以顯示資訊
    df = pd.read_csv(data_file)
    print(f"\n[INFO] 載入 2025 年資料: {len(df)} 筆")
    print(f"[INFO] 日期範圍: {df['date'].min()} ~ {df['date'].max()}")
    
    # 初始化訓練器
    print("\n[INFO] 初始化訓練器...")
    trainer = IncrementalTrainer(
        initial_periods=30,
        use_llm=True,
        use_enhanced=False
    )
    
    # 訓練
    print("\n[INFO] 開始訓練...")
    trainer.train_all(data_file=data_file)
    
    print("\n" + "=" * 60)
    print("訓練完成!")
    print("=" * 60)
    print("\n[INFO] 下一步:")
    print("  1. 在主頁面生成 2026 年預測")
    print("  2. 使用回饋校正頁面驗證預測")
    print("  3. 在性能追蹤頁面查看結果")

if __name__ == "__main__":
    train_2025_only()
