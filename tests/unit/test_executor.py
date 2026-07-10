import pytest
import tempfile
import os
from datetime import datetime
from execution.base import (
    ExecutorType,
    ExecutorStatus,
    ExecutorConfig,
    ExecutionJob,
    BaseExecutor,
)
from execution.executors import (
    LocalExecutor,
    RemoteExecutor,
    DockerExecutor,
    ExecutorManager,
)


class TestExecutorType:
    def test_values(self):
        assert ExecutorType.LOCAL.value == "local"
        assert ExecutorType.REMOTE.value == "remote"
        assert ExecutorType.DOCKER.value == "docker"
        assert ExecutorType.KUBERNETES.value == "kubernetes"
        assert ExecutorType.LAMBDA.value == "lambda"


class TestExecutorStatus:
    def test_values(self):
        assert ExecutorStatus.IDLE.value == "idle"
        assert ExecutorStatus.RUNNING.value == "running"
        assert ExecutorStatus.PAUSED.value == "paused"
        assert ExecutorStatus.STOPPED.value == "stopped"
        assert ExecutorStatus.ERROR.value == "error"
        assert ExecutorStatus.UNKNOWN.value == "unknown"


class TestExecutorConfig:
    def test_to_dict(self):
        config = ExecutorConfig(
            executor_id="test_exec",
            executor_type=ExecutorType.LOCAL,
            name="Test Executor",
            description="Test description",
            host="localhost",
            port=8080,
            timeout_seconds=300,
            max_concurrent_tasks=10,
            environment={"KEY": "VALUE"},
            config={"option": "value"},
        )
        data = config.to_dict()
        assert data["executor_id"] == "test_exec"
        assert data["executor_type"] == "local"
        assert data["name"] == "Test Executor"
        assert data["host"] == "localhost"
        assert data["port"] == 8080

    def test_default_values(self):
        config = ExecutorConfig(executor_id="test", executor_type=ExecutorType.LOCAL)
        assert config.name == ""
        assert config.port == 0
        assert config.timeout_seconds == 300
        assert config.max_concurrent_tasks == 10


class TestExecutionJob:
    def test_to_dict(self):
        job = ExecutionJob(
            job_id="test_job",
            executor_id="test_exec",
            task_id="task_1",
            tool_id="python_exec",
            parameters={"code": "print(1)"},
            status=ExecutorStatus.RUNNING,
            started_at=datetime.now(),
            result={"stdout": "1"},
            error=None,
            execution_time_ms=100.5,
            retry_count=0,
            max_retries=3,
        )
        data = job.to_dict()
        assert data["job_id"] == "test_job"
        assert data["executor_id"] == "test_exec"
        assert data["status"] == "running"
        assert data["result"] == {"stdout": "1"}
        assert data["execution_time_ms"] == 100.5


