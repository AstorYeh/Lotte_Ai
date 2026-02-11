"""
四群分區策略引擎
將 1-39 號碼分為四群,各自獨立分析後再跨群篩選
"""
import numpy as np
import pandas as pd
from src.models import FeatureEngine
from src.logger import logger

class GroupBasedStrategy:
    """四群分區策略引擎"""
    
    # 定義四個群組
    GROUPS = {
        'group1': (1, 10),
        'group2': (11, 20),
        'group3': (21, 30),
        'group4': (31, 39)
    }
    
    def __init__(self):
        # 初始化各群組的模型權重 (優化後)
        self.group_weights = {
            'group1': {
                'freq': 1.2, 'rsi': 0.8, 'slope': 1.0, 'knn': 0.9,
                'svm': 1.1, 'markov': 1.3, 'pca': 0.7,
                'xgboost': 1.5, 'random_forest': 1.4, 'llm': 0.5
            },
            'group2': {
                'freq': 1.2, 'rsi': 0.8, 'slope': 1.0, 'knn': 0.9,
                'svm': 1.1, 'markov': 1.3, 'pca': 0.7,
                'xgboost': 1.5, 'random_forest': 1.4, 'llm': 0.5
            },
            'group3': {
                'freq': 1.2, 'rsi': 0.8, 'slope': 1.0, 'knn': 0.9,
                'svm': 1.1, 'markov': 1.3, 'pca': 0.7,
                'xgboost': 1.5, 'random_forest': 1.4, 'llm': 0.5
            },
            'group4': {
                'freq': 1.2, 'rsi': 0.8, 'slope': 1.0, 'knn': 0.9,
                'svm': 1.1, 'markov': 1.3, 'pca': 0.7,
                'xgboost': 1.5, 'random_forest': 1.4, 'llm': 0.5
            }
        }
        
        logger.info("四群分區策略引擎已初始化")
        logger.info(f"群組定義: {self.GROUPS}")
    
    def analyze_group(self, feature_engine, group_id, llm_advice=None, use_enhanced=False):
        """
        分析單一群組,選出 0-3 顆號碼
        
        Args:
            feature_engine: 特徵引擎 (已計算好所有模型評分)
            group_id: 群組 ID (group1-4)
            llm_advice: LLM 建議 (可選)
            use_enhanced: 是否使用增強模型
        
        Returns:
            dict: {
                'selected_numbers': [5, 8],
                'scores': {5: 0.88, 8: 0.75, ...},
                'model_scores': {'freq': {...}, 'rsi': {...}, ...}
            }
        """
        group_range = self.GROUPS[group_id]
        group_numbers = list(range(group_range[0], group_range[1] + 1))
        
        # 取得該群組的所有模型評分
        all_scores = feature_engine.get_all_scores(use_enhanced=use_enhanced)
        
        # 篩選出該群組的號碼
        group_scores = all_scores.loc[all_scores.index.isin(group_numbers)]
        
        # 計算各模型的加權評分
        model_scores = {}
        model_names = ['freq', 'rsi', 'slope', 'knn', 'svm', 'markov', 'pca']
        
        # 如果使用增強模型,加入新模型
        if use_enhanced and 'xgboost' in all_scores.columns:
            model_names.extend(['xgboost', 'random_forest'])
        
        for model_name in model_names:
            if model_name in group_scores.columns:
                model_scores[model_name] = group_scores[model_name].to_dict()
        
        # 計算綜合評分
        weighted_scores = self._calculate_weighted_scores(
            group_scores, 
            self.group_weights[group_id],
            llm_advice,
            model_names
        )
        
        # 選出 0-3 顆號碼 (動態選擇)
        selected_numbers = self._select_top_numbers(weighted_scores, max_count=3)
        
        return {
            'selected_numbers': selected_numbers,
            'scores': weighted_scores,
            'model_scores': model_scores
        }
    
    def _calculate_weighted_scores(self, scores_df, weights, llm_advice=None, model_names=None):
        """計算加權綜合評分"""
        if model_names is None:
            model_names = ['freq', 'rsi', 'slope', 'knn', 'svm', 'markov', 'pca']
        
        weighted = pd.Series(0.0, index=scores_df.index)
        total_weight = 0
        
        # 模型加權
        for model_name in model_names:
            if model_name == 'llm':
                continue  # LLM 單獨處理
            
            weight = weights.get(model_name, 1.0)  # 如果權重不存在,使用預設值 1.0
            
            if model_name in scores_df.columns:
                weighted += scores_df[model_name] * weight
                total_weight += weight
        
        # 正規化
        if total_weight > 0:
            weighted = weighted / total_weight
        
        # 加入 LLM 建議 (如果有)
        if llm_advice and 'numbers' in llm_advice:
            llm_weight = weights.get('llm', 0.5)
            llm_confidence = llm_advice.get('confidence', 0.5)
            
            for num in llm_advice['numbers']:
                if num in weighted.index:
                    # LLM 建議的號碼加分
                    weighted[num] += llm_weight * llm_confidence
        
        return weighted.to_dict()
    
    def _select_top_numbers(self, scores, max_count=2, threshold=0.0, min_count=2):  # 🔥 強制 Top-2 (基礎模型優化)
        """
        強制 Top-N 選號策略 - 確保每群都選出固定數量的號碼
        
        策略改變 (方案 B):
        1. 移除閾值限制 (threshold=0.0)
        2. 強制選出 Top-N 最高分號碼 (min_count=max_count=2)
        3. 不再依賴評分高低,只選擇相對最高分的號碼
        
        原理:
        - 即使所有評分都很低,也要選出評分最高的 2 顆
        - 確保每群都有貢獻,避免選號不足
        - 「集中火力」體現在只選 Top 2,而非閾值篩選
        
        Args:
            scores: 評分字典 {num: score}
            max_count: 最多選幾顆 (固定 2)
            threshold: 最低分數閾值 (設為 0.0,不使用)
            min_count: 最少選幾顆 (固定 2,與 max_count 相同)
        
        Returns:
            list: 選出的號碼 (固定 2 顆)
        """
        # 排序 (評分由高到低)
        sorted_numbers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_numbers:
            return []
        
        # 🔥 強制選出 Top-N,不使用閾值
        # 直接選擇評分最高的 max_count 顆號碼
        selected = [num for num, score in sorted_numbers[:max_count]]
        
        return sorted(selected)
    
    def cross_group_selection(self, group_results, target_count=(6, 7)):
        """
        跨群篩選 - 恢復原始配置 (階段 2)
        
        策略:
        1. 恢復 6-7 顆選號 (容錯率優勢)
        2. 恢復群組平衡機制 (風險分散)
        3. 結合修復後的增強模型 (0.15/0.85)
        
        目標:
        - 結合原始配置優勢 + 修復後的增強模型
        - 2+ 顆命中率目標: 21-22%
        - 可能超越原始基準線 20.65%
        
        Args:
            group_results: 各群分析結果
            target_count: 目標數量範圍 (min, max) - 恢復為 (6, 7)
        
        Returns:
            dict: {
                'final_selection': [5, 8, 15, ...],  # 6-7 顆
                'selection_scores': {5: 0.88, ...}
            }
        """
        # 收集所有候選號碼與評分
        all_candidates = {}
        
        for group_id, result in group_results.items():
            for num in result['selected_numbers']:
                all_candidates[num] = result['scores'][num]
        
        # 按評分排序
        sorted_candidates = sorted(
            all_candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 恢復群組平衡機制
        # 確保每個群組至少有 1 顆,最多 2 顆
        final_selection = []
        group_counts = {
            'group1': 0,
            'group2': 0,
            'group3': 0,
            'group4': 0
        }
        
        # 定義群組範圍
        def get_group(num):
            if 1 <= num <= 10:
                return 'group1'
            elif 11 <= num <= 20:
                return 'group2'
            elif 21 <= num <= 30:
                return 'group3'
            else:
                return 'group4'
        
        # 第一輪: 按評分選號,但確保群組平衡
        for num, score in sorted_candidates:
            group = get_group(num)
            
            # 檢查群組是否已滿 (每群最多 2 顆)
            if group_counts[group] < 2:
                final_selection.append(num)
                group_counts[group] += 1
                
                # 達到目標數量就停止
                if len(final_selection) >= target_count[1]:
                    break
        
        # 第二輪: 如果不足 min_count,補充高分號碼
        min_count, max_count = target_count
        if len(final_selection) < min_count:
            for num, score in sorted_candidates:
                if num not in final_selection:
                    final_selection.append(num)
                    if len(final_selection) >= min_count:
                        break
        
        return {
            'final_selection': sorted(final_selection),
            'selection_scores': {num: all_candidates.get(num, 0) for num in final_selection}
        }
    
    def update_group_weights(self, group_id, adjustment):
        """
        更新群組權重
        
        Args:
            group_id: 群組 ID
            adjustment: 調整幅度 (例如 0.05 表示 +5%)
        """
        if group_id not in self.group_weights:
            logger.warning(f"群組 {group_id} 不存在")
            return
        
        # 對所有模型權重進行調整
        for model_name in self.group_weights[group_id]:
            self.group_weights[group_id][model_name] *= (1 + adjustment)
        
        logger.info(f"{group_id} 權重已調整 {adjustment:+.0%}")

if __name__ == "__main__":
    # 測試
    from src.models import FeatureEngine
    
    logger.section("測試四群分區策略")
    
    # 建立特徵引擎
    eng = FeatureEngine()
    scores = eng.get_all_scores()
    
    # 建立策略引擎
    strategy = GroupBasedStrategy()
    
    # 測試各群分析
    group_results = {}
    for group_id in strategy.GROUPS.keys():
        result = strategy.analyze_group(eng, group_id)
        group_results[group_id] = result
        
        logger.info(f"\n{group_id} 結果:")
        logger.info(f"  選出號碼: {result['selected_numbers']}")
    
    # 測試跨群篩選
    final_result = strategy.cross_group_selection(group_results)
    logger.info(f"\n最終選出: {final_result['final_selection']}")
