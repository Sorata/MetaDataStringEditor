"""
编辑对话框 - 用于编辑单个字符串的对话框窗口
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from editor_list_item import EditorListItem


class EditDialog:
    """编辑对话框类"""
    
    def __init__(self, parent: tk.Tk, editor_item: EditorListItem):
        self.parent = parent
        self.editor_item = editor_item
        self.result = False
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"编辑字符串 - 索引 {editor_item.index}")
        self.dialog.geometry("470x430")
        self.dialog.resizable(True, True)
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
        
        # 设置焦点
        self.text_widget.focus_set()
        
        # 绑定事件
        self._setup_bindings()
    
    def _center_window(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        
        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 使用设定的对话框大小
        dialog_width = 470
        dialog_height = 430
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 信息标签
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"索引: {self.editor_item.index}").pack(side=tk.LEFT)
        
        status_text = self.editor_item.status_text
        status_color = "red" if self.editor_item.is_edited else "black"
        status_label = ttk.Label(info_frame, text=f"状态: {status_text}", foreground=status_color)
        status_label.pack(side=tk.RIGHT)
        
        # 原始内容显示
        original_frame = ttk.LabelFrame(main_frame, text="原始内容", padding=5)
        original_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.original_text = tk.Text(original_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        original_scrollbar = ttk.Scrollbar(original_frame, orient=tk.VERTICAL, command=self.original_text.yview)
        self.original_text.configure(yscrollcommand=original_scrollbar.set)
        
        self.original_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        original_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设置原始内容
        self.original_text.config(state=tk.NORMAL)
        self.original_text.insert(tk.END, self.editor_item.original_text)
        self.original_text.config(state=tk.DISABLED)
        
        # 编辑内容
        edit_frame = ttk.LabelFrame(main_frame, text="编辑内容", padding=5)
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_widget = tk.Text(edit_frame, height=8, wrap=tk.WORD)
        edit_scrollbar = ttk.Scrollbar(edit_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=edit_scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        edit_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 设置当前内容
        self.text_widget.insert(tk.END, self.editor_item.current_text)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 按钮
        ttk.Button(button_frame, text="保存", command=self._save_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="放弃此次修改", command=self._discard_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="还原该串的修改", command=self._revert_changes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT)
        
        # 字符计数标签
        self.char_count_var = tk.StringVar()
        self.char_count_label = ttk.Label(button_frame, textvariable=self.char_count_var)
        self.char_count_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # 更新字符计数
        self._update_char_count()
        
        # 绑定文本变化事件
        self.text_widget.bind("<KeyRelease>", self._on_text_changed)
        self.text_widget.bind("<Button-1>", self._on_text_changed)
    
    def _setup_bindings(self):
        """设置键盘绑定"""
        self.dialog.bind("<Control-s>", lambda e: self._save_changes())
        self.dialog.bind("<Escape>", lambda e: self._cancel())
        self.dialog.bind("<Control-z>", lambda e: self._revert_changes())
        
        # 处理窗口关闭事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel)
    
    def _on_text_changed(self, event=None):
        """文本内容改变事件"""
        self._update_char_count()
    
    def _update_char_count(self):
        """更新字符计数显示"""
        content = self.text_widget.get("1.0", tk.END + "-1c")  # 去掉末尾的换行符
        char_count = len(content)
        byte_count = len(content.encode('utf-8'))
        self.char_count_var.set(f"字符: {char_count}, 字节: {byte_count}")
    
    def _save_changes(self):
        """保存修改"""
        try:
            # 获取文本内容
            content = self.text_widget.get("1.0", tk.END + "-1c")  # 去掉末尾的换行符
            
            # 检查内容是否过长
            if len(content.encode('utf-8')) > 10000:  # 限制为10KB
                if not messagebox.askyesno("警告", "文本内容较长，可能影响游戏性能。确定要保存吗？"):
                    return
            
            # 设置新内容
            self.editor_item.set_new_text(content)
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{str(e)}")
    
    def _discard_changes(self):
        """放弃此次修改"""
        self.result = False
        self.dialog.destroy()
    
    def _revert_changes(self):
        """还原该串的修改"""
        if self.editor_item.is_edited:
            if messagebox.askyesno("确认", "确定要还原该字符串的所有修改吗？"):
                self.editor_item.discard_changes()
                
                # 更新文本框内容
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert("1.0", self.editor_item.current_text)
                
                # 更新状态显示
                self._update_status_display()
                
                messagebox.showinfo("成功", "已还原修改")
        else:
            messagebox.showinfo("提示", "该字符串没有修改")
    
    def _update_status_display(self):
        """更新状态显示"""
        # 这里可以更新状态标签，但由于标签已经创建，需要重新获取状态
        # 简单起见，我们可以重新创建信息框架，但这里先保持简单
        pass
    
    def _cancel(self):
        """取消编辑"""
        # 检查是否有未保存的修改
        current_content = self.text_widget.get("1.0", tk.END + "-1c")
        if current_content != self.editor_item.current_text:
            if messagebox.askyesno("确认", "有未保存的修改，确定要取消吗？"):
                self.result = False
                self.dialog.destroy()
        else:
            self.result = False
            self.dialog.destroy()
    
    def show(self) -> bool:
        """显示对话框并返回结果"""
        # 等待对话框关闭
        self.dialog.wait_window()
        return self.result


class BatchEditDialog:
    """批量编辑对话框"""
    
    def __init__(self, parent: tk.Tk, editor_items: list):
        self.parent = parent
        self.editor_items = editor_items
        self.result = False
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"批量编辑 - {len(editor_items)} 个项目")
        self.dialog.geometry("500x300")
        self.dialog.resizable(True, True)
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self._center_window()
        
        # 创建界面
        self._create_widgets()
    
    def _center_window(self):
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        
        # 获取父窗口位置和大小
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 获取对话框大小
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 信息标签
        info_label = ttk.Label(main_frame, text=f"将对 {len(self.editor_items)} 个字符串执行批量操作")
        info_label.pack(pady=(0, 10))
        
        # 操作选择
        operation_frame = ttk.LabelFrame(main_frame, text="选择操作", padding=10)
        operation_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.operation_var = tk.StringVar(value="replace")
        
        ttk.Radiobutton(operation_frame, text="查找替换", variable=self.operation_var, value="replace").pack(anchor=tk.W)
        ttk.Radiobutton(operation_frame, text="添加前缀", variable=self.operation_var, value="prefix").pack(anchor=tk.W)
        ttk.Radiobutton(operation_frame, text="添加后缀", variable=self.operation_var, value="suffix").pack(anchor=tk.W)
        ttk.Radiobutton(operation_frame, text="转换大小写", variable=self.operation_var, value="case").pack(anchor=tk.W)
        
        # 参数输入
        params_frame = ttk.LabelFrame(main_frame, text="参数", padding=10)
        params_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 查找文本
        ttk.Label(params_frame, text="查找:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.find_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.find_var, width=40).grid(row=0, column=1, sticky=tk.EW, pady=2, padx=(5, 0))
        
        # 替换文本
        ttk.Label(params_frame, text="替换为:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.replace_var = tk.StringVar()
        ttk.Entry(params_frame, textvariable=self.replace_var, width=40).grid(row=1, column=1, sticky=tk.EW, pady=2, padx=(5, 0))
        
        params_frame.grid_columnconfigure(1, weight=1)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="执行", command=self._execute).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="取消", command=self._cancel).pack(side=tk.RIGHT)
        
        # 绑定事件
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel)
    
    def _execute(self):
        """执行批量操作"""
        operation = self.operation_var.get()
        find_text = self.find_var.get()
        replace_text = self.replace_var.get()
        
        try:
            count = 0
            
            for item in self.editor_items:
                current_text = item.current_text
                new_text = current_text
                
                if operation == "replace":
                    if find_text in current_text:
                        new_text = current_text.replace(find_text, replace_text)
                elif operation == "prefix":
                    new_text = find_text + current_text
                elif operation == "suffix":
                    new_text = current_text + find_text
                elif operation == "case":
                    if find_text.lower() == "upper":
                        new_text = current_text.upper()
                    elif find_text.lower() == "lower":
                        new_text = current_text.lower()
                    elif find_text.lower() == "title":
                        new_text = current_text.title()
                
                if new_text != current_text:
                    item.set_new_text(new_text)
                    count += 1
            
            messagebox.showinfo("完成", f"已处理 {count} 个字符串")
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"批量操作失败:\n{str(e)}")
    
    def _cancel(self):
        """取消操作"""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result