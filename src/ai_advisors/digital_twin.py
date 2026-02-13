# -*- coding: utf-8 -*-
"""
AI 分身助手 - 模擬用戶思維審查決策
使用規則引擎,不依賴 LLM
"""
import json
from pathlib import Path
from typing import Dict, List
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_isoformat


class DigitalTwinAdvisor:
    """AI 分身 - 審查預測決策 (規則引擎)"""
    
    def __init__(self):
        """初始化 AI 分身"""
        self.discord = DiscordNotifier()
        self.user_profile = self._load_user_profile()
        print("[INFO] AI 分身已啟用 (規則引擎模式,不使用 LLM)")
    
    def _load_user_profile(self) -> Dict:
        """載入用戶檔案"""
        profile_path = Path('config/user_profile.json')
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'risk_tolerance': 'moderate',
            'preferences': {
                'avoid_consecutive': True,
                'prefer_balanced': True
            }
        }
    
    def review_prediction(self, game: str, prediction: Dict) -> Dict:
        """
        審查預測決策 (使用規則引擎)
        
        Args:
            game: 遊戲名稱
            prediction: 預測結果
        
        Returns:
            審查結果
        """
        print(f"\n[Digital Twin] Reviewing {game} prediction...")
        
        concerns = []
        suggestions = []
        risk_level = 'low'
        
        # 規則 1: 檢查號碼範圍
        numbers = prediction.get('numbers', [])
        max_num = {'539': 39, 'lotto': 49, 'power': 38}
        if any(n > max_num.get(game, 39) or n < 1 for n in numbers):
            concerns.append("號碼超出有效範圍")
            risk_level = 'high'
        
        # 規則 2: 檢查重複號碼
        if len(numbers) != len(set(numbers)):
            concerns.append("存在重複號碼")
            risk_level = 'high'
        
        # 規則 3: 檢查連續號碼 (用戶偏好)
        if self.user_profile.get('preferences', {}).get('avoid_consecutive', True):
            sorted_nums = sorted(numbers)
            consecutive_count = 0
            for i in range(len(sorted_nums) - 1):
                if sorted_nums[i+1] - sorted_nums[i] == 1:
                    consecutive_count += 1
            if consecutive_count >= 3:
                concerns.append(f"包含 {consecutive_count} 組連續號碼")
                suggestions.append("考慮減少連續號碼")
                risk_level = 'medium'
        
        # 規則 4: 檢查號碼分布
        if game == '539':
            # 檢查是否過於集中在某個區間
            ranges = {'1-10': 0, '11-20': 0, '21-30': 0, '31-39': 0}
            for n in numbers:
                if n <= 10: ranges['1-10'] += 1
                elif n <= 20: ranges['11-20'] += 1
                elif n <= 30: ranges['21-30'] += 1
                else: ranges['31-39'] += 1
            
            max_in_range = max(ranges.values())
            if max_in_range >= 4:
                concerns.append(f"號碼過於集中在某個區間")
                suggestions.append("建議分散號碼選擇")
        
        # 規則 5: 檢查信心度
        confidence = prediction.get('confidence', 0)
        if confidence < 0.3:
            concerns.append(f"預測信心度過低 ({confidence:.2f})")
            suggestions.append("建議重新評估預測策略")
            risk_level = 'medium'
        
        result = {
            'game': game,
            'concerns': concerns,
            'suggestions': suggestions,
            'risk_level': risk_level,
            'approved': len(concerns) == 0 or risk_level == 'low',
            'timestamp': get_taiwan_isoformat()
        }
        
        # 發送審查報告
        self._send_review_report(result)
        
        return result
    
    def daily_strategic_review(self, context: Dict) -> Dict:
        
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
