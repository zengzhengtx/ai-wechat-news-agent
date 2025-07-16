"""
日期时间处理工具
统一处理timezone-aware和naive datetime对象
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union


def normalize_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """
    标准化datetime对象，确保都是timezone-aware的UTC时间
    
    Args:
        dt: 输入的datetime对象
        
    Returns:
        Optional[datetime]: 标准化后的datetime对象（UTC时区）
    """
    if dt is None:
        return None
    
    # 如果是naive datetime，假设为UTC
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    
    # 如果已经有时区信息，转换为UTC
    return dt.astimezone(timezone.utc)


def safe_datetime_subtract(dt1: Optional[datetime], dt2: Optional[datetime]) -> Optional[timedelta]:
    """
    安全的datetime相减操作
    
    Args:
        dt1: 第一个datetime对象
        dt2: 第二个datetime对象
        
    Returns:
        Optional[timedelta]: 时间差，如果任一参数为None则返回None
    """
    if dt1 is None or dt2 is None:
        return None
    
    # 标准化两个datetime对象
    normalized_dt1 = normalize_datetime(dt1)
    normalized_dt2 = normalize_datetime(dt2)
    
    if normalized_dt1 is None or normalized_dt2 is None:
        return None
    
    return normalized_dt1 - normalized_dt2


def safe_datetime_compare(dt1: Optional[datetime], dt2: Optional[datetime]) -> bool:
    """
    安全的datetime比较操作 (dt1 > dt2)
    
    Args:
        dt1: 第一个datetime对象
        dt2: 第二个datetime对象
        
    Returns:
        bool: dt1 > dt2，如果任一参数为None则返回False
    """
    if dt1 is None or dt2 is None:
        return False
    
    # 标准化两个datetime对象
    normalized_dt1 = normalize_datetime(dt1)
    normalized_dt2 = normalize_datetime(dt2)
    
    if normalized_dt1 is None or normalized_dt2 is None:
        return False
    
    return normalized_dt1 > normalized_dt2


def get_utc_now() -> datetime:
    """
    获取当前UTC时间
    
    Returns:
        datetime: 当前UTC时间（timezone-aware）
    """
    return datetime.now(timezone.utc)


def days_since(dt: Optional[datetime]) -> Optional[int]:
    """
    计算距离指定时间的天数
    
    Args:
        dt: 指定的datetime对象
        
    Returns:
        Optional[int]: 天数，如果dt为None则返回None
    """
    if dt is None:
        return None
    
    time_diff = safe_datetime_subtract(get_utc_now(), dt)
    if time_diff is None:
        return None
    
    return time_diff.days


def is_recent(dt: Optional[datetime], days: int = 30) -> bool:
    """
    判断时间是否在最近指定天数内
    
    Args:
        dt: 要检查的datetime对象
        days: 天数阈值
        
    Returns:
        bool: 是否在最近指定天数内
    """
    days_ago = days_since(dt)
    if days_ago is None:
        return False
    
    return days_ago <= days


def format_datetime_for_display(dt: Optional[datetime]) -> str:
    """
    格式化datetime对象用于显示
    
    Args:
        dt: datetime对象
        
    Returns:
        str: 格式化后的字符串
    """
    if dt is None:
        return "未知时间"
    
    normalized_dt = normalize_datetime(dt)
    if normalized_dt is None:
        return "无效时间"
    
    # 转换为本地时间显示
    local_dt = normalized_dt.astimezone()
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")


def parse_iso_datetime(date_str: str) -> Optional[datetime]:
    """
    解析ISO格式的日期时间字符串
    
    Args:
        date_str: ISO格式的日期时间字符串
        
    Returns:
        Optional[datetime]: 解析后的datetime对象
    """
    if not date_str:
        return None
    
    try:
        # 尝试解析ISO格式
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return normalize_datetime(dt)
    except (ValueError, AttributeError):
        try:
            # 尝试其他常见格式
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            return normalize_datetime(dt)
        except ValueError:
            return None
