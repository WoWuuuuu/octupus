# Octopus 组件规格说明

## 1. 决策层组件 (Decision Layer)

### 1.1 World Model (世界模型)

**位置**: `octopus/core/world_model.py`

**功能**: 
- 表示和管理系统对世界的理解状态
- 维护实体、关系、全局状态
- 支持状态快照和恢复

**核心类**:
- `WorldModel`: 主类，管理所有实体和状态
- `Entity`: 实体表示，包含属性和关系
- `StateSnapshot`: 状态快照，用于恢复
- `StateConfidence`: 状态置信度枚举

**状态置信度**:
| 置信度 | 值 | 说明 |
|--------|-----|------|
| CERTAIN | 1.0 | 确定 |
| HIGH | 0.9 | 高 |
| MEDIUM | 0.7 | 中等 |
| LOW | 0.5 | 低 |
| UNCERTAIN | 0.3 | 不确定 |

**主要方法**:
```python
class WorldModel:
    def add_entity(entity: Entity) -> None
    def update_entity(entity_id: str, properties: Dict) -> bool
    def get_entity(entity_id: str) -> Optional[Entity]
    def remove_entity(entity_id: str) -> bool
    def query_entities(entity_type: str, filters: Dict) -> List[Entity]
    def set_global_state(key: str, value: Any) -> None
    def get_global_state(key: str, default: Any) -> Any
    def add_goal(goal_id: str) -> None
    def remove_goal(goal_id: str) -> None
    def add_constraint(constraint: str) -> None
    def check_constraint(constraint: str) -> bool
    def create_snapshot() -> StateSnapshot
    def restore_snapshot(snapshot_id: str) -> bool
    def get_state_summary() -> Dict[str, Any]
    def export_state() -> str
    def import_state(state_json: str) -> bool
```

**数据格式**:
```python
# Entity 数据结构
entity = Entity(
    entity_id="user_1",
    entity_type="user",
    properties={"name": "Alice", "role": "developer", "active": True},
    relationships={"works_on": ["project_1"]},
    confidence=0.9,
    metadata={"created_at": "2026-01-01"}
)

# StateSnapshot 数据结构
snapshot = StateSnapshot(
    snapshot_id="snapshot_123",
    timestamp=datetime.now(),
    entities={...},
    global_state={...},
    active_goals=["project_1"],
    pending_decisions=["dec_456"],
    constraints=["must_have_approval"]
)
```

**使用示例**:
```python
world = WorldModel()

entity = Entity(
    entity_id="user_1",
    entity_type="user",
    properties={"name": "Alice", "role": "developer"}
)
world.add_entity(entity)

world.add_goal("deploy_application")
world.add_constraint("must have approval")

snapshot = world.create_snapshot()

# 查询实体
users = world.query_entities(entity_type="user", properties_filter={"active": True})
```

---

### 1.2 Perception Module (感知模块)

**位置**: `octopus/core/perception.py`

**功能**:
- 处理原始输入信号
- 意图识别和分类
- 实体提取（邮箱、URL、路径等）
- 上下文构建
- 置信度计算

**核心类**:
- `PerceptionModule`: 主类，处理感知
- `Intent`: 意图数据结构
- `PerceptionResult`: 感知结果
- `IntentParser`: 意图解析器
- `IntentType`: 意图类型枚举
- `SignalSource`: 信号来源枚举

**意图类型**:
| 类型 | 说明 |
|------|------|
| USER_REQUEST | 用户请求 |
| SYSTEM_EVENT | 系统事件 |
| EXTERNAL_SIGNAL | 外部信号 |
| SCHEDULED_TASK | 定时任务 |
| MONITORING_ALERT | 监控告警 |
| QUERY | 查询 |
| COMMAND | 命令 |
| QUERY_RESPONSE | 查询响应 |
| ERROR_OBSERVATION | 错误观察 |
| UNKNOWN | 未知 |

**信号来源**:
| 来源 | 说明 |
|------|------|
| USER | 用户 |
| API | API接口 |
| WEBHOOK | Webhook |
| SCHEDULER | 调度器 |
| MONITOR | 监控 |
| AGENT | 代理 |
| EXTERNAL | 外部 |
| INTERNAL | 内部 |

**主要方法**:
```python
class PerceptionModule:
    def perceive(raw_input: Any) -> PerceptionResult
    def register_sensor(name: str, sensor: Callable) -> None
    def register_context_provider(provider: Callable) -> None
    def get_perception_summary() -> Dict[str, Any]
```

