# MetaData String Editor - Python版本

这是一个用于编辑Unity `global-metadata.dat` 文件中字符串的GUI工具，使用Python和tkinter重构自原始的C# Windows Forms版本。

## 功能特性

- 读取和解析Unity的global-metadata.dat文件
- 图形化界面显示所有字符串
- 搜索包含特定关键词的字符串（支持快捷键）
- 编辑字符串内容
- 保存修改后的文件（支持另存为）
- 跨平台支持（Windows、Linux、macOS）

## 项目结构

```
py/
├── main.py                 # 程序入口点
├── metadata_file.py        # metadata文件处理类
├── editor_list_item.py     # 编辑项管理类
├── main_window.py          # 主窗口GUI
├── edit_dialog.py          # 编辑对话框GUI
├── utils.py               # 工具函数（日志、进度条等）
├── requirements.txt        # 依赖文件
└── README.md              # 说明文档
```

## 安装和运行

### 前提条件

- Python 3.7 或更高版本
- tkinter（通常随Python一起安装）

### 运行程序

```bash
# 进入py目录
cd py

# 直接运行
python main.py

# 或者指定文件路径
python main.py path/to/global-metadata.dat
```

## 使用方法

1. **加载文件**：点击"加载文件"按钮或使用菜单选择global-metadata.dat文件
2. **浏览字符串**：在列表中查看所有字符串，显示索引、原始内容、修改内容和状态
3. **搜索字符串**：
   - 在搜索框中输入关键词
   - 使用Ctrl+F快速聚焦搜索框
   - 使用F3/Shift+F3导航到下一个/上一个匹配项
4. **编辑字符串**：
   - 双击列表项或右键选择"编辑"
   - 在弹出的对话框中修改内容
   - 点击"保存"确认修改或"取消"放弃修改
5. **保存文件**：使用菜单中的"另存为"保存修改后的文件

## 快捷键

- `Ctrl+F` - 聚焦搜索框
- `F3` - 查找下一个
- `Shift+F3` - 查找上一个
- `Esc` - 清除搜索（在搜索框中）
- `Enter` - 在搜索框中按回车查找下一个

## 注意事项

1. **备份原文件**：在编辑之前，请务必备份原始的global-metadata.dat文件
2. **字符串长度**：修改后的字符串可以比原字符串更长或更短
3. **编码格式**：所有字符串使用UTF-8编码
4. **文件完整性**：程序会自动处理文件结构的更新，确保修改后的文件格式正确

## 技术说明

本工具基于对Unity IL2CPP metadata文件格式的理解，参考了[Il2CppDumper](https://github.com/Perfare/Il2CppDumper)项目的实现。

文件结构包括：
- 文件头：包含版本信息和各区域的偏移量
- 字符串列表区：存储每个字符串的长度和偏移量信息
- 字符串数据区：存储实际的字符串内容

修改时会更新字符串列表区的信息，并根据需要重新组织数据区的内容。