"""
Unit tests for Memory System (Episodic retrieval and float relevance coercion)
"""
import pytest
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.memory import LongTermMemory, MemoryType, MemoryRelevance, MemoryItem

def test_memory_indexing_and_retrieval():
    memory = LongTermMemory()
    
    # Store with tags and context
    memory.store(
        content={"event": "user_logged_in"},
        memory_type=MemoryType.EPISODIC,
        context={"user": "Alice"},
        tags=["auth", "login"]
    )
    
    # Query memory by tag
    results = memory.search(tags=["auth"])
    assert len(results) == 1
    assert results[0].content["event"] == "user_logged_in"
    
    # Query by context
    results_ctx = memory.search(context={"user": "Alice"})
    assert len(results_ctx) == 1

def test_relevance_float_coercion_and_sorting():
    memory = LongTermMemory()
    
    # Store using float value instead of Enum (simulates full_workflow demo inputs)
    memory.store(content={"info": "low_rel"}, relevance=0.3)
    memory.store(content={"info": "high_rel"}, relevance=0.8)
    
    # Search and sort
    results = memory.search()
    assert len(results) == 2
    # High relevance should be first in results list
    assert results[0].content["info"] == "high_rel"
    assert isinstance(results[0].relevance, MemoryRelevance)
    assert results[0].relevance == MemoryRelevance.HIGH
