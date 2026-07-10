"""
Octopus Models Package - Core Data Transfer Objects

This package contains all Pydantic models used for communication
between the Decision Brain and Execution Tentacles.
"""

from models.core_models import (
    # Enums
    TaskPriority,
    TaskStatus,
    ToolCategory,
    PlanStatus,
    ExecutionMode,
    
    # Tool Result Models (Tentacle → Brain)
    ToolMetadata,
    ToolParameter,
    ToolDefinition,
    ToolResult,
    
    # Task Request Models (Brain → Tentacle)
    TaskConstraints,
    TaskContext,
    TaskRequest,
    
    # Plan Models
    StepDependency,
    ExecutionStep,
    Plan,
    PlanValidation,
    
    # Communication Messages
    ExecutionRequest,
    ExecutionResponse,
    
    # Brain State Models
    WorldState,
    BrainThought,
    
    # Helper Functions
    create_task_request,
    create_plan,
    create_tool_result,
)

__all__ = [
    # Enums
    "TaskPriority",
    "TaskStatus",
    "ToolCategory",
    "PlanStatus",
    "ExecutionMode",
    
    # Tool Result
    "ToolMetadata",
    "ToolParameter", 
    "ToolDefinition",
    "ToolResult",
    
    # Task Request
    "TaskConstraints",
    "TaskContext",
    "TaskRequest",
    
    # Plan
    "StepDependency",
    "ExecutionStep",
    "Plan",
    "PlanValidation",
    
    # Communication
    "ExecutionRequest",
    "ExecutionResponse",
    
    # State
    "WorldState",
    "BrainThought",
    
    # Helpers
    "create_task_request",
    "create_plan",
    "create_tool_result",
]
