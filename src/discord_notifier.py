# -*- coding: utf-8 -*-
"""
Discord 推送通知模組
提供自動化系統的 Discord Webhook 推送功能
"""
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import traceback
from src.timezone_utils import get_taiwan_isoformat


class DiscordNotifier:
    """Discord 通知推送器"""
    
    # 號碼球 Emoji 映射
    NUMBER_EMOJIS = {
        1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
        6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
    }
    
    def __init__(self, config_path: str = "config/auto_config.json"):
        """初始化 Discord 通知器"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.webhook_url = self.config.get("discord", {}).get("webhook_url", "")
        self.enabled = self.config.get("discord", {}).get("enable_notifications", True)
        self.notification_types = self.config.get("discord", {}).get("notification_types", {})
        
    def _load_config(self) -> dict:
        """載入配置檔"""
        if not self.config_path.exists():
            print(f"⚠️ 配置檔不存在: {self.config_path}")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 載入配置檔失敗: {e}")
            return {}
    
    def _format_number_balls(self, numbers: List[int]) -> str:
        """格式化號碼為 Emoji 球"""
        balls = []
        for num in sorted(numbers):
            if num <= 10:
                balls.append(self.NUMBER_EMOJIS.get(num, f"{num:02d}"))
            else:
                balls.append(f"**{num:02d}**")
        return " ".join(balls)
    
    def _send_webhook(self, payload: dict, retry: int = 3) -> bool:
        """發送 Webhook 請求"""
        if not self.enabled:
            print("[INFO] Discord notification disabled")
            return False
        
        if not self.webhook_url:
            print("[WARNING] Discord Webhook URL not configured")
            return False
        
        for attempt in range(retry):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 204:
                    print(f"[SUCCESS] Discord notification sent")
                    return True
                else:
                    print(f"[WARNING] Discord notification failed (status: {response.status_code})")
                    
            except Exception as e:
                print(f"[ERROR] Discord notification error (attempt {attempt + 1}/{retry}): {e}")
                
        return False
    
    def send_prediction_result(
        self, 
        prediction_date: str, 
        predicted_numbers,  # 可以是單組 List[int] 或多組 List[List[int]]
        backtest_result: Optional[Dict] = None
    ) -> bool:
        """
        發送預測結果通知
        
        Args:
            prediction_date: 預測目標日期
            predicted_numbers: 預測號碼 (單組或多組)
            backtest_result: 回測結果 (可選)
        """
        if not self.notification_types.get("prediction", True):
            return False
        
        # 判斷是單組還是多組
        is_multiple = isinstance(predicted_numbers[0], list)
        
        # 建立 Embed
        embed = {
            "title": "🎯 新預測已生成!",
            "description": f"**預測日期**: {prediction_date}",
            "color": 0x00D4FF,  # 青色
            "fields": [],
            "timestamp": get_taiwan_isoformat(),
            "footer": {
                "text": "539 AI 預測大師 | 自動化系統"
            }
        }
        
        # 加入預測號碼
        if is_multiple:
            # 多組號碼
            embed["description"] += f"\n\n**共 {len(predicted_numbers)} 組號碼 (覆蓋率最大化)**"
            
            for i, numbers in enumerate(predicted_numbers, 1):
                strategy_names = [
                    "🎯 策略一 (分區優選)",
                    "🔥 策略二 (全域高分)",
                    "⚖️ 策略三 (平衡分布)",
                    "🎲 策略四 (高分混合)",
                    "🌐 策略五 (分散覆蓋)"
                ]
                strategy_name = strategy_names[i-1] if i <= len(strategy_names) else f"📊 策略{i}"
                
                embed["fields"].append({
                    "name": strategy_name,
                    "value": self._format_number_balls(numbers),
                    "inline": False
                })
        else:
            # 單組號碼 (向後兼容)
            embed["fields"].append({
                "name": "🎲 推薦號碼",
                "value": self._format_number_balls(predicted_numbers),
                "inline": False
            })
        
        # 如果有回測結果,加入回測資訊
        if backtest_result:
            backtest_date = backtest_result.get('date', '未知')
            backtest_hits = len(backtest_result.get('hits', []))
            backtest_accuracy = backtest_result.get('accuracy', 0)
            
            embed["fields"].append({
                "name": "📊 回測驗證",
                "value": f"日期: {backtest_date}\n命中: {backtest_hits}/5 ({backtest_accuracy:.0%})",
                "inline": False
            })
        
        payload = {
            "username": "539 AI 預測系統",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
    
    def send_verification_result(
        self,
        prediction_date: str,
        predicted_numbers: List[int],
        actual_numbers: List[int],
        hits: List[int],
        accuracy: float
    ) -> bool:
        """
        發送驗證結果通知
        
        Args:
            prediction_date: 預測日期
            predicted_numbers: 預測號碼
            actual_numbers: 實際開獎號碼
            hits: 命中號碼
            accuracy: 命中率
        """
        if not self.notification_types.get("verification", True):
            return False
        
        # 判斷結果等級
        if accuracy >= 0.6:
            color = 0x00FF88  # 綠色 - 優秀
            emoji = "🎉"
            title = "恭喜!預測命中率優秀!"
        elif accuracy >= 0.4:
            color = 0xFFD700  # 金色 - 良好
            emoji = "✨"
            title = "預測命中率良好!"
        else:
            color = 0xFF6B6B  # 紅色 - 一般
            emoji = "📊"
            title = "預測結果已驗證"
        
        embed = {
            "title": f"{emoji} {title}",
            "description": f"**預測日期**: {prediction_date}",
            "color": color,
            "fields": [
                {
                    "name": "🎲 預測號碼",
                    "value": self._format_number_balls(predicted_numbers),
                    "inline": False
                },
                {
                    "name": "🎯 實際開獎",
                    "value": self._format_number_balls(actual_numbers),
                    "inline": False
                },
                {
                    "name": "✅ 命中結果",
                    "value": f"命中: **{len(hits)}/5** ({accuracy:.0%})\n號碼: {self._format_number_balls(hits) if hits else '無'}",
                    "inline": False
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {
                "text": "539 AI 預測大師 | 自動驗證系統"
            }
        }
        
        payload = {
            "username": "539 AI 驗證系統",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
    
    def send_training_report(
        self,
        training_periods: int,
        avg_accuracy: float,
        improvements: Dict[str, float]
    ) -> bool:
        """
        發送訓練報告通知
        
        Args:
            training_periods: 訓練期數
            avg_accuracy: 平均命中率
            improvements: 改進指標
        """
        if not self.notification_types.get("training", True):
            return False
        
        embed = {
            "title": "🧠 模型訓練完成!",
            "description": "自動訓練優化已完成",
            "color": 0x9B59B6,  # 紫色
            "fields": [
                {
                    "name": "📈 訓練統計",
                    "value": f"訓練期數: **{training_periods}**\n平均命中率: **{avg_accuracy:.2%}**",
                    "inline": False
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {
                "text": "539 AI 預測大師 | 自動訓練系統"
            }
        }
        
        # 加入改進指標
        if improvements:
            improvement_text = "\n".join([
                f"{key}: {value:+.2%}" for key, value in improvements.items()
            ])
            embed["fields"].append({
                "name": "🎯 優化成果",
                "value": improvement_text,
                "inline": False
            })
        
        payload = {
            "username": "539 AI 訓練系統",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)

    def send_update_report(self, updated_stats: Dict[str, int]) -> bool:
        """
        發送資料更新報告
        
        Args:
            updated_stats: 更新統計 {遊戲: 筆數}
        """
        # 使用 verification 或 training 類別, 或者預測類別
        if not self.enabled:
            return False
            
        total_new = sum(updated_stats.values())
        if total_new == 0:
            return False 
            
        embed = {
            "title": "📥 資料更新完成",
            "description": f"已成功抓取並更新 **{total_new}** 筆新資料",
            "color": 0x3498DB,  # 藍色
            "fields": [],
            "timestamp": get_taiwan_isoformat(),
            "footer": {
                "text": "539 AI 預測大師 | 自動更新系統"
            }
        }
        
        # Add details
        for game, count in updated_stats.items():
            if count > 0:
                embed["fields"].append({
                    "name": f"🎲 {game.title()}",
                    "value": f"新增 **{count}** 筆資料",
                    "inline": True
                })
            
        payload = {
            "username": "539 AI 更新系統",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
    
    def send_error_alert(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> bool:
        """
        發送異常警報通知
        
        Args:
            error_type: 異常類型
            error_message: 異常訊息
            stack_trace: 堆疊追蹤 (可選)
        """
        if not self.notification_types.get("error", True):
            return False
        
        embed = {
            "title": "⚠️ 系統異常警報!",
            "description": f"**異常類型**: {error_type}",
            "color": 0xFF0000,  # 紅色
            "fields": [
                {
                    "name": "❌ 錯誤訊息",
                    "value": f"```\n{error_message[:1000]}\n```",
                    "inline": False
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {
                "text": "539 AI 預測大師 | 異常監控系統"
            }
        }
        
        # 如果有堆疊追蹤,加入 (限制長度)
        if stack_trace:
            embed["fields"].append({
                "name": "📋 堆疊追蹤",
                "value": f"```python\n{stack_trace[:1000]}\n```",
                "inline": False
            })
        
        payload = {
            "username": "539 AI 異常監控",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
    
    def send_test_message(self) -> bool:
        """發送測試訊息"""
        embed = {
            "title": "✅ Discord 推送測試",
            "description": "這是一則測試訊息,確認 Webhook 連線正常!",
            "color": 0x00D4FF,
            "fields": [
                {
                    "name": "🔧 系統狀態",
                    "value": "Discord 推送模組運作正常",
                    "inline": False
                }
            ],
            "timestamp": get_taiwan_isoformat(),
            "footer": {
                "text": "539 AI 預測大師 | 測試訊息"
            }
        }
        
        payload = {
            "username": "539 AI 測試系統",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)


if __name__ == "__main__":
    # 測試 Discord 推送
    print("=" * 60)
    print("Discord Notification Module Test")
    print("=" * 60)
    
    notifier = DiscordNotifier()
    
    # 測試 1: 基本連線測試
    print("\n[Test 1] Sending test message...")
    notifier.send_test_message()
    
    # 測試新功能
    print("\n[Test New] Sending update report...")
    notifier.send_update_report({'539': 5, 'lotto': 2, 'power': 0})
    
    print("\n" + "=" * 60)
    print("Test completed! Please check your Discord channel")
    print("=" * 60)
