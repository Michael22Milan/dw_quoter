# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 快速报价页
==============================
输入材质、重量、难度系数
实时计算并显示报价和预估时长
"""

import customtkinter as ctk
from ..config import COLORS, FONTS, DIFFICULTY_MIN, DIFFICULTY_MAX, DIFFICULTY_DEFAULT
from ..services import QuoteService, CostCalculator, EfficiencyService
from ..database import get_all_materials, get_active_machine_config


class QuotePage(ctk.CTkFrame):
    """
    快速报价页面
    
    功能:
    - 选择打印材质
    - 输入预估重量
    - 调整难度系数
    - 实时显示报价结果
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 输入变量
        self.selected_material = ctk.StringVar(value="316L不锈钢")
        self.weight_var = ctk.StringVar(value="100")
        self.difficulty_var = ctk.DoubleVar(value=DIFFICULTY_DEFAULT)
        
        # 标记是否已完成初始化
        self._initialized = False
        
        # 构建界面
        self._create_header()
        self._create_content()
        
        # 绑定变量变化事件
        self.weight_var.trace_add("write", self._on_input_change)
        self.difficulty_var.trace_add("write", self._on_input_change)
        
        self._initialized = True
        
        # 初始计算
        self._calculate_quote()
    
    def _create_header(self):
        """创建页面标题区"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ 快速报价",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="输入零件参数，即时获取精准报价",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
    
    def _create_content(self):
        """创建主要内容区"""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        content_frame.grid_columnconfigure((0, 1), weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # ============================================================
        # 左侧: 输入参数卡片
        # ============================================================
        input_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        input_card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 15), pady=10)
        
        # 卡片标题
        input_title = ctk.CTkLabel(
            input_card,
            text="📝 输入参数",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        input_title.pack(anchor="w", padx=25, pady=(25, 20))
        
        # --- 材质选择 ---
        material_label = ctk.CTkLabel(
            input_card,
            text="🧪 打印材质",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        material_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        # 获取材料列表
        materials = get_all_materials()
        material_names = [m.name for m in materials] if materials else ["316L不锈钢", "TC4钛合金"]
        
        self.material_menu = ctk.CTkOptionMenu(
            input_card,
            variable=self.selected_material,
            values=material_names,
            font=FONTS["body"],
            dropdown_font=FONTS["body"],
            width=250,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            command=self._on_material_change
        )
        self.material_menu.pack(anchor="w", padx=25, pady=(0, 20))
        
        # --- 重量输入 ---
        weight_label = ctk.CTkLabel(
            input_card,
            text="⚖️ 预估重量 (克)",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        weight_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        self.weight_entry = ctk.CTkEntry(
            input_card,
            textvariable=self.weight_var,
            font=FONTS["body"],
            width=250,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="输入零件重量"
        )
        self.weight_entry.pack(anchor="w", padx=25, pady=(0, 20))
        
        # --- 难度系数 ---
        difficulty_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        difficulty_frame.pack(fill="x", padx=25, pady=(10, 5))
        
        difficulty_label = ctk.CTkLabel(
            difficulty_frame,
            text="🎯 难度系数",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        difficulty_label.pack(side="left")
        
        self.difficulty_value_label = ctk.CTkLabel(
            difficulty_frame,
            text=f"{DIFFICULTY_DEFAULT:.1f}",
            font=FONTS["body"],
            text_color=COLORS["accent"]
        )
        self.difficulty_value_label.pack(side="right")
        
        self.difficulty_slider = ctk.CTkSlider(
            input_card,
            variable=self.difficulty_var,
            from_=DIFFICULTY_MIN,
            to=DIFFICULTY_MAX,
            width=250,
            height=20,
            corner_radius=10,
            fg_color=COLORS["bg_dark"],
            progress_color=COLORS["accent"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            command=self._on_slider_change
        )
        self.difficulty_slider.pack(anchor="w", padx=25, pady=(0, 5))
        
        # 难度说明
        difficulty_hint = ctk.CTkLabel(
            input_card,
            text="0.8 简单 ← → 2.0 复杂",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        difficulty_hint.pack(anchor="w", padx=25, pady=(0, 30))
        
        # 效率信息
        self.efficiency_label = ctk.CTkLabel(
            input_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.efficiency_label.pack(anchor="w", padx=25, pady=(20, 25))
        
        # ============================================================
        # 右侧: 报价结果卡片
        # ============================================================
        result_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        result_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        # 卡片标题
        result_title = ctk.CTkLabel(
            result_card,
            text="💰 报价结果",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        result_title.pack(anchor="w", padx=25, pady=(25, 30))
        
        # 报价金额 (超大字体)
        self.quote_label = ctk.CTkLabel(
            result_card,
            text="¥0.00",
            font=FONTS["price"],
            text_color=COLORS["success"]
        )
        self.quote_label.pack(pady=(20, 10))
        
        # 预估时长
        time_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        time_frame.pack(pady=20)
        
        time_icon = ctk.CTkLabel(
            time_frame,
            text="⏱️",
            font=("Segoe UI Emoji", 20)
        )
        time_icon.pack(side="left")
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="预估时长: 0分钟",
            font=FONTS["subtitle"],
            text_color=COLORS["text_primary"]
        )
        self.time_label.pack(side="left", padx=(10, 0))
        
        # 分隔线
        separator = ctk.CTkFrame(
            result_card,
            height=1,
            fg_color=COLORS["border"]
        )
        separator.pack(fill="x", padx=25, pady=20)
        
        # 计算明细
        self.detail_label = ctk.CTkLabel(
            result_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.detail_label.pack(anchor="w", padx=25, pady=(0, 25))
        
        # ============================================================
        # 右下: 设备信息卡片
        # ============================================================
        machine_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        machine_card.grid(row=1, column=1, sticky="nsew", padx=(15, 0), pady=(10, 10))
        
        machine_title = ctk.CTkLabel(
            machine_card,
            text="🖨️ 当前设备配置",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        machine_title.pack(anchor="w", padx=25, pady=(20, 15))
        
        self.machine_info_label = ctk.CTkLabel(
            machine_card,
            text="",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.machine_info_label.pack(anchor="w", padx=25, pady=(0, 20))
        
        # 跳转配置按钮
        config_btn = ctk.CTkButton(
            machine_card,
            text="⚙️ 修改配置",
            font=FONTS["body"],
            height=35,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["accent"],
            text_color=COLORS["accent"],
            hover_color=COLORS["bg_dark"],
            command=lambda: self.app.show_page("config")
        )
        config_btn.pack(anchor="w", padx=25, pady=(0, 20))
    
    def _on_material_change(self, value):
        """材质变化时的回调"""
        self._calculate_quote()
    
    def _on_slider_change(self, value):
        """滑块变化时的回调"""
        self.difficulty_value_label.configure(text=f"{value:.1f}")
        if self._initialized:
            self._calculate_quote()
    
    def _on_input_change(self, *args):
        """输入变化时的回调"""
        if self._initialized:
            self._calculate_quote()
    
    def _calculate_quote(self):
        """计算报价"""
        try:
            # 获取输入参数
            material_name = self.selected_material.get()
            weight_str = self.weight_var.get().strip()
            difficulty = self.difficulty_var.get()
            
            # 验证重量输入
            if not weight_str:
                weight = 0
            else:
                weight = float(weight_str)
            
            if weight <= 0:
                self._show_empty_result()
                return
            
            # 调用报价服务
            result = QuoteService.calculate_quote(material_name, weight, difficulty)
            
            # 更新显示
            self._update_result_display(result)
            
        except ValueError:
            self._show_empty_result()
    
    def _update_result_display(self, result):
        """更新报价结果显示"""
        # 报价金额
        quote_str = QuoteService.format_quote(result['quote'])
        self.quote_label.configure(text=quote_str)
        
        # 预估时长
        self.time_label.configure(
            text=f"预估时长: {result['time_formatted']}"
        )
        
        # 计算明细
        detail_text = (
            f"📊 计算明细:\n"
            f"    材料效率: {result['efficiency']:.4f} g/min ({result['efficiency_source']})\n"
            f"    开机成本: ¥{result['cost_per_min']:.4f}/min\n"
            f"    难度系数: {self.difficulty_var.get():.1f}"
        )
        self.detail_label.configure(text=detail_text)
        
        # 效率信息
        if result['order_count'] > 0:
            self.efficiency_label.configure(
                text=f"📈 效率数据来源: {result['efficiency_source']}"
            )
        else:
            self.efficiency_label.configure(
                text="📈 使用预设效率值 (录入更多工单以提高准确度)"
            )
        
        # 更新设备信息
        self._update_machine_info()
    
    def _show_empty_result(self):
        """显示空结果"""
        self.quote_label.configure(text="¥0.00")
        self.time_label.configure(text="预估时长: --")
        self.detail_label.configure(text="请输入有效的重量值")
    
    def _update_machine_info(self):
        """更新设备配置信息"""
        config = get_active_machine_config()
        if config:
            cost_per_min = CostCalculator.calculate_cost_per_minute(
                config.total_price, config.depreciation_years
            )
            info_text = (
                f"设备: {config.machine_name}\n"
                f"总价: ¥{config.total_price:,}\n"
                f"折旧: {config.depreciation_years} 年\n"
                f"费率: ¥{cost_per_min:.2f}/min"
            )
        else:
            info_text = "⚠️ 未配置设备\n请先进行设备配置"
        
        self.machine_info_label.configure(text=info_text)
    
    def refresh_data(self):
        """刷新数据 (外部调用)"""
        self._calculate_quote()
        self._update_machine_info()
    
    def on_show(self):
        """页面显示时的回调"""
        self.refresh_data()