class TestLocalExecutor:
    def test_init(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        assert executor.config.executor_id == "local_test"
        assert executor.status == ExecutorStatus.IDLE

    def test_start_stop(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        executor.start()
        assert executor.status == ExecutorStatus.RUNNING
        executor.stop()
        assert executor.status == ExecutorStatus.STOPPED

    def test_pause_resume(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        executor.start()
        executor.pause()
        assert executor.status == ExecutorStatus.PAUSED
        executor.resume()
        assert executor.status == ExecutorStatus.RUNNING
        executor.stop()

    def test_execute_python(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        job = executor.execute("python_exec", {"code": "print('hello')"})
        assert job.job_id is not None
        assert job.status == ExecutorStatus.STOPPED
        assert job.result is not None
        assert "stdout" in job.result

    def test_execute_shell(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        job = executor.execute("shell_exec", {"command": "echo hello"})
        assert job.status == ExecutorStatus.STOPPED
        assert "stdout" in job.result

    def test_execute_file_read(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
            executor = LocalExecutor(config)
            job = executor.execute("file_read", {"filepath": temp_path})
            assert job.status == ExecutorStatus.STOPPED
            assert job.result["content"] == "test content"
        finally:
            os.unlink(temp_path)

    def test_execute_file_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = os.path.join(tmpdir, "output.txt")
            config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
            executor = LocalExecutor(config)
            job = executor.execute("file_write", {"filepath": temp_path, "content": "written content"})
            assert job.status == ExecutorStatus.STOPPED
            with open(temp_path, "r") as f:
                assert f.read() == "written content"

    def test_execute_batch(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        jobs = [
            {"tool_id": "python_exec", "parameters": {"code": "print(1)"}},
            {"tool_id": "python_exec", "parameters": {"code": "print(2)"}},
        ]
        results = executor.execute_batch(jobs)
        assert len(results) == 2
        assert results[0].status == ExecutorStatus.STOPPED

    def test_cancel_job(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        result = executor.cancel_job("nonexistent")
        assert result is False

    def test_get_job_status(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        status = executor.get_job_status("nonexistent")
        assert status is None

    def test_health_check(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        health = executor.health_check()
        assert health["status"] == "healthy"
        assert health["executor_id"] == "local_test"

    def test_get_summary(self):
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        executor.execute("python_exec", {"code": "print(1)"})
        summary = executor.get_summary()
        assert summary["executor_id"] == "local_test"
        assert summary["total_jobs"] == 1
        assert summary["active_jobs"] == 0


class TestRemoteExecutor:
    def test_init(self):
        config = ExecutorConfig(executor_id="remote_test", executor_type=ExecutorType.REMOTE)
        executor = RemoteExecutor(config)
        assert executor.config.executor_id == "remote_test"

    def test_start_stop(self):
        config = ExecutorConfig(executor_id="remote_test", executor_type=ExecutorType.REMOTE)
        executor = RemoteExecutor(config)
        executor.start()
        executor.stop()

    def test_health_check(self):
        config = ExecutorConfig(executor_id="remote_test", executor_type=ExecutorType.REMOTE)
        executor = RemoteExecutor(config)
        health = executor.health_check()
        assert health["status"] == "unhealthy"


class TestDockerExecutor:
    def test_init(self):
        config = ExecutorConfig(executor_id="docker_test", executor_type=ExecutorType.DOCKER)
        executor = DockerExecutor(config)
        assert executor.config.executor_id == "docker_test"

    def test_start_without_docker(self):
        config = ExecutorConfig(executor_id="docker_test", executor_type=ExecutorType.DOCKER)
        executor = DockerExecutor(config)
        result = executor.start()
        assert result is False
        assert executor.status == ExecutorStatus.ERROR

    def test_health_check_without_docker(self):
        config = ExecutorConfig(executor_id="docker_test", executor_type=ExecutorType.DOCKER)
        executor = DockerExecutor(config)
        health = executor.health_check()
        assert health["status"] == "unhealthy"


class TestExecutorManager:
    def test_init(self):
        manager = ExecutorManager()
        assert len(manager.executors) == 0
        assert manager.default_executor_id is None

    def test_register_executor(self):
        manager = ExecutorManager()
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        result = manager.register_executor(executor)
        assert result is True
        assert "local_test" in manager.executors
        assert manager.default_executor_id == "local_test"

    def test_register_duplicate_executor(self):
        manager = ExecutorManager()
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor1 = LocalExecutor(config)
        executor2 = LocalExecutor(config)
        manager.register_executor(executor1)
        result = manager.register_executor(executor2)
        assert result is False

    def test_get_executor(self):
        manager = ExecutorManager()
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        manager.register_executor(executor)

        retrieved = manager.get_executor("local_test")
        assert retrieved is not None

    def test_get_default_executor(self):
        manager = ExecutorManager()
        config = ExecutorConfig(executor_id="local_test", executor_type=ExecutorType.LOCAL)
        executor = LocalExecutor(config)
        manager.register_executor(executor)

        default = manager.get_executor()
        assert default is not None

    def test_get_executor_not_found(self):
        manager = ExecutorManager()
        result = manager.get_executor("nonexistent")
        assert result is None

    def test_execute(self):
        manager = ExecutorManager()
        manager.create_local_executor("local_test")

        job = manager.execute("python_exec", {"code": "print(1)"})
        assert job is not None
        assert job.status == ExecutorStatus.STOPPED

    def test_execute_no_executor(self):
        manager = ExecutorManager()
        with pytest.raises(ValueError):
            manager.execute("python_exec", {})

    def test_list_executors(self):
        manager = ExecutorManager()
        manager.create_local_executor("local_test")

        executors = manager.list_executors()
        assert len(executors) == 1
        assert executors[0]["executor_id"] == "local_test"

    def test_start_stop_all(self):
        manager = ExecutorManager()
        manager.create_local_executor("local_test")

        manager.start_all()
        manager.stop_all()

    def test_set_default_executor(self):
        manager = ExecutorManager()
        manager.create_local_executor("local_test")

        result = manager.set_default_executor("local_test")
        assert result is True

        result = manager.set_default_executor("nonexistent")
        assert result is False

    def test_get_health_summary(self):
        manager = ExecutorManager()
        manager.create_local_executor("local_test")

        health = manager.get_health_summary()
        assert "local_test" in health
        assert health["local_test"]["status"] == "healthy"

    def test_create_local_executor(self):
        manager = ExecutorManager()
        executor = manager.create_local_executor("local_test", "Test Local", "Local executor")
        assert isinstance(executor, LocalExecutor)
        assert "local_test" in manager.executors

    def test_create_remote_executor(self):
        manager = ExecutorManager()
        executor = manager.create_remote_executor("remote_test", "localhost", 8080)
        assert isinstance(executor, RemoteExecutor)
        assert "remote_test" in manager.executors

    def test_create_docker_executor(self):
        manager = ExecutorManager()
        executor = manager.create_docker_executor("docker_test")
        assert isinstance(executor, DockerExecutor)
        assert "docker_test" in manager.executors