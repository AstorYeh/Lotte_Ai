"""
測試增強模型 - 只訓練 10 期
快速驗證模型整合是否正確
"""
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger
import pandas as pd

def main():
    logger.section("測試增強模型 (10 期)")
    logger.info("模型: 7 基礎 + XGBoost + Random Forest")
    
    # 建立訓練器 (啟用增強模型)
    trainer = IncrementalTrainer(
        initial_periods=30, 
        use_llm=False,
        use_enhanced=True  # 啟用增強模型
    )
    
    # 載入資料
    df = pd.read_csv("data/539_history.csv")
    logger.info(f"載入資料: {len(df)} 筆")
    
    # 只訓練 10 期作為測試
    logger.info("測試模式: 訓練第 31-40 期")
    test_end = min(40, len(df))
    
    for period_index in range(30, test_end):
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
    
    logger.success("測試完成!")
    logger.info(f"日誌位置: {trainer.iteration_logger.session_dir}")

if __name__ == "__main__":
    main()
