"""
漸進式訓練器
從第 30 期開始,逐期預測、驗證、學習,直到第 313 期
整合四群策略、LLM 顧問、權重優化器與迭代日誌
"""
import pandas as pd
import numpy as np
from pathlib import Path
from src.models import FeatureEngine
from src.group_strategy import GroupBasedStrategy
from src.llm_advisor import LLMAdvisor
from src.weight_optimizer import WeightOptimizer
from src.iteration_logger import IterationLogger
from src.logger import logger

class IncrementalTrainer:
    """漸進式訓練器 - 實現 30→313 期的學習流程"""
    
    def __init__(self, initial_periods=30, use_llm=True, use_enhanced=False):
        """
        初始化
        
        Args:
            initial_periods: 初始訓練期數
            use_llm: 是否使用 LLM 顧問
            use_enhanced: 是否使用增強模型 (XGBoost, Random Forest)
        """
        self.initial_periods = initial_periods
        self.use_llm = use_llm
        self.use_enhanced_models = use_enhanced
        
        # 初始化各模組
        self.strategy = GroupBasedStrategy()
        # 🔥 強化修補 4: 縮短觀察窗口 (5→3) 並提升學習率 (0.3→0.4),提高反應速度
        self.optimizer = WeightOptimizer(learning_rate=0.4, observation_window=3)
        self.iteration_logger = IterationLogger()
        
        if use_llm:
            self.llm_advisor = LLMAdvisor()
        else:
            self.llm_advisor = None
        
        # 記錄各群組的歷史表現
        self.group_history = {
            'group1': [],
            'group2': [],
            'group3': [],
            'group4': []
        }
        
        logger.section("漸進式訓練器已初始化")
        logger.info(f"初始訓練期數: {initial_periods}")
        logger.info(f"LLM 顧問: {'啟用' if use_llm else '停用'}")
        logger.info(f"增強模型: {'啟用 (XGBoost + Random Forest)' if use_enhanced else '停用'}")
    
    def train_all(self, data_file="data/539_train.csv"):
        """
        執行完整訓練流程
        
        Args:
            data_file: 訓練資料檔案
        """
        # 載入完整資料
        df = pd.read_csv(data_file)
        logger.info(f"載入訓練資料: {len(df)} 期")
        
        # 從第 initial_periods+1 期開始訓練
        total_periods = len(df)
        
        logger.section(f"開始漸進式訓練 (第 {self.initial_periods+1} 期 → 第 {total_periods} 期)")
        
        for period_index in range(self.initial_periods, total_periods):
            self.train_period(df, period_index)
        
        # 完成訓練
        self.iteration_logger.finalize()
        logger.success(f"訓練完成! 共訓練 {total_periods - self.initial_periods} 期")
    
    def train_period(self, df, period_index):
        """
        訓練單一期
        
        Args:
            df: 完整資料
            period_index: 當前期數索引
        """
        # 1. 準備訓練資料 (不包含當期)
        train_df = df.iloc[:period_index].copy()
        target_row = df.iloc[period_index]
        
        # 記錄開始
        self.iteration_logger.log_period_start(
            period_index + 1,
            len(train_df),
            target_row['date']
        )
        
        # 2. 建立特徵引擎 (直接傳入 DataFrame)
        feature_engine = FeatureEngine(data_df=train_df)
        all_scores = feature_engine.get_all_scores(use_enhanced=self.use_enhanced_models)
        
        # 3. 各群組分析
        group_results = {}
        
        for group_id in self.strategy.GROUPS.keys():
            # LLM 建議 (如果啟用)
            llm_advice = None
            if self.llm_advisor and self.llm_advisor.model:
                # 準備 LLM 所需資料
                group_range = self.strategy.GROUPS[group_id]
                historical_stats = self._get_group_stats(train_df, group_range)
                model_scores = self._get_group_model_scores(all_scores, group_range)
                
                llm_advice = self.llm_advisor.get_group_advice(
                    group_id,
                    group_range,
                    historical_stats,
                    model_scores
                )
            
            # 群組分析
            result = self.strategy.analyze_group(
                feature_engine, 
                group_id, 
                llm_advice,
                use_enhanced=self.use_enhanced_models
            )
            group_results[group_id] = result
            
            # 記錄
            self.iteration_logger.log_group_analysis(
                group_id,
                self.strategy.GROUPS[group_id],
                result['model_scores'],
                result['selected_numbers'],
                llm_advice
            )
        
        # 4. 跨群篩選
        final_result = self.strategy.cross_group_selection(group_results)
        predicted_numbers = final_result['final_selection']
        
        self.iteration_logger.log_cross_selection(
            list(set([num for r in group_results.values() for num in r['selected_numbers']])),
            predicted_numbers,
            final_result['selection_scores']
        )
        
        # 5. 驗證結果
        actual_numbers = [int(n) for n in target_row['numbers'].split(',')]
        hits = list(set(predicted_numbers).intersection(set(actual_numbers)))
        accuracy = len(hits) / 5.0
        
        # 計算各群命中率
        group_hits = {}
        for group_id, result in group_results.items():
            group_predicted = result['selected_numbers']
            if group_predicted:
                group_hits_nums = list(set(group_predicted).intersection(set(actual_numbers)))
                group_hits[group_id] = {
                    'hits': len(group_hits_nums),
                    'total': len(group_predicted),
                    'rate': len(group_hits_nums) / len(group_predicted) if group_predicted else 0
                }
            else:
                group_hits[group_id] = {'hits': 0, 'total': 0, 'rate': 0}
        
        self.iteration_logger.log_verification(
            predicted_numbers,
            actual_numbers,
            hits,
            accuracy,
            group_hits
        )
        
        # 6. 權重調整
        weight_decisions = {}
        
        for group_id in self.strategy.GROUPS.keys():
            group_accuracy = group_hits[group_id]['rate']
            
            # 更新群組歷史
            self.group_history[group_id].append({
                'period': period_index + 1,
                'accuracy': group_accuracy,
                'hits': group_hits[group_id]['hits'],
                'total': group_hits[group_id]['total']
            })
            
            # 優化權重
            decision = self.optimizer.optimize_group_weights(
                group_id,
                group_accuracy,
                self.group_history[group_id],
                self.strategy.group_weights[group_id]
            )
            
            weight_decisions[group_id] = decision
            
            # 應用調整
            if decision['action'] == 'adjust':
                self.strategy.update_group_weights(group_id, decision['adjustment'])
        
        # 記錄權重調整
        backtest_info = weight_decisions.get('group1', {}).get('backtest')
        self.iteration_logger.log_weight_adjustment(weight_decisions, backtest_info)
        
        # 7. 儲存當期記錄
        self.iteration_logger.save_period()
    
    def _get_group_stats(self, df, group_range):
        """取得群組的歷史統計"""
        # 簡化版統計
        return {
            "total_periods": len(df),
            "group_range": f"{group_range[0]}-{group_range[1]}"
        }
    
    def _get_group_model_scores(self, all_scores, group_range):
        """取得群組的模型評分"""
        group_numbers = list(range(group_range[0], group_range[1] + 1))
        group_scores = all_scores.loc[all_scores.index.isin(group_numbers)]
        
        model_scores = {}
        for col in group_scores.columns:
            model_scores[col] = group_scores[col].to_dict()
        
        return model_scores

if __name__ == "__main__":
    # 測試 - 只跑前 5 期
    logger.section("測試漸進式訓練器")
    
    trainer = IncrementalTrainer(initial_periods=30, use_llm=False)
    
    # 載入完整歷史資料 (用於測試)
    df = pd.read_csv("data/539_history.csv")
    logger.info(f"載入資料: {len(df)} 筆")
    
    # 只訓練 5 期作為測試 (第 31-35 期)
    logger.info("測試模式: 訓練第 31-35 期")
    test_end = min(35, len(df))
    
    for period_index in range(30, test_end):
        logger.info(f"\n{'='*60}")
        logger.info(f"開始訓練第 {period_index + 1} 期")
        logger.info(f"{'='*60}")
        trainer.train_period(df, period_index)
    
    trainer.iteration_logger.finalize()
    logger.success("測試完成!")
