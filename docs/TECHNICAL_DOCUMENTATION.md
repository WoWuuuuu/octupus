# Octopus v1.0.0 技术文档

> **文档版本**: v1.0.0\
> **最后更新**: 2026-08-11\
> **项目状态**: 生产就绪

***

## 目录

1. [项目架构设计](#1-项目架构设计)
2. [运行原理](#2-运行原理)
3. [业务流程](#3-业务流程)
4. [参数流转](#4-参数流转)
5. [AI功能应用](#5-ai功能应用)

***

## 1. 项目架构设计

### 1.1 整体架构图

Octopus 采用**决策-执行层分离架构**，基于"慢思考-快思考"双系统理论：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           用户交互层 (User Layer)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│   CLI/TUI (Rich + prompt_toolkit) │ API 接口 │ Demo 脚本                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         决策层 (Decision Layer) - 慢思考                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │WorldModel│ │Perception│ │Simulation│ │Decision  │ │ Ethics   │          │
│  │          │ │ Module   │ │  Engine  │ │ Engine   │ │Framework │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │LongTerm  │ │  Session │ │Approval  │ │Decision  │                        │
│  │ Memory   │ │  Store   │ │ Manager  │ │Card Render│                        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                      │
│  │Workspace │ │  Poller  │ │  Doctor  │                                      │
│  │Perceiver │ │  Module  │ │  Module  │                                      │
│  └──────────┘ └──────────┘ └──────────┘                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                         通信层 (Communication Layer)                         │
│              ODEP v1.0 Protocol │ JSON Schema Validator │ Transport         │
├─────────────────────────────────────────────────────────────────────────────┤
│                         执行层 (Execution Layer) - 快思考                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │  Local   │ │ Remote   │ │  Docker  │ │ Tool     │                        │
│  │ Executor │ │ Executor │ │ Executor │ │ Registry │                        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘                        │
│  ┌──────────────────────────────────┐                                        │
│  │      LLM Providers Manager       │                                        │
│  │  OpenAI │ Anthropic │ Google     │                                        │
│  └──────────────────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈选型

| 层次        | 技术              | 版本     | 说明             |
| --------- | --------------- | ------ | -------------- |
| **语言**    | Python          | ≥ 3.10 | 主开发语言          |
| **CLI框架** | prompt\_toolkit | ≥ 3.0  | 交互式命令行         |
| **渲染引擎**  | *Rich*          | ≥ 13.0 | 终端富文本渲染        |
| **AI框架**  | openai          | ≥ 1.0  | LLM API 调用     |
| **AI框架**  | python-dotenv   | ≥ 1.0  | 环境变量管理         |
| **网络**    | requests        | ≥ 2.31 | HTTP 请求        |
| **配置**    | pyyaml          | ≥ 6.0  | YAML 配置解析      |
| **版本控制**  | gitpython       | ≥ 3.1  | Git 仓库操作       |
| **测试**    | pytest          | ≥ 7.0  | 单元测试框架         |
| **验证**    | jsonschema      | ≥ 4.0  | JSON Schema 验证 |

### 1.3 核心模块划分

#### 决策层模块

| 模块     | 文件路径                      | 职责          | 关键类                                          |
| ------ | ------------------------- | ----------- | -------------------------------------------- |
| 世界模型   | `core/world_model.py`     | 全局状态管理、快照备份 | `WorldModel`, `Entity`, `StateSnapshot`      |
| 感知模块   | `core/perception.py`      | 意图提取、信号解析   | `PerceptionModule`, `Intent`                 |
| 模拟引擎   | `core/simulation.py`      | 场景预演、风险评估   | `SimulationEngine`, `Scenario`               |
| 决策引擎   | `core/decision_engine.py` | 多标准打分、决策制定  | `DecisionEngine`, `DecisionPolicy`           |
| 伦理框架   | `core/ethics.py`          | 风控审核、价值判断   | `EthicsFramework`, `EthicalRule`             |
| 长期记忆   | `core/memory.py`          | 经验存储、语义检索   | `LongTermMemory`, `MemoryItem`               |
| 会话管理   | `core/session.py`         | 会话生命周期管理    | `SessionStore`, `Session`                    |
| 批准机制   | `core/approval.py`        | 多级审批流程      | `ApprovalManager`, `ApprovalTask`            |
| 决策卡片   | `core/decision_card.py`   | 决策可视化渲染     | `DecisionCardRenderer`, `DecisionComparator` |
| LLM提供商 | `core/llm_provider.py`    | 多LLM接口抽象    | `LLMProviderManager`, `BaseLLMProvider`      |

#### 执行层模块

| 模块        | 文件路径                     | 职责       | 关键类                              |
| --------- | ------------------------ | -------- | -------------------------------- |
| 执行器基类     | `execution/base.py`      | 执行器接口定义  | `BaseExecutor`, `ExecutorConfig` |
| 本地执行器     | `execution/executors.py` | 本地任务执行   | `LocalExecutor`                  |
| 远程执行器     | `execution/executors.py` | SSH 远程执行 | `RemoteExecutor`                 |
| Docker执行器 | `execution/executors.py` | 容器内执行    | `DockerExecutor`                 |
| 执行器管理器    | `execution/executors.py` | 执行器调度    | `ExecutorManager`                |
| 工具注册      | `execution/tools.py`     | 工具管理     | `ToolRegistry`, `Tool`           |

#### 通信层模块

| 模块     | 文件路径                        | 职责       | 关键类                              |
| ------ | --------------------------- | -------- | -------------------------------- |
| ODEP协议 | `protocol/v1/messages.py`   | 消息定义     | `ExecutionIntent`, `ODEPMessage` |
| 协议枚举   | `protocol/v1/enums.py`      | 类型枚举     | `MessageType`, `ExecutionStatus` |
| 协议验证   | `protocol/v1/validators.py` | Schema校验 | `validate_execution_intent`      |
| 传输层    | `protocol/v1/transport.py`  | 通信传输     | `StdioTransport`                 |
| 协议适配   | `protocol/v1/adapters.py`   | 版本兼容     | `ODEPLegacyAdapter`              |

#### 辅助模块

| 模块    | 文件路径                      | 职责     | 关键类                                   |
| ----- | ------------------------- | ------ | ------------------------------------- |
| 工作区感知 | `perception/workspace.py` | 只读环境感知 | `LocalWorkspacePerceiver`             |
| 感知轮询  | `perception/poller.py`    | 变化检测   | `WorkspacePoller`, `FileSystemPoller` |
| 系统诊断  | `octopus/doctor.py`       | 健康检查   | `Doctor`, `SystemChecker`             |
| 项目脚手架 | `octopus/quickstart.py`   | 模板生成   | `Quickstart`, `ProjectTemplate`       |

### 1.4 系统集成关系

```
┌─────────────┐     ODEP Protocol     ┌─────────────┐
│  Decision   │ ◄────────────────────► │  Execution  │
│   Layer     │                        │   Layer     │
└──────┬──────┘                        └──────┬──────┘
       │                                     │
       ▼                                     ▼
┌─────────────┐                        ┌─────────────┐
│  Perception │                        │  Tool       │
│   Module    │                        │  Registry   │
└──────┬──────┘                        └──────┬──────┘
       │                                     │
       ▼                                     ▼
┌─────────────┐                        ┌─────────────┐
│  Workspace  │                        │  LLM        │
│  Perceiver  │                        │  Providers  │
└─────────────┘                        └─────────────┘
```

**接口定义**：

| 接口    | 方向 | 协议                      | 数据格式               |
| ----- | -- | ----------------------- | ------------------ |
| 决策→执行 | 下行 | ODEP EXECUTION\_REQUEST | `ExecutionIntent`  |
| 执行→决策 | 上行 | ODEP EXECUTION\_RESULT  | `ExecutionResult`  |
| 决策→审批 | 下行 | ODEP APPROVAL\_REQUEST  | `ApprovalRequest`  |
| 审批→决策 | 上行 | ODEP APPROVAL\_RESPONSE | `ApprovalResponse` |
| 感知→决策 | 内部 | Python 调用               | `PerceptionResult` |
| 决策→记忆 | 内部 | Python 调用               | `MemoryItem`       |

***

## 2. 运行原理

### 2.1 系统启动流程

```
用户启动 ──► 参数解析 ──► 模块初始化 ──► 命令分发 ──► 功能执行
    │             │            │            │            │
    │             │            │            │            └─► 返回结果
    │             │            │            └─► Shell 交互
    │             │            └─► 注册命令
    │             └─► 实例化核心组件
    └─► 解析 CLI 参数
```

**启动代码示例**：

```python
# octopus/cli.py - main() 函数

def main():
    # 1. 解析命令行参数
    cli = CLI()
    args = cli.parse()
    
    # 2. 初始化核心组件
    from perception import LocalWorkspacePerceiver
    from core.decision_engine import DecisionEngine, DecisionPolicy
    from core.session import SessionStore
    from core.approval import ApprovalManager
    
    perceiver = LocalWorkspacePerceiver()
    decision_engine = DecisionEngine()
    session_store = SessionStore()
    approval_manager = ApprovalManager()
    
    # 3. 配置决策策略
    policy = DecisionPolicy(
        policy_id="default_policy",
        criteria=[
            DecisionCriteria("outcome_value", 0.40),
            DecisionCriteria("risk_reduction", 0.25),
            DecisionCriteria("reversibility", 0.20),
            DecisionCriteria("confidence_alignment", 0.15),
        ],
    )
    decision_engine.add_policy(policy)
    
    # 4. 启动交互式 Shell
    shell = Shell()
    shell.register_command(ReadFileCommand(perceiver))
    shell.register_command(DecideCommand(decision_engine))
    shell.register_command(SessionCommand(session_store))
    # ... 更多命令
    shell.run()
```

### 2.2 核心服务工作机制

#### 2.2.1 决策引擎工作流程

```python
# core/decision_engine.py - make_decision()

def make_decision(self, context: Dict, options: List[Dict]) -> Decision:
    # 1. 选择决策策略
    policy = self._select_policy(context)
    
    # 2. 对每个选项进行多标准打分
    scored_options = []
    for option in options:
        scores = self._evaluate_option(option, policy, context)
        total_score = self._calculate_weighted_score(scores, policy)
        scored_options.append({...option, "total_score": total_score})
    
    # 3. 选择得分最高的选项
    best_option = max(scored_options, key=lambda x: x["total_score"])
    
    # 4. 生成决策结果
    return Decision(
        decision_id=uuid.uuid4(),
        selected_option=best_option,
        confidence=best_option["total_score"],
        reasoning=f"Selected based on {policy.name} policy",
    )
```

#### 2.2.2 ODEP 协议通信机制

```python
# protocol/v1/transport.py - StdioTransport

class StdioTransport(Transport):
    def send(self, message: ODEPMessage) -> None:
        """发送消息到执行层"""
        payload = message.to_dict()
        self._write_line(json.dumps(payload))
    
    def receive(self, timeout: float = 30) -> Optional[ODEPMessage]:
        """从执行层接收消息"""
        line = self._read_line(timeout)
        if line:
            data = json.loads(line)
            return ODEPMessage.from_dict(data)
        return None
```

#### 2.2.3 感知轮询机制

```python
# perception/poller.py - FileSystemPoller

class FileSystemPoller(BasePoller):
    def _poll_loop(self):
        """轮询主循环"""
        while not self._stop_event.is_set():
            if not self._pause_event.is_set():
                changes = self._detect_changes()
                if changes:
                    self._change_history.extend(changes)
                    for callback in self._callbacks:
                        callback(changes)
            time.sleep(self.config.poll_interval_seconds)
    
    def _detect_changes(self) -> List[WorkspaceChange]:
        """检测文件系统变化"""
        changes = []
        current_files = self._scan_directory()
        
        # 与上次扫描结果对比
        for filepath, metadata in current_files.items():
            if filepath not in self._previous_files:
                changes.append(WorkspaceChange(
                    change_type=ChangeType.FILE_CREATED,
                    path=filepath,
                ))
            elif metadata != self._previous_files[filepath]:
                changes.append(WorkspaceChange(
                    change_type=ChangeType.FILE_MODIFIED,
                    path=filepath,
                ))
        
        # 检测删除的文件
        for filepath in self._previous_files:
            if filepath not in current_files:
                changes.append(WorkspaceChange(
                    change_type=ChangeType.FILE_DELETED,
                    path=filepath,
                ))
        
        self._previous_files = current_files
        return changes
```

### 2.3 数据存储与处理机制

#### 会话存储结构

```python
# core/session.py - SessionStore

class SessionStore:
    def __init__(self, storage_path: str = None):
        self._sessions: Dict[str, Session] = {}
        self._current_session_id: Optional[str] = None
        self._storage_path = storage_path or os.path.expanduser("~/.octopus/sessions")
        self._load_sessions()
    
    def create(self, title: str, description: str = "") -> Session:
        """创建会话并持久化"""
        session = Session(
            session_id=uuid.uuid4(),
            title=title,
            description=description,
        )
        self._sessions[session.session_id] = session
        self._save_session(session)  # 保存到JSON文件
        return session
```

#### 记忆存储机制

```python
# core/memory.py - LongTermMemory

class LongTermMemory:
    def __init__(self, storage_path: str = None):
        self._memory_store: List[MemoryItem] = []
        self._storage_path = storage_path or os.path.expanduser("~/.octopus/memory")
        self._load_memories()
    
    def store(self, content: str, memory_type: MemoryType, 
              context: Dict = None, tags: List[str] = None) -> MemoryItem:
        """存储记忆，支持标签和上下文"""
        item = MemoryItem(
            memory_id=uuid.uuid4(),
            content=content,
            memory_type=memory_type,
            context=context or {},
            tags=tags or [],
        )
        self._memory_store.append(item)
        self._save_memories()
        return item
    
    def search(self, memory_type: MemoryType = None, 
               tags: List[str] = None, limit: int = 10) -> List[MemoryItem]:
        """语义搜索记忆"""
        results = self._memory_store
        if memory_type:
            results = [m for m in results if m.memory_type == memory_type]
        if tags:
            results = [m for m in results if all(t in m.tags for t in tags)]
        return results[-limit:]
```

### 2.4 关键技术实现细节

#### 状态快照与回滚

```python
# core/world_model.py

class WorldModel:
    def create_snapshot(self) -> StateSnapshot:
        """创建当前状态快照，用于故障恢复"""
        snapshot = StateSnapshot(
            snapshot_id=uuid.uuid4(),
            entities=self._deep_copy(self._entities),
            constraints=self._constraints.copy(),
            goals=self._goals.copy(),
        )
        self._snapshots[snapshot.snapshot_id] = snapshot
        return snapshot
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        """从快照回滚状态"""
        if snapshot_id in self._snapshots:
            snapshot = self._snapshots[snapshot_id]
            self._entities = self._deep_copy(snapshot.entities)
            self._constraints = snapshot.constraints.copy()
            self._goals = snapshot.goals.copy()
            return True
        return False
```

#### JSON Schema 验证

```python
# protocol/v1/validators.py

import jsonschema

EXECUTION_INTENT_SCHEMA = {
    "type": "object",
    "required": ["intent_id", "action_type", "parameters"],
    "properties": {
        "intent_id": {"type": "string"},
        "action_type": {"type": "string"},
        "parameters": {"type": "object"},
        "priority": {"type": "string", "enum": ["low", "normal", "high", "critical"]},
        "timeout_seconds": {"type": "integer"},
        "constraints": {"type": "array"},
    },
}

def validate_execution_intent(data: Dict) -> bool:
    """验证执行意图格式"""
    try:
        jsonschema.validate(data, EXECUTION_INTENT_SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False
```

***

## 3. 业务流程

### 3.1 主要业务场景流程

#### 场景一：用户请求处理流程

```
用户输入
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. 感知阶段                                                      │
│    PerceptionModule.perceive(input)                              │
│    - 提取意图 (Intent)                                            │
│    - 识别实体 (Entity)                                           │
│    - 计算置信度                                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. 状态记录                                                      │
│    WorldModel.update_state(intent, entities)                    │
│    - 更新全局状态                                                │
│    - 创建状态快照                                                │
│    SessionStore.add_event("decision_started")                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. 模拟预演                                                      │
│    SimulationEngine.simulate(scenario)                           │
│    - 生成可选方案                                                │
│    - 预测执行结果                                                │
│    - 评估风险等级                                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. 决策制定                                                      │
│    DecisionEngine.make_decision(context, options)                │
│    - 应用决策策略                                                │
│    - 多标准加权评分                                              │
│    - 选择最优方案                                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. 审批检查                                                      │
│    ApprovalManager.check_approval(decision_id)                   │
│    - 检查审批策略                                                │
│    - 自动/人工审批                                               │
│    - 等待审批结果                                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. 伦理审核                                                      │
│    EthicsFramework.evaluate(decision)                           │
│    - 检查伦理规则                                                │
│    - 合规性验证                                                  │
│    - 风控拦截                                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. 执行调用                                                      │
│    ODEPProtocol.send(ExecutionIntent)                            │
│    ExecutorManager.execute(intent)                               │
│    - 选择执行器                                                  │
│    - 执行任务                                                    │
│    - 返回结果                                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. 结果归档                                                      │
│    LongTermMemory.store(decision, outcome)                      │
│    SessionStore.add_event("decision_completed")                  │
│    WorldModel.update_state(result)                               │
└─────────────────────────────────────────────────────────────────┘
```

#### 场景二：工作区感知流程

```
用户请求感知
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ LocalWorkspacePerceiver                                         │
│    ├── read_file(path)        # 读取文件                        │
│    ├── repo_map(depth)        # 目录扫描                        │
│    ├── search(query)          # 内容搜索                       │
│    ├── git_status()           # Git状态                        │
│    ├── git_diff(file)         # Git差异                        │
│    └── git_log(limit)         # Git日志                        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ BudgetConfig 预算控制                                            │
│    - max_files: 最大文件数                                       │
│    - max_chars: 单文件最大字符数                                 │
│    - allowed_extensions: 允许的扩展名                           │
│    - excluded_patterns: 排除的模式                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ PerceptionResult 结果封装                                        │
│    - success: 是否成功                                           │
│    - data: 感知数据                                              │
│    - error: 错误信息                                             │
│    - metadata: 附加信息                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 异常处理流程

#### 执行失败处理

```
执行任务
    │
    ├──► 成功 → 返回结果 → 归档 → 更新状态
    │
    └──► 失败
            │
            ▼
        ExecutorStatus.ERROR
            │
            ▼
        检查回滚计划
            │
            ├──► 有回滚计划 → 执行回滚
            │
            └──► 无回滚计划 → 返回错误
                    │
                    ▼
                WorldModel.restore_snapshot()
                    │
                    ▼
                通知决策层重试
```

#### 审批超时处理

```
审批请求
    │
    ▼
ApprovalTask 创建
    │
    ▼
等待审批 (timeout_seconds)
    │
    ├──► 审批通过 → 执行决策
    ├──► 审批拒绝 → 取消决策
    │
    └──► 超时
            │
            ▼
        ApprovalStatus.TIMEOUT
            │
            ▼
        通知决策层
            │
            ▼
        重新决策或升级审批
```

### 3.3 并发与异步处理机制

#### 感知轮询并发

```python
# perception/poller.py

class WorkspacePoller:
    def __init__(self):
        self._pollers = {
            "file": FileSystemPoller(PollingConfig(
                poll_interval_seconds=5.0,
                include_patterns=["*.py", "*.md", "*.json"],
            )),
            "git": GitPoller(PollingConfig(
                poll_interval_seconds=10.0,
            )),
        }
    
    def start_all(self):
        """启动所有轮询器（并发）"""
        for poller in self._pollers.values():
            poller.start()  # 每个轮询器在独立线程运行
    
    def get_status(self) -> Dict:
        """获取所有轮询器状态"""
        return {
            name: {
                "status": poller.status.value,
                "recent_changes": poller.get_changes(limit=5),
            }
            for name, poller in self._pollers.items()
        }
```

#### 执行器任务并发

```python
# execution/executors.py

class ExecutorManager:
    def execute_batch(self, intent: ExecutionIntent) -> List[ExecutionJob]:
        """批量执行任务"""
        executor = self._get_executor(intent)
        jobs = []
        
        # 使用线程池并发执行
        with ThreadPoolExecutor(max_workers=4) as executor_pool:
            futures = {
                executor_pool.submit(executor.execute, item): item
                for item in intent.parameters.get("batch_items", [])
            }
            for future in as_completed(futures):
                job = future.result()
                jobs.append(job)
        
        return jobs
```

***

## 4. 参数流转

### 4.1 核心业务参数定义

#### 决策层参数

| 参数名              | 类型                       | 模块               | 说明      |
| ---------------- | ------------------------ | ---------------- | ------- |
| `goal`           | `str`                    | DecisionEngine   | 决策目标描述  |
| `options`        | `List[Dict]`             | DecisionEngine   | 决策选项列表  |
| `criteria`       | `List[DecisionCriteria]` | DecisionPolicy   | 评分标准及权重 |
| `entity_id`      | `str`                    | WorldModel       | 实体唯一标识  |
| `entity_type`    | `str`                    | WorldModel       | 实体类型    |
| `intent_type`    | `IntentType`             | PerceptionModule | 意图类型    |
| `session_id`     | `str`                    | SessionStore     | 会话唯一标识  |
| `approval_level` | `ApprovalLevel`          | ApprovalManager  | 审批级别    |

#### 执行层参数

| 参数名             | 类型               | 模块              | 说明     |
| --------------- | ---------------- | --------------- | ------ |
| `intent_id`     | `str`            | ExecutionIntent | 执行意图ID |
| `action_type`   | `str`            | ExecutionIntent | 动作类型   |
| `parameters`    | `Dict[str, Any]` | ExecutionIntent | 执行参数   |
| `priority`      | `Priority`       | ExecutionIntent | 优先级    |
| `executor_type` | `ExecutorType`   | ExecutorConfig  | 执行器类型  |
| `tool_id`       | `str`            | ToolRegistry    | 工具标识   |

#### ODEP 协议参数

| 参数名                | 类型            | 说明         |
| ------------------ | ------------- | ---------- |
| `message_id`       | `str`         | 消息唯一标识     |
| `message_type`     | `MessageType` | 消息类型       |
| `sender`           | `str`         | 发送方标识      |
| `recipient`        | `str`         | 接收方标识      |
| `payload`          | `Dict`        | 消息载荷       |
| `correlation_id`   | `str`         | 关联ID（用于追踪） |
| `timestamp`        | `datetime`    | 消息时间戳      |
| `protocol_version` | `str`         | 协议版本       |

### 4.2 参数传递路径

#### 决策请求参数流

```
用户输入 "帮我创建一个文件"
    │
    ▼
PerceptionModule.perceive()
    │  输出: Intent(intent_type="ACTION", entities=[Entity("file")])
    ▼
WorldModel.update_state()
    │  输入: Intent, Entity
    │  处理: 更新状态、创建快照
    ▼
SimulationEngine.simulate()
    │  输出: Scenario(options=["create_file", "ask_user"])
    ▼
DecisionEngine.make_decision()
    │  输入: context={"goal": "创建文件"}, options=[...]
    │  输出: Decision(selected_option="ask_user", confidence=0.85)
    ▼
ApprovalManager.check_approval()
    │  输入: decision_id, level=LOW
    │  输出: ApprovalTask(status="approved")
    ▼
ODEPProtocol.send()
    │  转换: Decision → ExecutionIntent
    │  输出: ODEPMessage(payload=ExecutionIntent)
    ▼
ExecutorManager.execute()
    │  输入: ExecutionIntent
    │  输出: ExecutionJob(result="success")
    ▼
WorldModel.update_state()
    │  输入: ExecutionResult
    │  处理: 更新状态、记录结果
```

### 4.3 参数验证与转换规则

#### JSON Schema 验证

```python
# protocol/v1/validators.py

EXECUTION_INTENT_SCHEMA = {
    "type": "object",
    "required": ["intent_id", "action_type", "parameters"],
    "properties": {
        "intent_id": {
            "type": "string",
            "pattern": "^intent_[a-zA-Z0-9_]+$",
        },
        "action_type": {
            "type": "string",
            "enum": ["read", "write", "execute", "query", "update"],
        },
        "parameters": {
            "type": "object",
            "additionalProperties": True,
        },
        "priority": {
            "type": "string",
            "enum": ["low", "normal", "high", "critical"],
            "default": "normal",
        },
        "timeout_seconds": {
            "type": "integer",
            "minimum": 1,
            "maximum": 3600,
        },
    },
    "additionalProperties": False,
}
```

#### 数据类型转换

```python
# protocol/v1/messages.py

class ExecutionIntent:
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionIntent":
        """从字典转换为对象，包含类型验证"""
        # 类型转换
        if "priority" in data:
            data["priority"] = Priority(data["priority"])
        
        # 时间戳转换
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，用于JSON序列化"""
        return {
            "intent_id": self.intent_id,
            "priority": self.priority.value,  # 枚举转字符串
            "created_at": self.created_at.isoformat(),  # 时间转字符串
        }
```

### 4.4 上下文信息管理机制

#### 会话上下文管理

```python
# core/session.py

class SessionStore:
    def update_context(self, session_id: str, context_update: Dict) -> Session:
        """更新会话上下文（合并更新）"""
        session = self._sessions.get(session_id)
        if session:
            # 合并上下文
            session.context.update(context_update)
            session.updated_at = datetime.now()
            self._save_session(session)
        return session
    
    def get_context(self, session_id: str) -> Dict:
        """获取会话上下文"""
        session = self._sessions.get(session_id)
        return session.context if session else {}
```

#### 决策上下文传递

```python
# core/decision_engine.py

class DecisionEngine:
    def make_decision(self, context: Dict, options: List[Dict]) -> Decision:
        """决策时携带上下文信息"""
        # 添加上下文元数据
        context_with_metadata = {
            **context,
            "timestamp": datetime.now(),
            "policy_id": self._current_policy.policy_id if self._current_policy else None,
        }
        
        # 传递给评分函数
        for option in options:
            scores = self._evaluate_option(option, context_with_metadata)
```

***

## 5. AI功能应用

### 5.1 AI模块应用场景

| 应用场景 | AI模块             | 说明          |
| ---- | ---------------- | ----------- |
| 意图识别 | PerceptionModule | NLP 理解用户输入  |
| 场景模拟 | SimulationEngine | AI 预测决策结果   |
| 智能决策 | DecisionEngine   | 多标准评分与推荐    |
| 内容生成 | LLM Providers    | 生成决策解释、报告   |
| 知识检索 | LongTermMemory   | 基于历史经验的语义检索 |
| 风险评估 | EthicsFramework  | 智能风控判断      |

### 5.2 AI技术选型及实现原理

#### LLM 提供商抽象

```python
# core/llm_provider.py

class BaseLLMProvider(ABC):
    """LLM 提供商抽象基类"""
    
    @abstractmethod
    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        """多轮对话接口"""
        pass
    
    @abstractmethod
    def complete(self, prompt: str) -> LLMResponse:
        """文本补全接口"""
        pass
    
    @abstractmethod
    def embeddings(self, text: str) -> List[float]:
        """文本向量化"""
        pass

class LLMProviderManager:
    """LLM 提供商管理器"""
    
    def chat(self, messages: List[ChatMessage]) -> LLMResponse:
        """使用默认或指定提供商"""
        provider = self._get_provider(self._default_provider_id)
        return provider.chat(messages)
    
    def embeddings(self, text: str) -> List[float]:
        """获取文本嵌入（用于语义检索）"""
        provider = self._get_provider(self._default_provider_id)
        return provider.embeddings(text)
```

#### 意图识别实现

```python
# core/perception.py

class PerceptionModule:
    def perceive(self, text: str) -> PerceptionResult:
        """理解用户输入，提取意图和实体"""
        # 1. 使用 LLM 分析意图
        messages = [
            ChatMessage(
                role=ChatRole.SYSTEM,
                content="你是意图识别系统，分析用户输入的意图和实体。",
            ),
            ChatMessage(
                role=ChatRole.USER,
                content=f"输入: {text}\n请识别意图类型和相关实体。",
            ),
        ]
        response = self.llm_provider.chat(messages)
        
        # 2. 解析 LLM 响应
        intent_data = self._parse_intent_response(response)
        
        # 3. 构造感知结果
        return PerceptionResult(
            intents=[Intent(**intent_data)],
            confidence=intent_data.get("confidence", 0.5),
            entities=intent_data.get("entities", []),
        )
```

### 5.3 AI解决的关键业务问题

#### a) 数据处理与分析

**场景**：大规模代码仓库分析

```python
# 使用 AI 分析代码库

class CodeAnalyzer:
    def analyze_repository(self, repo_path: str) -> AnalysisReport:
        """分析代码仓库结构和质量"""
        # 1. 工作区感知
        files = self.perceiver.repo_map(repo_path)
        content = self.perceiver.search("function|class|import")
        
        # 2. AI 辅助分析
        analysis_prompt = f"""
        分析以下代码结构：
        文件列表: {files}
        关键内容: {content}
        
        请提供：
        1. 项目结构总结
        2. 核心功能模块
        3. 代码质量评估
        4. 改进建议
        """
        response = self.llm.complete(analysis_prompt)
        
        return self._parse_analysis(response)
```

#### b) 业务决策支持

**场景**：产品方案选择

```python
# 使用 AI 辅助决策

class DecisionAdvisor:
    def evaluate_options(self, goal: str, options: List[Dict]) -> DecisionReport:
        """AI 评估不同方案"""
        # 1. 构造评估提示
        options_description = "\n".join([
            f"方案 {i+1}: {opt['name']}\n  描述: {opt['description']}"
            for i, opt in enumerate(options)
        ])
        
        prompt = f"""
        目标: {goal}
        
        可选方案:
        {options_description}
        
        请从以下维度评估每个方案：
        - 可行性
        - 成本效益
        - 风险等级
        - 实施难度
        - 长期价值
        
        给出每个方案的评分（1-10）和建议。
        """
        
        # 2. 获取 AI 评估
        response = self.llm.complete(prompt)
        
        # 3. 结合决策引擎
        ai_scores = self._parse_ai_evaluation(response)
        final_decision = self.decision_engine.make_decision(
            context={"goal": goal, "ai_scores": ai_scores},
            options=options,
        )
        
        return DecisionReport(
            ai_evaluation=response,
            final_decision=final_decision,
            reasoning=self._generate_reasoning(final_decision, ai_scores),
        )
```

#### c) 用户交互优化

**场景**：智能对话系统

```python
# 使用 AI 优化用户交互

class InteractiveAssistant:
    def __init__(self):
        self.llm_manager = LLMProviderManager()
        self.session_store = SessionStore()
    
    def chat(self, user_input: str, session_id: str = None) -> str:
        """智能对话"""
        # 1. 获取或创建会话
        session = self._get_or_create_session(session_id)
        
        # 2. 历史上下文
        history = self._get_chat_history(session)
        
        # 3. AI 响应
        messages = [
            ChatMessage(role=ChatRole.SYSTEM, content=self._get_system_prompt()),
            *history,
            ChatMessage(role=ChatRole.USER, content=user_input),
        ]
        
        response = self.llm_manager.chat(messages)
        
        # 4. 更新会话
        self._update_session(session, user_input, response.content)
        
        # 5. 附加建议
        suggestions = self._generate_suggestions(response.content)
        
        return f"{response.content}\n\n💡 建议: {suggestions}"
    
    def _generate_suggestions(self, response: str) -> str:
        """基于 AI 响应生成下一步建议"""
        prompt = f"""
        基于以下回答，生成3个下一步建议：
        {response}
        """
        ai_response = self.llm_manager.complete(prompt)
        return ai_response.content
```

#### d) 自动化任务处理

**场景**：智能工作流执行

```python
# 使用 AI 自动化任务

class AutomatedTaskExecutor:
    def execute_complex_task(self, description: str) -> TaskResult:
        """执行复杂任务"""
        # 1. AI 任务分解
        task_breakdown = self._ai_breakdown(description)
        
        # 2. 子任务执行
        results = []
        for sub_task in task_breakdown:
            # 2.1 感知环境
            env_info = self.perceiver.repo_map()
            
            # 2.2 决策执行方式
            execution_plan = self._plan_execution(sub_task, env_info)
            
            # 2.3 执行任务
            result = self.executor.execute(execution_plan)
            results.append(result)
        
        # 3. AI 结果汇总
        summary = self._ai_summarize(results)
        
        return TaskResult(
            original_task=description,
            subtasks=task_breakdown,
            results=results,
            summary=summary,
        )
    
    def _ai_breakdown(self, description: str) -> List[str]:
        """AI 将复杂任务分解为子任务"""
        prompt = f"""
        将以下任务分解为具体的执行步骤：
        "{description}"
        
        要求：
        1. 每个步骤具体可执行
        2. 步骤之间有逻辑顺序
        3. 考虑异常情况
        """
        response = self.llm.complete(prompt)
        return self._parse_steps(response)
```

#### e) 其他应用领域

**场景**：智能报告生成

```python
# 使用 AI 生成报告

class ReportGenerator:
    def generate_decision_report(self, decision: Decision) -> str:
        """生成决策报告"""
        # 1. 收集决策数据
        data = {
            "goal": decision.context.get("goal"),
            "options_considered": len(decision.options),
            "selected_option": decision.selected_option.name,
            "confidence": decision.confidence,
            "scores": decision.selected_option.scores,
        }
        
        # 2. AI 生成报告
        prompt = f"""
        请生成一份决策报告：
        
        决策目标: {data['goal']}
        考虑方案数: {data['options_considered']}
        选择方案: {data['selected_option']}
        置信度: {data['confidence']:.1%}
        评分详情: {json.dumps(data['scores'], indent=2)}
        
        报告要求：
        1. 决策摘要
        2. 方案对比
        3. 选择理由
        4. 风险评估
        5. 建议行动
        """
        
        response = self.llm.complete(prompt)
        return response.content
    
    def generate_analysis_report(self, workspace_analysis: Dict) -> str:
        """生成分析报告"""
        prompt = f"""
        基于以下分析数据，生成专业报告：
        {json.dumps(workspace_analysis, indent=2)}
        
        报告应包含：
        1. 数据概览
        2. 关键发现
        3. 趋势分析
        4. 行动建议
        """
        
        return self.llm.complete(prompt).content
```

***

## 附录

### 术语表

| 术语       | 全称                                  | 说明            |
| -------- | ----------------------------------- | ------------- |
| ODEP     | Octopus Decision Execution Protocol | 决策-执行协议       |
| LLM      | Large Language Model                | 大语言模型         |
| TUI      | Terminal User Interface             | 终端用户界面        |
| Policy   | Decision Policy                     | 决策策略          |
| Criteria | Decision Criteria                   | 决策标准          |
| Entity   | Entity                              | 实体            |
| Snapshot | State Snapshot                      | 状态快照          |
| Budget   | Budget Config                       | 预算配置          |

### 配置文件说明

#### .env 配置

```env
# LLM 提供商 API 密钥
OPENAI_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key
GOOGLE_API_KEY=your_api_key

# 默认 LLM 提供商
OCTOPUS_DEFAULT_LLM_PROVIDER=openai

# 执行器配置
OCTUPUS_EXECUTOR_TIMEOUT=60
OCTUPUS_MAX_CONCURRENT_JOBS=4

# 感知轮询配置
OCTUPUS_POLL_INTERVAL=5.0
```

#### application.yml 配置

```yaml
# config/application.yml
octopus:
  version: "1.0.0"
  
  llm:
    default_provider: "openai"
    temperature: 0.7
    max_tokens: 4096
    
  executor:
    default: "local"
    timeout_seconds: 60
    max_jobs: 10
  
  perception:
    budget:
      max_files: 100
      max_chars_per_file: 100000
    allowed_extensions:
      - ".py"
      - ".md"
      - ".json"
      - ".yaml"
  
  storage:
    sessions_path: "~/.octopus/sessions"
    memory_path: "~/.octopus/memory"
    approval_path: "~/.octopus/approvals"
```

### 版本历史

| 版本     | 日期         | 主要变更                              |
| ------ | ---------- | --------------------------------- |
| v0.1.0 | -          | 基础架构定义                            |
| v0.2.0 | -          | ODEP 协议标准化                        |
| v0.3.0 | -          | 工作区感知、CLI、决策卡片                    |
| v0.3.1 | -          | 会话管理、批准机制、决策比较                    |
| v0.4.0 | -          | 多执行器、多 LLM、感知轮询、Doctor、Quickstart |
| v1.0.0 | 2026-08-11 | 正式发布，完整文档和入门指引                    |

***

**Octopus v1.0.0 技术文档** | 决策-执行层分离架构
