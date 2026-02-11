# -*- coding: utf-8 -*-
"""
清理訓練資料腳本
清除所有訓練相關的資料,保留原始歷史資料
"""
import shutil
from pathlib import Path

def cleanup_training_data():
    """清除訓練資料"""
    
    # 需要清除的目錄
    dirs_to_clean = [
        'data/predictions',
        'data/weights',
        'data/models',
        'data/training_logs'
    ]
    
    print("=" * 60)
    print("開始清理訓練資料...")
    print("=" * 60)
    
    for dir_path in dirs_to_clean:
        path = Path(dir_path)
        
        if path.exists():
            # 刪除目錄
            shutil.rmtree(path)
            print(f"[OK] 已清除: {dir_path}")
        
        # 重建空目錄
        path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] 已重建: {dir_path}")
    
    print("\n" + "=" * 60)
    print("清理完成!")
    print("=" * 60)

if __name__ == "__main__":
    cleanup_training_data()
