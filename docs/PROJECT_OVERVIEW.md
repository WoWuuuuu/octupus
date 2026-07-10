# Octopus 项目介绍文档

## 一、项目概述

**Octopus** 是一个基于**决策-执行层分离架构**的 AI 系统框架。系统名称象征性地代表了"头"（决策层）和"触手"（执行层）的分离，实现了"Slow Thinking"（缓慢思考）范式。

### 架构设计理念

| 设计原则 | 说明 |
|---------|------|
| **关注点分离** | 决策层负责思考，执行层负责行动 |
| **消除信息噪音** | 避免无序的工具调用 |
| **防止逻辑冲突** | 确保决策一致性 |
| **长期规划支持** | 模拟引擎和记忆系统支持复杂决策 |
| **伦理约束** | 内置伦理框架确保决策符合价值体系 |

---

## 二、系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Octopus System                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           DECISION LAYER (Head - 缓慢思考)          │    │
│  │                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │    │
│  │  │ Perception  │→ │ World Model │→ │ Simulation│ │    │
│  │  │   Module     │  │             │  │   Engine   │ │    │
│  │  └─────────────┘  └─────────────┘  └───────────┘ │    │
│  │         ↓                ↓               ↓         │    │
│  │  ┌─────────────────────────────────────┐  │    │
│  │  │           Decision Engine                    │  │    │
│  │  │  (Option Comparison & Selection)            │  │    │
│  │  └─────────────────────────────────────────────┘  │    │
│  │         ↓                                            │    │
│  │  ┌──────────────┐  ┌────────────────┐             │    │
│  │  │    Ethics    │  │ Long-Term      │             │    │
│  │  │  Framework   │  │    Memory      │             │    │
│  │  └──────────────┘  └────────────────┘             │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                          ↓ ODEP Protocol                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          EXECUTION LAYER (Tentacles - 快速思考)      │    │
│  │                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │    │
│  │  │    Tool     │  │  Execution  │  │  External │ │    │
│  │  │  Registry   │←→│    Layer    │←→│   Agents   │ │    │
│  │  └─────────────┘  └─────────────┘  └───────────┘ │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 架构层次

| 层次 | 职责 | 特点 |
|------|------|------|
| **决策层** | 感知、推理、规划、决策 | 缓慢思考，深度分析 |
| **协议层** | 层间通信 | ODEP 协议 |
| **执行层** | 工具调用、任务执行 | 快速执行，无决策能力 |

---

## 三、核心模块详解

### 3.1 决策层组件

#### 3.1.1 World Model（世界模型）

**位置**: `octopus/core/world_model.py`

**功能**:
- 表示和管理系统对世界的理解状态
- 维护实体、关系、全局状态
- 支持状态快照和恢复

**核心类**:

| 类名 | 职责 |
|------|------|
| `WorldModel` | 主类，管理所有实体和状态 |
| `Entity` | 实体表示，包含属性和关系 |
| `StateSnapshot` | 状态快照，用于恢复 |
| `StateConfidence` | 状态置信度枚举 |

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

#### 3.1.2 Perception Module（感知模块）

**位置**: `octopus/core/perception.py`

**功能**:
- 处理原始输入信号
- 意图识别和分类
- 实体提取（邮箱、URL、路径等）
- 上下文构建
- 置信度计算

**核心类**:

| 类名 | 职责 |
|------|------|
| `PerceptionModule` | 主类，处理感知 |
| `Intent` | 意图数据结构 |
| `PerceptionResult` | 感知结果 |
| `IntentParser` | 意图解析器 |
| `IntentType` | 意图类型枚举 |
| `SignalSource` | 信号来源枚举 |

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

**感知流程**:

1. 信号收集
2. 意图分类
3. 实体提取
4. 上下文构建
5. 置信度计算

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

#### 3.1.3 Simulation Engine（模拟引擎）

**位置**: `octopus/core/simulation.py`

**功能**:
- 在虚拟环境中探索可能的未来场景
- 多路径探索和分支
- 风险评估
- 成功率计算
- 蒙特卡洛模拟（可选）

**核心类**:

