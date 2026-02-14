# -*- coding: utf-8 -*-
"""
自動化排程系統
使用 APScheduler 管理所有定時任務
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
from pathlib import Path
from typing import Callable, Optional
import traceback
from src.structured_logger import structured_logger
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_now


class AutoScheduler:
    """自動化排程管理器"""
    
    def __init__(self, config_path: str = "config/auto_config.json"):
        """初始化排程器"""
        from src.timezone_utils import TAIWAN_TZ
        self.config_path = Path(config_path)
        self.config = self._load_config()
        # 明確設定台灣時區
        self.scheduler = BlockingScheduler(timezone=TAIWAN_TZ)
        self.discord = DiscordNotifier(config_path)
        
        # 任務執行統計
        self.task_stats = {
            'data_update': {'success': 0, 'failed': 0},
            'verification': {'success': 0, 'failed': 0},
            'prediction': {'success': 0, 'failed': 0},
            'training': {'success': 0, 'failed': 0}
        }
    
    def _load_config(self) -> dict:
        """載入配置檔"""
        if not self.config_path.exists():
            print(f"[WARNING] Config file not found: {self.config_path}")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            return {}
    
    def _execute_with_retry(
        self, 
        task_func: Callable, 
        task_name: str,
        max_attempts: Optional[int] = None,
        interval_minutes: Optional[int] = None
    ) -> bool:
        """執行任務並支援重試機制"""
        if max_attempts is None:
            max_attempts = self.config.get('retry', {}).get('max_attempts', 3)
        if interval_minutes is None:
            interval_minutes = self.config.get('retry', {}).get('interval_minutes', 5)
        
        start_time = get_taiwan_now()
        
        for attempt in range(max_attempts):
            try:
                print(f"[INFO] Executing {task_name} (attempt {attempt + 1}/{max_attempts})...")
                
                # 執行任務
                task_func()
                
                # 計算執行時間
                duration = (get_taiwan_now() - start_time).total_seconds()
                
                # 記錄成功
                structured_logger.log_operation(
                    operation_type=task_name,
                    status='success',
                    duration_seconds=duration
                )
                
                # 更新統計
                if task_name in self.task_stats:
                    self.task_stats[task_name]['success'] += 1
                
                print(f"[SUCCESS] {task_name} completed in {duration:.2f}s")
                return True
                
            except Exception as e:
                error_msg = f"{task_name} failed: {e}"
                stack_trace = traceback.format_exc()
                
                print(f"[ERROR] {error_msg}")
                
                # 記錄異常
                structured_logger.log_execution_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=stack_trace,
                    context={'task_name': task_name, 'attempt': attempt + 1}
                )
                
                # 如果是最後一次嘗試,發送 Discord 警報
                if attempt == max_attempts - 1:
                    self.discord.send_error_alert(
                        error_type=f"{task_name} Failed",
                        error_message=error_msg,
                        stack_trace=stack_trace
                    )
                    
                    # 更新統計
                    if task_name in self.task_stats:
                        self.task_stats[task_name]['failed'] += 1
                    
                    return False
                
                # 等待後重試
                import time
                time.sleep(interval_minutes * 60)
        
        return False
    
    def add_daily_task(
        self, 
        task_func: Callable, 
        task_name: str, 
        hour: int, 
        minute: int
    ):
        """新增每日定時任務"""
        self.scheduler.add_job(
            lambda: self._execute_with_retry(task_func, task_name),
            CronTrigger(hour=hour, minute=minute),
            id=task_name,
            name=task_name,
            replace_existing=True
        )
        print(f"[INFO] Scheduled daily task: {task_name} at {hour:02d}:{minute:02d}")
    
    def add_weekly_task(
        self, 
        task_func: Callable, 
        task_name: str, 
        day_of_week: str, 
        hour: int, 
        minute: int
    ):
        """新增每週定時任務"""
        # day_of_week: 'monday', 'tuesday', ..., 'sunday'
        self.scheduler.add_job(
            lambda: self._execute_with_retry(task_func, task_name),
            CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            id=task_name,
            name=task_name,
            replace_existing=True
        )
        print(f"[INFO] Scheduled weekly task: {task_name} on {day_of_week} at {hour:02d}:{minute:02d}")
    
    # 真實任務函數
    def _run_data_update(self):
        """執行每日資料更新"""
        from src.auto_updater import AutoUpdater
        print("\n[Scheduler] Starting Data Update...")
        updater = AutoUpdater()
        updater.update_and_validate()
    
    def _run_verification(self):
        """執行預測驗證 (所有遊戲)"""
        from src.multi_game_manager import MultiGameManager
        print("\n[Scheduler] Starting Prediction Verification...")
        manager = MultiGameManager()
        results = manager.verify_all_predictions()
        
        # 儲存驗證結果供訓練流程使用
        self.last_verification_results = results
        
        # 發送驗證報告到 Discord
        if results:
            manager.send_verification_summary(results)
        
        return results

    def _run_training(self):
        """執行自動訓練 (使用驗證結果)"""
        from src.auto_trainer import AutoTrainer
        print("\n[Scheduler] Starting Auto Training...")
        trainer = AutoTrainer()
        
        # 傳遞驗證結果給訓練流程
        verification_results = getattr(self, 'last_verification_results', None)
        trainer.run_full_training(verification_results=verification_results)

    def _run_math_validation(self):
        """執行數學專家驗證"""
        from src.ai_advisors.math_validator import MathValidator
        print("\n[Scheduler] Starting Math Validation...")
        validator = MathValidator()
        results = validator.run_daily_validation()
        return results
    
    def _run_numerology_advice(self):
        """執行命理專家建議"""
        from src.ai_advisors.numerology_advisor import NumerologyAdvisor
        from datetime import date
        print("\n[Scheduler] Getting Numerology Advice...")
        advisor = NumerologyAdvisor()
        today = date.today().strftime('%Y-%m-%d')
        advice = advisor.get_daily_numerology_advice(today)
        advisor.send_daily_numerology_report(today, advice)
        return advice
    
    def _run_digital_twin_review(self):
        """執行 AI 分身審查"""
        from src.ai_advisors.digital_twin import DigitalTwinAdvisor
        print("\n[Scheduler] Starting Digital Twin Review...")
        twin = DigitalTwinAdvisor()
        context = {
            'verification_results': getattr(self, 'last_verification_results', {}),
            'timestamp': __import__('src.timezone_utils', fromlist=['get_taiwan_isoformat']).get_taiwan_isoformat()
        }
        review = twin.daily_strategic_review(context)
        return review
    
    def _run_prediction(self):
        """執行新預測生成與推送"""
        from src.multi_game_manager import MultiGameManager
        print("\n[Scheduler] Starting Prediction Generation...")
        manager = MultiGameManager()
        results = manager.generate_all_predictions()
        manager.send_all_predictions(results)

    def setup_default_schedule(self):
        """設定預設排程 (從配置檔讀取)"""
        schedule_config = self.config.get('schedule', {})
        
        # 解析時間字串
        def parse_time(time_str: str) -> tuple:
            """解析 HH:MM 格式的時間字串"""
            parts = time_str.split(':')
            return int(parts[0]), int(parts[1])
        
        # 每日資料更新 (20:35 - 配合台彩開獎約 20:30)
        update_time = schedule_config.get('data_update_time', '20:35')
        hour, minute = parse_time(update_time)
        self.add_daily_task(
            self._run_data_update,
            'data_update',
            hour,
            minute
        )
        
        # 每日訓練 (20:40)
        training_time = schedule_config.get('training_time', '20:40')
        hour, minute = parse_time(training_time)
        self.add_daily_task(
            self._run_training,
            'training',
            hour,
            minute
        )
        
        # 每日新預測與推送 (20:45)
        predict_time = schedule_config.get('prediction_time', '20:45')
        hour, minute = parse_time(predict_time)
        self.add_daily_task(
            self._run_prediction,
            'prediction',
            hour,
            minute
        )
        
    def start(self):
        """啟動排程器"""
        print("=" * 60)
        print("Auto Scheduler Starting... (Timezone: Taiwan)")
        print("=" * 60)
        
        # 顯示已排程的任務
        jobs = self.scheduler.get_jobs()
        print(f"\n[INFO] Total scheduled jobs: {len(jobs)}")
        for job in jobs:
            print(f"  - {job.name}: {job.trigger}")
        
        print("\n[INFO] Scheduler is running. Press Ctrl+C to stop.")
        print("=" * 60)
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n[INFO] Scheduler stopped by user")
            self.shutdown()
    
    def shutdown(self):
        """關閉排程器"""
        print("\n[INFO] Shutting down scheduler...")
        
        # 記錄統計
        structured_logger.log_operation(
            operation_type='scheduler_shutdown',
            status='success',
            details={'task_stats': self.task_stats}
        )
        
        if self.scheduler.running:
            self.scheduler.shutdown()
        print("[INFO] Scheduler shutdown complete")


if __name__ == "__main__":
    # 測試排程器
    scheduler = AutoScheduler()
    scheduler.setup_default_schedule()
    
    # 啟動排程器 (阻塞模式)
    scheduler.start()
