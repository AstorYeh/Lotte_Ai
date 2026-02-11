"""
539 測試資料生成器
用於生成模擬的 2025/2026 年開獎資料,方便測試訓練集/測試集分離功能
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_539_numbers():
    """隨機生成 5 個不重複的 1-39 號碼"""
    numbers = np.random.choice(range(1, 40), size=5, replace=False)
    return sorted(numbers.tolist())

def generate_test_data():
    """生成測試資料集"""
    
    # 生成 2025 年資料 (訓練集)
    train_data = []
    start_date = datetime(2025, 1, 1)
    
    # 2025 年每天開獎 (除了週日)
    current_date = start_date
    while current_date.year == 2025:
        # 跳過週日 (weekday() == 6)
        if current_date.weekday() != 6:
            numbers = generate_539_numbers()
            train_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'numbers': ','.join([f'{n:02d}' for n in numbers])
            })
        current_date += timedelta(days=1)
    
    # 生成 2026 年資料 (測試集) - 1月份
    test_data = []
    current_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 26)  # 到今天為止
    
    while current_date <= end_date:
        if current_date.weekday() != 6:
            numbers = generate_539_numbers()
            test_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'numbers': ','.join([f'{n:02d}' for n in numbers])
            })
        current_date += timedelta(days=1)
    
    # 建立 DataFrame
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)
    full_df = pd.concat([train_df, test_df], ignore_index=True)
    
    # 儲存檔案
    os.makedirs('data', exist_ok=True)
    
    train_df.to_csv('data/539_train.csv', index=False)
    test_df.to_csv('data/539_test.csv', index=False)
    full_df.to_csv('data/539_history.csv', index=False)
    
    print("=" * 60)
    print("[OK] 測試資料生成完成!")
    print("=" * 60)
    print(f"[訓練集] (2025): {len(train_df)} 筆 -> data/539_train.csv")
    print(f"[測試集] (2026): {len(test_df)} 筆 -> data/539_test.csv")
    print(f"[完整資料]: {len(full_df)} 筆 -> data/539_history.csv")
    print("=" * 60)
    
    # 顯示範例資料
    print("\n[訓練集範例] (前 5 筆):")
    print(train_df.head())
    
    print("\n[測試集範例] (前 5 筆):")
    print(test_df.head())
    
    return train_df, test_df, full_df

if __name__ == "__main__":
    generate_test_data()