**数据格式**:
```python
# Intent 数据结构
intent = Intent(
    intent_id="intent_123",
    intent_type=IntentType.COMMAND,
    raw_content="Execute script with param=value",
    parsed_content={"action": "execute", "target": "script"},
    entities=["/path/to/script.py"],
    confidence=0.85,
    source=SignalSource.USER,
    priority=2
)

# PerceptionResult 数据结构
result = PerceptionResult(
    intents=[intent],
    extracted_entities={"intent_123": {"entities": [...], "type": "command"}},
    contextual_info={"timestamp": "now"},
    confidence=0.85,
    processing_time_ms=15.2
)
```

**使用示例**:
```python
perception = PerceptionModule()

# 感知文本输入
result = perception.perceive("Please calculate the total revenue for Q1")

if result.intents:
    intent = result.intents[0]
    print(f"Type: {intent.intent_type.value}")
    print(f"Confidence: {intent.confidence}")
    print(f"Entities: {intent.entities}")

# 感知结构化输入
structured_input = {
    "content": "Fetch customer data",
    "context": {"source": "api", "user_id": "user_1"}
}
result = perception.perceive(structured_input)
```

---

### 1.3 Simulation Engine (模拟引擎)

**位置**: `octopus/core/simulation.py`

**功能**:
- 在虚拟环境中探索可能的未来场景
- 多路径探索和分支
- 风险评估
- 成功率计算
- 蒙特卡洛模拟（可选）

**核心类**:
- `SimulationEngine`: 主类，管理模拟
- `Scenario`: 场景定义
- `SimulationResult`: 模拟结果
- `SimulationConfig`: 模拟配置
- `SimulationState`: 模拟状态枚举
- `ActionSimulator`: 动作模拟器

**模拟状态**:
| 状态 | 说明 |
|------|------|
| PENDING | 待处理 |
| RUNNING | 运行中 |
| COMPLETED | 完成 |
| TERMINATED | 终止 |
| FAILED | 失败 |

**主要方法**:
```python
class SimulationEngine:
    def simulate_scenario(scenario: Scenario) -> SimulationResult
    def simulate_action_sequence(initial_state: Dict, actions: List) -> SimulationResult
    def generate_scenario_variants(base_scenario: Scenario, count: int) -> List[Scenario]
    def compare_scenarios(scenarios: List) -> List[SimulationResult]
    def set_world_model_accessor(accessor: Callable) -> None
    def get_simulation_summary() -> Dict[str, Any]
```

**配置参数**:
```python
config = SimulationConfig(
    max_depth=5,              # 最大模拟深度
    max_branches=3,           # 最大分支数
    simulation_time_horizon=100,  # 模拟时间范围
    uncertainty_level=0.1,    # 不确定性级别 (0-1)
    risk_weight=0.4,          # 风险权重
    reward_weight=0.6,        # 奖励权重
    enable_monte_carlo=False,  # 启用蒙特卡洛模拟
    monte_carlo_iterations=100,  # 蒙特卡洛迭代次数
    early_stopping_threshold=0.9  # 早停阈值
)
```

**数据格式**:
```python
# Scenario 数据结构
scenario = Scenario(
    scenario_id="scenario_123",
    name="Data Processing",
    initial_state={"resources": 100, "time": 10},
    actions_sequence=[
        {"type": "allocate", "parameters": {"amount": 20}},
        {"type": "execute", "parameters": {"task": "analysis"}}
    ],
    predicted_outcomes={},
    probability=0.8,
    risk_score=0.3,
    reward_score=0.7
)

# SimulationResult 数据结构
result = SimulationResult(
    scenario_id="scenario_123",
    status=SimulationState.COMPLETED,
    final_state={"resources": 80, "time": 8, "predicted_success": True},
    intermediate_states=[...],
    outcome_probability=0.85,
    risk_assessment={"execution_risk": 0.2, "state_risk": 0.1, "total_risk": 0.15},
    success_metrics={"goal_achievement": 0.9, "efficiency": 0.85, "overall_score": 0.88},
    execution_time_ms=123.4
)
```

**使用示例**:
```python
config = SimulationConfig(max_depth=5, uncertainty_level=0.1)
engine = SimulationEngine(config)

initial_state = {"resources": 100, "time": 10}
actions = [
    {"type": "allocate", "parameters": {"amount": 20}},
    {"type": "execute", "parameters": {"task": "analysis"}},
]

result = engine.simulate_action_sequence(initial_state, actions)
print(f"Success Score: {result.success_metrics['overall_score']:.2f}")
print(f"Risk Level: {result.risk_assessment['total_risk']:.2f}")

# 生成场景变体
variants = engine.generate_scenario_variants(scenario, count=3)
```

