"""
E-Commerce Refund Assistant - Practical Use Case for Octopus

Demonstrates how Octopus can be used in a real business scenario:
Automated refunds with risk simulation, financial constraints, and ethics guardrails.
"""

import sys
from pathlib import Path
import json

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import (
    WorldModel,
    PerceptionModule,
    SimulationEngine,
    DecisionEngine,
    DecisionPolicy,
    DecisionCriteria,
    LongTermMemory,
    EthicsFramework,
    Entity,
)
from core.ethics import EthicalGuideline, EthicalRule, ValueSystem, EthicalPrinciple
from execution import ExecutionLayer, Tool, ToolMetadata
from protocol import ExecutionIntent, Priority

def setup_refund_system():
    # 1. 初始化核心组件
    world_model = WorldModel()
    perception = PerceptionModule()
    simulation = SimulationEngine()
    decision = DecisionEngine()
    ethics = EthicsFramework()
    memory = LongTermMemory()
    execution = ExecutionLayer()
    
    decision.set_world_model(world_model)
    decision.set_simulation_engine(simulation)
    
    # 2. 设置决策策略：权衡“客户满意度”、“财务风险”和“可逆性”
    policy = DecisionPolicy(
        policy_id="refund_policy",
        name="Refund Policy",
        description="Policy to balance customer satisfaction and financial risk",
        criteria=[
            DecisionCriteria("customer_satisfaction", 0.5, "Maximize customer happiness"),
            DecisionCriteria("financial_safety", 0.3, "Minimize financial loss/fraud risk"),
            DecisionCriteria("reversibility", 0.2, "How easy it is to undo this operation"),
        ]
    )
    decision.add_policy(policy)
    
    # 3. 注册执行工具
    # 工具 1：自动退款 API
    refund_metadata = ToolMetadata(
        tool_id="instant_refund_api",
        name="Instant Refund API",
        description="Automatically process the refund and return money to the user's wallet",
        category="utility",
    )
    refund_tool = Tool(refund_metadata)
    refund_tool.register_executor(
        lambda params: f"【SUCCESS】Automatically refunded ${params.get('amount')} for Order {params.get('order_id')}."
    )
    execution.register_tool(refund_tool)
    
    # 工具 2：通知经理人工审批
    notify_metadata = ToolMetadata(
        tool_id="escalate_to_manager",
        name="Escalate to Manager",
        description="Notify the store manager to review this high-value refund request",
        category="utility",
    )
    notify_tool = Tool(notify_metadata)
    notify_tool.register_executor(
        lambda params: f"【NOTIFICATION SENT】Refund request of ${params.get('amount')} (Order {params.get('order_id')}) sent to Manager {params.get('manager_id', 'Admin')} for manual approval."
    )
    execution.register_tool(notify_tool)
    
    # 4. 注册伦理/财务风控规则 (Ethics Framework)
    # 硬约束规则：任何未经过经理人工审批的自动退款，金额不得超过 $100
    def refund_limit_rule_evaluator(action, context):
        tool_id = action.get("tool_id")
        params = action.get("parameters", {})
        amount = float(params.get("amount", 0))
        
        # 如果调用的是“自动退款API”且金额大于100，判定为【违规】（返回 True）
        if tool_id == "instant_refund_api" and amount > 100.0:
            return True # 违规，拦截！
        return False # 合规，放行
        
    value_system = ValueSystem(
        name="Financial Safety",
        description="Value system focused on financial risk control"
    )
    
    financial_guideline = EthicalGuideline(
        guideline_id="financial_risk_control",
        name="Financial Risk Control Guideline",
        description="Rules to prevent unauthorized financial payouts",
        value_system=value_system,
        rules=[
            EthicalRule(
                rule_id="max_auto_refund_limit",
                principle=EthicalPrinciple.SECURITY,
                description="Instant refunds cannot exceed $100 without manual audit",
                condition="tool_id == instant_refund_api and amount > 100",
                action="block",
                severity=3
            )
        ]
    )
    ethics.add_guideline(financial_guideline)
    ethics.register_rule_evaluator("max_auto_refund_limit", refund_limit_rule_evaluator)
    
    return {
        "world_model": world_model,
        "perception": perception,
        "decision": decision,
        "ethics": ethics,
        "execution": execution,
        "memory": memory
    }

