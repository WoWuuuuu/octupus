# CLI Agent Harness

## 什么是 harness

**harness（驱动层）是套在外部 Agent 外面的那层"驾驶舱"。**

外部 Agent（Claude Code、Codex、Hermes、OpenClaw……）本身是个黑盒：你不知道它内部怎么思考，也不该去改它。Octopus 想用它，只需要能**安全地把它开起来、把任务交给它、把结果收回来**——这一层就是 harness。

> 类比：Agent 是一台发动机，harness 是方向盘 + 仪表盘 + 安全带。发动机不用改，但你得能控制它、看见它的状态、出事时能急停。

## 它解决什么问题

Octopus 是"决策-执行分离"架构：

- **决策层**负责"该做什么"（已经做完，产出执行意图）
- **执行层**负责"把它做掉"

`Local / Remote / Docker` 这几种执行器只会跑**你写死的命令**。要让 Claude Code 这类**会自己思考的 Agent** 去干活，中间必须有一层翻译与管控——这就是 harness 的位置。

harness **不参与决策**。它拿到的是一个已经决定好的任务，只负责把它送出去、收回来。

## 工作原理

一次调用分五步：

```text
1. 选 Profile      →  决定用哪个 Agent、命令行长什么样
2. 组装命令        →  按该 Agent 的习惯拼参数（提示词走参数还是走 stdin）
3. 执行（可拦截）  →  受超时保护；dry_run 时到此为止，不真的跑
4. 捕获结果        →  stdout / stderr / 退出码 / 耗时
5. 归一化状态      →  产出两级状态
```

### 两级状态（重要）

真实世界里"没跑起来"和"跑了但没办成"是两回事，所以分开报告：

| 层级 | 字段 | 含义 | 取值 |
|------|------|------|------|
| 协议层 | `protocol_status` | harness 有没有成功把任务送出去并拿回响应 | `success` / `failed` / `timeout` / `not_found` / `dry_run` |
| 任务层 | `task_status` | Agent 到底有没有把事办成 | `success` / `failed` / `not_started` |

例如：

- `protocol_status=not_found` → 本机根本没装这个 Agent，任务压根没开始
- `protocol_status=success, task_status=failed` → 命令跑起来了，但 Agent 返回了非零退出码

## 内置 Agent

| agent_id | 命令 | 说明 |
|----------|------|------|
| `claude_code` | `claude -p <prompt>` | Claude Code 非交互模式 |
| `codex` | `codex exec <prompt>` | Codex 非交互模式 |

> 这两个命令行是按常见安装方式预设的，**请按你本机的实际版本调整**。用 `octopus agent list` 可以看本机是否装了。

### 自定义 Agent

```python
from execution.harness import AgentProfile, CliAgentHarness

harness = CliAgentHarness()
harness.register_profile(AgentProfile(
    agent_id="my_agent",
    name="My Agent",
    command=["my-agent", "run"],
    prompt_mode="arg",        # 或 "stdin"
))
```

## 用法

### CLI

```bash
# 看有哪些 Agent、本机装了没
octopus agent list

# 默认是 dry-run：只拼命令，不真执行
octopus agent run claude_code "把 README 里的错别字修一下"

# 真正执行（需要显式加 --execute）
octopus agent run claude_code "把 README 里的错别字修一下" --execute
```

### Python

```python
from execution.harness import CliAgentHarness

harness = CliAgentHarness()

# 只演练
plan = harness.run("claude_code", "修 README 错别字")
print(plan.command)

# 真跑
result = harness.run("claude_code", "修 README 错别字", dry_run=False, timeout_seconds=120)
print(result.protocol_status, result.task_status, result.stdout)
```

### 走执行器接口

```python
from execution.executors import ExecutorManager

manager = ExecutorManager()
manager.create_agent_executor("agent_1")

job = manager.execute(
    "agent_run",
    {"agent_id": "claude_code", "prompt": "修 README 错别字", "dry_run": False},
    executor_id="agent_1",
)
print(job.result)
```

## 安全默认

`agent_run` 和 `harness.run()` **默认 `dry_run=True`**。

理由：让一个会自己思考的 Agent 在你的仓库里动手，是有副作用的操作。按照 Octopus「执行前需批准」的原则，真实执行必须由调用方**显式开启**。

## 限制与注意事项

1. **只做进程级驱动，不做沙箱隔离。** harness 用子进程方式调用 Agent，Agent 能碰到的文件它都能碰。要更强隔离，应该把 Agent 跑在 Docker/远程环境里，而不是指望 harness 兜底。
2. **Agent 的命令行参数各不相同。** 内置的 `claude -p` / `codex exec` 只是常见形态，版本一变就可能失效；上生产前务必实测。
3. **输出是文本，不是结构化数据。** 目前只做截断（默认 20000 字符）和原样返回。要解析 Agent 的结构化结果，需要该 Agent 支持 JSON 输出模式。
4. **无法中途干预。** `cancel_job` 只能标记任务状态，**杀不掉已经在跑的进程**；超时是唯一的强制中断手段。
5. **不做鉴权与配额。** API key、模型、并发上限都由 Agent 自己管，harness 不介入。
6. **一次调用一个 Agent。** 不做多 Agent 编排、重试策略、结果合并——那是更上层的事。
7. **不记录完整会话。** 只留 stdout/stderr 和状态；Agent 的中间思考过程不保留。
