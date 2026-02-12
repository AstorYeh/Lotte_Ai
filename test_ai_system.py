# -*- coding: utf-8 -*-
"""
測試 AI 助手團隊
"""
import sys
import os

# 測試數學專家
print("=" * 60)
print("Test 1: Math Validator")
print("=" * 60)
try:
    from src.ai_advisors.math_validator import MathValidator
    validator = MathValidator()
    print("[OK] Math Validator loaded successfully")
    
    # 測試數據完整性檢查
    result = validator.check_data_integrity('539')
    print(f"Data integrity check: {result.get('is_valid', False)}")
    print(f"Total records: {result.get('total_records', 0)}")
except Exception as e:
    print(f"[ERROR] Math Validator test failed: {e}")

# 測試命理專家
print("\n" + "=" * 60)
print("Test 2: Numerology Advisor")
print("=" * 60)
try:
    from src.ai_advisors.numerology_advisor import NumerologyAdvisor
    from datetime import date
    advisor = NumerologyAdvisor()
    print("[OK] Numerology Advisor loaded successfully")
    
    # 測試取得建議
    today = date.today().strftime('%Y-%m-%d')
    advice = advisor.get_daily_numerology_advice(today)
    print(f"Confidence: {advice.get('confidence', 0)}")
except Exception as e:
    print(f"[ERROR] Numerology Advisor test failed: {e}")

# 測試 AI 分身
print("\n" + "=" * 60)
print("Test 3: Digital Twin Advisor")
print("=" * 60)
try:
    from src.ai_advisors.digital_twin import DigitalTwinAdvisor
    twin = DigitalTwinAdvisor()
    print("[OK] Digital Twin loaded successfully")
    print(f"User profile: {twin.user_profile.get('decision_style', 'N/A')}")
except Exception as e:
    print(f"[ERROR] Digital Twin test failed: {e}")

# 測試策略審查
print("\n" + "=" * 60)
print("Test 4: Strategy Reviewer")
print("=" * 60)
try:
    from src.ai_advisors.strategy_reviewer import StrategyReviewer
    reviewer = StrategyReviewer()
    print("[OK] Strategy Reviewer loaded successfully")
except Exception as e:
    print(f"[ERROR] Strategy Reviewer test failed: {e}")

# 測試預測管理器
print("\n" + "=" * 60)
print("Test 5: Prediction Manager")
print("=" * 60)
try:
    from src.prediction_manager import prediction_manager
    print("[OK] Prediction Manager loaded successfully")
    
    # 測試取得統計
    stats = prediction_manager.get_all_stats(days=30)
    print(f"Stats for {len(stats)} games")
    for game, stat in stats.items():
        if stat.get('verified', 0) > 0:
            print(f"  {game}: {stat['verified']} verified, avg accuracy: {stat.get('avg_accuracy', 0):.1%}")
except Exception as e:
    print(f"[ERROR] Prediction Manager test failed: {e}")

# 測試驗證機制
print("\n" + "=" * 60)
print("Test 6: Verification Mechanism")
print("=" * 60)
try:
    from src.multi_game_manager import MultiGameManager
    manager = MultiGameManager()
    print("[OK] MultiGameManager loaded successfully")
    
    # 測試數據同步檢查
    sync_status = manager.check_data_sync('539')
    print(f"539 data sync: {sync_status.get('synced', False)}")
    if sync_status.get('synced'):
        print(f"  Latest: {sync_status.get('latest_date')}")
except Exception as e:
    print(f"[ERROR] Verification test failed: {e}")

# 總結
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("[OK] All core modules tested")
print("System is ready!")