---

### 1.4 Decision Engine (决策引擎)

**位置**: `octopus/core/decision_engine.py`

**功能**:
- 评估和比较决策选项
- 多标准决策分析
- 执行意图生成
- 决策策略管理
- 决策历史追踪

**核心类**:
- `DecisionEngine`: 主类，管理决策
- `Decision`: 决策数据结构
- `DecisionOption`: 决策选项
- `DecisionPolicy`: 决策策略
- `DecisionCriteria`: 决策标准
- `DecisionStatus`: 决策状态枚举
- `DecisionPriority`: 决策优先级枚举

**决策状态**:
| 状态 | 说明 |
|------|------|
| PENDING | 待处理 |
| EVALUATING | 评估中 |
| DECIDED | 已决策 |
| EXECUTING | 执行中 |
| COMPLETED | 完成 |
| FAILED | 失败 |
| CANCELLED | 取消 |

**决策优先级**:
| 优先级 | 值 | 说明 |
|--------|-----|------|
| CRITICAL | 1 | 关键 |
| HIGH | 2 | 高 |
| NORMAL | 3 | 正常 |
| LOW | 4 | 低 |

**主要方法**:
```python
class DecisionEngine:
    def make_decision(context: Dict, options: List[Dict]) -> Decision
    def add_policy(policy: DecisionPolicy) -> None
    def set_active_policy(policy_id: str) -> bool
    def register_decision_callback(callback: Callable) -> None
    def get_decision(decision_id: str) -> Optional[Decision]
    def get_decision_summary() -> Dict[str, Any]
```

**数据格式**:
```python
# DecisionCriteria 数据结构
criteria = DecisionCriteria(
    name="outcome_value",
    weight=0.4,
    description="Value of the expected outcome"
)

# DecisionOption 数据结构
option = DecisionOption(
    option_id="opt_123",
    name="Quick Analysis",
    description="Fast but basic analysis",
    action_sequence=[
        {"tool_id": "calculator", "parameters": {"a": 10, "b": 20}}
    ],
    criteria_scores={"outcome_value": 0.7, "risk_reduction": 0.5},
    total_score=0.65,
    risk_level=0.3,
    reversibility=0.8,
    confidence=0.9,
    constraints_satisfied=True,
    estimated_cost=100,
    estimated_benefit=500
)

# Decision 数据结构
decision = Decision(
    decision_id="dec_123",
    context={"task": "analysis", "priority": "high"},
    options=[option1, option2],
    selected_option=option1,
    status=DecisionStatus.DECIDED,
    priority=DecisionPriority.HIGH,
    criteria=[criteria],
    reasoning="Selected option with highest expected value",
    confidence=0.85,
    execution_intent={...}
)
```

**使用示例**:
```python
decision = DecisionEngine()

# 创建决策策略
policy = DecisionPolicy(
    policy_id="sales_policy",
    name="Sales Decision Policy",
    description="Standard criteria for sales decisions",
    criteria=[
        DecisionCriteria("outcome_value", 0.40, "Revenue impact"),
        DecisionCriteria("risk_reduction", 0.30, "Risk mitigation"),
        DecisionCriteria("reversibility", 0.20, "Undo capability"),
        DecisionCriteria("confidence_alignment", 0.10, "Certainty level"),
    ],
    hard_constraints=["no_high_risk_actions"]
)
decision.add_policy(policy)

# 准备决策选项
options = [
    {
        "name": "Quick Sale",
        "description": "Fast transaction",
        "actions": [{"tool_id": "payment", "parameters": {...}}],
        "scores": {"outcome_value": 0.8, "risk_reduction": 0.5, ...},
        "risk_level": 0.3
    },
    {
        "name": "Premium Sale",
        "description": "Higher margin deal",
        "actions": [{"tool_id": "negotiation", "parameters": {...}}],
        "scores": {"outcome_value": 0.9, "risk_reduction": 0.7, ...},
        "risk_level": 0.5
    }
]

# 做出决策
result = decision.make_decision({"customer": "enterprise"}, options)
print(f"Selected: {result.selected_option.name}")
print(f"Reasoning: {result.reasoning}")
print(f"Confidence: {result.confidence}")
```

---

### 1.5 Long-Term Memory (长期记忆)

**位置**: `octopus/core/memory.py`

**功能**:
- 持久化存储经验和结果
- 多种记忆类型支持
- 语义搜索和检索
- 经验学习和遗忘机制
- 记忆索引管理

