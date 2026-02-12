# -*- coding: utf-8 -*-
"""
測試更新後的命理專家
"""
import os
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCth4rbHX4gOVnWchj2jlrNf44vGIaPmb8'

from src.ai_advisors.numerology_advisor import NumerologyAdvisor
from datetime import date
import json

print("=" * 60)
print("Testing Updated Numerology Advisor")
print("=" * 60)

advisor = NumerologyAdvisor()
today = date.today().strftime('%Y-%m-%d')

print(f"\nGetting advice for {today}...")
advice = advisor.get_daily_numerology_advice(today)

print("\n[Result]")
print(json.dumps(advice, indent=2, ensure_ascii=False))

print("\n" + "=" * 60)
