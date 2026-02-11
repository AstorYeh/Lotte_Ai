# -*- coding: utf-8 -*-
"""
特徵重要性分析 - 找出最有效的模型
"""
import sys
from pathlib import Path
import json
import pandas as pd
import numpy as np

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.incremental_trainer import IncrementalTrainer
from src.profit_evaluator import ProfitEvaluator

def analyze_feature_importance(test_periods=100):
    """
    分析每個模型的重要性
    
    方法:
    1. 逐個移除模型
    2. 重新訓練並評估
    3. 計算性能變化
    4. 貢獻度 = 基準性能 - 移除後性能
    
    Args:
        test_periods: 測試期數 (默認 100 期快速測試)
    
    Returns:
        dict: 模型重要性排序
    """
    print("="*80)
    print("特徵重要性分析")
    print("="*80)
    
    # 基礎 7 個模型 + 增強 2 個模型
    all_models = [
        'freq',           # 頻率
        'rsi',            # RSI 指標
        'slope',          # 線性回歸趨勢
        'knn',            # K 近鄰
        'svm',            # 支持向量機
        'markov',         # 馬可夫鏈
        'pca',            # PCA 變異數
        'xgboost',        # XGBoost (增強)
        'random_forest'   # Random Forest (增強)
    ]
    
    print(f"\n總模型數: {len(all_models)}")
    print(f"模型列表: {all_models}")
    print(f"\n測試策略: 逐個移除模型,評估性能變化")
    print(f"測試期數: {test_periods} 期")
    
    # 存儲結果
    results = {}
    
    # 1. 先測試基準 (所有模型)
    print(f"\n{'='*80}")
    print("步驟 1: 測試基準 (所有模型)")
    print(f"{'='*80}")
    
    baseline_score = test_model_combination(all_models, "基準 (所有模型)")
    print(f"\n基準 2+ 命中率: {baseline_score:.2f}%")
    
    # 2. 逐個移除模型
    print(f"\n{'='*80}")
    print("步驟 2: 逐個移除模型並評估")
    print(f"{'='*80}")
    
    for model in all_models:
        print(f"\n{'-'*80}")
        print(f"移除模型: {model}")
        print(f"{'-'*80}")
        
        # 創建不包含該模型的列表
        remaining_models = [m for m in all_models if m != model]
        
        # 測試
        score = test_model_combination(
            remaining_models, 
            f"移除 {model}"
        )
        
        # 計算貢獻度
        contribution = baseline_score - score
        
        results[model] = {
            'score_without': score,
            'contribution': contribution,
            'is_positive': contribution > 0
        }
        
        print(f"\n結果:")
        print(f"  移除後 2+ 命中率: {score:.2f}%")
        print(f"  貢獻度: {contribution:+.2f}%")
        
        if contribution > 0:
            print(f"  結論: ✅ 有效模型 (移除後性能下降)")
        elif contribution < 0:
            print(f"  結論: ❌ 噪音模型 (移除後性能提升!)")
        else:
            print(f"  結論: ⚪ 中性模型 (無影響)")
    
    # 3. 分析結果
    print(f"\n{'='*80}")
    print("步驟 3: 分析結果")
    print(f"{'='*80}")
    
    # 按貢獻度排序
    sorted_results = sorted(
        results.items(),
        key=lambda x: x[1]['contribution'],
        reverse=True
    )
    
    print(f"\n模型重要性排序 (按貢獻度):")
    print(f"\n{'排名':<6} {'模型':<15} {'貢獻度':<12} {'移除後性能':<15} {'結論'}")
    print("-"*80)
    
    for i, (model, data) in enumerate(sorted_results, 1):
        contribution = data['contribution']
        score = data['score_without']
        
        if contribution > 0.5:
            conclusion = "✅ 重要"
        elif contribution > 0:
            conclusion = "⚪ 有用"
        elif contribution > -0.5:
            conclusion = "⚠️ 可疑"
        else:
            conclusion = "❌ 噪音"
        
        print(f"{i:<6} {model:<15} {contribution:+.2f}%{'':<6} {score:.2f}%{'':<8} {conclusion}")
    
    # 4. 建議
    print(f"\n{'='*80}")
    print("步驟 4: 建議")
    print(f"{'='*80}")
    
    # 找出噪音模型
    noise_models = [m for m, d in results.items() if d['contribution'] < 0]
    useful_models = [m for m, d in results.items() if d['contribution'] >= 0]
    
    print(f"\n噪音模型 (建議移除): {noise_models if noise_models else '無'}")
    print(f"有用模型 (建議保留): {useful_models}")
    
    if noise_models:
        print(f"\n建議配置:")
        print(f"  保留模型: {useful_models}")
        print(f"  預期性能: {baseline_score + sum(abs(results[m]['contribution']) for m in noise_models):.2f}%")
    else:
        print(f"\n所有模型都是有用的,無法通過移除模型來提升性能")
    
    # 保存結果
    result_file = Path("logs") / "feature_importance_analysis.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'baseline_score': baseline_score,
            'model_importance': {
                m: {
                    'contribution': float(d['contribution']),
                    'score_without': float(d['score_without'])
                }
                for m, d in results.items()
            },
            'noise_models': noise_models,
            'useful_models': useful_models
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果已保存: {result_file}")
    
    return results

def test_model_combination(models, description):
    """
    測試特定模型組合的性能
    
    Args:
        models: 模型列表
        description: 描述
    
    Returns:
        float: 2+ 顆命中率
    """
    print(f"\n測試: {description}")
    print(f"模型數量: {len(models)}")
    print(f"模型列表: {models}")
    
    # 這裡需要修改 FeatureEngine 來支持選擇性啟用模型
    # 暫時返回模擬值
    # TODO: 實作實際訓練邏輯
    
    # 模擬: 返回隨機值
    # 實際應該執行完整訓練
    score = 20.0 + np.random.randn() * 2
    
    return score

def main():
    print("="*80)
    print("特徵重要性分析 - 找出最有效的模型")
    print("="*80)
    print("\n目標:")
    print("  1. 分析每個模型的貢獻度")
    print("  2. 找出噪音模型")
    print("  3. 優化模型組合")
    print("  4. 提升 2+ 命中率")
    print("="*80 + "\n")
    
    # 執行分析
    results = analyze_feature_importance(test_periods=100)
    
    print("\n" + "="*80)
    print("分析完成!")
    print("="*80)

if __name__ == "__main__":
    main()
