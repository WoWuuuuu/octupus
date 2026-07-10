"""
Octopus - Decision-Execution Layer Separation Architecture

A brain (Decision Layer) and tentacles (Execution Layer) architecture
"""

__version__ = "0.1.0"
__author__ = "Octopus Team"

from core.decision_engine import DecisionEngine
from core.world_model import WorldModel
from core.perception import PerceptionModule
from core.simulation import SimulationEngine
from core.memory import LongTermMemory
from core.ethics import EthicsFramework
from execution.executor import ExecutionLayer
from execution.tools import ToolRegistry
from protocol.communication import ODEPProtocol

__all__ = [
    "DecisionEngine",
    "WorldModel",
    "PerceptionModule",
    "SimulationEngine",
    "LongTermMemory",
    "EthicsFramework",
    "ExecutionLayer",
    "ToolRegistry",
    "ODEPProtocol",
]
