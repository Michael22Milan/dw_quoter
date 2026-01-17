# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 快速报价页 (v2.2)
=====================================
输入材质、重量、难度系数、风险系数、后处理参数
实时计算并显示分项报价和总报价
"""

import customtkinter as ctk
from ..config import (
    COLORS, FONTS, 
    DIFFICULTY_OPTIONS, DIFFICULTY_DEFAULT,
    RISK_OPTIONS, RISK_DEFAULT,
    POST_PROCESS_RATE_DEFAULT, POST_PROCESS_HOURS_DEFAULT
)
from ..services import QuoteService, CostCalculator, EfficiencyService
from ..database import get_all_materials, get_active_machine_config


class QuotePage(ctk.CTkFrame):
    """
    快速报价页面 (v2.2)
    
    功能:
    - 选择打印材质
    - 输入预估重量
    - 选择难度系数 (1-正常/2-偏难/3-很难)
    - 选择风险系数 (0/0.5/1/1.5/2)
    - 输入后处理时长和单价
    - 实时显示分项报价和总报价
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 输入变量
        self.selected_material = ctk.StringVar(value="316L不锈钢")
        self.weight_var = ctk.StringVar(value="100")
        self.difficulty_var = ctk.StringVar(value=DIFFICULTY_DEFAULT)
        self.risk_var = ctk.StringVar(value=RISK_DEFAULT)
        self.post_hours_var = ctk.StringVar(value=str(POST_PROCESS_HOURS_DEFAULT))
        self.post_rate_var = ctk.StringVar(value=str(POST_PROCESS_RATE_DEFAULT))
        
        # 标记是否已完成初始化
        self._initialized = False
        
        # 构建界面
        self._create_header()
        self._create_content()
        
        # 绑定变量变化事件
        self.weight_var.trace_add("write", self._on_input_change)
        self.post_hours_var.trace_add("write", self._on_input_change)
        self.post_rate_var.trace_add("write", self._on_input_change)
        
        self._initialized = True
        
        # 初始计算
        self._calculate_quote()
    
    def _create_header(self):
        """创建页面标题区"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 15))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚡ 快速报价",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="输入零件参数，即时获取精准报价（打印价格 + 后处理价格）",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
    
    def _create_content(self):
        """创建主要内容区"""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        content_frame.grid_columnconfigure((0, 1), weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # ============================================================
        # 左侧: 输入参数卡片
        # ============================================================
        input_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        input_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        
        # 创建滚动区域
        input_scroll = ctk.CTkScrollableFrame(
            input_card,
            fg_color="transparent",
            corner_radius=0
        )
        input_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 卡片标题
        input_title = ctk.CTkLabel(
            input_scroll,
            text="📝 输入参数",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        input_title.pack(anchor="w", padx=20, pady=(15, 15))
        
        # --- 材质选择 ---
        self._create_section_label(input_scroll, "🧪 打印材质")
        
        materials = get_all_materials()
        material_names = [m.name for m in materials] if materials else ["316L不锈钢", "TC4钛合金"]
        
        self.material_menu = ctk.CTkOptionMenu(
            input_scroll,
            variable=self.selected_material,
            values=material_names,
            font=FONTS["body"],
            dropdown_font=FONTS["body"],
            width=220,
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            command=self._on_material_change
        )
        self.material_menu.pack(anchor="w", padx=20, pady=(0, 12))
        
        # --- 重量输入 ---
        self._create_section_label(input_scroll, "⚖️ 预估重量 (克)")
        
        self.weight_entry = ctk.CTkEntry(
            input_scroll,
            textvariable=self.weight_var,
            font=FONTS["body"],
            width=220,
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="输入零件重量"
        )
        self.weight_entry.pack(anchor="w", padx=20, pady=(0, 12))
        
        # --- 难度系数 ---
        self._create_section_label(input_scroll, "🎯 难度系数")
        
        self.difficulty_menu = ctk.CTkOptionMenu(
            input_scroll,
            variable=self.difficulty_var,
            values=DIFFICULTY_OPTIONS,
            font=FONTS["body"],
            dropdown_font=FONTS["body"],
            width=220,
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            command=self._on_dropdown_change
        )
        self.difficulty_menu.pack(anchor="w", padx=20, pady=(0, 12))
        
        # --- 风险系数 ---
        self._create_section_label(input_scroll, "⚠️ 风险系数")
        
        self.risk_menu = ctk.CTkOptionMenu(
            input_scroll,
            variable=self.risk_var,
            values=RISK_OPTIONS,
            font=FONTS["body"],
            dropdown_font=FONTS["body"],
            width=220,
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["warning"],
            button_hover_color="#cc8800",
            dropdown_fg_color=COLORS["bg_card"],
            command=self._on_dropdown_change
        )
        self.risk_menu.pack(anchor="w", padx=20, pady=(0, 12))
        
        # 分隔线
        sep1 = ctk.CTkFrame(input_scroll, height=1, fg_color=COLORS["border"])
        sep1.pack(fill="x", padx=20, pady=10)
        
        # --- 后处理区域标题 ---
        post_title = ctk.CTkLabel(
            input_scroll,
            text="🔧 后处理参数",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        post_title.pack(anchor="w", padx=20, pady=(5, 10))
        
        # --- 后处理时长 ---
        self._create_section_label(input_scroll, "⏱️ 后处理时长 (小时)")
        
        self.post_hours_entry = ctk.CTkEntry(
            input_scroll,
            textvariable=self.post_hours_var,
            font=FONTS["body"],
            width=220,
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="0"
        )
        self.post_hours_entry.pack(anchor="w", padx=20, pady=(0, 12))
        
        # --- 后处理单价 ---
        self._create_section_label(input_scroll, "💰 后处理单价 (元/小时)")
        
        self.post_rate_entry = ctk.CTkEntry(
            input_scroll,
            textvariable=self.post_rate_var,
            font=FONTS["body"],
            width=220,
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="50"
        )
        self.post_rate_entry.pack(anchor="w", padx=20, pady=(0, 12))
        
        # 效率信息
        self.efficiency_label = ctk.CTkLabel(
            input_scroll,
            text="",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.efficiency_label.pack(anchor="w", padx=20, pady=(10, 15))
        
        # ============================================================
        # 右侧: 报价结果区域
        # ============================================================
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # --- 报价结果卡片 ---
        result_card = ctk.CTkFrame(
            right_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        result_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        result_title = ctk.CTkLabel(
            result_card,
            text="💰 报价结果",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        result_title.pack(anchor="w", padx=25, pady=(20, 15))
        
        # 总报价 (最大字体)
        total_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        total_frame.pack(fill="x", padx=25)
        
        total_label = ctk.CTkLabel(
            total_frame,
            text="总报价",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        total_label.pack(anchor="w")
        
        self.total_quote_label = ctk.CTkLabel(
            total_frame,
            text="¥0.00",
            font=FONTS["price"],
            text_color=COLORS["success"]
        )
        self.total_quote_label.pack(anchor="w", pady=(0, 10))
        
        # 分隔线
        sep2 = ctk.CTkFrame(result_card, height=1, fg_color=COLORS["border"])
        sep2.pack(fill="x", padx=25, pady=5)
        
        # 分项价格
        prices_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        prices_frame.pack(fill="x", padx=25, pady=10)
        
        # 打印价格
        print_row = ctk.CTkFrame(prices_frame, fg_color="transparent")
        print_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            print_row,
            text="🖨️ 打印价格:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        self.print_price_label = ctk.CTkLabel(
            print_row,
            text="¥0.00",
            font=FONTS["body"],
            text_color=COLORS["accent"]
        )
        self.print_price_label.pack(side="right")
        
        # 基准价格和系数
        base_row = ctk.CTkFrame(prices_frame, fg_color="transparent")
        base_row.pack(fill="x", pady=1)
        
        self.base_info_label = ctk.CTkLabel(
            base_row,
            text="    (基准 ¥0 × 系数 1)",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.base_info_label.pack(side="left")
        
        # 后处理价格
        post_row = ctk.CTkFrame(prices_frame, fg_color="transparent")
        post_row.pack(fill="x", pady=3)
        
        ctk.CTkLabel(
            post_row,
            text="🔧 后处理价格:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        self.post_price_label = ctk.CTkLabel(
            post_row,
            text="¥0.00",
            font=FONTS["body"],
            text_color=COLORS["warning"]
        )
        self.post_price_label.pack(side="right")
        
        # 预估时长
        time_row = ctk.CTkFrame(prices_frame, fg_color="transparent")
        time_row.pack(fill="x", pady=(10, 3))
        
        ctk.CTkLabel(
            time_row,
            text="⏱️ 预估打印时长:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        self.time_label = ctk.CTkLabel(
            time_row,
            text="--",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        self.time_label.pack(side="right")
        
        # --- 计算明细卡片 ---
        detail_card = ctk.CTkFrame(
            right_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        detail_card.grid(row=1, column=0, sticky="nsew")
        
        detail_title = ctk.CTkLabel(
            detail_card,
            text="📊 计算明细",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        detail_title.pack(anchor="w", padx=25, pady=(15, 10))
        
        self.detail_label = ctk.CTkLabel(
            detail_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.detail_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        # 设备信息
        self.machine_info_label = ctk.CTkLabel(
            detail_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"],
            justify="left"
        )
        self.machine_info_label.pack(anchor="w", padx=25, pady=(5, 10))
        
        # 跳转配置按钮
        config_btn = ctk.CTkButton(
            detail_card,
            text="⚙️ 修改设备配置",
            font=FONTS["small"],
            height=30,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_dark"],
            command=lambda: self.app.show_page("config")
        )
        config_btn.pack(anchor="w", padx=25, pady=(0, 15))
    
    def _create_section_label(self, parent, text):
        """创建输入区的标签"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        label.pack(anchor="w", padx=20, pady=(8, 4))
    
    def _on_material_change(self, value):
        """材质变化时的回调"""
        self._calculate_quote()
    
    def _on_dropdown_change(self, value):
        """下拉框变化时的回调"""
        if self._initialized:
            self._calculate_quote()
    
    def _on_input_change(self, *args):
        """输入变化时的回调"""
        if self._initialized:
            self._calculate_quote()
    
    def _parse_difficulty(self) -> int:
        """解析难度系数值"""
        difficulty_str = self.difficulty_var.get()
        # 提取数字部分 (如 "1 - 正常" -> 1)
        try:
            return int(difficulty_str.split(" ")[0])
        except:
            return 1
    
    def _parse_risk(self) -> float:
        """解析风险系数值"""
        try:
            return float(self.risk_var.get())
        except:
            return 0
    
    def _parse_float(self, var, default=0) -> float:
        """安全解析浮点数"""
        try:
            value = var.get().strip()
            return float(value) if value else default
        except:
            return default
    
    def _calculate_quote(self):
        """计算报价"""
        try:
            # 获取输入参数
            material_name = self.selected_material.get()
            weight = self._parse_float(self.weight_var, 0)
            difficulty = self._parse_difficulty()
            risk = self._parse_risk()
            post_hours = self._parse_float(self.post_hours_var, 0)
            post_rate = self._parse_float(self.post_rate_var, 50)
            
            # 验证重量输入
            if weight <= 0:
                self._show_empty_result()
                return
            
            # 调用报价服务
            result = QuoteService.calculate_quote(
                material_name=material_name,
                weight_g=weight,
                difficulty=difficulty,
                risk=risk,
                post_process_hours=post_hours,
                post_process_rate=post_rate
            )
            
            # 更新显示
            self._update_result_display(result)
            
        except Exception as e:
            self._show_empty_result()
    
    def _update_result_display(self, result):
        """更新报价结果显示"""
        # 总报价
        self.total_quote_label.configure(
            text=QuoteService.format_quote(result['total_quote'])
        )
        
        # 打印价格
        self.print_price_label.configure(
            text=QuoteService.format_quote(result['print_price'])
        )
        
        # 基准信息
        self.base_info_label.configure(
            text=f"    (基准 ¥{result['base_print_price']:,.0f} × 系数 {result['coefficient']})"
        )
        
        # 后处理价格
        self.post_price_label.configure(
            text=QuoteService.format_quote(result['post_process_price'])
        )
        
        # 预估时长
        self.time_label.configure(text=result['time_formatted'])
        
        # 计算明细
        detail_text = (
            f"材料效率: {result['efficiency']:.4f} g/min ({result['efficiency_source']})\n"
            f"开机成本: ¥{result['cost_per_min']:.4f}/min\n"
            f"预估时长: {result['time_min']:.1f} 分钟\n"
            f"基准打印价: ¥{result['base_print_price']:,.2f}\n"
            f"难度系数: {result['difficulty']}  |  风险系数: {result['risk']}\n"
            f"后处理: {result['post_process_hours']}小时 × ¥{result['post_process_rate']}/小时"
        )
        self.detail_label.configure(text=detail_text)
        
        # 效率信息
        if result['order_count'] > 0:
            self.efficiency_label.configure(
                text=f"📈 {result['efficiency_source']}"
            )
        else:
            self.efficiency_label.configure(
                text="📈 使用预设效率值"
            )
        
        # 更新设备信息
        self._update_machine_info()
    
    def _show_empty_result(self):
        """显示空结果"""
        self.total_quote_label.configure(text="¥0.00")
        self.print_price_label.configure(text="¥0.00")
        self.base_info_label.configure(text="    (基准 ¥0 × 系数 1)")
        self.post_price_label.configure(text="¥0.00")
        self.time_label.configure(text="--")
        self.detail_label.configure(text="请输入有效的重量值")
    
    def _update_machine_info(self):
        """更新设备配置信息"""
        config = get_active_machine_config()
        if config:
            cost_per_min = CostCalculator.calculate_cost_per_minute(
                config.total_price, config.depreciation_years
            )
            info_text = (
                f"🖨️ 设备: {config.machine_name} | "
                f"折旧: {config.depreciation_years}年 | "
                f"费率: ¥{cost_per_min:.2f}/min"
            )
        else:
            info_text = "⚠️ 未配置设备，请先进行设备配置"
        
        self.machine_info_label.configure(text=info_text)
    
    def refresh_data(self):
        """刷新数据 (外部调用)"""
        self._calculate_quote()
        self._update_machine_info()
    
    def on_show(self):
        """页面显示时的回调"""
        self.refresh_data()