**核心类**:
- `LongTermMemory`: 主类，管理记忆
- `MemoryItem`: 记忆项
- `DecisionOutcome`: 决策结果
- `MemoryIndex`: 记忆索引
- `MemoryType`: 记忆类型枚举
- `MemoryRelevance`: 记忆相关性枚举

**记忆类型**:
| 类型 | 说明 |
|------|------|
| EPISODIC | 事件记忆（具体事件） |
| SEMANTIC | 语义记忆（知识/模式） |
| PROCEDURAL | 过程记忆（操作流程） |
| WORKING | 工作记忆（临时存储） |

**记忆相关性**:
| 相关性 | 值 | 说明 |
|--------|-----|------|
| CRITICAL | 1.0 | 关键 |
| HIGH | 0.8 | 高 |
| MEDIUM | 0.5 | 中等 |
| LOW | 0.3 | 低 |
| IRRELEVANT | 0.0 | 无关 |

**主要方法**:
```python
class LongTermMemory:
    def __init__(self, max_items=10000, default_ttl=None, enable_auto_cleanup=True)
    def set_embedder(embedder: Callable) -> None
    def store(content: Dict, memory_type: MemoryType, ...) -> MemoryItem
    def retrieve(memory_id: str, increment_access=True) -> Optional[MemoryItem]
    def search(memory_type: Optional, tags: Optional, context: Optional, query: Optional, limit=10) -> List[MemoryItem]
    def store_outcome(outcome: DecisionOutcome) -> None
    def get_recent_outcomes(limit: int) -> List[DecisionOutcome]
    def cleanup_expired() -> int
    def get_statistics() -> Dict[str, Any]
```

**数据格式**:
```python
# MemoryItem 数据结构
memory = MemoryItem(
    memory_id="mem_123",
    memory_type=MemoryType.EPISODIC,
    content={"event": "successful_deployment", "metrics": {"duration": 120}},
    context={"project": "app_v2"},
    relevance=MemoryRelevance.HIGH,
    access_count=5,
    last_accessed=datetime.now(),
    expiration=datetime.now() + timedelta(days=30),
    tags=["deployment", "success", "production"]
)

# DecisionOutcome 数据结构
outcome = DecisionOutcome(
    decision_id="dec_123",
    selected_option_id="opt_456",
    execution_result={"status": "success", "output": {...}},
    actual_outcome={"deployed": True, "errors": []},
    expected_vs_actual={"accuracy": 0.95},
    lessons_learned=["Always verify dependencies"],
    success=True
)
```

**使用示例**:
```python
memory = LongTermMemory(max_items=10000, default_ttl=90)

# 存储记忆
memory.store(
    content={"event": "successful_deployment", "metrics": {...}},
    memory_type=MemoryType.EPISODIC,
    tags=["deployment", "success"],
    relevance=0.9,
    ttl_days=30
)

# 存储语义记忆
memory.store(
    content={"pattern": "recurring_issue", "frequency": "weekly"},
    memory_type=MemoryType.SEMANTIC,
    tags=["issue", "reports"]
)

# 搜索记忆
results = memory.search(tags=["deployment"], limit=5)

# 存储决策结果
outcome = DecisionOutcome(
    decision_id="dec_123",
    selected_option_id="opt_456",
    execution_result={"status": "success"},
    actual_outcome={"deployed": True},
    success=True
)
memory.store_outcome(outcome)

# 获取统计信息
stats = memory.get_statistics()
print(f"Total memories: {stats['total_memories']}")
print(f"Memory types: {stats['memory_types']}")
```

---

### 1.6 Ethics Framework (伦理框架)

**位置**: `octopus/core/ethics.py`

**功能**:
- 价值体系和伦理规则管理
- 决策伦理审查
- 约束检查和违规检测
- 审计日志记录

**核心类**:
- `EthicsFramework`: 主类，管理伦理
- `EthicalGuideline`: 伦理指南
- `EthicalRule`: 伦理规则
- `ValueSystem`: 价值系统
- `EthicsCheckResult`: 检查结果
- `EthicalPrinciple`: 伦理原则枚举
- `EthicsDecision`: 伦理决策枚举

**伦理原则**:
| 原则 | 说明 | 默认权重 |
|------|------|----------|
| NON_MALEFICENCE | 不伤害 | 1.0 |
| BENEFICENCE | 行善 | 0.8 |
| AUTONOMY | 自主 | 0.7 |
| JUSTICE | 公正 | 0.7 |
| FAIRNESS | 公平 | 0.7 |
| TRANSPARENCY | 透明 | 0.6 |
| ACCOUNTABILITY | 问责 | 0.6 |
| PRIVACY | 隐私 | 0.8 |
| SECURITY | 安全 | 0.9 |
| SUSTAINABILITY | 可持续 | 0.5 |

