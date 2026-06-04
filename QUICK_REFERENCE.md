# 🎯 Octopus 项目 - 快速参考卡

## 📍 项目位置

**新路径**: `D:\workspace\Octopus`

---

## 🎯 核心数据模型

### TaskRequest（Brain → Tentacle）

```python
from octopus.models.core_models import create_task_request

task = create_task_request(
    task_id="task_001",
    tool_id="web_scraper",
    parameters={"url": "https://example.com"},
    priority="normal"
)
```

### Plan（Brain 的输出）

```python
from octopus.models.core_models import (
    create_plan, ExecutionStep, StepDependency
)

plan = create_plan(
    plan_id="plan_001",
    objective="分析竞品价格",
    reasoning="需要先抓取数据，再进行分析",
    steps=[
        ExecutionStep(
            step_id="scrape",
            order=0,
            tool_id="web_scraper",
            description="抓取网站",
            parameters={"urls": ["site1.com"]}
        ),
        ExecutionStep(
            step_id="analyze",
            order=1,
            tool_id="data_processor",
            description="分析数据",
            parameters={"method": "statistical"},
            dependencies=StepDependency(depends_on=["scrape"])
        )
    ]
)
```

### ToolResult（Tentacle → Brain）

```python
from octopus.models.core_models import create_tool_result

result = create_tool_result(
    tool_id="web_scraper",
    task_id="task_001",
    status="completed",
    output={"prices": ["$10", "$20"]},
    execution_time_ms=1234.5,
    logs=["Connected", "Scraped", "Done"]
)
```

---

## 📁 核心文件

| 文件 | 作用 |
|------|------|
| `octopus/models/core_models.py` | Pydantic 数据模型定义 |
| `octopus/core/decision_engine.py` | 决策引擎 |
| `octopus/execution/executor.py` | 执行层 |
| `octopus/protocol/communication.py` | 通信协议 |

---

## 📚 关键文档

| 文档 | 作用 |
|------|------|
| `DEVELOPMENT_GUIDE.md` | 开发指南 |
| `docs/CODEX_COLLABORATION.md` | Codex 协作指南 |
| `docs/PYDANTIC_MODELS.md` | Pydantic 模型详解 |
| `docs/DATA_MODELS.md` | 数据模型可视化 |
| `docs/ARCHITECTURE.md` | 完整架构文档 |

---

## 🔧 与 Codex 协同开发

### 步骤 1：锁定架构

把以下内容放入 Cursor Rules：

```markdown
# Project Octopus Rules

## 核心原则
- Brain：只思考，不执行工具
- Tentacle：只执行，不决策
- 禁止 Monolith

## 必须使用 Pydantic 模型
所有通信使用 octopus.models.core_models
```

### 步骤 2：定义数据结构 ✅ 已完成

```python
from octopus.models.core_models import (
    TaskRequest, Plan, ToolResult
)
```

### 步骤 3：写大脑 ⬜ 待实现

文件：`octopus/brain/`

### 步骤 4：接触手 ⬜ 待实现

文件：`octopus/tentacles/`

---

## 🚀 快速开始

```bash
# 安装
cd D:\workspace\Octopus
pip install -e .

# 运行示例
python examples/full_workflow.py

# 使用 CLI
python -m octopus.cli

# 运行测试
python -m pytest tests/ -v
```

---

## 💡 核心概念

### 决策层（Slow Thinking）

- **感知**：理解输入和上下文
- **模拟**：探索可能的未来
- **决策**：选择最优方案
- **记忆**：记住经验

### 执行层（Fast Thinking）

- **接收**：TaskRequest
- **执行**：调用工具
- **返回**：ToolResult
- **日志**：记录所有操作

---

## 📊 数据流

```
User → Brain → Plan → TaskRequest → Tentacle → ToolResult → Brain → Output
```

---

## ⚙️ 配置

### 安装依赖

```toml
# pyproject.toml
dependencies = [
    "pydantic>=2.0",
    # ... 其他依赖
]
```

---

## 🎓 学习资源

1. **项目结构**: `D:\workspace\Octopus\docs\ARCHITECTURE.md`
2. **Codex 指南**: `D:\workspace\Octopus\docs\CODEX_COLLABORATION.md`
3. **数据模型**: `D:\workspace\Octopus\docs\PYDANTIC_MODELS.md`
4. **示例代码**: `D:\workspace\Octopus\examples\`

---

**状态**: ✅ 基础架构完成  
**下一步**: 与 Codex 协同开发 Decision Brain

---

🎉 **开始你的 Octopus 开发之旅！**
