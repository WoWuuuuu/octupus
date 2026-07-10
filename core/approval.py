from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import json
import os
from protocol.v1.messages import ApprovalRequest, ApprovalResponse
from protocol.v1.enums import ApprovalStatus


class ApprovalLevel(Enum):
    AUTO = "auto"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalPolicy:
    def __init__(
        self,
        name: str,
        level: ApprovalLevel,
        requires_human: bool = False,
        timeout_seconds: int = 3600,
        max_retries: int = 3,
        conditions: Optional[List[Callable]] = None,
    ):
        self.name = name
        self.level = level
        self.requires_human = requires_human
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.conditions = conditions or []

    def should_require_approval(self, decision: Dict[str, Any]) -> bool:
        if self.level == ApprovalLevel.AUTO:
            return False
        for condition in self.conditions:
            if condition(decision):
                return True
        return True

    def get_required_approvers(self) -> List[str]:
        if self.level == ApprovalLevel.AUTO:
            return []
        elif self.level == ApprovalLevel.LOW:
            return ["system"]
        elif self.level == ApprovalLevel.MEDIUM:
            return ["reviewer"]
        elif self.level == ApprovalLevel.HIGH:
            return ["manager"]
        else:
            return ["admin", "manager"]


@dataclass
class ApprovalTask:
    approval_id: str
    decision_id: str
    decision_summary: str
    level: ApprovalLevel
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: str = "system"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "decision_id": self.decision_id,
            "decision_summary": self.decision_summary,
            "level": self.level.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "requested_by": self.requested_by,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "reason": self.reason,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApprovalTask':
        data = data.copy()
        data["level"] = ApprovalLevel(data["level"])
        data["status"] = ApprovalStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("approved_at"):
            data["approved_at"] = datetime.fromisoformat(data["approved_at"])
        return cls(**data)


class ApprovalManager:
    def __init__(self, storage_path: str = "data/approvals"):
        self.storage_path = storage_path
        self.approvals: Dict[str, ApprovalTask] = {}
        self.policies: Dict[str, ApprovalPolicy] = {}
        self.default_policy = ApprovalPolicy(
            name="default",
            level=ApprovalLevel.LOW,
            requires_human=False,
            timeout_seconds=3600,
        )
        self.policies["default"] = self.default_policy
        os.makedirs(self.storage_path, exist_ok=True)
        self._load_all()

    def _load_all(self):
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json") and not filename.startswith("_"):
                approval_id = filename[:-5]
                filepath = os.path.join(self.storage_path, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        approval = ApprovalTask.from_dict(data)
                        self.approvals[approval_id] = approval
                except Exception:
                    pass

    def _save_approval(self, approval: ApprovalTask):
        filepath = os.path.join(self.storage_path, f"{approval.approval_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(approval.to_dict(), f, indent=2, ensure_ascii=False)

    def add_policy(self, policy: ApprovalPolicy):
        self.policies[policy.name] = policy

    def get_policy(self, policy_name: str) -> ApprovalPolicy:
        return self.policies.get(policy_name, self.default_policy)

    def create_approval(
        self,
        decision_id: str,
        decision_summary: str,
        level: ApprovalLevel = ApprovalLevel.LOW,
        requested_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalTask:
        approval_id = f"approval_{datetime.now().timestamp()}"
        approval = ApprovalTask(
            approval_id=approval_id,
            decision_id=decision_id,
            decision_summary=decision_summary,
            level=level,
            status=ApprovalStatus.PENDING,
            requested_by=requested_by,
            metadata=metadata or {},
        )
        self.approvals[approval_id] = approval
        self._save_approval(approval)
        return approval

    def get_approval(self, approval_id: str) -> Optional[ApprovalTask]:
        return self.approvals.get(approval_id)

    def approve(self, approval_id: str, approved_by: str = "user", reason: Optional[str] = None) -> bool:
        approval = self.approvals.get(approval_id)
        if not approval or approval.status != ApprovalStatus.PENDING:
            return False

        approval.status = ApprovalStatus.APPROVED
        approval.approved_by = approved_by
        approval.approved_at = datetime.now()
        approval.reason = reason
        self._save_approval(approval)
        return True

    def reject(self, approval_id: str, approved_by: str = "user", reason: Optional[str] = None) -> bool:
        approval = self.approvals.get(approval_id)
        if not approval or approval.status != ApprovalStatus.PENDING:
            return False

        approval.status = ApprovalStatus.REJECTED
        approval.approved_by = approved_by
        approval.approved_at = datetime.now()
        approval.reason = reason
        self._save_approval(approval)
        return True

    def list_pending(self) -> List[ApprovalTask]:
        return sorted(
            [a for a in self.approvals.values() if a.status == ApprovalStatus.PENDING],
            key=lambda x: x.created_at,
            reverse=True,
        )

    def list_by_status(self, status: ApprovalStatus) -> List[ApprovalTask]:
        return sorted(
            [a for a in self.approvals.values() if a.status == status],
            key=lambda x: x.created_at,
            reverse=True,
        )

    def list_all(self) -> List[ApprovalTask]:
        return sorted(
            [a for a in self.approvals.values()],
            key=lambda x: x.created_at,
            reverse=True,
        )

    def check_approval_required(
        self,
        decision: Dict[str, Any],
        policy_name: str = "default",
    ) -> bool:
        policy = self.get_policy(policy_name)
        return policy.should_require_approval(decision)

    def get_decision_approval(self, decision_id: str) -> Optional[ApprovalTask]:
        for approval in self.approvals.values():
            if approval.decision_id == decision_id:
                return approval
        return None

    def is_approved(self, decision_id: str) -> bool:
        approval = self.get_decision_approval(decision_id)
        return approval is not None and approval.status == ApprovalStatus.APPROVED

    def create_approval_request(
        self,
        intent_id: str,
        intent: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        approval_id = f"approval_{datetime.now().timestamp()}"
        return ApprovalRequest(
            approval_id=approval_id,
            intent_id=intent_id,
            intent=intent,
            context=context or {},
        )

    def create_approval_response(
        self,
        approval_id: str,
        status: ApprovalStatus,
        reason: Optional[str] = None,
    ) -> ApprovalResponse:
        return ApprovalResponse(
            approval_id=approval_id,
            status=status,
            reason=reason,
        )

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.approvals)
        pending = sum(1 for a in self.approvals.values() if a.status == ApprovalStatus.PENDING)
        approved = sum(1 for a in self.approvals.values() if a.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for a in self.approvals.values() if a.status == ApprovalStatus.REJECTED)

        level_counts = {}
        for a in self.approvals.values():
            l = a.level.value
            level_counts[l] = level_counts.get(l, 0) + 1

        return {
            "total_approvals": total,
            "pending_approvals": pending,
            "approved_approvals": approved,
            "rejected_approvals": rejected,
            "approval_levels": level_counts,
            "total_policies": len(self.policies),
        }