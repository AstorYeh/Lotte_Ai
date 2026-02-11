# -*- coding: utf-8 -*-
"""
測試 LLM 顧問功能
"""
from src.llm_advisor import LLMAdvisor
from src.logger import logger

def test_llm_advisor():
    """測試 LLM 顧問"""
    
    print("=" * 60)
    print("測試 LLM 顧問 (Gemini 2.5 Flash)")
    print("=" * 60)
    
    # 初始化 LLM 顧問
    advisor = LLMAdvisor()
    
    if not advisor.model:
        print("\n[ERROR] LLM 顧問初始化失敗")
        print("[INFO] 請檢查:")
        print("  1. GEMINI_API_KEY 環境變數是否設定")
        print("  2. API Key 是否有效")
        print("  3. 網路連線是否正常")
        return
    
    print("\n[OK] LLM 顧問初始化成功")
    
    # 準備測試資料
    group_name = "group1"
    group_range = (1, 10)
    
    # 模擬群組統計
    group_stats = {
        'freq': {1: '0.20', 2: '0.90', 3: '0.20', 4: '0.40', 5: '0.40', 
                 6: '0.70', 7: '0.40', 8: '0.40', 9: '0.80', 10: '0.30'},
        'rsi': {1: '0.25', 2: '0.60', 3: '0.50', 4: '0.00', 5: '0.00', 
                6: '0.50', 7: '0.50', 8: '1.00', 9: '0.00', 10: '0.60'},
        'slope': {1: '0.17', 2: '0.55', 3: '0.21', 4: '0.19', 5: '0.30', 
                  6: '0.31', 7: '0.38', 8: '0.31', 9: '0.76', 10: '0.18'}
    }
    
    # 模擬模型評分
    model_scores = {
        'knn': {1: '0.00', 2: '0.50', 3: '0.00', 4: '0.00', 5: '0.00', 
                6: '0.00', 7: '0.50', 8: '0.00', 9: '0.50', 10: '0.00'},
        'svm': {1: '0.38', 2: '0.68', 3: '0.00', 4: '0.30', 5: '0.61', 
                6: '0.51', 7: '0.17', 8: '0.26', 9: '0.55', 10: '0.14'},
        'markov': {1: '0.00', 2: '0.42', 3: '0.28', 4: '0.14', 5: '0.07', 
                   6: '0.07', 7: '0.27', 8: '0.49', 9: '0.95', 10: '0.44'}
    }
    
    print(f"\n[INFO] 測試群組: {group_name} {group_range}")
    print(f"[INFO] 統計指標: {len(group_stats)} 個")
    print(f"[INFO] 模型評分: {len(model_scores)} 個")
    
    # 調用 LLM 顧問
    print("\n[INFO] 正在調用 LLM 顧問...")
    try:
        advice = advisor.get_group_advice(
            group_id=group_name,
            group_range=group_range,
            historical_stats=group_stats,
            model_scores=model_scores
        )
        
        if advice:
            print("\n[SUCCESS] LLM 顧問回應成功!")
            print("\n" + "=" * 60)
            print("LLM 建議:")
            print("=" * 60)
            print(f"建議號碼: {advice.get('numbers', [])}")
            print(f"信心度: {advice.get('confidence', 0):.2f}")
            print(f"理由: {advice.get('reason', '')}")
            print("=" * 60)
        else:
            print("\n[WARNING] LLM 顧問沒有返回建議")
            
    except Exception as e:
        print(f"\n[ERROR] LLM 顧問調用失敗: {e}")
        import traceback
        print("\n詳細錯誤:")
        print(traceback.format_exc())
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

if __name__ == "__main__":
    test_llm_advisor()
