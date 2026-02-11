"""
測試 MinMaxScaler 修復是否正確
驗證 XGBoost 和 Random Forest 不再全為 0
"""
from src.models import FeatureEngine
import pandas as pd

def main():
    print("="*60)
    print("測試 MinMaxScaler 修復")
    print("="*60)
    
    # 載入測試資料 (使用前 60 期)
    df = pd.read_csv("data/539_history.csv").head(60)
    print(f"載入資料: {len(df)} 期")
    
    # 建立特徵引擎
    eng = FeatureEngine(data_df=df)
    
    # 測試增強模型
    print("\n計算所有模型評分 (包含增強模型)...")
    scores = eng.get_all_scores(use_enhanced=True)
    
    # 驗證 XGBoost 和 Random Forest 不再全為 0
    print("\n" + "="*60)
    print("驗證結果")
    print("="*60)
    
    for model in ['xgboost', 'random_forest']:
        if model in scores.columns:
            model_scores = scores[model]
            print(f"\n{model.upper()}:")
            print(f"  評分範圍: {model_scores.min():.3f} - {model_scores.max():.3f}")
            print(f"  平均值: {model_scores.mean():.3f}")
            print(f"  非零數量: {(model_scores > 0.01).sum()} / 39")
            
            # 檢查是否有非零值
            if model_scores.max() > 0.01:
                print(f"  [OK] {model} 正常運作!")
            else:
                print(f"  [FAIL] {model} 仍然全為 0!")
                return False
    
    print("\n" + "="*60)
    print("前 5 名號碼的模型評分對比")
    print("="*60)
    
    # 計算綜合評分
    avg_scores = scores.mean(axis=1).sort_values(ascending=False)
    top5 = avg_scores.head(5)
    
    # 檢查哪些模型可用
    has_xgb = 'xgboost' in scores.columns
    has_rf = 'random_forest' in scores.columns
    
    if has_xgb and has_rf:
        print("\n號碼 | 綜合 | Freq | RSI | XGB | RF")
        print("-" * 50)
        for num in top5.index:
            print(f"{num:4d} | {avg_scores[num]:.3f} | {scores.loc[num, 'freq']:.3f} | "
                  f"{scores.loc[num, 'rsi']:.3f} | {scores.loc[num, 'xgboost']:.3f} | "
                  f"{scores.loc[num, 'random_forest']:.3f}")
    else:
        print("\n號碼 | 綜合 | Freq | RSI")
        print("-" * 40)
        for num in top5.index:
            print(f"{num:4d} | {avg_scores[num]:.3f} | {scores.loc[num, 'freq']:.3f} | "
                  f"{scores.loc[num, 'rsi']:.3f}")
    
    print("\n" + "="*60)
    print("[SUCCESS] MinMaxScaler 修復成功!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
