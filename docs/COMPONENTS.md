# Octopus 组件规格与数据模型说明书

本说明书详细列出了 Octopus 架构中所有核心决策层组件与执行层的类定义和核心数据模型。

---

## 1. 核心决策组件规格

### 💾 WorldModel (世界模型)
- **职责**：维护 Agent 认知的全局状态、活动目标（Active Goals）与外部约束（Constraints）。
- **关键方法**：
  - `create_snapshot() -> StateSnapshot`：生成当前状态的内存拷贝快照。
  - `restore_snapshot(snapshot_id) -> bool`：发生故障或违规时一键回滚状态，保证事务一致性。

### 🔎 PerceptionModule (感知模块)
- **职责**：从非结构化输入信号中提取 `Intent` 和 `Entities`。
- **数据结构**：
  - `Intent`: 包含 `intent_type` (COMMAND/QUERY/ERROR等)、`raw_content`。

### 🎮 SimulationEngine (模拟引擎)
- **职责**：预演 Action Sequence 在特定 initial state 下的走向，输出 `SimulationResult`（含 `total_risk` 风险模型及 `overall_score` 成功指标）。

### ⚖️ DecisionEngine (决策引擎)
- **职责**：根据当前 Policy 要求的 Criteria（如客户满意度、成本、风险）及其权重分配，对候选方案做加权平均分值排序。
- **关键方法**：
  - `make_decision(context, options) -> Decision`：做出决策
  - `add_policy(policy)`：添加决策策略

### 🛡️ EthicsFramework (伦理与风控框架)
- **职责**：审查动作是否违背商业或安全红线。
- **数据结构**：
  - `EthicalRule`: 包含原则、描述、条件及严重程度。
  - `EthicsDecision`: 包含 APPROVED (通过), BLOCKED (一票否决), REQUIRES_REVIEW (转人工审批)。

### 🧠 LongTermMemory (长期记忆系统)
- **职责**：以 Episodic(情节) 或 Semantic(语义) 方式持久化保存经验，支持基于向量的语义检索，并具备 `float-to-enum` 相关性防御纠错。
- **关键方法**：
  - `store(content, memory_type, context, tags)`：存储记忆
  - `retrieve(memory_id)`：检索记忆
  - `search(memory_type, tags, context)`：搜索记忆

### 🃏 DecisionCard (决策卡片)
- **职责**：可视化决策结果，支持文本、JSON、Rich 三种输出格式。
- **数据结构**：
  - `DecisionCard`: 包含决策ID、目标、状态、选项列表、选中选项、推理过程。
  - `DecisionCardOption`: 包含选项ID、名称、描述、总分、风险等级、可逆性、置信度。
- **关键方法**：
  - `to_text()`：文本格式输出
  - `to_json()`：JSON格式输出
  - `render(card, format)`：渲染决策卡片

### 🔄 DecisionComparator (决策比较器)
- **职责**：对比多个决策结果，生成对比摘要和统计信息。
- **关键方法**：
  - `compare(cards, format)`：对比多个决策卡片
  - `_generate_summary(cards)`：生成对比摘要

### 📝 Session (会话管理系统)
- **职责**：管理决策会话的生命周期，支持创建、切换、归档、搜索、时间线等功能。
- **数据结构**：
  - `Session`: 包含会话ID、标题、描述、状态、类型、创建时间、更新时间、上下文、标签、决策ID列表、事件列表。
  - `SessionStatus`: ACTIVE/PAUSED/COMPLETED/ARCHIVED
  - `SessionType`: DECISION/EXPLORATION/RESEARCH/REVIEW/OTHER
  - `SessionEvent`: 包含事件ID、类型、时间戳、描述、元数据。
- **关键方法**：
  - `create(title, description)`：创建会话
  - `get(session_id)`：获取会话
  - `set_current(session_id)`：设置当前会话
  - `list(status, session_type)`：列出会话
  - `search(query)`：搜索会话
  - `get_timeline(session_id)`：获取时间线

### 🔑 ApprovalManager (批准机制)
- **职责**：管理决策批准流程，支持不同级别（AUTO/LOW/MEDIUM/HIGH/CRITICAL）的审批。
- **数据结构**：
  - `ApprovalLevel`: AUTO/LOW/MEDIUM/HIGH/CRITICAL
  - `ApprovalPolicy`: 包含名称、级别、是否需要人工审批、超时时间、最大重试次数、条件列表。
  - `ApprovalTask`: 包含审批ID、决策ID、决策摘要、级别、状态、创建时间、请求人、审批人、审批时间、原因。
- **关键方法**：
  - `create_approval(decision_id, summary, level)`：创建审批请求
  - `approve(approval_id, approved_by, reason)`：批准
  - `reject(approval_id, approved_by, reason)`：拒绝
  - `list_pending()`：列出待审批
  - `is_approved(decision_id)`：检查是否已批准

---

## 2. 工作区感知组件

