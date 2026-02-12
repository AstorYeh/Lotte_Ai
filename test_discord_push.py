# -*- coding: utf-8 -*-
"""
測試 Discord 號碼推送功能
"""
from src.discord_notifier import DiscordNotifier
from datetime import datetime, timedelta

print("=" * 60)
print("Discord 號碼推送測試")
print("=" * 60)

# 初始化通知器
notifier = DiscordNotifier()

# 測試 1: 基本連線測試
print("\n[Test 1] Basic connection test...")
result1 = notifier.send_test_message()
print(f"Result: {'SUCCESS' if result1 else 'FAILED'}")

# 測試 2: 單組號碼推送
print("\n[Test 2] Single number set push...")
test_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %A')
test_numbers = [3, 12, 18, 25, 33]
backtest = {
    'date': '2026-02-11',
    'actual': [5, 12, 19, 28, 35],
    'predicted': [3, 12, 18, 25, 33],
    'hits': [12],
    'accuracy': 0.2
}

result2 = notifier.send_prediction_result(
    prediction_date=test_date,
    predicted_numbers=test_numbers,
    backtest_result=backtest
)
print(f"Result: {'SUCCESS' if result2 else 'FAILED'}")

# 測試 3: 多組號碼推送 (5組策略)
print("\n[Test 3] Multiple number sets push (5 strategies)...")
test_numbers_multi = [
    [2, 8, 15, 23, 31],   # 策略一
    [1, 9, 17, 25, 33],   # 策略二
    [5, 12, 19, 26, 35],  # 策略三
    [3, 11, 18, 27, 36],  # 策略四
    [7, 14, 21, 28, 38]   # 策略五
]

result3 = notifier.send_prediction_result(
    prediction_date=test_date,
    predicted_numbers=test_numbers_multi,
    backtest_result=backtest
)
print(f"Result: {'SUCCESS' if result3 else 'FAILED'}")

# 測試 4: 驗證結果推送
print("\n[Test 4] Verification result push...")
result4 = notifier.send_verification_result(
    prediction_date='2026-02-11 Tuesday',
    predicted_numbers=[3, 12, 18, 25, 33],
    actual_numbers=[5, 12, 19, 28, 33],
    hits=[12, 33],
    accuracy=0.4
)
print(f"Result: {'SUCCESS' if result4 else 'FAILED'}")

# 測試 5: 訓練報告推送
print("\n[Test 5] Training report push...")
result5 = notifier.send_training_report(
    training_periods=50,
    avg_accuracy=0.28,
    improvements={
        'Hit Rate Improvement': 0.05,
        'Zero Hit Reduction': -0.15
    }
)
print(f"Result: {'SUCCESS' if result5 else 'FAILED'}")

# 測試 6: 資料更新報告
print("\n[Test 6] Data update report...")
result6 = notifier.send_update_report({
    '539': 3,
    'lotto': 2,
    'power': 1,
    'star3': 0,
    'star4': 0
})
print(f"Result: {'SUCCESS' if result6 else 'FAILED'}")

print("\n" + "=" * 60)
print("Test completed! Please check your Discord channel")
print("=" * 60)

# 統計結果
results = [result1, result2, result3, result4, result5, result6]
success_count = sum(results)
print(f"\nTotal: {success_count}/{len(results)} tests passed")
