# Octopus 项目综合说明书

**Octopus** 是一个基于 **决策-执行层分离架构 (Decision-Execution Separation)** 的 AI Agent 开发框架。它实现了大模型的"慢思考 (Slow Thinking)"与"快思考 (Fast Thinking)"双系统理论，旨在解决复杂商业场景下，Agent 因无序调用 API 而产生的死循环、高额 Token 消耗以及敏感操作缺乏安全边界的问题。

---

## 📦 版本

**v1.0.0** - 正式发布版本，包含完整的决策-执行层分离架构、多执行器集成、多LLM提供商支持、感知轮询、系统诊断工具和项目脚手架

---

## 🚀 快速开始

### 1. 环境准备
- **Python 版本要求**：Python >= 3.10
- **推荐方式 - 一键运行**：
  ```bash
  git clone https://github.com/WoWuuuuu/octupus.git
  cd octupus
  python run_octopus.py
  ```

### 2. 安装开发环境
```bash
pip install -e .
```

### 3. 运行示例
- **运行完整工作流演示**：
  ```bash
  python demo/full_workflow_demo.py
  ```
- **启动交互式CLI**：
  ```bash
  octopus shell
  ```

---

## 🛠️ 开发与测试指南

### 1. 运行测试套件
```bash
python -m pytest tests/ -v
```

### 2. 代码格式化与规范
- 格式化代码：`black .`
- 代码风格检查：`ruff check .`
- 静态类型检查：`mypy .`

---

## 📖 CLI 命令速查

通过 `python -m octopus.cli shell` 启动交互命令行后，可用以下指令：

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

### 其他命令
| 命令 | 说明 |
|------|------|
| `version` | 显示版本 |
| `help` | 显示帮助 |
| `exit` | 退出CLI |

---

## 📋 核心组件

### 决策层组件
- **WorldModel**: 世界状态建模
- **PerceptionModule**: 意图感知和解析
- **SimulationEngine**: 未来场景模拟
- **DecisionEngine**: 结构化决策制定
- **LongTermMemory**: 长期记忆系统
- **EthicsFramework**: 价值体系和伦理框架
- **DecisionCard**: 决策卡片渲染
- **DecisionComparator**: 决策比较功能
- **SessionStore**: 会话管理系统
- **ApprovalManager**: 批准机制

### 工作区感知模块
- **LocalWorkspacePerceiver**: 文件读取、目录扫描、内容搜索、Git操作、URL读取

### 通信协议
- **ODEP v1.0**: Octopus Decision Execution Protocol v1.0
- **JSON Schema Validation**: 消息格式验证
- **Transport Layer**: 传输层实现
- **Protocol Adapter**: v0/v1协议适配

### 执行器模块
- **ExecutorManager**: 执行器管理器
- **LocalExecutor**: 本地执行器
- **RemoteExecutor**: 远程执行器
- **DockerExecutor**: Docker执行器

### LLM提供商
- **LLMProviderManager**: LLM提供商管理器
- **OpenAIProvider**: OpenAI提供商
- **AnthropicProvider**: Anthropic提供商
- **GoogleProvider**: Google提供商

### 感知轮询
- **FileSystemPoller**: 文件系统变化检测
- **GitPoller**: Git仓库变化检测
- **WorkspacePoller**: 统一工作区轮询管理

### 辅助工具
- **Doctor**: 系统健康诊断工具
- **Quickstart**: 项目脚手架初始化

---

## 📁 项目结构

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

---

## 🎯 功能特性

### v0.1 - 基础架构
- 决策-执行层分离架构
- 核心组件定义

### v0.2 - 协议标准化
- ODEP v1.0协议规范
- JSON Schema验证
- 传输层实现
- 向后兼容性

### v0.3 - 核心能力
- 工作区只读感知模块
- 交互式CLI/TUI
- 决策卡片渲染

### v0.3.1 - 会话与批准
- 会话管理系统
- 批准机制
- 决策比较功能

### v0.4 - 扩展能力
- 多执行器集成（本地、远程、Docker）
- 多LLM提供商支持（OpenAI、Anthropic、Google）
- 感知轮询模式（文件系统、Git仓库变化检测）
- Doctor系统诊断工具
- Quickstart项目脚手架