| 类名 | 职责 |
|------|------|
| `SimulationEngine` | 主类，管理模拟 |
| `Scenario` | 场景定义 |
| `SimulationResult` | 模拟结果 |
| `SimulationConfig` | 模拟配置 |
| `SimulationState` | 模拟状态枚举 |
| `ActionSimulator` | 动作模拟器 |

**模拟状态**:

| 状态 | 说明 |
|------|------|
| PENDING | 待处理 |
| RUNNING | 运行中 |
| COMPLETED | 完成 |
| TERMINATED | 终止 |
| FAILED | 失败 |

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

#### 3.1.4 Decision Engine（决策引擎）

**位置**: `octopus/core/decision_engine.py`

**功能**:
- 评估和比较决策选项
- 多标准决策分析
- 执行意图生成
- 决策策略管理
- 决策历史追踪

**核心类**:

| 类名 | 职责 |
|------|------|
| `DecisionEngine` | 主类，管理决策 |
| `Decision` | 决策数据结构 |
| `DecisionOption` | 决策选项 |
| `DecisionPolicy` | 决策策略 |
| `DecisionCriteria` | 决策标准 |
| `DecisionStatus` | 决策状态枚举 |
| `DecisionPriority` | 决策优先级枚举 |

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

**决策流程**:

1. 加载决策策略
2. 创建决策选项
3. 评估每个选项（基于多标准评分）
4. 检查约束条件
5. 选择最佳选项
6. 生成执行意图

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

**决策标准示例**:

| 标准 | 权重 | 说明 |
|------|------|------|
| outcome_value | 0.40 | 预期结果价值 |
| risk_reduction | 0.25 | 风险降低程度 |
| reversibility | 0.20 | 可逆转性 |
| confidence_alignment | 0.15 | 置信度匹配 |

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

#### 3.1.5 Long-Term Memory（长期记忆）

**位置**: `octopus/core/memory.py`

**功能**:
- 持久化存储经验和结果
- 多种记忆类型支持
- 语义搜索和检索
- 经验学习和遗忘机制
- 记忆索引管理

**核心类**:

| 类名 | 职责 |
|------|------|
| `LongTermMemory` | 主类，管理记忆 |
| `MemoryItem` | 记忆项 |
| `DecisionOutcome` | 决策结果 |
| `MemoryIndex` | 记忆索引 |
| `MemoryType` | 记忆类型枚举 |
| `MemoryRelevance` | 记忆相关性枚举 |

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

#### 3.1.6 Ethics Framework（伦理框架）

**位置**: `octopus/core/ethics.py`

**功能**:
- 价值体系和伦理规则管理
- 决策伦理审查
- 约束检查和违规检测
- 审计日志记录

**核心类**:

| 类名 | 职责 |
|------|------|
| `EthicsFramework` | 主类，管理伦理 |
| `EthicalGuideline` | 伦理指南 |
| `EthicalRule` | 伦理规则 |
| `ValueSystem` | 价值系统 |
| `EthicsCheckResult` | 检查结果 |
| `EthicalPrinciple` | 伦理原则枚举 |
| `EthicsDecision` | 伦理决策枚举 |

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

### 3.2 执行层组件

#### 3.2.1 Tool Registry（工具注册表）

**位置**: `octopus/execution/tools.py`

**功能**:
- 工具注册和管理
- 工具搜索和过滤
- 工具元数据管理
- 分类和标签索引

**核心类**:

| 类名 | 职责 |
|------|------|
| `ToolRegistry` | 主类，管理工具 |
| `Tool` | 工具封装 |
| `ToolMetadata` | 工具元数据 |
| `ToolParameter` | 工具参数 |
| `ToolExecution` | 工具执行记录 |
| `ToolCategory` | 工具类别枚举 |
| `ToolStatus` | 工具状态枚举 |

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

#### 3.2.2 Execution Layer（执行层）

**位置**: `octopus/execution/executor.py`

**功能**:
- 接收并执行决策层的执行意图
- 任务队列管理
- 执行计划编排
- 错误处理和重试
- 执行历史追踪

**核心类**:

| 类名 | 职责 |
|------|------|
| `ExecutionLayer` | 主类，管理执行 |
| `ExecutionPlan` | 执行计划 |
| `ExecutionTask` | 执行任务 |
| `ExecutionState` | 执行状态枚举 |

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

