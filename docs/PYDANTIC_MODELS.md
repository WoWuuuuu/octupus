# 🎓 Octopus Pydantic 模型详解

## 📋 概述

Octopus 使用 **Pydantic** 作为核心的数据验证和序列化框架。所有决策层和执行层之间的通信都通过强类型的 Pydantic 模型进行。

## 🎯 为什么选择 Pydantic？

1. **类型安全** - 编译时检查数据类型
2. **自动验证** - 内置数据验证逻辑
3. **自文档化** - 自动生成 JSON Schema
4. **序列化** - 轻松转换为 JSON
5. **IDE 支持** - 完整的代码补全和类型检查

---

## 📦 模型分类

### 1. 任务请求模型（Brain → Tentacle）

#### TaskRequest - 任务请求

**文件**: `octopus/models/core_models.py:179`

```python
class TaskRequest(BaseModel):
    """
    TaskRequest - Brain 发送给 Tentacle 的任务命令包
    
    作用：
    - 定义要执行的具体任务
    - 指定使用哪个工具
    - 传递必要的参数
    - 设置约束和优先级
    """
    
    # 任务标识
    task_id: str  # 唯一任务ID (UUID)
    plan_id: Optional[str]  # 所属计划ID
    
    # 执行信息
    tool_id: str  # 使用哪个工具
    parameters: Dict[str, Any]  # 工具参数
    
    # 优先级和调度
    priority: TaskPriority = TaskPriority.NORMAL
    
    # 约束和护栏
    constraints: TaskConstraints = TaskConstraints()
    
    # 上下文
    context: TaskContext = TaskContext()
    
    # 重试配置
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: float = Field(default=1.0, ge=0)
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="brain")
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
```

**使用示例**:

```python
task = TaskRequest(
    task_id="task_001",
    plan_id="plan_001",
    tool_id="web_scraper",
    parameters={
        "url": "https://example.com",
        "selectors": ["h1", ".price"]
    },
    priority=TaskPriority.HIGH,
    constraints=TaskConstraints(
        max_execution_time_seconds=30
    )
)
```

---

#### TaskConstraints - 任务约束

**文件**: `octopus/models/core_models.py:157`

```python
class TaskConstraints(BaseModel):
    """
    TaskConstraints - 任务执行的约束和限制
    
    作用：
    - 设置超时限制
    - 控制成本
    - 限制可用工具
    - 定义重试策略
    """
    
    max_execution_time_seconds: Optional[int] = None
    max_cost: Optional[float] = None
    
    # 工具限制
    allowed_tools: Optional[List[str]] = None
    blocked_tools: Optional[List[str]] = None
    require_approval_before: Optional[List[str]] = None
    
    # 重试策略
    retry_policy: Optional[Dict[str, Any]] = None
```

---

#### TaskContext - 任务上下文

**文件**: `octopus/models/core_models.py:166`

```python
class TaskContext(BaseModel):
    """
    TaskContext - 任务执行的上下文信息
    
    作用：
    - 传递用户信息
    - 维护会话历史
    - 追踪实体状态
    """
    
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    entity_state: Dict[str, Any] = Field(default_factory=dict)
    custom: Dict[str, Any] = Field(default_factory=dict)
```

---

### 2. 计划模型（Brain 的输出）

#### Plan - 执行计划

**文件**: `octopus/models/core_models.py:298`

```python
class Plan(BaseModel):
    """
    Plan - Brain 生成的完整执行蓝图
    
    作用：
    - 定义完整的执行计划
    - 包含所有执行步骤
    - 记录决策理由
    - 设置成功标准
    
    这是 Decision Brain 的主要输出！
    """
    
    # 计划标识
    plan_id: str  # 唯一计划ID
    
    # 目标
    objective: str  # 高层次目标
    description: Optional[str] = None
    
    # 执行步骤
    steps: List[ExecutionStep]  # 有序执行步骤列表
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    
    # 状态
    status: PlanStatus = PlanStatus.DRAFT
    
    # Brain 的推理过程（用于可观测性）
    reasoning: str  # 为什么选择这个方案
    alternatives_considered: List[str] = Field(default_factory=list)
    simulation_results: Optional[Dict[str, Any]] = None
    
    # 成功标准
    success_criteria: List[str] = Field(default_factory=list)
    expected_outcome: Optional[Dict[str, Any]] = None
    
    # 错误处理
    fallback_plan_id: Optional[str] = None
    max_execution_time_seconds: Optional[int] = None
    
    # 验证
    is_validated: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    
    # 伦理检查
    ethics_approved: bool = False
    ethics_notes: Optional[str] = None
    constraints_satisfied: bool = True
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="brain")
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1
    
    # 结果（执行时填充）
    completed_steps: List[str] = Field(default_factory=list)
    step_results: Dict[str, ToolResult] = Field(default_factory=dict)
    final_output: Optional[Any] = None
```

