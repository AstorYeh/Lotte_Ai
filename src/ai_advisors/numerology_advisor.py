# -*- coding: utf-8 -*-
"""
命理專家助手 - 提供天文數理建議
"""
import json
import os
from datetime import datetime
from typing import Dict, List
from google import genai
from lunarcalendar import Converter, Solar, Lunar
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_isoformat


class NumerologyAdvisor:
    """命理專家 - 提供天文數理建議"""
    
    def __init__(self):
        self.discord = DiscordNotifier()
        self.llm_client = self._init_gemini_client()
    
    def _init_gemini_client(self):
        """初始化 Gemini API 客戶端"""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("[WARNING] GOOGLE_API_KEY not set, Numerology Advisor disabled")
            return None
        
        return genai.Client(api_key=api_key)
    
    def _get_lunar_info(self, target_date: str) -> Dict:
        """取得準確的農曆資訊"""
        try:
            dt = datetime.strptime(target_date, '%Y-%m-%d')
            solar = Solar(dt.year, dt.month, dt.day)
            lunar = Converter.Solar2Lunar(solar)
            
            # 農曆月份名稱
            lunar_months = ['正月', '二月', '三月', '四月', '五月', '六月',
                          '七月', '八月', '九月', '十月', '冬月', '臘月']
            
            # 農曆日期名稱 (1-30)
            def get_lunar_day_name(day: int) -> str:
                if day <= 10:
                    return f"初{['一','二','三','四','五','六','七','八','九','十'][day-1]}"
                elif day < 20:
                    return f"十{['一','二','三','四','五','六','七','八','九'][day-11]}" if day > 10 else "初十"
                elif day == 20:
                    return "二十"
                elif day < 30:
                    return f"廿{['一','二','三','四','五','六','七','八','九'][day-21]}"
                else:
                    return "三十"
            
            lunar_date_str = f"農曆{lunar_months[lunar.month-1]}{get_lunar_day_name(lunar.day)}"
            
            # 天干地支
            heavenly_stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
            earthly_branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
            
            # 簡化版:使用年份計算天干地支
            year_offset = (dt.year - 4) % 60
            stem = heavenly_stems[year_offset % 10]
            branch = earthly_branches[year_offset % 12]
            
            return {
                'lunar_date': lunar_date_str,
                'lunar_year': lunar.year,
                'lunar_month': lunar.month,
                'lunar_day': lunar.day,
                'heavenly_stem': stem,
                'earthly_branch': branch,
                'ganzhi': f"{stem}{branch}"
            }
        except Exception as e:
            print(f"[WARNING] Lunar calculation failed: {e}")
            return {
                'lunar_date': '未知',
                'heavenly_stem': '未知',
                'earthly_branch': '未知',
                'ganzhi': '未知'
            }
    
    def get_daily_numerology_advice(self, target_date: str) -> Dict:
        """取得當日的天文數理建議"""
        if not self.llm_client:
            return self._get_default_advice()
        
        try:
            dt = datetime.strptime(target_date, '%Y-%m-%d')
            weekday = dt.strftime('%A')
            
            # 取得準確的農曆資訊
            lunar_info = self._get_lunar_info(target_date)
            
            prompt = f"""
你是一位精通天文曆法和數理命理的專家。請為以下日期提供彩票選號建議:

日期: {target_date} ({weekday})
農曆: {lunar_info['lunar_date']}
天干地支: {lunar_info['ganzhi']}年
遊戲: 台灣539 (從1-39選5個號碼)

請根據以下角度分析:

1. **農曆與節氣**
   - 根據 {lunar_info['lunar_date']} 分析月相對數字能量的影響
   - 判斷當前節氣

2. **天干地支與五行**
   - 天干: {lunar_info['heavenly_stem']}
   - 地支: {lunar_info['earthly_branch']}
   - 推算五行屬性 (金木水火土)
   - 對應的幸運數字

3. **數理吉凶**
   - 適合的數字範圍
   - 建議避開的數字
   - 陰陽平衡建議

4. **綜合建議**
   - 推薦 3-5 個幸運數字
   - 信心度評估 (0-1)
   - 簡短說明

請以 JSON 格式回應:
{{
  "lunar_date": "{lunar_info['lunar_date']}",
  "solar_term": "立春",
  "heavenly_stem": "{lunar_info['heavenly_stem']}",
  "earthly_branch": "{lunar_info['earthly_branch']}",
  "element": "木",
  "lucky_numbers": [3, 8, 13, 28, 33],
  "avoid_numbers": [4, 9, 14],
  "yin_yang_balance": "建議選擇3陽2陰",
  "confidence": 0.65,
  "explanation": "今日木旺,宜選帶3、8之數..."
}}

注意: 這只是輔助參考,不保證中獎。
"""
            
            response = self.llm_client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            
            # 解析 JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response.text, re.DOTALL)
            if json_match:
                advice = json.loads(json_match.group())
                return advice
            else:
                return self._get_default_advice()
                
        except Exception as e:
            print(f"[ERROR] Numerology advice failed: {e}")
            return self._get_default_advice()
    
    def _get_default_advice(self) -> Dict:
        """預設建議 (當 LLM 不可用時)"""
        return {
            "lunar_date": "未知",
            "solar_term": "未知",
            "element": "未知",
            "lucky_numbers": [],
            "avoid_numbers": [],
            "yin_yang_balance": "平衡為佳",
            "confidence": 0.5,
            "explanation": "命理建議暫時無法提供"
        }
    
    def integrate_with_prediction(self, ml_predictions: List[List[int]], 
                                   numerology_advice: Dict) -> Dict:
        """整合機器學習預測與命理建議"""
        lucky_numbers = set(numerology_advice.get('lucky_numbers', []))
        avoid_numbers = set(numerology_advice.get('avoid_numbers', []))
        
        # 分析每組預測與命理的契合度
        scored_predictions = []
        
        for pred in ml_predictions:
            lucky_count = len(set(pred) & lucky_numbers)
            avoid_count = len(set(pred) & avoid_numbers)
            
            # 計算契合度分數
            harmony_score = (lucky_count * 0.3) - (avoid_count * 0.2)
            
            scored_predictions.append({
                'numbers': pred,
                'lucky_count': lucky_count,
                'avoid_count': avoid_count,
                'harmony_score': harmony_score
            })
        
        # 排序
        scored_predictions.sort(key=lambda x: x['harmony_score'], reverse=True)
        
        return {
            'ranked_predictions': scored_predictions,
            'numerology_advice': numerology_advice,
            'recommendation': scored_predictions[0]['numbers'] if scored_predictions else []
        }
    
    def send_daily_numerology_report(self, target_date: str, advice: Dict):
        """發送每日命理報告到 Discord"""
        embed = {
            "title": f"🔮 每日命理建議 - {target_date}",
            "description": advice.get('explanation', ''),
            "color": 0x9B59B6,  # 紫色
            "fields": [
                {
                    "name": "📅 農曆資訊",
                    "value": f"{advice.get('lunar_date')} · {advice.get('solar_term')}",
                    "inline": True
                },
                {
                    "name": "☯️ 五行",
                    "value": advice.get('element', '未知'),
                    "inline": True
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {"text": f"信心度: {advice.get('confidence', 0):.0%} | 僅供參考"}
        }
        
        # 添加幸運數字
        if advice.get('lucky_numbers'):
            embed['fields'].append({
                "name": "🍀 幸運數字",
                "value": ", ".join(map(str, advice.get('lucky_numbers', []))),
                "inline": False
            })
        
        # 添加避開數字
        if advice.get('avoid_numbers'):
            embed['fields'].append({
                "name": "⚠️ 避開數字",
                "value": ", ".join(map(str, advice.get('avoid_numbers', []))),
                "inline": False
            })
        
        payload = {
            "username": "命理專家助手",
            "embeds": [embed]
        }
        
        self.discord._send_webhook(payload)


if __name__ == "__main__":
    from datetime import date
    advisor = NumerologyAdvisor()
    today = date.today().strftime('%Y-%m-%d')
    advice = advisor.get_daily_numerology_advice(today)
    print(json.dumps(advice, indent=2, ensure_ascii=False))
    advisor.send_daily_numerology_report(today, advice)
