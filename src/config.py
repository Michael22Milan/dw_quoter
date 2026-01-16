# -*- coding: utf-8 -*-
"""
SLM智能报价系统 - 全局配置常量
================================
包含设备信息、折旧参数、UI主题等全局配置
"""

# ============================================================
# 设备配置 (Machine Configuration)
# ============================================================

# 设备型号与对应价格 (单位: 元)
MACHINES = {
    "DW-HP120": 1_500_000,  # 150万
    "DW-HP200": 3_000_000,  # 300万
}

# 可选折旧年限
DEPRECIATION_YEARS_OPTIONS = [1, 2, 3]

# ============================================================
# 工作时间参数 (Working Time Parameters)
# ============================================================

# 每年工作天数 (考虑节假日和维护)
WORK_DAYS_PER_YEAR = 330

# 每天工作小时数
HOURS_PER_DAY = 8

# ============================================================
# 材料配置 (Material Configuration)
# ============================================================

# 材料预设效率 (g/min) - 冷启动时使用
DEFAULT_MATERIALS = {
    "316L不锈钢": {
        "default_efficiency": 0.053,  # g/min
        "description": "奥氏体不锈钢，耐腐蚀性优异"
    },
    "TC4钛合金": {
        "default_efficiency": 0.047,  # g/min
        "description": "Ti-6Al-4V，航空航天常用材料"
    }
}

# ============================================================
# 难度系数配置 (Difficulty Coefficient)
# ============================================================

# 难度系数范围
DIFFICULTY_MIN = 0.8   # 最小难度 (简单几何体)
DIFFICULTY_MAX = 2.0   # 最大难度 (复杂结构)
DIFFICULTY_DEFAULT = 1.0  # 默认难度

# ============================================================
# UI 主题配置 (UI Theme Configuration)
# ============================================================

# 窗口尺寸
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# 颜色主题 (深色科技风)
COLORS = {
    "bg_dark": "#1a1a2e",        # 深色背景
    "bg_card": "#16213e",        # 卡片背景
    "bg_sidebar": "#0f0f23",     # 侧边栏背景
    "accent": "#00d4ff",         # 强调色 (青色)
    "accent_hover": "#00a8cc",   # 强调色悬停
    "success": "#00ff88",        # 成功色 (绿色)
    "warning": "#ffaa00",        # 警告色 (橙色)
    "text_primary": "#ffffff",   # 主文本
    "text_secondary": "#a0a0a0", # 次要文本
    "border": "#2a2a4a",         # 边框色
}

# 字体配置
FONTS = {
    "title": ("Microsoft YaHei UI", 24, "bold"),
    "subtitle": ("Microsoft YaHei UI", 16, "bold"),
    "body": ("Microsoft YaHei UI", 13),
    "small": ("Microsoft YaHei UI", 11),
    "price": ("Microsoft YaHei UI", 48, "bold"),  # 报价大字体
    "mono": ("Consolas", 13),  # 等宽字体
}

# ============================================================
# 应用程序信息 (Application Info)
# ============================================================

APP_NAME = "SLM 智能报价系统"
APP_VERSION = "2.1"
APP_AUTHOR = "DW Tech"

# 数据库文件名
DATABASE_FILE = "slm_data.db"