**使用示例**:

```python
plan = Plan(
    plan_id="plan_001",
    objective="分析竞品价格策略",
    reasoning="需要先抓取数据，再进行分析，最后生成报告",
    steps=[
        ExecutionStep(
            step_id="scrape",
            order=0,
            tool_id="web_scraper",
            description="抓取竞品网站",
            parameters={"urls": ["site1.com", "site2.com"]}
        ),
        ExecutionStep(
            step_id="analyze",
            order=1,
            tool_id="data_analyzer",
            description="分析价格数据",
            parameters={"method": "statistical"},
            dependencies=StepDependency(depends_on=["scrape"])
        ),
        ExecutionStep(
            step_id="report",
            order=2,
            tool_id="report_generator",
            description="生成分析报告",
            parameters={"format": "pdf"},
            dependencies=StepDependency(depends_on=["analyze"])
        )
    ],
    success_criteria=[
        "成功抓取至少3个网站",
        "分析准确率 > 90%",
        "报告生成成功"
    ],
    ethics_approved=True
)
```

---

#### ExecutionStep - 执行步骤

**文件**: `octopus/models/core_models.py:273`

```python
class ExecutionStep(BaseModel):
    """
    ExecutionStep - 计划中的单个执行步骤
    
    作用：
    - 定义单个可执行的工作单元
    - 指定依赖关系
    - 定义预期输出
    """
    
    step_id: str  # 唯一步骤ID
    order: int  # 执行顺序 (0-indexed)
    
    # 执行信息
    tool_id: str  # 使用哪个工具
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: str  # 步骤描述
    
    # 依赖
    dependencies: StepDependency = StepDependency()
    
    # 输出模式
    expected_output_type: Optional[str] = None
    output_key: Optional[str] = None  # 存储结果用的key
    
    # 错误处理
    on_failure: str = "abort"  # abort|retry|skip
    max_retries: int = 3
```

---

#### StepDependency - 步骤依赖

**文件**: `octopus/models/core_models.py:265`

```python
class StepDependency(BaseModel):
    """
    StepDependency - 定义步骤间的依赖关系
    
    作用：
    - 指定前置步骤
    - 设置执行条件
    """
    
    depends_on: List[str] = Field(default_factory=list)  # 依赖的步骤ID列表
    condition: Optional[str] = None  # 执行条件
    timeout_seconds: Optional[int] = None  # 步骤超时
```

---

### 3. 工具结果模型（Tentacle → Brain）

#### ToolResult - 工具执行结果

**文件**: `octopus/models/core_models.py:101`

```python
class ToolResult(BaseModel):
    """
    ToolResult - Tentacle 执行完成后的结果数据包
    
    作用：
    - 返回执行状态
    - 传递输出数据
    - 记录执行日志
    - 提供错误信息
    
    这是 Tentacle 的主要输出！
    """
    
    # 标识
    tool_id: str  # 哪个工具
    task_id: str  # 哪个任务
    
    # 状态
    status: TaskStatus  # 执行状态
    error: Optional[str] = None  # 错误信息
    error_code: Optional[str] = None  # 错误代码
    
    # 输出
    output: Optional[Any] = None  # 实际输出
    partial_output: Optional[Any] = None  # 流式输出
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None  # 执行时间（毫秒）
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # 重试信息
    retry_count: int = 0
    max_retries: int = 3
    
    # 日志（用于可观测性）
    logs: List[str] = Field(default_factory=list)  # 执行日志
    warnings: List[str] = Field(default_factory=list)  # 警告
```

**使用示例**:

```python
# 成功结果
result = ToolResult(
    tool_id="web_scraper",
    task_id="task_001",
    status=TaskStatus.COMPLETED,
    output={
        "h1": "Example Domain",
        "prices": ["$19.99", "$29.99", "$39.99"],
        "count": 3
    },
    execution_time_ms=1234.5,
    logs=[
        "Connecting to example.com...",
        "Fetching HTML...",
        "Parsing content...",
        "Extracted 3 prices"
    ]
)

# 失败结果
error_result = ToolResult(
    tool_id="web_scraper",
    task_id="task_002",
    status=TaskStatus.FAILED,
    error="Connection timeout after 30s",
    error_code="ERR_TIMEOUT",
    execution_time_ms=30000.0,
    logs=[
        "Connecting to example.com...",
        "Waiting for response...",
        "ERROR: Connection timeout"
    ],
    retry_count=2,
    max_retries=3
)
```

