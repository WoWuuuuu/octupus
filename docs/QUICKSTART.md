# Octopus 快速入门指南

## 安装

```bash
# 克隆项目
git clone https://github.com/your-repo/Octopus.git
cd Octopus

# 安装依赖
pip install -e .

# 或者仅安装运行时依赖
pip install -e ".[dev]"
```

## 快速开始

### 1. 简单示例

```python
from octopus.core import (
    WorldModel,
    PerceptionModule,
    DecisionEngine,
)
from octopus.execution import ExecutionLayer, Tool, ToolMetadata

# 创建组件
world_model = WorldModel()
perception = PerceptionModule()
decision = DecisionEngine()
execution = ExecutionLayer()

# 设置决策引擎
decision.set_world_model(world_model)

# 创建工具
metadata = ToolMetadata(
    tool_id="calculator",
    name="Calculator",
    description="Simple calculator",
    category="utility",
)

tool = Tool(metadata)
tool.register_executor(lambda params: params.get("a", 0) + params.get("b", 0))
execution.register_tool(tool)

# 处理输入
result = perception.perceive("Add 10 and 20")
print(f"Intent: {result.intents[0].intent_type.value}")

# 做决策
options = [
    {
        "name": "Calculate",
        "actions": [{"tool_id": "calculator", "parameters": {"a": 10, "b": 20}}],
        "scores": {"outcome_value": 0.9, "risk_reduction": 0.8, "reversibility": 0.7}
    }
]

decision_result = decision.make_decision({"task": "addition"}, options)
print(f"Selected: {decision_result.selected_option.name}")

# 执行
if decision_result.execution_intent:
    from octopus.protocol import ExecutionIntent, Priority
    
    intent = ExecutionIntent(
        intent_id=decision_result.decision_id,
        action_type="calculate",
        parameters=decision_result.execution_intent["parameters"],
        priority=Priority.NORMAL,
    )
    
    exec_result = execution.execute_intent(intent)
    print(f"Result: {exec_result.output}")  # 输出: 30
```

### 2. 完整工作流示例

查看 `examples/full_workflow.py` 获取完整的端到端示例。

```bash
python examples/full_workflow.py
```

### 3. 使用CLI

```bash
python -m octopus.cli
```

在CLI中：

```
octopus> help
octopus> status
octopus> perceive I need to analyze data
octopus> decide Create a report
octopus> exit
```

## 核心概念

### 决策层 (Decision Layer)

决策层负责"思考"：

1. **Perception**: 理解用户意图
2. **World Model**: 维护世界状态
3. **Simulation**: 探索未来场景
4. **Decision Engine**: 选择最佳行动方案
5. **Ethics Framework**: 确保符合伦理
6. **Memory**: 记住过去的经验

### 执行层 (Execution Layer)

执行层负责"行动"：

1. **Tool Registry**: 管理可用工具
2. **Execution Layer**: 执行决策指令
3. **Error Handling**: 处理执行错误

### 通信协议

**ODEP (Octopus Decision Execution Protocol)** 连接两个层：

```
Decision Layer → ODEP Protocol → Execution Layer
```

## 常见使用场景

### 场景1: 自动化任务规划

```python
from octopus.core import WorldModel, PerceptionModule, SimulationEngine, DecisionEngine
from octopus.execution import ExecutionLayer
from octopus.protocol import ExecutionIntent, Priority

# 初始化
world = WorldModel()
perception = PerceptionModule()
simulation = SimulationEngine()
decision = DecisionEngine()
execution = ExecutionLayer()

# 设置连接
decision.set_world_model(world)
decision.set_simulation_engine(simulation)

# 用户输入
user_input = "Schedule a meeting with the team next week"
perception_result = perception.perceive(user_input)

# 决策
context = {"intent": perception_result.intents[0].intent_type.value}
options = [
    {
        "name": "Create Meeting",
        "actions": [{"tool_id": "calendar", "parameters": {...}}],
        "scores": {"outcome_value": 0.9, "risk_reduction": 0.7}
    },
    {
        "name": "Send Email",
        "actions": [{"tool_id": "email", "parameters": {...}}],
        "scores": {"outcome_value": 0.6, "risk_reduction": 0.8}
    }
]

decision_result = decision.make_decision(context, options)

# 执行
if decision_result.selected_option:
    intent = ExecutionIntent(
        intent_id=decision_result.decision_id,
        action_type="scheduling",
        parameters=decision_result.execution_intent["parameters"],
        priority=Priority.NORMAL,
    )
    result = execution.execute_intent(intent)
```

