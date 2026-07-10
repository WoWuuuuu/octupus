import os
from core.llm_client import llm
from config import config

def main():
    print("="*50)
    config.print_config()
    
    print("\n[测试发送] : '你好，请用一句话介绍一下你自己。'")
    print("[正在等待大模型响应...]\n")
    
    try:
        response = llm.chat(
            prompt="你好，请用一句话介绍一下你自己。",
            system_prompt="你是一个友好的AI助手。",
            json_mode=False
        )
        print(f"🤖 [大模型回复]:\n{response}")
    except Exception as e:
        print(f"❌ [调用失败]: {e}")
        
    print("="*50)

if __name__ == "__main__":
    main()
