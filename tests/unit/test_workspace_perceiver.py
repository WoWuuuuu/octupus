import pytest
from pathlib import Path
import tempfile
import os

from perception import (
    LocalWorkspacePerceiver,
    PerceptionResult,
    BudgetConfig,
)


class TestBudgetConfig:
    def test_is_file_allowed_allowed_extension(self):
        config = BudgetConfig()
        assert config.is_file_allowed(Path("test.py")) is True
        assert config.is_file_allowed(Path("README.md")) is True
        assert config.is_file_allowed(Path("config.json")) is True

    def test_is_file_allowed_excluded_pattern(self):
        config = BudgetConfig()
        assert config.is_file_allowed(Path("__pycache__")) is False
        assert config.is_file_allowed(Path(".git")) is False
        assert config.is_file_allowed(Path("test.pyc")) is False

    def test_is_file_allowed_disallowed_extension(self):
        config = BudgetConfig()
        assert config.is_file_allowed(Path("test.exe")) is False
        assert config.is_file_allowed(Path("image.png")) is False


class TestLocalWorkspacePerceiver:
    @pytest.fixture
    def temp_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "subdir"))
            with open(os.path.join(tmpdir, "test.py"), "w") as f:
                f.write("def hello():\n    return 'world'\n")
            with open(os.path.join(tmpdir, "README.md"), "w") as f:
                f.write("# Test Project\n")
            with open(os.path.join(tmpdir, "subdir", "nested.py"), "w") as f:
                f.write("nested code\n")
            yield Path(tmpdir)

    def test_read_file_success(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.read_file("test.py")
        assert result.success is True
        assert "def hello()" in result.data
        assert result.metadata["file_path"] == str(temp_workspace / "test.py")

    def test_read_file_not_found(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.read_file("nonexistent.py")
        assert result.success is False
        assert "File not found" in result.error

    def test_read_file_disallowed(self, temp_workspace):
        with open(os.path.join(temp_workspace, "test.exe"), "w") as f:
            f.write("binary content")
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.read_file("test.exe")
        assert result.success is False
        assert "File type not allowed" in result.error

    def test_repo_map(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.repo_map(depth=2)
        assert result.success is True
        assert result.data["name"] == temp_workspace.name
        assert result.data["type"] == "directory"
        child_names = [child["name"] for child in result.data["children"]]
        assert "test.py" in child_names
        assert "README.md" in child_names
        assert "subdir" in child_names

    def test_search(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.search("hello")
        assert result.success is True
        assert len(result.data) >= 1
        assert result.data[0]["file_path"] == "test.py"

    def test_search_no_results(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.search("nonexistent_pattern")
        assert result.success is True
        assert len(result.data) == 0

    def test_git_status_not_repo(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.git_status()
        assert result.success is False

    def test_git_diff_not_repo(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.git_diff()
        assert result.success is False

    def test_git_log_not_repo(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.git_log()
        assert result.success is False

    def test_read_url_invalid(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.read_url("http://nonexistent.invalid")
        assert result.success is False

    def test_read_url_timeout(self, temp_workspace):
        perceiver = LocalWorkspacePerceiver(root_path=str(temp_workspace))
        result = perceiver.read_url("http://10.255.255.1")
        assert result.success is False


class TestPerceptionResult:
    def test_to_dict(self):
        result = PerceptionResult(
            success=True,
            data={"key": "value"},
            metadata={"source": "test"}
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["data"] == {"key": "value"}
        assert d["metadata"] == {"source": "test"}
        assert d["error"] is None