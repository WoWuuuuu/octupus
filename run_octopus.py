#!/usr/bin/env python3
"""
Octopus v1.0.0 一键运行脚本
决策-执行层分离系统
"""

import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_banner():
    banner = """
========================================
         Octopus v1.0.0
   决策-执行层分离系统
========================================
    """
    print(banner)


def install_dependencies():
    print("\n🔧 检查并安装依赖...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("✅ 依赖安装成功")
        else:
            print(f"⚠️  依赖安装警告:\n{result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print("⚠️  依赖安装超时，请手动安装: pip install -e .")
    except Exception as e:
        print(f"⚠️  依赖安装失败: {e}")


def init_system():
    print("\n🔄 正在初始化系统...")
    
    modules = [
        ("工作区感知模块", "perception", "LocalWorkspacePerceiver"),
        ("决策引擎", "core.decision_engine", "DecisionEngine"),
        ("会话管理系统", "core.session", "SessionStore"),
        ("批准机制", "core.approval", "ApprovalManager"),
        ("执行器管理器", "execution.executors", "ExecutorManager"),
        ("LLM提供商管理器", "core.llm_provider", "LLMProviderManager"),
        ("感知轮询系统", "perception.poller", "WorkspacePoller"),
        ("Doctor诊断工具", "octopus.doctor", "Doctor"),
        ("Quickstart脚手架", "octopus.quickstart", "Quickstart"),
    ]
    
    for name, module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            _ = getattr(module, class_name)
            print(f"✅ {name}已就绪")
        except Exception as e:
            print(f"⚠️  {name}加载失败: {e}")
    
    time.sleep(1)


def launch_cli():
    print("\n🖥️  启动交互式 CLI...")
    print("=" * 50)
    try:
        subprocess.run([sys.executable, "-m", "octopus.cli", "shell"])
    except KeyboardInterrupt:
        print("\n👋 CLI已退出")
    except Exception as e:
        print(f"❌ CLI启动失败: {e}")


def demo_perception():
    print("\n👁️  工作区感知演示")
    print("=" * 50)
    
    from perception import LocalWorkspacePerceiver
    perceiver = LocalWorkspacePerceiver()
    
    print("\n📁 项目目录结构:")
    result = perceiver.repo_map(depth=2)
    if result.success:
        print_tree(result.data)
    
    print("\n📄 读取README.md:")
    result = perceiver.read_file("README.md")
    if result.success:
        print(result.data[:300], "...")
    
    input("\n按回车键继续...")


def print_tree(node, indent=0):
    name = node.get("name", "")
    node_type = node.get("type", "")
    
    prefix = "  " * indent
    if node_type == "directory":
        print(f"{prefix}📁 {name}")
        for child in node.get("children", []):
            print_tree(child, indent + 1)
    elif node_type == "file":
        print(f"{prefix}📄 {name}")


def demo_decision():
    print("\n⚖️  决策引擎演示")
    print("=" * 50)
    
    from core.decision_engine import DecisionEngine, DecisionPolicy, DecisionCriteria
    
    engine = DecisionEngine()
    policy = DecisionPolicy(
        policy_id="demo_policy",
        name="Demo Policy",
        criteria=[
            DecisionCriteria("outcome_value", 0.40),
            DecisionCriteria("risk_reduction", 0.25),
            DecisionCriteria("reversibility", 0.20),
            DecisionCriteria("confidence_alignment", 0.15),
        ],
    )
    engine.add_policy(policy)
    
    goal = "我周末应该去公园还是看电影"
    print(f"\n决策目标: {goal}")
    
    options = [
        {
            "option_id": "option_1",
            "name": "去公园",
            "description": "户外活动，呼吸新鲜空气",
            "scores": {"outcome_value": 0.8, "risk_reduction": 0.9, "reversibility": 0.9, "confidence_alignment": 0.7},
        },
        {
            "option_id": "option_2",
            "name": "看电影",
            "description": "室内娱乐，放松心情",
            "scores": {"outcome_value": 0.7, "risk_reduction": 0.8, "reversibility": 0.8, "confidence_alignment": 0.8},
        },
    ]
    
    result = engine.make_decision({"goal": goal}, options)
    print(f"\n推荐选择: {result.selected_option.name}")
    print(f"置信度: {result.confidence:.2f}")
    print(f"理由: {result.reasoning[:100]}...")
    
    input("\n按回车键继续...")


def demo_session():
    print("\n📝 会话管理演示")
    print("=" * 50)
    
    from core.session import SessionStore
    
    store = SessionStore()
    
    print("\n创建演示会话...")
    session = store.create("周末计划", "讨论周末的活动安排")
    print(f"✅ 创建会话: {session.session_id[-20:]} - {session.title}")
    
    print("\n会话列表:")
    sessions = store.list()
    for s in sessions:
        print(f"   - {s.session_id[-20:]}: {s.title}")
    
    input("\n按回车键继续...")


def demo_approval():
    print("\n🔑 批准机制演示")
    print("=" * 50)
    
    from core.approval import ApprovalManager, ApprovalLevel
    
    manager = ApprovalManager()
    
    print("\n创建批准请求...")
    approval = manager.create_approval("demo_decision", "部署生产环境", ApprovalLevel.HIGH)
    print(f"✅ 创建批准请求: {approval.approval_id[-20:]}")
    print(f"   级别: {approval.level.value}")
    print(f"   状态: {approval.status.value}")
    
    print("\n批准该请求...")
    if manager.approve(approval.approval_id, reason="已完成代码审查"):
        print(f"✅ 请求已批准")
    
    input("\n按回车键继续...")


def demo_executor():
    print("\n🚀 执行器演示")
    print("=" * 50)
    
    from execution.executors import ExecutorManager
    
    manager = ExecutorManager()
    
    print("\n注册本地执行器...")
    manager.create_local_executor("local_demo")
    print("✅ 本地执行器已注册")
    
    print("\n执行器列表:")
    executors = manager.list_executors()
    for ex in executors:
        print(f"   - {ex.executor_id}: {ex.executor_type.value}")
    
    input("\n按回车键继续...")


def demo_doctor():
    print("\n👨‍⚕️  系统诊断演示")
    print("=" * 50)
    
    from octopus.doctor import Doctor
    
    doctor = Doctor()
    
    print("\n运行系统诊断...")
    summary = doctor.get_summary()
    print(f"✅ 诊断完成")
    print(f"   检查项: {summary.get('total_checks', 0)}")
    print(f"   通过: {summary.get('passed', 0)}")
    print(f"   警告: {summary.get('warnings', 0)}")
    print(f"   失败: {summary.get('failed', 0)}")
    
    input("\n按回车键继续...")


def demo_quickstart():
    print("\n📁 项目脚手架演示")
    print("=" * 50)
    
    from octopus.quickstart import Quickstart
    
    quickstart = Quickstart()
    
    print("\n可用模板:")
    templates = quickstart.list_templates()
    for name, template in templates.items():
        print(f"   - {name}: {template.description}")
    
    input("\n按回车键继续...")


def show_menu():
    menu = """
========================================
             功能菜单
========================================

1. 🖥️  启动交互式 CLI
2. 👁️  演示工作区感知
3. ⚖️  演示决策引擎
4. 📝  演示会话管理
5. 🔑  演示批准机制
6. 🚀  演示执行器
7. 👨‍⚕️  运行系统诊断
8. 📁  使用项目脚手架
9. ❌  退出

请选择功能 (1-9): 
"""
    return input(menu).strip()


def main():
    print_banner()
    
    install_dependencies()
    init_system()
    
    while True:
        choice = show_menu()
        
        if choice == "1":
            launch_cli()
        elif choice == "2":
            demo_perception()
        elif choice == "3":
            demo_decision()
        elif choice == "4":
            demo_session()
        elif choice == "5":
            demo_approval()
        elif choice == "6":
            demo_executor()
        elif choice == "7":
            demo_doctor()
        elif choice == "8":
            demo_quickstart()
        elif choice == "9":
            print("\n👋 感谢使用 Octopus！")
            break
        else:
            print("\n❌ 无效选择，请输入 1-9")


if __name__ == "__main__":
    main()
