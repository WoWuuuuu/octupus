"""
Octopus - Decision-Execution Layer Separation Architecture

A brain (Decision Layer) and tentacles (Execution Layer) architecture
"""

__version__ = "0.1.0"
__author__ = "Octopus Team"

from octopus.core.decision_engine import DecisionEngine
from octopus.core.world_model import WorldModel
from octopus.core.perception import PerceptionModule
from octopus.core.simulation import SimulationEngine
from octopus.core.memory import LongTermMemory
from octopus.core.ethics import EthicsFramework
from octopus.execution.executor import ExecutionLayer
from octopus.execution.tools import ToolRegistry
from octopus.protocol.communication import ODEPProtocol

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
