# -*- coding: utf-8 -*-
"""
轉換台灣彩券官方資料格式
將官方下載的 CSV 轉換成系統需要的格式
"""
import pandas as pd
from pathlib import Path
import os
import sys

# Windows Unicode console fix
sys.stdout.reconfigure(encoding='utf-8')

def get_file_path(year, game_name):
    """
    Find the correct file path, handling the extra '2024' directory issue.
    """
    # Try standard path
    path1 = f"D:/539/data/temp_{year}/{game_name}_{year}.csv"
    if os.path.exists(path1):
        return path1
    
    # Try nested path (common for 2024)
    path2 = f"D:/539/data/temp_{year}/{year}/{game_name}_{year}.csv"
    if os.path.exists(path2):
        return path2
        
    return None

def convert_539_data():
    """轉換 539 資料"""
    print("\n" + "=" * 80)
    print("[1/5] 轉換 539 資料")
    print("=" * 80)
    
    all_data = []
    
    for year in [2024, 2025, 2026]:
        file_path = get_file_path(year, "今彩539")
        if not file_path:
            print(f"  {year} 年: 找不到檔案 (今彩539)")
            continue
            
        try:
            # 讀取官方 CSV (使用 UTF-8-SIG 處理 BOM)
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"  {year} 年: {len(df)} 筆")
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row.iloc[2]) if len(row) > 2 else str(row.iloc[0])
                    
                    if '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            year_part = int(parts[0])
                            if year_part < 1000:  # 民國年
                                year_part += 1911
                            date = f"{year_part}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                        else:
                            continue
                    else:
                        continue
                    
                    numbers = []
                    for col in row[6:11]:  # 5個號碼
                        try:
                            num = int(col)
                            if 1 <= num <= 39:
                                numbers.append(num)
                        except:
                            pass
                    
                    if len(numbers) == 5:
                        numbers.sort()
                        all_data.append({
                            'date': date,
                            'numbers': ','.join([str(n) for n in numbers])
                        })
                except Exception as e:
                    pass
        
        except Exception as e:
            print(f"  {year} 年: 讀取失敗 - {e}")
    
    if all_data:
        df = pd.DataFrame(all_data)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/539_history.csv", index=False)
        print(f"\n[OK] 539 完成: {len(df)} 筆資料")
        return len(df)
    return 0


def convert_lotto_data():
    """轉換大樂透資料"""
    print("\n" + "=" * 80)
    print("[2/5] 轉換大樂透資料")
    print("=" * 80)
    
    all_data = []
    
    for year in [2024, 2025, 2026]:
        file_path = get_file_path(year, "大樂透")
        if not file_path:
             print(f"  {year} 年: 找不到檔案 (大樂透)")
             continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"  {year} 年: {len(df)} 筆")
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row.iloc[2])
                    if '/' in date_str:
                        parts = date_str.split('/')
                        year_part = int(parts[0]) + 1911 if int(parts[0]) < 1000 else int(parts[0])
                        date = f"{year_part}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    else:
                        continue
                    
                    numbers = []
                    for col in row[6:12]:  # 6個號碼
                        try:
                            num = int(col)
                            numbers.append(num)
                        except:
                            pass
                    
                    special = None
                    try:
                        special = int(row.iloc[12])
                    except:
                        pass
                    
                    if len(numbers) == 6 and special is not None:
                        numbers.sort()
                        # Flattened format
                        record = {'date': date}
                        for i, n in enumerate(numbers):
                            record[f'{i+1}'] = n
                        record['special'] = special
                        all_data.append(record)
                except:
                    pass
        
        except Exception as e:
            print(f"  {year} 年: 讀取失敗 - {e}")
    
    if all_data:
        Path("data/lotto").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(all_data)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        # Ensure column order
        cols = ['date', '1', '2', '3', '4', '5', '6', 'special']
        df = df[cols]
        df.to_csv("data/lotto/lotto_history.csv", index=False)
        print(f"\n[OK] 大樂透完成: {len(df)} 筆資料")
        return len(df)
    return 0


