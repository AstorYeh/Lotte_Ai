# -*- coding: utf-8 -*-
"""
多遊戲預測管理器
統一管理所有遊戲的預測
"""
from src.auto_predictor import AutoPredictor
from src.games.lotto_predictor import LottoPredictor
from src.games.power_predictor import PowerPredictor
from src.games.star3_predictor import Star3Predictor
from src.games.star4_predictor import Star4Predictor
from src.discord_notifier import DiscordNotifier


class MultiGameManager:
    """多遊戲預測管理器"""
    
    def __init__(self):
        self.discord = DiscordNotifier()
        
        # 初始化各遊戲預測器
        self.predictors = {
            '539': AutoPredictor(),
            'lotto': LottoPredictor(),
            'power': PowerPredictor(),
            'star3': Star3Predictor(),
            'star4': Star4Predictor()
        }
    
    def _save_prediction_to_csv(self, game_name, data):
        """將預測結果儲存為 CSV (供 Dashboard 讀取)"""
        try:
            import pandas as pd
            from pathlib import Path
            
            # 確保目錄存在
            save_dir = Path("predictions")
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / f"{game_name}_predictions.csv"
            
            # 準備資料
            date = data.get('date')
            preds = data.get('predictions')
            
            # 轉換為字串格式儲存
            # Lotto/539: [[1,2,3...], [4,5,6...]]
            # Power: [{'zone1': [...], 'zone2': 1}, ...]
            # Star: ['123', '456']
            
            formatted_preds = []
            if game_name == 'power':
                # 威力彩特殊處理
                for p in preds:
                    formatted_preds.append({'zone1': p['zone1'], 'zone2': p['zone2']})
            else:
                formatted_preds = preds
            
            df = pd.DataFrame([{
                'date': date,
                'numbers': str(formatted_preds),
                'created_at': __import__('src.timezone_utils', fromlist=['get_taiwan_now']).get_taiwan_now()
            }])
            
            # 這裡我們只儲存最新的一期，覆蓋舊的或者追加?
            # Dashboard 只讀取 latest = df.iloc[-1]
            # 我們可以追加
            
            if file_path.exists():
                try:
                    old_df = pd.read_csv(file_path)
                    # 避免重複日期
                    if date not in old_df['date'].values:
                        df = pd.concat([old_df, df], ignore_index=True)
                    else:
                        # 更新該日期的預測
                        old_df.loc[old_df['date'] == date, 'numbers'] = str(formatted_preds)
                        df = old_df
                except:
                    pass
            
            df.to_csv(file_path, index=False)
            print(f"[OK] {game_name} 預測已存檔: {file_path}")
            
        except Exception as e:
            print(f"[ERROR] {game_name} 存檔失敗: {e}")

    def generate_all_predictions(self):
        """生成所有遊戲的預測"""
        results = {}
        
        print("=" * 80)
        print("多遊戲預測系統 - 生成所有預測")
        print("=" * 80)
        
        # 1. 539
        print("\n[1/5] 今彩539...")
        try:
            # 539 AutoPredictor 通常已經自己存檔了，但為了保險起見我們也存一份到 predictions/
            # AutoPredictor saving path might be different
            result_539 = self.predictors['539'].generate_new_prediction()
            if result_539:
                results['539'] = result_539
                # 539 result format might need adjustment for _save_prediction_to_csv
                # result_539 structure: {'date': ..., 'num_sets': ..., 'predictions': ...} ?
                # AutoPredictor returns differently? Let's check AutoPredictor if needed.
                # Assuming result_539 has 'predictions' key with list of lists
                
                # Check structure compatibility
                if 'predictions' not in result_539 and 'numbers' in result_539:
                     result_539['predictions'] = result_539['numbers']
                
                self._save_prediction_to_csv('539', result_539)
                print(f"[OK] 539 完成: {result_539.get('num_sets', len(result_539.get('predictions', [])))} 組")
        except Exception as e:
            print(f"[ERROR] 539 失敗: {e}")
        
        # 2. 大樂透
        print("\n[2/5] 大樂透...")
        try:
            lotto_preds = self.predictors['lotto'].generate_predictions(5)
            lotto_date = self.predictors['lotto'].get_next_draw_date()
            results['lotto'] = {
                'date': lotto_date,
                'predictions': lotto_preds
            }
            self._save_prediction_to_csv('lotto', results['lotto'])
            print(f"[OK] 大樂透完成: 5 組")
        except Exception as e:
            print(f"[ERROR] 大樂透失敗: {e}")
        
        # 3. 威力彩
        print("\n[3/5] 威力彩...")
        try:
            power_preds = self.predictors['power'].generate_predictions(5)
            power_date = self.predictors['power'].get_next_draw_date()
            results['power'] = {
                'date': power_date,
                'predictions': power_preds
            }
            self._save_prediction_to_csv('power', results['power'])
            print(f"[OK] 威力彩完成: 5 組")
        except Exception as e:
            print(f"[ERROR] 威力彩失敗: {e}")
        
        # 4. 3星彩
        print("\n[4/5] 3星彩...")
        try:
            star3_preds = self.predictors['star3'].generate_predictions(5)
            star3_date = self.predictors['star3'].get_next_draw_date()
            results['star3'] = {
                'date': star3_date,
                'predictions': star3_preds
            }
            self._save_prediction_to_csv('star3', results['star3'])
            print(f"[OK] 3星彩完成: 5 組")
        except Exception as e:
            print(f"[ERROR] 3星彩失敗: {e}")
        
        # 5. 4星彩
        print("\n[5/5] 4星彩...")
        try:
            star4_preds = self.predictors['star4'].generate_predictions(5)
            star4_date = self.predictors['star4'].get_next_draw_date()
            results['star4'] = {
                'date': star4_date,
                'predictions': star4_preds
            }
            self._save_prediction_to_csv('star4', results['star4'])
            print(f"[OK] 4星彩完成: 5 組")
        except Exception as e:
            print(f"[ERROR] 4星彩失敗: {e}")
        
        print("\n" + "=" * 80)
        print(f"預測完成! 共 {len(results)} 個遊戲")
        print("=" * 80)
        
        return results
    
    def send_all_predictions(self, results):
        """推送所有預測到 Discord"""
        print("\n推送預測到 Discord...")
        
        for game, data in results.items():
            try:
                if game == '539':
                    # 539 已經在生成時推送了
                    print(f"[OK] 539 已推送")
                else:
                    self._send_game_prediction(game, data)
                    print(f"[OK] {game} 已推送")
            except Exception as e:
                print(f"[ERROR] {game} 推送失敗: {e}")
    
    def _send_game_prediction(self, game_name, data):
        """推送單個遊戲的預測"""
        # 建立 Discord Embed
        game_names = {
            'lotto': '大樂透',
            'power': '威力彩',
            'star3': '3星彩',
            'star4': '4星彩'
        }
        
        embed = {
            "title": f"🎯 {game_names.get(game_name, game_name)} 預測",
            "description": f"**預測日期**: {data['date']}",
            "color": 0x00D4FF,
            "fields": [],
            "timestamp": __import__('src.timezone_utils', fromlist=['get_taiwan_isoformat']).get_taiwan_isoformat()
        }
        
        # 添加預測號碼
        predictions = data.get('predictions', [])
        for i, pred in enumerate(predictions, 1):
            if game_name == 'power':
                value = f"第一區: {pred['zone1']}\n第二區: {pred['zone2']}"
            elif game_name in ['star3', 'star4']:
                value = f"`{pred}`"
            else:
                value = str(pred)
            
            embed["fields"].append({
                "name": f"第 {i} 組",
                "value": value,
                "inline": False
            })
        
        payload = {
            "username": f"{game_names.get(game_name)} AI 預測",
            "embeds": [embed]
        }
        
        self.discord._send_webhook(payload)


if __name__ == "__main__":
    manager = MultiGameManager()
    results = manager.generate_all_predictions()
    manager.send_all_predictions(results)