**伦理决策**:
| 决策 | 说明 |
|------|------|
| APPROVED | 批准 |
| APPROVED_WITH_CONDITIONS | 有条件批准 |
| REQUIRES_REVIEW | 需要复审 |
| REJECTED | 拒绝 |
| BLOCKED | 阻止 |

**主要方法**:
```python
class EthicsFramework:
    def check_ethics(action: Dict, context: Optional[Dict]) -> EthicsCheckResult
    def add_guideline(guideline: EthicalGuideline) -> None
    def set_active_guideline(guideline_id: str) -> bool
    def register_rule_evaluator(rule_id: str, evaluator: Callable) -> None
    def create_default_guideline() -> EthicalGuideline
    def get_audit_log(limit: Optional[int]) -> List[Dict[str, Any]]
    def get_framework_summary() -> Dict[str, Any]
```

**数据格式**:
```python
# EthicalRule 数据结构
rule = EthicalRule(
    rule_id="privacy_protection",
    principle=EthicalPrinciple.PRIVACY,
    description="Protect user privacy and personal data",
    condition="action involves user data",
    action="condition",
    severity=2,
    exceptions=["anonymized_data"]
)

# EthicsCheckResult 数据结构
result = EthicsCheckResult(
    decision=EthicsDecision.APPROVED,
    applicable_rules=[rule1, rule2],
    violated_rules=[],
    approved_rules=[rule1, rule2],
    conditions=["requires_user_consent"],
    review_required=False,
    ethical_score=0.95,
    details={"message": "All checks passed"}
)
```

**使用示例**:
```python
ethics = EthicsFramework()

# 创建默认伦理指南
guideline = ethics.create_default_guideline()
ethics.add_guideline(guideline)

# 注册自定义规则评估器
def privacy_check(action, context):
    return context.get("user_consent", False) or action.get("data_type") == "public"

ethics.register_rule_evaluator("privacy_rule", privacy_check)

# 检查伦理
action = {
    "type": "data_access",
    "target": "customer_records",
    "purpose": "analysis",
    "data_type": "anonymized"
}

result = ethics.check_ethics(action, {"user_consent": True})

if result.decision == EthicsDecision.APPROVED:
    print("Action approved")
elif result.decision == EthicsDecision.REQUIRES_REVIEW:
    print(f"Review required: {result.review_reason}")

# 查看审计日志
logs = ethics.get_audit_log(limit=10)
```

---

## 2. 执行层组件 (Execution Layer)

### 2.1 Tool Registry (工具注册表)

**位置**: `octopus/execution/tools.py`

**功能**:
- 工具注册和管理
- 工具搜索和过滤
- 工具元数据管理
- 分类和标签索引

**核心类**:
- `ToolRegistry`: 主类，管理工具
- `Tool`: 工具封装
- `ToolMetadata`: 工具元数据
- `ToolParameter`: 工具参数
- `ToolExecution`: 工具执行记录
- `ToolCategory`: 工具类别枚举
- `ToolStatus`: 工具状态枚举

**工具类别**:
| 类别 | 说明 |
|------|------|
| CODE_EXECUTION | 代码执行 |
| DATA_RETRIEVAL | 数据检索 |
| FILE_OPERATIONS | 文件操作 |
| NETWORK | 网络操作 |
| SYSTEM | 系统操作 |
| EXTERNAL_INTEGRATION | 外部集成 |
| UTILITY | 实用工具 |

**工具状态**:
| 状态 | 说明 |
|------|------|
| AVAILABLE | 可用 |
| DEGRADED | 降级 |
| UNAVAILABLE | 不可用 |
| MAINTENANCE | 维护中 |

**主要方法**:
```python
class ToolRegistry:
    def register_tool(tool: Tool) -> bool
    def unregister_tool(tool_id: str) -> bool
    def get_tool(tool_id: str) -> Optional[Tool]
    def search_tools(category: Optional, tags: Optional, query: Optional) -> List[Tool]
    def get_tools_by_category(category: ToolCategory) -> List[Tool]
    def get_tools_by_tags(tags: List[str]) -> List[Tool]
    def get_tool_metadata(tool_id: str) -> Optional[Dict[str, Any]]
    def get_all_metadata() -> List[Dict[str, Any]]
    def get_registry_summary() -> Dict[str, Any]
```

