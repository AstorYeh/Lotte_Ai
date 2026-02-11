# -*- coding: utf-8 -*-
"""
分割資料腳本
將 539_history.csv 分割成 2025 和 2026 兩個檔案
"""
import pandas as pd
from pathlib import Path

def split_data_by_year():
    """按年份分割資料"""
    
    print("=" * 60)
    print("開始分割資料...")
    print("=" * 60)
    
    # 讀取完整資料
    df = pd.read_csv('data/539_history.csv')
    print(f"\n[INFO] 總資料筆數: {len(df)}")
    
    # 解析日期並提取年份
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    # 分割資料
    df_2025 = df[df['year'] == 2025].copy()
    df_2026 = df[df['year'] == 2026].copy()
    
    # 移除臨時欄位
    df_2025 = df_2025.drop('year', axis=1)
    df_2026 = df_2026.drop('year', axis=1)
    
    # 確保日期格式一致
    df_2025['date'] = df_2025['date'].dt.strftime('%Y-%m-%d')
    df_2026['date'] = df_2026['date'].dt.strftime('%Y-%m-%d')
    
    # 儲存
    df_2025.to_csv('data/539_2025.csv', index=False)
    df_2026.to_csv('data/539_2026.csv', index=False)
    
    print(f"\n[OK] 2025 資料: {len(df_2025)} 筆")
    print(f"   日期範圍: {df_2025['date'].min()} ~ {df_2025['date'].max()}")
    print(f"\n[OK] 2026 資料: {len(df_2026)} 筆")
    print(f"   日期範圍: {df_2026['date'].min()} ~ {df_2026['date'].max()}")
    
    print("\n" + "=" * 60)
    print("分割完成!")
    print("=" * 60)
    
    return df_2025, df_2026

if __name__ == "__main__":
    split_data_by_year()
