# -*- coding: utf-8 -*-
"""
測試命理專家的農曆日期準確性
"""
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCth4rbHX4gOVnWchj2jlrNf44vGIaPmb8'

from src.ai_advisors.numerology_advisor import NumerologyAdvisor
from datetime import date
import json

print("=" * 60)
print("Testing Lunar Date Accuracy")
print("=" * 60)

advisor = NumerologyAdvisor()
today = '2026-02-12'

print(f"\nTesting date: {today}")
print("Expected: 農曆正月十五 (元宵節)")

advice = advisor.get_daily_numerology_advice(today)

print(f"\nLLM returned:")
print(f"  Lunar Date: {advice.get('lunar_date', 'N/A')}")
print(f"  Solar Term: {advice.get('solar_term', 'N/A')}")
print(f"  Element: {advice.get('element', 'N/A')}")

# 檢查是否需要使用專門的農曆庫
print("\n" + "-" * 60)
print("Suggestion: Consider using 'lunarcalendar' or 'borax' library")
print("for accurate lunar date calculation")
print("=" * 60)
