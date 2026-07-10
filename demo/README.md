# Octopus Demos & Tests Guide

This directory contains executable demos and refined unit tests for the **Octopus** Decision-Execution Separation agent framework.

---

## 🎮 Executable Demos

These python scripts run interactively or programmatically to showcase different parts of the system. Run them from the project root.

| Filename | Purpose / Focus | How to Run |
|----------|-----------------|------------|
| `run_cli.py` | Interactive terminal interface to control the Agent. Type commands like `status`, `perceive`, `decide`, or `memory`. | `python demo/run_cli.py` |
| `refund_chat_bot.py` | Chatbot refund assistant that parses natural language inputs and performs automated refunds. | `python demo/refund_chat_bot.py` |
| `refund_agent_demo.py` | E-commerce refund agent scenario demonstrating decision making and financial risk/guardrails. | `python demo/refund_agent_demo.py` |
| `full_workflow_demo.py` | Runs the full 8-step simulation pipeline (Perception -> World Model -> Simulation -> Decision -> Ethics -> ODEP -> Tools -> Memory). | `python demo/full_workflow_demo.py` |
| `simple_workflow_demo.py` | Minimal programmatic API usage demo showing basic component creation and execution. | `python demo/simple_workflow_demo.py` |
| `experience_demo.py` | Integration reference guide detailing how to hook up local LLMs (Ollama) or closed APIs (OpenAI/LangChain). | `python demo/experience_demo.py` |

---

## 🧪 Refined Test Cases

Our unit/integration tests have been refactored into modular, feature-focused files inside the `tests/` subdirectory.

To run the entire test suite, execute `pytest` from the project root:
```bash
python -m pytest demo/tests/ -v
```

### Test Files Breakdown:
1. **`test_world_model.py`**
   - Highlights: World state tracking, entity management, and state snapshots with **rollback capabilities (存档与回滚)**.
2. **`test_decision_planning.py`**
   - Highlights: Tool registration/execution, DecisionEngine policy weights, and SimulationEngine multi-trajectory exploration.
3. **`test_ethics_guardrails.py`**
   - Highlights: EthicsFramework rules evaluation and critical action **blocking guardrails (风控熔断拦截)**.
4. **`test_memory_system.py`**
   - Highlights: Long-Term Memory indexing, episodic search, and defensive **float-to-enum relevance coercion**.
5. **`test_odep_protocol.py`**
   - Highlights: ODEP protocol pub/sub event bus and layer message correlation.
