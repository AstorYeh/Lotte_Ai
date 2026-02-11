"""
執行完整 2025 年訓練
從第 30 期開始,訓練到第 313 期 (2025-12-31)
"""
import sys
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger
import pandas as pd

def main():
    logger.section("開始完整 2025 年訓練")
    logger.info("訓練範圍: 第 31 期 → 第 313 期 (共 283 期)")
    logger.info("預估時間: 30-60 分鐘")
    
    # 建立訓練器 (不使用 LLM 以加快速度)
    trainer = IncrementalTrainer(initial_periods=30, use_llm=False)
    
    # 執行完整訓練
    trainer.train_all(data_file="data/539_history.csv")
    
    logger.success("2025 年訓練完成!")
    logger.info(f"訓練日誌: {trainer.iteration_logger.session_dir}")
    
    # 顯示統計
    stats = trainer.iteration_logger.summary.get('statistics', {})
    logger.section("訓練統計")
    logger.result("總期數", stats.get('total_periods', 0))
    logger.result("平均命中率", f"{stats.get('average_accuracy', 0):.2%}")
    logger.result("最佳命中率", f"{stats.get('best_accuracy', 0):.2%}")
    logger.result("最差命中率", f"{stats.get('worst_accuracy', 0):.2%}")
    logger.result("總命中數", stats.get('total_hits', 0))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n訓練被使用者中斷")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"訓練過程發生錯誤: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        sys.exit(1)
