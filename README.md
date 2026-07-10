# Octopus - Decision-Execution Layer Separation Architecture

**Octopus** 是一个决策-执行层分离系统。系统名称象征性地代表了"头"（决策层）和"触手"（执行层）的分离。

## 📦 版本

**v0.4** - 完成阶段三：多执行器集成、多LLM提供商支持、感知轮询、系统诊断工具、项目脚手架

## 核心架构

### 决策层（Slow Thinking - 缓慢思考）
- **World Model**: 世界状态建模
- **Perception Module**: 意图感知和解析
- **Simulation Engine**: 未来场景模拟
- **Decision Engine**: 结构化决策制定
- **Long-Term Memory**: 长期记忆系统
- **Ethics Framework**: 价值体系和伦理框架
- **Session Management**: 会话管理系统
- **Approval Mechanism**: 批准机制
- **Decision Card**: 决策卡片渲染
- **Decision Comparator**: 决策比较功能

### 执行层（Fast Thinking - 快速思考）
- **Tool Registry**: 工具注册和管理
- **Execution Layer**: 纯工具执行
- **ODEP Protocol**: 层间通信协议
- **Executors**: 多执行器支持（本地、远程、Docker）
- **LLM Providers**: 多LLM提供商支持（OpenAI、Anthropic、Google）

### 通信协议
- **ODEP v1.0**: Octopus Decision Execution Protocol v1.0
- **JSON Schema Validation**: 消息格式验证
- **Transport Layer**: 支持 stdin/stdout、HTTP、消息队列、RPC
- **Backward Compatibility**: v0/v1 协议适配

### 工作区感知
- **File Reading**: 文件读取
- **Directory Scanning**: 目录结构扫描
- **Content Search**: 内容搜索
- **Git Operations**: Git 状态、差异、日志
- **URL Reading**: 网页内容提取
- **Budget Control**: 文件访问预算控制

### 感知轮询
- **File System Polling**: 文件系统变化检测
- **Git Polling**: Git 仓库变化检测
- **WorkSpace Poller**: 统一工作区轮询管理
- **Change History**: 变化历史记录与回调

### 辅助工具
- **Doctor**: 系统健康诊断工具
- **Quickstart**: 项目脚手架初始化

## 快速开始

### 安装

```bash
pip install -e .
```

### 运行示例

```bash
python demo/full_workflow_demo.py
```

### 使用CLI

```bash
python -m octopus.cli shell
```

## CLI 命令

### 文件操作
| 命令 | 说明 |
|------|------|
| `read <file_path>` | 读取文件内容 |
| `ls [depth]` | 列出目录结构 |
| `search <query>` | 搜索文件内容 |

### Git 操作
| 命令 | 说明 |
|------|------|
| `git status` | 查看Git状态 |
| `git diff [file_path]` | 查看Git差异 |
| `git log [limit]` | 查看Git日志 |

### 决策操作
| 命令 | 说明 |
|------|------|
| `decide <goal>` | 做出决策 |
| `compare <goal1> <goal2> [...]` | 对比多个决策 |

### 会话管理
| 命令 | 说明 |
|------|------|
| `session create <title> [description]` | 创建会话 |
| `session list` | 列出所有会话 |
| `session show <session_id>` | 显示会话详情 |
| `session switch <session_id>` | 切换会话 |
| `session archive <session_id>` | 归档会话 |
| `session search <query>` | 搜索会话 |
| `session current` | 显示当前会话 |

### 批准管理
| 命令 | 说明 |
|------|------|
| `approval list` | 列出所有批准 |
| `approval pending` | 列出待批准 |
| `approval approve <approval_id> [reason]` | 批准 |
| `approval reject <approval_id> [reason]` | 拒绝 |
| `approval create <decision_id> <summary> [level]` | 创建批准请求 |
| `approval stats` | 批准统计 |

### 执行器管理
| 命令 | 说明 |
|------|------|
| `executor list` | 列出所有执行器 |
| `executor status <executor_id>` | 查看执行器状态 |
| `executor health` | 执行器健康检查 |
| `executor default <executor_id>` | 设置默认执行器 |

