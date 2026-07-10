import pytest
import tempfile
import os
from octopus.quickstart import ProjectTemplate, Quickstart


class TestProjectTemplate:
    def test_init(self):
        template = ProjectTemplate(
            name="test",
            description="Test template",
            files={"test.txt": "content"},
            directories=["dir1", "dir2"],
        )
        assert template.name == "test"
        assert template.description == "Test template"
        assert template.files == {"test.txt": "content"}
        assert template.directories == ["dir1", "dir2"]


class TestQuickstart:
    def test_list_templates(self):
        templates = Quickstart.list_templates()
        assert isinstance(templates, list)
        assert len(templates) >= 2
        names = [t["name"] for t in templates]
        assert "basic" in names
        assert "advanced" in names

    def test_get_template_details(self):
        template = Quickstart.get_template_details("basic")
        assert template is not None
        assert template.name == "basic"

    def test_get_template_details_not_found(self):
        template = Quickstart.get_template_details("nonexistent")
        assert template is None

    def test_create_project_basic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = Quickstart.create_project("test_project", "basic", tmpdir)
            assert result["project_name"] == "test_project"
            assert result["template"] == "basic"
            assert result["total_files"] > 0
            assert result["total_directories"] > 0

            project_dir = os.path.join(tmpdir, "test_project")
            assert os.path.exists(project_dir)
            assert os.path.exists(os.path.join(project_dir, "config", "application.yml"))
            assert os.path.exists(os.path.join(project_dir, "README.md"))

    def test_create_project_advanced(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = Quickstart.create_project("test_project_adv", "advanced", tmpdir)
            assert result["project_name"] == "test_project_adv"
            assert result["template"] == "advanced"

            project_dir = os.path.join(tmpdir, "test_project_adv")
            assert os.path.exists(project_dir)
            assert os.path.exists(os.path.join(project_dir, "agents"))
            assert os.path.exists(os.path.join(project_dir, "services"))

    def test_create_project_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "existing"))
            with pytest.raises(ValueError):
                Quickstart.create_project("existing", "basic", tmpdir)

    def test_create_project_invalid_template(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                Quickstart.create_project("test", "invalid_template", tmpdir)

    def test_template_variables_replaced(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Quickstart.create_project("my_project", "basic", tmpdir)
            readme_path = os.path.join(tmpdir, "my_project", "README.md")
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "my_project" in content
            assert "{{project_name}}" not in content

    def test_basic_template_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = Quickstart.create_project("basic_test", "basic", tmpdir)
            created_files = result["created_files"]

            expected_files = [
                "config/application.yml",
                ".env.example",
                "tools/__init__.py",
                "tools/custom_tools.py",
                "demo/basic_workflow.py",
                "tests/test_basic.py",
                "README.md",
            ]

            for expected in expected_files:
                assert expected in created_files, f"Missing expected file: {expected}"

    def test_advanced_template_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = Quickstart.create_project("adv_test", "advanced", tmpdir)
            created_files = result["created_files"]

            expected_files = [
                "config/application.yml",
                ".env.example",
                "tools/__init__.py",
                "tools/custom_tools.py",
                "agents/__init__.py",
                "agents/simple_agent.py",
                "services/__init__.py",
                "services/workspace_service.py",
                "demo/full_workflow.py",
                "tests/test_agent.py",
                "docs/ARCHITECTURE.md",
                "README.md",
            ]

            for expected in expected_files:
                assert expected in created_files, f"Missing expected file: {expected}"