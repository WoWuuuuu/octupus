from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import os
import shutil


@dataclass
class ProjectTemplate:
    name: str
    description: str
    files: Dict[str, str] = field(default_factory=dict)
    directories: List[str] = field(default_factory=list)


class Quickstart:
    TEMPLATES = {
        "basic": ProjectTemplate(
            name="basic",
            description="Basic Octopus project template",
            directories=[
                "config",
                "tools",
                "demo",
                "tests",
            ],
            files={
                "config/application.yml": """octopus:
  name: "{{project_name}}"
  version: "1.0.0"
  log_level: INFO

workspace:
  root_path: "./"
  max_files: 100
  max_chars_per_file: 10000

session:
  storage_path: "./data/sessions"

approval:
  storage_path: "./data/approvals"
  default_level: LOW
""",
                ".env.example": """# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Octopus Settings
OCTOPUS_LOG_LEVEL=INFO
""",
                "tools/__init__.py": "",
                "tools/custom_tools.py": """from execution import Tool, ToolMetadata, ToolCategory, ToolParameter


def create_greeting_tool() -> Tool:
    metadata = ToolMetadata(
        tool_id="greeting",
        name="Greeting Tool",
        description="Generate a greeting message",
        category=ToolCategory.UTILITY,
        parameters=[
            ToolParameter(
                name="name",
                param_type="string",
                description="Name to greet",
                required=True,
            ),
        ],
        return_type="string",
    )
    
    tool = Tool(metadata)
    
    def executor(params):
        name = params.get("name", "World")
        return f"Hello, {name}!"
    
    tool.register_executor(executor)
    return tool
""",
                "demo/basic_workflow.py": """from core.decision_engine import DecisionEngine, DecisionPolicy, DecisionCriteria
from core.decision_card import DecisionCardRenderer
from execution import ExecutorManager


def main():
    decision_engine = DecisionEngine()
    
    policy = DecisionPolicy(
        policy_id="default_policy",
        name="Default Decision Policy",
        description="Standard decision criteria",
        criteria=[
            DecisionCriteria("outcome_value", 0.40, "Value of outcome"),
            DecisionCriteria("risk_reduction", 0.25, "Risk reduction"),
            DecisionCriteria("reversibility", 0.20, "Ease of reversal"),
            DecisionCriteria("confidence_alignment", 0.15, "Confidence match"),
        ],
    )
    decision_engine.add_policy(policy)
    
    context = {"goal": "greet user", "priority": "high"}
    options = [
        {
            "option_id": "option_1",
            "name": "Formal Greeting",
            "description": "Professional greeting",
            "scores": {"outcome_value": 0.8, "risk_reduction": 0.9, "reversibility": 1.0, "confidence_alignment": 0.8},
        },
        {
            "option_id": "option_2",
            "name": "Casual Greeting",
            "description": "Friendly greeting",
            "scores": {"outcome_value": 0.7, "risk_reduction": 1.0, "reversibility": 1.0, "confidence_alignment": 0.9},
        },
    ]
    
    result = decision_engine.make_decision(context, options)
    
    if result.status.value == "decided":
        renderer = DecisionCardRenderer()
        card = renderer.render_from_decision(result)
        renderer.render(card)
    else:
        print(f"Decision failed: {result.reasoning}")


if __name__ == "__main__":
    main()
""",
                "tests/test_basic.py": """import pytest


def test_project_structure():
    assert True


def test_decision_engine():
    from core.decision_engine import DecisionEngine
    engine = DecisionEngine()
    assert engine is not None


def test_executor_manager():
    from execution import ExecutorManager
    manager = ExecutorManager()
    assert manager is not None
""",
                "README.md": """# {{project_name}}

An Octopus-based AI Agent project.

## Getting Started

### Installation

```bash
pip install -e .
```

### Run Demo

```bash
python demo/basic_workflow.py
```

### Start CLI

```bash
python -m octopus.cli shell
```

## Project Structure

```
{{project_name}}/
├── config/           # Configuration files
├── tools/            # Custom tools
├── demo/             # Demo scripts
├── tests/            # Test cases
└── README.md
```

## License

MIT License
""",
            },
        ),
        "advanced": ProjectTemplate(
            name="advanced",
            description="Advanced Octopus project template with full features",
            directories=[
                "config",
                "tools",
                "agents",
                "services",
                "demo",
                "tests",
                "docs",
            ],
            files={
                "config/application.yml": """octopus:
  name: "{{project_name}}"
  version: "1.0.0"
  log_level: DEBUG

workspace:
  root_path: "./"
  max_files: 200
  max_chars_per_file: 50000

session:
  storage_path: "./data/sessions"

approval:
  storage_path: "./data/approvals"
  default_level: MEDIUM

execution:
  default_executor: local
  executors:
    local:
      type: local
      max_concurrent_tasks: 10
""",
                ".env.example": """# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

# Octopus Settings
OCTOPUS_LOG_LEVEL=DEBUG
OCTOPUS_WORKSPACE_ROOT=./
""",
                "tools/__init__.py": "",
                "tools/custom_tools.py": """from execution import Tool, ToolMetadata, ToolCategory, ToolParameter


def create_greeting_tool() -> Tool:
    metadata = ToolMetadata(
        tool_id="greeting",
        name="Greeting Tool",
        description="Generate a greeting message",
        category=ToolCategory.UTILITY,
        parameters=[
            ToolParameter(
                name="name",
                param_type="string",
                description="Name to greet",
                required=True,
            ),
        ],
        return_type="string",
    )
    
    tool = Tool(metadata)
    
    def executor(params):
        name = params.get("name", "World")
        return f"Hello, {name}!"
    
    tool.register_executor(executor)
    return tool


def create_calculator_tool() -> Tool:
    metadata = ToolMetadata(
        tool_id="calculator",
        name="Calculator",
        description="Perform basic arithmetic operations",
        category=ToolCategory.UTILITY,
        parameters=[
            ToolParameter(
                name="operation",
                param_type="string",
                description="Arithmetic operation",
                required=True,
                options=["add", "subtract", "multiply", "divide"],
            ),
            ToolParameter(
                name="a",
                param_type="number",
                description="First number",
                required=True,
            ),
            ToolParameter(
                name="b",
                param_type="number",
                description="Second number",
                required=True,
            ),
        ],
        return_type="number",
    )
    
    tool = Tool(metadata)
    
    def executor(params):
        operation = params.get("operation")
        a = params.get("a")
        b = params.get("b")
        
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a / b if b != 0 else "Division by zero"
    
    tool.register_executor(executor)
    return tool
""",
                "agents/__init__.py": "",
                "agents/simple_agent.py": """from core.decision_engine import DecisionEngine, DecisionPolicy, DecisionCriteria
from core.session import SessionStore
from core.approval import ApprovalManager
from execution import ExecutorManager


class SimpleAgent:
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.session_store = SessionStore()
        self.approval_manager = ApprovalManager()
        self.executor_manager = ExecutorManager()
        
        self._init_policy()
        self._init_executor()
    
    def _init_policy(self):
        policy = DecisionPolicy(
            policy_id="agent_policy",
            name="Agent Decision Policy",
            description="Policy for agent decisions",
            criteria=[
                DecisionCriteria("outcome_value", 0.35),
                DecisionCriteria("risk_reduction", 0.25),
                DecisionCriteria("reversibility", 0.20),
                DecisionCriteria("confidence_alignment", 0.20),
            ],
        )
        self.decision_engine.add_policy(policy)
    
    def _init_executor(self):
        self.executor_manager.create_local_executor("local")
    
    def make_decision(self, goal: str, options: List[Dict]) -> Any:
        session = self.session_store.create(f"Decision: {goal}")
        
        context = {"goal": goal, "priority": "normal"}
        result = self.decision_engine.make_decision(context, options)
        
        if result.status.value == "decided":
            session.add_decision(result.decision_id)
            session.complete()
        
        return result
    
    def execute(self, tool_id: str, parameters: Dict) -> Any:
        return self.executor_manager.execute(tool_id, parameters)
""",
                "services/__init__.py": "",
                "services/workspace_service.py": """from perception import LocalWorkspacePerceiver, BudgetConfig


class WorkspaceService:
    def __init__(self):
        self.perceiver = LocalWorkspacePerceiver()
    
    def read_file(self, filepath: str) -> Any:
        return self.perceiver.read_file(filepath)
    
    def list_directory(self, depth: int = 2) -> Any:
        return self.perceiver.repo_map(depth=depth)
    
    def search(self, query: str) -> Any:
        return self.perceiver.search(query)
    
    def git_status(self) -> Any:
        return self.perceiver.git_status()
""",
                "demo/full_workflow.py": """from agents.simple_agent import SimpleAgent
from core.decision_card import DecisionCardRenderer


def main():
    agent = SimpleAgent()
    
    goal = "plan project structure"
    options = [
        {
            "option_id": "option_1",
            "name": "Monolithic Structure",
            "description": "Single codebase approach",
            "scores": {"outcome_value": 0.6, "risk_reduction": 0.8, "reversibility": 0.9, "confidence_alignment": 0.7},
        },
        {
            "option_id": "option_2",
            "name": "Microservices Structure",
            "description": "Distributed service approach",
            "scores": {"outcome_value": 0.8, "risk_reduction": 0.6, "reversibility": 0.5, "confidence_alignment": 0.8},
        },
        {
            "option_id": "option_3",
            "name": "Hybrid Structure",
            "description": "Combined approach",
            "scores": {"outcome_value": 0.7, "risk_reduction": 0.7, "reversibility": 0.7, "confidence_alignment": 0.7},
        },
    ]
    
    result = agent.make_decision(goal, options)
    
    if result.status.value == "decided":
        renderer = DecisionCardRenderer()
        card = renderer.render_from_decision(result)
        renderer.render(card)
    else:
        print(f"Decision failed: {result.reasoning}")


if __name__ == "__main__":
    main()
""",
                "tests/test_agent.py": """import pytest


def test_simple_agent():
    from agents.simple_agent import SimpleAgent
    agent = SimpleAgent()
    assert agent is not None
    assert agent.decision_engine is not None


def test_workspace_service():
    from services.workspace_service import WorkspaceService
    service = WorkspaceService()
    assert service is not None
""",
                "docs/ARCHITECTURE.md": """# {{project_name}} Architecture

## Overview

This project is built on Octopus, a decision-execution layer separation framework.

## Components

### Agents
- `agents/simple_agent.py`: Main agent implementation

### Services
- `services/workspace_service.py`: Workspace perception service

### Tools
- `tools/custom_tools.py`: Custom tool implementations

## Workflow

1. Receive input
2. Parse intent
3. Make decision
4. Request approval (if needed)
5. Execute action
6. Store result
""",
                "README.md": """# {{project_name}}

An advanced Octopus-based AI Agent project.

## Getting Started

### Installation

```bash
pip install -e .
```

### Run Demo

```bash
python demo/full_workflow.py
```

### Start CLI

```bash
python -m octopus.cli shell
```

### Check System Health

```bash
python -m octopus.cli doctor
```

## Project Structure

```
{{project_name}}/
├── agents/           # Agent implementations
├── services/         # Business services
├── tools/            # Custom tools
├── config/           # Configuration files
├── demo/             # Demo scripts
├── tests/            # Test cases
├── docs/             # Documentation
└── README.md
```

## License

MIT License
""",
            },
        ),
    }

    @classmethod
    def create_project(cls, project_name: str, template: str = "basic", output_dir: str = "./") -> Dict[str, Any]:
        if template not in cls.TEMPLATES:
            raise ValueError(f"Template '{template}' not found. Available: {list(cls.TEMPLATES.keys())}")

        template_data = cls.TEMPLATES[template]
        project_dir = os.path.join(output_dir, project_name)

        if os.path.exists(project_dir):
            raise ValueError(f"Directory '{project_dir}' already exists")

        os.makedirs(project_dir)

        for dir_name in template_data.directories:
            dir_path = os.path.join(project_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)

        created_files = []
        for file_path, content in template_data.files.items():
            content = content.replace("{{project_name}}", project_name)
            full_path = os.path.join(project_dir, file_path)
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(file_path)

        return {
            "project_name": project_name,
            "template": template,
            "project_dir": project_dir,
            "created_files": created_files,
            "total_files": len(created_files),
            "total_directories": len(template_data.directories),
        }

    @classmethod
    def list_templates(cls) -> List[Dict[str, str]]:
        return [
            {"name": name, "description": template.description}
            for name, template in cls.TEMPLATES.items()
        ]

    @classmethod
    def get_template_details(cls, template_name: str) -> Optional[ProjectTemplate]:
        return cls.TEMPLATES.get(template_name)