def convert_power_data():
    """轉換威力彩資料"""
    print("\n" + "=" * 80)
    print("[3/5] 轉換威力彩資料")
    print("=" * 80)
    
    all_data = []
    
    for year in [2024, 2025, 2026]:
        file_path = get_file_path(year, "威力彩")
        if not file_path:
             print(f"  {year} 年: 找不到檔案 (威力彩)")
             continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"  {year} 年: {len(df)} 筆")
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row.iloc[2])
                    if '/' in date_str:
                        parts = date_str.split('/')
                        year_part = int(parts[0]) + 1911 if int(parts[0]) < 1000 else int(parts[0])
                        date = f"{year_part}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    else:
                        continue
                    
                    zone1 = []
                    for col in row[6:12]:
                        try:
                            num = int(col)
                            zone1.append(num)
                        except:
                            pass
                    
                    zone2 = None
                    try:
                        zone2 = int(row.iloc[12])
                    except:
                        pass
                    
                    if len(zone1) == 6 and zone2 is not None:
                        zone1.sort()
                        record = {'date': date}
                        for i, n in enumerate(zone1):
                            record[f'{i+1}'] = n
                        record['zone2'] = zone2
                        all_data.append(record)
                except:
                    pass
        
        except Exception as e:
            print(f"  {year} 年: 讀取失敗 - {e}")
    
    if all_data:
        Path("data/power").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(all_data)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        cols = ['date', '1', '2', '3', '4', '5', '6', 'zone2']
        df = df[cols]
        df.to_csv("data/power/power_history.csv", index=False)
        print(f"\n[OK] 威力彩完成: {len(df)} 筆資料")
        return len(df)
    return 0


def convert_star3_data():
    """轉換 3星彩資料"""
    print("\n" + "=" * 80)
    print("[4/5] 轉換 3星彩資料")
    print("=" * 80)
    
    all_data = []
    
    for year in [2024, 2025, 2026]:
        file_path = get_file_path(year, "3星彩")
        if not file_path: continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"  {year} 年: {len(df)} 筆")
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row.iloc[2])
                    if '/' in date_str:
                        parts = date_str.split('/')
                        year_part = int(parts[0]) + 1911 if int(parts[0]) < 1000 else int(parts[0])
                        date = f"{year_part}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    else:
                        continue
                    
                    # 3星彩號碼 (Index 6, 7, 8)
                    n1 = str(row.iloc[6]).strip()
                    n2 = str(row.iloc[7]).strip()
                    n3 = str(row.iloc[8]).strip()
                    
                    if n1.isdigit() and n2.isdigit() and n3.isdigit():
                        all_data.append({
                            'date': date,
                            '1': n1, '2': n2, '3': n3
                        })
                except:
                    pass
        except:
             pass
    
    if all_data:
        Path("data/star3").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(all_data)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/star3/star3_history.csv", index=False)
        print(f"\n[OK] 3星彩完成: {len(df)} 筆資料")
        return len(df)
    return 0


def convert_star4_data():
    """轉換 4星彩資料"""
    print("\n" + "=" * 80)
    print("[5/5] 轉換 4星彩資料")
    print("=" * 80)
    
    all_data = []
    
    for year in [2024, 2025, 2026]:
        file_path = get_file_path(year, "4星彩")
        if not file_path: continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"  {year} 年: {len(df)} 筆")
            
            for _, row in df.iterrows():
                try:
                    date_str = str(row.iloc[2])
                    if '/' in date_str:
                        parts = date_str.split('/')
                        year_part = int(parts[0]) + 1911 if int(parts[0]) < 1000 else int(parts[0])
                        date = f"{year_part}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    else:
                        continue
                    
                    # 4星彩號碼 (Index 6, 7, 8, 9)
                    n1 = str(row.iloc[6]).strip()
                    n2 = str(row.iloc[7]).strip()
                    n3 = str(row.iloc[8]).strip()
                    n4 = str(row.iloc[9]).strip()
                    
                    if n1.isdigit() and n2.isdigit() and n3.isdigit() and n4.isdigit():
                         all_data.append({
                            'date': date,
                            '1': n1, '2': n2, '3': n3, '4': n4
                        })
                except:
                    pass
        except:
            pass
    
    if all_data:
        Path("data/star4").mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(all_data)
        df = df.drop_duplicates(subset=['date'])
        df = df.sort_values('date')
        df.to_csv("data/star4/star4_history.csv", index=False)
        print(f"\n[OK] 4星彩完成: {len(df)} 筆資料")
        return len(df)
    return 0


if __name__ == "__main__":
    print("=" * 80)
    print("轉換台灣彩券官方資料")
    print("=" * 80)
    
    total = 0
    total += convert_539_data()
    total += convert_lotto_data()
    total += convert_power_data()
    total += convert_star3_data()
    total += convert_star4_data()
    
    print("\n" + "=" * 80)
    print("轉換完成!")
    print("=" * 80)
    print(f"總筆數: {total}")
    print("=" * 80)
