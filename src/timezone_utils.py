# -*- coding: utf-8 -*-
"""
台灣時區工具模組
統一處理所有時間相關操作,確保使用台灣時區 (Asia/Taipei, UTC+8)
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional

# 台灣時區常數
TAIWAN_TZ = ZoneInfo("Asia/Taipei")


def get_taiwan_now() -> datetime:
    """
    取得當前台灣時間
    使用 UTC 時間轉換確保準確性
    
    Returns:
        datetime: 帶有台灣時區資訊的當前時間
    """
    return datetime.now(timezone.utc).astimezone(TAIWAN_TZ)


def to_taiwan_time(dt: datetime) -> datetime:
    """
    將任意時間轉換為台灣時區
    
    Args:
        dt: 要轉換的時間 (可以是 naive 或 aware datetime)
    
    Returns:
        datetime: 轉換後的台灣時區時間
    """
    if dt.tzinfo is None:
        # 如果是 naive datetime, 假設它已經是系統當地時間 (即台灣時間)
        # 這是為了兼容舊程式碼中產生的 datetime.now()
        dt = dt.replace(tzinfo=TAIWAN_TZ)
    return dt.astimezone(TAIWAN_TZ)


def format_taiwan_time(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化台灣時間為字串
    
    Args:
        dt: 要格式化的時間,若為 None 則使用當前時間
        fmt: 格式化字串,預設為 "%Y-%m-%d %H:%M:%S"
    
    Returns:
        str: 格式化後的時間字串
    """
    if dt is None:
        dt = get_taiwan_now()
    elif dt.tzinfo is None or dt.tzinfo != TAIWAN_TZ:
        dt = to_taiwan_time(dt)
    
    return dt.strftime(fmt)


def get_taiwan_date_str(dt: Optional[datetime] = None) -> str:
    """
    取得台灣日期字串 (YYYY-MM-DD)
    
    Args:
        dt: 要格式化的時間,若為 None 則使用當前時間
    
    Returns:
        str: 日期字串
    """
    return format_taiwan_time(dt, "%Y-%m-%d")


def get_taiwan_datetime_str(dt: Optional[datetime] = None) -> str:
    """
    取得台灣日期時間字串 (YYYY-MM-DD HH:MM:SS)
    
    Args:
        dt: 要格式化的時間,若為 None 則使用當前時間
    
    Returns:
        str: 日期時間字串
    """
    return format_taiwan_time(dt, "%Y-%m-%d %H:%M:%S")


def get_taiwan_timestamp_str(dt: Optional[datetime] = None) -> str:
    """
    取得台灣時間戳記字串 (YYYYMMDD_HHMMSS)
    用於檔案命名
    
    Args:
        dt: 要格式化的時間,若為 None 則使用當前時間
    
    Returns:
        str: 時間戳記字串
    """
    return format_taiwan_time(dt, "%Y%m%d_%H%M%S")


def get_taiwan_date_only_str(dt: Optional[datetime] = None) -> str:
    """
    取得台灣日期字串 (YYYYMMDD)
    用於日誌檔案命名
    
    Args:
        dt: 要格式化的時間,若為 None 則使用當前時間
    
    Returns:
        str: 日期字串
    """
    return format_taiwan_time(dt, "%Y%m%d")


def get_taiwan_isoformat(dt: Optional[datetime] = None) -> str:
    """
    取得台灣時間的 ISO 格式字串
    
    Args:
        dt: 要格式化的時間,若為 None 則使用當前時間
    
    Returns:
        str: ISO 格式時間字串
    """
    if dt is None:
        dt = get_taiwan_now()
    elif dt.tzinfo is None or dt.tzinfo != TAIWAN_TZ:
        dt = to_taiwan_time(dt)
    
    return dt.isoformat()


def taiwan_timedelta(days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> datetime:
    """
    從當前台灣時間計算時間差
    
    Args:
        days: 天數差
        hours: 小時差
        minutes: 分鐘差
        seconds: 秒數差
    
    Returns:
        datetime: 計算後的台灣時間
    """
    now = get_taiwan_now()
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return now + delta


if __name__ == "__main__":
    # 測試時區工具
    print("=" * 60)
    print("台灣時區工具測試")
    print("=" * 60)
    
    now = get_taiwan_now()
    print(f"\n當前台灣時間: {now}")
    print(f"時區資訊: {now.tzinfo}")
    print(f"UTC 偏移: {now.strftime('%z')}")
    
    print(f"\n格式化測試:")
    print(f"  日期: {get_taiwan_date_str()}")
    print(f"  日期時間: {get_taiwan_datetime_str()}")
    print(f"  時間戳記: {get_taiwan_timestamp_str()}")
    print(f"  日期 (檔名): {get_taiwan_date_only_str()}")
    print(f"  ISO 格式: {get_taiwan_isoformat()}")
    
    print(f"\n時間差測試:")
    print(f"  1天後: {format_taiwan_time(taiwan_timedelta(days=1))}")
    print(f"  1小時前: {format_taiwan_time(taiwan_timedelta(hours=-1))}")
