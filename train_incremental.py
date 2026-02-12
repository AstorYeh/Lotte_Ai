# -*- coding: utf-8 -*-
"""
增量訓練腳本 - 只訓練新增的期數
支援 GPU 加速
"""
import json
from pathlib import Path
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger
import pandas as pd


def get_last_trained_period():
    """從 config.json 讀取上次訓練到第幾期"""
    config_file = Path('config.json')
    
    if not config_file.exists():
        return 30  # 預設從第 30 期開始
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 假設 config 中有記錄最後訓練期數
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
            
        logger.info(f"Updated last_trained_period to {period}")
    except Exception as e:
        logger.error(f"Failed to update config: {e}")


def incremental_train(use_gpu=True):
    """
    增量訓練 - 只訓練新增的期數
    
    Args:
        use_gpu: 是否使用 GPU 加速
    """
    print("=" * 60)
    print("Incremental Training (GPU Accelerated)")
    print("=" * 60)
    
    # 1. 讀取資料
    data_file = Path('data/539_train.csv')
    df = pd.read_csv(data_file)
    total_periods = len(df)
    
    # 2. 取得上次訓練進度
    last_period = get_last_trained_period()
    
    print(f"\n[INFO] Total periods: {total_periods}")
    print(f"[INFO] Last trained: {last_period}")
    print(f"[INFO] New periods to train: {total_periods - last_period}")
    
    if total_periods <= last_period:
        print("\n[INFO] No new periods to train!")
        return
    
    # 3. 初始化訓練器
    trainer = IncrementalTrainer(
        initial_periods=last_period,
        use_llm=True,
        use_enhanced=use_gpu  # GPU 模式啟用增強模型
    )
    
    # 4. 只訓練新增的期數
    print(f"\n[INFO] Training periods {last_period + 1} to {total_periods}...")
    print(f"[INFO] GPU Acceleration: {'ON' if use_gpu else 'OFF'}")
    
    for period_index in range(last_period, total_periods):
        trainer.train_period(df, period_index)
    
    # 5. 完成訓練
    trainer.iteration_logger.finalize()
    
    # 6. 更新進度
    update_last_trained_period(total_periods)
    
    print("\n" + "=" * 60)
    print(f"[SUCCESS] Incremental training complete!")
    print(f"[SUCCESS] Trained {total_periods - last_period} new periods")
    print("=" * 60)


if __name__ == "__main__":
    # 檢查是否有 GPU
    try:
        import torch
        has_gpu = torch.cuda.is_available()
        print(f"[INFO] GPU Available: {has_gpu}")
        if has_gpu:
            print(f"[INFO] GPU Device: {torch.cuda.get_device_name(0)}")
    except:
        has_gpu = False
        print("[INFO] PyTorch not found, GPU detection skipped")
    
    # 執行增量訓練
    incremental_train(use_gpu=has_gpu)
