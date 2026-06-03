# 🎨 Octopus 数据模型可视化

## 数据流向图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DECISION BRAIN (Head)                                 │
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐   │
│  │   Perceive   │────▶│    Think    │────▶│        Plan             │   │
│  │   Module     │     │   (Reason)  │     │                        │   │
│  └──────────────┘     └──────────────┘     │  ┌─────────────────┐  │   │
│         │                   │                │  │ ExecutionStep 1  │  │   │
│         │                   │                │  │ ExecutionStep 2  │  │   │
│         ▼                   ▼                │  │ ExecutionStep 3  │  │   │
│  ┌──────────────┐     ┌──────────────┐     │  └─────────────────┘  │   │
│  │   World      │     │   Memory     │     └──────────┬───────────┘   │
│  │   Model      │     │   System     │                │               │
│  └──────────────┘     └──────────────┘                │               │
│                                                       │               │
│                                                       │               │
│                    OUTPUT: Plan                        │               │
│                    ┌────────────────────────┐         │               │
│                    │  Plan                  │         │               │
│                    │  - plan_id            │         │               │
│                    │  - objective          │         │               │
│                    │  - steps[]            │         │               │
│                    │  - reasoning         │         │               │
│                    │  - success_criteria  │         │               │
│                    └──────────┬───────────┘         │               │
└───────────────────────────────┼─────────────────────┼───────────────┘
                                │
                                │ TaskRequest (per step)
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMMUNICATION BUS (Protocol)                              │
│                                                                          │
│  Message Format:                                                           │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │ ExecutionRequest                                                │       │
│  │   - request_id: "req_001"                                      │       │
│  │   - task: TaskRequest                                          │       │
│  │     * task_id: "task_001"                                     │       │
│  │     * tool_id: "web_scraper"                                  │       │
│  │     * parameters: {"url": "..."}                              │       │
│  │     * priority: "normal"                                       │       │
│  │     * constraints: {...}                                       │       │
│  └────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EXECUTION TENTACLES (Tentacles)                         │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │ Tentacle #1: Web Scraper                                        │       │
│  │                                                                 │       │
│  │   INPUT: TaskRequest                                            │       │
│  │   ┌──────────────────────────────────────────────────────┐      │       │
│  │   │ task_id: "task_001"                                  │      │       │
│  │   │ tool_id: "web_scraper"                              │      │       │
│  │   │ parameters: {                                        │      │       │
│  │   │   url: "https://example.com",                       │      │       │
│  │   │   selectors: ["h1", ".price"]                       │      │       │
│  │   │ }                                                    │      │       │
│  │   └──────────────────────────────────────────────────────┘      │       │
│  │                                                                 │       │
│  │   PROCESSING:                                                   │       │
│  │   1. Connect to URL                                             │       │
│  │   2. Parse HTML                                                │       │
│  │   3. Extract data                                              │       │
│  │                                                                 │       │
│  │   OUTPUT: ToolResult                                            │       │
│  │   ┌──────────────────────────────────────────────────────┐      │       │
│  │   │ tool_id: "web_scraper"                               │      │       │
│  │   │ task_id: "task_001"                                 │      │       │
│  │   │ status: "completed"                                 │      │       │
│  │   │ output: {                                            │      │       │
│  │   │   h1: "Example Domain",                            │      │       │
│  │   │   prices: ["$19.99", "$29.99", "$39.99"]           │      │       │
│  │   │ }                                                    │      │       │
│  │   │ execution_time_ms: 1234.5                           │      │       │
│  │   │ logs: ["Connecting...", "Parsing...", "Done"]        │      │       │
│  │   └──────────────────────────────────────────────────────┘      │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │ Tentacle #2: Data Processor                                     │       │
│  │   (Receives output from Tentacle #1 as input)                  │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                │
                                │ ToolResult (per step)
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DECISION BRAIN (Head) - Receive                       │
│                                                                          │
│  INPUT: ToolResult (from each Tentacle)                                    │
│  ┌────────────────────────────────────────────────────────────────┐       │
│  │ tool_id: "web_scraper"                                          │       │
│  │ task_id: "task_001"                                             │       │
│  │ status: "completed"                                             │       │
│  │ output: {h1: "...", prices: [...]}                             │       │
│  └────────────────────────────────────────────────────────────────┘       │
│                           │                                                │
│                           ▼                                                │
│                    ┌──────────────┐                                       │
│                    │    Assess    │                                       │
│                    │   Progress   │                                       │
│                    └──────────────┘                                       │
│                           │                                                │
│                           ▼                                                │
│                    ┌──────────────┐                                       │
│                    │   Update     │                                       │
│                    │ World Model  │                                       │
│                    └──────────────┘                                       │
│                           │                                                │
│                           ▼                                                │
│                    ┌──────────────┐                                       │
│                    │  Decision:   │                                       │
│                    │  - Continue? │                                       │
│                    │  - Retry?    │                                       │
│                    │  - Abort?    │                                       │
│                    └──────────────┘                                       │
│                                                                          │
│  FINAL OUTPUT:                                                           │
│  ┌────────────────────────────────────────────────────────────────┐      │
│  │ Plan                                                           │      │
│  │   - plan_id: "plan_xyz"                                        │      │
│  │   - status: "completed" OR "partially_completed" OR "failed"   │      │
│  │   - completed_steps: ["s1", "s2", "s3"]                       │      │
│  │   - step_results: {                                           │      │
│  │       "s1": ToolResult {...},                                 │      │
│  │       "s2": ToolResult {...},                                 │      │
│  │       "s3": ToolResult {...},                                 │      │
│  │   }                                                            │      │
│  │   - final_output: {aggregated_results}                        │      │
│  └────────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 数据模型关系图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA MODEL HIERARCHY                             │
└─────────────────────────────────────────────────────────────────────────┘

                        Plan (Master Blueprint)
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ExecutionStep      ExecutionStep      ExecutionStep
            │                │                │
            └────────┬────────┘                │
                     │                         │
                     ▼                         ▼
            TaskRequest              TaskRequest
            (per step)              (per step)
                     │                         │
                     └────────┬────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ ExecutionRequest│
                     │ (Network Envelope)│
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Communication│
                     │      Bus       │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ ExecutionResponse│
                     │ (Network Envelope)│
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   ToolResult    │
                     │ (per tentacle)  │
                     └─────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         FIELD DETAILS                                    │
└─────────────────────────────────────────────────────────────────────────┘

Plan
├── plan_id: string (UUID)
├── objective: string
├── steps: List[ExecutionStep]
│   ├── step_id: string
│   ├── tool_id: string
│   ├── parameters: Dict
│   └── dependencies: StepDependency
├── reasoning: string (Why this plan?)
├── status: PlanStatus enum
└── step_results: Dict[step_id, ToolResult]


TaskRequest
├── task_id: string (UUID)
├── tool_id: string
├── parameters: Dict
├── priority: TaskPriority enum
├── constraints: TaskConstraints
└── context: TaskContext


ToolResult
├── tool_id: string
├── task_id: string
├── status: TaskStatus enum
├── output: Any
├── error: string (optional)
├── execution_time_ms: float
├── logs: List[string]
└── metadata: Dict


ExecutionRequest (Wrapper)
├── request_id: string
├── task: TaskRequest
└── timeout_seconds: int


ExecutionResponse (Wrapper)
├── request_id: string
├── task_id: string
└── result: ToolResult
```

## 时序图：完整交互流程

```
┌─────────┐           ┌─────────┐           ┌─────────┐           ┌─────────┐
│  User   │           │  Brain  │           │  Bus    │           │ Tentacle│
└────┬────┘           └────┬────┘           └────┬────┘           └────┬────┘
     │                      │                      │                      │
     │ 1. User Input        │                      │                      │
     │─────────────────────▶│                      │                      │
     │                      │                      │                      │
     │                      │ 2. Perceive & Think  │                      │
     │                      │──────────────────────▶│                      │
     │                      │                      │                      │
     │                      │ 3. Generate Plan     │                      │
     │                      │─────────────────────│                      │
     │                      │                      │                      │
     │                      │ 4. Create TaskRequest                      │
     │                      │─────────────────────│                      │
     │                      │                      │                      │
     │                      │ 5. Send ExecutionRequest                    │
     │                      │─────────────────────│─────────────────────▶│
     │                      │                      │                      │
     │                      │                      │                      │
     │                      │                      │ 6. Execute Tool      │
     │                      │                      │─────────────────────▶│
     │                      │                      │                      │
     │                      │                      │                      │
     │                      │                      │ 7. Return ToolResult │
     │                      │                      │◀─────────────────────│
     │                      │                      │                      │
     │                      │ 8. Receive ToolResult                     │
     │                      │◀────────────────────│─────────────────────│
     │                      │                      │                      │
     │                      │ 9. Assess & Decide  │                      │
     │                      │ (continue/retry/abort)                    │
     │                      │                      │                      │
     │                      │ 10. Final Output    │                      │
     │◀─────────────────────│                      │                      │
     │                      │                      │                      │
```

## 完整数据流说明

### 数据流转阶段

| 阶段 | 组件 | 输入 | 输出 | 说明 |
|------|------|------|------|------|
| 1. 感知 | PerceptionModule | 原始输入 | PerceptionResult | 意图识别和实体提取 |
| 2. 状态更新 | WorldModel | Intent + Entities | 更新后的状态 | 维护世界模型状态 |
| 3. 模拟 | SimulationEngine | State + Context | SimulationResult | 场景模拟和风险评估 |
| 4. 决策 | DecisionEngine | Options + Criteria | Decision | 多标准决策分析 |
| 5. 伦理检查 | EthicsFramework | Action + Context | EthicsCheckResult | 伦理约束验证 |
| 6. 协议通信 | ODEPProtocol | ExecutionIntent | ODEPMessage | 消息传递 |
| 7. 执行 | ExecutionLayer | ExecutionIntent | ExecutionResult | 工具执行 |
| 8. 记忆存储 | LongTermMemory | DecisionOutcome | MemoryItem | 持久化结果 |

### 核心数据结构

#### 1. Intent（意图）

```python
{
    "intent_id": "intent_123",
    "intent_type": "command",
    "raw_content": "Execute script with param=value",
    "parsed_content": {
        "action": "execute",
        "target": "script",
        "parameters": {"param": "value"}
    },
    "entities": ["/path/to/script.py"],
    "confidence": 0.85,
    "source": "user",
    "priority": 2,
    "timestamp": "2026-01-15T10:30:00Z"
}
```

#### 2. Decision（决策）

```python
{
    "decision_id": "dec_456",
    "context": {"task": "data_analysis", "priority": "high"},
    "options": [
        {
            "option_id": "opt_1",
            "name": "Quick Analysis",
            "action_sequence": [{"tool_id": "calculator", "parameters": {...}}],
            "scores": {"outcome_value": 0.8, "risk_reduction": 0.6},
            "total_score": 0.72,
            "risk_level": 0.3
        },
        {
            "option_id": "opt_2",
            "name": "Comprehensive Analysis",
            "action_sequence": [{"tool_id": "data_fetcher", "parameters": {...}}],
            "scores": {"outcome_value": 0.9, "risk_reduction": 0.7},
            "total_score": 0.81,
            "risk_level": 0.5
        }
    ],
    "selected_option": "opt_2",
    "status": "decided",
    "reasoning": "Selected 'Comprehensive Analysis' with total score 0.81",
    "confidence": 0.9,
    "execution_intent": {...}
}
```

#### 3. ExecutionIntent（执行意图）

```python
{
    "intent_id": "exec_789",
    "action_type": "data_analysis",
    "parameters": {
        "action_sequence": [
            {"tool_id": "data_fetcher", "parameters": {"type": "full"}},
            {"tool_id": "calculator", "parameters": {"operation": "sum"}}
        ]
    },
    "priority": 2,
    "timeout_seconds": 300,
    "constraints": ["no_pii_access"],
    "metadata": {"origin": "decision_engine"}
}
```

#### 4. ExecutionResult（执行结果）

```python
{
    "intent_id": "exec_789",
    "status": "success",
    "output": {"total": 15000, "count": 100},
    "execution_time_ms": 1234.5,
    "partial_results": [
        {"tool_id": "data_fetcher", "output": [...], "time_ms": 800},
        {"tool_id": "calculator", "output": 15000, "time_ms": 434.5}
    ],
    "metadata": {"plan_id": "plan_001", "task_count": 2}
}
```

#### 5. MemoryItem（记忆项）

```python
{
    "memory_id": "mem_abc",
    "memory_type": "episodic",
    "content": {
        "event": "successful_analysis",
        "decision_id": "dec_456",
        "outcome": "positive",
        "metrics": {"accuracy": 0.95, "duration_ms": 1234}
    },
    "context": {"task_type": "data_analysis", "priority": "high"},
    "relevance": 0.8,
    "access_count": 5,
    "tags": ["analysis", "success", "Q1_report"],
    "created_at": "2026-01-15T10:35:00Z",
    "expiration": "2026-04-15T10:35:00Z"
}
```

## 状态转换图

### 决策状态转换

```
                    ┌──────────────────────────────────────┐
                    │           DECISION STATES            │
                    └──────────────────────────────────────┘

  ┌──────────┐
  │ PENDING  │◀──────────────────────────────────────────┐
  └────┬─────┘                                          │
       │ options provided                                │
       ▼                                                │
  ┌──────────────┐                                      │
  │ EVALUATING  │                                      │
  └──────┬───────┘                                      │
         │ options evaluated                             │
         ▼                                              │
  ┌──────────────┐                                      │
  │  DECIDED    │───────────────────────────────────────┤
  └──────┬───────┘                                      │
         │ execution started                             │
         ▼                                              │
  ┌──────────────┐                                      │
  │ EXECUTING  │───────────────────────────────────────┤
  └──────┬───────┘                                      │
         │ completed                                    │
         ▼                                              │
  ┌──────────────┐                                      │
  │ COMPLETED  │───────────────────────────────────────┤
  └──────────────┘                                      │

         │ error / cancelled
         ▼
  ┌──────────────┐
  │   FAILED    │
  └──────────────┘
```

### 执行状态转换

```
                    ┌──────────────────────────────────────┐
                    │          EXECUTION STATES            │
                    └──────────────────────────────────────┘

  ┌──────────┐
  │   IDLE   │◀──────────────────────────────────────────┐
  └────┬─────┘                                          │
       │ execution intent received                      │
       ▼                                                │
  ┌──────────────┐                                      │
  │ EXECUTING  │                                      │
  └──────┬───────┘                                      │
         │ task completed                               │
         ▼                                              │
  ┌──────────────┐                                      │
  │   IDLE      │◀─────────────────────────────────────┤
  └──────┬───────┘                                      │
         │ error occurred                               │
         ▼                                              │
  ┌──────────────┐                                      │
  │   ERROR     │───────────────────────────────────────┤
  └──────────────┘                                      │
```

## 数据格式规范

### 输入格式规范

#### 用户输入
```python
# 格式1: 纯文本
input_text = "Please calculate the sum of 15 and 27"

# 格式2: 结构化输入
structured_input = {
    "content": "Fetch customer data",
    "context": {
        "source": "api",
        "user_id": "user_123",
        "timestamp": "2026-01-15T10:30:00Z"
    }
}

# 格式3: 批量输入
batch_input = [
    {"content": "Task 1", "context": {...}},
    {"content": "Task 2", "context": {...}}
]
```

#### 决策选项
```python
options = [
    {
        "option_id": "opt_1",
        "name": "Option Name",
        "description": "Description of the option",
        "actions": [
            {
                "tool_id": "tool_name",
                "parameters": {"key": "value"},
                "metadata": {"timeout": 30}
            }
        ],
        "scores": {
            "outcome_value": 0.8,
            "risk_reduction": 0.6,
            "reversibility": 0.9,
            "confidence_alignment": 0.7
        },
        "risk_level": 0.3,
        "reversibility": 0.8,
        "confidence": 0.9,
        "estimated_cost": 100,
        "estimated_benefit": 500,
        "metadata": {}
    }
]
```

### 输出格式规范

#### 标准化响应
```python
response = {
    "status": "success",  # "success", "error", "pending"
    "data": {...},        # 实际数据
    "metadata": {
        "timestamp": "2026-01-15T10:30:00Z",
        "version": "1.0",
        "trace_id": "abc-123"
    },
    "errors": []          # 错误列表（如有）
}
```

#### 错误响应
```python
error_response = {
    "status": "error",
    "data": None,
    "metadata": {
        "timestamp": "2026-01-15T10:30:00Z",
        "version": "1.0"
    },
    "errors": [
        {
            "code": "E001",
            "message": "Tool not found",
            "details": {"tool_id": "unknown_tool"},
            "retryable": False
        }
    ]
}
```

## 代码示例

### Example 1: 完整工作流程

```python
from octopus.core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    DecisionPolicy,
    DecisionCriteria,
    EthicsFramework,
    Entity,
)
from octopus.execution import ExecutionLayer, Tool, ToolMetadata
from octopus.protocol import ExecutionIntent, Priority

