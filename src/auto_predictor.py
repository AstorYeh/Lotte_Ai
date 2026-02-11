# -*- coding: utf-8 -*-
"""
自動預測與驗證模組
整合預測引擎,實現自動化預測與驗證流程
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from src.models import FeatureEngine
from src.strategy import StrategyEngine
from src.reporter import GeminiReporter
from src.prediction_history import PredictionHistory
from src.auzonet_crawler import fetch_auzonet_single_date
from src.structured_logger import structured_logger
from src.discord_notifier import DiscordNotifier


class AutoPredictor:
    """自動預測協調器"""
    
    def __init__(self):
        """初始化"""
        self.prediction_history = PredictionHistory()
        self.discord = DiscordNotifier()
    
    def verify_pending_prediction(self) -> Optional[Dict]:
        """驗證待驗證的預測"""
        print("=" * 60)
        print("Auto Verification Starting...")
        print("=" * 60)
        
        # 檢查是否有待驗證的預測
        pending = self.prediction_history.get_pending_prediction()
        
        if not pending:
            print("[INFO] No pending prediction to verify")
            return None
        
        prediction_date = pending.get('prediction_date', '')
        predicted_numbers = pending.get('predicted_numbers', [])
        
        print(f"\n[INFO] Found pending prediction: {prediction_date}")
        print(f"[INFO] Predicted numbers: {predicted_numbers}")
        
        try:
            # 解析日期
            date_part = prediction_date.split()[0] if ' ' in prediction_date else prediction_date
            
            # 抓取實際開獎號碼
            print(f"\n[Step 1] Fetching actual results for {date_part}...")
            actual_numbers = fetch_auzonet_single_date(date_part)
            
            if not actual_numbers or len(actual_numbers) != 5:
                print(f"[WARNING] No results available for {date_part} yet")
                return None
            
            print(f"[SUCCESS] Actual numbers: {actual_numbers}")
            
            # 計算命中 (支援多組號碼)
            print(f"\n[Step 2] Calculating accuracy...")
            best_accuracy = 0.0
            best_hits = []
            best_set = []
            
            # 統一轉為列表 List[List[int]]
            prediction_sets = []
            if len(predicted_numbers) > 0 and isinstance(predicted_numbers[0], list):
                prediction_sets = predicted_numbers
            else:
                prediction_sets = [predicted_numbers]
                
            actual_set = set(actual_numbers)
            
            for i, p_set in enumerate(prediction_sets, 1):
                p_set_clean = [int(x) for x in p_set]
                hits = list(set(p_set_clean) & actual_set)
                acc = len(hits) / 5.0
                print(f"  Set {i}: {p_set_clean} -> Hits: {len(hits)} ({acc:.0%})")
                
                if acc > best_accuracy or (acc == best_accuracy and len(hits) > len(best_hits)):
                    best_accuracy = acc
                    best_hits = hits
                    best_set = p_set_clean
            
            if not best_set and prediction_sets:
                 best_set = [int(x) for x in prediction_sets[0]]

            print(f"  Best Result: {len(best_hits)}/5 ({best_accuracy:.0%})")
            
            # 更新預測記錄
            print(f"\n[Step 3] Updating prediction history...")
            self.prediction_history.update_actual_result(
                prediction_date=prediction_date,
                actual_numbers=actual_numbers
            )
            
            # 更新訓練集
            print(f"\n[Step 4] Updating training data...")
            self._update_training_data(date_part, actual_numbers)
            
            # 記錄日誌
            structured_logger.log_operation(
                operation_type='auto_verification',
                status='success',
                details={
                    'prediction_date': prediction_date,
                    'best_hits': len(best_hits),
                    'best_accuracy': best_accuracy,
                    'num_sets': len(prediction_sets)
                }
            )
            
            # Discord 通知 (使用最佳結果)
            print(f"\n[Step 5] Sending Discord notification...")
            self.discord.send_verification_result(
                prediction_date=prediction_date,
                predicted_numbers=best_set, # 顯示最佳那一組
                actual_numbers=actual_numbers,
                hits=best_hits,
                accuracy=best_accuracy
            )
            
            result = {
                'prediction_date': prediction_date,
                'predicted_numbers': predicted_numbers,
                'actual_numbers': actual_numbers,
                'hits': best_hits,
                'accuracy': best_accuracy
            }
            
            print("\n" + "=" * 60)
            print(f"Verification completed! Best Accuracy: {best_accuracy:.0%}")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
            import traceback
            traceback.print_exc()
            structured_logger.log_execution_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={'operation': 'auto_verification', 'prediction_date': prediction_date}
            )
            return None
    
    def _update_training_data(self, date: str, numbers: List[int]):
        """更新訓練集"""
        try:
            train_file = Path('data/539_train.csv')
            
            if not train_file.exists():
                print("[WARNING] Training file not found")
                return
            
            df_train = pd.read_csv(train_file)
            
            # 檢查是否已存在
            if date in df_train['date'].values:
                print(f"[INFO] Date {date} already in training data")
                return
            
            # 新增記錄
            new_row = {
                'date': date,
                'numbers': ','.join([str(n) for n in sorted(numbers)])
            }
            
            df_train = pd.concat([df_train, pd.DataFrame([new_row])], ignore_index=True)
            
            # 排序
            df_train['date'] = pd.to_datetime(df_train['date'])
            df_train = df_train.sort_values('date').reset_index(drop=True)
            df_train['date'] = df_train['date'].dt.strftime('%Y-%m-%d')
            
            # 儲存
            df_train.to_csv(train_file, index=False)
            
            # 同步到 history (如果存在)
            history_file = Path('data/539_history.csv')
            if history_file.exists():
                df_train.to_csv(history_file, index=False)
            
            print(f"[SUCCESS] Training data updated: {len(df_train)} records")
            
        except Exception as e:
            print(f"[ERROR] Failed to update training data: {e}")
    
    def generate_new_prediction(self) -> Optional[Dict]:
        """生成新預測 (5 組號碼)"""
        print("=" * 60)
        print("Auto Prediction Starting (5 Sets)...")
        print("=" * 60)
        
        # 檢查是否有待驗證的預測
        if self.prediction_history.has_pending_prediction():
            print("[WARNING] There is a pending prediction, skipping new prediction")
            return None
        
        try:
            # 1. 執行回測
            print("\n[Step 1] Running backtest...")
            backtest_result = self._run_backtest()
            
            # 2. 生成 5 組預測號碼
            print("\n[Step 2] Generating 5 prediction sets...")
            eng = FeatureEngine()
            strat = StrategyEngine()
            
            scores = eng.get_all_scores(use_enhanced=True, use_time_series=False)
            final_scores = strat.calculate_total_score(scores)
            
            # 生成 5 組不同的號碼組合
            all_candidates = self._generate_multiple_sets(final_scores, num_sets=5)
            
            # 3. 計算預測日期
            last_date = pd.to_datetime(eng.df.iloc[-1]['date'])
            next_date = last_date + timedelta(days=1)
            
            # 跳過週日
            while next_date.weekday() == 6:
                next_date += timedelta(days=1)
            
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday = weekday_names[next_date.weekday()]
            prediction_date = f"{next_date.strftime('%Y-%m-%d')} {weekday}"
            
            print(f"[INFO] Prediction date: {prediction_date}")
            print(f"[INFO] Generated {len(all_candidates)} prediction sets:")
            for i, nums in enumerate(all_candidates, 1):
                print(f"  Set {i}: {nums}")
            
            # 4. 儲存預測 (儲存所有 5 組)
            print("\n[Step 3] Saving predictions...")
            self.prediction_history.save_prediction(
                prediction_date=prediction_date,
                numbers=all_candidates,  # 儲存所有 5 組
                backtest_result=backtest_result
            )
            
            # 5. 生成 AI 報告
            print("\n[Step 4] Generating AI report...")
            try:
                reporter = GeminiReporter()
                # 使用第一組號碼生成報告
                report = reporter.generate_report(all_candidates[0], final_scores)
            except Exception as e:
                print(f"[WARNING] AI report generation failed: {e}")
                report = None
            
            # 6. 記錄日誌
            structured_logger.log_operation(
                operation_type='auto_prediction',
                status='success',
                details={
                    'prediction_date': prediction_date,
                    'prediction_sets': all_candidates,
                    'num_sets': len(all_candidates)
                }
            )
            
            # 7. Discord 通知 (發送所有 5 組)
            print("\n[Step 5] Sending Discord notification...")
            self.discord.send_prediction_result(
                prediction_date=prediction_date,
                predicted_numbers=all_candidates,  # 傳遞所有 5 組
                backtest_result=backtest_result
            )
            
            result = {
                'prediction_date': prediction_date,
                'predicted_numbers': all_candidates,
                'num_sets': len(all_candidates),
                'backtest_result': backtest_result,
                'ai_report': report
            }
            
            print("\n" + "=" * 60)
            print(f"Prediction completed! Date: {prediction_date}")
            print(f"Generated {len(all_candidates)} sets for maximum coverage")
            print("=" * 60)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            import traceback
            traceback.print_exc()
            structured_logger.log_execution_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={'operation': 'auto_prediction'}
            )
            return None
    
    def _generate_multiple_sets(self, scores_df, num_sets=5) -> List[List[int]]:
        """生成多組號碼以提高覆蓋率"""
        all_sets = []
        used_combinations = set()
        
        # 確保 scores_df 有 num 欄位
        if 'num' not in scores_df.columns:
            scores_df = scores_df.copy()
            scores_df['num'] = scores_df.index
        
        # 策略 1: 標準分區策略
        strat = StrategyEngine()
        try:
             set1 = sorted(strat.partition_strategy(scores_df.copy()))[:5]
             all_sets.append(set1)
             used_combinations.add(tuple(set1))
        except:
             pass
        
        # 策略 2: 全域 Top 5
        set2 = sorted(scores_df.nlargest(5, 'total_score')['num'].tolist())
        if tuple(set2) not in used_combinations:
            all_sets.append(set2)
            used_combinations.add(tuple(set2))
        
        # 策略 3: 平衡策略 (每個分區取 1-2 個)
        ranges = [[1, 10], [11, 20], [21, 30], [31, 39]]
        set3 = []
        for start, end in ranges:
            subset = scores_df[(scores_df['num'] >= start) & (scores_df['num'] <= end)]
            if not subset.empty:
                top_in_range = subset.nlargest(1, 'total_score')['num'].tolist()
                set3.extend(top_in_range)
        
        # 補足到 5 個
        if len(set3) < 5:
            remaining = scores_df[~scores_df['num'].isin(set3)].nlargest(5 - len(set3), 'total_score')
            set3.extend(remaining['num'].tolist())
        
        set3 = sorted(set3[:5])
        if tuple(set3) not in used_combinations and len(set3) == 5:
            all_sets.append(set3)
            used_combinations.add(tuple(set3))
        
        # 策略 4: 高分 + 隨機組合
        top_3 = sorted(scores_df.nlargest(3, 'total_score')['num'].tolist())
        remaining_pool = scores_df[~scores_df['num'].isin(top_3)]
        if len(remaining_pool) >= 2:
            random_2 = sorted(remaining_pool.sample(n=2)['num'].tolist())
            set4 = sorted(top_3 + random_2)
            if tuple(set4) not in used_combinations and len(set4) == 5:
                all_sets.append(set4)
                used_combinations.add(tuple(set4))
        
        # 策略 5: 分散策略 (確保號碼分散)
        set5 = []
        for start, end in ranges:
            subset = scores_df[(scores_df['num'] >= start) & (scores_df['num'] <= end)]
            if not subset.empty and len(set5) < 5:
                # 隨機選擇該區間的高分號碼
                top_candidates = subset.nlargest(3, 'total_score')
                if len(top_candidates) > 0:
                    selected = top_candidates.sample(n=min(1, len(top_candidates)))['num'].tolist()
                    set5.extend(selected)
        
        if len(set5) < 5:
            remaining = scores_df[~scores_df['num'].isin(set5)].nlargest(5 - len(set5), 'total_score')
            set5.extend(remaining['num'].tolist())
        
        set5 = sorted(set5[:5])
        if tuple(set5) not in used_combinations and len(set5) == 5:
            all_sets.append(set5)
            used_combinations.add(tuple(set5))
        
        # 確保有 5 組
        while len(all_sets) < num_sets:
            # 生成隨機組合
            if len(scores_df) >= 5:
                random_set = sorted(scores_df.sample(n=5)['num'].tolist())
                if tuple(random_set) not in used_combinations:
                    all_sets.append(random_set)
                    used_combinations.add(tuple(random_set))
            else:
                break
        
        return all_sets[:num_sets]
    
    def _run_backtest(self) -> Optional[Dict]:
        """執行回測"""
        try:
            full_df = pd.read_csv("data/539_history.csv")
            
            if len(full_df) < 100:
                print("[WARNING] Insufficient data for backtest")
                return None
            
            eng_ver = FeatureEngine()
            real_last_draw = eng_ver.df.iloc[-1]
            real_last_nums = [int(n) for n in real_last_draw['numbers'].split(',')]
            
            # 使用倒數第二筆之前的資料來預測倒數第一筆
            eng_ver.df = eng_ver.df.iloc[:-1].reset_index(drop=True)
            eng_ver.numbers_series = eng_ver.numbers_series[:-1]
            
            scores_ver = eng_ver.get_all_scores(use_enhanced=True, use_time_series=False)
            strat_ver = StrategyEngine()
            candidates_ver = strat_ver.partition_strategy(strat_ver.calculate_total_score(scores_ver))
            
            hits = set(candidates_ver).intersection(set(real_last_nums))
            accuracy = len(hits) / 5.0
            
            strat_ver.update_weights(accuracy)
            
            result = {
                'date': str(real_last_draw['date']),
                'actual': real_last_nums,
                'predicted': candidates_ver,
                'hits': list(hits),
                'accuracy': accuracy
            }
            
            print(f"[INFO] Backtest result: {len(hits)}/5 ({accuracy:.0%})")
            
            return result
            
        except Exception as e:
            print(f"[WARNING] Backtest failed: {e}")
            return None


if __name__ == "__main__":
    # 測試自動預測
    predictor = AutoPredictor()
    
    print("\n[Test 1] Verify pending prediction...")
    verify_result = predictor.verify_pending_prediction()
    
    print("\n[Test 2] Generate new prediction...")
    predict_result = predictor.generate_new_prediction()
