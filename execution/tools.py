"""
Tool Registry - Management and registration of execution tools for Octopus Execution Layer

Provides a registry for all executable tools and their metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum


class ToolCategory(Enum):
    CODE_EXECUTION = "code_execution"
    DATA_RETRIEVAL = "data_retrieval"
    FILE_OPERATIONS = "file_operations"
    NETWORK = "network"
    SYSTEM = "system"
    EXTERNAL_INTEGRATION = "external_integration"
    UTILITY = "utility"


class ToolStatus(Enum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"


@dataclass
class ToolParameter:
    name: str
    param_type: str
    description: str
    required: bool = True
    default: Any = None
    options: Optional[List[Any]] = None
    validation: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.param_type,
            "description": self.description,
            "required": self.required,
            "default": self.default,
            "options": self.options,
        }


@dataclass
class ToolMetadata:
    tool_id: str
    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    author: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: List[ToolParameter] = field(default_factory=list)
    return_type: str = "any"
    examples: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None
    timeout_seconds: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "author": self.author,
            "tags": self.tags,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "examples": self.examples,
            "constraints": self.constraints,
            "rate_limit": self.rate_limit,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
        }


@dataclass
class ToolExecution:
    execution_id: str
    tool_id: str
    parameters: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "tool_id": self.tool_id,
            "parameters": self.parameters,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


class Tool:
    def __init__(self, metadata: ToolMetadata):
        self.metadata = metadata
        self.executor: Optional[Callable] = None
        self.status = ToolStatus.AVAILABLE
        self.execution_history: List[ToolExecution] = []
    
    def register_executor(self, executor: Callable):
        self.executor = executor
    
    def execute(self, parameters: Dict[str, Any]) -> Any:
        if not self.executor:
            raise ValueError(f"No executor registered for tool {self.metadata.tool_id}")
        
        execution = ToolExecution(
            execution_id=f"exec_{datetime.now().timestamp()}",
            tool_id=self.metadata.tool_id,
            parameters=parameters,
            started_at=datetime.now(),
        )
        
        try:
            result = self.executor(parameters)
            execution.status = "success"
            execution.result = result
            execution.completed_at = datetime.now()
            execution.execution_time_ms = (
                execution.completed_at - execution.started_at
            ).total_seconds() * 1000
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.now()
            execution.execution_time_ms = (
                execution.completed_at - execution.started_at
            ).total_seconds() * 1000
            raise
        
        self.execution_history.append(execution)
        return execution


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        self.tags_index: Dict[str, List[str]] = {}
    
    def register_tool(self, tool: Tool) -> bool:
        tool_id = tool.metadata.tool_id
        
        if tool_id in self.tools:
            return False
        
        self.tools[tool_id] = tool
        
        category = tool.metadata.category
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(tool_id)
        
        for tag in tool.metadata.tags:
            if tag not in self.tags_index:
                self.tags_index[tag] = []
            self.tags_index[tag].append(tool_id)
        
        return True
    
    def get_tool(self, tool_id: str) -> Optional[Tool]:
        return self.tools.get(tool_id)
    
    def unregister_tool(self, tool_id: str) -> bool:
        if tool_id not in self.tools:
            return False
        
        tool = self.tools[tool_id]
        category = tool.metadata.category
        if category in self.categories:
            self.categories[category].remove(tool_id)
        
        for tag in tool.metadata.tags:
            if tag in self.tags_index:
                self.tags_index[tag].remove(tool_id)
        
        del self.tools[tool_id]
        return True
    
    def search_tools(
        self,
        category: Optional[ToolCategory] = None,
        tags: Optional[List[str]] = None,
        query: Optional[str] = None
    ) -> List[Tool]:
        results = set(self.tools.keys())
        
        if category:
            category_tools = set(self.categories.get(category, []))
            results = results.intersection(category_tools)
        
        if tags:
            for tag in tags:
                tag_tools = set(self.tags_index.get(tag, []))
                results = results.intersection(tag_tools)
        
        if query:
            query_lower = query.lower()
            query_results = set()
            for tool_id in results:
                tool = self.tools[tool_id]
                if (query_lower in tool.metadata.name.lower() or
                    query_lower in tool.metadata.description.lower()):
                    query_results.add(tool_id)
            results = results.intersection(query_results)
        
        return [self.tools[tid] for tid in results]
    
    def get_tools_by_category(self, category: ToolCategory) -> List[Tool]:
        tool_ids = self.categories.get(category, [])
        return [self.tools[tid] for tid in tool_ids if tid in self.tools]
    
    def get_tools_by_tags(self, tags: List[str]) -> List[Tool]:
        tool_ids_set = None
        for tag in tags:
            tag_tools = set(self.tags_index.get(tag, []))
            if tool_ids_set is None:
                tool_ids_set = tag_tools
            else:
                tool_ids_set = tool_ids_set.intersection(tag_tools)
        
        if not tool_ids_set:
            return []
        
        return [self.tools[tid] for tid in tool_ids_set if tid in self.tools]
    
    def get_tool_metadata(self, tool_id: str) -> Optional[Dict[str, Any]]:
        tool = self.tools.get(tool_id)
        if tool:
            return tool.metadata.to_dict()
        return None
    
    def get_all_metadata(self) -> List[Dict[str, Any]]:
        return [tool.metadata.to_dict() for tool in self.tools.values()]
    
    def get_registry_summary(self) -> Dict[str, Any]:
        category_counts = {
            cat.value: len(tool_ids) 
            for cat, tool_ids in self.categories.items()
        }
        
        return {
            "total_tools": len(self.tools),
            "categories": category_counts,
            "total_tags": len(self.tags_index),
            "tools_by_status": {
                "available": sum(
                    1 for t in self.tools.values() 
                    if t.status == ToolStatus.AVAILABLE
                ),
                "degraded": sum(
                    1 for t in self.tools.values() 
                    if t.status == ToolStatus.DEGRADED
                ),
                "unavailable": sum(
                    1 for t in self.tools.values() 
                    if t.status == ToolStatus.UNAVAILABLE
                ),
            },
        }


def create_code_execution_tool() -> Tool:
    metadata = ToolMetadata(
        tool_id="code_executor",
        name="Code Executor",
        description="Execute code in a sandboxed environment",
        category=ToolCategory.CODE_EXECUTION,
        parameters=[
            ToolParameter(
                name="code",
                param_type="string",
                description="Code to execute",
                required=True
            ),
            ToolParameter(
                name="language",
                param_type="string",
                description="Programming language",
                required=True,
                options=["python", "javascript", "bash"]
            ),
            ToolParameter(
                name="timeout",
                param_type="int",
                description="Execution timeout in seconds",
                required=False,
                default=30
            ),
        ],
        return_type="execution_result",
        constraints=["No file system access", "No network access"],
    )
    
    tool = Tool(metadata)
    return tool


def create_data_retrieval_tool() -> Tool:
    metadata = ToolMetadata(
        tool_id="data_retriever",
        name="Data Retriever",
        description="Retrieve data from configured data sources",
        category=ToolCategory.DATA_RETRIEVAL,
        parameters=[
            ToolParameter(
                name="query",
                param_type="string",
                description="Data retrieval query",
                required=True
            ),
            ToolParameter(
                name="source",
                param_type="string",
                description="Data source identifier",
                required=False,
                default="default"
            ),
        ],
        return_type="data",
    )
    
    tool = Tool(metadata)
    return tool
