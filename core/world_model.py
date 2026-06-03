"""
World Model - State representation and management for Octopus Decision Layer

Represents the understanding of the world state without direct tool invocation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import json


class StateConfidence(Enum):
    CERTAIN = 1.0
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    UNCERTAIN = 0.3


@dataclass
class Entity:
    entity_id: str
    entity_type: str
    properties: Dict[str, Any]
    relationships: Dict[str, List[str]] = field(default_factory=dict)
    confidence: float = 1.0
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_property(self, key: str, value: Any, confidence: float = 1.0):
        self.properties[key] = value
        self.confidence = min(self.confidence, confidence)
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "relationships": self.relationships,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class StateSnapshot:
    snapshot_id: str
    timestamp: datetime
    entities: Dict[str, Entity]
    global_state: Dict[str, Any]
    active_goals: List[str] = field(default_factory=list)
    pending_decisions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "global_state": self.global_state,
            "active_goals": self.active_goals,
            "pending_decisions": self.pending_decisions,
            "constraints": self.constraints,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateSnapshot':
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        data["entities"] = {
            k: Entity(**v) if isinstance(v, dict) else v 
            for k, v in data["entities"].items()
        }
        return cls(**data)


class WorldModel:
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.global_state: Dict[str, Any] = {}
        self.snapshots: List[StateSnapshot] = []
        self.state_history: List[Dict[str, Any]] = []
        self.confidence_threshold: float = 0.5
    
    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity
        self._record_state_change("entity_added", entity.entity_id)
    
    def update_entity(self, entity_id: str, properties: Dict[str, Any]) -> bool:
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        for key, value in properties.items():
            entity.update_property(key, value)
        
        self._record_state_change("entity_updated", entity_id)
        return True
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)
    
    def remove_entity(self, entity_id: str) -> bool:
        if entity_id in self.entities:
            del self.entities[entity_id]
            self._record_state_change("entity_removed", entity_id)
            return True
        return False
    
    def query_entities(
        self,
        entity_type: Optional[str] = None,
        properties_filter: Optional[Dict[str, Any]] = None
    ) -> List[Entity]:
        results = list(self.entities.values())
        
        if entity_type:
            results = [e for e in results if e.entity_type == entity_type]
        
        if properties_filter:
            def matches_filter(entity: Entity) -> bool:
                for key, value in properties_filter.items():
                    if key not in entity.properties:
                        return False
                    if isinstance(value, (list, set)):
                        if entity.properties[key] not in value:
                            return False
                    elif entity.properties[key] != value:
                        return False
                return True
            results = [e for e in results if matches_filter(e)]
        
        return results
    
    def set_global_state(self, key: str, value: Any) -> None:
        self.global_state[key] = value
        self._record_state_change("global_state_updated", key)
    
    def get_global_state(self, key: str, default: Any = None) -> Any:
        return self.global_state.get(key, default)
    
    def add_goal(self, goal_id: str) -> None:
        if goal_id not in self.global_state.get("active_goals", []):
            if "active_goals" not in self.global_state:
                self.global_state["active_goals"] = []
            self.global_state["active_goals"].append(goal_id)
            self._record_state_change("goal_added", goal_id)
    
    def remove_goal(self, goal_id: str) -> None:
        if "active_goals" in self.global_state:
            try:
                self.global_state["active_goals"].remove(goal_id)
                self._record_state_change("goal_removed", goal_id)
            except ValueError:
                pass
    
    def add_constraint(self, constraint: str) -> None:
        if "constraints" not in self.global_state:
            self.global_state["constraints"] = []
        if constraint not in self.global_state["constraints"]:
            self.global_state["constraints"].append(constraint)
            self._record_state_change("constraint_added", constraint)
    
    def check_constraint(self, constraint: str) -> bool:
        return constraint in self.global_state.get("constraints", [])
    
    def create_snapshot(self) -> StateSnapshot:
        snapshot = StateSnapshot(
            snapshot_id=f"snapshot_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            entities=dict(self.entities),
            global_state=dict(self.global_state),
            active_goals=self.global_state.get("active_goals", []),
            pending_decisions=self.global_state.get("pending_decisions", []),
            constraints=self.global_state.get("constraints", []),
        )
        self.snapshots.append(snapshot)
        return snapshot
    
    def restore_snapshot(self, snapshot_id: str) -> bool:
        for snapshot in self.snapshots:
            if snapshot.snapshot_id == snapshot_id:
                self.entities = dict(snapshot.entities)
                self.global_state = dict(snapshot.global_state)
                self._record_state_change("snapshot_restored", snapshot_id)
                return True
        return False
    
    def _record_state_change(self, change_type: str, entity_id: str) -> None:
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "change_type": change_type,
            "entity_id": entity_id,
        })
    
    def get_state_summary(self) -> Dict[str, Any]:
        return {
            "entity_count": len(self.entities),
            "entity_types": list(set(e.entity_type for e in self.entities.values())),
            "global_keys": list(self.global_state.keys()),
            "goal_count": len(self.global_state.get("active_goals", [])),
            "constraint_count": len(self.global_state.get("constraints", [])),
            "snapshot_count": len(self.snapshots),
            "history_length": len(self.state_history),
        }
    
    def export_state(self) -> str:
        return json.dumps({
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "global_state": self.global_state,
            "timestamp": datetime.now().isoformat(),
        }, default=str)
    
    def import_state(self, state_json: str) -> bool:
        try:
            data = json.loads(state_json)
            self.entities = {
                k: Entity(**v) for k, v in data.get("entities", {}).items()
            }
            self.global_state = data.get("global_state", {})
            return True
        except Exception:
            return False