---

#### ToolMetadata - 工具元数据

**文件**: `octopus/models/core_models.py:69`

```python
class ToolMetadata(BaseModel):
    """
    ToolMetadata - 工具的元数据信息
    """
    
    tool_id: str
    tool_name: str
    category: ToolCategory
    version: str = "1.0.0"
    execution_time_ms: Optional[float] = None
```

---

#### ToolDefinition - 工具定义

**文件**: `octopus/models/core_models.py:88`

```python
class ToolDefinition(BaseModel):
    """
    ToolDefinition - 完整工具定义
    
    包含工具的所有信息：
    - 基本信息
    - 参数定义
    - 返回类型
    - 约束
    """
    
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    
    parameters: List[ToolParameter] = Field(default_factory=list)
    return_type: str = "any"
    
    constraints: List[str] = Field(default_factory=list)
    timeout_seconds: int = 60
    rate_limit: Optional[int] = None
    
    version: str = "1.0.0"
```

---

### 4. 通信包装模型

#### ExecutionRequest - 执行请求（网络传输）

**文件**: `octopus/models/core_models.py:349`

```python
class ExecutionRequest(BaseModel):
    """
    ExecutionRequest - 网络传输的请求包装器
    
    作用：
    - 包装 TaskRequest
    - 添加传输层信息
    - 包含认证令牌
    """
    
    request_id: str  # 唯一请求ID
    task: TaskRequest  # 实际任务
    
    auth_token: Optional[str] = Field(None, exclude=True)  # 不序列化
    timeout_seconds: int = 300
    
    created_at: datetime = Field(default_factory=datetime.now)
```

---

#### ExecutionResponse - 执行响应（网络传输）

**文件**: `octopus/models/core_models.py:362`

```python
class ExecutionResponse(BaseModel):
    """
    ExecutionResponse - 网络传输的响应包装器
    
    作用：
    - 包装 ToolResult
    - 包含请求ID用于关联
    - 记录接收时间
    """
    
    request_id: str  # 关联的请求ID
    task_id: str  # 关联的任务ID
    result: ToolResult  # 实际结果
    
    received_at: datetime = Field(default_factory=datetime.now)
```

---

### 5. 状态和日志模型

#### WorldState - 世界状态

**文件**: `octopus/models/core_models.py:378`

```python
class WorldState(BaseModel):
    """
    WorldState - Brain 对当前世界的理解
    
    作用：
    - 维护实体列表
    - 追踪关系
    - 管理目标和约束
    """
    
    state_id: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)
    current_goals: List[str] = Field(default_factory=list)
    active_constraints: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
```

---

#### BrainThought - 思考日志

**文件**: `octopus/models/core_models.py:388`

```python
class BrainThought(BaseModel):
    """
    BrainThought - Brain 的单个推理单元
    
    作用：
    - 记录"缓慢思考"过程
    - 追踪推理链
    - 用于可观测性和调试
    """
    
    thought_id: str
    plan_id: Optional[str] = None
    
    thought_type: str  # perception, reasoning, planning, evaluation, decision
    content: str  # 思考内容
    
    confidence: float = Field(ge=0, le=1)  # 置信度
    
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 🔧 枚举类型

### TaskPriority - 任务优先级

```python
class TaskPriority(str, Enum):
    CRITICAL = "critical"  # 必须立即执行
    HIGH = "high"         # 尽快执行
    NORMAL = "normal"     # 标准优先级
    LOW = "low"          # 可以等待
```

### TaskStatus - 任务状态

```python
class TaskStatus(str, Enum):
    PENDING = "pending"      # 队列中，未开始
    RUNNING = "running"     # 正在执行
    COMPLETED = "completed"  # 成功完成
    FAILED = "failed"       # 执行失败
    CANCELLED = "cancelled" # 已取消
    RETRYING = "retrying"   # 正在重试
