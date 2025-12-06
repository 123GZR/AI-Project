import tkinter as tk
from tkinter import ttk, messagebox
from knowledge_base import knowledge_base

class KnowledgeBaseUI:
    def __init__(self, parent, frame):
        self.parent = parent
        self.frame = frame
        self.root = parent.root
    
    def create(self):
        """创建知识库界面"""
        # 知识库搜索框
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.kb_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.kb_search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<Return>", self.search_knowledge_base)
        
        search_button = ttk.Button(search_frame, text="搜索", command=self.search_knowledge_base, width=6)
        search_button.pack(side=tk.LEFT)
        
        # 分类选择
        category_frame = ttk.Frame(self.frame)
        category_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(category_frame, text="分类:", font=('微软雅黑', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.category_var = tk.StringVar(value="all")
        self.category_combobox = ttk.Combobox(
            category_frame, 
            textvariable=self.category_var,
            width=15,
            state="readonly"
        )
        self.update_category_combobox()
        self.category_combobox.pack(side=tk.LEFT)
        
        # 知识库条目列表
        self.kb_listbox = tk.Listbox(
            self.frame, 
            width=30, 
            height=15, 
            font=('微软雅黑', 10),
            selectmode=tk.SINGLE,
            bd=0,
            highlightthickness=0,
            relief=tk.FLAT,
            bg="#f0f0f0"
        )
        self.kb_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.kb_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.kb_listbox.config(yscrollcommand=scrollbar.set)
        
        # 绑定事件
        self.kb_listbox.bind("<Double-1>", self.view_knowledge_item)
        self.kb_listbox.bind("<Button-3>", self.show_kb_menu)
        
        # 创建右键菜单
        self.kb_menu = tk.Menu(self.root, tearoff=0)
        self.kb_menu.add_command(label="查看详情", command=self.view_knowledge_item)
        self.kb_menu.add_command(label="编辑", command=self.edit_knowledge_item)
        self.kb_menu.add_command(label="删除", command=self.delete_knowledge_item)
        self.kb_menu.add_command(label="添加关联", command=self.add_knowledge_relation)
        
        # 操作按钮
        action_frame = ttk.Frame(self.frame)
        action_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        add_button = ttk.Button(action_frame, text="添加知识", command=self.add_knowledge_item, width=8)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_button = ttk.Button(action_frame, text="刷新", command=self.refresh_knowledge_list, width=6)
        refresh_button.pack(side=tk.LEFT)
        
        # 初始加载知识库
        self.refresh_knowledge_list()
    
    def update_category_combobox(self):
        """更新分类下拉框"""
        categories = knowledge_base.get_categories()
        items = ["全部类别"] + [category["name"] for category in categories]
        self.category_combobox['values'] = items
        self.category_combobox.current(0)
        
        # 保存分类映射关系
        self.category_map = {"all": "all"}
        for category in categories:
            self.category_map[category["name"]] = category["id"]
    
    def refresh_knowledge_list(self):
        """刷新知识库列表"""
        self.kb_listbox.delete(0, tk.END)
        
        # 清空列表
        self.kb_listbox.delete(0, tk.END)
        # 清空ID映射列表
        self.kb_item_ids = []
        
        # 获取所有知识条目
        items = knowledge_base.data["knowledge_items"]
        
        # 按创建时间降序排序
        items.sort(key=lambda x: x["created_at"], reverse=True)
        
        for item in items:
            # 获取分类名称
            category_name = "未知分类"
            for category in knowledge_base.data["categories"]:
                if category["id"] == item["category_id"]:
                    category_name = category["name"]
                    break
            
            display_text = f"[{category_name}] {item['title']}"
            self.kb_listbox.insert(tk.END, display_text)
            # 保存条目ID映射到单独的列表
            self.kb_item_ids.append(item["id"])
    
    def search_knowledge_base(self, event=None):
        """搜索知识库"""
        query = self.kb_search_var.get().strip()
        category_name = self.category_var.get()
        category_id = self.category_map.get(category_name, "all")
        
        # 搜索知识库
        if category_id == "all":
            results = knowledge_base.search_knowledge_items(query)
        else:
            results = knowledge_base.search_knowledge_items(query, category_id=category_id)
        
        # 更新列表显示
        self.kb_listbox.delete(0, tk.END)
        # 清空ID映射列表
        self.kb_item_ids = []
        for item in results:
            # 获取分类名称
            category_name = "未知分类"
            for category in knowledge_base.data["categories"]:
                if category["id"] == item["category_id"]:
                    category_name = category["name"]
                    break
            
            display_text = f"[{category_name}] {item['title']}"
            self.kb_listbox.insert(tk.END, display_text)
            # 保存条目ID映射到单独的列表
            self.kb_item_ids.append(item["id"])
    
    def view_knowledge_item(self, event=None):
        """查看知识条目详情"""
        selection = self.kb_listbox.curselection()
        if selection:
            index = selection[0]
            # 获取条目ID
            if 0 <= index < len(self.kb_item_ids):
                item_id = self.kb_item_ids[index]
            else:
                # 如果索引无效，尝试从数据中查找
                items = knowledge_base.data["knowledge_items"]
                if index < len(items):
                    item_id = items[index]["id"]
                else:
                    return
            
            # 获取知识条目
            item = knowledge_base.get_knowledge_item(item_id)
            if item:
                # 创建详情窗口
                detail_window = tk.Toplevel(self.root)
                detail_window.title(f"知识详情 - {item['title']}")
                detail_window.geometry("600x500")
                detail_window.resizable(True, True)
                
                # 标题
                title_label = ttk.Label(detail_window, text=item['title'], font=('微软雅黑', 14, 'bold'))
                title_label.pack(fill=tk.X, padx=10, pady=10)
                
                # 分类和标签
                meta_frame = ttk.Frame(detail_window)
                meta_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
                
                # 获取分类名称
                category_name = "未知分类"
                for category in knowledge_base.data["categories"]:
                    if category["id"] == item["category_id"]:
                        category_name = category["name"]
                        break
                
                ttk.Label(meta_frame, text=f"分类: {category_name}", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 20))
                ttk.Label(meta_frame, text=f"类型: {item['type']}", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 20))
                ttk.Label(meta_frame, text=f"浏览: {item['views']}", font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=(0, 20))
                
                # 标签显示
                tags_text = ", ".join(item['tags']) if item['tags'] else "无标签"
                ttk.Label(meta_frame, text=f"标签: {tags_text}", font=('微软雅黑', 10)).pack(side=tk.LEFT)
                
                # 内容区域
                content_frame = ttk.LabelFrame(detail_window, text="内容")
                content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                content_text = tk.scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, font=('微软雅黑', 10))
                content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                content_text.insert(tk.END, item['content'])
                content_text.config(state=tk.DISABLED)
                
                # 相关知识
                related_items = knowledge_base.get_related_items(item_id)
                if related_items:
                    related_frame = ttk.LabelFrame(detail_window, text="相关知识")
                    related_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    
                    for related_item in related_items:
                        related_label = ttk.Label(
                            related_frame, 
                            text=f"• {related_item['title']}", 
                            font=('微软雅黑', 10),
                            foreground="#0078d7",
                            cursor="hand2"
                        )
                        related_label.pack(anchor=tk.W, padx=10, pady=2)
                        
                        # 绑定点击事件
                        def on_related_click(rel_item_id):
                            # 关闭当前窗口并打开相关条目
                            detail_window.destroy()
                            # 查找并选中相关条目
                            for i in range(self.kb_listbox.size()):
                                rel_id = self.kb_listbox.itemcget(i, "id")
                                if not rel_id:
                                    # 如果没有id属性，尝试从数据中查找
                                    items = knowledge_base.data["knowledge_items"]
                                    if i < len(items) and items[i]["id"] == rel_item_id:
                                        self.kb_listbox.selection_set(i)
                                        break
                                elif rel_id == rel_item_id:
                                    self.kb_listbox.selection_set(i)
                                    break
                            # 查看相关条目
                            self.view_knowledge_item()
                        
                        related_label.bind("<Button-1>", lambda e, rid=related_item["id"]: on_related_click(rid))
    
    def show_kb_menu(self, event):
        """显示知识库右键菜单"""
        try:
            # 获取选中项
            index = self.kb_listbox.nearest(event.y)
            self.kb_listbox.selection_clear(0, tk.END)
            self.kb_listbox.selection_set(index)
            # 显示菜单
            self.kb_menu.post(event.x_root, event.y_root)
        except Exception as e:
            pass
    
    def add_knowledge_item(self):
        """添加知识条目"""
        # 创建添加窗口
        add_window = tk.Toplevel(self.root)
        add_window.title("添加知识条目")
        add_window.geometry("600x500")
        add_window.resizable(True, True)
        
        # 按钮框架（先创建，确保显示在底部）
        button_frame = ttk.Frame(add_window, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.S)
        
        # 表单框架（使用不同的填充方式，避免覆盖按钮框架）
        form_frame = ttk.Frame(add_window, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # 标题
        ttk.Label(form_frame, text="标题:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        title_var = tk.StringVar()
        title_entry = ttk.Entry(form_frame, textvariable=title_var, width=50)
        title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 分类
        ttk.Label(form_frame, text="分类:", font=('微软雅黑', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar()
        category_combobox = ttk.Combobox(form_frame, textvariable=category_var, width=48, state="readonly")
        
        # 加载分类
        categories = knowledge_base.get_categories()
        category_names = [category["name"] for category in categories]
        category_combobox['values'] = category_names
        if category_names:
            category_combobox.current(0)
        category_combobox.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # 类型
        ttk.Label(form_frame, text="类型:", font=('微软雅黑', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        type_var = tk.StringVar(value="text")
        type_combobox = ttk.Combobox(form_frame, textvariable=type_var, width=48, state="readonly")
        type_combobox['values'] = ["text", "image", "code", "multimodal"]
        type_combobox.current(0)
        type_combobox.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        # 标签
        ttk.Label(form_frame, text="标签:", font=('微软雅黑', 10)).grid(row=3, column=0, sticky=tk.NW, pady=5)
        tags_text = tk.scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, height=2, width=50, font=('微软雅黑', 10))
        tags_text.grid(row=3, column=1, sticky=tk.EW, pady=5)
        ttk.Label(form_frame, text="(多个标签用逗号分隔)", font=('微软雅黑', 8, 'italic'), foreground="#888888").grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # 内容
        ttk.Label(form_frame, text="内容:", font=('微软雅黑', 10)).grid(row=5, column=0, sticky=tk.NW, pady=5)
        content_text = tk.scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, height=15, width=50, font=('微软雅黑', 10))
        content_text.grid(row=5, column=1, sticky=tk.NSEW, pady=5)
        
        # 配置网格权重
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(5, weight=1)
        
        def save_item():
            """保存知识条目"""
            title = title_var.get().strip()
            content = content_text.get("1.0", tk.END).strip()
            
            if not title or not content:
                messagebox.showwarning("警告", "标题和内容不能为空")
                return
            
            # 获取分类ID
            category_name = category_var.get()
            category_id = None
            for category in categories:
                if category["name"] == category_name:
                    category_id = category["id"]
                    break
            
            # 处理标签
            tags_str = tags_text.get("1.0", tk.END).strip()
            tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
            
            # 创建知识条目
            item_data = {
                "title": title,
                "content": content,
                "category_id": category_id,
                "tags": tags,
                "type": type_var.get()
            }
            
            # 添加到知识库
            item_id = knowledge_base.add_knowledge_item(item_data)
            if item_id:
                self.refresh_knowledge_list()
                add_window.destroy()
                self.parent.show_toast("知识条目已添加")
        
        cancel_button = ttk.Button(button_frame, text="取消", command=add_window.destroy)
        cancel_button.pack(side=tk.LEFT)
        
        save_button = ttk.Button(button_frame, text="保存", command=save_item, style="Accent.TButton")
        save_button.pack(side=tk.RIGHT)
    
    def edit_knowledge_item(self):
        """编辑知识条目"""
        selection = self.kb_listbox.curselection()
        if selection:
            index = selection[0]
            # 获取条目ID
            item_id = self.kb_listbox.itemcget(index, "id")
            if not item_id:
                # 如果没有id属性，尝试从数据中查找
                items = knowledge_base.data["knowledge_items"]
                if index < len(items):
                    item_id = items[index]["id"]
                else:
                    return
            
            # 获取知识条目
            item = knowledge_base.get_knowledge_item(item_id)
            if item:
                # 创建编辑窗口
                edit_window = tk.Toplevel(self.root)
                edit_window.title(f"编辑知识条目 - {item['title']}")
                edit_window.geometry("600x500")
                edit_window.resizable(True, True)
                
                # 按钮框架（先创建，确保显示在底部）
                button_frame = ttk.Frame(edit_window, padding="10")
                button_frame.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.S)
                
                # 表单框架（使用不同的填充方式，避免覆盖按钮框架）
                form_frame = ttk.Frame(edit_window, padding="10")
                form_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
                
                # 标题
                ttk.Label(form_frame, text="标题:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
                title_var = tk.StringVar(value=item['title'])
                title_entry = ttk.Entry(form_frame, textvariable=title_var, width=50)
                title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)
                
                # 分类
                ttk.Label(form_frame, text="分类:", font=('微软雅黑', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
                category_var = tk.StringVar()
                category_combobox = ttk.Combobox(form_frame, textvariable=category_var, width=48, state="readonly")
                
                # 加载分类
                categories = knowledge_base.get_categories()
                category_names = [category["name"] for category in categories]
                category_combobox['values'] = category_names
                
                # 设置当前分类
                current_category_name = "未知分类"
                for category in categories:
                    if category["id"] == item["category_id"]:
                        current_category_name = category["name"]
                        break
                category_var.set(current_category_name)
                category_combobox.grid(row=1, column=1, sticky=tk.EW, pady=5)
                
                # 类型
                ttk.Label(form_frame, text="类型:", font=('微软雅黑', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
                type_var = tk.StringVar(value=item['type'])
                type_combobox = ttk.Combobox(form_frame, textvariable=type_var, width=48, state="readonly")
                type_combobox['values'] = ["text", "image", "code", "multimodal"]
                type_combobox.current(type_combobox['values'].index(item['type']))
                type_combobox.grid(row=2, column=1, sticky=tk.EW, pady=5)
                
                # 标签
                ttk.Label(form_frame, text="标签:", font=('微软雅黑', 10)).grid(row=3, column=0, sticky=tk.NW, pady=5)
                tags_text = tk.scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, height=2, width=50, font=('微软雅黑', 10))
                tags_text.insert(tk.END, ", ".join(item['tags']))
                tags_text.grid(row=3, column=1, sticky=tk.EW, pady=5)
                ttk.Label(form_frame, text="(多个标签用逗号分隔)", font=('微软雅黑', 8, 'italic'), foreground="#888888").grid(row=4, column=1, sticky=tk.W, pady=2)
                
                # 内容
                ttk.Label(form_frame, text="内容:", font=('微软雅黑', 10)).grid(row=5, column=0, sticky=tk.NW, pady=5)
                content_text = tk.scrolledtext.ScrolledText(form_frame, wrap=tk.WORD, height=15, width=50, font=('微软雅黑', 10))
                content_text.insert(tk.END, item['content'])
                content_text.grid(row=5, column=1, sticky=tk.NSEW, pady=5)
                
                # 配置网格权重
                form_frame.grid_columnconfigure(1, weight=1)
                form_frame.grid_rowconfigure(5, weight=1)
                
                def update_item():
                    """更新知识条目"""
                    title = title_var.get().strip()
                    content = content_text.get("1.0", tk.END).strip()
                    
                    if not title or not content:
                        messagebox.showwarning("警告", "标题和内容不能为空")
                        return
                    
                    # 获取分类ID
                    category_name = category_var.get()
                    category_id = None
                    for category in categories:
                        if category["name"] == category_name:
                            category_id = category["id"]
                            break
                    
                    # 处理标签
                    tags_str = tags_text.get("1.0", tk.END).strip()
                    tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
                    
                    # 更新知识条目
                    update_data = {
                        "title": title,
                        "content": content,
                        "category_id": category_id,
                        "tags": tags,
                        "type": type_var.get()
                    }
                    
                    # 更新知识库
                    success = knowledge_base.update_knowledge_item(item_id, update_data)
                    if success:
                        self.refresh_knowledge_list()
                        edit_window.destroy()
                        self.parent.show_toast("知识条目已更新")
                
                cancel_button = ttk.Button(button_frame, text="取消", command=edit_window.destroy)
                cancel_button.pack(side=tk.LEFT)
                
                save_button = ttk.Button(button_frame, text="保存", command=update_item, style="Accent.TButton")
                save_button.pack(side=tk.RIGHT)
    
    def delete_knowledge_item(self):
        """删除知识条目"""
        selection = self.kb_listbox.curselection()
        if selection:
            index = selection[0]
            # 获取条目ID
            item_id = self.kb_listbox.itemcget(index, "id")
            if not item_id:
                # 如果没有id属性，尝试从数据中查找
                items = knowledge_base.data["knowledge_items"]
                if index < len(items):
                    item_id = items[index]["id"]
                else:
                    return
            
            # 获取知识条目
            item = knowledge_base.get_knowledge_item(item_id)
            if item:
                if messagebox.askyesno("确认", f"确定要删除知识条目 '{item['title']}' 吗？"):
                    success = knowledge_base.delete_knowledge_item(item_id)
                    if success:
                        self.refresh_knowledge_list()
                        self.parent.show_toast("知识条目已删除")
    
    def add_knowledge_relation(self):
        """添加知识关联"""
        selection = self.kb_listbox.curselection()
        if selection:
            index = selection[0]
            # 获取源条目ID
            source_id = self.kb_listbox.itemcget(index, "id")
            if not source_id:
                # 如果没有id属性，尝试从数据中查找
                items = knowledge_base.data["knowledge_items"]
                if index < len(items):
                    source_id = items[index]["id"]
                else:
                    return
            
            # 创建关联窗口
            relation_window = tk.Toplevel(self.root)
            relation_window.title("添加知识关联")
            relation_window.geometry("500x300")
            relation_window.resizable(True, True)
            
            # 表单框架
            form_frame = ttk.Frame(relation_window, padding="10")
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            # 目标知识选择
            ttk.Label(form_frame, text="目标知识:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
            
            # 获取所有知识条目（排除当前条目）
            all_items = knowledge_base.data["knowledge_items"]
            target_items = [item for item in all_items if item["id"] != source_id]
            
            target_titles = [item["title"] for item in target_items]
            self.target_var = tk.StringVar()
            target_combobox = ttk.Combobox(
                form_frame, 
                textvariable=self.target_var,
                values=target_titles,
                width=40,
                state="readonly"
            )
            if target_titles:
                target_combobox.current(0)
            target_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5)
            
            # 关联类型
            ttk.Label(form_frame, text="关联类型:", font=('微软雅黑', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
            
            relation_types = ["related_to", "part_of", "prerequisite", "solution_to"]
            self.relation_type_var = tk.StringVar(value="related_to")
            relation_combobox = ttk.Combobox(
                form_frame, 
                textvariable=self.relation_type_var,
                values=relation_types,
                width=40,
                state="readonly"
            )
            relation_combobox.grid(row=1, column=1, sticky=tk.EW, pady=5)
            
            # 配置网格权重
            form_frame.grid_columnconfigure(1, weight=1)
            
            # 按钮框架
            button_frame = ttk.Frame(relation_window, padding="10")
            button_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            def save_relation():
                """保存知识关联"""
                target_title = self.target_var.get()
                relation_type = self.relation_type_var.get()
                
                # 获取目标条目ID
                target_id = None
                for item in target_items:
                    if item["title"] == target_title:
                        target_id = item["id"]
                        break
                
                if target_id:
                    # 添加关联
                    relation_id = knowledge_base.add_relation(source_id, target_id, relation_type)
                    if relation_id:
                        relation_window.destroy()
                        self.parent.show_toast("知识关联已添加")
            
            cancel_button = ttk.Button(button_frame, text="取消", command=relation_window.destroy)
            cancel_button.pack(side=tk.LEFT)
            
            save_button = ttk.Button(button_frame, text="保存", command=save_relation, style="Accent.TButton")
            save_button.pack(side=tk.RIGHT)
