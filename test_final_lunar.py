# -*- coding: utf-8 -*-
"""
最終農曆測試並發送到 Discord
"""
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCth4rbHX4gOVnWchj2jlrNf44vGIaPmb8'

from src.ai_advisors.numerology_advisor import NumerologyAdvisor
from datetime import date

print("=" * 60)
print("Final Lunar Calendar Test & Discord Push")
print("=" * 60)

advisor = NumerologyAdvisor()
today = date.today().strftime('%Y-%m-%d')

print(f"\nDate: {today}")
advice = advisor.get_daily_numerology_advice(today)

print(f"\n[Result]")
print(f"Lunar Date: {advice.get('lunar_date', 'N/A')}")
print(f"Element: {advice.get('element', 'N/A')}")
print(f"Lucky Numbers: {advice.get('lucky_numbers', [])}")
print(f"Confidence: {advice.get('confidence', 0):.0%}")

print(f"\nSending to Discord...")
advisor.send_daily_numerology_report(today, advice)

print("\n" + "=" * 60)
print("[SUCCESS] Please check Discord for the updated report!")
print("Expected: 農曆臘月廿五")
print("=" * 60)
