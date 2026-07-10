# ODEP v1.0 协议规范

## 文档信息
- **版本**: v1.0
- **创建日期**: 2026-07-10
- **对标**: Spice SDEP v0.1
- **状态**: 进行中

---

## 目录

1. [协议概述](#一协议概述)
2. [消息类型定义](#二消息类型定义)
3. [与Spice SDEP的对比分析](#三与spice-sdep的对比分析)
4. [JSON Schema定义](#四json-schema定义)
5. [传输层设计](#五传输层设计)
6. [向后兼容性](#六向后兼容性)

---

## 一、协议概述

### 1.1 设计目标

ODEP (Octopus Decision Execution Protocol) v1.0 是一个用于决策层与执行层之间通信的标准化协议，对标Spice的SDEP协议，具备以下设计目标：

1. **传输无关**: 支持多种传输方式（stdin/stdout、HTTP、队列、RPC）
2. **协议优先**: 外部执行器无需了解Octopus内部实现
3. **可审计**: 完整的执行意图和结果追踪
4. **版本化**: 支持协议版本演进和向后兼容
5. **类型安全**: 基于JSON Schema进行消息验证

### 1.2 协议生命周期

```
Observation → WorldDelta → WorldState → Decision → ExecutionIntent → ExecutionResult → Outcome → Reflection
```

### 1.3 核心概念

| 概念 | 定义 |
|------|------|
| **Intent** | 决策层发出的执行意图 |
| **Result** | 执行层返回的执行结果 |
| **StateUpdate** | 世界状态变更通知 |
| **Approval** | 批准检查点（可选） |
| **Message** | 协议消息封装 |

---

## 二、消息类型定义

### 2.1 消息类型枚举

```python
class MessageType(Enum):
    EXECUTE_REQUEST = "execute.request"
    EXECUTE_RESPONSE = "execute.response"
    STATE_UPDATE = "state.update"
    DECISION_REQUEST = "decision.request"
    DECISION_RESPONSE = "decision.response"
    APPROVAL_REQUEST = "approval.request"
    APPROVAL_RESPONSE = "approval.response"
    OBSERVATION = "observation"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
```

### 2.2 ExecutionIntent（执行意图）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| intent_id | string | ✅ | 意图唯一标识 |
| action_type | string | ✅ | 动作类型 |
| parameters | object | ✅ | 动作参数 |
| priority | Priority | ✅ | 优先级 |
| timeout_seconds | int | ❌ | 超时时间（秒） |
| constraints | list[string] | ❌ | 约束条件 |
| rollback_plan | object | ❌ | 回滚计划 |
| metadata | object | ❌ | 元数据 |
| created_at | datetime | ✅ | 创建时间 |

### 2.3 ExecutionResult（执行结果）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| intent_id | string | ✅ | 关联的意图ID |
| status | ExecutionStatus | ✅ | 执行状态 |
| output | any | ❌ | 执行输出 |
| error | string | ❌ | 错误信息 |
| execution_time_ms | float | ❌ | 执行时间（毫秒） |
| partial_results | list[any] | ❌ | 部分结果 |
| metadata | object | ❌ | 元数据 |
| completed_at | datetime | ✅ | 完成时间 |

### 2.4 WorldStateUpdate（世界状态更新）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| state_type | string | ✅ | 状态类型 |
| changes | object | ✅ | 变更内容 |
| source | string | ✅ | 来源标识 |
| confidence | float | ❌ | 置信度（0-1） |
| timestamp | datetime | ✅ | 时间戳 |
| causal_links | list[string] | ❌ | 因果关联 |

### 2.5 ODEPMessage（协议消息封装）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message_id | string | ✅ | 消息唯一标识 |
| message_type | MessageType | ✅ | 消息类型 |
| sender | string | ✅ | 发送者标识 |
| recipient | string | ✅ | 接收者标识 |
| payload | object | ✅ | 消息载荷 |
| correlation_id | string | ❌ | 关联ID |
| timestamp | datetime | ✅ | 发送时间 |
| ttl_seconds | int | ❌ | 消息TTL（秒） |
| retry_count | int | ❌ | 重试次数 |
| metadata | object | ❌ | 元数据 |
| protocol_version | string | ✅ | 协议版本 |

### 2.6 枚举类型

```python
class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    PARTIAL = "partial"

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELEGATED = "delegated"
```

---

## 三、与Spice SDEP的对比分析

### 3.1 SDEP消息结构分析

**SDEP核心消息类型：**

| 消息类型 | SDEP字段 | ODEP对应 | 差距 |
|---------|---------|---------|------|
| execute.request | intent_id, action, context, constraints | intent_id, action_type, parameters, constraints | 字段命名差异 |
| execute.response | intent_id, status, output, error | intent_id, status, output, error | 基本一致 |
| decision.request | goal, context, options | 新增 | 需要新增 |
| decision.response | decision_id, selected, reasoning | 新增 | 需要新增 |
| approval.request | approval_id, intent, context | 新增 | 需要新增 |
| approval.response | approval_id, status, reason | 新增 | 需要新增 |

### 3.2 字段级差距分析

**ExecutionIntent字段对比：**

| SDEP字段 | SDEP类型 | ODEP字段 | ODEP类型 | 状态 |
|---------|---------|---------|---------|------|
| intent_id | string | intent_id | string | ✅一致 |
| action | string | action_type | string | ✅一致 |
| context | object | parameters | object | ✅等价 |
| constraints | array[string] | constraints | array[string] | ✅一致 |
| timeout | number | timeout_seconds | int | ✅等价 |
| priority | string | priority | Priority | ✅增强 |
| rollback_plan | object | rollback_plan | object | ✅一致 |
| metadata | object | metadata | object | ✅一致 |
| created_at | string | created_at | datetime | ✅一致 |

**ExecutionResult字段对比：**

| SDEP字段 | SDEP类型 | ODEP字段 | ODEP类型 | 状态 |
|---------|---------|---------|---------|------|
| intent_id | string | intent_id | string | ✅一致 |
| status | string | status | ExecutionStatus | ✅增强 |
| output | any | output | any | ✅一致 |
| error | string | error | string | ✅一致 |
| execution_time_ms | number | execution_time_ms | float | ✅一致 |
| partial_results | array | partial_results | array[any] | ✅一致 |
| metadata | object | metadata | object | ✅一致 |
| completed_at | string | completed_at | datetime | ✅一致 |

### 3.3 ODEP v1.0增强项

1. **协议版本化**: 新增`protocol_version`字段
2. **执行状态扩展**: 新增`PARTIAL`状态支持部分成功
3. **批准机制**: 新增`APPROVAL_REQUEST`/`APPROVAL_RESPONSE`消息类型
4. **决策消息**: 新增`DECISION_REQUEST`/`DECISION_RESPONSE`消息类型
5. **消息TTL**: 新增`ttl_seconds`字段支持消息过期
6. **重试计数**: 新增`retry_count`字段支持重试追踪

---

## 四、JSON Schema定义

### 4.1 ExecutionIntent Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExecutionIntent",
  "type": "object",
  "required": ["intent_id", "action_type", "parameters", "priority", "created_at"],
  "properties": {
    "intent_id": {
      "type": "string",
      "description": "意图唯一标识"
    },
    "action_type": {
      "type": "string",
      "description": "动作类型"
    },
    "parameters": {
      "type": "object",
      "description": "动作参数"
    },
    "priority": {
      "type": "integer",
      "enum": [1, 2, 3, 4],
      "description": "优先级: 1=CRITICAL, 2=HIGH, 3=NORMAL, 4=LOW"
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 0,
      "description": "超时时间（秒）"
    },
    "constraints": {
      "type": "array",
      "items": {"type": "string"},
      "description": "约束条件"
    },
    "rollback_plan": {
      "type": "object",
      "description": "回滚计划"
    },
    "metadata": {
      "type": "object",
      "description": "元数据"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "创建时间"
    }
  }
}
```

### 4.2 ExecutionResult Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExecutionResult",
  "type": "object",
  "required": ["intent_id", "status", "completed_at"],
  "properties": {
    "intent_id": {
      "type": "string",
      "description": "关联的意图ID"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "running", "success", "failed", "cancelled", "timeout", "partial"],
      "description": "执行状态"
    },
    "output": {
      "description": "执行输出"
    },
    "error": {
      "type": "string",
      "description": "错误信息"
    },
    "execution_time_ms": {
      "type": "number",
      "minimum": 0,
      "description": "执行时间（毫秒）"
    },
    "partial_results": {
      "type": "array",
      "description": "部分结果"
    },
    "metadata": {
      "type": "object",
      "description": "元数据"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time",
      "description": "完成时间"
    }
  }
}
```

### 4.3 ODEPMessage Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ODEPMessage",
  "type": "object",
  "required": ["message_id", "message_type", "sender", "recipient", "payload", "timestamp", "protocol_version"],
  "properties": {
    "message_id": {
      "type": "string",
      "description": "消息唯一标识"
    },
    "message_type": {
      "type": "string",
      "enum": ["execute.request", "execute.response", "state.update", "decision.request", "decision.response", "approval.request", "approval.response", "observation", "error", "heartbeat"],
      "description": "消息类型"
    },
    "sender": {
      "type": "string",
      "description": "发送者标识"
    },
    "recipient": {
      "type": "string",
      "description": "接收者标识"
    },
    "payload": {
      "type": "object",
      "description": "消息载荷"
    },
    "correlation_id": {
      "type": "string",
      "description": "关联ID"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "发送时间"
    },
    "ttl_seconds": {
      "type": "integer",
      "minimum": 0,
      "description": "消息TTL（秒）"
    },
    "retry_count": {
      "type": "integer",
      "minimum": 0,
      "description": "重试次数"
    },
    "metadata": {
      "type": "object",
      "description": "元数据"
    },
    "protocol_version": {
      "type": "string",
      "description": "协议版本",
      "default": "1.0"
    }
  }
}
```

---

## 五、传输层设计

### 5.1 传输方式支持

| 传输方式 | 说明 | 适用场景 |
|---------|------|---------|
| stdin/stdout | 通过标准输入输出传输 | 本地执行器 |
| HTTP/HTTPS | 通过REST API传输 | 远程执行器 |
| Message Queue | 通过消息队列传输（Redis、RabbitMQ） | 异步执行 |
| RPC | 通过gRPC或JSON-RPC传输 | 高性能场景 |

### 5.2 传输抽象层

```python
class Transport:
    def send(self, message: ODEPMessage) -> None:
        """发送消息"""
        pass
    
    def receive(self) -> Optional[ODEPMessage]:
        """接收消息"""
        pass
    
    def close(self) -> None:
        """关闭连接"""
        pass
```

### 5.3 传输实现

| 实现类 | 传输方式 | 依赖 |
|--------|---------|------|
| StdioTransport | stdin/stdout | - |
| HttpTransport | HTTP/HTTPS | requests |
| RedisTransport | Redis队列 | redis |
| GrpcTransport | gRPC | grpcio |

---

## 六、向后兼容性

### 6.1 版本策略

- **主版本号**: 不兼容的协议变更
- **次版本号**: 向后兼容的功能新增
- **修订号**: 向后兼容的问题修复

### 6.2 兼容层设计

```python
class ODEPLegacyAdapter:
    """ODEP v0 兼容适配器"""
    
    def convert_v0_to_v1(self, v0_message: dict) -> ODEPMessage:
        """将v0消息转换为v1格式"""
        pass
    
    def convert_v1_to_v0(self, v1_message: ODEPMessage) -> dict:
        """将v1消息转换为v0格式"""
        pass
```

### 6.3 迁移路径

| 阶段 | 版本 | 兼容策略 |
|------|------|---------|
| Phase 1 | v0.2 | 双版本支持，默认v0 |
| Phase 2 | v0.3 | 默认v1，v0标记deprecated |
| Phase 3 | v0.4 | 移除v0支持 |

---

## 七、实现计划

### 7.1 文件结构

```
protocol/
├── __init__.py
├── v1/
│   ├── __init__.py
│   ├── messages.py        # 消息类型定义
│   ├── enums.py           # 枚举类型
│   ├── transport.py       # 传输层抽象
│   ├── validators.py      # JSON Schema验证
│   └── adapters.py        # 兼容适配器
└── legacy/
    ├── __init__.py
    └── communication.py   # 原ODEP v0实现（保持不变）
```

### 7.2 实现步骤

1. **Step 1**: 创建`protocol/v1/enums.py` - 枚举类型定义
2. **Step 2**: 创建`protocol/v1/messages.py` - 消息类型定义（dataclass）
3. **Step 3**: 创建`protocol/v1/validators.py` - JSON Schema验证
4. **Step 4**: 创建`protocol/v1/transport.py` - 传输层抽象
5. **Step 5**: 创建`protocol/v1/adapters.py` - 兼容适配器
6. **Step 6**: 更新`protocol/__init__.py` - 导出v1接口
7. **Step 7**: 创建测试用例