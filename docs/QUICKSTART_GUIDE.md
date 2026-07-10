# Octopus v1.0.0 入门指引

欢迎使用 Octopus！这是一份详细的入门指南，帮助你从零开始使用 Octopus 决策-执行层分离系统。

---

## 📋 目录

1. [环境准备](#1-环境准备)
2. [安装 Octopus](#2-安装-octopus)
3. [一键运行体验](#3-一键运行体验)
4. [交互式 CLI 指南](#4-交互式-cli-指南)
5. [核心功能演示](#5-核心功能演示)
6. [常见问题](#6-常见问题)

---

## 1. 环境准备

### 1.1 检查 Python 版本

Octopus 需要 Python 3.10 或更高版本。请先检查你的 Python 版本：

```bash
python --version
# 或
python3 --version
```

**输出示例**：
```
Python 3.11.5
```

如果你的 Python 版本低于 3.10，请先升级 Python。

### 1.2 安装 Git（可选）

如果你想通过 Git 克隆项目，请确保已安装 Git：

```bash
git --version
```

---

## 2. 安装 Octopus

### 方式一：使用 Git 克隆（推荐）

```bash
# 克隆项目
git clone https://github.com/WoWuuuuu/octupus.git

# 进入项目目录
cd octupus
```

### 方式二：下载 ZIP 包

1. 访问 GitHub 仓库：https://github.com/WoWuuuuu/octupus
2. 点击 "Code" 按钮，选择 "Download ZIP"
3. 解压到本地目录

### 安装依赖

```bash
# 使用 pip 安装开发模式
pip install -e .

# 安装后验证
pip show octopus
```

**输出示例**：
```
Name: octopus
Version: 1.0.0
Summary: Octopus - Decision-Execution Layer Separation Architecture
Home-page: https://github.com/WoWuuuuu/octupus
```

---

## 3. 一键运行体验

Octopus 提供了 `run_octopus.py` 脚本，让你无需任何配置即可体验完整功能：

```bash
python run_octopus.py
```

运行后你将看到：

```
========================================
         Octopus v1.0.0
   决策-执行层分离系统
========================================

正在初始化系统...

✅ 工作区感知模块已就绪
✅ 决策引擎已启动
✅ 会话管理系统已加载
✅ 批准机制已激活
✅ 执行器管理器已初始化
✅ LLM提供商管理器已就绪
✅ 感知轮询系统已准备
✅ Doctor诊断工具已就绪
✅ Quickstart脚手架已可用

========================================
             功能菜单
========================================

1. 🖥️  启动交互式 CLI
2. 👁️  演示工作区感知
3. ⚖️  演示决策引擎
4. 📝  演示会话管理
5. 🔑  演示批准机制
6. 🚀  演示执行器
7. 👨‍⚕️  运行系统诊断
8. 📁  使用项目脚手架
9. ❌  退出

请选择功能 (1-9):
```

选择数字即可体验相应功能！

---

## 4. 交互式 CLI 指南

### 4.1 启动 CLI

```bash
octopus shell
```

或

```bash
python -m octopus.cli shell
```

### 4.2 CLI 界面

```
╭─────────────────────────────────────────────────────────────╮
│                      Welcome                                │
│  Octopus Interactive Shell                                 │
│  Type 'help' for available commands                        │
│  Type 'exit' to quit                                       │
╰─────────────────────────────────────────────────────────────╯

octopus>
```

### 4.3 常用命令

#### 文件操作

```bash
# 读取文件
octopus> read README.md

# 列出目录结构
octopus> ls 3

# 搜索文件内容
octopus> search ODEP
```

#### Git 操作

```bash
# 查看 Git 状态
octopus> git status

# 查看 Git 差异
octopus> git diff

# 查看 Git 日志
octopus> git log 5
```

#### 决策操作

```bash
# 做出决策
octopus> decide 我周末应该去公园还是看电影

# 对比多个决策
octopus> compare 去公园 看电影 学习
```

#### 会话管理

```bash
# 创建会话
octopus> session create 周末计划 讨论周末的活动安排

# 列出所有会话
octopus> session list

# 查看当前会话
octopus> session current

# 切换会话
octopus> session switch <session_id>

# 搜索会话
octopus> session search 周末
```

#### 批准管理

```bash
# 创建批准请求
octopus> approval create decision_1 重要决策 high

# 列出待批准
octopus> approval pending

# 批准
octopus> approval approve <approval_id> 同意执行

# 拒绝
octopus> approval reject <approval_id> 需要进一步评估
```

#### 系统诊断

```bash
# 运行系统诊断
octopus> doctor run

# 查看诊断摘要
octopus> doctor summary
```

#### 项目脚手架

```bash
# 列出项目模板
octopus> quickstart list

# 创建新项目
octopus> quickstart create my_project basic
```

### 4.4 命令帮助

输入 `help` 查看所有可用命令：

```bash
octopus> help
```

---

## 5. 核心功能演示

### 5.1 工作区感知演示

```bash
# 查看项目目录结构
octopus> ls 2

# 读取配置文件
octopus> read config/application.yml

# 搜索关键词
octopus> search decision
```

### 5.2 决策引擎演示

```bash
# 让系统帮你做决策
octopus> decide 我应该选择哪个编程语言学习

# 系统会输出决策卡片，包含：
# - 选项列表
# - 各选项评分
# - 推荐选择
# - 决策理由
```

### 5.3 会话管理演示

```bash
# 创建一个会话
octopus> session create 学习计划 制定本周学习计划

# 查看会话列表
octopus> session list

# 创建另一个会话
octopus> session create 项目开发 讨论新项目开发方案

# 切换会话
octopus> session switch <session_id>
```

### 5.4 批准机制演示

```bash
# 创建一个高优先级批准请求
octopus> approval create my_decision 部署生产环境 critical

# 查看待批准列表
octopus> approval pending

# 批准该请求
octopus> approval approve <approval_id> 已完成代码审查
```

### 5.5 系统诊断演示

```bash
# 运行完整诊断
octopus> doctor run

# 系统会检查：
# - 系统环境（Python版本、操作系统）
# - 依赖包状态
# - 配置文件
# - 网络连接
```

---

## 6. 常见问题

### Q1: 运行时提示缺少依赖？

```bash
# 重新安装依赖
pip install -e .
```

### Q2: CLI 命令无法识别？

确保已安装在开发模式：
```bash
pip install -e .

# 验证安装
octopus --help
```

### Q3: 如何退出交互式 CLI？

```bash
octopus> exit
```

或使用快捷键 `Ctrl+C`

### Q4: 会话数据保存在哪里？

会话数据默认保存在 `~/.octopus/sessions/` 目录下。

### Q5: 如何配置 LLM 提供商？

复制 `.env.example` 文件并配置 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API 密钥：

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

### Q6: 运行测试？

```bash
python -m pytest tests/ -v
```

---

## 📚 更多资源

- **项目主页**：https://github.com/WoWuuuuu/octupus
- **架构文档**：[ARCHITECTURE.md](ARCHITECTURE.md)
- **组件规格**：[COMPONENTS.md](COMPONENTS.md)
- **协议规范**：[ODEP_V1_SPEC.md](ODEP_V1_SPEC.md)

---

## 📞 反馈

如果你遇到问题或有建议，欢迎在 GitHub 上提交 Issue！

---

**Octopus v1.0.0** | 决策-执行层分离系统
