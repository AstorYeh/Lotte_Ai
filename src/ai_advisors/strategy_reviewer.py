# -*- coding: utf-8 -*-
"""
策略審查助手 - 第三方策略監督
"""
import json
import os
from pathlib import Path
from typing import Dict
from google import genai
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_isoformat


class StrategyReviewer:
    """策略審查助手 - 第三方監督機制"""
    
    def __init__(self):
        self.discord = DiscordNotifier()
        self.llm_client = self._init_gemini_client()
    
    def _init_gemini_client(self):
        """初始化 Gemini API 客戶端"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("[WARNING] GOOGLE_API_KEY not set, Strategy Reviewer disabled")
            return None
        
        return genai.Client(api_key=api_key)
    
    def analyze_strategy_health(self, game: str, recent_accuracy: float, 
                                current_config: Dict) -> Dict:
        """分析策略健康狀態"""
        if not self.llm_client:
            return {'health_score': 75, 'note': 'LLM analysis skipped'}
        
        try:
            prompt = f"""
你是一個專業的彩票預測策略分析師。請分析以下策略的健康狀態:

遊戲: {game}
最近命中率: {recent_accuracy:.1%}
當前配置: {json.dumps(current_config, indent=2, ensure_ascii=False)}

請提供:
1. 策略健康評分 (0-100)
2. 主要問題識別
3. 風險評估
4. 改進建議

以 JSON 格式回應:
{{
  "health_score": 75,
  "main_issues": ["問題1", "問題2"],
  "risk_level": "medium",
  "improvement_suggestions": ["建議1", "建議2"]
}}
"""
            
            response = self.llm_client.generate_content(prompt)
            
            # 解析 JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response.text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return {'health_score': 75, 'note': 'Unable to parse response'}
                
        except Exception as e:
            print(f"[ERROR] Strategy analysis failed: {e}")
            return {'health_score': 75, 'error': str(e)}
    
    def run_weekly_review(self, games_data: Dict) -> Dict:
        """執行每週審查"""
        print("\n[Strategy Reviewer] Starting weekly review...")
        
        reviews = {}
        critical_games = []
        
        for game, data in games_data.items():
            analysis = self.analyze_strategy_health(
                game,
                data.get('recent_accuracy', 0),
                data.get('config', {})
            )
            
            reviews[game] = analysis
            
            # 檢查是否需要警報
            if analysis.get('health_score', 100) < 60:
                critical_games.append(game)
        
        # 生成報告
        report = {
            'timestamp': get_taiwan_isoformat(),
            'reviews': reviews,
            'critical_games': critical_games
        }
        
        # 發送警報
        if critical_games:
            self._send_review_alert(report)
        
        return report
    
    def _send_review_alert(self, report: Dict):
        """發送審查警報"""
        critical_games = report['critical_games']
        
        embed = {
            "title": "🤖 AI 策略審查報告",
            "description": f"發現 {len(critical_games)} 個遊戲需要關注",
            "color": 0xFF6B00,  # 橘色
            "fields": [],
            "timestamp": get_taiwan_isoformat(),
            "footer": {"text": "AI 策略審查助手 | 第三方監督"}
        }
        
        for game in critical_games[:3]:
            review = report['reviews'][game]
            embed['fields'].append({
                "name": f"⚠️ {game.upper()}",
                "value": f"健康評分: {review.get('health_score', 'N/A')}/100",
                "inline": True
            })
        
        payload = {
            "username": "AI 策略審查助手",
            "embeds": [embed]
        }
        
        self.discord._send_webhook(payload)


if __name__ == "__main__":
    reviewer = StrategyReviewer()
    test_data = {
        '539': {
            'recent_accuracy': 0.15,
            'config': {'weights': {}}
        }
    }
    result = reviewer.run_weekly_review(test_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
