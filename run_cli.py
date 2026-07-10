import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import json
from core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    LongTermMemory,
    EthicsFramework,
)
from execution import ExecutionLayer
from protocol import ExecutionIntent, Priority


def run_demo():
    print("="*60)
    print("Octopus - 决策-执行分离系统")
    print("="*60)
    print()
    print("这是一个简单的演示，展示大脑(决策)和触手(执行)的协作")
    print()
    
    world_model = WorldModel()
    perception = PerceptionModule()
    decision = DecisionEngine()
    execution = ExecutionLayer()
    memory = LongTermMemory()
    
    print("系统已启动：")
    print("   - 世界模型已加载")
    print("   - 感知模块已就绪")
    print("   - 决策引擎已启动")
    print("   - 执行层已激活")
    print("   - 记忆系统已准备")
    print()
    
    while True:
        print("="*60)
        print("请输入命令：")
        print("1. status - 查看系统状态")
        print("2. perceive <输入> - 让系统理解你的输入")
        print("3. decide <场景> - 让系统做决策")
        print("4. execute <动作> - 执行一个动作")
        print("5. memory - 查看记忆")
        print("6. exit - 退出")
        print("="*60)
        
        cmd = input("\n你想做什么？ ").strip()
        
        if not cmd:
            continue
            
        parts = cmd.split()
        command = parts[0].lower()
        
        if command == "exit":
            print("再见！")
            break
            
        elif command == "status":
            status = {
                "世界模型": world_model.get_state_summary(),
                "决策引擎": decision.get_decision_summary(),
                "执行层": execution.get_execution_summary(),
                "记忆系统": memory.get_statistics(),
            }
            print("\n系统状态：")
            print(json.dumps(status, indent=2, ensure_ascii=False))
            
        elif command == "perceive":
            if len(parts) < 2:
                print("请输入要理解的内容，比如：perceive 帮我订明天的机票")
                continue
            text = " ".join(parts[1:])
            result = perception.perceive(text)
            print("\n感知结果：")
            print("   输入: {}".format(text))
            if result.intents:
                print("   识别到意图: {}".format(result.intents[0].intent_type.value))
            else:
                print("   识别到意图: 未识别")
            print("   置信度: {}".format(result.confidence))
            
        elif command == "decide":
            if len(parts) < 2:
                print("请输入决策场景，比如：decide 我周末应该去公园还是看电影")
                continue
            context = " ".join(parts[1:])
            print("\n正在为场景做决策: {}".format(context))
            
            options = [
                {
                    "name": "方案A",
                    "description": "选择第一个选项",
                    "actions": [{"tool_id": "action", "parameters": {"do": "option_a"}}],
                    "scores": {"outcome_value": 0.8, "risk_reduction": 0.6, "reversibility": 0.7}
                },
                {
                    "name": "方案B",
                    "description": "选择第二个选项",
                    "actions": [{"tool_id": "action", "parameters": {"do": "option_b"}}],
                    "scores": {"outcome_value": 0.7, "risk_reduction": 0.8, "reversibility": 0.9}
                }
            ]
            
            result = decision.make_decision({"input": context}, options)
            print("   选择: {}".format(result.selected_option.name))
            print("   原因: {}".format(result.reasoning))
            
        elif command == "execute":
            if len(parts) < 2:
                print("请输入要执行的动作，比如：execute say_hello")
                continue
            action = " ".join(parts[1:])
            print("\n正在执行: {}".format(action))
            
            intent = ExecutionIntent(
                intent_id="demo_intent",
                action_type="demo",
                parameters={"action": action},
                priority=Priority.NORMAL,
            )
            
            result = execution.execute_intent(intent)
            print("   状态: {}".format(result.status.value))
            if result.output:
                print("   结果: {}".format(result.output))
            
        elif command == "memory":
            memories = memory.search(limit=3)
            stats = memory.get_statistics()
            print("\n记忆系统：")
            print("   总记忆数: {}".format(stats.get('total_memories', 0)))
            print("   最近记忆:")
            for i, m in enumerate(memories, 1):
                print("     {}. {}".format(i, m.to_dict().get('content', '无')))
                
        else:
            print("未知命令: {}".format(command))
            print("可用命令: status, perceive, decide, execute, memory, exit")
            
        print("\n按回车键继续...")
        input()


if __name__ == "__main__":
    run_demo()
