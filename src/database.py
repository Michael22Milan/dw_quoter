# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 数据库模型
=============================
使用Peewee ORM管理SQLite数据库
包含材料表、工单表、设备配置表
"""

import os
from datetime import datetime
from peewee import (
    SqliteDatabase, Model, CharField, FloatField, 
    BooleanField, DateTimeField, ForeignKeyField, IntegerField
)
from .config import DATABASE_FILE, DEFAULT_MATERIALS, MACHINES, DEPRECIATION_YEARS_OPTIONS

# ============================================================
# 数据库连接
# ============================================================

# 获取数据库文件路径 (与主程序同目录)
def get_db_path():
    """获取数据库文件的绝对路径"""
    # 如果是打包后的exe，使用exe所在目录
    if getattr(os.sys, 'frozen', False):
        base_path = os.path.dirname(os.sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, DATABASE_FILE)

# 创建数据库连接
db = SqliteDatabase(None)  # 延迟初始化


# ============================================================
# 数据模型定义
# ============================================================

class BaseModel(Model):
    """基础模型类"""
    class Meta:
        database = db


class Material(BaseModel):
    """
    材料表 - 存储可用的打印材料及其预设效率
    
    字段:
        name: 材料名称 (唯一)
        default_efficiency: 出厂预设效率 (g/min)
        description: 材料描述
    """
    name = CharField(unique=True, max_length=50)
    default_efficiency = FloatField(default=0.05)
    description = CharField(max_length=200, default="")
    
    def __str__(self):
        return self.name


class WorkOrder(BaseModel):
    """
    工单记录表 - 存储历史打印工单数据
    
    字段:
        material: 关联的材料
        weight_g: 实际打印重量 (克)
        time_min: 实际打印时长 (分钟)
        is_lattice: 是否为晶格/点阵结构 (True则不参与效率计算)
        note: 备注信息
        created_at: 创建时间
    """
    material = ForeignKeyField(Material, backref='work_orders', on_delete='CASCADE')
    weight_g = FloatField()
    time_min = FloatField()
    is_lattice = BooleanField(default=False)
    note = CharField(max_length=200, default="")
    created_at = DateTimeField(default=datetime.now)
    
    def __str__(self):
        return f"{self.material.name} - {self.weight_g}g / {self.time_min}min"
    
    @property
    def efficiency(self):
        """计算该工单的打印效率 (g/min)"""
        if self.time_min > 0:
            return self.weight_g / self.time_min
        return 0


class MachineConfig(BaseModel):
    """
    设备配置表 - 存储用户选择的设备和折旧设置
    
    字段:
        machine_name: 设备型号
        total_price: 设备总价
        depreciation_years: 折旧年限
        is_active: 是否为当前激活配置
    """
    machine_name = CharField(max_length=50)
    total_price = IntegerField()
    depreciation_years = IntegerField(default=3)
    is_active = BooleanField(default=True)
    updated_at = DateTimeField(default=datetime.now)
    
    def __str__(self):
        return f"{self.machine_name} - {self.depreciation_years}年折旧"


# ============================================================
# 数据库初始化函数
# ============================================================

def init_db():
    """
    初始化数据库
    - 连接数据库
    - 创建表结构
    - 注入冷启动数据
    """
    db_path = get_db_path()
    db.init(db_path)
    db.connect()
    
    # 创建表 (如果不存在)
    db.create_tables([Material, WorkOrder, MachineConfig], safe=True)
    
    # 检查是否需要冷启动数据
    _inject_cold_start_data()
    
    return db


def _inject_cold_start_data():
    """
    注入冷启动数据
    - 预设材料信息
    - 模拟历史工单数据
    - 默认设备配置
    """
    # 1. 注入材料数据
    for mat_name, mat_info in DEFAULT_MATERIALS.items():
        Material.get_or_create(
            name=mat_name,
            defaults={
                'default_efficiency': mat_info['default_efficiency'],
                'description': mat_info.get('description', '')
            }
        )
    
    # 2. 检查是否有历史工单，没有则注入模拟数据
    if WorkOrder.select().count() == 0:
        _inject_sample_work_orders()
    
    # 3. 检查是否有设备配置，没有则创建默认配置
    if MachineConfig.select().count() == 0:
        # 默认使用DW-HP120，3年折旧
        MachineConfig.create(
            machine_name="DW-HP120",
            total_price=MACHINES["DW-HP120"],
            depreciation_years=3,
            is_active=True
        )


def _inject_sample_work_orders():
    """
    注入模拟的历史工单数据
    用于冷启动时提供初始的效率参考值
    """
    # 获取材料对象
    mat_316l = Material.get_or_none(Material.name == "316L不锈钢")
    mat_tc4 = Material.get_or_none(Material.name == "TC4钛合金")
    
    # 316L不锈钢的模拟工单 (效率约0.053 g/min)
    if mat_316l:
        sample_orders_316l = [
            {"weight_g": 150.0, "time_min": 2830.0, "is_lattice": False, "note": "标准结构件"},
            {"weight_g": 85.0, "time_min": 1603.0, "is_lattice": False, "note": "支架"},
            {"weight_g": 220.0, "time_min": 4150.0, "is_lattice": False, "note": "壳体"},
            {"weight_g": 45.0, "time_min": 849.0, "is_lattice": False, "note": "小型零件"},
            {"weight_g": 180.0, "time_min": 3396.0, "is_lattice": False, "note": "法兰盘"},
        ]
        for order in sample_orders_316l:
            WorkOrder.create(material=mat_316l, **order)
    
    # TC4钛合金的模拟工单 (效率约0.047 g/min)
    if mat_tc4:
        sample_orders_tc4 = [
            {"weight_g": 120.0, "time_min": 2553.0, "is_lattice": False, "note": "航空接头"},
            {"weight_g": 65.0, "time_min": 1383.0, "is_lattice": False, "note": "医疗植入件"},
            {"weight_g": 200.0, "time_min": 4255.0, "is_lattice": False, "note": "结构件"},
            {"weight_g": 35.0, "time_min": 745.0, "is_lattice": False, "note": "小型配件"},
            {"weight_g": 95.0, "time_min": 2021.0, "is_lattice": False, "note": "支架结构"},
        ]
        for order in sample_orders_tc4:
            WorkOrder.create(material=mat_tc4, **order)


def close_db():
    """关闭数据库连接"""
    if not db.is_closed():
        db.close()


# ============================================================
# 数据查询辅助函数
# ============================================================

def get_all_materials():
    """获取所有材料列表"""
    return list(Material.select())


def get_material_by_name(name):
    """根据名称获取材料"""
    return Material.get_or_none(Material.name == name)


def get_active_machine_config():
    """获取当前激活的设备配置"""
    return MachineConfig.get_or_none(MachineConfig.is_active == True)


def save_machine_config(machine_name, depreciation_years):
    """
    保存设备配置
    
    Args:
        machine_name: 设备型号
        depreciation_years: 折旧年限
    """
    # 先将所有配置设为非激活
    MachineConfig.update(is_active=False).execute()
    
    # 获取设备价格
    total_price = MACHINES.get(machine_name, 1_500_000)
    
    # 创建或更新配置
    config, created = MachineConfig.get_or_create(
        machine_name=machine_name,
        depreciation_years=depreciation_years,
        defaults={
            'total_price': total_price,
            'is_active': True,
            'updated_at': datetime.now()
        }
    )
    
    if not created:
        config.is_active = True
        config.updated_at = datetime.now()
        config.save()
    
    return config


def add_work_order(material_name, weight_g, time_min, is_lattice=False, note=""):
    """
    添加新的工单记录
    
    Args:
        material_name: 材料名称
        weight_g: 重量 (克)
        time_min: 时长 (分钟)
        is_lattice: 是否晶格结构
        note: 备注
    
    Returns:
        WorkOrder: 创建的工单对象
    """
    material = get_material_by_name(material_name)
    if not material:
        raise ValueError(f"材料 '{material_name}' 不存在")
    
    return WorkOrder.create(
        material=material,
        weight_g=weight_g,
        time_min=time_min,
        is_lattice=is_lattice,
        note=note
    )


def get_recent_work_orders(limit=20):
    """获取最近的工单记录"""
    return (WorkOrder
            .select(WorkOrder, Material)
            .join(Material)
            .order_by(WorkOrder.created_at.desc())
            .limit(limit))


def delete_work_order(order_id):
    """删除指定工单"""
    order = WorkOrder.get_or_none(WorkOrder.id == order_id)
    if order:
        order.delete_instance()
        return True
    return False