def run_refund_case(system, user_name, order_id, amount, is_vip=False):
    print("\n" + "="*70)
    print(f"CASE: User '{user_name}' requests refund for Order '{order_id}' - Amount: ${amount}")
    print("="*70)
    
    world_model = system["world_model"]
    decision = system["decision"]
    ethics = system["ethics"]
    execution = system["execution"]
    memory = system["memory"]
    
    # Step 1: 更新世界模型 (录入当前用户信息和退款金额)
    customer = Entity(
        entity_id=f"user_{user_name}",
        entity_type="user",
        properties={"vip": is_vip, "risk_score": 0.1 if is_vip else 0.4}
    )
    world_model.add_entity(customer)
    world_model.add_goal(f"resolve_refund_{order_id}")
    
    # Step 2: 提供两个可行的决策选项
    # 选项 A：走自动退款 API 快速结案（高客户满意度，但有一定财务风险）
    # 选项 B：挂起并转人工审批（客户满意度中等，但安全性 100%）
    options = [
        {
            "name": "Option A: Auto Payout",
            "description": "Trigger Instant Refund API for rapid resolution",
            "actions": [{"tool_id": "instant_refund_api", "parameters": {"order_id": order_id, "amount": amount}}],
            "scores": {
                # VIP 客户的满意度权重更高
                "customer_satisfaction": 0.99 if is_vip else 0.8,
                "financial_safety": 0.5, # 自动退款有被薅羊毛的可能
                "reversibility": 0.2, # 钱一旦付出去，极难追回
            }
        },
        {
            "name": "Option B: Escalate to Manual Review",
            "description": "Escalate to store manager for safety audit",
            "actions": [{"tool_id": "escalate_to_manager", "parameters": {"order_id": order_id, "amount": amount, "manager_id": "Manager_Bob"}}],
            "scores": {
                "customer_satisfaction": 0.4, # 人工审批速度慢，客户满意度较低
                "financial_safety": 0.95, # 极其安全
                "reversibility": 0.9, # 还没付钱，随时可以取消，可逆性极高
            }
        }
    ]
    
    context = {"user_id": customer.entity_id, "order_id": order_id, "amount": amount}
    
    # Step 3: 决策引擎打分，选择最佳选项
    decision_result = decision.make_decision(context, options)
    print(f"[Decision] Preferred Option: {decision_result.selected_option.name}")
    print(f"[Reasoning] {decision_result.reasoning}")
    
    # Step 4: 伦理风控系统审查决策 (Ethics Check)
    # 获取选中的动作序列并审查
    intent_data = decision_result.execution_intent
    action_to_check = intent_data["parameters"]["action_sequence"][0]
    
    ethics_result = ethics.check_ethics(action_to_check, context)
    print(f"[Ethics Check] Status: {ethics_result.decision.value} (Score: {ethics_result.ethical_score})")
    
    # Step 5: 根据伦理审查结果执行动作
    if ethics_result.decision.value == "approved":
        # 伦理审查通过，正式下发指令给执行层 (触手)
        print("[Action] Executing preferred option...")
        intent = ExecutionIntent(
            intent_id=decision_result.decision_id,
            action_type="refund_payout",
            parameters=intent_data["parameters"],
            priority=Priority.NORMAL
        )
        exec_result = execution.execute_intent(intent)
        print(f"[Execution Result] {exec_result.output}")
        
    else:
        # 伦理审查拒绝！触发熔断，降级执行选项 B (转人工审核)
        print("[GUARDRAILS TRIGGERED] Auto payout REJECTED due to risk control limit! Falling back to Manual Review...")
        
        fallback_action = options[1] # Option B
        intent = ExecutionIntent(
            intent_id=decision_result.decision_id + "_fallback",
            action_type="escalation",
            parameters={"action_sequence": fallback_action["actions"]},
            priority=Priority.HIGH
        )
        exec_result = execution.execute_intent(intent)
        print(f"[Execution Result] {exec_result.output}")
        
    # Step 6: 存储结果到长期记忆库
    memory.store(
        content={
            "user": user_name,
            "order": order_id,
            "amount": amount,
            "approved": ethics_result.decision.value == "approved",
            "execution": exec_result.output
        },
        tags=["refund", "audit"]
    )
    print("[Memory] Saved transaction log to Long-Term Memory.")

def main():
    print("*"*75)
    print("OCTOPUS USE CASE: SMART REFUND AGENT WITH FINANCIAL SAFETY GUARDRAILS")
    print("*"*75)
    
    # 搭建退款系统
    system = setup_refund_system()
    
    # 场景一：VIP 客户申请小额退款（$30）
    # 预期：决策引擎倾向于自动退款（提升满意度），且没有触发伦理熔断限额（$30 <= $100），顺利自动打款。
    run_refund_case(system, user_name="Alice", order_id="ORD-9921", amount=30.0, is_vip=True)
    
    # 场景二：VIP 客户申请大额退款（$150）
    # 预期：决策引擎依然会因为打分偏向自动退款（Option A），但在发出命令前被伦理风控强制熔断拒绝（$150 > $100）。
    # 系统安全降级，执行选项 B，将请求安全流转给经理 Bob 人工审核。
    run_refund_case(system, user_name="Charlie", order_id="ORD-8854", amount=150.0, is_vip=True)

if __name__ == "__main__":
    main()
