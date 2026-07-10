"""
Octopus Quick Experience + LLM Integration Demo (Fixed)

体验 Octopus 项目并集成第三方 LLM
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    DecisionPolicy,
    DecisionCriteria,
    LongTermMemory,
    MemoryType,
    EthicsFramework,
    Entity,
)
from execution import ExecutionLayer, Tool, ToolMetadata
from protocol import ExecutionIntent, Priority


def create_llm_tool():
    """创建一个 LLM 工具（演示用）"""
    metadata = ToolMetadata(
        tool_id="llm_chat",
        name="LLM Chat",
        description="Chat with a language model",
        category="ai",
    )
    
    tool = Tool(metadata)
    
    def llm_executor(params):
        prompt = params.get("prompt", "Hello")
        
        responses = {
            "天气": "今天天气晴朗，25度，适合外出。",
            "时间": "现在是2026年5月27日。",
            "代码": "这是一个简单的Python函数：print('Hello World')",
        }
        
        for key, value in responses.items():
            if key in prompt:
                return f"LLM Response: {value}"
        
        return f"LLM Response: Received your message: '{prompt}', I'm learning!"
    
    tool.register_executor(llm_executor)
    return tool


def quick_experience():
    """快速体验 Octopus"""
    print("="*70)
    print("Octopus Quick Experience + LLM Integration")
    print("="*70)
    
    print("\n[1/6] Initializing components...")
    world_model = WorldModel()
    perception = PerceptionModule()
    simulation = SimulationEngine()
    decision = DecisionEngine()
    memory = LongTermMemory()
    ethics = EthicsFramework()
    execution = ExecutionLayer()
    
    print("   OK: World Model, Perception, Simulation, Decision")
    print("   OK: Memory, Ethics, Execution")
    
    print("\n[2/6] Setting decision policy...")
    policy = DecisionPolicy(
        policy_id="quick_policy",
        name="Quick Policy",
        description="Quick decision making",
        criteria=[
            DecisionCriteria("outcome_value", 0.4, "Result value"),
            DecisionCriteria("risk_reduction", 0.3, "Risk reduction"),
            DecisionCriteria("reversibility", 0.3, "Reversibility"),
        ],
    )
    decision.add_policy(policy)
    print("   OK: Policy loaded")
    
    print("\n[3/6] Registering tools...")
    
    llm_tool = create_llm_tool()
    execution.register_tool(llm_tool)
    
    calc_metadata = ToolMetadata(
        tool_id="calculator",
        name="Calculator",
        description="Simple math calculation",
        category="utility",
    )
    calc_tool = Tool(calc_metadata)
    calc_tool.register_executor(lambda p: f"Calculation Result: {p['a']} + {p['b']} = {p['a'] + p['b']}")
    execution.register_tool(calc_tool)
    
    print("   OK: LLM Chat tool")
    print("   OK: Calculator tool")
    
    print("\n" + "="*70)
    print("Demo Scenarios")
    print("="*70)
    
    scenarios = [
        {
            "name": "Scenario 1: LLM Weather Query",
            "input": "Check today's weather",
            "tool_id": "llm_chat",
            "params": {"prompt": "天气"},
        },
        {
            "name": "Scenario 2: Calculator",
            "input": "Calculate 15 + 27",
            "tool_id": "calculator",
            "params": {"a": 15, "b": 27},
        },
        {
            "name": "Scenario 3: Decision Demo",
            "input": "Make an important decision",
            "decision": True,
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario: {scenario['name']}")
        print(f"User Input: {scenario['input']}")
        
        result = perception.perceive(scenario['input'])
        if result.intents:
            print(f"Perceived Intent: {result.intents[0].intent_type.value}")
            print(f"Confidence: {result.confidence:.2f}")
        
        if scenario.get('decision'):
            context = {"task": "important_decision"}
            options = [
                {
                    "name": "Conservative",
                    "description": "Safe, low risk",
                    "scores": {"outcome_value": 0.7, "risk_reduction": 0.9, "reversibility": 0.8},
                },
                {
                    "name": "Aggressive",
                    "description": "High risk, high reward",
                    "scores": {"outcome_value": 0.9, "risk_reduction": 0.4, "reversibility": 0.5},
                },
            ]
            
            decision_result = decision.make_decision(context, options)
            print(f"Decision: {decision_result.selected_option.name}")
            print(f"Reasoning: {decision_result.reasoning}")
            
        else:
            tool_id = scenario['tool_id']
            params = scenario['params']
            
            exec_result = execution.execute_single(tool_id, params)
            print(f"Execution Result: {exec_result}")
        
        memory.store(
            content={"scenario": scenario['name'], "input": scenario['input']},
            memory_type=MemoryType.EPISODIC,
            tags=["demo", f"scenario_{i}"],
        )
        
        print("Saved to memory")
    
    print("\n" + "="*70)
    print("Memory System Query")
    print("="*70)
    results = memory.search(tags=["demo"])
    print(f"Found {len(results)} memories:")
    for i, mem in enumerate(results[:3], 1):
        print(f"  {i}. {mem.content}")
    
    print("\n" + "="*70)
    print("Experience Complete!")
    print("="*70)


def llm_integration_guide():
    """LLM Integration Guide"""
    print("\n" + "="*70)
    print("LLM Integration Guide")
    print("="*70)
    
    guide = """
Method 1: Direct OpenAI GPT Integration

pip install openai

Example code:

from openai import OpenAI

def create_openai_tool(api_key):
    metadata = ToolMetadata(
        tool_id="openai_chat",
        name="OpenAI Chat",
        description="Chat with GPT",
        category="ai",
    )
    tool = Tool(metadata)
    
    client = OpenAI(api_key=api_key)
    
    def executor(params):
        prompt = params.get("prompt", "")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    tool.register_executor(executor)
    return tool


Method 2: Use LangChain for Multiple LLMs

pip install langchain langchain-openai

from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


Method 3: Local LLM (Ollama)

pip install ollama

import ollama

response = ollama.chat(model='llama2', messages=[
    {'role': 'user', 'content': 'Hello!'}
])


Best Practices:
1. Create an adapter layer for unified interface
2. Support multiple LLM backend switching
3. Add retry and error handling
4. Implement caching mechanism
    """
    print(guide)


if __name__ == "__main__":
    quick_experience()
    llm_integration_guide()
