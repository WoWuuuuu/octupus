# Octopus 项目综合说明书

**Octopus** 是一个基于 **决策-执行层分离架构 (Decision-Execution Separation)** 的 AI Agent 开发框架。它实现了大模型的“慢思考 (Slow Thinking)”与“快思考 (Fast Thinking)”双系统理论，旨在解决复杂商业场景下，Agent 因无序调用 API 而产生的死循环、高额 Token 消耗以及敏感操作缺乏安全边界的问题。

---

## 🚀 快速开始

### 1. 环境准备
项目核心库仅基于 Python 标准库实现，零外部运行时依赖。
- **Python 版本要求**：Python >= 3.10
- **安装开发依赖（可选，用于格式化和静态检查）**：
  ```bash
  pip install -e .[dev]
  ```

### 2. 运行简易示例
项目提供了无侵入的示例脚本，可以直接运行：
- **运行基础工作流 API 演示**：
  ```bash
  python demo/simple_workflow_demo.py
  ```
- **运行智能客服退款风控实战**：
  ```bash
  python demo/refund_agent_demo.py
  ```
- **启动对话式退款助手 (机器人交互)**：
  ```bash
  python demo/refund_chat_bot.py
  ```

---

## 🛠️ 开发与测试指南

### 1. 运行测试套件
项目测试已重构为模块化单元测试，使用 `pytest` 运行：
```bash
python -m pytest demo/tests/ -v
```

### 2. 代码格式化与规范
- 格式化代码：`black .`
- 代码风格检查：`ruff check .`
- 静态类型检查：`mypy .`

---

## 📖 常用指令速查 (CLI Tool)
通过 `python demo/run_cli.py` 启动交互命令行后，可用以下指令：
*   `status`：打印当前世界模型实体数、决策统计及记忆利用率。
*   `perceive <内容>`：测试感知层提取的意图和实体。
*   `decide <场景>`：输入决策上下文，自动基于预设方案及权重进行推理选择。
*   `memory`：查询长期记忆库中存储的历史操作结果。
