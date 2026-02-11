# -*- coding: utf-8 -*-
"""
自動訓練模組
整合 IncrementalTrainer,實現自動化訓練流程
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import shutil
import json
from typing import Optional, Dict
from src.incremental_trainer import IncrementalTrainer
from src.structured_logger import structured_logger
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_timestamp_str


class AutoTrainer:
    """自動訓練協調器"""
    
    def __init__(self):
        """初始化"""
        self.config_file = Path('config.json')
        self.backup_dir = Path('config/backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.discord = DiscordNotifier()
    
    def _backup_config(self) -> Optional[Path]:
        """備份權重配置"""
        if not self.config_file.exists():
            print("[WARNING] Config file not found")
            return None
        
        timestamp = get_taiwan_timestamp_str()
        backup_path = self.backup_dir / f"config_{timestamp}.json"
        
        try:
            shutil.copy2(self.config_file, backup_path)
            file_size = self.config_file.stat().st_size
            
            structured_logger.log_backup(
                backup_type='auto_training',
                source_path=str(self.config_file),
                backup_path=str(backup_path),
                file_size_bytes=file_size,
                success=True
            )
            
            print(f"[SUCCESS] Config backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"[ERROR] Config backup failed: {e}")
            return None
    
    def should_trigger_training(self) -> bool:
        """判斷是否需要訓練 (目前設定為每日訓練)"""
        # 可以在這裡加入更複雜的判斷邏輯
        # 例如: 檢查是否有足夠的新驗證資料
        return True
    
    def run_full_training(self) -> Optional[Dict]:
        """執行完整訓練流程"""
        print("=" * 60)
        print("Auto Training Starting...")
        print("=" * 60)
        
        result = {
            'success': False,
            'training_periods': 0,
            'avg_accuracy': 0.0,
            'improvements': {},
            'errors': []
        }
        
        try:
            # 1. 備份權重配置
            print("\n[Step 1] Backing up weight configuration...")
            self._backup_config()
            
            # 2. 檢查是否需要訓練
            print("\n[Step 2] Checking training trigger conditions...")
            if not self.should_trigger_training():
                print("[INFO] Training not triggered")
                result['success'] = True
                return result
            
            # 3. 執行訓練
            print("\n[Step 3] Running incremental training...")
            trainer = IncrementalTrainer(
                data_path="data/539_train.csv",
                config_path="config.json",
                use_llm=True,
                use_enhanced_models=True
            )
            
            # 執行訓練
            training_result = trainer.train()
            
            if not training_result:
                result['errors'].append("Training execution failed")
                return result
            
            # 4. 分析訓練結果
            print("\n[Step 4] Analyzing training results...")
            result['training_periods'] = training_result.get('total_periods', 0)
            result['avg_accuracy'] = training_result.get('avg_accuracy', 0.0)
            
            # 計算改進
            if 'improvements' in training_result:
                result['improvements'] = training_result['improvements']
            
            result['success'] = True
            
            # 5. 記錄日誌
            structured_logger.log_operation(
                operation_type='auto_training',
                status='success',
                details={
                    'training_periods': result['training_periods'],
                    'avg_accuracy': result['avg_accuracy'],
                    'improvements': result['improvements']
                }
            )
            
            # 6. Discord 通知
            print("\n[Step 5] Sending Discord notification...")
            self.discord.send_training_report(
                training_periods=result['training_periods'],
                avg_accuracy=result['avg_accuracy'],
                improvements=result['improvements']
            )
            
            print("\n" + "=" * 60)
            print(f"Training completed! Avg accuracy: {result['avg_accuracy']:.2%}")
            print("=" * 60)
            
        except Exception as e:
            result['errors'].append(str(e))
            structured_logger.log_execution_error(
                error_type=type(e).__name__,
                error_message=str(e),
                context={'operation': 'auto_training'}
            )
            
            # Discord 異常通知
            self.discord.send_error_alert(
                error_type="Auto Training Failed",
                error_message=str(e)
            )
        
        return result
    
    def run_quick_training(self, periods: int = 10) -> Optional[Dict]:
        """執行快速訓練 (僅訓練最近 N 期)"""
        print("=" * 60)
        print(f"Quick Training Starting (Last {periods} periods)...")
        print("=" * 60)
        
        result = {
            'success': False,
            'training_periods': 0,
            'avg_accuracy': 0.0,
            'errors': []
        }
        
        try:
            # 備份配置
            self._backup_config()
            
            # 讀取資料
            df = pd.read_csv("data/539_train.csv")
            
            if len(df) < periods:
                print(f"[WARNING] Insufficient data for {periods} periods training")
                periods = len(df)
            
            # 僅使用最近 N 期資料
            df_recent = df.tail(periods).reset_index(drop=True)
            
            # 儲存臨時資料
            temp_file = Path("data/temp_train.csv")
            df_recent.to_csv(temp_file, index=False)
            
            # 執行訓練
            trainer = IncrementalTrainer(
                data_path=str(temp_file),
                config_path="config.json",
                use_llm=False,  # 快速訓練不使用 LLM
                use_enhanced_models=True
            )
            
            training_result = trainer.train()
            
            # 清理臨時檔案
            temp_file.unlink()
            
            if training_result:
                result['training_periods'] = periods
                result['avg_accuracy'] = training_result.get('avg_accuracy', 0.0)
                result['success'] = True
                
                print(f"\n[SUCCESS] Quick training completed: {result['avg_accuracy']:.2%}")
            
        except Exception as e:
            result['errors'].append(str(e))
            print(f"[ERROR] Quick training failed: {e}")
        
        return result


if __name__ == "__main__":
    # 測試自動訓練
    trainer = AutoTrainer()
    
    print("\n[Test 1] Full training...")
    result = trainer.run_full_training()
    
    print("\n[Result]")
    print(f"  Success: {result['success']}")
    print(f"  Training Periods: {result['training_periods']}")
    print(f"  Avg Accuracy: {result['avg_accuracy']:.2%}")
    if result['improvements']:
        print(f"  Improvements: {result['improvements']}")
    if result['errors']:
        print(f"  Errors: {result['errors']}")
