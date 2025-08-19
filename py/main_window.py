"""
主窗口GUI - 使用tkinter实现MetaData String Editor的主界面
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
import threading
from typing import List, Optional
import os

from metadata_file import MetadataFile
from editor_list_item import EditorListItem
from edit_dialog import EditDialog
from utils import Logger, ProgressBar


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MetaData String Editor - Python版本")
        self.root.geometry("1000x700")
        
        # 数据
        self.metadata_file: Optional[MetadataFile] = None
        self.editor_items: List[EditorListItem] = []
        self.search_results: List[int] = []
        self.current_search_index = -1
        self.last_search_keyword = ""
        
        # 状态
        self.is_loading = False
        self.is_saving = False
        
        # 创建界面
        self._create_widgets()
        self._setup_bindings()
        self._setup_callbacks()
        
        # 设置初始状态
        self._update_search_display()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 创建菜单栏
        self._create_menu()
        
        # 创建工具栏
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 文件操作按钮
        ttk.Button(toolbar_frame, text="加载文件", command=self._load_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="另存为", command=self._save_file_as).pack(side=tk.LEFT, padx=(0, 10))
        
        # 搜索框
        ttk.Label(toolbar_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # 搜索按钮
        ttk.Button(toolbar_frame, text="上一个", command=self._search_previous).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar_frame, text="下一个", command=self._search_next).pack(side=tk.LEFT, padx=(0, 5))
        
        # 搜索计数显示
        self.search_count_var = tk.StringVar()
        self.search_count_label = ttk.Label(toolbar_frame, textvariable=self.search_count_var)
        self.search_count_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 创建主要内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建列表视图
        self._create_listview(main_frame)
        
        # 创建状态栏
        self._create_statusbar()
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="加载文件", command=self._load_file, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="另存为", command=self._save_file_as, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="关闭文件", command=self._close_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        
        # 编辑菜单
        edit_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="查找", command=self._focus_search, accelerator="Ctrl+F")
        edit_menu.add_command(label="查找下一个", command=self._search_next, accelerator="F3")
        edit_menu.add_command(label="查找上一个", command=self._search_previous, accelerator="Shift+F3")
        
        # 帮助菜单
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
    
    def _create_listview(self, parent):
        """创建列表视图"""
        # 创建Treeview
        columns = ("索引", "原始内容", "当前内容", "状态")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=20)
        
        # 设置列标题和宽度
        self.tree.heading("索引", text="索引")
        self.tree.heading("原始内容", text="原始内容")
        self.tree.heading("当前内容", text="当前内容")
        self.tree.heading("状态", text="状态")
        
        self.tree.column("索引", width=80, minwidth=60)
        self.tree.column("原始内容", width=400, minwidth=200)
        self.tree.column("当前内容", width=400, minwidth=200)
        self.tree.column("状态", width=60, minwidth=40)
        
        # 创建滚动条
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # 创建右键菜单
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self._edit_selected_item)
        
        # 绑定事件
        self.tree.bind("<Double-1>", self._on_item_double_click)
        self.tree.bind("<Button-3>", self._on_item_right_click)
    
    def _create_statusbar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def _setup_bindings(self):
        """设置键盘绑定"""
        self.root.bind("<Control-o>", lambda e: self._load_file())
        self.root.bind("<Control-s>", lambda e: self._save_file_as())
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<F3>", lambda e: self._search_next())
        self.root.bind("<Shift-F3>", lambda e: self._search_previous())
        self.root.bind("<Escape>", lambda e: self._clear_search())
        
        # 搜索框事件
        self.search_var.trace("w", self._on_search_changed)
        self.search_entry.bind("<Return>", lambda e: self._search_next())
    
    def _setup_callbacks(self):
        """设置回调函数"""
        Logger.set_callback(self._update_status)
        ProgressBar.set_callbacks(
            set_max_cb=self._set_progress_max,
            update_cb=self._update_progress,
            plus_one_cb=self._progress_plus_one
        )
    
    def _load_file(self):
        """加载文件"""
        if self.is_loading or self.is_saving:
            messagebox.showwarning("警告", "后台操作进行中，请稍候")
            return
        
        file_path = filedialog.askopenfilename(
            title="选择global-metadata.dat文件",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        
        if file_path:
            self._load_file_async(file_path)
    
    def _load_file_async(self, file_path: str):
        """异步加载文件"""
        self.is_loading = True
        self._clear_data()
        
        def load_thread():
            try:
                # 加载文件
                self.metadata_file = MetadataFile(file_path)
                
                # 创建编辑项
                self.editor_items = []
                for i in range(self.metadata_file.get_string_count()):
                    str_bytes = self.metadata_file.str_bytes[i]
                    item = EditorListItem(str_bytes, i)
                    self.editor_items.append(item)
                
                # 更新界面
                self.root.after(0, self._refresh_listview)
                self.root.after(0, lambda: setattr(self, 'is_loading', False))
                self.root.after(0, lambda: self.root.title(f"MetaData String Editor - {os.path.basename(file_path)}"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"加载文件失败:\n{str(e)}"))
                self.root.after(0, lambda: setattr(self, 'is_loading', False))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _refresh_listview(self):
        """刷新列表视图"""
        Logger.info("刷新列表视图")
        
        # 清空现有项
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新项
        for item in self.editor_items:
            data = item.get_display_data()
            self.tree.insert("", tk.END, values=data, tags=(str(item.index),))
        
        Logger.info(f"已加载 {len(self.editor_items)} 个字符串")
    
    def _save_file_as(self):
        """另存为文件"""
        if not self.metadata_file:
            messagebox.showwarning("警告", "请先加载文件")
            return
        
        if self.is_loading or self.is_saving:
            messagebox.showwarning("警告", "后台操作进行中，请稍候")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".dat",
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")]
        )
        
        if file_path:
            self._save_file_async(file_path)
    
    def _save_file_async(self, file_path: str):
        """异步保存文件"""
        self.is_saving = True
        
        def save_thread():
            try:
                # 更新metadata文件中的字符串数据
                for item in self.editor_items:
                    self.metadata_file.set_string_bytes(item.index, item.current_bytes)
                
                # 保存文件
                self.metadata_file.save_to_file(file_path)
                
                self.root.after(0, lambda: messagebox.showinfo("成功", "文件保存成功"))
                self.root.after(0, lambda: setattr(self, 'is_saving', False))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"保存文件失败:\n{str(e)}"))
                self.root.after(0, lambda: setattr(self, 'is_saving', False))
        
        threading.Thread(target=save_thread, daemon=True).start()
    
    def _close_file(self):
        """关闭文件"""
        self._clear_data()
        self.root.title("MetaData String Editor - Python版本")
    
    def _clear_data(self):
        """清空数据"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 清空数据
        if self.metadata_file:
            self.metadata_file.close()
            self.metadata_file = None
        
        self.editor_items.clear()
        self.search_results.clear()
        self.current_search_index = -1
        self.last_search_keyword = ""
        
        # 清空搜索
        self.search_var.set("")
        self._update_search_display()
    
    def _focus_search(self):
        """聚焦搜索框"""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
    
    def _clear_search(self):
        """清除搜索"""
        if self.search_entry == self.root.focus_get():
            self.search_var.set("")
            self.tree.focus_set()
    
    def _on_search_changed(self, *args):
        """搜索内容改变事件"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.search_results.clear()
            self.current_search_index = -1
            self.last_search_keyword = ""
            self._update_search_display()
        else:
            # 当搜索内容改变时，自动执行搜索
            self._perform_search()
    
    def _perform_search(self):
        """执行搜索"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.search_results.clear()
            self.current_search_index = -1
            self.last_search_keyword = ""
            self._update_search_display()
            return
        
        # 如果搜索关键词改变了，重新搜索
        if keyword != self.last_search_keyword:
            self.search_results.clear()
            self.current_search_index = -1
            self.last_search_keyword = keyword
            
            # 搜索匹配项
            for i, item in enumerate(self.editor_items):
                if item.match_keyword(keyword):
                    self.search_results.append(i)
        
        self._update_search_display()
    
    def _search_next(self):
        """搜索下一个"""
        self._perform_search()
        if not self.search_results:
            Logger.info("找不到搜索字符串")
            return
        
        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self._navigate_to_search_result()
    
    def _search_previous(self):
        """搜索上一个"""
        self._perform_search()
        if not self.search_results:
            Logger.info("找不到搜索字符串")
            return
        
        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self._navigate_to_search_result()
    
    def _navigate_to_search_result(self):
        """导航到搜索结果"""
        if 0 <= self.current_search_index < len(self.search_results):
            item_index = self.search_results[self.current_search_index]
            
            # 清除之前的选择
            for selected in self.tree.selection():
                self.tree.selection_remove(selected)
            
            # 选择并滚动到目标项
            children = self.tree.get_children()
            if item_index < len(children):
                target_item = children[item_index]
                self.tree.selection_set(target_item)
                self.tree.see(target_item)
                self.tree.focus(target_item)
            
            self._update_search_display()
    
    def _update_search_display(self):
        """更新搜索显示"""
        if not self.search_var.get().strip():
            self.search_count_var.set("")
        elif not self.search_results:
            self.search_count_var.set("0/0")
        else:
            self.search_count_var.set(f"{self.current_search_index + 1}/{len(self.search_results)}")
    
    def _on_item_double_click(self, event):
        """列表项双击事件"""
        self._edit_selected_item()
    
    def _on_item_right_click(self, event):
        """列表项右键点击事件"""
        # 选择点击的项
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _edit_selected_item(self):
        """编辑选中的项"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # 获取选中项的索引
        item_id = selection[0]
        values = self.tree.item(item_id, "values")
        if not values:
            return
        
        try:
            index = int(values[0])
            if 0 <= index < len(self.editor_items):
                editor_item = self.editor_items[index]
                
                # 打开编辑对话框
                dialog = EditDialog(self.root, editor_item)
                if dialog.show():
                    # 更新列表显示
                    new_values = editor_item.get_display_data()
                    self.tree.item(item_id, values=new_values)
                    
        except (ValueError, IndexError):
            pass
    
    def _show_about(self):
        """显示关于对话框"""
        about_text = """MetaData String Editor - Python版本
版本: 1.0.0

这是一个用于编辑Unity global-metadata.dat文件中字符串的工具。

功能特性:
• 跨平台支持 (Windows, macOS, Linux)
• 现代化图形界面
• 快速搜索和过滤
• 批量编辑支持
• 安全的文件操作

使用Python和tkinter重构自原始的C# Windows Forms版本。"""
        
        messagebox.showinfo("关于", about_text)
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_var.set(message)
    
    def _set_progress_max(self, max_value: int):
        """设置进度条最大值"""
        self.progress_bar.configure(maximum=max_value)
        self.progress_var.set(0)
    
    def _update_progress(self, value: int):
        """更新进度条值"""
        self.progress_var.set(value)
    
    def _progress_plus_one(self):
        """进度条加1"""
        current = self.progress_var.get()
        self.progress_var.set(current + 1)
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
    
    def load_file_on_startup(self, file_path: str):
        """启动时加载文件"""
        if os.path.exists(file_path):
            self.root.after(100, lambda: self._load_file_async(file_path))