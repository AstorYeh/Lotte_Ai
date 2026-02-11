# -*- coding: utf-8 -*-
"""
測試預測推送
"""
from src.auto_predictor import AutoPredictor

print("=" * 60)
print("Testing Prediction Generation & Discord Push")
print("=" * 60)

predictor = AutoPredictor()
result = predictor.generate_new_prediction()

if result:
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("=" * 60)
    print(f"Date: {result['prediction_date']}")
    print(f"Number of sets: {result['num_sets']}")
    print("\nPredicted numbers:")
    for i, nums in enumerate(result['predicted_numbers'], 1):
        print(f"  Set {i}: {nums}")
    
    if result.get('backtest_result'):
        bt = result['backtest_result']
        print(f"\nBacktest: {len(bt.get('hits', []))}/5 ({bt.get('accuracy', 0):.0%})")
else:
    print("\n[FAILED] Prediction generation failed")
