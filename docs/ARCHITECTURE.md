# Octopus 架构文档

## 概述

Octopus 是一个基于决策-执行层分离的 AI 系统架构。它实现了"Slow Thinking"（缓慢思考）范式，将 AI 系统的决策能力与执行能力解耦，从而实现更清晰的关注点分离和更好的可维护性。

## 架构原理

### 核心思想

Octopus 的核心思想是将系统分为两个层次：

1. **决策层（Head）**：负责"缓慢思考"，包括感知、推理、规划和决策
2. **执行层（Tentacles）**：负责"快速执行"，包括工具调用和任务执行

这种分离带来以下优势：
- **消除信息噪音**：避免无序的工具调用
- **防止逻辑冲突**：确保决策一致性
- **真正的业务决策能力**：结构化的决策过程
- **长期规划功能**：模拟和记忆系统支持

## 系统架构图

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
│  │  - Code Execution  - Data Retrieval                 │    │
│  │  - File Operations - API Integration                 │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

| 分类 | 技术 | 版本要求 |
|------|------|----------|
| 语言 | Python | >= 3.10 |
| 构建工具 | setuptools | >= 61.0 |
| 开发依赖 | pytest, pytest-asyncio, black, mypy, ruff | 见 `pyproject.toml` |

## 项目结构

```
octopus/
├── core/                    # 决策层核心组件
│   ├── __init__.py
│   ├── world_model.py       # 世界模型 - 状态管理
│   ├── perception.py        # 感知模块 - 意图识别
│   ├── simulation.py        # 模拟引擎 - 场景模拟
│   ├── decision_engine.py   # 决策引擎 - 结构化决策
│   ├── memory.py            # 长期记忆 - 持久化存储
│   └── ethics.py            # 伦理框架 - 伦理约束
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
├── cli.py                   # 命令行界面
└── __init__.py              # 包初始化
```

## 核心组件详解

### 决策层组件

#### 1. World Model (世界模型)

**功能**：表示和管理系统对世界的理解状态

**核心特性**：
- 实体管理（Entity）
- 全局状态存储
- 目标追踪
- 约束管理
- 状态快照和恢复

**核心类**：
```python
class WorldModel:
    def add_entity(entity: Entity)
    def update_entity(entity_id: str, properties: Dict)
    def query_entities(entity_type: str, filters: Dict)
    def set_global_state(key: str, value: Any)
    def create_snapshot() -> StateSnapshot
    def restore_snapshot(snapshot_id: str)
```

#### 2. Perception Module (感知模块)

**功能**：理解并解析输入信号，提取意图

**核心流程**：
1. 信号收集
2. 意图分类
3. 实体提取
4. 上下文构建
5. 置信度计算

**核心类**：
```python
class PerceptionModule:
    def perceive(raw_input: Any) -> PerceptionResult
    def register_sensor(name: str, sensor: Callable)
    def register_context_provider(provider: Callable)
```

#### 3. Simulation Engine (模拟引擎)

**功能**：在虚拟环境中探索可能的未来场景

**核心特性**：
- 多路径探索
- 不确定性建模
- 风险评估
- 成功率计算

**核心类**：
```python
class SimulationEngine:
    def simulate_scenario(scenario: Scenario) -> SimulationResult
    def simulate_action_sequence(initial_state, actions) -> SimulationResult
    def generate_scenario_variants(base_scenario, count: int) -> List[Scenario]
    def compare_scenarios(scenarios: List) -> List[SimulationResult]
```

#### 4. Decision Engine (决策引擎)

**功能**：评估选项、比较权衡、做出结构化决策

**决策流程**：
1. 加载决策策略
2. 创建决策选项
3. 评估每个选项
4. 检查约束条件
5. 选择最佳选项
6. 生成执行意图

**核心类**：
```python
class DecisionEngine:
    def make_decision(context: Dict, options: List[Dict]) -> Decision
    def add_policy(policy: DecisionPolicy)
    def set_active_policy(policy_id: str)
```

#### 5. Long-Term Memory (长期记忆)

**功能**：持久化存储决策结果和经验教训

**记忆类型**：
- **Episodic**：事件记忆
- **Semantic**：语义记忆
- **Procedural**：过程记忆
- **Working**：工作记忆

**核心类**：
```python
class LongTermMemory:
    def store(content: Dict, memory_type: MemoryType) -> MemoryItem
    def retrieve(memory_id: str) -> Optional[MemoryItem]
    def search(memory_type, tags, context, query) -> List[MemoryItem]
    def store_outcome(outcome: DecisionOutcome)
```

#### 6. Ethics Framework (伦理框架)

**功能**：整合价值体系和伦理约束

**核心特性**：
- 伦理规则定义
- 约束检查
- 决策批准/拒绝
- 审计日志

**核心类**：
```python
class EthicsFramework:
    def check_ethics(action: Dict, context: Dict) -> EthicsCheckResult
    def add_guideline(guideline: EthicalGuideline)
    def register_rule_evaluator(rule_id: str, evaluator: Callable)
```

### 执行层组件

#### 1. Tool Registry (工具注册表)

**功能**：管理和注册所有可执行工具

