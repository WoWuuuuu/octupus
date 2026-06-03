"""
Long-Term Memory - Memory system integration for Octopus Decision Layer

Provides persistent storage and retrieval of decision outcomes and learnings.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import json


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    WORKING = "working"


class MemoryRelevance(Enum):
    CRITICAL = 1.0
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.3
    IRRELEVANT = 0.0


@dataclass
class MemoryItem:
    memory_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    relevance: MemoryRelevance = MemoryRelevance.MEDIUM
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    expiration: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    embeddings: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "context": self.context,
            "relevance": self.relevance.value,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "created_at": self.created_at.isoformat(),
            "expiration": self.expiration.isoformat() if self.expiration else None,
            "tags": self.tags,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        data["memory_type"] = MemoryType(data["memory_type"])
        data["relevance"] = MemoryRelevance(data["relevance"])
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("expiration"):
            data["expiration"] = datetime.fromisoformat(data["expiration"])
        return cls(**data)


@dataclass
class DecisionOutcome:
    decision_id: str
    selected_option_id: str
    execution_result: Dict[str, Any]
    actual_outcome: Dict[str, Any]
    expected_vs_actual: Dict[str, float] = field(default_factory=dict)
    lessons_learned: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "selected_option_id": self.selected_option_id,
            "execution_result": self.execution_result,
            "actual_outcome": self.actual_outcome,
            "expected_vs_actual": self.expected_vs_actual,
            "lessons_learned": self.lessons_learned,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "metadata": self.metadata,
        }


class MemoryIndex:
    def __init__(self):
        self.by_type: Dict[MemoryType, List[str]] = {}
        self.by_tag: Dict[str, List[str]] = {}
        self.by_context: Dict[str, List[str]] = {}
        self.temporal_index: List[str] = []
    
    def index_memory(self, memory: MemoryItem):
        if memory.memory_type not in self.by_type:
            self.by_type[memory.memory_type] = []
        self.by_type[memory.memory_type].append(memory.memory_id)
        
        for tag in memory.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            self.by_tag[tag].append(memory.memory_id)
        
        for key, value in memory.context.items():
            context_key = f"{key}:{value}"
            if context_key not in self.by_context:
                self.by_context[context_key] = []
            self.by_context[context_key].append(memory.memory_id)
        
        self.temporal_index.append(memory.memory_id)
    
    def search_by_type(self, memory_type: MemoryType) -> List[str]:
        return self.by_type.get(memory_type, [])
    
    def search_by_tags(self, tags: List[str]) -> List[str]:
        result_sets = [set(self.by_tag.get(tag, [])) for tag in tags]
        if not result_sets:
            return []
        common = result_sets[0]
        for result_set in result_sets[1:]:
            common = common.intersection(result_set)
        return list(common)
    
    def search_by_context(self, context: Dict[str, Any]) -> List[str]:
        result_sets = []
        for key, value in context.items():
            context_key = f"{key}:{value}"
            if context_key in self.by_context:
                result_sets.append(set(self.by_context[context_key]))
        
        if not result_sets:
            return []
        
        common = result_sets[0]
        for result_set in result_sets[1:]:
            common = common.intersection(result_set)
        return list(common)


class LongTermMemory:
    def __init__(
        self,
        max_items: int = 10000,
        default_ttl: Optional[int] = None,
        enable_auto_cleanup: bool = True
    ):
        self.memories: Dict[str, MemoryItem] = {}
        self.index = MemoryIndex()
        self.outcomes: Dict[str, DecisionOutcome] = {}
        self.max_items = max_items
        self.default_ttl = default_ttl
        self.enable_auto_cleanup = enable_auto_cleanup
        self.embedder: Optional[Callable] = None
        self.access_policies: Dict[str, Callable] = {}
    
    def set_embedder(self, embedder: Callable):
        self.embedder = embedder
    
    def store(
        self,
        content: Dict[str, Any],
        memory_type: MemoryType = MemoryType.EPISODIC,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        relevance: MemoryRelevance = MemoryRelevance.MEDIUM,
        ttl_days: Optional[int] = None
    ) -> MemoryItem:
        memory_id = f"mem_{datetime.now().timestamp()}_{len(self.memories)}"
        
        expiration = None
        if ttl_days:
            expiration = datetime.now() + timedelta(days=ttl_days)
        elif self.default_ttl:
            expiration = datetime.now() + timedelta(days=self.default_ttl)
        
        memory = MemoryItem(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            context=context or {},
            relevance=relevance,
            expiration=expiration,
            tags=tags or [],
        )
        
        if self.embedder and memory_type == MemoryType.SEMANTIC:
            memory.embeddings = self.embedder(str(content))
        
        self.memories[memory_id] = memory
        self.index.index_memory(memory)
        
        self._enforce_capacity()
        
        return memory
    
    def retrieve(
        self,
        memory_id: str,
        increment_access: bool = True
    ) -> Optional[MemoryItem]:
        memory = self.memories.get(memory_id)
        
        if memory and increment_access:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
        
        return memory
    
    def search(
        self,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        candidate_ids = set()
        
        if memory_type:
            candidate_ids.update(self.index.search_by_type(memory_type))
        
        if tags:
            tag_results = self.index.search_by_tags(tags)
            if candidate_ids:
                candidate_ids = candidate_ids.intersection(set(tag_results))
            else:
                candidate_ids.update(tag_results)
        
        if context:
            context_results = self.index.search_by_context(context)
            if candidate_ids:
                candidate_ids = candidate_ids.intersection(set(context_results))
            else:
                candidate_ids.update(context_results)
        
        if not candidate_ids:
            candidate_ids = set(self.memories.keys())
        
        candidates = [
            self.memories[mid] for mid in candidate_ids 
            if mid in self.memories
        ]
        
        if query and self.embedder:
            candidates = self._semantic_search(candidates, query)
        
        candidates = self._filter_valid(candidates)
        
        candidates.sort(
            key=lambda m: (
                m.relevance.value,
                m.access_count,
                m.created_at
            ),
            reverse=True
        )
        
        return candidates[:limit]
    
    def _semantic_search(
        self,
        candidates: List[MemoryItem],
        query: str
    ) -> List[MemoryItem]:
        if not self.embedder:
            return candidates
        
        query_embedding = self.embedder(query)
        
        scored = []
        for memory in candidates:
            if memory.embeddings:
                similarity = self._cosine_similarity(
                    query_embedding, 
                    memory.embeddings
                )
                scored.append((memory, similarity))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored]
    
    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        if len(vec1) != len(vec2) or len(vec1) == 0:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _filter_valid(self, memories: List[MemoryItem]) -> List[MemoryItem]:
        valid = []
        now = datetime.now()
        
        for memory in memories:
            if memory.expiration and memory.expiration < now:
                continue
            valid.append(memory)
        
        return valid
    
    def _enforce_capacity(self):
        if len(self.memories) <= self.max_items:
            return
        
        excess = len(self.memories) - self.max_items
        
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: (
                m.relevance.value,
                m.access_count,
                m.created_at
            )
        )
        
        to_remove = sorted_memories[:excess]
        for memory in to_remove:
            del self.memories[memory.memory_id]
    
    def store_outcome(self, outcome: DecisionOutcome):
        self.outcomes[outcome.decision_id] = outcome
        
        self.store(
            content={
                "decision_id": outcome.decision_id,
                "selected_option_id": outcome.selected_option_id,
                "success": outcome.success,
                "lessons": outcome.lessons_learned,
            },
            memory_type=MemoryType.EPISODIC,
            context={"decision_id": outcome.decision_id},
            tags=["outcome", "decision"],
            relevance=(
                MemoryRelevance.CRITICAL if outcome.success 
                else MemoryRelevance.HIGH
            ),
        )
    
    def get_recent_outcomes(self, limit: int = 10) -> List[DecisionOutcome]:
        sorted_outcomes = sorted(
            self.outcomes.values(),
            key=lambda o: o.timestamp,
            reverse=True
        )
        return sorted_outcomes[:limit]
    
    def cleanup_expired(self) -> int:
        now = datetime.now()
        expired_ids = [
            mid for mid, memory in self.memories.items()
            if memory.expiration and memory.expiration < now
        ]
        
        for mid in expired_ids:
            del self.memories[mid]
        
        return len(expired_ids)
    
    def get_statistics(self) -> Dict[str, Any]:
        memory_types = {}
        for memory in self.memories.values():
            mem_type = memory.memory_type.value
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1
        
        return {
            "total_memories": len(self.memories),
            "memory_types": memory_types,
            "total_outcomes": len(self.outcomes),
            "successful_outcomes": sum(
                1 for o in self.outcomes.values() if o.success
            ),
            "max_capacity": self.max_items,
            "utilization": len(self.memories) / self.max_items if self.max_items > 0 else 0,
        }
