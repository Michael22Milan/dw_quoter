# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 数据进化页
==============================
录入实际工单数据，不断优化打印效率的估算
"""

import customtkinter as ctk
from datetime import datetime
from ..config import COLORS, FONTS
from ..database import (
    get_all_materials, add_work_order, 
    get_recent_work_orders, delete_work_order
)
from ..services import EfficiencyService


class DataPage(ctk.CTkFrame):
    """
    数据进化页面
    
    功能:
    - 录入实际打印工单
    - 标记晶格结构 (不参与效率计算)
    - 展示最近录入的工单列表
    - 显示当前材料效率统计
    """
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 输入变量
        self.selected_material = ctk.StringVar(value="316L不锈钢")
        self.weight_var = ctk.StringVar(value="")
        self.time_hours_var = ctk.StringVar(value="")
        self.time_mins_var = ctk.StringVar(value="")
        self.is_lattice_var = ctk.BooleanVar(value=False)
        self.note_var = ctk.StringVar(value="")
        
        # 构建界面
        self._create_header()
        self._create_content()
    
    def _create_header(self):
        """创建页面标题区"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 20))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 数据进化",
            font=FONTS["title"],
            text_color=COLORS["text_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="录入真实工单数据，让报价系统越用越准确",
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
        # 左侧: 工单录入表单
        # ============================================================
        form_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        form_card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 15), pady=10)
        
        # 表单标题
        form_title = ctk.CTkLabel(
            form_card,
            text="📝 录入新工单",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        form_title.pack(anchor="w", padx=25, pady=(25, 20))
        
        # --- 材质选择 ---
        material_label = ctk.CTkLabel(
            form_card,
            text="🧪 打印材质",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        material_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        materials = get_all_materials()
        material_names = [m.name for m in materials] if materials else ["316L不锈钢", "TC4钛合金"]
        
        self.material_menu = ctk.CTkOptionMenu(
            form_card,
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
            dropdown_fg_color=COLORS["bg_card"]
        )
        self.material_menu.pack(anchor="w", padx=25, pady=(0, 15))
        
        # --- 实际重量 ---
        weight_label = ctk.CTkLabel(
            form_card,
            text="⚖️ 实际重量 (克)",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        weight_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        self.weight_entry = ctk.CTkEntry(
            form_card,
            textvariable=self.weight_var,
            font=FONTS["body"],
            width=250,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="输入实际打印重量"
        )
        self.weight_entry.pack(anchor="w", padx=25, pady=(0, 15))
        
        # --- 实际时长 ---
        time_label = ctk.CTkLabel(
            form_card,
            text="⏱️ 实际打印时长",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        time_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        time_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        time_frame.pack(anchor="w", padx=25, pady=(0, 15))
        
        self.hours_entry = ctk.CTkEntry(
            time_frame,
            textvariable=self.time_hours_var,
            font=FONTS["body"],
            width=80,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="小时"
        )
        self.hours_entry.pack(side="left")
        
        hours_label = ctk.CTkLabel(
            time_frame,
            text="小时",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        hours_label.pack(side="left", padx=(5, 15))
        
        self.mins_entry = ctk.CTkEntry(
            time_frame,
            textvariable=self.time_mins_var,
            font=FONTS["body"],
            width=80,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="分钟"
        )
        self.mins_entry.pack(side="left")
        
        mins_label = ctk.CTkLabel(
            time_frame,
            text="分钟",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        mins_label.pack(side="left", padx=(5, 0))
        
        # --- 晶格结构开关 ---
        lattice_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        lattice_frame.pack(fill="x", padx=25, pady=(15, 5))
        
        self.lattice_switch = ctk.CTkSwitch(
            lattice_frame,
            text="🔷 是晶格/点阵结构",
            variable=self.is_lattice_var,
            font=FONTS["body"],
            fg_color=COLORS["bg_dark"],
            progress_color=COLORS["warning"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"]
        )
        self.lattice_switch.pack(anchor="w")
        
        lattice_hint = ctk.CTkLabel(
            form_card,
            text="⚠️ 晶格结构的数据不会参与效率计算",
            font=FONTS["small"],
            text_color=COLORS["warning"]
        )
        lattice_hint.pack(anchor="w", padx=25, pady=(5, 15))
        
        # --- 备注 ---
        note_label = ctk.CTkLabel(
            form_card,
            text="📋 备注 (可选)",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        )
        note_label.pack(anchor="w", padx=25, pady=(10, 5))
        
        self.note_entry = ctk.CTkEntry(
            form_card,
            textvariable=self.note_var,
            font=FONTS["body"],
            width=250,
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            placeholder_text="零件名称或备注"
        )
        self.note_entry.pack(anchor="w", padx=25, pady=(0, 25))
        
        # --- 提交按钮 ---
        submit_btn = ctk.CTkButton(
            form_card,
            text="📥 录入工单",
            font=FONTS["subtitle"],
            height=50,
            width=250,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._submit_order
        )
        submit_btn.pack(anchor="w", padx=25, pady=(0, 25))
        
        # 状态提示
        self.status_label = ctk.CTkLabel(
            form_card,
            text="",
            font=FONTS["small"],
            text_color=COLORS["success"]
        )
        self.status_label.pack(anchor="w", padx=25, pady=(0, 20))
        
        # ============================================================
        # 右上: 效率统计卡片
        # ============================================================
        stats_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        stats_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=10)
        
        stats_title = ctk.CTkLabel(
            stats_card,
            text="📈 当前效率统计",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        stats_title.pack(anchor="w", padx=25, pady=(20, 15))
        
        self.stats_content = ctk.CTkFrame(stats_card, fg_color="transparent")
        self.stats_content.pack(fill="x", padx=25, pady=(0, 20))
        
        # ============================================================
        # 右下: 最近工单列表
        # ============================================================
        list_card = ctk.CTkFrame(
            content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        list_card.grid(row=1, column=1, sticky="nsew", padx=(15, 0), pady=(10, 10))
        
        list_header = ctk.CTkFrame(list_card, fg_color="transparent")
        list_header.pack(fill="x", padx=25, pady=(20, 10))
        
        list_title = ctk.CTkLabel(
            list_header,
            text="📋 最近录入 (最新20条)",
            font=FONTS["subtitle"],
            text_color=COLORS["accent"]
        )
        list_title.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            list_header,
            text="🔄",
            font=FONTS["body"],
            width=35,
            height=35,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["bg_dark"],
            command=self._refresh_list
        )
        refresh_btn.pack(side="right")
        
        # 工单列表滚动区域
        self.list_scroll = ctk.CTkScrollableFrame(
            list_card,
            fg_color="transparent",
            corner_radius=0
        )
        self.list_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))
    
    def _submit_order(self):
        """提交工单"""
        try:
            # 获取输入
            material = self.selected_material.get()
            weight_str = self.weight_var.get().strip()
            hours_str = self.time_hours_var.get().strip()
            mins_str = self.time_mins_var.get().strip()
            is_lattice = self.is_lattice_var.get()
            note = self.note_var.get().strip()
            
            # 验证输入
            if not weight_str:
                self._show_status("❌ 请输入重量", "error")
                return
            
            weight = float(weight_str)
            if weight <= 0:
                self._show_status("❌ 重量必须大于0", "error")
                return
            
            # 计算总时长 (分钟)
            hours = float(hours_str) if hours_str else 0
            mins = float(mins_str) if mins_str else 0
            total_mins = hours * 60 + mins
            
            if total_mins <= 0:
                self._show_status("❌ 请输入有效的打印时长", "error")
                return
            
            # 添加工单
            add_work_order(
                material_name=material,
                weight_g=weight,
                time_min=total_mins,
                is_lattice=is_lattice,
                note=note
            )
            
            # 清空表单
            self.weight_var.set("")
            self.time_hours_var.set("")
            self.time_mins_var.set("")
            self.is_lattice_var.set(False)
            self.note_var.set("")
            
            # 刷新显示
            self._refresh_stats()
            self._refresh_list()
            
            # 刷新报价页
            self.app.refresh_quote_page()
            
            # 显示成功提示
            efficiency = weight / total_mins
            self._show_status(
                f"✅ 录入成功! 效率: {efficiency:.4f} g/min",
                "success"
            )
            
        except ValueError as e:
            self._show_status(f"❌ 输入格式错误: {e}", "error")
        except Exception as e:
            self._show_status(f"❌ 录入失败: {e}", "error")
    
    def _show_status(self, message: str, status_type: str = "success"):
        """显示状态提示"""
        color = COLORS["success"] if status_type == "success" else COLORS["warning"]
        self.status_label.configure(text=message, text_color=color)
        
        # 3秒后清除
        self.after(3000, lambda: self.status_label.configure(text=""))
    
    def _refresh_stats(self):
        """刷新效率统计"""
        # 清除旧内容
        for widget in self.stats_content.winfo_children():
            widget.destroy()
        
        # 获取效率统计
        stats = EfficiencyService.get_all_materials_efficiency()
        
        for material_name, (efficiency, source, count) in stats.items():
            row_frame = ctk.CTkFrame(self.stats_content, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            name_label = ctk.CTkLabel(
                row_frame,
                text=f"🧪 {material_name}",
                font=FONTS["body"],
                text_color=COLORS["text_primary"]
            )
            name_label.pack(anchor="w")
            
            value_label = ctk.CTkLabel(
                row_frame,
                text=f"    效率: {efficiency:.4f} g/min ({source})",
                font=FONTS["small"],
                text_color=COLORS["accent"]
            )
            value_label.pack(anchor="w")
    
    def _refresh_list(self):
        """刷新工单列表"""
        # 清除旧内容
        for widget in self.list_scroll.winfo_children():
            widget.destroy()
        
        # 获取最近工单
        orders = get_recent_work_orders(20)
        
        if not orders:
            empty_label = ctk.CTkLabel(
                self.list_scroll,
                text="暂无工单记录\n开始录入您的第一条工单吧!",
                font=FONTS["body"],
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(pady=30)
            return
        
        # 显示工单列表
        for order in orders:
            self._create_order_row(order)
    
    def _create_order_row(self, order):
        """创建工单行"""
        row_frame = ctk.CTkFrame(
            self.list_scroll,
            fg_color=COLORS["bg_dark"],
            corner_radius=8
        )
        row_frame.pack(fill="x", pady=3, padx=5)
        
        # 左侧信息
        info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=8)
        
        # 第一行: 材质和重量
        line1 = ctk.CTkLabel(
            info_frame,
            text=f"🧪 {order.material.name}  |  ⚖️ {order.weight_g}g  |  ⏱️ {order.time_min:.0f}min",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        )
        line1.pack(anchor="w")
        
        # 第二行: 效率和时间
        efficiency = order.weight_g / order.time_min if order.time_min > 0 else 0
        lattice_tag = " 🔷晶格" if order.is_lattice else ""
        note_text = f" | {order.note}" if order.note else ""
        
        line2 = ctk.CTkLabel(
            info_frame,
            text=f"效率: {efficiency:.4f} g/min{lattice_tag}{note_text}",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        line2.pack(anchor="w")
        
        # 删除按钮
        del_btn = ctk.CTkButton(
            row_frame,
            text="🗑️",
            font=FONTS["small"],
            width=30,
            height=30,
            corner_radius=5,
            fg_color="transparent",
            hover_color=COLORS["warning"],
            command=lambda oid=order.id: self._delete_order(oid)
        )
        del_btn.pack(side="right", padx=10)
    
    def _delete_order(self, order_id):
        """删除工单"""
        if delete_work_order(order_id):
            self._refresh_stats()
            self._refresh_list()
            self.app.refresh_quote_page()
            self._show_status("✅ 已删除", "success")
    
    def on_show(self):
        """页面显示时的回调"""
        self._refresh_stats()
        self._refresh_list()
