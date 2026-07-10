import pytest
import tempfile
import os
import time
from perception.poller import (
    PollingStatus,
    ChangeType,
    WorkspaceChange,
    PollingConfig,
    BasePoller,
    FileSystemPoller,
    GitPoller,
    WorkspacePoller,
)


class TestChangeType:
    def test_change_type_values(self):
        assert ChangeType.FILE_CREATED.value == "file_created"
        assert ChangeType.FILE_MODIFIED.value == "file_modified"
        assert ChangeType.FILE_DELETED.value == "file_deleted"
        assert ChangeType.FILE_RENAMED.value == "file_renamed"
        assert ChangeType.DIR_CREATED.value == "dir_created"
        assert ChangeType.DIR_DELETED.value == "dir_deleted"
        assert ChangeType.GIT_CHANGED.value == "git_changed"


class TestWorkspaceChange:
    def test_to_dict(self):
        change = WorkspaceChange(
            change_id="test_1",
            change_type=ChangeType.FILE_CREATED,
            path="test.py",
            previous_path=None,
            metadata={"size": 100},
        )
        data = change.to_dict()
        assert data["change_id"] == "test_1"
        assert data["change_type"] == "file_created"
        assert data["path"] == "test.py"
        assert data["previous_path"] is None
        assert data["metadata"] == {"size": 100}
        assert "timestamp" in data


class TestPollingConfig:
    def test_default_config(self):
        config = PollingConfig()
        assert config.poll_interval_seconds == 5.0
        assert config.max_changes_per_poll == 100
        assert "*.py" in config.include_patterns
        assert "*.pyc" in config.exclude_patterns
        assert config.git_watch is True
        assert config.file_watch is True


class TestFileSystemPoller:
    @pytest.fixture
    def temp_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("initial content")
            yield tmpdir

    def test_detect_file_created(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        changes = poller._detect_changes()
        assert len(changes) >= 1
        assert changes[0].change_type == ChangeType.FILE_CREATED
        assert changes[0].path == "test.py"

    def test_detect_file_modified(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        poller._detect_changes()

        time.sleep(0.1)
        with open(os.path.join(temp_workspace, "test.py"), "w") as f:
            f.write("modified content")

        changes = poller._detect_changes()
        assert len(changes) >= 1
        assert changes[0].change_type == ChangeType.FILE_MODIFIED

    def test_detect_file_deleted(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        poller._detect_changes()

        os.remove(os.path.join(temp_workspace, "test.py"))

        changes = poller._detect_changes()
        assert len(changes) >= 1
        assert changes[0].change_type == ChangeType.FILE_DELETED

    def test_exclude_patterns(self, temp_workspace):
        os.makedirs(os.path.join(temp_workspace, "__pycache__"), exist_ok=True)
        with open(os.path.join(temp_workspace, "__pycache__", "test.pyc"), "w") as f:
            f.write("compiled")
        poller = FileSystemPoller(temp_workspace)
        changes = poller._detect_changes()
        pyc_changes = [c for c in changes if ".pyc" in c.path]
        assert len(pyc_changes) == 0

    def test_start_stop(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        assert poller.status == PollingStatus.STOPPED

        poller.start()
        assert poller.status == PollingStatus.RUNNING

        poller.stop()
        assert poller.status == PollingStatus.STOPPED

    def test_pause_resume(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        poller.start()
        poller.pause()
        assert poller.status == PollingStatus.PAUSED

        poller.resume()
        assert poller.status == PollingStatus.RUNNING
        poller.stop()

    def test_callbacks(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        callback_results = []

        def callback(changes):
            callback_results.extend(changes)

        poller.add_callback(callback)
        changes = poller._detect_changes()
        if changes:
            for cb in poller._callbacks:
                cb(changes)

        assert len(callback_results) >= 1

        poller.remove_callback(callback)
        callback_results.clear()
        changes = poller._detect_changes()
        if changes:
            for cb in poller._callbacks:
                cb(changes)

        assert len(callback_results) == 0

    def test_get_changes(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        changes = poller._detect_changes()
        poller._change_history.extend(changes)
        history = poller.get_changes(limit=5)
        assert len(history) >= 1

    def test_clear_history(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        changes = poller._detect_changes()
        poller._change_history.extend(changes)
        assert len(poller._change_history) >= 1

        poller.clear_history()
        assert len(poller._change_history) == 0

    def test_get_summary(self, temp_workspace):
        poller = FileSystemPoller(temp_workspace)
        summary = poller.get_summary()
        assert summary["status"] == "stopped"
        assert "poll_interval" in summary
        assert "total_changes_detected" in summary


class TestGitPoller:
    @pytest.fixture
    def temp_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_detect_git_changes_not_repo(self, temp_workspace):
        poller = GitPoller(temp_workspace)
        changes = poller._detect_changes()
        assert len(changes) == 0

    def test_get_summary(self, temp_workspace):
        poller = GitPoller(temp_workspace)
        summary = poller.get_summary()
        assert summary["status"] == "stopped"

    def test_start_stop(self, temp_workspace):
        poller = GitPoller(temp_workspace)
        poller.start()
        assert poller.status == PollingStatus.RUNNING
        poller.stop()
        assert poller.status == PollingStatus.STOPPED


class TestWorkspacePoller:
    @pytest.fixture
    def temp_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("content")
            yield tmpdir

    def test_init_with_all_pollers(self, temp_workspace):
        poller = WorkspacePoller(temp_workspace)
        assert len(poller.pollers) == 2

    def test_init_file_only(self, temp_workspace):
        config = PollingConfig(git_watch=False)
        poller = WorkspacePoller(temp_workspace, config)
        assert len(poller.pollers) == 1

    def test_start_stop(self, temp_workspace):
        poller = WorkspacePoller(temp_workspace)
        poller.start()
        poller.stop()

    def test_get_status(self, temp_workspace):
        poller = WorkspacePoller(temp_workspace)
        status = poller.get_status()
        assert "file_system" in status

    def test_set_poll_interval(self, temp_workspace):
        poller = WorkspacePoller(temp_workspace)
        poller.set_poll_interval(1.0)
        assert poller.config.poll_interval_seconds == 1.0