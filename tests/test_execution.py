"""
Tests for Octopus Execution Layer Components
"""

import pytest
from datetime import datetime
from execution import (
    ExecutionLayer,
    ToolRegistry,
    Tool,
    ToolMetadata,
    ToolParameter,
    ToolCategory,
    ExecutionTask,
    ExecutionPlan,
    ExecutionState,
)
from protocol import (
    ODEPProtocol,
    ExecutionIntent,
    ExecutionResult,
    ExecutionStatus,
    Priority,
)


class TestToolRegistry:
    def test_create_tool_registry(self):
        registry = ToolRegistry()
        assert registry is not None
        assert len(registry.tools) == 0
    
    def test_register_tool(self):
        registry = ToolRegistry()
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        result = registry.register_tool(tool)
        assert result is True
        assert len(registry.tools) == 1
        assert registry.get_tool("test_tool") is not None
    
    def test_register_duplicate_tool(self):
        registry = ToolRegistry()
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        registry.register_tool(tool)
        result = registry.register_tool(tool)
        assert result is False
    
    def test_unregister_tool(self):
        registry = ToolRegistry()
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        registry.register_tool(tool)
        
        result = registry.unregister_tool("test_tool")
        assert result is True
        assert len(registry.tools) == 0
    
    def test_search_by_category(self):
        registry = ToolRegistry()
        
        metadata1 = ToolMetadata(
            tool_id="tool_1",
            name="Tool 1",
            description="Utility tool",
            category=ToolCategory.UTILITY,
        )
        metadata2 = ToolMetadata(
            tool_id="tool_2",
            name="Tool 2",
            description="Network tool",
            category=ToolCategory.NETWORK,
        )
        
        registry.register_tool(Tool(metadata1))
        registry.register_tool(Tool(metadata2))
        
        results = registry.get_tools_by_category(ToolCategory.UTILITY)
        assert len(results) == 1
        assert results[0].metadata.tool_id == "tool_1"
    
    def test_search_by_tags(self):
        registry = ToolRegistry()
        
        metadata1 = ToolMetadata(
            tool_id="tool_1",
            name="Tool 1",
            description="Tagged tool",
            category=ToolCategory.UTILITY,
            tags=["important", "urgent"],
        )
        metadata2 = ToolMetadata(
            tool_id="tool_2",
            name="Tool 2",
            description="Another tool",
            category=ToolCategory.UTILITY,
            tags=["important"],
        )
        
        registry.register_tool(Tool(metadata1))
        registry.register_tool(Tool(metadata2))
        
        results = registry.get_tools_by_tags(["urgent"])
        assert len(results) == 1
        assert results[0].metadata.tool_id == "tool_1"
    
    def test_search_by_query(self):
        registry = ToolRegistry()
        
        metadata1 = ToolMetadata(
            tool_id="calculator",
            name="Calculator",
            description="Mathematical calculator",
            category=ToolCategory.UTILITY,
        )
        metadata2 = ToolMetadata(
            tool_id="printer",
            name="Printer",
            description="Document printer",
            category=ToolCategory.UTILITY,
        )
        
        registry.register_tool(Tool(metadata1))
        registry.register_tool(Tool(metadata2))
        
        results = registry.search_tools(query="calculator")
        assert len(results) == 1
        assert results[0].metadata.tool_id == "calculator"


class TestTool:
    def test_create_tool(self):
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        assert tool is not None
        assert tool.metadata.tool_id == "test_tool"
    
    def test_tool_execution(self):
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        def executor(params):
            return params.get("value", 0) * 2
        
        tool.register_executor(executor)
        
        result = tool.execute({"value": 5})
        assert result.result == 10
    
    def test_tool_execution_error(self):
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        def failing_executor(params):
            raise ValueError("Test error")
        
        tool.register_executor(failing_executor)
        
        with pytest.raises(ValueError):
            tool.execute({})


