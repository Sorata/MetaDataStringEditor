"""
MetadataFile类 - 处理Unity global-metadata.dat文件的读取和解析
"""
import struct
import io
import os
import re
from typing import List, Optional
from utils import Logger, ProgressBar, safe_decode_utf8


class StringLiteral:
    """字符串字面量信息"""
    
    def __init__(self, length: int = 0, offset: int = 0):
        self.length = length
        self.offset = offset


class MetadataFile:
    """Metadata文件处理类"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_data: Optional[bytes] = None
        self.memory_stream: Optional[io.BytesIO] = None
        
        # 文件头信息
        self.string_literal_offset: int = 0
        self.string_literal_count: int = 0
        self.data_info_position: int = 0
        self.string_literal_data_offset: int = 0
        self.string_literal_data_count: int = 0
        
        # 字符串数据
        self.string_literals: List[StringLiteral] = []
        self.str_bytes: List[bytes] = []
        
        # 加载文件
        self._load_file()
    
    def _load_file(self):
        """加载文件到内存"""
        try:
            Logger.info("开始加载文件")
            with open(self.file_path, 'rb') as f:
                self.file_data = f.read()
            
            self.memory_stream = io.BytesIO(self.file_data)
            
            # 读取文件结构
            self._read_header()
            self._read_literals()
            self._read_string_bytes()
            
            Logger.info("文件加载完成")
            
        except Exception as e:
            Logger.error(f"加载文件失败: {str(e)}")
            raise
    
    def _read_header(self):
        """读取文件头"""
        Logger.info("读取文件头")
        
        self.memory_stream.seek(0)
        
        # 读取魔数
        vanity = struct.unpack('<I', self.memory_stream.read(4))[0]
        if vanity != 0xFAB11BAF:
            raise ValueError("文件格式错误：魔数检查失败")
        
        # 读取版本
        version = struct.unpack('<i', self.memory_stream.read(4))[0]
        
        # 读取字符串列表信息
        self.string_literal_offset = struct.unpack('<I', self.memory_stream.read(4))[0]
        self.string_literal_count = struct.unpack('<I', self.memory_stream.read(4))[0]
        
        # 记录当前位置，后面保存时需要更新这里的数据
        self.data_info_position = self.memory_stream.tell()
        
        # 读取字符串数据区信息
        self.string_literal_data_offset = struct.unpack('<I', self.memory_stream.read(4))[0]
        self.string_literal_data_count = struct.unpack('<I', self.memory_stream.read(4))[0]
        
        Logger.info(f"字符串数量: {self.string_literal_count // 8}")
        Logger.info(f"数据区偏移: {self.string_literal_data_offset}")
        Logger.info(f"数据区大小: {self.string_literal_data_count}")
    
    def _read_literals(self):
        """读取字符串字面量列表"""
        Logger.info("读取字符串字面量列表")
        
        string_count = self.string_literal_count // 8
        ProgressBar.set_max(string_count)
        
        self.memory_stream.seek(self.string_literal_offset)
        
        for i in range(string_count):
            length = struct.unpack('<I', self.memory_stream.read(4))[0]
            offset = struct.unpack('<I', self.memory_stream.read(4))[0]
            
            self.string_literals.append(StringLiteral(length, offset))
            ProgressBar.plus_one()
    
    def _read_string_bytes(self):
        """读取字符串字节数据"""
        Logger.info("读取字符串数据")
        
        # 创建待翻译目录
        translate_dir = "待翻译"
        if not os.path.exists(translate_dir):
            os.makedirs(translate_dir)
            Logger.info(f"创建目录: {translate_dir}")
        
        ProgressBar.set_max(len(self.string_literals))
        japanese_count = 0
        
        for i, literal in enumerate(self.string_literals):
            # 定位到字符串数据位置
            pos = self.string_literal_data_offset + literal.offset
            self.memory_stream.seek(pos)
            
            # 读取字符串字节
            str_data = self.memory_stream.read(literal.length)
            self.str_bytes.append(str_data)
            
            # 检测日语文本
            try:
                text = safe_decode_utf8(str_data)
                if self._is_japanese_text(text):
                    japanese_count += 1
                    # 输出到待翻译文件
                    filename = f"{i}.txt"
                    filepath = os.path.join(translate_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(text)
            except Exception as e:
                # 忽略解码错误
                pass
            
            ProgressBar.plus_one()
        
        if japanese_count > 0:
            Logger.info(f"检测到 {japanese_count} 个日语文本，已输出到 {translate_dir} 目录")
    
    def _is_japanese_text(self, text: str) -> bool:
        """检测文本是否包含日语字符"""
        if not text or len(text.strip()) == 0:
            return False
        
        # 日语字符范围：
        # 平假名: \u3040-\u309F
        # 片假名: \u30A0-\u30FF  
        # 汉字(CJK统一表意文字): \u4E00-\u9FAF
        # 日语标点符号: \u3000-\u303F
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]')
        
        # 检查是否包含日语字符
        if japanese_pattern.search(text):
            # 进一步过滤：确保不是纯数字、纯英文或过短的文本
            if len(text.strip()) >= 2 and not text.strip().isdigit() and not text.strip().isascii():
                return True
        
        return False
    
    def get_string_count(self) -> int:
        """获取字符串数量"""
        return len(self.str_bytes)
    
    def get_string(self, index: int) -> str:
        """获取指定索引的字符串"""
        if 0 <= index < len(self.str_bytes):
            return safe_decode_utf8(self.str_bytes[index])
        return ""
    
    def set_string_bytes(self, index: int, new_bytes: bytes):
        """设置指定索引的字符串字节数据"""
        if 0 <= index < len(self.str_bytes):
            self.str_bytes[index] = new_bytes
    
    def save_to_file(self, output_path: str):
        """保存修改后的文件"""
        Logger.info("开始保存文件")
        
        try:
            with open(output_path, 'wb') as f:
                # 先写入原始文件内容
                f.write(self.file_data)
            
            # 重新打开文件进行修改
            with open(output_path, 'r+b') as f:
                self._update_file(f)
            
            Logger.info("文件保存完成")
            
        except Exception as e:
            Logger.error(f"保存文件失败: {str(e)}")
            raise
    
    def _update_file(self, file_handle):
        """更新文件内容"""
        # 更新字符串字面量列表
        Logger.info("更新字符串字面量列表")
        ProgressBar.set_max(len(self.string_literals))
        
        file_handle.seek(self.string_literal_offset)
        
        total_size = 0
        for i, str_data in enumerate(self.str_bytes):
            # 更新字面量信息
            self.string_literals[i].offset = total_size
            self.string_literals[i].length = len(str_data)
            
            # 写入长度和偏移
            file_handle.write(struct.pack('<I', self.string_literals[i].length))
            file_handle.write(struct.pack('<I', self.string_literals[i].offset))
            
            total_size += len(str_data)
            ProgressBar.plus_one()
        
        # 进行4字节对齐
        aligned_size = total_size
        remainder = (self.string_literal_data_offset + total_size) % 4
        if remainder != 0:
            aligned_size += 4 - remainder
        
        # 检查是否需要重新定位数据区
        new_data_offset = self.string_literal_data_offset
        if aligned_size > self.string_literal_data_count:
            # 如果数据区后面还有其他数据，需要移动到文件末尾
            file_handle.seek(0, 2)  # 移动到文件末尾
            if self.string_literal_data_offset + self.string_literal_data_count < file_handle.tell():
                new_data_offset = file_handle.tell()
        
        # 写入字符串数据
        Logger.info("更新字符串数据")
        ProgressBar.set_max(len(self.str_bytes))
        
        file_handle.seek(new_data_offset)
        for str_data in self.str_bytes:
            file_handle.write(str_data)
            ProgressBar.plus_one()
        
        # 更新文件头中的数据区信息
        Logger.info("更新文件头")
        file_handle.seek(self.data_info_position)
        file_handle.write(struct.pack('<I', new_data_offset))
        file_handle.write(struct.pack('<I', aligned_size))
    
    def close(self):
        """关闭文件资源"""
        if self.memory_stream:
            self.memory_stream.close()
            self.memory_stream = None
        self.file_data = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()