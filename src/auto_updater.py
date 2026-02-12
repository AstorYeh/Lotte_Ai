# -*- coding: utf-8 -*-
"""
自動資料更新模組
整合爬蟲與資料驗證,實現自動化資料更新流程 (支援所有遊戲: 539, Lotto, Power, Star3, Star4)
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import os
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Optional, List, Dict, Any
from src.structured_logger import structured_logger
from src.discord_notifier import DiscordNotifier
from src.timezone_utils import get_taiwan_timestamp_str, get_taiwan_now

class AutoUpdater:
    """自動資料更新協調器 (支援全遊戲)"""
    
    def __init__(self):
        """初始化"""
        # 定義檔案路徑
        self.data_dir = Path('data')
        self.paths = {
            '539': self.data_dir / '539_history.csv',
            'lotto': self.data_dir / 'lotto' / 'lotto_history.csv',
            'power': self.data_dir / 'power' / 'power_history.csv',
            'star3': self.data_dir / 'star3' / 'star3_history.csv',
            'star4': self.data_dir / 'star4' / 'star4_history.csv'
        }
        
        # 訓練檔案 (主要用於 539, 其他遊戲若有需要也可加入)
        self.train_file_539 = self.data_dir / '539_train.csv'
        
        self.backup_dir = self.data_dir / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.discord = DiscordNotifier()

        # 爬蟲設定
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _backup_file(self, file_path: Path) -> Optional[Path]:
        """備份檔案"""
        if not file_path.exists():
            return None
        
        timestamp = get_taiwan_timestamp_str()
        # 建立子目錄以保持整潔
        game_name = file_path.stem.split('_')[0]
        backup_subdir = self.backup_dir / game_name
        backup_subdir.mkdir(exist_ok=True)
        
        backup_path = backup_subdir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        try:
            shutil.copy2(file_path, backup_path)
            file_size = file_path.stat().st_size
            
            structured_logger.log_backup(
                backup_type='auto_update',
                source_path=str(file_path),
                backup_path=str(backup_path),
                file_size_bytes=file_size,
                success=True
            )
            
            print(f"[SUCCESS] Backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            structured_logger.log_backup(
                backup_type='auto_update',
                source_path=str(file_path),
                backup_path=str(backup_path),
                success=False
            )
            return None

    def _download_html(self, url: str) -> Optional[str]:
        """下載 HTML 內容"""
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"[ERROR] HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")
            return None

    def _parse_539(self, html_content: str, current_ym: str) -> List[Dict]:
        """解析 539"""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        
        tables = soup.find_all('table', class_='history_view_table')
        for table in tables:
            tds = table.find_all('td')
            for td in tds:
                text = td.get_text(separator=' ', strip=True)
                date_match = date_pattern.search(text)
                if date_match:
                    date_str = date_match.group(0)
                    if not date_str.startswith(current_ym): continue 
                    
                    parent_tr = td.find_parent('tr')
                    if not parent_tr: continue
                    
                    ball_ul = parent_tr.find('ul', class_='history_ball')
                    if not ball_ul: continue
                    
                    sorted_li = None
                    for li in ball_ul.find_all('li'):
                        if '大小順序' in li.get_text():
                            sorted_li = li
                            break
                    
                    nums = []
                    if sorted_li:
                        links = sorted_li.find_all('a', class_='history_ball_link')
                        nums = [int(link.get_text(strip=True)) for link in links]
                    else:
                        links = ball_ul.find_all('a', class_='history_ball_link')
                        nums = [int(link.get_text(strip=True)) for link in links[:5]]
                    
                    if len(nums) == 5:
                        nums.sort()
                        data.append({
                            'date': date_str,
                            'numbers': ','.join(map(str, nums))
                        })
                        print(f"Parsed 539 {date_str}: {nums}")
        return data

    def _parse_power(self, html_content: str, current_ym: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        tables = soup.find_all('table', class_='history_view_table')
        
        for table in tables:
            tds = table.find_all('td')
            for td in tds:
                text = td.get_text(separator=' ', strip=True)
                date_match = date_pattern.search(text)
                if date_match:
                    date_str = date_match.group(0)
                    if not date_str.startswith(current_ym): continue
                    
                    parent_tr = td.find_parent('tr')
                    if not parent_tr: continue
                    
                    ball_ul = parent_tr.find('ul', class_='history_ball')
                    if not ball_ul: continue
                    
                    sorted_li = None
                    for li in ball_ul.find_all('li'):
                        if '大小順序' in li.get_text():
                            sorted_li = li
                            break
                    
                    if sorted_li:
                        links = sorted_li.find_all('a', class_='history_ball_link')
                        nums = [int(link.get_text(strip=True)) for link in links]
                    else:
                        links = ball_ul.find_all('a', class_='history_ball_link')
                        if len(links) >= 12: nums = [int(t.get_text()) for t in links[6:12]]
                        elif len(links) >= 6: nums = [int(t.get_text()) for t in links[:6]]
                        else: nums = []

                    special_td = parent_tr.find('td', style=lambda x: x and 'color:#005aff' in x and 'font-size:48px' in x)
                    special = special_td.get_text(strip=True) if special_td else None
                    if not special:
                         cells = parent_tr.find_all('td', recursive=False)
                         if len(cells) >= 3: special = cells[2].get_text(strip=True)

                    if nums and special:
                        data.append({
                            'date': date_str,
                            '1': nums[0], '2': nums[1], '3': nums[2],
                            '4': nums[3], '5': nums[4], '6': nums[5],
                            'zone2': special
                        })
                        print(f"Parsed Power {date_str}: {nums} + {special}")
        return data

    def _parse_lotto(self, html_content: str, current_ym: str) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
        tables = soup.find_all('table', class_='history_view_table')
        
        for table in tables:
            tds = table.find_all('td')
            for td in tds:
                text = td.get_text(separator=' ', strip=True)
                date_match = date_pattern.search(text)
                if date_match:
                    date_str = date_match.group(0)
                    if not date_str.startswith(current_ym): continue
                    
                    parent_tr = td.find_parent('tr')
                    if not parent_tr: continue
                    
                    ball_ul = parent_tr.find('ul', class_='history_ball')
                    if not ball_ul: continue
                    
                    sorted_li = None
                    for li in ball_ul.find_all('li'):
                        if '大小順序' in li.get_text():
                            sorted_li = li
                            break
                    
                    if sorted_li:
                       links = sorted_li.find_all('a', class_='history_ball_link')
                       nums = [int(link.get_text(strip=True)) for link in links]
                    else:
                       links = ball_ul.find_all('a', class_='history_ball_link')
                       if len(links) >= 12: nums = [int(t.get_text()) for t in links[6:12]]
                       else: nums = [int(t.get_text()) for t in links[:6]]
                    
                    special_td = parent_tr.find('td', style=lambda x: x and 'color:#005aff' in x)
                    special = special_td.get_text(strip=True) if special_td else "0"
                    
                    if nums:
                        data.append({
                            'date': date_str,
                            '1': nums[0], '2': nums[1], '3': nums[2],
                            '4': nums[3], '5': nums[4], '6': nums[5],
                            'special': special
                        })
                        print(f"Parsed Lotto {date_str}: {nums} + {special}")
        return data

    def _parse_star(self, html_content: str, current_ym: str, star_type: int) -> List[Dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
        rows = soup.find_all('tr', class_='history_view_star')
        
        for row in rows:
            tds = row.find_all('td')
            if len(tds) < 3: continue
            
            date_text = tds[2].get_text()
            date_match = date_pattern.search(date_text)
            if not date_match: continue
            date_str = date_match.group(1)
            
            if not date_str.startswith(current_ym): continue
            
            ball_td = tds[1]
            spans = ball_td.find_all('span')
            nums = [s.get_text(strip=True) for s in spans]
            
            if len(nums) == star_type:
                record = {'date': date_str}
                for i, n in enumerate(nums):
                    record[f'{i+1}'] = n
                data.append(record)
                print(f"Parsed Star{star_type} {date_str}: {nums}")
        return data

    def _update_csv(self, file_path: Path, new_data: List[Dict]) -> int:
        """更新 CSV, 返回新增筆數"""
        if not new_data:
            return 0
        
        added_count = 0
        try:
            new_df = pd.DataFrame(new_data)
            
            if file_path.exists():
                old_df = pd.read_csv(file_path)
                original_len = len(old_df)
                
                # 合併
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
                # 去重 (依賴 date)
                combined_df.drop_duplicates(subset=['date'], keep='last', inplace=True)
                combined_df.sort_values(by='date', ascending=True, inplace=True)
                
                final_len = len(combined_df)
                added_count = final_len - original_len
                # 注意: 如果是更新既有日期的資料(修正), len 可能不變, 但內容變了.
                # 這裡簡化為數量變化. 若完全一樣則為 0.
            else:
                combined_df = new_df
                # Create parent dir if not exists
                file_path.parent.mkdir(parents=True, exist_ok=True)
                combined_df.sort_values(by='date', ascending=True, inplace=True)
                added_count = len(combined_df)
            
            if added_count > 0 or not file_path.exists(): # Always save if new file
                combined_df.to_csv(file_path, index=False)
                print(f"[INFO] Updated {file_path.name}: +{added_count} records")
            else:
                print(f"[INFO] No new records for {file_path.name}")
                
            return max(0, added_count) # Ensure non-negative
            
        except Exception as e:
            print(f"[ERROR] Update CSV {file_path} failed: {e}")
            return 0

    def update_and_validate(self) -> dict:
        """執行完整更新流程"""
        print("=" * 60)
        print("Auto Data Update Starting (All Games)")
        print("=" * 60)
        
        result = {
            'success': False,
            'updated_stats': {}, # {game: count}
            'new_records': 0,    # Total count for compatibility
            'errors': []
        }
        
        # 取得當前年月 (e.g., "2026-02")
        now = get_taiwan_now()
        current_year = now.year
        current_month = now.month
        current_ym = now.strftime('%Y-%m')
        
        # 1. Update 539
        try:
            self._backup_file(self.paths['539'])
            url_539 = f"https://lotto.auzo.tw/daily539/list_{current_year}_{current_month}.html"
            html_539 = self._download_html(url_539)
            if html_539:
                data_539 = self._parse_539(html_539, current_ym)
                count = self._update_csv(self.paths['539'], data_539)
                result['updated_stats']['539'] = count
                
                # 同步到 train_csv
                if count > 0:
                     self._update_csv(self.train_file_539, data_539)
        except Exception as e:
            result['errors'].append(f"539 Error: {e}")

        # 2. Update Power
        try:
            self._backup_file(self.paths['power'])
            url_power = f"https://lotto.auzo.tw/power/list_{current_year}_{current_month}.html"
            html_power = self._download_html(url_power)
            if html_power:
                data_power = self._parse_power(html_power, current_ym)
                count = self._update_csv(self.paths['power'], data_power)
                result['updated_stats']['power'] = count
        except Exception as e:
            result['errors'].append(f"Power Error: {e}")

        # 3. Update Lotto
        try:
            self._backup_file(self.paths['lotto'])
            url_lotto = f"https://lotto.auzo.tw/biglotto/list_{current_year}_{current_month}.html"
            html_lotto = self._download_html(url_lotto)
            if html_lotto:
                data_lotto = self._parse_lotto(html_lotto, current_ym)
                count = self._update_csv(self.paths['lotto'], data_lotto)
                result['updated_stats']['lotto'] = count
        except Exception as e:
             result['errors'].append(f"Lotto Error: {e}")

        # 4. Update Star3
        try:
            self._backup_file(self.paths['star3'])
            url_star3 = "https://lotto.auzo.tw/lotto_historylist_three-star.html"
            html_star3 = self._download_html(url_star3)
            if html_star3:
                data_star3 = self._parse_star(html_star3, current_ym, 3)
                count = self._update_csv(self.paths['star3'], data_star3)
                result['updated_stats']['star3'] = count
        except Exception as e:
            result['errors'].append(f"Star3 Error: {e}")
            
        # 5. Update Star4
        try:
            self._backup_file(self.paths['star4'])
            url_star4 = "https://lotto.auzo.tw/lotto_historylist_four-star.html"
            html_star4 = self._download_html(url_star4)
            if html_star4:
                data_star4 = self._parse_star(html_star4, current_ym, 4)
                count = self._update_csv(self.paths['star4'], data_star4)
                result['updated_stats']['star4'] = count
        except Exception as e:
            result['errors'].append(f"Star4 Error: {e}")

        # Summary
        result['new_records'] = sum(result['updated_stats'].values())
        if not result['errors']:
            result['success'] = True
            print(f"\n[SUCCESS] Update complete. Stats: {result['updated_stats']}")
            
            # Send Discord Notification
            if result['new_records'] > 0:
                self.discord.send_update_report(result['updated_stats'])
            
            # 提取並發送當日開獎號碼
            today_results = self._get_today_results()
            if today_results:
                self.discord.send_today_results(today_results)
        else:
            print(f"\n[WARNING] Errors occurred: {result['errors']}")
            
        # Log
        structured_logger.log_operation(
            operation_type='auto_data_update_all',
            status='success' if result['success'] else 'partial_failure',
            details=result
        )
        
        return result
    
    def _get_today_results(self) -> Dict[str, Dict]:
        """提取當日開獎號碼"""
        import pandas as pd
        from src.timezone_utils import get_taiwan_now
        
        today = get_taiwan_now().strftime('%Y-%m-%d')
        results = {}
        
        # 539
        try:
            df_539 = pd.read_csv(self.paths['539'])
            today_539 = df_539[df_539['date'] == today]
            if not today_539.empty:
                row = today_539.iloc[0]
                results['539'] = {
                    'date': row['date'],
                    'numbers': [int(row[f'n{i}']) for i in range(1, 6)]
                }
        except:
            pass
        
        # Power
        try:
            df_power = pd.read_csv(self.paths['power'])
            today_power = df_power[df_power['date'] == today]
            if not today_power.empty:
                row = today_power.iloc[0]
                results['power'] = {
                    'date': row['date'],
                    'numbers': [int(row[f'n{i}']) for i in range(1, 7)],
                    'special': str(int(row['special'])).zfill(2)
                }
        except:
            pass
        
        # Lotto
        try:
            df_lotto = pd.read_csv(self.paths['lotto'])
            today_lotto = df_lotto[df_lotto['date'] == today]
            if not today_lotto.empty:
                row = today_lotto.iloc[0]
                results['lotto'] = {
                    'date': row['date'],
                    'numbers': [int(row[f'n{i}']) for i in range(1, 7)],
                    'special': str(int(row['special'])).zfill(2)
                }
        except:
            pass
        
        # Star3
        try:
            df_star3 = pd.read_csv(self.paths['star3'])
            today_star3 = df_star3[df_star3['date'] == today]
            if not today_star3.empty:
                row = today_star3.iloc[0]
                results['star3'] = {
                    'date': row['date'],
                    'numbers': [row['n1'], row['n2'], row['n3']]
                }
        except:
            pass
        
        # Star4
        try:
            df_star4 = pd.read_csv(self.paths['star4'])
            today_star4 = df_star4[df_star4['date'] == today]
            if not today_star4.empty:
                row = today_star4.iloc[0]
                results['star4'] = {
                    'date': row['date'],
                    'numbers': [row['n1'], row['n2'], row['n3'], row['n4']]
                }
        except:
            pass
        
        return results

if __name__ == "__main__":
    updater = AutoUpdater()
    updater.update_and_validate()
