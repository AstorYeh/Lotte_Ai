"""
迭代日誌記錄器
記錄每一期的學習過程,包含群組分析、預測結果、驗證與權重調整
"""
import json
from datetime import datetime
from pathlib import Path
from src.logger import logger
from src.timezone_utils import get_taiwan_timestamp_str, get_taiwan_isoformat

class IterationLogger:
    """迭代學習日誌記錄器"""
    
    def __init__(self):
        self.log_dir = Path("logs/iterations")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = get_taiwan_timestamp_str()
        self.session_dir = self.log_dir / self.current_session
        self.session_dir.mkdir(exist_ok=True)
        
        # 建立總結檔案
        self.summary_file = self.session_dir / "training_summary.json"
        self.summary = {
            "session_id": self.current_session,
            "start_time": get_taiwan_isoformat(),
            "total_periods": 0,
            "iterations": []
        }
        
        logger.info(f"迭代日誌記錄器已啟動: {self.session_dir}")
    
    def log_period_start(self, period_index, train_size, target_date):
        """記錄期數開始"""
        self.current_period = {
            "period_index": period_index,
            "train_size": train_size,
            "target_date": target_date,
            "timestamp": get_taiwan_isoformat(),
            "groups": {},
            "cross_selection": {},
            "verification": {},
            "weight_adjustment": {}
        }
        
        logger.section(f"第 {period_index} 期學習")
        logger.info(f"訓練資料: 第 1-{train_size} 期")
        logger.info(f"預測目標: 第 {period_index} 期 ({target_date})")
    
    def log_group_analysis(self, group_id, group_range, model_scores, selected_numbers, llm_advice=None):
        """記錄群組分析過程"""
        group_log = {
            "group_id": group_id,
            "range": group_range,
            "model_scores": model_scores,
            "selected_numbers": selected_numbers,
            "llm_advice": llm_advice
        }
        
        self.current_period["groups"][group_id] = group_log
        
        logger.info(f"\n[{group_id} 分析] ({group_range[0]}-{group_range[1]})")
        logger.info(f"  模型評分: {self._format_scores(model_scores)}")
        if llm_advice:
            logger.info(f"  LLM 建議: {llm_advice}")
        logger.result(f"選出號碼", selected_numbers if selected_numbers else "無")
    
    def log_cross_selection(self, candidates, final_selection, selection_scores):
        """記錄跨群篩選過程"""
        cross_log = {
            "candidates": candidates,
            "final_selection": final_selection,
            "selection_scores": selection_scores
        }
        
        self.current_period["cross_selection"] = cross_log
        
        logger.info(f"\n[跨群篩選]")
        logger.info(f"  候選號碼: {candidates}")
        logger.result("最終選出", final_selection)
    
    def log_verification(self, predicted, actual, hits, accuracy, group_hits):
        """記錄驗證結果"""
        verification_log = {
            "predicted": predicted,
            "actual": actual,
            "hits": hits,
            "accuracy": accuracy,
            "group_hits": group_hits
        }
        
        self.current_period["verification"] = verification_log
        
        logger.info(f"\n[驗證結果]")
        logger.info(f"  實際開獎: {actual}")
        logger.info(f"  命中號碼: {hits}")
        logger.result("命中率", f"{len(hits)}/5 = {accuracy:.0%}")
        
        logger.info(f"\n  各群命中率:")
        for group_id, hit_info in group_hits.items():
            symbol = "✓" if hit_info['rate'] > 0 else ""
            logger.info(f"    - {group_id}: {hit_info['hits']}/{hit_info['total']} = {hit_info['rate']:.0%} {symbol}")
    
    def log_weight_adjustment(self, decisions, backtest_result=None):
        """記錄權重調整決策"""
        adjustment_log = {
            "decisions": decisions,
            "backtest_result": backtest_result,
            "timestamp": get_taiwan_isoformat()
        }
        
        self.current_period["weight_adjustment"] = adjustment_log
        
        logger.info(f"\n[權重調整決策]")
        for group_id, decision in decisions.items():
            action = decision.get('action', 'maintain')
            reason = decision.get('reason', '')
            
            if action == 'adjust':
                adjustment = decision.get('adjustment', 0)
                logger.info(f"  {group_id}: {action} {adjustment:+.0%} - {reason}")
            else:
                logger.info(f"  {group_id}: {action} - {reason}")
        
        if backtest_result:
            logger.info(f"\n  歷史驗證: {backtest_result['message']}")
            if backtest_result['is_valid']:
                logger.success("執行調整")
            else:
                logger.warning("不執行調整")
    
    def save_period(self):
        """儲存當期記錄"""
        period_index = self.current_period['period_index']
        period_file = self.session_dir / f"period_{period_index:03d}.json"
        
        with open(period_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_period, f, indent=2, ensure_ascii=False)
        
        # 更新總結
        self.summary['iterations'].append({
            "period": period_index,
            "accuracy": self.current_period['verification'].get('accuracy', 0),
            "hits": len(self.current_period['verification'].get('hits', [])),
            "file": str(period_file.name)
        })
        self.summary['total_periods'] += 1
        
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, indent=2, ensure_ascii=False)
        
        logger.success(f"第 {period_index} 期記錄已儲存")
    
    def finalize(self):
        """完成訓練,生成最終報告"""
        self.summary['end_time'] = get_taiwan_isoformat()
        
        # 計算統計
        accuracies = [it['accuracy'] for it in self.summary['iterations']]
        total_hits = sum(it['hits'] for it in self.summary['iterations'])
        
        self.summary['statistics'] = {
            "total_periods": len(accuracies),
            "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
            "total_hits": total_hits,
            "best_accuracy": max(accuracies) if accuracies else 0,
            "worst_accuracy": min(accuracies) if accuracies else 0
        }
        
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.summary, f, indent=2, ensure_ascii=False)
        
        logger.section("訓練完成")
        logger.result("總期數", self.summary['statistics']['total_periods'])
        logger.result("平均命中率", f"{self.summary['statistics']['average_accuracy']:.2%}")
        logger.result("總命中數", self.summary['statistics']['total_hits'])
        logger.success(f"訓練報告已儲存: {self.summary_file}")
    
    def _format_scores(self, scores):
        """格式化評分顯示"""
        if isinstance(scores, dict):
            return {k: {num: f"{score:.2f}" for num, score in v.items()} 
                    for k, v in scores.items()}
        return scores

if __name__ == "__main__":
    # 測試
    logger_test = IterationLogger()
    
    # 模擬第 31 期
    logger_test.log_period_start(31, 30, "2025-01-31")
    
    # 群組分析
    logger_test.log_group_analysis(
        "群組1", (1, 10),
        {"freq": {5: 0.85, 8: 0.72}, "rsi": {5: 0.90, 8: 0.75}},
        [5, 8],
        llm_advice="建議選 5, 8 (信心度: 0.78)"
    )
    
    # 跨群篩選
    logger_test.log_cross_selection(
        [5, 8, 15, 20, 25, 32, 38],
        [5, 8, 15, 20, 25, 32, 38],
        {5: 0.88, 8: 0.75}
    )
    
    # 驗證
    logger_test.log_verification(
        [5, 8, 15, 20, 25, 32, 38],
        [5, 12, 20, 28, 35],
        [5, 20],
        0.4,
        {"群組1": {"hits": 1, "total": 2, "rate": 0.5}}
    )
    
    # 權重調整
    logger_test.log_weight_adjustment({
        "群組1": {"action": "adjust", "adjustment": 0.05, "reason": "表現良好"}
    })
    
    logger_test.save_period()
    logger_test.finalize()
