# Octopus 组件规格与数据模型说明书

本说明书详细列出了 Octopus 架构中 6 个核心决策层组件与执行层的类定义和核心数据模型。

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

### 🛡️ EthicsFramework (伦理与风控框架)
- **职责**：审查动作是否违背商业或安全红线。
- **数据结构**：
  - `EthicalRule`: 包含原则、描述、条件及严重程度。
  - `EthicsDecision`: 包含 APPROVED (通过), BLOCKED (一票否决), REQUIRES_REVIEW (转人工审批)。

### 🧠 LongTermMemory (长期记忆系统)
- **职责**：以 Episodic(情节) 或 Semantic(语义) 方式持久化保存经验，支持基于向量的语义检索，并具备 `float-to-enum` 相关性防御纠错。

---

## 2. 数据结构规范

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
```
