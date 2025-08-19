"""
工具模块 - 提供日志记录和进度条功能
"""
import threading
from typing import Callable, Optional


class Logger:
    """日志记录器"""
    
    _callback = None
    _debug_mode = False
    
    @classmethod
    def set_callback(cls, callback):
        """设置回调函数，用于在主线程更新GUI"""
        cls._callback = callback
    
    @classmethod
    def set_debug_mode(cls, debug_mode: bool):
        """设置调试模式"""
        cls._debug_mode = debug_mode
    
    @classmethod
    def _log(cls, level: str, message: str):
        """内部日志方法"""
        # 如果不是调试模式，跳过DEBUG级别的日志
        if level == "DEBUG" and not cls._debug_mode:
            return
            
        log_message = f"[{level}] {message}"
        print(log_message)  # 同时输出到控制台
        
        if cls._callback:
            cls._callback(log_message)
    
    @classmethod
    def debug(cls, message: str):
        """调试日志"""
        cls._log("DEBUG", message)
    
    @classmethod
    def info(cls, message: str):
        """信息日志"""
        cls._log("INFO", message)
    
    @classmethod
    def warning(cls, message: str):
        """警告日志"""
        cls._log("WARNING", message)
    
    @classmethod
    def error(cls, message: str):
        """错误日志"""
        cls._log("ERROR", message)


class ProgressBar:
    """进度条管理器"""
    
    set_max_callback: Optional[Callable[[int], None]] = None
    update_callback: Optional[Callable[[int], None]] = None
    plus_one_callback: Optional[Callable[[], None]] = None
    
    @classmethod
    def set_callbacks(cls, 
                     set_max_cb: Optional[Callable[[int], None]] = None,
                     update_cb: Optional[Callable[[int], None]] = None,
                     plus_one_cb: Optional[Callable[[], None]] = None):
        """设置进度条回调函数"""
        if set_max_cb:
            cls.set_max_callback = set_max_cb
        if update_cb:
            cls.update_callback = update_cb
        if plus_one_cb:
            cls.plus_one_callback = plus_one_cb
    
    @classmethod
    def set_max(cls, max_value: int):
        """设置进度条最大值"""
        if cls.set_max_callback:
            cls.set_max_callback(max_value)
    
    @classmethod
    def update(cls, value: int):
        """更新进度条值"""
        if cls.update_callback:
            cls.update_callback(value)
    
    @classmethod
    def plus_one(cls):
        """进度条加1"""
        if cls.plus_one_callback:
            cls.plus_one_callback()


def safe_decode_utf8(data: bytes) -> str:
    """安全地解码UTF-8字节数据"""
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码或使用错误处理
        try:
            return data.decode('utf-8', errors='replace')
        except:
            return data.decode('latin-1', errors='replace')


def safe_encode_utf8(text: str) -> bytes:
    """安全地编码为UTF-8字节数据"""
    try:
        return text.encode('utf-8')
    except UnicodeEncodeError:
        return text.encode('utf-8', errors='replace')