**核心类**：
```python
class ToolRegistry:
    def register_tool(tool: Tool) -> bool
    def get_tool(tool_id: str) -> Optional[Tool]
    def search_tools(category, tags, query) -> List[Tool]
```

**工具类别**：
- CODE_EXECUTION
- DATA_RETRIEVAL
- FILE_OPERATIONS
- NETWORK
- SYSTEM
- EXTERNAL_INTEGRATION
- UTILITY

#### 2. Execution Layer (执行层)

**功能**：根据决策层的指令执行工具

**核心特性**：
- 任务队列管理
- 执行计划
- 错误处理和重试
- 执行历史追踪

**核心类**：
```python
class ExecutionLayer:
    def execute_intent(intent: ExecutionIntent) -> ExecutionResult
    def execute_single(tool_id: str, parameters: Dict) -> Any
    def execute_batch(executions: List[Dict]) -> List[Any]
    def cancel_execution(plan_id: str) -> bool
```

### 通信协议

#### ODEP Protocol (Octopus Decision Execution Protocol)

**功能**：决策层和执行层之间的通信

**消息类型**：
| 消息类型 | 用途 |
|----------|------|
| `execute.request` | 执行请求 |
| `execute.response` | 执行响应 |
| `state.update` | 状态更新 |
| `decision.request` | 决策请求 |
| `decision.response` | 决策响应 |
| `observation` | 观察结果 |
| `error` | 错误信息 |

**核心类**：
```python
class ODEPProtocol:
    def send_execute_request(sender, recipient, intent) -> ODEPMessage
    def send_execute_response(sender, recipient, result, correlation_id) -> ODEPMessage
    def send_state_update(sender, recipient, update) -> ODEPMessage
    def subscribe(component, callback)
    def publish(component, message)
```

## 数据流

```
1. 输入 → Perception → World Model
                ↓
2. Context → Simulation Engine
                ↓
3. Options → Decision Engine
                ↓
4. Ethics Check → Ethics Framework
                ↓
5. Intent → ODEP Protocol
                ↓
6. Execution → Execution Layer
                ↓
7. Result → Memory + World Model Update
```

## 接口定义

### 决策层接口

```python
class IDecisionLayer(Protocol):
    def perceive(input: Any) -> PerceptionResult
    def make_decision(context: Dict, options: List[Dict]) -> Decision
    def check_ethics(action: Dict) -> EthicsCheckResult
    def get_world_model() -> WorldModel
```

### 执行层接口

```python
class IExecutionLayer(Protocol):
    def execute_intent(intent: ExecutionIntent) -> ExecutionResult
    def execute_single(tool_id: str, params: Dict) -> Any
    def register_tool(tool: Tool) -> bool
    def get_tool_registry() -> ToolRegistry
```

### 协议接口

```python
class IODEPProtocol(Protocol):
    def send_execute_request(intent: ExecutionIntent) -> ODEPMessage
    def send_execute_response(result: ExecutionResult) -> ODEPMessage
    def subscribe(component: str, callback: Callable)
    def publish(component: str, message: ODEPMessage)
```

## 错误处理

### 错误类型

1. **感知错误**: 输入解析失败
2. **模拟错误**: 场景模拟失败
3. **决策错误**: 无法做出决策
4. **伦理错误**: 伦理检查未通过
5. **执行错误**: 工具执行失败
6. **通信错误**: 协议通信失败

### 错误处理策略

```python
try:
    result = execution.execute_intent(intent)
except ExecutionError as e:
    if e.retryable:
        execution.retry(intent, max_attempts=3)
    else:
        log_error(e)
        notify_decision_layer(e)
```

## 性能优化

### 建议

1. **模拟引擎**: 使用异步执行和结果缓存
2. **记忆系统**: 实现 LRU 缓存和自动清理
3. **执行层**: 并行任务执行和超时控制
4. **协议**: 消息队列和批量处理

### 监控指标

- 感知延迟
- 模拟执行时间
- 决策置信度
- 执行成功率
- 工具响应时间
- 协议消息延迟

## 扩展性

### 添加新工具

```python
metadata = ToolMetadata(
    tool_id="new_tool",
    name="New Tool",
    description="Description",
    category=ToolCategory.UTILITY,
)

tool = Tool(metadata)
tool.register_executor(lambda params: do_something(params))

execution.register_tool(tool)
```

### 添加新的伦理规则

```python
def custom_evaluator(action, context):
    return action.get("type") != "prohibited_action"

ethics.register_rule_evaluator("custom_rule", custom_evaluator)
```

### 自定义决策策略

```python
policy = DecisionPolicy(
    policy_id="custom_policy",
    name="Custom Policy",
    criteria=[
        DecisionCriteria("custom_metric", 1.0, "Custom criteria")
    ],
)

decision.add_policy(policy)
decision.set_active_policy("custom_policy")
```

## 最佳实践

1. **分离关注点**: 决策层不直接执行工具
2. **状态管理**: 使用 World Model 维护一致的世界状态
3. **错误恢复**: 实现重试和回滚机制
4. **审计追踪**: 记录所有决策和执行结果
5. **性能监控**: 追踪关键路径的执行时间
6. **安全检查**: 所有决策经过伦理框架审查

## 参考资料

- Slow Thinking Paradigm (2026)
- OpenClaw Execution Agents