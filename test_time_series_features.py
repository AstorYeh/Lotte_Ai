# -*- coding: utf-8 -*-
"""
測試時間序列特徵
"""
import sys
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models import FeatureEngine

def main():
    print("="*80)
    print("測試時間序列特徵")
    print("="*80)
    
    # 創建特徵引擎
    print("\n1. 創建 FeatureEngine...")
    eng = FeatureEngine(data_path='data/539_history.csv')
    
    # 測試時間序列特徵
    print("\n2. 測試時間序列特徵...")
    scores = eng.get_all_scores(use_enhanced=True, use_time_series=True)
    
    print(f"\n3. 評分結果:")
    print(f"  - 總模型數: {len(scores.columns)}")
    print(f"  - 模型列表: {list(scores.columns)}")
    print(f"\n前 10 個號碼的評分:")
    print(scores.head(10))
    
    # 檢查時間序列特徵
    ts_features = ['days_since', 'consecutive_absence', 'frequency_trend', 'periodicity']
    print(f"\n4. 時間序列特徵檢查:")
    for feature in ts_features:
        if feature in scores.columns:
            print(f"  ✅ {feature}: 範圍 [{scores[feature].min():.3f}, {scores[feature].max():.3f}]")
        else:
            print(f"  ❌ {feature}: 未找到")
    
    print("\n" + "="*80)
    print("測試完成!")
    print("="*80)

if __name__ == "__main__":
    main()