```

### ToolCategory - 工具类别

```python
class ToolCategory(str, Enum):
    WEB_SCRAPING = "web_scraping"
    DATABASE = "database"
    CODE_EXECUTION = "code_execution"
    EMAIL = "email"
    API_CALL = "api_call"
    FILE_SYSTEM = "file_system"
    MESSAGE_QUEUE = "message_queue"
    CUSTOM = "custom"
```

### PlanStatus - 计划状态

```python
class PlanStatus(str, Enum):
    DRAFT = "draft"                    # 正在构建
    VALIDATED = "validated"            # 通过验证
    APPROVED = "approved"             # 已批准
    REJECTED = "rejected"             # 被拒绝
    EXECUTING = "executing"           # 正在执行
    COMPLETED = "completed"            # 成功完成
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
```

---

## 🏭 工厂函数

为了简化模型创建，提供了工厂函数：

### create_task_request

```python
def create_task_request(
    task_id: str,
    tool_id: str,
    parameters: Dict[str, Any],
    priority: TaskPriority = TaskPriority.NORMAL,
    **kwargs
) -> TaskRequest:
    """创建 TaskRequest 的快捷方式"""
```

**使用**:

```python
task = create_task_request(
    task_id="task_001",
    tool_id="web_scraper",
    parameters={"url": "https://example.com"},
    priority=TaskPriority.HIGH
)
```

---

### create_plan

```python
def create_plan(
    plan_id: str,
    objective: str,
    steps: List[ExecutionStep],
    reasoning: str,
    **kwargs
) -> Plan:
    """创建 Plan 的快捷方式"""
```

**使用**:

```python
plan = create_plan(
    plan_id="plan_001",
    objective="分析数据",
    reasoning="需要先抓取再分析",
    steps=[step1, step2]
)
```

---

### create_tool_result

```python
def create_tool_result(
    tool_id: str,
    task_id: str,
    status: TaskStatus,
    output: Any = None,
    **kwargs
) -> ToolResult:
    """创建 ToolResult 的快捷方式"""
```

**使用**:

```python
result = create_tool_result(
    tool_id="web_scraper",
    task_id="task_001",
    status=TaskStatus.COMPLETED,
    output={"data": "success"}
)
```

---

## 💡 最佳实践

### 1. 始终使用类型注解

```python
# ✅ 正确
def process_task(task: TaskRequest) -> ToolResult:
    ...

# ❌ 错误
def process_task(task):
    ...
```

### 2. 使用工厂函数

```python
# ✅ 正确 - 使用工厂函数
task = create_task_request(...)

# ❌ 错误 - 手动创建所有字段
task = TaskRequest(
    task_id="...",
    tool_id="...",
    ...
)
```

### 3. 记录日志

```python
# ✅ 正确 - 添加执行日志
result = create_tool_result(...)
result.logs.append("Step 1: Connecting...")
result.logs.append("Step 2: Processing...")
result.logs.append("Complete!")
```

### 4. 错误处理

```python
# ✅ 正确 - 提供详细错误信息
result = create_tool_result(
    tool_id="web_scraper",
    task_id="task_001",
    status=TaskStatus.FAILED,
    error="Connection timeout",
    error_code="ERR_TIMEOUT",
    logs=["Trying to connect...", "ERROR: Timeout"]
)
```

---

## 📊 模型关系图

```
ExecutionRequest (网络包装)
    ↓
TaskRequest (任务定义)
    ↓
ToolDefinition (工具定义)
    ↓
ToolResult (执行结果)
    ↑
Plan (执行计划)
    ↓
ExecutionStep[] (步骤列表)
    ↓
TaskRequest[] (每个步骤的任务)
    ↓
ToolResult[] (每个步骤的结果)
    ↓
Plan.step_results[] (收集结果)
```

---

## 🔍 验证示例

### Pydantic 自动验证

```python
from pydantic import ValidationError

try:
    task = TaskRequest(
        task_id="task_001",
        tool_id="web_scraper",
        parameters={"url": "invalid_url"},  # 自动验证 URL 格式
        priority="invalid_priority"  # 自动验证枚举值
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

---

## 🚀 序列化

### JSON 序列化

```python
# 转换为 JSON
json_str = plan.model_dump_json(indent=2)
print(json_str)

# 从 JSON 恢复
plan = Plan.model_validate_json(json_str)
```

### 字典序列化

```python
# 转换为字典
plan_dict = plan.model_dump()
print(plan_dict)

# 从字典恢复
plan = Plan.model_validate(plan_dict)
```

---

这个文档提供了 Octopus 项目中所有 Pydantic 模型的完整参考！🎓