### 👀 LocalWorkspacePerceiver (本地工作区感知器)
- **职责**：提供只读的工作区感知能力，包括文件读取、目录扫描、内容搜索、Git操作、URL读取。
- **关键方法**：
  - `read_file(filepath)`：读取文件内容
  - `repo_map(depth)`：生成目录结构树
  - `search(query)`：搜索文件内容
  - `git_status()`：获取Git状态
  - `git_diff(filepath)`：获取Git差异
  - `git_log(limit)`：获取Git日志
  - `read_url(url, timeout)`：读取URL内容

### 📊 BudgetConfig (预算配置)
- **职责**：控制工作区感知的资源访问限制。
- **数据结构**：
  - `max_files`: 最大文件数
  - `max_chars_per_file`: 每个文件最大字符数
  - `allowed_extensions`: 允许的文件扩展名
  - `excluded_patterns`: 排除的文件模式

---

## 3. ODEP v1.0 协议组件

### 📬 Message Types (消息类型)
- **MessageType**: EXECUTION_REQUEST, EXECUTION_RESULT, WORLD_STATE_UPDATE, APPROVAL_REQUEST, APPROVAL_RESPONSE, DECISION_REQUEST, DECISION_RESPONSE, ERROR, PING, PONG
- **ExecutionStatus**: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, TIMEOUT
- **Priority**: LOW, NORMAL, HIGH, CRITICAL
- **ApprovalStatus**: PENDING, APPROVED, REJECTED, TIMEOUT

### 📦 Message Data Classes (消息数据类)
- **ExecutionIntent**: 执行意图，包含intent_id、action_type、parameters、priority、timeout_seconds、constraints、rollback_plan。
- **ExecutionResult**: 执行结果，包含intent_id、status、output、error、execution_time_ms、partial_results。
- **WorldStateUpdate**: 世界状态更新，包含state_type、changes、source、confidence、timestamp、causal_links。
- **ApprovalRequest**: 批准请求，包含approval_id、intent_id、intent、context。
- **ApprovalResponse**: 批准响应，包含approval_id、status、reason。
- **DecisionRequest**: 决策请求，包含decision_id、goal、context、options。
- **DecisionResponse**: 决策响应，包含decision_id、selected、reasoning、confidence。
- **ODEPMessage**: 协议消息容器，包含message_id、message_type、sender、recipient、payload、correlation_id、timestamp、ttl_seconds、retry_count、protocol_version。

### ✅ Validators (验证器)
- **validate_execution_intent(data)**: 验证执行意图
- **validate_execution_result(data)**: 验证执行结果
- **validate_odep_message(data)**: 验证协议消息

### 🔌 Transport (传输层)
- **Transport**: 抽象传输层基类
- **StdioTransport**: 标准输入输出传输实现

### 🔄 Adapter (适配器)
- **ODEPLegacyAdapter**: ODEP v0 到 v1 的协议适配器

---

## 4. 执行器组件

### 🚀 ExecutorManager (执行器管理器)
- **职责**：管理多种执行器的注册、选择和调度。
- **关键方法**：
  - `register_executor(executor)`：注册执行器
  - `get_executor(executor_id)`：获取执行器
  - `get_default_executor()`：获取默认执行器
  - `execute(intent)`：执行任务
  - `list_executors()`：列出所有执行器
  - `get_health_summary()`：获取健康摘要

### 🖥️ LocalExecutor (本地执行器)
- **职责**：在本地执行任务，支持Python代码、Shell命令、文件读写等。
- **关键方法**：
  - `execute_python(code)`：执行Python代码
  - `execute_shell(command)`：执行Shell命令
  - `execute_file_read(filepath)`：读取文件
  - `execute_file_write(filepath, content)`：写入文件

### 🌐 RemoteExecutor (远程执行器)
- **职责**：通过SSH执行远程任务。
- **关键方法**：
  - `execute_remote(command)`：执行远程命令

### 🐳 DockerExecutor (Docker执行器)
- **职责**：在Docker容器中执行任务。
- **关键方法**：
  - `execute_in_container(command)`：在容器中执行命令

### 数据结构
- **ExecutorType**: LOCAL, REMOTE, DOCKER
- **ExecutorStatus**: STOPPED, RUNNING, PAUSED, ERROR
- **ExecutorConfig**: 包含executor_id、executor_type、host、port、timeout等。
- **ExecutionJob**: 包含job_id、intent_id、executor_id、status、result等。

---

## 5. LLM提供商组件

### 🤖 LLMProviderManager (LLM提供商管理器)
- **职责**：管理多种LLM提供商的注册和切换。
- **关键方法**：
  - `register_provider(provider)`：注册提供商
  - `get_provider(provider_id)`：获取提供商
  - `get_default_provider()`：获取默认提供商
  - `chat(messages)`：调用聊天接口
  - `complete(prompt)`：调用补全接口
  - `embeddings(text)`：获取文本嵌入

### 🔑 OpenAIProvider (OpenAI提供商)
- **职责**：集成OpenAI API。

