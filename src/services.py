# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 核心业务逻辑
================================
包含成本计算、效率统计、报价生成等核心算法
"""

from peewee import fn
from .config import WORK_DAYS_PER_YEAR, HOURS_PER_DAY, MACHINES
from .database import (
    Material, WorkOrder, MachineConfig,
    get_active_machine_config, get_material_by_name
)


# ============================================================
# 成本计算服务
# ============================================================

class CostCalculator:
    """
    成本计算器
    基于设备价格和折旧年限计算每分钟开机成本
    """
    
    @staticmethod
    def calculate_cost_per_minute(total_price: int, depreciation_years: int) -> float:
        """
        计算每分钟开机成本
        
        公式: 设备总价 / (折旧年限 × 年工作天数 × 日工作小时 × 60分钟)
        
        Args:
            total_price: 设备总价 (元)
            depreciation_years: 折旧年限 (年)
        
        Returns:
            float: 每分钟成本 (元/分钟)
        """
        total_minutes = (depreciation_years * 
                        WORK_DAYS_PER_YEAR * 
                        HOURS_PER_DAY * 
                        60)
        return total_price / total_minutes
    
    @staticmethod
    def get_machine_cost_table():
        """
        获取所有设备在不同折旧年限下的成本表
        
        Returns:
            dict: {设备型号: {年限: 每分钟成本}}
        """
        cost_table = {}
        for machine_name, total_price in MACHINES.items():
            cost_table[machine_name] = {}
            for years in [1, 2, 3]:
                cost_per_min = CostCalculator.calculate_cost_per_minute(
                    total_price, years
                )
                cost_table[machine_name][years] = cost_per_min
        return cost_table
    
    @staticmethod
    def get_current_cost_per_minute() -> float:
        """
        获取当前配置下的每分钟成本
        
        Returns:
            float: 每分钟成本，如果没有配置返回0
        """
        config = get_active_machine_config()
        if config:
            return CostCalculator.calculate_cost_per_minute(
                config.total_price,
                config.depreciation_years
            )
        return 0.0


# ============================================================
# 效率统计服务
# ============================================================

class EfficiencyService:
    """
    效率统计服务
    基于历史工单数据动态计算材料打印效率
    """
    
    @staticmethod
    def get_material_efficiency(material_name: str) -> tuple:
        """
        获取指定材料的打印效率
        
        使用加权平均法计算: 总重量 / 总时长
        自动排除晶格结构的工单数据
        
        Args:
            material_name: 材料名称
        
        Returns:
            tuple: (效率值g/min, 数据来源描述, 有效工单数)
        """
        material = get_material_by_name(material_name)
        if not material:
            return 0.05, "默认值", 0
        
        # 查询该材料的有效工单 (排除晶格结构)
        valid_orders = (WorkOrder
                       .select()
                       .where(
                           (WorkOrder.material == material) &
                           (WorkOrder.is_lattice == False)
                       ))
        
        order_count = valid_orders.count()
        
        if order_count == 0:
            # 没有历史数据，返回预设效率
            return material.default_efficiency, "预设值", 0
        
        # 使用聚合查询计算总重量和总时长
        stats = (WorkOrder
                .select(
                    fn.SUM(WorkOrder.weight_g).alias('total_weight'),
                    fn.SUM(WorkOrder.time_min).alias('total_time')
                )
                .where(
                    (WorkOrder.material == material) &
                    (WorkOrder.is_lattice == False)
                )
                .dicts()
                .first())
        
        total_weight = stats['total_weight'] or 0
        total_time = stats['total_time'] or 0
        
        if total_time > 0:
            efficiency = total_weight / total_time
            return efficiency, f"基于{order_count}条历史数据", order_count
        
        return material.default_efficiency, "预设值", 0
    
    @staticmethod
    def get_all_materials_efficiency() -> dict:
        """
        获取所有材料的效率统计
        
        Returns:
            dict: {材料名: (效率, 来源, 工单数)}
        """
        from .database import get_all_materials
        
        result = {}
        for material in get_all_materials():
            result[material.name] = EfficiencyService.get_material_efficiency(
                material.name
            )
        return result


# ============================================================
# 报价服务
# ============================================================

class QuoteService:
    """
    报价服务
    整合成本和效率计算，生成最终报价
    """
    
    @staticmethod
    def calculate_quote(
        material_name: str,
        weight_g: float,
        difficulty: float = 1.0
    ) -> dict:
        """
        计算报价
        
        公式: 报价 = (重量 / 效率) × 每分钟成本 × 难度系数
        
        Args:
            material_name: 材料名称
            weight_g: 预估重量 (克)
            difficulty: 难度系数 (0.8-2.0)
        
        Returns:
            dict: {
                'quote': 报价金额,
                'time_min': 预估时长(分钟),
                'time_formatted': 格式化时长,
                'efficiency': 使用的效率值,
                'efficiency_source': 效率数据来源,
                'cost_per_min': 每分钟成本,
                'order_count': 参考的工单数
            }
        """
        # 获取每分钟成本
        cost_per_min = CostCalculator.get_current_cost_per_minute()
        
        # 获取材料效率
        efficiency, source, order_count = EfficiencyService.get_material_efficiency(
            material_name
        )
        
        # 计算预估打印时长 (分钟)
        if efficiency > 0:
            time_min = weight_g / efficiency
        else:
            time_min = 0
        
        # 计算报价
        quote = time_min * cost_per_min * difficulty
        
        # 格式化时长
        hours = int(time_min // 60)
        minutes = int(time_min % 60)
        if hours > 0:
            time_formatted = f"{hours}小时{minutes}分钟"
        else:
            time_formatted = f"{minutes}分钟"
        
        return {
            'quote': round(quote, 2),
            'time_min': round(time_min, 1),
            'time_formatted': time_formatted,
            'efficiency': round(efficiency, 4),
            'efficiency_source': source,
            'cost_per_min': round(cost_per_min, 4),
            'order_count': order_count
        }
    
    @staticmethod
    def format_quote(quote: float) -> str:
        """
        格式化报价金额
        
        Args:
            quote: 报价金额
        
        Returns:
            str: 格式化后的字符串 (如: ¥12,345.00)
        """
        return f"¥{quote:,.2f}"


# ============================================================
# 数据统计服务
# ============================================================

class StatisticsService:
    """
    数据统计服务
    提供各类统计分析功能
    """
    
    @staticmethod
    def get_overview_stats() -> dict:
        """
        获取概览统计数据
        
        Returns:
            dict: 包含总工单数、各材料工单数等
        """
        from .database import get_all_materials
        
        total_orders = WorkOrder.select().count()
        valid_orders = WorkOrder.select().where(WorkOrder.is_lattice == False).count()
        lattice_orders = total_orders - valid_orders
        
        # 各材料统计
        material_stats = {}
        for material in get_all_materials():
            count = (WorkOrder
                    .select()
                    .where(WorkOrder.material == material)
                    .count())
            material_stats[material.name] = count
        
        return {
            'total_orders': total_orders,
            'valid_orders': valid_orders,
            'lattice_orders': lattice_orders,
            'material_stats': material_stats
        }
