# -*- coding: utf-8 -*-
"""
增量訓練並推送到 GitHub
只訓練新增期數,支援 GPU 加速
"""
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from src.incremental_trainer import IncrementalTrainer
from src.timezone_utils import get_taiwan_timestamp_str


def get_last_trained_period():
    """從 config.json 讀取上次訓練到第幾期"""
    config_file = Path('config.json')
    
    if not config_file.exists():
        return 30
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('last_trained_period', 30)
    except:
        return 30


def update_last_trained_period(period):
    """更新 config.json 中的最後訓練期數"""
    config_file = Path('config.json')
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['last_trained_period'] = period
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to update config: {e}")


def incremental_train(use_gpu=True):
    """增量訓練"""
    print("=" * 60)
    print("Incremental Training (GPU Accelerated)")
    print("=" * 60)
    
    # 讀取資料
    data_file = Path('data/539_train.csv')
    df = pd.read_csv(data_file)
    total_periods = len(df)
    
    # 取得上次訓練進度
    last_period = get_last_trained_period()
    
    print(f"\n[INFO] Total periods: {total_periods}")
    print(f"[INFO] Last trained: {last_period}")
    print(f"[INFO] New periods: {total_periods - last_period}")
    
    if total_periods <= last_period:
        print("\n[INFO] No new periods to train!")
        return False
    
    # 初始化訓練器
    trainer = IncrementalTrainer(
        initial_periods=last_period,
        use_llm=True,
        use_enhanced=use_gpu
    )
    
    # 訓練新增期數
    print(f"\n[INFO] Training periods {last_period + 1} to {total_periods}...")
    print(f"[INFO] GPU: {'ON' if use_gpu else 'OFF'}")
    
    for period_index in range(last_period, total_periods):
        trainer.train_period(df, period_index)
    
    trainer.iteration_logger.finalize()
    update_last_trained_period(total_periods)
    
    print(f"\n[SUCCESS] Trained {total_periods - last_period} new periods!")
    return True


def git_push():
    """推送到 GitHub"""
    print("\n" + "=" * 60)
    print("Pushing to GitHub...")
    print("=" * 60)
    
    try:
        # 檢查變更
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd='d:/539'
        )
        
        if not status.stdout.strip():
            print("[INFO] No changes to commit")
            return True
        
        # Add, Commit, Push
        subprocess.run(['git', 'add', 'config.json', 'logs/iterations/'], cwd='d:/539', check=True)
        
        timestamp = get_taiwan_timestamp_str()
        commit_msg = f"chore: 增量訓練更新 - {timestamp}"
        
        subprocess.run(['git', 'commit', '-m', commit_msg], cwd='d:/539', check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd='d:/539', check=True)
        
        print("[SUCCESS] Pushed to GitHub!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")
        return False


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Incremental Training & GitHub Push")
    print("=" * 60)
    
    # 檢查 GPU
    try:
        import torch
        has_gpu = torch.cuda.is_available()
        if has_gpu:
            print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
    except:
        has_gpu = False
        print("[INFO] GPU: Not available")
    
    # 增量訓練
    if not incremental_train(use_gpu=has_gpu):
        print("\n[INFO] No training needed")
        sys.exit(0)
    
    # 推送到 GitHub
    if not git_push():
        print("\n[WARNING] GitHub push failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Incremental training and push successful!")
    print("=" * 60)


if __name__ == "__main__":
    main()
