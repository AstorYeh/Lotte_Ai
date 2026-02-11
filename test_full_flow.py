# -*- coding: utf-8 -*-
"""
完整測試流程:驗證 + 預測
"""
from src.auto_predictor import AutoPredictor

print("=" * 60)
print("Full Test: Verification + Prediction")
print("=" * 60)

predictor = AutoPredictor()

# 步驟 1: 驗證待驗證的預測
print("\n[Step 1] Verifying pending prediction...")
verify_result = predictor.verify_pending_prediction()

if verify_result:
    print("\n[SUCCESS] Verification completed!")
    print(f"   Date: {verify_result['prediction_date']}")
    print(f"   Accuracy: {verify_result['accuracy']:.0%}")
    print(f"   Hits: {len(verify_result['hits'])}/5")
else:
    print("\n[WARNING] No pending prediction or verification failed")

# 步驟 2: 生成新預測
print("\n" + "=" * 60)
print("[Step 2] Generating new prediction...")
print("=" * 60)

predict_result = predictor.generate_new_prediction()

if predict_result:
    print("\n" + "=" * 60)
    print("[SUCCESS] Prediction completed!")
    print("=" * 60)
    print(f"Date: {predict_result['prediction_date']}")
    print(f"Number of sets: {predict_result['num_sets']}")
    print("\nPredicted numbers:")
    for i, nums in enumerate(predict_result['predicted_numbers'], 1):
        print(f"  Set {i}: {nums}")
    
    if predict_result.get('backtest_result'):
        bt = predict_result['backtest_result']
        print(f"\nBacktest: {len(bt.get('hits', []))}/5 ({bt.get('accuracy', 0):.0%})")
else:
    print("\n[ERROR] Prediction generation failed")
