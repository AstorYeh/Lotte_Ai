"""
LLM 顧問模組
使用 Gemini 作為第八個模型維度,提供選號建議
"""
import json
import time
import google.generativeai as genai
from src.api_key_manager import api_key_manager
from src.logger import logger
from src.api_quota_config import API_QUOTA_CONFIG, DAILY_USAGE
from src.timezone_utils import get_taiwan_now
import os

class LLMAdvisor:
    """LLM 顧問 - 使用 Gemini 提供選號建議"""
    
    def __init__(self):
        """初始化 LLM"""
        # 使用新的 API Key
        api_key = API_QUOTA_CONFIG['api_key']
        
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            self.model = None
            logger.warning("LLM 顧問未啟用 (缺少 API Key)")
            return
        
        try:
            genai.configure(api_key=api_key)
            # 使用免費版模型
            self.model = genai.GenerativeModel(
                API_QUOTA_CONFIG['model'],
                generation_config={
                    'max_output_tokens': API_QUOTA_CONFIG['max_output_tokens'],
                    'temperature': API_QUOTA_CONFIG['temperature']
                }
            )
            logger.info(f"LLM 顧問已啟用 ({API_QUOTA_CONFIG['model']})")
        except Exception as e:
            self.model = None
            logger.error(f"LLM 初始化失敗: {e}")
    
    def _check_quota(self):
        """檢查每日配額"""
        today = get_taiwan_now().strftime('%Y-%m-%d')
        
        # 重置每日計數
        if DAILY_USAGE['date'] != today:
            DAILY_USAGE['date'] = today
            DAILY_USAGE['requests'] = 0
            DAILY_USAGE['tokens_used'] = 0
        
        # 檢查是否超過每日限制
        if DAILY_USAGE['requests'] >= API_QUOTA_CONFIG['daily_limit']:
            logger.warning(f"已達每日配額限制 ({API_QUOTA_CONFIG['daily_limit']})")
            return False
        
        return True
    
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
        
        # 檢查配額
        if not self._check_quota():
            if API_QUOTA_CONFIG['fallback_to_default']:
                return {
                    'numbers': [],
                    'confidence': 0.5,
                    'reason': '配額已用完'
                }
            return None
        
        try:
            # 加入延遲以避免超過 RPM
            time.sleep(API_QUOTA_CONFIG['request_delay'])
            
            prompt = self._build_prompt(group_id, group_range, historical_stats, model_scores)
            
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            # 更新配額使用
            DAILY_USAGE['requests'] += 1
            
            logger.debug(f"LLM 建議 ({group_id}): {result}")
            return result
            
        except Exception as e:
            logger.error(f"LLM 建議失敗 ({group_id}): {e}")
            if API_QUOTA_CONFIG['fallback_to_default']:
                return {
                    'numbers': [],
                    'confidence': 0.5,
                    'reason': f'錯誤: {str(e)[:50]}'
                }
            return None
    
    def _build_prompt(self, group_id, group_range, historical_stats, model_scores):
        """建立精簡 LLM prompt"""
        
        # 只取前 3 名以節省 tokens
        top_scores = {}
        for model_name, scores in model_scores.items():
            if isinstance(scores, dict):
                sorted_scores = sorted(scores.items(), key=lambda x: float(x[1]) if isinstance(x[1], (int, float, str)) else 0, reverse=True)[:3]
                top_scores[model_name] = {num: f"{float(score):.2f}" for num, score in sorted_scores}
        
        # 精簡提示詞
        prompt = f"""分析 539 彩券 {group_id} ({group_range[0]}-{group_range[1]})。

模型評分(前3):
{json.dumps(top_scores, ensure_ascii=False)}

建議0-3個號碼,優先選多模型看好的。

JSON格式回答:
{{"numbers": [5,8], "confidence": 0.78, "reason": "簡短理由"}}
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
