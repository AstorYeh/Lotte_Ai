"""
LLM 顧問模組
使用 Gemini 作為第八個模型維度,提供選號建議
"""
import json
import google.generativeai as genai
from src.api_key_manager import api_key_manager
from src.logger import logger
import os

class LLMAdvisor:
    """LLM 顧問 - 使用 Gemini 提供選號建議"""
    
    def __init__(self):
        """初始化 LLM"""
        # 從 API Key Manager 讀取
        api_key = api_key_manager.load_api_key("google_gemini")
        
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            self.model = None
            logger.warning("LLM 顧問未啟用 (缺少 API Key)")
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')  # Gemini 2.5 Pro
            logger.info("LLM 顧問已啟用 (Gemini 2.0 Flash)")
        except Exception as e:
            self.model = None
            logger.error(f"LLM 初始化失敗: {e}")
    
    def get_group_advice(self, group_id, group_range, historical_stats, model_scores):
        """
        取得單一群組的 LLM 建議
        
        Args:
            group_id: 群組 ID (group1-4)
            group_range: 群組範圍 (1, 10)
            historical_stats: 歷史統計資料
            model_scores: 七大模型的評分
        
        Returns:
            dict: {
                'numbers': [5, 8],
                'confidence': 0.78,
                'reason': '...'
            }
        """
        if not self.model:
            return None
        
        try:
            prompt = self._build_prompt(group_id, group_range, historical_stats, model_scores)
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            logger.debug(f"LLM 建議 ({group_id}): {result}")
            return result
            
        except Exception as e:
            logger.error(f"LLM 建議失敗 ({group_id}): {e}")
            return None
    
    def _build_prompt(self, group_id, group_range, historical_stats, model_scores):
        """建立 LLM prompt"""
        
        # 格式化模型評分 (取前 5 名)
        top_scores = {}
        for model_name, scores in model_scores.items():
            if isinstance(scores, dict):
                sorted_scores = sorted(scores.items(), key=lambda x: float(x[1]) if isinstance(x[1], (int, float, str)) else 0, reverse=True)[:5]
                top_scores[model_name] = {num: str(score) if isinstance(score, str) else f"{float(score):.2f}" for num, score in sorted_scores}
        
        prompt = f"""你是 539 彩券分析專家。請分析以下資料並給出選號建議。

## 群組資訊
- 群組: {group_id}
- 號碼範圍: {group_range[0]}-{group_range[1]}
- 可選號碼數: 0-3 顆 (動態調整,不強制)

## 歷史統計 (最近 30 期)
{json.dumps(historical_stats, indent=2, ensure_ascii=False)}

## 七大模型評分 (前 5 名)
{json.dumps(top_scores, indent=2, ensure_ascii=False)}

## 請回答
1. 建議選出幾顆號碼? (0-3 顆,根據機率決定)
2. 具體建議哪些號碼?
3. 信心度評分 (0-1,小數點後兩位)
4. 簡短理由 (一句話)

**重要**: 
- 如果該群組沒有明顯的高機率號碼,可以選 0 顆
- 不要強制湊數,寧缺勿濫
- 優先考慮多個模型都看好的號碼

請以 JSON 格式回答:
{{
  "numbers": [5, 8],
  "confidence": 0.78,
  "reason": "號碼 5 和 8 在頻率與 RSI 模型中都排名前列"
}}

如果建議選 0 顆,請回答:
{{
  "numbers": [],
  "confidence": 0.5,
  "reason": "該群組無明顯高機率號碼"
}}
"""
        return prompt
    
    def _parse_response(self, response_text):
        """解析 LLM 回應"""
        try:
            # 嘗試提取 JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                
                # 驗證格式
                if 'numbers' in result and 'confidence' in result:
                    return {
                        'numbers': result.get('numbers', []),
                        'confidence': float(result.get('confidence', 0.5)),
                        'reason': result.get('reason', '')
                    }
            
            # 解析失敗,返回預設值
            logger.warning(f"LLM 回應解析失敗: {response_text[:100]}")
            return {
                'numbers': [],
                'confidence': 0.5,
                'reason': 'LLM 回應格式錯誤'
            }
            
        except Exception as e:
            logger.error(f"LLM 回應解析錯誤: {e}")
            return {
                'numbers': [],
                'confidence': 0.5,
                'reason': f'解析錯誤: {e}'
            }
    
    def get_all_groups_advice(self, groups_data):
        """
        取得所有群組的 LLM 建議
        
        Args:
            groups_data: {
                'group1': {'range': (1,10), 'stats': {...}, 'scores': {...}},
                ...
            }
        
        Returns:
            dict: {'group1': {...}, 'group2': {...}, ...}
        """
        if not self.model:
            return {}
        
        all_advice = {}
        
        for group_id, data in groups_data.items():
            advice = self.get_group_advice(
                group_id,
                data['range'],
                data.get('stats', {}),
                data.get('scores', {})
            )
            
            if advice:
                all_advice[group_id] = advice
        
        return all_advice

if __name__ == "__main__":
    # 測試
    advisor = LLMAdvisor()
    
    if advisor.model:
        # 模擬資料
        test_stats = {
            "avg_frequency": {"5": 0.15, "8": 0.12},
            "recent_trend": "上升"
        }
        
        test_scores = {
            "freq": {5: 0.85, 8: 0.72, 3: 0.65},
            "rsi": {5: 0.90, 8: 0.75, 2: 0.65}
        }
        
        advice = advisor.get_group_advice(
            "group1",
            (1, 10),
            test_stats,
            test_scores
        )
        
        logger.info(f"LLM 建議: {advice}")
    else:
        logger.warning("LLM 測試跳過 (未設定 API Key)")
