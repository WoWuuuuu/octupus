from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class ExecutorType(Enum):
    LOCAL = "local"
    REMOTE = "remote"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    LAMBDA = "lambda"


class ExecutorStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ExecutorConfig:
    executor_id: str
    executor_type: ExecutorType
    name: str = ""
    description: str = ""
    host: str = "localhost"
    port: int = 0
    timeout_seconds: int = 300
    max_concurrent_tasks: int = 10
    environment: Dict[str, str] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "executor_id": self.executor_id,
            "executor_type": self.executor_type.value,
            "name": self.name,
            "description": self.description,
            "host": self.host,
            "port": self.port,
            "timeout_seconds": self.timeout_seconds,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "environment": self.environment,
            "config": self.config,
        }


@dataclass
class ExecutionJob:
    job_id: str
    executor_id: str
    task_id: str
    tool_id: str
    parameters: Dict[str, Any]
    status: ExecutorStatus = ExecutorStatus.IDLE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "executor_id": self.executor_id,
            "task_id": self.task_id,
            "tool_id": self.tool_id,
            "parameters": self.parameters,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


class BaseExecutor(ABC):
    def __init__(self, config: ExecutorConfig):
        self.config = config
        self.status = ExecutorStatus.IDLE
        self.active_jobs: Dict[str, ExecutionJob] = {}
        self.job_history: List[ExecutionJob] = []

    @abstractmethod
    def execute(self, tool_id: str, parameters: Dict[str, Any]) -> ExecutionJob:
        pass

    @abstractmethod
    def execute_batch(self, jobs: List[Dict[str, Any]]) -> List[ExecutionJob]:
        pass

    @abstractmethod
    def cancel_job(self, job_id: str) -> bool:
        pass

    @abstractmethod
    def get_job_status(self, job_id: str) -> Optional[ExecutionJob]:
        pass

    @abstractmethod
    def start(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass

    @abstractmethod
    def pause(self) -> bool:
        pass

    @abstractmethod
    def resume(self) -> bool:
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        pass

    def get_status(self) -> ExecutorStatus:
        return self.status

    def get_active_jobs(self) -> List[ExecutionJob]:
        return list(self.active_jobs.values())

    def get_job_history(self) -> List[ExecutionJob]:
        return self.job_history

    def get_summary(self) -> Dict[str, Any]:
        successful = sum(1 for j in self.job_history if j.status == ExecutorStatus.STOPPED and not j.error)
        failed = sum(1 for j in self.job_history if j.error)
        return {
            "executor_id": self.config.executor_id,
            "executor_type": self.config.executor_type.value,
            "name": self.config.name,
            "status": self.status.value,
            "active_jobs": len(self.active_jobs),
            "total_jobs": len(self.job_history),
            "successful_jobs": successful,
            "failed_jobs": failed,
            "max_concurrent_tasks": self.config.max_concurrent_tasks,
        }