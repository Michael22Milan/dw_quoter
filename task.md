# SLM智能报价系统 v2.2 - 开发任务清单

**关联提案**: proposal.md  
**预计影响文件**: 4个

---

## 任务总览

| 序号 | 任务 | 涉及文件 | 优先级 |
|------|------|----------|--------|
| T1 | 更新配置常量 | `src/config.py` | P0 |
| T2 | 修改报价算法 | `src/services.py` | P0 |
| T3 | 重构报价页面UI | `src/ui/page_quote.py` | P0 |
| T4 | 更新文档 | `README.md` | P1 |

---

## 详细任务

### T1: 更新配置常量 (`src/config.py`)

**变更内容**：

- [ ] 删除原有难度系数范围配置 (`DIFFICULTY_MIN`, `DIFFICULTY_MAX`, `DIFFICULTY_DEFAULT`)
- [ ] 新增难度系数选项列表（带描述文字）
  ```python
  DIFFICULTY_OPTIONS = {
      1: "1 - 正常",
      2: "2 - 偏难", 
      3: "3 - 很难"
  }
  DIFFICULTY_DEFAULT = 1
  ```
- [ ] 新增风险系数选项列表
  ```python
  RISK_OPTIONS = [0, 0.5, 1, 1.5, 2]
  RISK_DEFAULT = 0
  ```
- [ ] 新增后处理相关配置
  ```python
  POST_PROCESS_RATE_DEFAULT = 50  # 元/小时
  POST_PROCESS_RATE_MIN = 10
  POST_PROCESS_RATE_MAX = 200
  ```

---

### T2: 修改报价算法 (`src/services.py`)

**变更内容**：

- [ ] 修改 `QuoteService.calculate_quote()` 方法签名
  ```python
  def calculate_quote(
      material_name: str,
      weight_g: float,
      difficulty: int = 1,           # 改为整数
      risk: float = 0,               # 新增
      post_process_hours: float = 0, # 新增
      post_process_rate: float = 50  # 新增
  ) -> dict:
  ```

- [ ] 修改报价计算逻辑
  ```python
  # 基准打印价格
  base_print_price = time_min * cost_per_min
  
  # 打印价格 = 基准价格 × (难度系数 + 风险系数)
  coefficient = difficulty + risk
  print_price = base_print_price * coefficient
  
  # 后处理价格
  post_process_price = post_process_hours * post_process_rate
  
  # 最终报价
  total_quote = print_price + post_process_price
  ```

- [ ] 修改返回值结构
  ```python
  return {
      'base_print_price': ...,    # 基准打印价格
      'print_price': ...,         # 打印价格（含系数）
      'post_process_price': ...,  # 后处理价格
      'total_quote': ...,         # 最终总报价
      'coefficient': ...,         # 系数和（难度+风险）
      'time_min': ...,
      'time_formatted': ...,
      'efficiency': ...,
      'efficiency_source': ...,
      'cost_per_min': ...,
      'order_count': ...
  }
  ```

---

### T3: 重构报价页面UI (`src/ui/page_quote.py`)

**变更内容**：

#### 3.1 输入组件变更

- [ ] 删除难度系数滑块 (`CTkSlider`)
- [ ] 新增难度系数下拉框 (`CTkOptionMenu`)
  - 选项: "1 - 正常", "2 - 偏难", "3 - 很难"
  - 默认值: "1 - 正常"
- [ ] 新增风险系数下拉框 (`CTkOptionMenu`)
  - 选项: 0, 0.5, 1, 1.5, 2
  - 默认值: 0
- [ ] 新增后处理时长输入框 (`CTkEntry`)
  - 单位: 小时
  - 默认值: 0
- [ ] 新增后处理单价输入框 (`CTkEntry`)
  - 单位: 元/小时
  - 默认值: 50
  - 可编辑

#### 3.2 输出显示变更

- [ ] 修改报价显示区域，分项展示：
  - 基准打印价格
  - 系数加成 (难度 + 风险)
  - **打印价格** (突出显示)
  - 后处理价格
  - **最终总报价** (最大字体突出显示)

#### 3.3 计算明细变更

- [ ] 更新计算明细显示内容：
  ```
  📊 计算明细:
      材料效率: x.xxxx g/min (数据来源)
      开机成本: ¥x.xxxx/min
      预估时长: xx小时xx分钟
      基准打印价: ¥xxxx.xx
      难度系数: x
      风险系数: x.x
      系数加成: x (难度+风险)
      后处理时长: x.x 小时
      后处理单价: ¥xx/小时
  ```

#### 3.4 变量绑定

- [ ] 更新变量定义
  ```python
  self.difficulty_var = ctk.StringVar(value="1 - 正常")
  self.risk_var = ctk.StringVar(value="0")
  self.post_hours_var = ctk.StringVar(value="0")
  self.post_rate_var = ctk.StringVar(value="50")
  ```

- [ ] 绑定变化事件，实现实时计算

---

### T4: 更新文档 (`README.md`)

**变更内容**：

- [ ] 更新版本号为 v2.2
- [ ] 更新报价公式说明
- [ ] 更新使用指南中的快速报价部分
- [ ] 新增后处理价格说明
- [ ] 更新版本历史

---

## 执行顺序

```
T1 (config.py) 
    ↓
T2 (services.py)
    ↓
T3 (page_quote.py)
    ↓
T4 (README.md)
    ↓
测试验证
    ↓
重新打包exe
```

---

## 验收标准

- [ ] 难度系数改为下拉选择 (1-正常/2-偏难/3-很难)
- [ ] 风险系数下拉可用 (0/0.5/1/1.5/2)
- [ ] 后处理时长可输入
- [ ] 后处理单价可调整（默认50）
- [ ] 报价分项显示（打印价格/后处理价格/总报价）
- [ ] 公式正确：打印价格 = 基准价 × (难度+风险)
- [ ] 实时计算无延迟
- [ ] 无报错/崩溃

---

**用户已确认，可开始执行**
