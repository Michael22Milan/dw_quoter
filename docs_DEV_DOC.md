# **SLM 智能报价系统 \- 开发架构文档 (Development Documentation)**

**文档版本**: v2.1

**目标读者**: Cursor AI, 开发人员

**技术栈**: Python 3.13+, CustomTkinter, SQLite, Peewee ORM

## **1\. 项目概览 (Project Overview)**

**SLM-Quoter** 是一款专为金属 3D 打印服务商设计的**离线桌面端报价软件**。

核心价值在于\*\*“数据驱动的自进化报价”\*\*：系统基于历史真实工单数据，动态计算材料的打印效率（g/min），结合设备折旧成本，实现精准、快速的自动化报价。

### **1.1 核心需求**

1. **离线运行**：Windows 环境，无外网依赖，本地 SQLite 数据库。  
2. **现代 UI**：使用 CustomTkinter 实现深色科技风（Dark/Cyberpunk）。  
3. **动态进化**：通过录入实际工单，自动修正“单位时间打印克重”，排除晶格结构干扰。  
4. **冷启动**：系统初始化时预置清洗后的历史数据（TC4 & 316L）。

## **2\. 系统架构 (System Architecture)**

采用 **MVP (Model-View-Presenter)** 的变体架构，确保界面与逻辑解耦。

### **2.1 目录结构**

SLM\_Quoter/  
├── main.py                 \# 程序入口  
├── requirements.txt        \# 依赖清单  
├── README.md               \# 项目说明  
├── docs/  
│   └── DEV\_DOC.md          \# 本文档  
├── src/  
│   ├── \_\_init\_\_.py  
│   ├── config.py           \# 全局配置 (常量定义)  
│   ├── database.py         \# 数据库连接与 ORM 模型定义  
│   ├── services.py         \# 核心业务逻辑 (计算、数据读写)  
│   └── ui/                 \# 界面层  
│       ├── \_\_init\_\_.py  
│       ├── app\_window.py   \# 主窗口框架  
│       ├── page\_config.py  \# 设备配置页  
│       ├── page\_quote.py   \# 报价计算页  
│       └── page\_data.py    \# 数据录入页  
└── assets/                 \# 图标、资源文件 (如有)  
    └── initial\_data.csv    \# 初始冷启动数据

## **3\. 数据库设计 (Database Schema)**

使用 Peewee ORM 管理 SQLite 数据库 slm\_data.db。

### **3.1 表结构**

#### **A. Material (材料表)**

| 字段名 | 类型 | 说明 |
| :---- | :---- | :---- |
| id | Integer | PK |
| name | String | 材料名称 (Unique) |
| default\_efficiency | Float | 出厂预设效率 (g/min) |

#### **B. WorkOrder (工单记录表)**

| 字段名 | 类型 | 说明 |
| :---- | :---- | :---- |
| id | Integer | PK |
| material | FK | 关联 Material 表 |
| weight\_g | Float | 实际重量 (g) |
| time\_min | Float | 实际打印时长 (min) |
| is\_lattice | Boolean | **关键字段**：是否为晶格结构 (True则不参与效率计算) |
| created\_at | DateTime | 录入时间 |

### **3.2 数据冷启动策略**

在 database.py 初始化时，检查数据库是否为空。若为空，则插入以下预设数据：

* **316L 不锈钢**: 预设效率 0.053 g/min  
* **TC4 钛合金**: 预设效率 0.047 g/min  
* 同时模拟写入几条历史工单数据以展示图表效果。

## **4\. 核心算法逻辑 (Core Algorithms)**

### **4.1 基础开机成本 (![][image1])**

\# 常量定义  
WORK\_DAYS\_PER\_YEAR \= 330  
HOURS\_PER\_DAY \= 8

def calculate\_machine\_cost(total\_price, depreciation\_years):  
    total\_minutes \= depreciation\_years \* WORK\_DAYS\_PER\_YEAR \* HOURS\_PER\_DAY \* 60  
    return total\_price / total\_minutes

### **4.2 动态材料效率 (![][image2])**

采用**加权平均法**，而非简单算术平均，以消除小样件波动误差。

**过滤条件**：必须排除 is\_lattice \== True 的记录。

$$ E\_{mat} \= \\frac{\\sum (\\text{HistoryWeights})}{\\sum (\\text{HistoryTimes})} $$

\# 伪代码逻辑  
valid\_orders \= query(WorkOrder).where(material=mat, is\_lattice=False)  
if not valid\_orders:  
    return mat.default\_efficiency  
total\_weight \= sum(o.weight\_g for o in valid\_orders)  
total\_time \= sum(o.time\_min for o in valid\_orders)  
return total\_weight / total\_time

### **4.3 最终报价 (![][image3])**

$$ P \= (\\frac{Weight}{E\_{mat}}) \\times C\_{min} \\times Difficulty $$

## **5\. UI/UX 规范 (UI Specification)**

### **5.1 风格指南**

* **库**: customtkinter  
* **主题**: System / Dark Blue  
* **字体**: Microsoft YaHei UI (Win) / Arial (Mac)  
* **布局**: 左侧侧边栏导航，右侧内容区。

### **5.2 页面功能**

#### **Page 1: 设备配置 (Machine Config)**

* **输入**: 设备型号 (DW-HP120/200)，折旧年限 (1/2/3年)。  
* **输出**: 实时计算并在卡片中高亮显示“每分钟成本”。  
* **联动**: 此处的计算结果必须存储在全局变量或单例中，供报价页调用。

#### **Page 2: 快速报价 (Quote Calculator)**

* **输入**: 材质选择 (下拉)，重量 (输入框)，难度 (滑块 0.8-2.0)。  
* **显示**:  
  * 预估打印时长 (xx小时xx分)  
  * 建议报价 (超大字体，青色高亮)  
  * 数据源提示 ("基于 xx 条历史数据计算")  
* **交互**: 输入即计算，无须点击按钮。**注意初始化顺序，避免 AttributeError**。

#### **Page 3: 数据进化 (Data Learning)**

* **输入**: 材质，实际重量，实际时长，**是否晶格(Switch开关)**。  
* **列表**: 展示最近 20 条录入记录。  
* **功能**: 点击“录入”后，自动刷新数据库，并触发全局效率重新计算。

## **6\. 开发任务清单 (Checklist for Cursor)**

请按以下顺序提示 Cursor 进行开发：

1. **环境初始化**:  
   * 创建目录结构。  
   * 创建 requirements.txt (仅需 customtkinter, peewee)。  
2. **数据层开发 (src/database.py)**:  
   * 定义 Model。  
   * 编写 init\_db() 函数，包含冷启动数据注入。  
3. **业务层开发 (src/services.py)**:  
   * 编写成本计算函数。  
   * 编写效率查询函数 (SQL Aggregation)。  
4. **UI 框架搭建 (src/ui/app\_window.py)**:  
   * 继承 CTk。  
   * 搭建 Sidebar 和 页面容器。  
   * **重要**: 确保页面实例化顺序，或使用 lazy loading 防止初始化报错。  
5. **页面实现**:  
   * 实现 Page 1, 2, 3 的布局和逻辑绑定。  
   * 实现 Page 3 的手写 Table 组件 (避免引入额外复杂库)。  
6. **联调与打包**:  
   * 在 main.py 中组装。  
   * 测试 Python 3.13 兼容性。  
   * 生成 PyInstaller 打包指令。