# 1. 初始化组件
world_model = WorldModel()
perception = PerceptionModule()
simulation = SimulationEngine()
decision = DecisionEngine()
ethics = EthicsFramework()
execution = ExecutionLayer()

# 2. 配置决策策略
policy = DecisionPolicy(
    policy_id="example_policy",
    name="Example Policy",
    criteria=[
        DecisionCriteria("outcome_value", 0.4, "Value of outcome"),
        DecisionCriteria("risk_reduction", 0.3, "Risk reduction"),
        DecisionCriteria("reversibility", 0.3, "Reversibility"),
    ]
)
decision.add_policy(policy)

# 3. 注册工具
def calculator_executor(params):
    return params.get("a", 0) + params.get("b", 0)

metadata = ToolMetadata(
    tool_id="calculator",
    name="Calculator",
    description="Basic arithmetic operations",
    category="utility"
)
tool = Tool(metadata)
tool.register_executor(calculator_executor)
execution.register_tool(tool)

# 4. 处理输入
input_text = "Calculate 10 + 20"
perception_result = perception.perceive(input_text)

# 5. 更新世界模型
world_model.add_entity(Entity(
    entity_id="user_1",
    entity_type="user",
    properties={"request": input_text}
))

# 6. 做出决策
options = [
    {
        "name": "Execute Calculation",
        "actions": [{"tool_id": "calculator", "parameters": {"a": 10, "b": 20}}],
        "scores": {"outcome_value": 0.9, "risk_reduction": 0.9, "reversibility": 1.0}
    }
]
decision_result = decision.make_decision({"task": "calculation"}, options)

