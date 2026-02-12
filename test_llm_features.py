# -*- coding: utf-8 -*-
"""
測試 AI 助手的 LLM 功能
"""
import os

# 設定 API Key
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBJROn-8cBV0UDhJ0SuqfvqafzjGwBzlXw'

print("=" * 60)
print("Testing AI Advisors with LLM")
print("=" * 60)

# 測試命理專家的 LLM 功能
print("\n[Test 1] Numerology Advisor with LLM")
print("-" * 60)
try:
    from src.ai_advisors.numerology_advisor import NumerologyAdvisor
    from datetime import date
    
    advisor = NumerologyAdvisor()
    today = date.today().strftime('%Y-%m-%d')
    
    print(f"Getting numerology advice for {today}...")
    advice = advisor.get_daily_numerology_advice(today)
    
    print(f"\nLunar Date: {advice.get('lunar_date', 'N/A')}")
    print(f"Element: {advice.get('element', 'N/A')}")
    print(f"Lucky Numbers: {advice.get('lucky_numbers', [])}")
    print(f"Confidence: {advice.get('confidence', 0):.0%}")
    print(f"Explanation: {advice.get('explanation', 'N/A')[:100]}...")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# 測試 AI 分身的決策審查
print("\n[Test 2] Digital Twin Decision Review")
print("-" * 60)
try:
    from src.ai_advisors.digital_twin import DigitalTwinAdvisor
    
    twin = DigitalTwinAdvisor()
    
    test_decisions = {
        'recent_accuracy': 0.18,
        'strategy': 'ensemble',
        'pending_adjustments': True
    }
    
    print("Reviewing system decisions...")
    review = twin.review_system_decisions(test_decisions)
    
    print(f"\nOverall Assessment: {review.get('overall_assessment', 'N/A')}")
    print(f"Strengths: {review.get('strengths', [])[:2]}")
    print(f"Weaknesses: {review.get('weaknesses', [])[:2]}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("LLM Testing Complete!")
print("=" * 60)
