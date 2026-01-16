# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 设备配置页
==============================
用于配置设备型号和折旧年限
实时计算并显示每分钟开机成本
"""

import customtkinter as ctk
from ..config import COLORS, FONTS, MACHINES, DEPRECIATION_YEARS_OPTIONS
from ..services import CostCalculator
from ..database import get_active_machine_config, save_machine_config


class ConfigPage(ctk.CTkFrame):
    """
    设备配置页面
    
    功能:
    - 选择设备型号 (DW-HP120 / DW-HP200)
    - 选择折旧年限 (1/2/3年)
    - 实时显示各配置下的每分钟成本
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 当前选择
        self.selected_machine = ctk.StringVar(value="DW-HP120")
        self.selected_years = ctk.IntVar(value=3)
        
        # 构建界面
        self._create_header()
        self._create_content()
        
        # 加载已保存的配置
        self._load_saved_config()
    
    def _create_header(self):
        """创建页面标题区"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ 设备配置",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        # 副标题
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="配置您的设备型号和折旧年限，系统将自动计算基准费率",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
    
    def _create_content(self):
        """创建主要内容区"""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        content_frame.grid_columnconfigure((0, 1), weight=1)
        
        # ============================================================
        # 左侧: 设备选择卡片
        # ============================================================
        machine_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        machine_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)
        
        # 卡片标题
        machine_title = ctk.CTkLabel(
            machine_card,
            text="🖨️ 设备型号",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        machine_title.pack(anchor="w", padx=25, pady=(25, 15))
        
        # 设备选项
        for machine_name, price in MACHINES.items():
            machine_btn = ctk.CTkRadioButton(
                machine_card,
                text=f"{machine_name}",
                variable=self.selected_machine,
                value=machine_name,
                font=FONTS["body"],
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                command=self._on_config_change
            )
            machine_btn.pack(anchor="w", padx=25, pady=8)
            
            # 价格说明
            price_label = ctk.CTkLabel(
                machine_card,
                text=f"      设备总价: ¥{price:,}",
                font=FONTS["small"],
                text_color=COLORS["text_secondary"]
            )
            price_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        # ============================================================
        # 右侧: 折旧年限选择卡片
        # ============================================================
        years_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        years_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        # 卡片标题
        years_title = ctk.CTkLabel(
            years_card,
            text="📅 折旧年限",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        years_title.pack(anchor="w", padx=25, pady=(25, 15))
        
        # 年限选项
        for years in DEPRECIATION_YEARS_OPTIONS:
            years_btn = ctk.CTkRadioButton(
                years_card,
                text=f"{years} 年",
                variable=self.selected_years,
                value=years,
                font=FONTS["body"],
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                command=self._on_config_change
            )
            years_btn.pack(anchor="w", padx=25, pady=12)
        
        # 说明文字
        info_label = ctk.CTkLabel(
            years_card,
            text="💡 年限越短，单价越高\n    按每年330工作日计算",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        info_label.pack(anchor="w", padx=25, pady=(20, 25))
        
        # ============================================================
        # 底部: 成本计算结果卡片
        # ============================================================
        result_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        result_card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(20, 10))
        
        # 结果标题
        result_title = ctk.CTkLabel(
            result_card,
            text="📊 成本计算结果",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        result_title.pack(anchor="w", padx=25, pady=(25, 15))
        
        # 当前配置显示
        self.config_label = ctk.CTkLabel(
            result_card,
            text="",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self.config_label.pack(anchor="w", padx=25)
        
        # 每分钟成本 (大字体高亮)
        cost_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        cost_frame.pack(fill="x", padx=25, pady=20)
        
        cost_prefix = ctk.CTkLabel(
            cost_frame,
            text="每分钟开机成本:",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        cost_prefix.pack(side="left")
        
        self.cost_value_label = ctk.CTkLabel(
            cost_frame,
            text="¥0.00",
            font=FONTS["price"],
            text_color=COLORS["accent"]
        )
        self.cost_value_label.pack(side="left", padx=(20, 0))
        
        self.cost_unit_label = ctk.CTkLabel(
            cost_frame,
            text="/分钟",
            font=FONTS["subtitle"],
            text_color=COLORS["text_secondary"]
        )
        self.cost_unit_label.pack(side="left")
        
        # ============================================================
        # 成本对照表
        # ============================================================
        table_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        table_card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 20))
        
        table_title = ctk.CTkLabel(
            table_card,
            text="📋 成本对照表 (元/分钟)",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        table_title.pack(anchor="w", padx=25, pady=(20, 15))
        
        # 表格框架
        table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        table_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        # 获取成本表
        cost_table = CostCalculator.get_machine_cost_table()
        
        # 表头
        headers = ["设备型号", "1年折旧", "2年折旧", "3年折旧"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(
                table_frame,
                text=header,
                font=FONTS["body"],
                text_color=COLORS["text_secondary"]
            )
            label.grid(row=0, column=col, padx=20, pady=8, sticky="w")
        
        # 表格数据
        for row, (machine_name, costs) in enumerate(cost_table.items(), start=1):
            # 设备名称
            name_label = ctk.CTkLabel(
                table_frame,
                text=machine_name,
                font=FONTS["body"],
                text_color=COLORS["text_primary"]
            )
            name_label.grid(row=row, column=0, padx=20, pady=8, sticky="w")
            
            # 各年限成本
            for col, years in enumerate([1, 2, 3], start=1):
                cost = costs[years]
                cost_label = ctk.CTkLabel(
                    table_frame,
                    text=f"¥{cost:.2f}",
                    font=FONTS["mono"],
                    text_color=COLORS["success"]
                )
                cost_label.grid(row=row, column=col, padx=20, pady=8, sticky="w")
        
        # 保存按钮
        save_btn = ctk.CTkButton(
            content_frame,
            text="💾 保存配置",
            font=FONTS["subtitle"],
            height=50,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._save_config
        )
        save_btn.grid(row=3, column=0, columnspan=2, pady=(10, 20))
        
        # 初始更新显示
        self._update_cost_display()
    
    def _load_saved_config(self):
        """加载已保存的配置"""
        config = get_active_machine_config()
        if config:
            self.selected_machine.set(config.machine_name)
            self.selected_years.set(config.depreciation_years)
            self._update_cost_display()
    
    def _on_config_change(self):
        """配置变化时的回调"""
        self._update_cost_display()
    
    def _update_cost_display(self):
        """更新成本显示"""
        machine = self.selected_machine.get()
        years = self.selected_years.get()
        price = MACHINES.get(machine, 1_500_000)
        
        # 计算每分钟成本
        cost_per_min = CostCalculator.calculate_cost_per_minute(price, years)
        
        # 更新显示
        self.config_label.configure(
            text=f"当前配置: {machine} | 设备总价 ¥{price:,} | 折旧 {years} 年"
        )
        self.cost_value_label.configure(text=f"¥{cost_per_min:.2f}")
    
    def _save_config(self):
        """保存配置"""
        machine = self.selected_machine.get()
        years = self.selected_years.get()
        
        save_machine_config(machine, years)
        
        # 刷新报价页面
        self.app.refresh_quote_page()
        
        # 显示保存成功提示
        self._show_save_success()
    
    def _show_save_success(self):
        """显示保存成功提示"""
        # 创建临时提示标签
        success_label = ctk.CTkLabel(
            self,
            text="✅ 配置已保存",
            font=FONTS["body"],
            text_color=COLORS["success"],
            fg_color=COLORS["bg_card"],
            corner_radius=8,
            padx=20,
            pady=10
        )
        success_label.place(relx=0.5, rely=0.9, anchor="center")
        
        # 2秒后自动消失
        self.after(2000, success_label.destroy)
    
    def on_show(self):
        """页面显示时的回调"""
        self._load_saved_config()