### 3.3 通信协议

#### ODEP Protocol（Octopus Decision Execution Protocol）

**位置**: `octopus/protocol/communication.py`

**功能**:
- 决策层和执行层之间的通信
- 消息队列管理
- 请求-响应关联
- 状态更新传播

**核心类**:

| 类名 | 职责 |
|------|------|
| `ODEPProtocol` | 主类，管理协议 |
| `ODEPMessage` | 消息结构 |
| `ExecutionIntent` | 执行意图 |
| `ExecutionResult` | 执行结果 |
| `WorldStateUpdate` | 世界状态更新 |
| `MessageType` | 消息类型枚举 |
| `ExecutionStatus` | 执行状态枚举 |
| `Priority` | 优先级枚举 |

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

## 四、模块间接口定义

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

## 五、数据处理流程

### 完整工作流程

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Input      │───▶│ Perception   │───▶│ World Model  │
│   Signal     │    │   Module     │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Memory     │◀───│ Decision     │◀───│ Simulation   │
│  (Learning)  │    │   Engine     │    │   Engine     │
└──────────────┘    └──────────────┘    └──────────────┘
                        │
                        ▼
              ┌──────────────┐
              │ Ethics       │
              │ Framework    │
              └──────────────┘
                        │
                        ▼
              ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
              │  ODEP        │───▶│ Execution    │───▶│   Tools      │
              │  Protocol    │    │   Layer      │    │   Registry   │
              └──────────────┘    └──────────────┘    └──────────────┘
                                                │
                                                ▼
                                   ┌──────────────┐
                                   │   External   │
                                   │   Agents     │
                                   └──────────────┘
```

### 详细数据流转

1. **输入层 → 感知模块**: 原始信号输入，意图识别
   - 输入: 文本/结构化数据
   - 输出: `PerceptionResult`（包含意图列表、实体提取、置信度）

2. **感知模块 → 世界模型**: 更新实体和状态
   - 输入: 意图信息、上下文
   - 输出: 状态更新确认

3. **世界模型 → 模拟引擎**: 提供当前状态
   - 输入: 当前状态快照
   - 输出: 模拟结果（风险评估、成功率）

4. **模拟引擎 → 决策引擎**: 场景模拟结果
   - 输入: `SimulationResult`
   - 输出: 决策选项评分更新

5. **决策引擎 → 伦理框架**: 决策方案审查
   - 输入: 执行意图
   - 输出: `EthicsCheckResult`（批准/拒绝）

6. **决策引擎 → ODEP协议**: 执行意图传递
   - 输入: `ExecutionIntent`
   - 输出: `ODEPMessage`

7. **ODEP协议 → 执行层**: 消息分发
   - 输入: 协议消息
   - 输出: 执行请求

8. **执行层 → 工具注册表**: 工具查找
   - 输入: 工具ID
   - 输出: `Tool` 对象

9. **执行层 → 外部工具**: 执行操作
   - 输入: `ExecutionTask`
   - 输出: 工具执行结果

10. **执行结果 → 记忆系统**: 结果持久化
    - 输入: `DecisionOutcome`
    - 输出: 记忆存储确认

---

## 六、关键业务逻辑实现

### 6.1 决策制定流程

```python
def make_decision(self, context, options, constraints, priority):
    # 1. 创建决策对象
    decision = Decision(decision_id, context, options, priority, criteria)

    # 2. 处理每个选项
    for option_data in options:
        option = DecisionOption(...)
        option.calculate_total_score(criteria)  # 多标准评分
        option.constraints_satisfied = check_constraints(option)
        decision.options.append(option)

    # 3. 模拟增强（可选）
    if simulation_engine:
        for option in decision.options:
            sim_result = simulation.simulate_action_sequence(
                context, option.action_sequence
            )
            option.criteria_scores["outcome_value"] = sim_result.success_metrics["overall_score"]
            option.risk_level = sim_result.risk_assessment["total_risk"]

    # 4. 选择最佳选项
    decision.select_best_option()

    # 5. 生成执行意图
    decision.create_execution_intent()

    return decision