**数据格式**:
```python
# ToolParameter 数据结构
param = ToolParameter(
    name="query",
    param_type="string",
    description="Data retrieval query",
    required=True,
    default="*",
    options=["users", "orders", "products"]
)

# ToolMetadata 数据结构
metadata = ToolMetadata(
    tool_id="data_retriever",
    name="Data Retriever",
    description="Retrieve data from configured sources",
    category=ToolCategory.DATA_RETRIEVAL,
    version="1.0.0",
    parameters=[param],
    return_type="dict",
    examples=[{"input": {"query": "users"}, "output": {...}}],
    constraints=["rate_limit: 100/min"],
    timeout_seconds=30
)

# ToolExecution 数据结构
execution = ToolExecution(
    execution_id="exec_123",
    tool_id="data_retriever",
    parameters={"query": "users"},
    started_at=datetime.now(),
    completed_at=datetime.now(),
    status="success",
    result={"count": 42},
    execution_time_ms=156.7
)
```

**使用示例**:
```python
registry = ToolRegistry()

# 创建工具元数据
metadata = ToolMetadata(
    tool_id="data_processor",
    name="Data Processor",
    description="Process and analyze data",
    category=ToolCategory.DATA_RETRIEVAL,
    parameters=[
        ToolParameter("data", "array", "Input data", required=True),
        ToolParameter("operation", "string", "Operation type", options=["sum", "avg", "max"])
    ],
    timeout_seconds=60
)

# 创建工具并注册执行器
tool = Tool(metadata)
tool.register_executor(lambda params: sum(params["data"]) if params.get("operation") == "sum" else 0)

# 注册工具
registry.register_tool(tool)

# 搜索工具
tools = registry.search_tools(category=ToolCategory.DATA_RETRIEVAL, tags=["analysis"])
```

---

### 2.2 Execution Layer (执行层)

**位置**: `octopus/execution/executor.py`

**功能**:
- 接收并执行决策层的执行意图
- 任务队列管理
- 执行计划编排
- 错误处理和重试
- 执行历史追踪

**核心类**:
- `ExecutionLayer`: 主类，管理执行
- `ExecutionPlan`: 执行计划
- `ExecutionTask`: 执行任务
- `ExecutionState`: 执行状态枚举

**执行状态**:
| 状态 | 说明 |
|------|------|
| IDLE | 空闲 |
| EXECUTING | 执行中 |
| PAUSED | 暂停 |
| STOPPED | 停止 |
| ERROR | 错误 |

**主要方法**:
```python
class ExecutionLayer:
    def __init__(self, protocol: Optional[ODEPProtocol] = None)
    def register_tool(tool: Tool) -> bool
    def unregister_tool(tool_id: str) -> bool
    def register_error_handler(error_type: str, handler: Callable) -> None
    def register_pre_execution_hook(hook: Callable) -> None
    def register_post_execution_hook(hook: Callable) -> None
    def execute_intent(intent: ExecutionIntent) -> ExecutionResult
    def execute_single(tool_id: str, parameters: Dict) -> Any
    def execute_batch(executions: List[Dict]) -> List[Any]
    def cancel_execution(plan_id: str) -> bool
    def get_plan_status(plan_id: str) -> Optional[Dict[str, Any]]
    def get_active_executions() -> List[Dict[str, Any]]
    def get_execution_summary() -> Dict[str, Any]
    def get_tool_registry() -> ToolRegistry
```

**数据格式**:
```python
# ExecutionTask 数据结构
task = ExecutionTask(
    task_id="task_123",
    intent_id="intent_456",
    tool_id="calculator",
    parameters={"a": 10, "b": 5},
    priority=3,
    state=ExecutionState.EXECUTING,
    started_at=datetime.now(),
    max_retries=3
)

# ExecutionPlan 数据结构
plan = ExecutionPlan(
    plan_id="plan_123",
    intent_id="intent_456",
    tasks=[task1, task2],
    current_task_index=0,
    status="running",
    results=[],
    metadata={"created_by": "decision_engine"}
)
```

**使用示例**:
```python
execution = ExecutionLayer()
execution.register_tool(my_tool)

# 创建执行意图
intent = ExecutionIntent(
    intent_id="exec_123",
    action_type="process_data",
    parameters={
        "action_sequence": [
            {"tool_id": "data_processor", "parameters": {"data": [1, 2, 3]}},
            {"tool_id": "calculator", "parameters": {"a": 10, "b": 20}}
        ]
    },
    priority=Priority.NORMAL,
    timeout_seconds=300
)

# 执行意图
result = execution.execute_intent(intent)
print(f"Status: {result.status.value}")
print(f"Output: {result.output}")

# 执行单个工具
result = execution.execute_single("calculator", {"a": 100, "b": 50})
print(f"Result: {result}")

# 批量执行
results = execution.execute_batch([
    {"tool_id": "calculator", "parameters": {"a": 1, "b": 2}},
    {"tool_id": "data_processor", "parameters": {"data": [10, 20, 30]}}
])
```

