# -*- coding: utf-8 -*-
"""
539 AI 預測系統 - 自動化主程式
整合所有自動化模組,實現完全自動化運行 (支援所有遊戲)
"""
import signal
import sys
from pathlib import Path
from src.scheduler import AutoScheduler
from src.auto_updater import AutoUpdater
from src.multi_game_manager import MultiGameManager
from src.auto_trainer import AutoTrainer
from src.structured_logger import structured_logger
from src.discord_notifier import DiscordNotifier


class AutomationSystem:
    """自動化系統主控制器"""
    
    def __init__(self):
        """初始化系統"""
        self.scheduler = AutoScheduler()
        self.updater = AutoUpdater()
        self.manager = MultiGameManager()
        self.trainer = AutoTrainer()
        self.discord = DiscordNotifier()
        
        # 註冊信號處理器 (優雅關閉)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """處理關閉信號"""
        print("\n[INFO] Received shutdown signal")
        self.shutdown()
        sys.exit(0)
    
    def setup_tasks(self):
        """設定自動化任務"""
        # 每日資料更新任務
        self.scheduler._placeholder_data_update = self.task_data_update
        
        # 每日預測驗證任務
        self.scheduler._placeholder_verification = self.task_verification
        
        # 每日新預測任務
        self.scheduler._placeholder_prediction = self.task_prediction
        
        # 每日訓練任務
        self.scheduler._placeholder_training = self.task_training
    
    def task_data_update(self):
        """資料更新任務"""
        print("\n[TASK] Data Update Task")
        try:
            result = self.updater.update_and_validate()
            
            if result['success'] and result['new_records'] > 0:
                print(f"[SUCCESS] Updated {result['new_records']} new records")
            elif result['success']:
                print("[INFO] No new data available")
            else:
                print(f"[ERROR] Update failed: {result['errors']}")
        except Exception as e:
            print(f"[ERROR] Data update exception: {e}")
    
    def task_verification(self):
        """預測驗證任務 (主要針對 539)"""
        print("\n[TASK] Verification Task")
        try:
            # 539 驗證 (因為只有 539 有完整的歷史追蹤機制)
            if '539' in self.manager.predictors:
                result = self.manager.predictors['539'].verify_pending_prediction()
                if result:
                    print(f"[SUCCESS] Verified 539 prediction: {result['accuracy']:.0%} accuracy")
                else:
                    print("[INFO] No pending 539 prediction to verify")
        except Exception as e:
            print(f"[ERROR] Verification failed: {e}")
    
    def task_prediction(self):
        """新預測任務 (所有遊戲)"""
        print("\n[TASK] Prediction Task (All Games)")
        try:
            results = self.manager.generate_all_predictions()
            self.manager.send_all_predictions(results)
            print(f"[SUCCESS] Generated and sent predictions for {len(results)} games")
        except Exception as e:
            print(f"[ERROR] Prediction task failed: {e}")
    
    def task_training(self):
        """訓練任務"""
        print("\n[TASK] Training Task")
        try:
            result = self.trainer.run_full_training()
            
            if result['success']:
                if result['training_periods'] > 0:
                    print(f"[SUCCESS] Training completed: {result['avg_accuracy']:.2%} accuracy")
                else:
                    print("[INFO] Training skipped (conditions not met)")
            else:
                print(f"[ERROR] Training failed: {result['errors']}")
        except Exception as e:
            print(f"[ERROR] Training exception: {e}")
    
    def start(self):
        """啟動自動化系統"""
        print("=" * 60)
        print("539 AI Automation System (v5.0 Multi-Game)")
        print("=" * 60)
        
        # 發送啟動通知
        try:
            self.discord.send_test_message()
        except Exception as e:
            print(f"[WARNING] Failed to send startup notification: {e}")
        
        # 記錄啟動
        structured_logger.log_operation(
            operation_type='system_startup',
            status='success',
            details={'version': '5.0.0'}
        )
        
        # 設定任務
        self.setup_tasks()
        
        # 設定排程
        self.scheduler.setup_default_schedule()
        
        # 啟動排程器 (阻塞模式)
        self.scheduler.start()
    
    def shutdown(self):
        """關閉系統"""
        print("\n[INFO] Shutting down automation system...")
        
        # 記錄關閉
        structured_logger.log_operation(
            operation_type='system_shutdown',
            status='success'
        )
        
        # 關閉排程器
        self.scheduler.shutdown()
        
        print("[INFO] System shutdown complete")


def main():
    """主函數"""
    system = AutomationSystem()
    system.start()


if __name__ == "__main__":
    main()
