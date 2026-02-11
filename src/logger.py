"""
539 AI 預測系統 - 日誌模組
提供統一的日誌記錄功能,支援控制台輸出與檔案記錄
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from src.timezone_utils import get_taiwan_date_only_str

class Logger:
    """統一的日誌管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        
        # 建立 logs 目錄
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 設定日誌檔案名稱 (按日期)
        today = get_taiwan_date_only_str()
        self.log_file = self.log_dir / f"539_ai_{today}.log"
        
        # 設定 logger
        self.logger = logging.getLogger("539_AI")
        self.logger.setLevel(logging.DEBUG)
        
        # 清除既有的 handlers (避免重複)
        self.logger.handlers.clear()
        
        # 檔案 handler (詳細記錄)
        file_handler = logging.FileHandler(
            self.log_file, 
            encoding='utf-8',
            mode='a'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 控制台 handler (簡潔輸出)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '[%(levelname)s] %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 加入 handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 記錄啟動訊息
        self.info("=" * 60)
        self.info("539 AI 預測系統啟動")
        self.info(f"日誌檔案: {self.log_file}")
        self.info("=" * 60)
    
    def debug(self, message):
        """除錯訊息"""
        self.logger.debug(message)
    
    def info(self, message):
        """一般訊息"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告訊息"""
        self.logger.warning(message)
    
    def error(self, message):
        """錯誤訊息"""
        self.logger.error(message)
    
    def critical(self, message):
        """嚴重錯誤訊息"""
        self.logger.critical(message)
    
    def section(self, title):
        """區段標題"""
        self.info("")
        self.info("=" * 60)
        self.info(f"  {title}")
        self.info("=" * 60)
    
    def step(self, step_num, description):
        """步驟訊息"""
        self.info(f"\n[步驟 {step_num}] {description}")
    
    def result(self, key, value):
        """結果訊息"""
        self.info(f"  → {key}: {value}")
    
    def success(self, message):
        """成功訊息"""
        self.info(f"✓ {message}")
    
    def fail(self, message):
        """失敗訊息"""
        self.error(f"✗ {message}")

# 建立全域 logger 實例
logger = Logger()

if __name__ == "__main__":
    # 測試日誌功能
    logger.section("測試日誌系統")
    logger.step(1, "測試各種日誌等級")
    logger.debug("這是除錯訊息 (僅記錄到檔案)")
    logger.info("這是一般訊息")
    logger.warning("這是警告訊息")
    logger.error("這是錯誤訊息")
    logger.critical("這是嚴重錯誤訊息")
    
    logger.step(2, "測試結果輸出")
    logger.result("訓練集筆數", 313)
    logger.result("預測日期", "2026-01-01 週四")
    
    logger.step(3, "測試成功/失敗訊息")
    logger.success("資料載入成功")
    logger.fail("網路連線失敗")
    
    logger.info(f"\n日誌已儲存至: {logger.log_file}")
