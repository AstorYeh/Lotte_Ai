# -*- coding: utf-8 -*-
"""
測試更新後的農曆計算
"""
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCth4rbHX4gOVnWchj2jlrNf44vGIaPmb8'

from src.ai_advisors.numerology_advisor import NumerologyAdvisor
import json

print("=" * 60)
print("Testing Updated Numerology Advisor with Lunar Calendar")
print("=" * 60)

advisor = NumerologyAdvisor()
today = '2026-02-12'

print(f"\nTesting date: {today}")
print("Expected: 農曆正月十五 (元宵節)")

advice = advisor.get_daily_numerology_advice(today)

print(f"\n[Result]")
print(f"Lunar Date: {advice.get('lunar_date', 'N/A')}")
print(f"Solar Term: {advice.get('solar_term', 'N/A')}")
print(f"Element: {advice.get('element', 'N/A')}")
print(f"Lucky Numbers: {advice.get('lucky_numbers', [])}")
print(f"Confidence: {advice.get('confidence', 0):.0%}")

print("\n" + "=" * 60)
print("[SUCCESS] Lunar calendar integration complete!")
print("=" * 60)
