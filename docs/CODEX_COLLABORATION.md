# 🎯 Octopus 与 Codex 协同开发指南

## 📋 第一步：锁定架构规则

把以下内容添加到你的 **Cursor Rules for AI** 或 `.cursorrules` 文件：

```markdown
# Project Octopus - Agentic System Architecture Rules

## 核心哲学

**Octopus 采用生物隐喻**：八爪鱼有聪明的大脑和无数灵活的触手。

- **Head（决策层）**：不直接使用工具，只负责感知、模拟、规划、评估
- **Tentacles（执行层）**：纯粹的 ReAct 代理或工具函数，只执行任务不决策

## 硬性规则（违反 = 重写）

### ❌ 禁止：Monolith 面条代码

```python
# 禁止模式：脑手不分的 ReAct 循环
while True:
    thought = model.think()
    if "tool" in thought:
        result = execute(tool, thought)
        # 错误！这里混在一起了！
```

### ✅ 允许：清晰的职责分离

```python
# 正确模式：Decision Brain → Communication → Execution Tentacle

# 决策层（大脑）
plan: Plan = brain.make_decision(context)
#                    ↓ 通信协议
# 执行层（触手）
result: ToolResult = tentacles.execute(plan)
```

## 数据模型约定

### 必须使用 Pydantic 模型

所有层间通信必须使用 `octopus.models.core_models` 中定义的模型：

- `TaskRequest` - 任务请求（Brain → Tentacle）
- `Plan` - 执行计划（Brain 的输出）
- `ToolResult` - 工具结果（Tentacle → Brain）

### 模型导入示例

```python
from octopus.models.core_models import (
    TaskRequest,
    Plan,
    ToolResult,
    TaskPriority,
    create_task_request,
    create_plan
)
```

## 开发阶段约定

### Phase 1: 搭骨架（定义数据结构）

在此阶段只定义：
- 数据模型（已完成 ✅）
- 接口契约
- 消息格式

**Codex 任务示例**：
> "Define the data models for TaskRequest, Plan, and ToolResult using Pydantic"

### Phase 2: 写大脑（Decision Brain）

**Codex 任务示例**：
> "Write the Decision Brain module that uses the core models. Focus on the Prompt Engineering for the reasoning loop."

**Codex 提示**：
> "Remember: The Brain does NOT call tools. It only generates Plans."

### Phase 3: 接触手（Execution Tentacles）

**Codex 任务示例**：
> "Write the Execution Tentacle base class that receives TaskRequests and returns ToolResults"

**Codex 提示**：
> "Tentacles are dumb but fast. They should be simple ReAct agents or direct function calls."

## 可观测性要求

### 必须记录的内容

**Decision Brain（Slow Thinking）**：
- 每个推理步骤（BrainThought）
- 考虑的替代方案
- 选择当前方案的理由
- 世界状态变化

**Execution Tentacles（Fast Thinking）**：
- 每个工具调用
- 执行时间
- 返回结果
- 错误和警告

### 日志格式示例

```python
from octopus.models.core_models import BrainThought

# Brain 记录思考过程
thought = BrainThought(
    thought_id="think_001",
    thought_type="reasoning",
    content="Analyzing user request: gather competitor pricing",
    confidence=0.95
)

# Tentacle 记录执行过程
result = ToolResult(
    tool_id="web_scraper",
    task_id="task_123",
    status="completed",
    output={"prices": [...]},
    logs=["Connecting to website...", "Parsing HTML...", "Extracted 15 prices"]
)
```

## 禁止事项

1. ❌ 不允许在 Brain 模块中直接调用工具
2. ❌ 不允许在 Tentacle 模块中做高层次的决策
3. ❌ 不允许跳过类型检查直接传 dict
4. ❌ 不允许在循环中既规划又执行

## 允许事项

1. ✅ Brain 可以调用 Simulation Engine 模拟未来
2. ✅ Brain 可以访问 Memory 和 World State
3. ✅ Tentacle 可以重试失败的子任务
4. ✅ Tentacle 可以返回部分结果

## 验收标准

每次提交代码前，必须确保：

- [ ] 代码使用 Pydantic 模型进行类型检查
- [ ] Decision Brain 没有直接的工具调用
- [ ] 所有推理过程都有日志记录
- [ ] 单元测试覆盖核心逻辑
- [ ] 模型示例与文档一致

## 文件结构约定

```
octopus/
├── models/                    # ✅ 核心数据模型（Pydantic）
│   ├── __init__.py
│   └── core_models.py
├── brain/                     # ⬜ 决策层（待实现）
│   ├── __init__.py
│   ├── decision_brain.py
│   ├── planner.py
│   ├── evaluator.py
│   └── delegator.py
├── tentacles/                 # ⬜ 执行层（待实现）
│   ├── __init__.py
│   ├── base_tentacle.py
│   ├── web_scraper.py
│   ├── database.py
│   └── code_executor.py
├── protocol/                 # ✅ 通信协议（已实现）
│   ├── __init__.py
│   └── communication.py
└── tests/                    # 测试
    ├── test_models.py
    ├── test_brain.py
    └── test_tentacles.py
```

## 与 Codex 对话示例

### 对话 1：定义数据结构

**你**：
```
请基于 octopus/models/core_models.py 中已定义的数据模型，
创建一个示例用法文档，展示如何创建 TaskRequest, Plan, 和 ToolResult。
```

**Codex 输出**：
```python
# 示例代码...
```

### 对话 2：实现决策大脑

**你**：
```
现在请实现 Decision Brain 模块。

要求：
1. 使用 core_models 中的 Pydantic 模型
2. Brain 不直接调用工具，只生成 Plan
3. 包含完整的 Prompt Engineering
4. 记录所有推理过程为 BrainThought

请先写一个简单的版本，包含：
- make_decision(context) -> Plan
- evaluate_plan(plan) -> PlanValidation
- delegate_to_tentacles(plan) -> List[TaskRequest]
```

### 对话 3：实现执行触手

**你**：
```
现在请实现 Execution Tentacles 模块。

要求：
1. 接收 TaskRequest，返回 ToolResult
2. 使用 core_models 中的类型
3. 包含重试逻辑和错误处理
4. 记录所有执行日志

请实现：
- BaseTentacle 抽象基类
- 具体的工具实现（WebScraperTentacle, CodeExecutionTentacle）
```

## 下一步

1. ✅ 已完成：核心数据模型
2. ⬜ 下一步：实现 Decision Brain
3. ⬜ 下一步：实现 Execution Tentacles
4. ⬜ 下一步：实现通信协议
5. ⬜ 下一步：集成测试

---

**记住**：Octopus 的核心是"脑手分离"。大脑思考，触手执行。永远不要让它们混在一起！