```

### 6.2 选项评分算法

```python
def calculate_total_score(self, criteria):
    """
    加权求和评分算法:
    total_score = Σ(score_i * weight_i) / Σ(weight_i)
    """
    total_weight = sum(c.weight for c in criteria)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(
        self.criteria_scores.get(c.name, 0.0) * c.weight
        for c in criteria
    )

    return weighted_sum / total_weight
```

### 6.3 执行计划编排

```python
def execute_intent(self, intent):
    # 1. 创建执行计划
    plan = self._create_execution_plan(intent)

    # 2. 依次执行任务
    results = []
    while not plan.is_complete():
        task = plan.get_current_task()

        # 3. 执行单个任务
        task_result = self._execute_task(task)
        results.append(task_result)

        # 4. 错误处理和重试
        if error and task.retry_count < task.max_retries:
            task.retry_count += 1
            continue
        elif error:
            return ExecutionResult(status=FAILED, error=str(e))

        plan.advance_task()

    # 5. 返回结果
    return ExecutionResult(status=SUCCESS, output=results)
```

### 6.4 伦理检查流程

```python
def check_ethics(self, action, context):
    result = EthicsCheckResult()

    # 1. 获取适用规则
    applicable_rules = self._get_applicable_rules(action)

    # 2. 评估每个规则
    for rule in applicable_rules:
        evaluator = self.rule_evaluators.get(rule.rule_id)
        if evaluator and not evaluator(action, context):
            result.violated_rules.append(rule)

    # 3. 计算伦理分数
    ethical_score = 1.0 - (len(violated_rules) / len(applicable_rules))

    # 4. 做出决策
    if len(violated_rules) == 0:
        result.decision = EthicsDecision.APPROVED
    elif ethical_score > 0.5:
        result.decision = EthicsDecision.APPROVED_WITH_CONDITIONS
    else:
        result.decision = EthicsDecision.REJECTED

    return result
```

---

## 七、技术栈选型

### 核心技术

| 分类 | 技术 | 版本要求 | 选型理由 |
|------|------|----------|----------|
| 语言 | Python | >= 3.10 | 语法简洁，生态成熟，适合AI/ML开发 |
| 构建工具 | setuptools | >= 61.0 | Python标准打包工具 |
| 类型注解 | typing | 内置 | 提高代码可维护性 |
| 数据类 | dataclasses | 内置 | 简化数据结构定义 |

### 开发依赖

| 工具 | 用途 |
|------|------|
| pytest | 单元测试 |
| pytest-asyncio | 异步测试 |
| black | 代码格式化 |
| mypy | 类型检查 |
| ruff | 代码检查 |

### 架构设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| **分层架构** | 决策层/执行层分离 | 关注点分离 |
| **策略模式** | 决策策略管理 | 可插拔策略 |
| **观察者模式** | 协议订阅/发布 | 事件驱动 |
| **工厂模式** | 工具注册 | 动态工具加载 |
| **责任链模式** | 伦理规则评估 | 链式规则检查 |

---

## 八、技术难点说明

### 8.1 核心挑战

| 难点 | 描述 | 解决方案 |
|------|------|----------|
| **意图理解歧义** | 自然语言输入可能有多种解释 | 置信度计算、多意图识别 |
| **决策一致性** | 确保决策符合既定策略和伦理 | 策略模式 + 伦理框架 |
| **模拟准确性** | 预测未来场景的不确定性 | 蒙特卡洛模拟、风险评估 |
| **执行可靠性** | 工具执行可能失败 | 重试机制、错误处理 |
| **记忆管理** | 长期记忆的有效检索和遗忘 | LRU缓存、TTL机制 |
| **性能优化** | 复杂决策可能耗时 | 异步执行、结果缓存 |

### 8.2 性能优化策略

1. **模拟引擎优化**
   - 使用异步执行
   - 结果缓存机制
   - 早停阈值（`early_stopping_threshold`）

2. **记忆系统优化**
   - LRU 缓存实现
   - 自动清理过期记忆
   - 语义索引加速搜索

3. **执行层优化**
   - 并行任务执行
   - 超时控制
   - 批量处理

4. **协议优化**
   - 消息队列
   - 批量消息处理
   - 消息压缩

### 8.3 监控指标

| 指标 | 目标值 | 监控意义 |
|------|--------|----------|
| 感知延迟 | < 50ms | 输入响应速度 |
| 模拟执行时间 | < 500ms | 场景探索效率 |
| 决策置信度 | > 0.7 | 决策质量 |
| 执行成功率 | > 95% | 执行可靠性 |
| 工具响应时间 | < 1000ms | 工具性能 |
| 协议消息延迟 | < 10ms | 层间通信效率 |

---

## 九、扩展指南

### 9.1 添加新工具

```python
# 1. 创建元数据
metadata = ToolMetadata(
    tool_id="my_custom_tool",
    name="My Custom Tool",
    description="Description",
    category=ToolCategory.UTILITY,
    parameters=[
        ToolParameter("input", "string", "Input data", required=True)
    ],
)

