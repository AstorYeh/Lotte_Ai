# -*- coding: utf-8 -*-
"""
更新訓練數據 - 將 history 複製到 train
"""
import pandas as pd
import shutil

# 複製歷史數據到訓練數據
shutil.copy('data/539_history.csv', 'data/539_train.csv')

# 讀取並顯示資訊
df = pd.read_csv('data/539_train.csv')

print(f"訓練數據已更新!")
print(f"總筆數: {len(df)}")
print(f"日期範圍: {df.iloc[0]['date']} ~ {df.iloc[-1]['date']}")
