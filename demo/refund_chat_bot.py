"""
Interactive Conversational Refund Bot - Chat UI for E-Commerce Refund Agent
"""

import sys
from pathlib import Path
import re

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from examples.refund_agent_demo import setup_refund_system, run_refund_case
from core import Entity
from protocol import ExecutionIntent, Priority

def parse_conversational_input(text):
    """
    用正则提取对话中的结构化参数：用户名、订单号、退款金额
    示例："我是 VIP 用户 Alice，订单 ORD-9921 退款 50 元"
    """
    text_lower = text.lower()
    
    # 提取用户名 (目前支持 demo 预设的 Alice, Charlie 等)
    user_name = "Guest"
    if "alice" in text_lower:
        user_name = "Alice"
    elif "charlie" in text_lower:
        user_name = "Charlie"
    elif "bob" in text_lower:
        user_name = "Bob"
        
    # 提取订单号 (如 ORD-12345 或 ord123)
    order_match = re.search(r'ord[-_]?\d+', text_lower)
    order_id = order_match.group(0).upper() if order_match else "ORD-UNKNOWN"
    
    # 提取退款金额 (数字)
    amount_match = re.search(r'\d+(\.\d+)?', text)
    # 如果用户没输金额，默认 50 元
    amount = float(amount_match.group(0)) if amount_match else 50.0
    
    # 判定是否包含 VIP 关键字
    is_vip = "vip" in text_lower
    
    return {
        "user_name": user_name,
        "order_id": order_id,
        "amount": amount,
        "is_vip": is_vip
    }

def start_chat():
    print("="*75)
    print("           OCTOPUS CHAT BOT - 智能客服退款助手 (对话版)             ")
    print("="*75)
    print("系统已经加载风控规则：自动秒退款限额为 $100。")
    print("说明：")
    print("  - 你可以扮演 VIP 客户 Alice（系统打分时更偏向用户满意度）")
    print("  - 也可以扮演普通客户 Charlie")
    print("  - 退出聊天请输入 'exit'")
    print("="*75)
    
    # 启动退款 Agent 引擎
    system = setup_refund_system()
    
    while True:
        try:
            user_input = input("\n[用户] 请输入你的请求 (如: 我是 VIP 客户 Alice, 订单 ORD-9921 申请退款 150元) \n> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == "exit":
                print("智能客服系统已关闭，再见！")
                break
                
            # 1. 语义感知解析 (将对话翻译为结构化参数)
            parsed = parse_conversational_input(user_input)
            
            print(f"\n【感知解析结果】 用户名: {parsed['user_name']} | VIP: {parsed['is_vip']} | 订单: {parsed['order_id']} | 金额: ${parsed['amount']}")
            
            # 2. 运行退款工作流
            run_refund_case(
                system=system,
                user_name=parsed["user_name"],
                order_id=parsed["order_id"],
                amount=parsed["amount"],
                is_vip=parsed["is_vip"]
            )
            
            print("\n" + "-"*50)
            
        except KeyboardInterrupt:
            print("\n系统强行终止。")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    start_chat()
