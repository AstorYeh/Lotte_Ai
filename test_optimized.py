"""
測試優化後的增強模型 - 10 期測試
驗證增加初始訓練期數的效果
"""
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger
import pandas as pd

def main():
    logger.section("測試優化後的增強模型 (10 期)")
    logger.info("優化項目: 初始訓練期數 30 → 50")
    logger.info("模型: 7 基礎 + XGBoost + Random Forest")
    
    # 建立訓練器 (使用優化參數)
    trainer = IncrementalTrainer(
        initial_periods=50,  # 優化: 增加到 50
        use_llm=False,
        use_enhanced=True
    )
    
    # 載入資料
    df = pd.read_csv("data/539_history.csv")
    logger.info(f"載入資料: {len(df)} 筆")
    
    # 只訓練 10 期作為測試 (第 51-60 期)
    logger.info("測試模式: 訓練第 51-60 期")
    test_end = min(60, len(df))
    
    for period_index in range(50, test_end):
        logger.info(f"\n{'='*60}")
        logger.info(f"訓練第 {period_index + 1} 期")
        logger.info(f"{'='*60}")
        trainer.train_period(df, period_index)
    
    trainer.iteration_logger.finalize()
    
    # 顯示結果
    stats = trainer.iteration_logger.summary.get('statistics', {})
    logger.section("測試結果")
    logger.result("測試期數", stats.get('total_periods', 0))
    logger.result("平均命中率", f"{stats.get('average_accuracy', 0):.2%}")
    logger.result("總命中數", stats.get('total_hits', 0))
    
    # 與之前比較
    logger.section("與優化前比較")
    logger.info("優化前 (30 期初始): 10 期測試平均 20%")
    logger.info(f"優化後 (50 期初始): {stats.get('average_accuracy', 0):.2%}")
    
    improvement = (stats.get('average_accuracy', 0) - 0.20) / 0.20 * 100
    if improvement > 0:
        logger.success(f"提升: +{improvement:.1f}%")
    else:
        logger.warning(f"變化: {improvement:.1f}%")
    
    logger.success("測試完成!")
    logger.info(f"日誌位置: {trainer.iteration_logger.session_dir}")

if __name__ == "__main__":
    main()
