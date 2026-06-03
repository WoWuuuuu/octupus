# Octopus - Decision-Execution Layer Separation Architecture

**Octopus** 是一个决策-执行层分离系统。系统名称象征性地代表了"头"（决策层）和"触手"（执行层）的分离。

## 核心架构

### 决策层（Slow Thinking - 缓慢思考）

- **World Model**: 世界状态建模
- **Perception Module**: 意图感知和解析
- **Simulation Engine**: 未来场景模拟
- **Decision Engine**: 结构化决策制定
- **Long-Term Memory**: 长期记忆系统
- **Ethics Framework**: 价值体系和伦理框架

### 执行层（Fast Thinking - 快速思考）

- **Tool Registry**: 工具注册和管理
- **Execution Layer**: 纯工具执行
- **ODEP Protocol**: 层间通信协议

## 快速开始

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

在CLI中你可以使用以下命令：

- `status` - 查看系统状态
- `perceive <input>` - 处理输入
- `decide <context>` - 做决策
- `execute <intent>` - 执行意图
- `memory` - 查看记忆
- `help` - 显示帮助

## 核心组件

### 决策层

```python
from octopus.core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    LongTermMemory,
    EthicsFramework,
)

world_model = WorldModel()
perception = PerceptionModule()
simulation = SimulationEngine()
decision = DecisionEngine()
memory = LongTermMemory()
ethics = EthicsFramework()

decision.set_world_model(world_model)
decision.set_simulation_engine(simulation)
```

### 执行层

```python
from octopus.execution import ExecutionLayer, ToolRegistry

registry = ToolRegistry()
execution = ExecutionLayer()

for tool_id, tool in registry.tools.items():
    execution.register_tool(tool)

result = execution.execute_single("tool_id", {"param": "value"})
```

### 通信协议

```python
from octopus.protocol import ODEPProtocol, ExecutionIntent, Priority

protocol = ODEPProtocol()

intent = ExecutionIntent(
    intent_id="intent_1",
    action_type="example",
    parameters={"key": "value"},
    priority=Priority.NORMAL,
)

message = protocol.send_execute_request("decision", "execution", intent)
```

## 架构优势

1. **消除信息噪音** - 避免无序的工具调用
2. **防止逻辑冲突** - 自主操作中的决策一致性
3. **真正的业务决策能力** - 结构化的决策过程
4. **长期规划功能** - 模拟和记忆系统支持

## 项目结构

```
octopus/
├── core/                    # 决策层核心组件
│   ├── world_model.py      # 世界模型
│   ├── perception.py       # 感知模块
│   ├── simulation.py       # 模拟引擎
│   ├── decision_engine.py  # 决策引擎
│   ├── memory.py           # 长期记忆
│   └── ethics.py          # 伦理框架
├── execution/              # 执行层组件
│   ├── tools.py           # 工具注册表
│   └── executor.py        # 执行层
├── protocol/              # 通信协议
│   └── communication.py   # ODEP协议
├── cli.py                 # 命令行界面
└── __init__.py           # 包初始化
```

## 示例

查看 `examples/full_workflow.py` 了解完整的工作流程演示。

## 许可证

MIT License
