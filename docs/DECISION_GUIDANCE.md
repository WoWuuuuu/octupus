# Decision Guidance (decision.md)

## 这是什么

`decision.md` 是 Octopus 的**决策指导文件**。

它用人类可读的 Markdown，声明「决策应该如何被评价和选择」：

- 这次决策要优化什么（Primary Objective）
- 各项评价标准占多大权重（Preferences / Weights）
- 哪些是绝对不可违反的硬约束（Hard Constraints）
- 冲突时怎么取舍（Trade-off Rules）

Octopus 在做决策时会读取它，用其中的权重来打分排序，并把完整指导注入到 LLM 决策提示里。

## 它不是什么

`decision.md` **不是**：

- 记忆存储
- 事件日志
- 对话历史
- 执行脚本
- 工具编排计划
- 权限配置文件

它只描述决策标准，不记录发生过什么，也不赋予任何执行权限。

## 存放位置

按优先级查找：

1. `<workspace>/.octopus/decision.md`（推荐）
2. `<workspace>/decision.md`

## 文件结构

| 章节 | 是否影响运行时 | 作用 |
|------|--------------|------|
| Decision Scope | 否（元信息） | 说明适用范围 |
| **Primary Objective** | ✅ 是 | 主导优化目标 |
| Secondary Objectives | ✅ 是 | 次级目标 |
| **Preferences / Weights** | ✅ 是 | 评分维度与权重 |
| **Hard Constraints** | ✅ 是 | 违反即淘汰 |
| **Trade-off Rules** | ✅ 是 | 取舍规则 |
| Decision Principles | 否（暂不生效） | 决策原则 |
| Evaluation Criteria | 否（暂不生效） | 评价标准说明 |
| Reflection Guidance | 否（暂不生效） | 复盘问题 |

> 「运行时生效」指的是这些章节会被映射成决策策略并参与打分；其余章节会被解析、展示，但当前版本还不参与计算。

## 用法

### 1. 生成模板

```bash
octopus decision init
```

会写入 `.octopus/decision.md`。已存在时需加 `--force` 覆盖：

```bash
octopus decision init --force
```

### 2. 查看与校验

```bash
octopus decision show
```

会打印当前加载的指导、权重表、硬约束，并给出校验结果（例如权重总和是否为 1.00）。

### 3. 在代码中使用

```python
from core.decision_engine import DecisionEngine
from core.decision_guidance import load_decision_guidance

engine = DecisionEngine()

guidance = load_decision_guidance()          # 自动查找 .octopus/decision.md
if guidance:
    engine.set_decision_guidance(guidance)   # 权重会变成生效策略，并注入 LLM 提示

decision = engine.make_decision(context, options)
```

## 示例

```md
# decision.md

Schema Version: 0.1
Artifact Type: Decision Guidance

## Primary Objective

```md
Primary Objective:
让「决策-执行层分离」这一核心价值可被验证。
```

## Preferences / Weights

```md
- outcome_value: 0.35
- risk_reduction: 0.25
- reversibility: 0.20
- confidence_alignment: 0.20
```

## Hard Constraints

```md
- 不得破坏 ODEP v1.0 的向后兼容
```
```

## 校验规则

`octopus decision show` 会检查并给出提示：

- 缺少 Primary Objective
- 缺少 Preferences / Weights（会退回默认评价标准）
- 权重总和不在 1.00 附近
- 未声明任何 Hard Constraints
