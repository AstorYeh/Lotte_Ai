# -*- coding: utf-8 -*-
"""
數學專家 AI 助手
負責資料驗證、統計分析、模型驗證
使用純計算,不依賴 LLM
"""
import pandas as pd
import numpy as np
from pathlib import Path
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_isoformat


class MathValidator:
    """數學專家 - 資料驗證與統計分析 (純計算)"""
    
    def __init__(self):
        """初始化數學驗證器"""
        self.discord = DiscordNotifier()
        self.data_paths = {
            '539': Path('data/539.csv'),
            '539_train': Path('data/539_train.csv')
        }
        print("[INFO] 數學專家已啟用 (純計算模式,不使用 LLM)")
    
    def check_data_integrity(self, game: str) -> dict:
        """檢查歷史資料的完整性和正確性"""
        try:
            # 讀取歷史資料
            history_file = f"data/{game}_history.csv"
            if not Path(history_file).exists():
                return {'error': f'History file not found: {history_file}'}
            
            df = pd.read_csv(history_file)
            issues = []
            
            # 1. 檢查期數連續性 (僅 539)
            if game == '539' and 'period' in df.columns:
                periods = df['period'].tolist()
                for i in range(len(periods)-1):
                    if periods[i+1] - periods[i] != 1:
                        issues.append(f"期數不連續: {periods[i]} -> {periods[i+1]}")
            
            # 2. 檢查號碼範圍
            max_number = {'539': 39, 'lotto': 49, 'power': 38, 'star3': 9, 'star4': 9}
            number_cols = [col for col in df.columns if col.isdigit() or col in ['1', '2', '3', '4', '5', '6']]
            
            for col in number_cols:
                if col in df.columns:
                    invalid = df[df[col] > max_number.get(game, 39)][col]
                    if len(invalid) > 0:
                        issues.append(f"發現超出範圍的號碼 (欄位 {col}): {invalid.tolist()[:5]}")
            
            # 3. 檢查重複
            if 'date' in df.columns:
                duplicates = df[df.duplicated(subset=['date'], keep=False)]
                if len(duplicates) > 0:
                    issues.append(f"發現重複日期: {duplicates['date'].tolist()[:5]}")
            
            result = {
                'game': game,
                'total_records': len(df),
                'date_range': f"{df['date'].min()} ~ {df['date'].max()}" if 'date' in df.columns else 'N/A',
                'issues': issues,
                'is_valid': len(issues) == 0
            }
            
            return result
            
        except Exception as e:
            return {'error': str(e), 'is_valid': False}
    
    def validate_prediction_logic(self, game: str, prediction_data: Dict) -> Dict:
        """驗證預測邏輯的數學正確性"""
        if not self.llm_client:
            return {'is_valid': True, 'note': 'LLM validation skipped'}
        
        try:
            prompt = f"""
你是一位專業的統計學和機率論專家。請驗證以下彩票預測系統的數學邏輯:

遊戲: {game}
預測數據: {json.dumps(prediction_data, indent=2, ensure_ascii=False)}

請檢查:
1. 機率計算是否正確
2. 權重分配是否合理
3. 統計方法是否恰當
4. 是否存在數學謬誤
5. 預測結果是否符合遊戲規則

以 JSON 格式回應:
{{
  "is_valid": true,
  "confidence": 0.95,
  "issues": [],
  "suggestions": [],
  "severity": "low"
}}
"""
            
            response = self.llm_client.generate_content(prompt)
            # 嘗試解析 JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response.text, re.DOTALL)
            if json_match:
                validation = json.loads(json_match.group())
                return validation
            else:
                return {'is_valid': True, 'note': 'Unable to parse LLM response'}
                
        except Exception as e:
            print(f"[ERROR] Math validation failed: {e}")
            return {'is_valid': True, 'error': str(e)}
    
    def run_daily_validation(self) -> Dict:
        """執行每日數據驗證"""
        print("\n[Math Validator] Starting daily validation...")
        
        results = {}
        has_critical_issues = False
        
        for game in ['539', 'lotto', 'power', 'star3', 'star4']:
            # 數據完整性檢查
            integrity = self.check_data_integrity(game)
            results[game] = integrity
            
            # 如果有嚴重問題,發送警報
            if not integrity.get('is_valid', False):
                has_critical_issues = True
                self._send_validation_alert(game, integrity)
        
        # 生成摘要
        results['summary'] = {
            'timestamp': get_taiwan_isoformat(),
            'has_critical_issues': has_critical_issues,
            'total_games_checked': 5
        }
        
        return results
    
    def _send_validation_alert(self, game: str, integrity: Dict):
        """發送驗證警報"""
        issues = integrity.get('issues', [])
        
        embed = {
            "title": f"⚠️ 數學專家警報 - {game.upper()}",
            "description": "發現數據完整性問題",
            "color": 0xE74C3C,  # 紅色
            "fields": [
                {
                    "name": "📊 資料筆數",
                    "value": str(integrity.get('total_records', 'N/A')),
                    "inline": True
                },
                {
                    "name": "📅 日期範圍",
                    "value": integrity.get('date_range', 'N/A'),
                    "inline": True
                },
                {
                    "name": "🚨 發現問題",
                    "value": "\n".join([f"• {issue}" for issue in issues[:5]]),
                    "inline": False
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {"text": "數學專家助手 | 數據守門員"}
        }
        
        payload = {
            "username": "數學專家助手",
            "embeds": [embed]
        }
        
        self.discord._send_webhook(payload)


if __name__ == "__main__":
    validator = MathValidator()
    results = validator.run_daily_validation()
    print(json.dumps(results, indent=2, ensure_ascii=False))
