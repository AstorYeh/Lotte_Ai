"""
使用增強模型 (9 個模型) 重新訓練
比較 7 模型 vs 9 模型的命中率差異
"""
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger
import pandas as pd

def main():
    logger.section("使用增強模型重新訓練")
    logger.info("模型配置: 7 個基礎模型 + XGBoost + Random Forest")
    logger.info("訓練範圍: 第 51 期 → 第 335 期")
    logger.info("初始訓練: 前 50 期 (優化後)")
    logger.info("預估時間: 15-20 分鐘")
    
    # 建立訓練器 (不使用 LLM,使用增強模型,增加初始期數)
    trainer = IncrementalTrainer(
        initial_periods=50,  # 從 30 增加到 50
        use_llm=False,
        use_enhanced=True
    )
    
    # 執行完整訓練
    logger.info("\n開始訓練...")
    trainer.train_all(data_file="data/539_history.csv")
    
    logger.success("訓練完成!")
    logger.info(f"訓練日誌: {trainer.iteration_logger.session_dir}")
    
    # 顯示統計
    stats = trainer.iteration_logger.summary.get('statistics', {})
    logger.section("訓練統計")
    logger.result("總期數", stats.get('total_periods', 0))
    logger.result("平均命中率", f"{stats.get('average_accuracy', 0):.2%}")
    logger.result("最佳命中率", f"{stats.get('best_accuracy', 0):.2%}")
    logger.result("最差命中率", f"{stats.get('worst_accuracy', 0):.2%}")
    logger.result("總命中數", stats.get('total_hits', 0))
    
    # 與之前的結果比較
    logger.section("與 7 模型比較")
    logger.info("7 模型平均命中率: 16.07%")
    logger.info(f"9 模型平均命中率: {stats.get('average_accuracy', 0):.2%}")
    
    improvement = (stats.get('average_accuracy', 0) - 0.1607) / 0.1607 * 100
    if improvement > 0:
        logger.success(f"提升: +{improvement:.1f}%")
    else:
        logger.warning(f"下降: {improvement:.1f}%")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n訓練被使用者中斷")
    except Exception as e:
        logger.critical(f"訓練過程發生錯誤: {e}")
        import traceback
        logger.debug(traceback.format_exc())