### 🔷 AnthropicProvider (Anthropic提供商)
- **职责**：集成Anthropic API。

### 🟢 GoogleProvider (Google提供商)
- **职责**：集成Google Gemini API。

### 数据结构
- **LLMProviderType**: OPENAI, ANTHROPIC, GOOGLE, MOCK
- **ChatRole**: SYSTEM, USER, ASSISTANT, TOOL
- **ChatMessage**: 包含role、content、tool_calls、tool_response等。
- **LLMResponse**: 包含content、finish_reason、usage、model等。
- **LLMConfig**: 包含provider_type、api_key、model、temperature等。

---

## 6. 感知轮询组件

### 👀 FileSystemPoller (文件系统轮询器)
- **职责**：检测文件系统变化（创建、修改、删除）。
- **关键方法**：
  - `start()`：启动轮询
  - `stop()`：停止轮询
  - `pause()`：暂停轮询
  - `resume()`：恢复轮询
  - `get_changes(limit)`：获取变化记录
  - `add_callback(callback)`：添加变化回调
  - `remove_callback(callback)`：移除回调

### 📚 GitPoller (Git轮询器)
- **职责**：检测Git仓库变化。
- **关键方法**：
  - `detect_changes()`：检测Git变化

### 🏢 WorkspacePoller (工作区轮询器)
- **职责**：统一管理文件系统和Git轮询。
- **关键方法**：
  - `start_all()`：启动所有轮询器
  - `stop_all()`：停止所有轮询器
  - `get_status()`：获取所有轮询器状态

### 数据结构
- **PollingStatus**: STOPPED, RUNNING, PAUSED
- **ChangeType**: CREATED, MODIFIED, DELETED, RENAMED
- **WorkspaceChange**: 包含change_type、path、old_path、timestamp等。
- **PollingConfig**: 包含poll_interval、exclude_patterns、max_history等。

---

## 7. 辅助工具组件

### 👨‍⚕️ Doctor (系统诊断工具)
- **职责**：从系统环境、依赖、配置、网络等方面进行健康检查。
- **检查器类型**：
  - `SystemChecker`: 系统环境检查
  - `DependencyChecker`: 依赖检查
  - `ConfigurationChecker`: 配置检查
  - `NetworkChecker`: 网络检查
- **关键方法**：
  - `run_all()`：运行所有检查
  - `run_checker(checker_name)`：运行指定检查
  - `get_summary()`：获取诊断摘要
  - `format_json()`：JSON格式输出
  - `format_text()`：文本格式输出
  - `format_rich()`：Rich格式输出

### 数据结构
- **CheckStatus**: PASS, WARN, FAIL
- **CheckResult**: 包含checker_name、check_name、status、details、suggestion等。

### 🚀 Quickstart (项目脚手架)
- **职责**：提供项目模板，支持快速初始化Octopus项目。
- **模板类型**：
  - `basic`: 基础模板
  - `advanced`: 高级模板
- **关键方法**：
  - `list_templates()`：列出所有模板
  - `get_template_details(template_name)`：获取模板详情
  - `create_project(project_name, template)`：创建新项目

### 数据结构
- **ProjectTemplate**: 包含name、description、variables、files等。

---

## 8. 数据结构规范

### Entity (实体定义)
```python
@dataclass
class Entity:
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    confidence: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)
```

### ExecutionIntent (执行意图)
```python
@dataclass
class ExecutionIntent:
    intent_id: str
    action_type: str
    parameters: Dict[str, Any]
    priority: Priority = Priority.NORMAL
    timeout_seconds: Optional[int] = None
    constraints: List[str] = field(default_factory=list)
    rollback_plan: Optional[Dict[str, Any]] = None
```

### DecisionOption (决策选项)
```python
@dataclass
class DecisionOption:
    option_id: str
    name: str
    description: str
    total_score: float
    risk_level: float
    reversibility: float
    confidence: float
    criteria_scores: Dict[str, float] = field(default_factory=dict)
```

### DecisionCriteria (决策标准)
```python
@dataclass
class DecisionCriteria:
    name: str
    weight: float
    description: str = ""
```

### DecisionPolicy (决策策略)
```python
@dataclass
class DecisionPolicy:
    policy_id: str
    name: str
    description: str = ""
    criteria: List[DecisionCriteria] = field(default_factory=list)
```

### Session (会话)
```python
@dataclass
class Session:
    session_id: str
    title: str
    description: str = ""
    status: SessionStatus = SessionStatus.ACTIVE
    session_type: SessionType = SessionType.DECISION
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    decision_ids: List[str] = field(default_factory=list)
    events: List[SessionEvent] = field(default_factory=list)
```

### ApprovalTask (审批任务)
```python
@dataclass
class ApprovalTask:
    approval_id: str
    decision_id: str
    decision_summary: str
    level: ApprovalLevel
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: str = "system"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    reason: Optional[str] = None
```