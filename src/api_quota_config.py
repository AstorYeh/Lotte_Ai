# -*- coding: utf-8 -*-
"""
API 配額優化配置
免費版 Gemini API 限制管理
"""

# 免費版限制 (Gemini 2.5 Flash)
# RPM (Requests Per Minute): 15
# TPM (Tokens Per Minute): 1,000,000
# RPD (Requests Per Day): 1,500

API_QUOTA_CONFIG = {
    # API Key
    'api_key': 'AIzaSyBdVEYHYD91Nice77gJ04gHE37Z-BCX8Og',
    
    # 模型選擇 (免費版使用 Flash)
    'model': 'gemini-2.0-flash-exp',  # 更快,更省配額
    
    # 請求延遲 (秒)
    'request_delay': 5,  # 每次請求間隔5秒,避免超過 RPM
    
    # 每日請求限制 (此專案僅用 40% 配額)
    'daily_limit': 40,  # 40% 配額,其他專案使用 60%
    
    # Token 優化
    'max_output_tokens': 300,  # 進一步限制輸出長度 (500→300)
    'temperature': 0.2,  # 更低溫度,更精簡 (0.3→0.2)
    
    # 提示詞優化
    'use_concise_prompts': True,  # 使用精簡提示詞
    'strip_examples': True,  # 移除範例以節省 tokens
    
    # 快取策略
    'cache_responses': True,  # 快取相同日期的回應
    'cache_duration_hours': 24,
    
    # 錯誤處理
    'retry_on_quota_error': False,  # 配額錯誤不重試
    'fallback_to_default': True  # 配額用完時使用預設值
}

# 每日配額追蹤
DAILY_USAGE = {
    'date': None,
    'requests': 0,
    'tokens_used': 0
}
