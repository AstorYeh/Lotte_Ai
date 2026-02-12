# -*- coding: utf-8 -*-
"""
AI 分身助手 - 模擬用戶思維的決策顧問
"""
import json
import os
from pathlib import Path
from typing import Dict
from google import genai
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_isoformat


class DigitalTwinAdvisor:
    """AI 分身 - 模擬用戶思維的決策顧問"""
    
    def __init__(self):
        self.discord = DiscordNotifier()
        self.llm_client = self._init_gemini_client()
        self.user_profile = self._load_user_profile()
    
    def _init_gemini_client(self):
        """初始化 Gemini API 客戶端"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("[WARNING] GOOGLE_API_KEY not set, Digital Twin disabled")
            return None
        
        return genai.Client(api_key=api_key)
    
    def _load_user_profile(self) -> Dict:
        """載入用戶思維檔案"""
        profile_file = Path('config/user_profile.json')
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 預設檔案
        return {
            'decision_style': 'analytical',
            'risk_tolerance': 'moderate',
            'priority': 'long_term_stability'
        }
    
    def review_system_decisions(self, decisions: Dict) -> Dict:
        """審查系統決策,提供用戶視角的批判性意見"""
        if not self.llm_client:
            return {'overall_assessment': 'approve', 'note': 'LLM review skipped'}
        
        try:
            prompt = f"""
你是用戶的 AI 分身,現在要審查系統提出的決策建議。

**用戶特質**:
- 決策風格: {self.user_profile.get('decision_style')}
- 風險容忍度: {self.user_profile.get('risk_tolerance')}
- 優先考量: {self.user_profile.get('priority')}

**系統決策**:
{json.dumps(decisions, indent=2, ensure_ascii=False)}

請以用戶的批判性思維審查:

1. **合理性檢查**: 這些決策符合常識和邏輯嗎?
2. **風險評估**: 有哪些潛在風險被忽略了?
3. **替代觀點**: 從不同角度看,有什麼問題?
4. **改進建議**: 如何讓決策更穩健?
5. **紅旗警示**: 有什麼需要立即注意的問題?

以 JSON 格式回應:
{{
  "overall_assessment": "approve",
  "strengths": ["優點1", "優點2"],
  "weaknesses": ["缺點1"],
  "red_flags": [],
  "improvement_suggestions": ["建議1"],
  "final_recommendation": "建議繼續執行"
}}
"""
            
            response = self.llm_client.generate_content(prompt)
            
            # 解析 JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response.text, re.DOTALL)
            if json_match:
                review = json.loads(json_match.group())
                return review
            else:
                return {'overall_assessment': 'approve', 'note': 'Unable to parse response'}
                
        except Exception as e:
            print(f"[ERROR] Digital Twin review failed: {e}")
            return {'overall_assessment': 'approve', 'error': str(e)}
    
    def daily_strategic_review(self, context: Dict) -> Dict:
        """每日策略性審查"""
        print("\n[Digital Twin] Starting daily strategic review...")
        
        # 審查系統決策
        review = self.review_system_decisions(context)
        
        # 生成報告
        report = {
            'timestamp': get_taiwan_isoformat(),
            'decision_review': review
        }
        
        # 如果有重要發現,發送通知
        if review.get('overall_assessment') == 'concern' or review.get('red_flags'):
            self._send_twin_alert(report)
        
        return report
    
    def _send_twin_alert(self, report: Dict):
        """發送 AI 分身的警示"""
        review = report['decision_review']
        
        assessment_emoji = {
            'approve': '✅',
            'concern': '⚠️',
            'reject': '❌'
        }
        emoji = assessment_emoji.get(review.get('overall_assessment', 'approve'), '❓')
        
        embed = {
            "title": "🧠 AI 分身策略審查",
            "description": "您的 AI 分身發現了需要注意的事項",
            "color": 0x3498DB,  # 藍色
            "fields": [
                {
                    "name": f"{emoji} 整體評估",
                    "value": review.get('overall_assessment', 'N/A').upper(),
                    "inline": True
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {"text": "AI Digital Twin | 模擬您的思維"}
        }
        
        # 添加紅旗警示
        if review.get('red_flags'):
            embed['fields'].append({
                "name": "🚩 需要注意",
                "value": "\n".join([f"• {flag}" for flag in review['red_flags'][:3]]),
                "inline": False
            })
        
        # 添加改進建議
        if review.get('improvement_suggestions'):
            embed['fields'].append({
                "name": "💡 改進建議",
                "value": "\n".join([f"• {sug}" for sug in review['improvement_suggestions'][:2]]),
                "inline": False
            })
        
        payload = {
            "username": "AI 分身助手",
            "embeds": [embed]
        }
        
        self.discord._send_webhook(payload)


if __name__ == "__main__":
    twin = DigitalTwinAdvisor()
    test_context = {
        'recent_accuracy': 0.18,
        'pending_adjustments': True,
        'system_health': 'good'
    }
    result = twin.daily_strategic_review(test_context)
    print(json.dumps(result, indent=2, ensure_ascii=False))
