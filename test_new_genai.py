# -*- coding: utf-8 -*-
"""
測試新版 Google GenAI API
"""
import os

# 設定 API Key
os.environ['GOOGLE_API_KEY'] = 'AIzaSyCth4rbHX4gOVnWchj2jlrNf44vGIaPmb8'

print("=" * 60)
print("Testing New Google GenAI API")
print("=" * 60)

# 測試新版 API
print("\n[Test] Using new google.genai package")
print("-" * 60)
try:
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
    
    print("Client created successfully")
    
    # 測試簡單的生成
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='請用繁體中文回答:今天是2026年2月12日,請提供3個幸運數字(1-39之間)。'
    )
    
    print(f"\nResponse: {response.text[:200]}")
    print("\n[SUCCESS] New API works!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
