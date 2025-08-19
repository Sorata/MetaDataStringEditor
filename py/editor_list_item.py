"""
EditorListItem类 - 管理字符串编辑项的状态和操作
"""
from typing import Optional
from utils import safe_decode_utf8, safe_encode_utf8


class EditorListItem:
    """编辑列表项，管理单个字符串的编辑状态"""
    
    def __init__(self, original_bytes: bytes, index: int):
        self.index = index
        self.original_bytes = original_bytes
        self.new_bytes: Optional[bytes] = None
        self.is_edited = False
        
        # 缓存原始字符串内容
        self._original_text = safe_decode_utf8(original_bytes)
    
    @property
    def original_text(self) -> str:
        """获取原始字符串内容"""
        return self._original_text
    
    @property
    def current_text(self) -> str:
        """获取当前字符串内容（如果已编辑则返回新内容，否则返回原始内容）"""
        if self.is_edited and self.new_bytes is not None:
            return safe_decode_utf8(self.new_bytes)
        return self._original_text
    
    @property
    def current_bytes(self) -> bytes:
        """获取当前字符串字节数据"""
        if self.is_edited and self.new_bytes is not None:
            return self.new_bytes
        return self.original_bytes
    
    @property
    def status_text(self) -> str:
        """获取状态文本"""
        return "*" if self.is_edited else ""
    
    def set_new_text(self, new_text: str):
        """设置新的字符串内容"""
        # 移除回车符（与C#版本保持一致）
        cleaned_text = new_text.replace('\r', '')
        new_bytes = safe_encode_utf8(cleaned_text)
        
        # 检查是否与原始内容相同
        if new_bytes == self.original_bytes:
            # 如果新内容与原始内容相同，则取消编辑状态
            self.discard_changes()
        else:
            # 设置新内容
            self.new_bytes = new_bytes
            self.is_edited = True
    
    def discard_changes(self):
        """丢弃修改，恢复到原始状态"""
        self.new_bytes = None
        self.is_edited = False
    
    def match_keyword(self, keyword: str) -> bool:
        """检查是否匹配搜索关键词（不区分大小写）"""
        if not keyword:
            return False
        
        keyword_lower = keyword.lower()
        
        # 搜索原始内容
        if keyword_lower in self.original_text.lower():
            return True
        
        # 如果有修改内容，也搜索修改后的内容
        if self.is_edited and self.new_bytes is not None:
            current_text = safe_decode_utf8(self.new_bytes)
            if keyword_lower in current_text.lower():
                return True
        
        return False
    
    def get_display_data(self) -> tuple:
        """获取用于显示的数据元组 (索引, 原始内容, 当前内容, 状态)"""
        return (
            str(self.index),
            self.original_text,
            self.current_text if self.is_edited else "",
            self.status_text
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        status = " (已修改)" if self.is_edited else ""
        return f"[{self.index}] {self.original_text[:50]}...{status}"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"EditorListItem(index={self.index}, edited={self.is_edited}, text='{self.original_text[:30]}...')"