### 系统诊断
| 命令 | 说明 |
|------|------|
| `doctor run` | 运行系统健康检查 |
| `doctor summary` | 查看诊断摘要 |

### 项目脚手架
| 命令 | 说明 |
|------|------|
| `quickstart list` | 列出项目模板 |
| `quickstart create <name> [template]` | 创建新项目 |

### 其他命令
| 命令 | 说明 |
|------|------|
| `version` | 显示版本 |
| `help` | 显示帮助 |
| `exit` | 退出CLI |

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
    DecisionCard,
    DecisionCardRenderer,
    DecisionComparator,
    Session,
    SessionStore,
    ApprovalManager,
)

# 执行器
from octopus.execution.executors import (
    ExecutorManager,
    LocalExecutor,
    RemoteExecutor,
    DockerExecutor,
)

# LLM提供商
from octopus.core.llm_provider import (
    LLMProviderManager,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
)

world_model = WorldModel()
perception = PerceptionModule()
simulation = SimulationEngine()
decision = DecisionEngine()
memory = LongTermMemory()
ethics = EthicsFramework()
renderer = DecisionCardRenderer()
comparator = DecisionComparator()
session_store = SessionStore()
approval_manager = ApprovalManager()
```

### 工作区感知

```python
from perception import LocalWorkspacePerceiver

perceiver = LocalWorkspacePerceiver()

# 读取文件
result = perceiver.read_file("README.md")

# 目录扫描
result = perceiver.repo_map(depth=3)

# 搜索内容
result = perceiver.search("ODEP")

# Git状态
result = perceiver.git_status()
```

### 通信协议

```python
from protocol.v1.messages import ExecutionIntent, ExecutionResult
from protocol.v1.enums import Priority

intent = ExecutionIntent(
    intent_id="intent_1",
    action_type="example",
    parameters={"key": "value"},
    priority=Priority.NORMAL,
)

from protocol.v1.validators import validate_execution_intent
validate_execution_intent(intent.to_dict())
```

## 架构优势

1. **消除信息噪音** - 避免无序的工具调用
2. **防止逻辑冲突** - 自主操作中的决策一致性
3. **真正的业务决策能力** - 结构化的决策过程
4. **长期规划功能** - 模拟和记忆系统支持
5. **可追踪性** - 会话管理和批准机制
6. **决策对比** - 多决策比较和优化

## 项目结构

```
octopus/
├── core/                    # 决策层核心组件
│   ├── world_model.py      # 世界模型
│   ├── perception.py       # 感知模块
│   ├── simulation.py       # 模拟引擎
│   ├── decision_engine.py  # 决策引擎
│   ├── memory.py           # 长期记忆
│   ├── ethics.py          # 伦理框架
│   ├── decision_card.py   # 决策卡片渲染
│   ├── session.py         # 会话管理系统
│   ├── approval.py        # 批准机制
│   └── llm_provider.py    # LLM提供商抽象与实现
├── perception/             # 工作区感知模块
│   ├── __init__.py
│   ├── workspace.py       # 工作区感知实现
│   └── poller.py          # 感知轮询模块
├── execution/             # 执行器模块
│   ├── __init__.py
│   ├── base.py            # 执行器抽象接口
│   └── executors.py       # 多种执行器实现
├── protocol/              # 通信协议
│   ├── __init__.py
│   └── v1/                # ODEP v1.0协议
│       ├── __init__.py
│       ├── enums.py       # 消息类型枚举
│       ├── messages.py    # 消息数据类
│       ├── validators.py  # JSON Schema验证
│       ├── transport.py   # 传输层实现
│       └── adapters.py    # v0/v1适配器
├── octopus/               # CLI框架
│   ├── __init__.py
│   ├── cli.py            # 命令行界面
│   ├── doctor.py         # 系统诊断工具
│   └── quickstart.py     # 项目脚手架
├── demo/                  # 示例脚本
├── tests/                 # 测试用例
├── docs/                  # 文档
└── config/                # 配置文件
```

## 测试

运行所有测试：

```bash
python -m pytest tests/ -v
```

## 许可证

MIT License