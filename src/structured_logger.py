# -*- coding: utf-8 -*-
"""
結構化日誌系統
提供多種專用日誌類型的統一管理
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import traceback as tb


class StructuredLogger:
    """結構化日誌管理器"""
    
    LOG_TYPES = {
        'execution_errors': 'logs/execution_errors.log',
        'modifications': 'logs/modifications.log',
        'operations': 'logs/operations.log',
        'backups': 'logs/backups.log',
        'analysis': 'logs/analysis.log'
    }
    
    def __init__(self):
        """初始化日誌系統"""
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # 建立各類型日誌記錄器
        self.loggers = {}
        for log_type, log_file in self.LOG_TYPES.items():
            self.loggers[log_type] = self._create_logger(log_type, log_file)
    
    def _create_logger(self, name: str, log_file: str) -> logging.Logger:
        """建立日誌記錄器"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # 避免重複添加 handler
        if logger.handlers:
            return logger
        
        # 檔案 handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 格式化
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        return logger
    
    def log_execution_error(
        self, 
        error_type: str, 
        error_message: str, 
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """記錄執行異常"""
        logger = self.loggers['execution_errors']
        
        log_entry = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        if stack_trace:
            log_entry['stack_trace'] = stack_trace
        
        logger.error(json.dumps(log_entry, ensure_ascii=False, indent=2))
    
    def log_modification(
        self,
        modification_type: str,
        target: str,
        old_value: Any,
        new_value: Any,
        reason: Optional[str] = None
    ):
        """記錄配置修改"""
        logger = self.loggers['modifications']
        
        log_entry = {
            'modification_type': modification_type,
            'target': target,
            'old_value': str(old_value),
            'new_value': str(new_value),
            'reason': reason or 'N/A'
        }
        
        logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
    
    def log_operation(
        self,
        operation_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        duration_seconds: Optional[float] = None
    ):
        """記錄自動任務執行"""
        logger = self.loggers['operations']
        
        log_entry = {
            'operation_type': operation_type,
            'status': status,
            'details': details or {},
        }
        
        if duration_seconds is not None:
            log_entry['duration_seconds'] = round(duration_seconds, 2)
        
        logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
    
    def log_backup(
        self,
        backup_type: str,
        source_path: str,
        backup_path: str,
        file_size_bytes: Optional[int] = None,
        success: bool = True
    ):
        """記錄備份操作"""
        logger = self.loggers['backups']
        
        log_entry = {
            'backup_type': backup_type,
            'source_path': source_path,
            'backup_path': backup_path,
            'success': success
        }
        
        if file_size_bytes is not None:
            log_entry['file_size_bytes'] = file_size_bytes
        
        logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
    
    def log_analysis(
        self,
        analysis_type: str,
        results: Dict[str, Any],
        recommendations: Optional[list] = None
    ):
        """記錄分析結果"""
        logger = self.loggers['analysis']
        
        log_entry = {
            'analysis_type': analysis_type,
            'results': results,
            'recommendations': recommendations or []
        }
        
        logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))


# 建立全域實例
structured_logger = StructuredLogger()


if __name__ == "__main__":
    # 測試結構化日誌系統
    print("=" * 60)
    print("Structured Logger Test")
    print("=" * 60)
    
    # 測試 1: 執行異常日誌
    print("\n[Test 1] Logging execution error...")
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        structured_logger.log_execution_error(
            error_type=type(e).__name__,
            error_message=str(e),
            stack_trace=tb.format_exc(),
            context={'module': 'test', 'function': 'main'}
        )
    
    # 測試 2: 修改日誌
    print("[Test 2] Logging modification...")
    structured_logger.log_modification(
        modification_type='weight_update',
        target='group1.hot_weight',
        old_value=0.4,
        new_value=0.5,
        reason='Backtest accuracy improvement'
    )
    
    # 測試 3: 運行日誌
    print("[Test 3] Logging operation...")
    structured_logger.log_operation(
        operation_type='auto_prediction',
        status='success',
        details={'predicted_numbers': [5, 12, 18, 25, 33]},
        duration_seconds=12.5
    )
    
    # 測試 4: 備份日誌
    print("[Test 4] Logging backup...")
    structured_logger.log_backup(
        backup_type='training_data',
        source_path='data/539_train.csv',
        backup_path='data/backups/539_train_20260210.csv',
        file_size_bytes=9091,
        success=True
    )
    
    # 測試 5: 分析日誌
    print("[Test 5] Logging analysis...")
    structured_logger.log_analysis(
        analysis_type='daily_performance',
        results={
            'total_predictions': 10,
            'avg_accuracy': 0.28,
            'best_model': 'XGBoost'
        },
        recommendations=[
            'Increase hot_weight by 0.05',
            'Enable time_series features'
        ]
    )
    
    print("\n" + "=" * 60)
    print("Test completed! Check logs/ directory")
    print("=" * 60)
