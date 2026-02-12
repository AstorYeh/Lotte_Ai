# -*- coding: utf-8 -*-
"""
完整系統推送測試
"""
import os
import sys

# 設定 API Key
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCth4rbHX4gOVnWchj2jlrNf44vGIaPmb8'

print("=" * 60)
print("Complete System Push Test")
print("=" * 60)

# 測試 1: 命理專家建議 + Discord 推送
print("\n[Test 1] Numerology Advisor with Discord Push")
print("-" * 60)
try:
    from src.ai_advisors.numerology_advisor import NumerologyAdvisor
    from datetime import date
    
    advisor = NumerologyAdvisor()
    today = date.today().strftime('%Y-%m-%d')
    
    print(f"Getting numerology advice for {today}...")
    advice = advisor.get_daily_numerology_advice(today)
    
    print(f"Lucky Numbers: {advice.get('lucky_numbers', [])}")
    print(f"Element: {advice.get('element', 'N/A')}")
    print(f"Confidence: {advice.get('confidence', 0):.0%}")
    
    print("\nSending to Discord...")
    advisor.send_daily_numerology_report(today, advice)
    print("[SUCCESS] Numerology report sent to Discord!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# 測試 2: 驗證機制測試
print("\n[Test 2] Verification Mechanism")
print("-" * 60)
try:
    from src.multi_game_manager import MultiGameManager
    
    manager = MultiGameManager()
    
    # 檢查數據同步
    print("Checking data sync...")
    sync_status = manager.check_data_sync('539')
    print(f"539 synced: {sync_status.get('synced', False)}")
    print(f"Latest date: {sync_status.get('latest_date', 'N/A')}")
    
    # 執行驗證
    print("\nRunning verification...")
    results = manager.verify_all_predictions()
    
    verified_count = sum(r.get('verified', 0) for r in results.values())
    print(f"Total verified: {verified_count}")
    
    # 發送驗證摘要
    if results:
        print("\nSending verification summary to Discord...")
        manager.send_verification_summary(results)
        print("[SUCCESS] Verification summary sent!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# 測試 3: 預測管理器統計
print("\n[Test 3] Prediction Manager Stats")
print("-" * 60)
try:
    from src.prediction_manager import prediction_manager
    
    stats = prediction_manager.get_all_stats(days=30)
    print(f"Games tracked: {len(stats)}")
    
    for game, stat in stats.items():
        if stat.get('verified', 0) > 0:
            print(f"{game}: {stat['verified']} verified, avg accuracy: {stat.get('avg_accuracy', 0):.1%}")
    
    print("[SUCCESS] Stats retrieved!")
    
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 60)
print("Push Test Complete!")
print("=" * 60)
print("\nPlease check your Discord channel for:")
print("1. Numerology advice report")
print("2. Verification summary")
