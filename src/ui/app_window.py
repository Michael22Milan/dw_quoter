# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 主窗口框架
==============================
使用CustomTkinter构建的现代化深色主题界面
包含侧边栏导航和页面容器
"""

import customtkinter as ctk
from ..config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    COLORS, FONTS, APP_NAME, APP_VERSION
)


class AppWindow(ctk.CTk):
    """
    主窗口类
    采用左侧侧边栏导航 + 右侧内容区的布局
    """
    
    def __init__(self):
        super().__init__()
        
        # ============================================================
        # 窗口基础配置
        # ============================================================
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # 设置深色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 设置窗口背景色
        self.configure(fg_color=COLORS["bg_dark"])
        
        # 页面容器字典
        self.pages = {}
        self.current_page = None
        
        # ============================================================
        # 构建界面
        # ============================================================
        self._create_layout()
        self._create_sidebar()
        self._create_pages()
        
        # 默认显示设备配置页
        self.show_page("config")
    
    def _create_layout(self):
        """创建主布局框架"""
        # 配置网格权重
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 侧边栏框架
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=COLORS["bg_sidebar"]
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        
        # 内容区框架
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["bg_dark"]
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
    
    def _create_sidebar(self):
        """创建侧边栏导航"""
        # Logo区域
        logo_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        logo_frame.pack(fill="x", padx=20, pady=(30, 10))
        
        # Logo图标 (使用emoji)
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🏭",
            font=("Segoe UI Emoji", 36)
        )
        logo_label.pack()
        
        # 应用名称
        app_name_label = ctk.CTkLabel(
            logo_frame,
            text="SLM 智能报价",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        app_name_label.pack(pady=(5, 0))
        
        # 版本号
        version_label = ctk.CTkLabel(
            logo_frame,
            text=f"v{APP_VERSION}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        version_label.pack()
        
        # 分隔线
        separator = ctk.CTkFrame(
            self.sidebar_frame,
            height=1,
            fg_color=COLORS["border"]
        )
        separator.pack(fill="x", padx=20, pady=20)
        
        # 导航按钮容器
        nav_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        nav_frame.pack(fill="x", padx=10)
        
        # 导航按钮配置
        nav_items = [
            ("config", "⚙️  设备配置", "配置设备型号和折旧年限"),
            ("quote", "⚡  快速报价", "输入参数获取报价"),
            ("data", "📊  数据进化", "录入工单优化报价"),
        ]
        
        self.nav_buttons = {}
        
        for page_id, text, tooltip in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                font=FONTS["body"],
                height=45,
                anchor="w",
                corner_radius=8,
                fg_color="transparent",
                text_color=COLORS["text_primary"],
                hover_color=COLORS["bg_card"],
                command=lambda p=page_id: self.show_page(p)
            )
            btn.pack(fill="x", pady=3)
            self.nav_buttons[page_id] = btn
        
        # 底部信息
        bottom_frame = ctk.CTkFrame(
            self.sidebar_frame,
            fg_color="transparent"
        )
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # 提示文本
        tip_label = ctk.CTkLabel(
            bottom_frame,
            text="💡 持续录入工单\n让报价越来越准确",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        tip_label.pack()
    
    def _create_pages(self):
        """创建所有页面 (延迟加载)"""
        # 导入页面模块
        from .page_config import ConfigPage
        from .page_quote import QuotePage
        from .page_data import DataPage
        
        # 创建页面实例
        self.pages["config"] = ConfigPage(self.content_frame, self)
        self.pages["quote"] = QuotePage(self.content_frame, self)
        self.pages["data"] = DataPage(self.content_frame, self)
        
        # 初始隐藏所有页面
        for page in self.pages.values():
            page.grid_remove()
    
    def show_page(self, page_id: str):
        """
        切换显示指定页面
        
        Args:
            page_id: 页面标识 (config/quote/data)
        """
        # 隐藏当前页面
        if self.current_page and self.current_page in self.pages:
            self.pages[self.current_page].grid_remove()
        
        # 显示目标页面
        if page_id in self.pages:
            self.pages[page_id].grid(row=0, column=0, sticky="nsew")
            self.pages[page_id].on_show()  # 触发页面显示事件
            self.current_page = page_id
        
        # 更新导航按钮状态
        self._update_nav_buttons(page_id)
    
    def _update_nav_buttons(self, active_page: str):
        """更新导航按钮的选中状态"""
        for page_id, btn in self.nav_buttons.items():
            if page_id == active_page:
                btn.configure(
                    fg_color=COLORS["accent"],
                    text_color=COLORS["bg_dark"],
                    hover_color=COLORS["accent_hover"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_primary"],
                    hover_color=COLORS["bg_card"]
                )
    
    def refresh_quote_page(self):
        """刷新报价页面 (当设备配置或工单数据变化时调用)"""
        if "quote" in self.pages:
            self.pages["quote"].refresh_data()
