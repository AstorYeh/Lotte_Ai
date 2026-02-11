# -*- coding: utf-8 -*-
"""
多遊戲預測系統 - 測試腳本
快速測試所有遊戲的預測功能
"""
from src.multi_game_manager import MultiGameManager

print("=" * 80)
print("多遊戲預測系統 - 完整測試")
print("=" * 80)

# 初始化管理器
manager = MultiGameManager()

# 生成所有預測
results = manager.generate_all_predictions()

# 顯示結果
print("\n" + "=" * 80)
print("預測結果摘要")
print("=" * 80)

for game, data in results.items():
    if game == '539':
        print(f"\n[539] 今彩539")
        print(f"  日期: {data.get('prediction_date', 'N/A')}")
        print(f"  組數: {data.get('num_sets', 0)}")
    elif game == 'lotto':
        print(f"\n[大樂透]")
        print(f"  日期: {data['date']}")
        print(f"  組數: {len(data['predictions'])}")
        for i, nums in enumerate(data['predictions'][:2], 1):
            print(f"    第{i}組: {nums}")
    elif game == 'power':
        print(f"\n[威力彩]")
        print(f"  日期: {data['date']}")
        print(f"  組數: {len(data['predictions'])}")
        for i, pred in enumerate(data['predictions'][:2], 1):
            print(f"    第{i}組: 第一區{pred['zone1']} + 第二區{pred['zone2']}")
    elif game == 'star3':
        print(f"\n[3星彩]")
        print(f"  日期: {data['date']}")
        print(f"  組數: {len(data['predictions'])}")
        print(f"    範例: {', '.join(data['predictions'][:3])}")
    elif game == 'star4':
        print(f"\n[4星彩]")
        print(f"  日期: {data['date']}")
        print(f"  組數: {len(data['predictions'])}")
        print(f"    範例: {', '.join(data['predictions'][:3])}")

# 推送到 Discord
print("\n" + "=" * 80)
print("推送到 Discord")
print("=" * 80)
manager.send_all_predictions(results)

print("\n" + "=" * 80)
print("測試完成!")
print("=" * 80)
print(f"總共 {len(results)} 個遊戲")
print("請檢查 Discord 頻道確認推送結果")