### 场景2: 数据分析决策

```python
from octopus.core import SimulationEngine, DecisionEngine

simulation = SimulationEngine()
decision = DecisionEngine()

# 模拟不同分析方案
scenarios = [
    {
        "name": "Quick Analysis",
        "initial_state": {"data_size": 10000},
        "actions": [{"type": "basic_analysis"}],
    },
    {
        "name": "Deep Analysis", 
        "initial_state": {"data_size": 10000},
        "actions": [{"type": "deep_learning_analysis"}],
    }
]

# 决策
options = [
    {
        "name": scenario["name"],
        "actions": scenario["actions"],
        "scores": {"outcome_value": 0.8, "risk_reduction": 0.6}
    }
    for scenario in scenarios
]

result = decision.make_decision({"task": "analysis"}, options)
```

### 场景3: 伦理约束检查

```python
from octopus.core import EthicsFramework

ethics = EthicsFramework()
guideline = ethics.create_default_guideline()
ethics.add_guideline(guideline)

# 检查行动
action = {
    "type": "data_access",
    "target": "user_records",
    "purpose": "marketing"
}

result = ethics.check_ethics(action, {"user_consent": False})

if result.decision.value == "approved":
    print("Proceed with action")
elif result.decision.value == "requires_review":
    print(f"Manual review needed: {result.review_reason}")
else:
    print("Action blocked")
```

## 配置

### 模拟配置

```python
from octopus.core import SimulationConfig

config = SimulationConfig(
    max_depth=10,
    uncertainty_level=0.05,
    risk_weight=0.5,
    reward_weight=0.5,
    enable_monte_carlo=True,
    monte_carlo_iterations=1000
)

simulation = SimulationEngine(config)
```

### 决策策略

```python
from octopus.core import DecisionPolicy, DecisionCriteria

policy = DecisionPolicy(
    policy_id="custom",
    name="Custom Policy",
    criteria=[
        DecisionCriteria("outcome_value", 0.50),
        DecisionCriteria("risk_reduction", 0.30),
        DecisionCriteria("reversibility", 0.20),
    ],
    hard_constraints=["no_data_loss"],
)

decision.add_policy(policy)
decision.set_active_policy("custom")
```

### 工具注册

```python
from octopus.execution import Tool, ToolMetadata, ToolCategory

metadata = ToolMetadata(
    tool_id="custom_tool",
    name="Custom Tool",
    description="My custom tool",
    category=ToolCategory.UTILITY,
)

tool = Tool(metadata)
tool.register_executor(lambda params: do_something(params))

execution.register_tool(tool)
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_core.py -v

# 运行集成测试
pytest tests/test_integration.py -v
```

## 性能监控

```python
# 获取系统状态
print(decision.get_decision_summary())
print(execution.get_execution_summary())
print(memory.get_statistics())
```

## 调试技巧

1. **启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查决策理由**:
```python
print(decision_result.reasoning)
```

3. **查看模拟结果**:
```python
print(f"Risk: {sim_result.risk_assessment}")
print(f"Success: {sim_result.success_metrics}")
```

4. **审计伦理检查**:
```python
print(ethics.get_audit_log(limit=10))
```

## 最佳实践

1. **分离关注点**: 决策层不直接执行工具
2. **状态管理**: 使用 World Model 维护一致性
3. **错误恢复**: 实现重试和回滚
4. **审计追踪**: 记录所有决策和执行
5. **性能监控**: 追踪关键指标
6. **安全检查**: 所有决策经过伦理审查

## 下一步

- 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解架构详情
- 阅读 [COMPONENTS.md](COMPONENTS.md) 查看组件规格
- 查看 [examples/](examples/) 获取更多示例
- 运行测试确保一切正常

## 支持

如有问题，请查看：
- GitHub Issues
- 文档中的故障排除部分
- 示例代码

祝你使用愉快！🎉
