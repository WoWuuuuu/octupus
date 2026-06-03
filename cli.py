"""
Octopus CLI - Command Line Interface for Octopus System

Provides command-line interface for interacting with Octopus.
"""

import sys
import json
from typing import Optional, Dict, Any
from octopus.core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    LongTermMemory,
    EthicsFramework,
)
from octopus.execution import ExecutionLayer, ToolRegistry
from octopus.protocol import ODEPProtocol, ExecutionIntent, Priority


class OctopusCLI:
    def __init__(self):
        self.world_model = WorldModel()
        self.perception = PerceptionModule()
        self.simulation = SimulationEngine()
        self.decision = DecisionEngine()
        self.memory = LongTermMemory()
        self.ethics = EthicsFramework()
        self.execution = ExecutionLayer()
        self.protocol = ODEPProtocol()
        
        self._setup_components()
    
    def _setup_components(self):
        self.decision.set_world_model(self.world_model)
        self.decision.set_simulation_engine(self.simulation)
        
        default_guideline = self.ethics.create_default_guideline()
        self.ethics.add_guideline(default_guideline)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        parts = command.strip().split()
        if not parts:
            return {"error": "No command provided"}
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == "status":
            return self._get_status()
        elif cmd == "perceive":
            return self._perceive(" ".join(args))
        elif cmd == "decide":
            return self._make_decision(" ".join(args))
        elif cmd == "execute":
            return self._execute(" ".join(args))
        elif cmd == "memory":
            return self._check_memory()
        elif cmd == "help":
            return self._show_help()
        elif cmd == "exit":
            sys.exit(0)
        else:
            return {"error": f"Unknown command: {cmd}"}
    
    def _get_status(self) -> Dict[str, Any]:
        return {
            "world_model": self.world_model.get_state_summary(),
            "decision_engine": self.decision.get_decision_summary(),
            "execution_layer": self.execution.get_execution_summary(),
            "memory": self.memory.get_statistics(),
            "ethics": self.ethics.get_framework_summary(),
        }
    
    def _perceive(self, input_str: str) -> Dict[str, Any]:
        result = self.perception.perceive(input_str)
        return {
            "perception_result": result.to_dict(),
            "message": "Perception completed successfully"
        }
    
    def _make_decision(self, context_str: str) -> Dict[str, Any]:
        context = {"input": context_str, "timestamp": "now"}
        
        options = [
            {
                "name": "Option A",
                "description": "Execute action sequence A",
                "actions": [
                    {"tool_id": "default", "parameters": {"action": "test"}}
                ],
                "scores": {
                    "outcome_value": 0.8,
                    "risk_reduction": 0.6,
                    "reversibility": 0.7,
                    "confidence_alignment": 0.9
                }
            },
            {
                "name": "Option B",
                "description": "Execute action sequence B",
                "actions": [
                    {"tool_id": "default", "parameters": {"action": "alternative"}}
                ],
                "scores": {
                    "outcome_value": 0.7,
                    "risk_reduction": 0.8,
                    "reversibility": 0.9,
                    "confidence_alignment": 0.7
                }
            }
        ]
        
        decision = self.decision.make_decision(context, options)
        
        ethics_result = self.ethics.check_ethics(
            decision.execution_intent or {},
            context
        )
        
        return {
            "decision": decision.to_dict(),
            "ethics_check": ethics_result.to_dict(),
            "message": "Decision made successfully"
        }
    
    def _execute(self, intent_str: str) -> Dict[str, Any]:
        intent = ExecutionIntent(
            intent_id=f"intent_{id(self)}",
            action_type="execute",
            parameters={"action": intent_str},
            priority=Priority.NORMAL,
        )
        
        result = self.execution.execute_intent(intent)
        
        return {
            "execution_result": result.to_dict(),
            "message": "Execution completed"
        }
    
    def _check_memory(self) -> Dict[str, Any]:
        recent_memories = self.memory.search(limit=5)
        recent_outcomes = self.memory.get_recent_outcomes(limit=5)
        
        return {
            "recent_memories": [m.to_dict() for m in recent_memories],
            "recent_outcomes": [o.to_dict() for o in recent_outcomes],
            "statistics": self.memory.get_statistics(),
        }
    
    def _show_help(self) -> Dict[str, Any]:
        return {
            "commands": {
                "status": "Show system status and statistics",
                "perceive <input>": "Process input through perception module",
                "decide <context>": "Make a decision based on context",
                "execute <intent>": "Execute an intent",
                "memory": "Check memory statistics and recent items",
                "help": "Show this help message",
                "exit": "Exit the CLI",
            },
            "description": "Octopus - Decision-Execution Layer Separation Architecture"
        }
    
    def run_interactive(self):
        print("=" * 60)
        print("Octopus CLI - Decision-Execution Layer System")
        print("=" * 60)
        print("Type 'help' for available commands, 'exit' to quit")
        print()
        
        while True:
            try:
                command = input("octopus> ").strip()
                
                if not command:
                    continue
                
                result = self.process_command(command)
                print(json.dumps(result, indent=2, default=str))
                print()
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    cli = OctopusCLI()
    cli.run_interactive()


if __name__ == "__main__":
    main()