# 7. 伦理检查
ethics.add_guideline(ethics.create_default_guideline())
ethics_result = ethics.check_ethics(decision_result.execution_intent or {}, {})

# 8. 执行
if ethics_result.decision.value == "approved" and decision_result.execution_intent:
    intent = ExecutionIntent(
        intent_id=decision_result.decision_id,
        action_type="calculation",
        parameters=decision_result.execution_intent["parameters"],
        priority=Priority.NORMAL
    )
    exec_result = execution.execute_intent(intent)
    print(f"Result: {exec_result.output}")
```

### Example 2: 数据流转监控

```python
from octopus.core import LongTermMemory, MemoryType
from octopus.core.decision_engine import DecisionOutcome

# 监控执行结果并存储
memory = LongTermMemory()

# 存储决策结果
outcome = DecisionOutcome(
    decision_id="dec_123",
    selected_option_id="opt_456",
    execution_result={"status": "success"},
    actual_outcome={"result": 30},
    success=True,
    lessons_learned=["Calculator works correctly"]
)
memory.store_outcome(outcome)

# 查询历史记录
recent_outcomes = memory.get_recent_outcomes(limit=5)
print(f"Recent outcomes: {len(recent_outcomes)}")

# 搜索相关记忆
results = memory.search(tags=["calculation", "success"])
print(f"Found {len(results)} related memories")
```

---

**版本**: Octopus v0.1.0  
**最后更新**: 2026年6月