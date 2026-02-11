import sys
import os
import pandas as pd
from src.crawler import fetch_data
from src.models import FeatureEngine
from src.strategy import StrategyEngine
from src.reporter import GeminiReporter
from src.logger import logger

def main():
    logger.section("539 AI 預測系統")
    
    # 1. Update Data
    logger.step(1, "更新歷史資料")
    df = fetch_data() # This saves to csv
    if df is None:
        logger.warning("無法獲取資料,將嘗試使用本地備份")
    
    # Check if we have data
    if not os.path.exists("data/539_history.csv"):
        logger.critical("錯誤: 無資料可用,請檢查網路連線或目標網站狀態")
        return

    # 2. Feedback Loop (Simulated Backtest on Last Draw)
    logger.step(2, "執行上一期回測與權重校正")
    # We need to peek at the second to last state to predict the last state
    try:
        # Load full data to find cutoff
        full_df = pd.read_csv("data/539_history.csv")
        if len(full_df) > 100:
            # Create a temporary cutoff file for the engine to load
            # verification_data = full_df[:-1] 
            # target = full_df.iloc[-1]
            
            # Since FeatureEngine loads from disk, we might need to trick it or pass df directly.
            # I modified FeatureEngine to load from disk by default, let's instantiate it with a patched load method 
            # or just overwrite the file temporarily? Overwriting is risky.
            # Better: FeatureEngine already reloads in __init__. 
            # Let's just instantiate FeatureEngine and manually slice the internal dataframe if possible.
            # But the logic inside calc methods calls get_binary_matrix which uses self.df. 
            # So we can modify self.df after init.
            
            eng_ver = FeatureEngine()
            real_last_draw = eng_ver.df.iloc[-1]
            real_last_nums = [int(n) for n in real_last_draw['numbers'].split(',')]
            
            # Slice dataframe to exclude last row (simulate we are in the past)
            eng_ver.df = eng_ver.df.iloc[:-1].reset_index(drop=True)
            eng_ver.numbers_series = eng_ver.numbers_series[:-1]
            
            print(f"回測目標期數: {real_last_draw['date']} (實際開獎: {real_last_nums})")
            
            # Calculate scores based on past data
            scores_ver = eng_ver.get_all_scores()
            
            # Run strategy
            strat = StrategyEngine()
            candidates_ver = strat.partition_strategy(strat.calculate_total_score(scores_ver))
            
            print(f"回測預測號碼: {candidates_ver}")
            
            # Calculate Accuracy
            hits = set(candidates_ver).intersection(set(real_last_nums))
            accuracy = len(hits) / 5.0
            print(f"回測命中數: {len(hits)} (命中率: {accuracy:.0%}) - {hits}")
            
            # Update Weights
            strat.update_weights(accuracy)
            
        else:
            print("歷史資料不足，跳過回測。")
            
    except Exception as e:
        print(f"回測過程發生錯誤 (不影響預測): {e}")

    # 3. Real Prediction
    logger.step(3, "執行本期預測")
    # Initialize fresh engines (will load full data)
    eng = FeatureEngine() 
    strat = StrategyEngine() # Will load updated config
    
    scores = eng.get_all_scores()
    final_scores = strat.calculate_total_score(scores)
    
    # Save scores for debugging
    final_scores.to_csv("data/latest_scores.csv")
    
    candidates = strat.partition_strategy(final_scores)
    
    # 計算預測目標日期
    from datetime import datetime, timedelta
    last_date = pd.to_datetime(eng.df.iloc[-1]['date'])
    next_date = last_date + timedelta(days=1)
    
    # 跳過週日
    while next_date.weekday() == 6:
        next_date += timedelta(days=1)
    
    # 格式化日期與星期
    weekday_names = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
    weekday = weekday_names[next_date.weekday()]
    prediction_date = f"{next_date.strftime('%Y-%m-%d')} {weekday}"
    
    logger.result("預測目標日期", prediction_date)
    logger.result("本期推薦號碼", candidates)
    
    # 4. Generate AI Report
    logger.step(4, "生成 AI 分析報告")
    reporter = GeminiReporter()
    report = reporter.generate_report(candidates, final_scores)
    
    print("-" * 50)
    print(report)
    print("-" * 50)
    
    # Save report
    with open("data/latest_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    logger.success("報告已存檔至 data/latest_report.txt")
    logger.info(f"\n日誌檔案: {logger.log_file}")

if __name__ == "__main__":
    main()