---

## 3. 通信协议 (Protocol)

### 3.1 ODEP Protocol (Octopus Decision Execution Protocol)

**位置**: `octopus/protocol/communication.py`

**功能**:
- 决策层和执行层之间的通信
- 消息队列管理
- 请求-响应关联
- 状态更新传播

**核心类**:
- `ODEPProtocol`: 主类，管理协议
- `ODEPMessage`: 消息结构
- `ExecutionIntent`: 执行意图
- `ExecutionResult`: 执行结果
- `WorldStateUpdate`: 世界状态更新
- `MessageType`: 消息类型枚举
- `ExecutionStatus`: 执行状态枚举
- `Priority`: 优先级枚举

**消息类型**:
| 类型 | 说明 |
|------|------|
| EXECUTE_REQUEST | 执行请求 |
| EXECUTE_RESPONSE | 执行响应 |
| STATE_UPDATE | 状态更新 |
| DECISION_REQUEST | 决策请求 |
| DECISION_RESPONSE | 决策响应 |
| OBSERVATION | 观察结果 |
| ERROR | 错误信息 |
| HEARTBEAT | 心跳 |

**执行状态**:
| 状态 | 说明 |
|------|------|
| PENDING | 待处理 |
| RUNNING | 运行中 |
| SUCCESS | 成功 |
| FAILED | 失败 |
| CANCELLED | 取消 |
| TIMEOUT | 超时 |

**优先级**:
| 优先级 | 值 | 说明 |
|--------|-----|------|
| CRITICAL | 1 | 关键 |
| HIGH | 2 | 高 |
| NORMAL | 3 | 正常 |
| LOW | 4 | 低 |

**主要方法**:
```python
class ODEPProtocol:
    def send_execute_request(sender: str, recipient: str, intent: ExecutionIntent) -> ODEPMessage
    def send_execute_response(sender: str, recipient: str, result: ExecutionResult, correlation_id: str) -> ODEPMessage
    def send_state_update(sender: str, recipient: str, update: WorldStateUpdate) -> ODEPMessage
    def subscribe(component: str, callback: Callable) -> None
    def publish(component: str, message: ODEPMessage) -> None
    def get_pending_request(intent_id: str) -> Optional[ODEPMessage]
    def get_messages_by_type(message_type: MessageType) -> List[ODEPMessage]
    def clear_processed_messages(before_timestamp: datetime) -> None
```

**数据格式**:
```python
# ExecutionIntent 数据结构
intent = ExecutionIntent(
    intent_id="intent_123",
    action_type="data_analysis",
    parameters={"query": "SELECT * FROM sales"},
    priority=Priority.NORMAL,
    timeout_seconds=300,
    constraints=["no_pii_access"],
    rollback_plan={"action": "rollback_transaction"},
    metadata={"origin": "decision_engine"}
)

# ExecutionResult 数据结构
result = ExecutionResult(
    intent_id="intent_123",
    status=ExecutionStatus.SUCCESS,
    output={"rows": 1000, "columns": 5},
    execution_time_ms=1234.5,
    partial_results=[...],
    metadata={"plan_id": "plan_456"}
)

# ODEPMessage 数据结构
message = ODEPMessage(
    message_id="msg_123",
    message_type=MessageType.EXECUTE_REQUEST,
    sender="decision_layer",
    recipient="execution_layer",
    payload={"execution_intent": intent.to_dict()},
    correlation_id="intent_123",
    timestamp=datetime.now(),
    ttl_seconds=60
)
```

**使用示例**:
```python
protocol = ODEPProtocol()

# 创建执行意图
intent = ExecutionIntent(
    intent_id="intent_1",
    action_type="analysis",
    parameters={"data": [1, 2, 3]},
    priority=Priority.HIGH
)

# 发送执行请求
message = protocol.send_execute_request("decision", "execution", intent)

# 处理执行结果
response = ExecutionResult(
    intent_id="intent_1",
    status=ExecutionStatus.SUCCESS,
    output={"result": 6}
)
protocol.send_execute_response("execution", "decision", response, "intent_1")

# 发送状态更新
update = WorldStateUpdate(
    state_type="entity_update",
    changes={"user_1": {"active": True}},
    source="execution_layer",
    confidence=1.0
)
protocol.send_state_update("execution", "decision", update)
```

---

## 4. 接口定义总结

### 4.1 决策层接口

