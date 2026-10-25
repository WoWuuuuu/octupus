# decision.md

Status: Active
Schema Version: 0.1
Artifact Type: Decision Guidance

本文件是 Octopus 项目自身的决策指导。它声明 Octopus 在「决定下一步做什么」时，
应该优化什么、各项标准占多大权重、哪些是硬约束、以及发生冲突时如何取舍。

它只描述「决策应该如何被评价和选择」，不记录历史、不存记忆、不执行动作。

## Decision Scope

```md
Domain: octopus_project_evolution
Decision Class: next_capability_prioritization
Applies To: 决定 Octopus 下一步优先建设哪项能力
Does Not Apply To: 线上事故应急、已经排期的既定任务
Authority: default_policy_guidance
```

## Primary Objective

```md
Primary Objective:
让「决策-执行层分离」这一核心价值可被验证，而不是单纯堆功能。
```

## Secondary Objectives

```md
- 提升决策的可审计性：每个决策都能说清依据
- 降低对外部执行器的耦合
- 保持 ODEP 协议向后兼容
- 控制新增的复杂度
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
- 不得让决策层直接执行动作
```

## Trade-off Rules

```md
- 当「新能力」与「稳定性」冲突时，优先稳定性
- 当「收益」与「可逆性」冲突时，优先可逆性
```

## Decision Principles

```md
- 先可观测，再可优化
- 决策依据必须可回溯
```

## Evaluation Criteria

```md
- 是否提升了决策质量，而不仅仅是增加了功能
```

## Reflection Guidance

```md
- 这次决策真的解决了最初的问题吗？
- 有没有更小的、可逆的方案？
```
