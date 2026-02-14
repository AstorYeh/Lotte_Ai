# -*- coding: utf-8 -*-
"""
手動測試腳本 - 完整流程測試
用於測試整個 539 AI 預測系統的完整流程
"""
import sys
import io
from pathlib import Path
from datetime import datetime
from src.timezone_utils import get_taiwan_datetime_str

# 設定 stdout 為 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_section(title):
    """列印區段標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_imports():
    """測試核心模組導入"""
    print_section("1. 測試核心模組導入")
    
    try:
        from src.auto_trainer import AutoTrainer
        print("[OK] AutoTrainer 導入成功")
    except Exception as e:
        print(f"[FAIL] AutoTrainer 導入失敗: {e}")
        return False
    
    try:
        from src.scheduler import AutoScheduler
        print("[OK] AutoScheduler 導入成功")
    except Exception as e:
        print(f"[FAIL] AutoScheduler 導入失敗: {e}")
        return False
    
    try:
        from src.auto_updater import AutoUpdater
        print("[OK] AutoUpdater 導入成功")
    except Exception as e:
        print(f"[FAIL] AutoUpdater 導入失敗: {e}")
        return False
    
    try:
        from src.multi_game_manager import MultiGameManager
        print("[OK] MultiGameManager 導入成功")
    except Exception as e:
        print(f"[FAIL] MultiGameManager 導入失敗: {e}")
        return False
    
    try:
        from src.incremental_trainer import IncrementalTrainer
        print("[OK] IncrementalTrainer 導入成功")
    except Exception as e:
        print(f"[FAIL] IncrementalTrainer 導入失敗: {e}")
        return False
    
    return True

def test_data_files():
    """測試資料檔案存在性"""
    print_section("2. 測試資料檔案")
    
    required_files = [
        "data/539_train.csv",
        "data/539_history.csv",
        "config.json",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"[OK] {file_path} ({size:,} bytes)")
        else:
            print(f"[FAIL] {file_path} 不存在")
            all_exist = False
    
    return all_exist

def test_timezone():
    """測試時區設定"""
    print_section("3. 測試時區設定")
    
    try:
        from src.timezone_utils import get_taiwan_now, TAIWAN_TZ
        now = get_taiwan_now()
        print(f"[OK] 當前台灣時間: {now}")
        print(f"[OK] 時區: {now.tzinfo}")
        print(f"[OK] UTC 偏移: {now.strftime('%z')}")
        return True
    except Exception as e:
        print(f"[FAIL] 時區測試失敗: {e}")
        return False

def test_feature_engine():
    """測試特徵引擎"""
    print_section("4. 測試特徵引擎")
    
    try:
        import pandas as pd
        from src.models import FeatureEngine
        
        # 讀取少量資料測試
        df = pd.read_csv("data/539_train.csv").tail(10)
        print(f"[OK] 讀取訓練資料: {len(df)} 筆")
        
        # 建立特徵引擎
        engine = FeatureEngine(data_df=df)
        print("[OK] FeatureEngine 初始化成功")
        
        # 測試評分
        scores = engine.get_all_scores(use_enhanced=False)
        print(f"[OK] 取得評分: {len(scores)} 個號碼")
        
        return True
    except Exception as e:
        print(f"[FAIL] 特徵引擎測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_incremental_trainer():
    """測試增量訓練器"""
    print_section("5. 測試增量訓練器(快速測試)")
    
    try:
        import pandas as pd
        from src.incremental_trainer import IncrementalTrainer
        
        # 使用少量資料測試
        df = pd.read_csv("data/539_train.csv").tail(35)
        print(f"[OK] 讀取測試資料: {len(df)} 筆")
        
        # 初始化訓練器
        trainer = IncrementalTrainer(
            initial_periods=30,
            use_llm=False,  # 快速測試不使用 LLM
            use_enhanced=False
        )
        print("[OK] IncrementalTrainer 初始化成功")
        
        # 測試單期訓練
        print("[...] 測試訓練第 31 期...")
        trainer.train_period(df, 30)
        print("[OK] 單期訓練成功")
        
        return True
    except Exception as e:
        print(f"[FAIL] 增量訓練器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scheduler_config():
    """測試排程器配置"""
    print_section("6. 測試排程器配置")
    
    try:
        from src.scheduler import AutoScheduler
        
        scheduler = AutoScheduler()
        print("[OK] AutoScheduler 初始化成功")
        print(f"[OK] 配置檔案: {scheduler.config_path}")
        print(f"[OK] 時區: {scheduler.scheduler.timezone}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 排程器測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_discord_notifier():
    """測試 Discord 通知器"""
    print_section("7. 測試 Discord 通知器")
    
    try:
        from src.discord_notifier import DiscordNotifier
        
        notifier = DiscordNotifier()
        print("[OK] DiscordNotifier 初始化成功")
        
        # 檢查是否有 webhook URL
        if hasattr(notifier, 'webhook_url') and notifier.webhook_url:
            print("[OK] Discord Webhook 已設定")
        else:
            print("[WARN] Discord Webhook 未設定(可選)")
        
        return True
    except Exception as e:
        print(f"[FAIL] Discord 通知器測試失敗: {e}")
        return False

def run_full_test():
    """執行完整測試"""
    print("\n" + "=" * 60)
    print("  539 AI 預測系統 - 完整流程測試")
    print("  測試時間:", get_taiwan_datetime_str())
    print("=" * 60)
    
    results = []
    
    # 執行各項測試
    results.append(("核心模組導入", test_imports()))
    results.append(("資料檔案檢查", test_data_files()))
    results.append(("時區設定", test_timezone()))
    results.append(("特徵引擎", test_feature_engine()))
    results.append(("增量訓練器", test_incremental_trainer()))
    results.append(("排程器配置", test_scheduler_config()))
    results.append(("Discord 通知器", test_discord_notifier()))
    
    # 總結
    print_section("測試總結")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("\n[SUCCESS] 所有測試通過!系統運作正常。")
        return 0
    else:
        print(f"\n[WARNING] 有 {total - passed} 項測試失敗,請檢查錯誤訊息。")
        return 1

if __name__ == "__main__":
    sys.exit(run_full_test())
