from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum
import threading
import time


class PollingStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class ChangeType(Enum):
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    FILE_DELETED = "file_deleted"
    FILE_RENAMED = "file_renamed"
    DIR_CREATED = "dir_created"
    DIR_DELETED = "dir_deleted"
    GIT_CHANGED = "git_changed"


@dataclass
class WorkspaceChange:
    change_id: str
    change_type: ChangeType
    path: str
    previous_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "path": self.path,
            "previous_path": self.previous_path,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class PollingConfig:
    poll_interval_seconds: float = 5.0
    max_changes_per_poll: int = 100
    include_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.md", "*.json"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["*.pyc", "__pycache__", ".git"])
    git_watch: bool = True
    file_watch: bool = True


class BasePoller(ABC):
    def __init__(self, config: PollingConfig = None):
        self.config = config or PollingConfig()
        self.status = PollingStatus.STOPPED
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._callbacks: List[Callable[[List[WorkspaceChange]], None]] = []
        self._change_history: List[WorkspaceChange] = []

    @abstractmethod
    def _detect_changes(self) -> List[WorkspaceChange]:
        pass

    def start(self):
        if self.status == PollingStatus.RUNNING:
            return
        self.status = PollingStatus.RUNNING
        self._stop_event.clear()
        self._pause_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.status = PollingStatus.STOPPED
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)

    def pause(self):
        if self.status == PollingStatus.RUNNING:
            self.status = PollingStatus.PAUSED
            self._pause_event.set()

    def resume(self):
        if self.status == PollingStatus.PAUSED:
            self.status = PollingStatus.RUNNING
            self._pause_event.clear()

    def add_callback(self, callback: Callable[[List[WorkspaceChange]], None]):
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[List[WorkspaceChange]], None]):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def get_changes(self, limit: int = 100) -> List[WorkspaceChange]:
        return self._change_history[-limit:]

    def clear_history(self):
        self._change_history.clear()

    def _poll_loop(self):
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.5)
                continue

            try:
                changes = self._detect_changes()
                if changes:
                    self._change_history.extend(changes)
                    for callback in self._callbacks:
                        try:
                            callback(changes)
                        except Exception:
                            pass
            except Exception:
                pass

            time.sleep(self.config.poll_interval_seconds)

    def get_status(self) -> PollingStatus:
        return self.status

    def get_summary(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "poll_interval": self.config.poll_interval_seconds,
            "total_changes_detected": len(self._change_history),
            "callbacks_registered": len(self._callbacks),
        }


class FileSystemPoller(BasePoller):
    def __init__(self, workspace_path: str, config: PollingConfig = None):
        super().__init__(config)
        self.workspace_path = workspace_path
        self._last_state: Dict[str, float] = {}

    def _detect_changes(self) -> List[WorkspaceChange]:
        import os

        changes: List[WorkspaceChange] = []
        current_state: Dict[str, float] = {}

        for root, dirs, files in os.walk(self.workspace_path):
            dirs[:] = [d for d in dirs if d not in self.config.exclude_patterns]

            for filename in files:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, self.workspace_path)

                if not self._matches_pattern(rel_path):
                    continue

                try:
                    mtime = os.path.getmtime(filepath)
                    current_state[rel_path] = mtime

                    if rel_path not in self._last_state:
                        changes.append(WorkspaceChange(
                            change_id=f"change_{datetime.now().timestamp()}",
                            change_type=ChangeType.FILE_CREATED,
                            path=rel_path,
                        ))
                    elif self._last_state[rel_path] != mtime:
                        changes.append(WorkspaceChange(
                            change_id=f"change_{datetime.now().timestamp()}",
                            change_type=ChangeType.FILE_MODIFIED,
                            path=rel_path,
                            metadata={"mtime": mtime},
                        ))
                except Exception:
                    pass

        for rel_path in self._last_state:
            if rel_path not in current_state:
                changes.append(WorkspaceChange(
                    change_id=f"change_{datetime.now().timestamp()}",
                    change_type=ChangeType.FILE_DELETED,
                    path=rel_path,
                ))

        self._last_state = current_state
        return changes[:self.config.max_changes_per_poll]

    def _matches_pattern(self, filepath: str) -> bool:
        import fnmatch

        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(filepath, pattern):
                return False

        if self.config.include_patterns:
            for pattern in self.config.include_patterns:
                if fnmatch.fnmatch(filepath, pattern):
                    return True
            return False

        return True


class GitPoller(BasePoller):
    def __init__(self, repo_path: str, config: PollingConfig = None):
        super().__init__(config)
        self.repo_path = repo_path
        self._last_status: Optional[str] = None
        self._last_diff: Optional[str] = None

    def _detect_changes(self) -> List[WorkspaceChange]:
        changes: List[WorkspaceChange] = []

        try:
            import subprocess

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            current_status = result.stdout

            if self._last_status is not None and current_status != self._last_status:
                changes.append(WorkspaceChange(
                    change_id=f"change_{datetime.now().timestamp()}",
                    change_type=ChangeType.GIT_CHANGED,
                    path=self.repo_path,
                    metadata={"status": current_status},
                ))

            self._last_status = current_status
        except Exception:
            pass

        return changes[:self.config.max_changes_per_poll]


class WorkspacePoller:
    def __init__(self, workspace_path: str, config: PollingConfig = None):
        self.workspace_path = workspace_path
        self.config = config or PollingConfig()
        self.pollers: List[BasePoller] = []

        if self.config.file_watch:
            self.file_poller = FileSystemPoller(workspace_path, config)
            self.pollers.append(self.file_poller)

        if self.config.git_watch:
            self.git_poller = GitPoller(workspace_path, config)
            self.pollers.append(self.git_poller)

    def start(self):
        for poller in self.pollers:
            poller.start()

    def stop(self):
        for poller in self.pollers:
            poller.stop()

    def pause(self):
        for poller in self.pollers:
            poller.pause()

    def resume(self):
        for poller in self.pollers:
            poller.resume()

    def add_callback(self, callback: Callable[[List[WorkspaceChange]], None]):
        for poller in self.pollers:
            poller.add_callback(callback)

    def get_changes(self, limit: int = 100) -> List[WorkspaceChange]:
        all_changes = []
        for poller in self.pollers:
            all_changes.extend(poller.get_changes(limit))
        all_changes.sort(key=lambda c: c.timestamp, reverse=True)
        return all_changes[:limit]

    def clear_history(self):
        for poller in self.pollers:
            poller.clear_history()

    def get_status(self) -> Dict[str, Any]:
        status = {}
        for poller in self.pollers:
            if isinstance(poller, FileSystemPoller):
                status["file_system"] = poller.get_summary()
            elif isinstance(poller, GitPoller):
                status["git"] = poller.get_summary()
        return status

    def set_poll_interval(self, interval_seconds: float):
        self.config.poll_interval_seconds = interval_seconds
        for poller in self.pollers:
            poller.config.poll_interval_seconds = interval_seconds