# 2. 创建工具并注册执行器
tool = Tool(metadata)
tool.register_executor(lambda params: process_input(params["input"]))

# 3. 注册到执行层
execution.register_tool(tool)
```

### 9.2 添加伦理规则

```python
def custom_ethics_check(action, context):
    # 自定义伦理检查逻辑
    if action.get("type") == "sensitive_operation":
        return context.get("approved", False)
    return True

ethics.register_rule_evaluator("custom_rule", custom_ethics_check)
```

### 9.3 自定义决策策略

```python
policy = DecisionPolicy(
    policy_id="custom_policy",
    name="Custom Policy",
    criteria=[
        DecisionCriteria("custom_metric", 1.0, "Custom evaluation")
    ],
    hard_constraints=["no_dangerous_actions"]
)

decision.add_policy(policy)
decision.set_active_policy("custom_policy")
```

---

## 十、项目结构

```
octopus/
├── core/                    # 决策层核心组件
│   ├── __init__.py
│   ├── world_model.py       # 世界模型
│   ├── perception.py        # 感知模块
│   ├── simulation.py        # 模拟引擎
│   ├── decision_engine.py   # 决策引擎
│   ├── memory.py            # 长期记忆
│   └── ethics.py            # 伦理框架
├── execution/               # 执行层组件
│   ├── __init__.py
│   ├── tools.py             # 工具注册表
│   └── executor.py          # 执行层
├── protocol/                # 通信协议
│   ├── __init__.py
│   └── communication.py     # ODEP协议
├── models/                  # 数据模型
│   ├── __init__.py
│   └── core_models.py       # Pydantic模型定义
├── examples/                # 示例代码
│   ├── __init__.py
│   ├── full_workflow.py     # 完整工作流演示
│   └── simple_example.py    # 简单示例
├── tests/                   # 测试用例
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_execution.py
│   └── test_integration.py
├── docs/                    # 文档
│   ├── PROJECT_OVERVIEW.md  # 项目介绍（本文档）
│   ├── ARCHITECTURE.md
│   ├── COMPONENTS.md
│   └── DATA_MODELS.md
├── cli.py                   # 命令行界面
├── README.md
└── pyproject.toml           # 项目配置
```

---

## 十一、快速开始

### 安装

```bash
pip install -e .
```

### 运行示例

```bash
python examples/full_workflow.py
```

### 使用CLI

```bash
python -m octopus.cli
```

CLI 命令:
- `status` - 查看系统状态
- `perceive <input>` - 处理输入
- `decide <context>` - 做决策
- `execute <intent>` - 执行意图
- `memory` - 查看记忆
- `help` - 显示帮助

---

## 十二、最佳实践

1. **分离关注点**: 决策层不直接执行工具
2. **状态管理**: 使用 World Model 维护一致的世界状态
3. **错误恢复**: 实现重试和回滚机制
4. **审计追踪**: 记录所有决策和执行结果
5. **性能监控**: 追踪关键路径的执行时间
6. **安全检查**: 所有决策经过伦理框架审查
7. **配置管理**: 使用策略模式管理决策标准
8. **扩展性设计**: 预留插件接口支持自定义工具和规则

---

**版本**: Octopus v0.1.0
**最后更新**: 2026年6月
