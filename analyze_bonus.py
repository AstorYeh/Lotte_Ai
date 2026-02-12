import pandas as pd
import glob
import os
from collections import Counter

def analyze_bonus():
    # 1. Spring Festival Bonus Data
    bonus_files = [
        'data/2024/2024/大樂透加開獎項_2024.csv',
        'data/2025/大樂透加開獎項_2025.csv'
    ]
    
    # 2. Regular 2025 Draws
    regular_files = [
        'data/2025/大樂透_2025.csv'
    ]
    
    all_numbers_hits = []
    
    print("Analyzing Combined Data (Bonus + 2025 Regular)...")
    
    # Process Bonus Files (Spring Festival)
    for f in bonus_files:
        if not os.path.exists(f): 
            continue
        print(f"Reading Bonus Data: {f}...")
        try:
            df = pd.read_csv(f)
            if '期別' not in df.columns: continue
            
            # Group by period to get the verified "pool" of 9 numbers per draw
            grouped = df.groupby('期別')
            for name, group in grouped:
                period_nums = set()
                for col in ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5', '獎號6']:
                    period_nums.update(group[col].dropna().unique())
                
                # Each number in the pool counts as 1 hit/appearance
                all_numbers_hits.extend([int(x) for x in period_nums])
                
        except Exception as e:
            print(f"Error: {e}")

    # Process Regular Files (2025 Trends)
    for f in regular_files:
        if not os.path.exists(f):
            continue
        print(f"Reading Regular Data: {f}...")
        try:
            df = pd.read_csv(f)
            # Regular draw: 6 numbers + 1 special number (physically drawn from the same machine)
            for _, row in df.iterrows():
                draw_nums = []
                # Main numbers
                for col in ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5', '獎號6']:
                    if pd.notna(row[col]):
                        draw_nums.append(int(row[col]))
                
                # Special number
                if '特別號' in df.columns and pd.notna(row['特別號']):
                    draw_nums.append(int(row['特別號']))
                
                # Add to total counts
                all_numbers_hits.extend(draw_nums)
                print(f"  Regular Draw {row.get('期別', 'N/A')}: {draw_nums}")
                
        except Exception as e:
            print(f"Error: {e}")

    # Frequency Analysis
    counts = Counter(all_numbers_hits)
    
    print("\n" + "="*50)
    print("🏆 Top Recommended Numbers (Combined Frequency)")
    print("="*50)
    
    sorted_counts = counts.most_common()
    
    rank = 1
    top_6 = []
    
    # Just generic formatting
    print(f"{'Rank':<5} | {'Number':<8} | {'Frequency':<10}")
    print("-" * 30)
    
    for num, freq in sorted_counts[:15]:
        print(f"#{rank:02d}   | {num:02d}       | {freq}")
        if rank <= 6:
            top_6.append(num)
        rank += 1
        
    print("\n" + "="*50)
    print(f"🔥 FINAL GOLDEN SET (Top 6): {sorted(top_6)}")
    print("="*50)

if __name__ == "__main__":
    analyze_bonus()