```python
class IDecisionLayer(Protocol):
    def perceive(input: Any) -> PerceptionResult
    def make_decision(context: Dict, options: List[Dict]) -> Decision
    def check_ethics(action: Dict) -> EthicsCheckResult
    def get_world_model() -> WorldModel
```

### 4.2 执行层接口

```python
class IExecutionLayer(Protocol):
    def execute_intent(intent: ExecutionIntent) -> ExecutionResult
    def execute_single(tool_id: str, params: Dict) -> Any
    def register_tool(tool: Tool) -> bool
    def get_tool_registry() -> ToolRegistry
```

### 4.3 协议接口

```python
class IODEPProtocol(Protocol):
    def send_execute_request(intent: ExecutionIntent) -> ODEPMessage
    def send_execute_response(result: ExecutionResult) -> ODEPMessage
    def subscribe(component: str, callback: Callable) -> None
    def publish(component: str, message: ODEPMessage) -> None
```

---

## 5. 错误处理

### 5.1 常见错误类型

| 错误类型 | 说明 | 处理策略 |
|----------|------|----------|
| 感知错误 | 输入解析失败 | 返回置信度为0的结果 |
| 模拟错误 | 场景模拟异常 | 回退到默认值 |
| 决策错误 | 无法做出决策 | 返回空决策，记录日志 |
| 伦理错误 | 伦理检查未通过 | 拒绝执行，记录审计日志 |
| 执行错误 | 工具执行失败 | 重试机制（最多3次） |
| 通信错误 | 协议通信失败 | 消息重传，队列存储 |

### 5.2 错误处理策略

```python
try:
    result = execution.execute_intent(intent)
except ExecutionError as e:
    if e.retryable:
        execution.retry(intent, max_attempts=3)
    else:
        log_error(e)
        notify_decision_layer(e)
        # 可选：回滚操作
        if intent.rollback_plan:
            execute_rollback(intent.rollback_plan)
```

---

## 6. 性能优化

### 6.1 建议

1. **模拟引擎**: 使用异步执行和结果缓存
2. **记忆系统**: 实现 LRU 缓存和自动清理
3. **执行层**: 并行任务执行和超时控制
4. **协议**: 消息队列和批量处理

### 6.2 监控指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 感知延迟 | 输入到意图识别时间 | < 50ms |
| 模拟执行时间 | 场景模拟耗时 | < 500ms |
| 决策置信度 | 决策确定程度 | > 0.7 |
| 执行成功率 | 工具执行成功比例 | > 95% |
| 工具响应时间 | 单个工具执行耗时 | < 1000ms |
| 协议消息延迟 | 消息传递耗时 | < 10ms |

---

## 7. 最佳实践

1. **分离关注点**: 决策层不直接执行工具
2. **状态管理**: 使用 World Model 维护一致的世界状态
3. **错误恢复**: 实现重试和回滚机制
4. **审计追踪**: 记录所有决策和执行结果
5. **性能监控**: 追踪关键路径的执行时间
6. **安全检查**: 所有决策经过伦理框架审查
7. **配置管理**: 使用策略模式管理决策标准
8. **扩展性设计**: 预留插件接口支持自定义工具和规则

---

## 8. 扩展指南

### 8.1 添加新工具

```python
# 1. 创建元数据
metadata = ToolMetadata(
    tool_id="my_custom_tool",
    name="My Custom Tool",
    description="Description of what the tool does",
    category=ToolCategory.UTILITY,
    parameters=[
        ToolParameter("input", "string", "Input data", required=True)
    ],
    timeout_seconds=60
)

# 2. 创建工具并注册执行器
tool = Tool(metadata)
tool.register_executor(lambda params: process_input(params["input"]))

# 3. 注册到执行层
execution.register_tool(tool)
```

### 8.2 添加伦理规则

```python
# 1. 创建规则评估器
def custom_ethics_check(action, context):
    # 自定义伦理检查逻辑
    if action.get("type") == "sensitive_operation":
        return context.get("approved", False)
    return True

# 2. 注册规则
ethics.register_rule_evaluator("custom_rule", custom_ethics_check)
```

### 8.3 自定义决策策略

```python
# 创建自定义策略
policy = DecisionPolicy(
    policy_id="custom_policy",
    name="Custom Policy",
    description="Custom decision criteria",
    criteria=[
        DecisionCriteria("custom_metric", 1.0, "Custom evaluation metric")
    ],
    hard_constraints=["no_dangerous_actions"]
)

# 添加并激活策略
decision.add_policy(policy)
decision.set_active_policy("custom_policy")
```

---

**版本**: Octopus v0.1.0  
**最后更新**: 2026年6月