class TestExecutionLayer:
    def test_create_execution_layer(self):
        execution = ExecutionLayer()
        assert execution is not None
        assert execution.state == ExecutionState.IDLE
    
    def test_register_tool(self):
        execution = ExecutionLayer()
        metadata = ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        result = execution.register_tool(tool)
        assert result is True
        assert len(execution.tool_registry.tools) == 1
    
    def test_execute_single(self):
        execution = ExecutionLayer()
        
        metadata = ToolMetadata(
            tool_id="adder",
            name="Adder",
            description="Adds two numbers",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        def adder_executor(params):
            return params.get("a", 0) + params.get("b", 0)
        
        tool.register_executor(adder_executor)
        execution.register_tool(tool)
        
        result = execution.execute_single("adder", {"a": 3, "b": 7})
        assert result == 10
    
    def test_execute_single_tool_not_found(self):
        execution = ExecutionLayer()
        
        with pytest.raises(ValueError):
            execution.execute_single("nonexistent", {})
    
    def test_execute_intent(self):
        execution = ExecutionLayer()
        
        metadata = ToolMetadata(
            tool_id="multiplier",
            name="Multiplier",
            description="Multiplies two numbers",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        def multiplier_executor(params):
            return params.get("a", 1) * params.get("b", 1)
        
        tool.register_executor(multiplier_executor)
        execution.register_tool(tool)
        
        intent = ExecutionIntent(
            intent_id="test_intent",
            action_type="multiply",
            parameters={
                "action_sequence": [
                    {"tool_id": "multiplier", "parameters": {"a": 4, "b": 5}}
                ]
            },
            priority=Priority.NORMAL,
        )
        
        result = execution.execute_intent(intent)
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output == 20
    
    def test_execute_batch(self):
        execution = ExecutionLayer()
        
        metadata = ToolMetadata(
            tool_id="doubler",
            name="Doubler",
            description="Doubles a number",
            category=ToolCategory.UTILITY,
        )
        tool = Tool(metadata)
        
        def doubler_executor(params):
            return params.get("value", 0) * 2
        
        tool.register_executor(doubler_executor)
        execution.register_tool(tool)
        
        executions = [
            {"tool_id": "doubler", "parameters": {"value": 5}},
            {"tool_id": "doubler", "parameters": {"value": 10}},
            {"tool_id": "doubler", "parameters": {"value": 15}},
        ]
        
        results = execution.execute_batch(executions)
        assert len(results) == 3
        assert results[0]["result"] == 10
        assert results[1]["result"] == 20
        assert results[2]["result"] == 30
    
    def test_get_execution_summary(self):
        execution = ExecutionLayer()
        summary = execution.get_execution_summary()
        
        assert "state" in summary
        assert "registered_tools" in summary
        assert summary["state"] == "idle"


class TestODEPProtocol:
    def test_create_protocol(self):
        protocol = ODEPProtocol()
        assert protocol is not None
        assert len(protocol.message_queue) == 0
    
    def test_send_execute_request(self):
        protocol = ODEPProtocol()
        
        intent = ExecutionIntent(
            intent_id="test_intent",
            action_type="test",
            parameters={"key": "value"},
            priority=Priority.NORMAL,
        )
        
        message = protocol.send_execute_request("decision", "execution", intent)
        assert message is not None
        assert message.message_type.value == "execute.request"
        assert len(protocol.message_queue) == 1
    
    def test_send_execute_response(self):
        protocol = ODEPProtocol()
        
        result = ExecutionResult(
            intent_id="test_intent",
            status=ExecutionStatus.SUCCESS,
            output={"data": "success"},
        )
        
        message = protocol.send_execute_response(
            "execution",
            "decision",
            result,
            "test_intent"
        )
        
        assert message is not None
        assert message.message_type.value == "execute.response"
        assert len(protocol.message_queue) == 1
    
    def test_send_state_update(self):
        protocol = ODEPProtocol()
        
        from protocol import WorldStateUpdate
        
        update = WorldStateUpdate(
            state_type="entity_update",
            changes={"key": "new_value"},
            source="test",
        )
        
        message = protocol.send_state_update("execution", "decision", update)
        assert message is not None
        assert message.message_type.value == "state.update"
    
    def test_pending_requests(self):
        protocol = ODEPProtocol()
        
        intent = ExecutionIntent(
            intent_id="pending_intent",
            action_type="test",
            parameters={},
            priority=Priority.NORMAL,
        )
        
        protocol.send_execute_request("decision", "execution", intent)
        
        pending = protocol.get_pending_request("pending_intent")
        assert pending is not None
        assert pending.correlation_id == "pending_intent"


class TestExecutionTask:
    def test_create_task(self):
        task = ExecutionTask(
            task_id="task_1",
            intent_id="intent_1",
            tool_id="tool_1",
            parameters={"param": "value"},
        )
        
        assert task is not None
        assert task.task_id == "task_1"
        assert task.state == ExecutionState.IDLE
    
    def test_task_to_dict(self):
        task = ExecutionTask(
            task_id="task_1",
            intent_id="intent_1",
            tool_id="tool_1",
            parameters={"param": "value"},
        )
        
        task_dict = task.to_dict()
        assert task_dict["task_id"] == "task_1"
        assert task_dict["state"] == "idle"


class TestExecutionPlan:
    def test_create_plan(self):
        plan = ExecutionPlan(
            plan_id="plan_1",
            intent_id="intent_1",
            tasks=[],
        )
        
        assert plan is not None
        assert plan.plan_id == "plan_1"
        assert plan.current_task_index == 0
    
    def test_advance_task(self):
        task1 = ExecutionTask(
            task_id="task_1",
            intent_id="intent_1",
            tool_id="tool_1",
            parameters={},
        )
        task2 = ExecutionTask(
            task_id="task_2",
            intent_id="intent_1",
            tool_id="tool_2",
            parameters={},
        )
        
        plan = ExecutionPlan(
            plan_id="plan_1",
            intent_id="intent_1",
            tasks=[task1, task2],
        )
        
        assert plan.get_current_task().task_id == "task_1"
        plan.advance_task()
        assert plan.get_current_task().task_id == "task_2"
    
    def test_is_complete(self):
        task = ExecutionTask(
            task_id="task_1",
            intent_id="intent_1",
            tool_id="tool_1",
            parameters={},
        )
        
        plan = ExecutionPlan(
            plan_id="plan_1",
            intent_id="intent_1",
            tasks=[task],
        )
        
        assert plan.is_complete() is False
        plan.advance_task()
        assert plan.is_complete() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
