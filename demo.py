
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import json
from core import (
    WorldModel,
    PerceptionModule,
    DecisionEngine,
    LongTermMemory,
)
from execution import ExecutionLayer
from protocol import ExecutionIntent, Priority


def run_demo():
    print("="*60)
    print("Octopus - Decision-Execution Architecture Demo")
    print("="*60)
    print()
    
    world_model = WorldModel()
    perception = PerceptionModule()
    decision = DecisionEngine()
    execution = ExecutionLayer()
    memory = LongTermMemory()
    
    print("System Components:")
    print("   - World Model: Loaded")
    print("   - Perception Module: Ready")
    print("   - Decision Engine: Active")
    print("   - Execution Layer: Online")
    print("   - Memory System: Prepared")
    print()
    
    while True:
        print("="*60)
        print("Available Commands:")
        print("1. status     - Show system status")
        print("2. perceive   - Analyze input (e.g., perceive hello)")
        print("3. decide     - Make decision (e.g., decide task)")
        print("4. execute    - Execute action (e.g., execute test)")
        print("5. memory     - Check memory")
        print("6. exit       - Quit")
        print("="*60)
        
        cmd = input("\nCommand: ").strip()
        
        if not cmd:
            continue
            
        parts = cmd.split()
        command = parts[0].lower()
        
        if command == "exit":
            print("Goodbye!")
            break
            
        elif command == "status":
            status = {
                "world_model": world_model.get_state_summary(),
                "decision_engine": decision.get_decision_summary(),
                "execution_layer": execution.get_execution_summary(),
                "memory": memory.get_statistics(),
            }
            print("\nSystem Status:")
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif command == "perceive":
            if len(parts) < 2:
                print("Usage: perceive <text>")
                continue
            text = " ".join(parts[1:])
            result = perception.perceive(text)
            print("\nPerception Result:")
            print("   Input: {}".format(text))
            if result.intents:
                print("   Intent: {}".format(result.intents[0].intent_type.value))
            else:
                print("   Intent: unknown")
            print("   Confidence: {}".format(result.confidence))
            
        elif command == "decide":
            if len(parts) < 2:
                print("Usage: decide <context>")
                continue
            context = " ".join(parts[1:])
            print("\nMaking decision for: {}".format(context))
            
            options = [
                {
                    "name": "Option A",
                    "description": "First choice",
                    "actions": [{"tool_id": "action", "parameters": {"do": "a"}}],
                    "scores": {"outcome_value": 0.8, "risk_reduction": 0.6, "reversibility": 0.7}
                },
                {
                    "name": "Option B",
                    "description": "Second choice",
                    "actions": [{"tool_id": "action", "parameters": {"do": "b"}}],
                    "scores": {"outcome_value": 0.7, "risk_reduction": 0.8, "reversibility": 0.9}
                }
            ]
            
            result = decision.make_decision({"input": context}, options)
            print("   Selected: {}".format(result.selected_option.name))
            print("   Reasoning: {}".format(result.reasoning))
            
        elif command == "execute":
            if len(parts) < 2:
                print("Usage: execute <action>")
                continue
            action = " ".join(parts[1:])
            print("\nExecuting: {}".format(action))
            
            intent = ExecutionIntent(
                intent_id="demo_intent",
                action_type="demo",
                parameters={"action": action},
                priority=Priority.NORMAL,
            )
            
            result = execution.execute_intent(intent)
            print("   Status: {}".format(result.status.value))
            if result.output:
                print("   Output: {}".format(result.output))
            
        elif command == "memory":
            memories = memory.search(limit=3)
            stats = memory.get_statistics()
            print("\nMemory System:")
            print("   Total Memories: {}".format(stats.get('total_memories', 0)))
            print("   Recent Memories:")
            for i, m in enumerate(memories, 1):
                print("     {}. {}".format(i, m.to_dict().get('content', 'None')))
                
        else:
            print("Unknown command: {}".format(command))
            print("Available: status, perceive, decide, execute, memory, exit")
            
        print("\nPress Enter to continue...")
        input()


if __name__ == "__main__":
    run_demo()
