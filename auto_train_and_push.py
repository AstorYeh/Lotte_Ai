# -*- coding: utf-8 -*-
"""
自動訓練並推送到 GitHub
本機執行訓練,完成後自動提交並推送結果
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from src.auto_trainer import AutoTrainer
from src.timezone_utils import get_taiwan_timestamp_str


def run_training():
    """執行訓練"""
    print("=" * 60)
    print("Starting Auto Training...")
    print("=" * 60)
    
    trainer = AutoTrainer()
    result = trainer.run_full_training()
    
    if result['success']:
        print(f"\n[SUCCESS] Training completed!")
        print(f"  Periods: {result['training_periods']}")
        print(f"  Accuracy: {result['avg_accuracy']:.2%}")
        return True
    else:
        print(f"\n[ERROR] Training failed: {result['errors']}")
        return False


def git_push():
    """提交並推送到 GitHub"""
    print("\n" + "=" * 60)
    print("Pushing to GitHub...")
    print("=" * 60)
    
    try:
        # 檢查是否有變更
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd='d:/539'
        )
        
        if not status.stdout.strip():
            print("[INFO] No changes to commit")
            return True
        
        # Add 變更的檔案
        subprocess.run(['git', 'add', 'config.json'], cwd='d:/539', check=True)
        subprocess.run(['git', 'add', 'logs/iterations/'], cwd='d:/539', check=True)
        
        # Commit
        timestamp = get_taiwan_timestamp_str()
        commit_msg = f"chore: 自動訓練更新 - {timestamp}"
        
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd='d:/539',
            check=True
        )
        
        # Push
        subprocess.run(['git', 'push', 'origin', 'main'], cwd='d:/539', check=True)
        
        print("[SUCCESS] Pushed to GitHub!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")
        return False


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Auto Training & GitHub Push")
    print("=" * 60)
    
    # 1. 執行訓練
    if not run_training():
        print("\n[ABORT] Training failed, skipping GitHub push")
        sys.exit(1)
    
    # 2. 推送到 GitHub
    if not git_push():
        print("\n[WARNING] GitHub push failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Training and push successful!")
    print("=" * 60)


if __name__ == "__main__":
    main()
