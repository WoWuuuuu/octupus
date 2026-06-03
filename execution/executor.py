"""
Execution Layer - Pure tool execution component for Octopus

Manages execution of tools based on instructions from the Decision Layer.
Does not make autonomous decisions - strictly follows instructions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum

from octopus.protocol.communication import (
    ExecutionIntent,
    ExecutionResult,
    ExecutionStatus,
    ODEPProtocol
)
from octopus.execution.tools import ToolRegistry, Tool, ToolExecution


class ExecutionState(Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class ExecutionTask:
    task_id: str
    intent_id: str
    tool_id: str
    parameters: Dict[str, Any]
    priority: int = 3
    state: ExecutionState = ExecutionState.IDLE
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "intent_id": self.intent_id,
            "tool_id": self.tool_id,
            "parameters": self.parameters,
            "priority": self.priority,
            "state": self.state.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionPlan:
    plan_id: str
    intent_id: str
    tasks: List[ExecutionTask]
    current_task_index: int = 0
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_current_task(self) -> Optional[ExecutionTask]:
        if 0 <= self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None
    
    def advance_task(self):
        self.current_task_index += 1
    
    def is_complete(self) -> bool:
        return self.current_task_index >= len(self.tasks)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "intent_id": self.intent_id,
            "tasks": [t.to_dict() for t in self.tasks],
            "current_task_index": self.current_task_index,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "results": self.results,
            "metadata": self.metadata,
        }


class ExecutionLayer:
    def __init__(self, protocol: Optional[ODEPProtocol] = None):
        self.tool_registry = ToolRegistry()
        self.protocol = protocol or ODEPProtocol()
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.active_tasks: Dict[str, ExecutionTask] = {}
        self.task_queue: List[ExecutionTask] = []
        self.state = ExecutionState.IDLE
        self.error_handlers: Dict[str, Callable] = {}
        self.pre_execution_hooks: List[Callable] = []
        self.post_execution_hooks: List[Callable] = []
        self.execution_history: List[ExecutionResult] = []
    
    def register_tool(self, tool: Tool) -> bool:
        return self.tool_registry.register_tool(tool)
    
    def unregister_tool(self, tool_id: str) -> bool:
        return self.tool_registry.unregister_tool(tool_id)
    
    def register_error_handler(self, error_type: str, handler: Callable):
        self.error_handlers[error_type] = handler
    
    def register_pre_execution_hook(self, hook: Callable):
        self.pre_execution_hooks.append(hook)
    
    def register_post_execution_hook(self, hook: Callable):
        self.post_execution_hooks.append(hook)
    
    def execute_intent(self, intent: ExecutionIntent) -> ExecutionResult:
        try:
            self.state = ExecutionState.EXECUTING
            
            for hook in self.pre_execution_hooks:
                try:
                    hook(intent)
                except Exception:
                    pass
            
            plan = self._create_execution_plan(intent)
            self.execution_plans[plan.plan_id] = plan
            
            result = self._execute_plan(plan)
            
            for hook in self.post_execution_hooks:
                try:
                    hook(plan, result)
                except Exception:
                    pass
            
            self.state = ExecutionState.IDLE
            return result
            
        except Exception as e:
            self.state = ExecutionState.ERROR
            return ExecutionResult(
                intent_id=intent.intent_id,
                status=ExecutionStatus.FAILED,
                error=str(e),
            )
    
    def _create_execution_plan(self, intent: ExecutionIntent) -> ExecutionPlan:
        actions = intent.parameters.get("action_sequence", [])
        
        plan_id = f"plan_{datetime.now().timestamp()}"
        
        tasks = []
        for i, action in enumerate(actions):
            task = ExecutionTask(
                task_id=f"task_{plan_id}_{i}",
                intent_id=intent.intent_id,
                tool_id=action.get("tool_id", "unknown"),
                parameters=action.get("parameters", {}),
                priority=intent.priority.value,
            )
            tasks.append(task)
        
        if not tasks:
            default_task = ExecutionTask(
                task_id=f"task_{plan_id}_0",
                intent_id=intent.intent_id,
                tool_id="default",
                parameters=intent.parameters,
                priority=intent.priority.value,
            )
            tasks.append(default_task)
        
        plan = ExecutionPlan(
            plan_id=plan_id,
            intent_id=intent.intent_id,
            tasks=tasks,
        )
        
        return plan
    
    def _execute_plan(self, plan: ExecutionPlan) -> ExecutionResult:
        plan.started_at = datetime.now()
        plan.status = "running"
        
        results = []
        
        while not plan.is_complete():
            task = plan.get_current_task()
            if not task:
                break
            
            task.state = ExecutionState.EXECUTING
            task.started_at = datetime.now()
            self.active_tasks[task.task_id] = task
            
            try:
                task_result = self._execute_task(task)
                task.state = ExecutionState.IDLE
                task.completed_at = datetime.now()
                task.result = task_result
                results.append(task_result)
                plan.results.append(task_result)
                
            except Exception as e:
                task.state = ExecutionState.ERROR
                task.error = str(e)
                task.completed_at = datetime.now()
                
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    continue
                
                plan.status = "failed"
                plan.completed_at = datetime.now()
                
                return ExecutionResult(
                    intent_id=plan.intent_id,
                    status=ExecutionStatus.FAILED,
                    output=results,
                    error=str(e),
                    metadata={"failed_task": task.task_id},
                )
            
            plan.advance_task()
        
        plan.status = "completed"
        plan.completed_at = datetime.now()
        
        execution_result = ExecutionResult(
            intent_id=plan.intent_id,
            status=ExecutionStatus.SUCCESS,
            output=results if len(results) > 1 else results[0] if results else None,
            execution_time_ms=(
                (plan.completed_at - plan.started_at).total_seconds() * 1000
                if plan.started_at else 0
            ),
            metadata={
                "plan_id": plan.plan_id,
                "task_count": len(plan.tasks),
            },
        )
        
        self.execution_history.append(execution_result)
        return execution_result
    
    def _execute_task(self, task: ExecutionTask) -> Any:
        tool = self.tool_registry.get_tool(task.tool_id)
        
        if not tool:
            raise ValueError(f"Tool not found: {task.tool_id}")
        
        execution = tool.execute(task.parameters)
        return execution.result if hasattr(execution, 'result') else execution
    
    def execute_single(
        self,
        tool_id: str,
        parameters: Dict[str, Any]
    ) -> Any:
        tool = self.tool_registry.get_tool(tool_id)
        
        if not tool:
            raise ValueError(f"Tool not found: {tool_id}")
        
        execution = tool.execute(parameters)
        return execution.result if hasattr(execution, 'result') else execution
    
    def execute_batch(
        self,
        executions: List[Dict[str, Any]]
    ) -> List[Any]:
        results = []
        for exec_spec in executions:
            tool_id = exec_spec.get("tool_id")
            parameters = exec_spec.get("parameters", {})
            
            try:
                result = self.execute_single(tool_id, parameters)
                results.append({"success": True, "result": result})
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        
        return results
    
    def cancel_execution(self, plan_id: str) -> bool:
        if plan_id in self.execution_plans:
            plan = self.execution_plans[plan_id]
            plan.status = "cancelled"
            plan.completed_at = datetime.now()
            
            for task in plan.tasks:
                if task.task_id in self.active_tasks:
                    task.state = ExecutionState.STOPPED
            
            return True
        return False
    
    def get_plan_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        plan = self.execution_plans.get(plan_id)
        if plan:
            return plan.to_dict()
        return None
    
    def get_active_executions(self) -> List[Dict[str, Any]]:
        return [
            task.to_dict() 
            for task in self.active_tasks.values()
        ]
    
    def get_execution_summary(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "active_plans": len(self.execution_plans),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "total_executions": len(self.execution_history),
            "successful_executions": sum(
                1 for r in self.execution_history 
                if r.status == ExecutionStatus.SUCCESS
            ),
            "failed_executions": sum(
                1 for r in self.execution_history 
                if r.status == ExecutionStatus.FAILED
            ),
            "registered_tools": len(self.tool_registry.tools),
        }
    
    def get_tool_registry(self) -> ToolRegistry:
        return self.tool_registry
