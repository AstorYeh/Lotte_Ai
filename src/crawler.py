import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime
from src.logger import logger

def parse_roc_date(date_str):
    """
    Parse ROC date string (e.g., 113/01/01) to Gregorian date string (e.g., 2024-01-01).
    """
    try:
        match = re.match(r'(\d+)/(\d+)/(\d+)', date_str)
        if match:
            roc_year, month, day = map(int, match.groups())
            year = roc_year + 1911
            return f"{year}-{month:02d}-{day:02d}"
    except Exception as e:
        print(f"Date parsing error: {date_str}, {e}")
    return None

def fetch_data(url="https://www.pilio.idv.tw/lto539/list539APP.asp", split_by_year=True):
    """
    抓取 539 歷史資料並根據年份分離訓練集與測試集
    
    Args:
        url: 資料來源網址
        split_by_year: 是否按年份分離資料 (預設 True)
                      - 訓練集: 2025 年資料 -> data/539_train.csv
                      - 測試集: 2026 年後資料 -> data/539_test.csv
                      - 完整資料: 所有資料 -> data/539_history.csv
    
    Returns:
        dict: {'train': DataFrame, 'test': DataFrame, 'full': DataFrame}
    """
    logger.section("資料爬蟲")
    logger.info(f"目標網址: {url}")
    logger.info(f"資料分離模式: {'啟用' if split_by_year else '停用'}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logger.info("開始抓取資料...")
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = 'utf-8' 
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        data = []
        text = soup.get_text()
        
        # Pattern: Date (ROC) followed by 5 numbers.
        pattern = re.compile(r'(\d{2,3}/\d{2}/\d{2}).*?(\d{2})[^\d]+(\d{2})[^\d]+(\d{2})[^\d]+(\d{2})[^\d]+(\d{2})')
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = pattern.search(line)
            if match:
                date_str = match.group(1)
                nums = match.group(2, 3, 4, 5, 6)
                
                std_date = parse_roc_date(date_str)
                if std_date:
                    # Sort numbers to ensure consistency
                    sorted_nums = sorted(list(nums))
                    data.append({
                        'date': std_date,
                        'numbers': ','.join(sorted_nums)
                    })
        
        if data:
            logger.success(f"成功解析 {len(data)} 筆原始資料")
            df = pd.DataFrame(data)
            # Remove duplicates based on date
            df = df.drop_duplicates(subset=['date'])
            logger.info(f"去除重複後剩餘 {len(df)} 筆")
            # Sort by date
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date').reset_index(drop=True)
            logger.info(f"日期範圍: {df['date'].min()} ~ {df['date'].max()}")
            
            os.makedirs('data', exist_ok=True)
            
            if split_by_year:
                # 分離訓練集 (2025) 與測試集 (2026+)
                train_df = df[df['date'].dt.year == 2025].copy()
                test_df = df[df['date'].dt.year >= 2026].copy()
                
                # 格式化日期為字串
                train_df['date'] = train_df['date'].dt.strftime('%Y-%m-%d')
                test_df['date'] = test_df['date'].dt.strftime('%Y-%m-%d')
                df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                
                # 儲存訓練集
                train_path = 'data/539_train.csv'
                train_df.to_csv(train_path, index=False)
                logger.result("訓練集 (2025)", f"{len(train_df)} 筆 → {train_path}")
                
                # 儲存測試集
                test_path = 'data/539_test.csv'
                test_df.to_csv(test_path, index=False)
                logger.result("測試集 (2026+)", f"{len(test_df)} 筆 → {test_path}")
                
                # 儲存完整資料
                full_path = 'data/539_history.csv'
                df.to_csv(full_path, index=False)
                logger.result("完整資料", f"{len(df)} 筆 → {full_path}")
                logger.success("資料儲存完成")
                
                return {
                    'train': train_df,
                    'test': test_df,
                    'full': df
                }
            else:
                # 不分離,僅儲存完整資料
                df['date'] = df['date'].dt.strftime('%Y-%m-%d')
                output_path = 'data/539_history.csv'
                df.to_csv(output_path, index=False)
                print(f"Successfully saved {len(df)} records to {output_path}")
                return df
        else:
            logger.warning("未找到符合格式的資料")
            logger.warning("網站結構可能已變更,請檢查資料來源")
            return None

    except Exception as e:
        logger.error(f"資料抓取失敗: {e}")
        return None

def fetch_single_date(target_date, url="https://www.pilio.idv.tw/lto539/list539APP.asp"):
    """
    抓取指定日期的開獎號碼
    
    Args:
        target_date: 目標日期 (datetime 或 str, 格式: YYYY-MM-DD)
        url: 資料來源網址
    
    Returns:
        list: 開獎號碼列表 [n1, n2, n3, n4, n5] 或 None (找不到)
    """
    # 轉換日期格式
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
    
    target_str = target_date.strftime("%Y-%m-%d")
    
    logger.info(f"查詢日期: {target_str}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = 'utf-8'
        
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text()
        
        # Pattern: Date (ROC) followed by 5 numbers
        pattern = re.compile(r'(\d{2,3}/\d{2}/\d{2}).*?(\d{2})[^\d]+(\d{2})[^\d]+(\d{2})[^\d]+(\d{2})[^\d]+(\d{2})')
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = pattern.search(line)
            if match:
                date_str = match.group(1)
                nums = match.group(2, 3, 4, 5, 6)
                
                std_date = parse_roc_date(date_str)
                if std_date == target_str:
                    # 找到目標日期
                    numbers = [int(n) for n in nums]
                    logger.success(f"找到 {target_str} 的開獎號碼: {numbers}")
                    return numbers
        
        logger.warning(f"找不到 {target_str} 的開獎記錄")
        return None
        
    except requests.exceptions.Timeout:
        logger.error("請求超時,請檢查網路連線")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"請求失敗: {e}")
        return None
    except Exception as e:
        logger.error(f"未預期的錯誤: {e}")
        return None

if __name__ == "__main__":
    # 測試指定日期抓取
    test_date = "2025-02-04"
    result = fetch_single_date(test_date)
    if result:
        print(f"開獎號碼: {result}")
    else:
        print("查詢失敗")
    
    # 原有的完整抓取測試
    fetch_data()
