"""
Unit tests for World Model (State snapshotting and rollback)
"""
import pytest
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.world_model import WorldModel, Entity

def test_entity_lifecycle():
    world = WorldModel()
    
    # 1. Add entity
    user = Entity(entity_id="user_1", entity_type="user", properties={"name": "Alice"})
    world.add_entity(user)
    assert len(world.entities) == 1
    assert world.get_entity("user_1").properties["name"] == "Alice"
    
    # 2. Update entity
    world.update_entity("user_1", {"name": "Alice Smith", "level": "VIP"})
    assert world.get_entity("user_1").properties["name"] == "Alice Smith"
    assert world.get_entity("user_1").properties["level"] == "VIP"
    
    # 3. Remove entity
    world.remove_entity("user_1")
    assert len(world.entities) == 0

def test_state_snapshot_and_rollback():
    world = WorldModel()
    world.set_global_state("cash", 100.0)
    user = Entity(entity_id="user_1", entity_type="user", properties={"name": "Alice"})
    world.add_entity(user)
    
    # Create Save Snapshot (存档)
    snapshot = world.create_snapshot()
    assert snapshot is not None
    
    # Modify state (做高风险操作)
    world.set_global_state("cash", 20.0)
    world.update_entity("user_1", {"name": "Bob"})
    
    # Rollback to Snapshot (回滚读档)
    success = world.restore_snapshot(snapshot.snapshot_id)
    assert success is True
    assert world.get_global_state("cash") == 100.0
    assert world.get_entity("user_1").properties["name"] == "Alice"
