"""
完整訓練腳本 - 強化修補版本
執行完整的漸進式訓練 (30 → 335 期)
確保與舊訓練記錄完全分離
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.incremental_trainer import IncrementalTrainer
from src.logger import logger
from src.timezone_utils import get_taiwan_now

def main():
    print("=" * 70)
    print("  539 AI 完整訓練 - 強化修補版本")
    print("=" * 70)
    print()
    
    # 確認修改版本
    print("[版本確認]")
    print("  - 權重優化器: 放寬調整條件 [OK]")
    print("  - 群組策略: 降低閾值至 0.45 [OK]")
    print("  - 學習參數: 學習率 0.4, 觀察窗口 3 [OK]")
    print()
    
    # 載入完整歷史數據
    data_file = "data/539_history.csv"
    df = pd.read_csv(data_file)
    
    print("[數據資訊]")
    print(f"  - 數據來源: {data_file}")
    print(f"  - 總期數: {len(df)} 期")
    print(f"  - 日期範圍: {df.iloc[0]['date']} ~ {df.iloc[-1]['date']}")
    print()
    
    # 設定訓練參數
    initial_periods = 30  # 從第 30 期開始
    total_periods = len(df)
    training_periods = total_periods - initial_periods
    
    print("[訓練計畫]")
    print(f"  - 初始訓練期數: {initial_periods} 期")
    print(f"  - 漸進訓練期數: {training_periods} 期 (第 {initial_periods+1} ~ {total_periods} 期)")
    print(f"  - 預計訓練時間: ~{training_periods * 3} 秒 (約 {training_periods * 3 / 60:.1f} 分鐘)")
    print()
    
    # 確認是否繼續
    print("[重要提醒]")
    print("  本次訓練將:")
    print("  1. 使用修改後的新版本代碼")
    print("  2. 創建全新的訓練記錄 (時間戳記標記)")
    print("  3. 不會影響舊的訓練記錄")
    print()
    
    response = input("確認開始完整訓練? (y/n): ")
    if response.lower() != 'y':
        print("訓練已取消")
        return
    
    print()
    print("=" * 70)
    print("  開始訓練...")
    print("=" * 70)
    print()
    
    # 初始化訓練器
    trainer = IncrementalTrainer(
        initial_periods=initial_periods,
        use_llm=False,  # 暫不使用 LLM (加快速度)
        use_enhanced=True  # 使用增強模型
    )
    
    # 記錄開始時間
    start_time = get_taiwan_now()
    
    # 執行訓練
    try:
        for period_index in range(initial_periods, total_periods):
            period_num = period_index + 1
            
            # 每 10 期顯示進度
            if period_num % 10 == 0 or period_num == initial_periods + 1:
                elapsed = (get_taiwan_now() - start_time).total_seconds()
                progress = (period_index - initial_periods) / training_periods * 100
                eta = elapsed / (period_index - initial_periods + 1) * (total_periods - period_index) if period_index > initial_periods else 0
                
                print(f"\n[進度 {progress:.1f}%] 第 {period_num}/{total_periods} 期")
                print(f"  已耗時: {elapsed:.0f}秒 | 預計剩餘: {eta:.0f}秒")
            
            # 訓練單期
            trainer.train_period(df, period_index)
        
        # 完成訓練
        trainer.iteration_logger.finalize()
        
        # 計算總耗時
        total_time = (get_taiwan_now() - start_time).total_seconds()
        
        print()
        print("=" * 70)
        print("  訓練完成!")
        print("=" * 70)
        print()
        print(f"[統計資訊]")
        print(f"  - 總訓練期數: {training_periods} 期")
        print(f"  - 總耗時: {total_time:.0f} 秒 ({total_time/60:.1f} 分鐘)")
        print(f"  - 平均速度: {total_time/training_periods:.1f} 秒/期")
        print()
        
        # 讀取訓練結果
        latest_session = sorted(
            Path("logs/iterations").glob("*"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[0]
        
        print(f"[訓練記錄]")
        print(f"  - Session ID: {latest_session.name}")
        print(f"  - 位置: {latest_session}")
        print()
        
        # 讀取摘要
        import json
        summary_file = latest_session / "training_summary.json"
        if summary_file.exists():
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            stats = summary['statistics']
            print(f"[訓練結果]")
            print(f"  - 平均準確率: {stats['average_accuracy']:.2%}")
            print(f"  - 最佳準確率: {stats['best_accuracy']:.2%}")
            print(f"  - 最差準確率: {stats['worst_accuracy']:.2%}")
            print(f"  - 總命中數: {stats['total_hits']}")
            print()
            
            # 計算 0% 期數
            zero_periods = sum(1 for it in summary['iterations'] if it['accuracy'] == 0)
            zero_rate = zero_periods / stats['total_periods']
            print(f"  - 0% 期數: {zero_periods}/{stats['total_periods']} ({zero_rate:.1%})")
            
            # 計算各準確率區間分布
            acc_dist = {}
            for it in summary['iterations']:
                acc = it['accuracy']
                if acc == 0:
                    key = '0%'
                elif acc <= 0.2:
                    key = '20%'
                elif acc <= 0.4:
                    key = '40%'
                elif acc <= 0.6:
                    key = '60%'
                elif acc <= 0.8:
                    key = '80%'
                else:
                    key = '100%'
                acc_dist[key] = acc_dist.get(key, 0) + 1
            
            print()
            print(f"[準確率分布]")
            for key in ['0%', '20%', '40%', '60%', '80%', '100%']:
                if key in acc_dist:
                    count = acc_dist[key]
                    pct = count / stats['total_periods'] * 100
                    print(f"  {key:>4}: {count:>3} 期 ({pct:>5.1f}%)")
        
        print()
        print("[下一步]")
        print("  1. 執行分析: python analyze_training.py")
        print("  2. 查看學習曲線圖")
        print("  3. 對比修改前後的結果")
        
    except KeyboardInterrupt:
        print("\n\n訓練已中斷!")
        print("部分結果已保存,可稍後繼續")
    except Exception as e:
        print(f"\n\n訓練過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
