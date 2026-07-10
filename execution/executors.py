from typing import Any, Dict, List, Optional
from datetime import datetime
import subprocess
import json
import threading
import time
from execution.base import (
    BaseExecutor,
    ExecutorConfig,
    ExecutorStatus,
    ExecutionJob,
    ExecutorType,
)
from execution.tools import ToolRegistry


class LocalExecutor(BaseExecutor):
    def __init__(self, config: ExecutorConfig):
        super().__init__(config)
        self.tool_registry = ToolRegistry()
        self._shutdown_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def execute(self, tool_id: str, parameters: Dict[str, Any]) -> ExecutionJob:
        job = ExecutionJob(
            job_id=f"job_{datetime.now().timestamp()}",
            executor_id=self.config.executor_id,
            task_id=parameters.get("task_id", "unknown"),
            tool_id=tool_id,
            parameters=parameters,
        )

        job.status = ExecutorStatus.RUNNING
        job.started_at = datetime.now()
        self.active_jobs[job.job_id] = job

        try:
            result = self._execute_tool(tool_id, parameters)
            job.result = result
            job.status = ExecutorStatus.STOPPED
        except Exception as e:
            job.error = str(e)
            job.status = ExecutorStatus.ERROR

        job.completed_at = datetime.now()
        job.execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000

        del self.active_jobs[job.job_id]
        self.job_history.append(job)

        return job

    def _execute_tool(self, tool_id: str, parameters: Dict[str, Any]) -> Any:
        if tool_id == "python_exec":
            code = parameters.get("code", "")
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )
            return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}

        elif tool_id == "shell_exec":
            command = parameters.get("command", "")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
            )
            return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}

        elif tool_id == "file_read":
            filepath = parameters.get("filepath", "")
            with open(filepath, "r", encoding="utf-8") as f:
                return {"content": f.read()}

        elif tool_id == "file_write":
            filepath = parameters.get("filepath", "")
            content = parameters.get("content", "")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True}

        else:
            tool = self.tool_registry.get_tool(tool_id)
            if tool:
                execution = tool.execute(parameters)
                return execution.result if hasattr(execution, "result") else execution
            raise ValueError(f"Tool not found: {tool_id}")

    def execute_batch(self, jobs: List[Dict[str, Any]]) -> List[ExecutionJob]:
        results = []
        for job_spec in jobs:
            tool_id = job_spec.get("tool_id")
            parameters = job_spec.get("parameters", {})
            result = self.execute(tool_id, parameters)
            results.append(result)
        return results

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = ExecutorStatus.STOPPED
            job.error = "Cancelled"
            job.completed_at = datetime.now()
            del self.active_jobs[job_id]
            self.job_history.append(job)
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[ExecutionJob]:
        return self.active_jobs.get(job_id)

    def start(self) -> bool:
        self.status = ExecutorStatus.RUNNING
        self._shutdown_event.clear()
        return True

    def stop(self) -> bool:
        self.status = ExecutorStatus.STOPPED
        self._shutdown_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        return True

    def pause(self) -> bool:
        self.status = ExecutorStatus.PAUSED
        return True

    def resume(self) -> bool:
        self.status = ExecutorStatus.RUNNING
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "executor_id": self.config.executor_id,
            "type": "local",
            "active_jobs": len(self.active_jobs),
            "total_jobs": len(self.job_history),
        }

    def register_tool(self, tool):
        self.tool_registry.register_tool(tool)


class RemoteExecutor(BaseExecutor):
    def __init__(self, config: ExecutorConfig):
        super().__init__(config)
        self._client = None
        self._connected = False

    def execute(self, tool_id: str, parameters: Dict[str, Any]) -> ExecutionJob:
        job = ExecutionJob(
            job_id=f"job_{datetime.now().timestamp()}",
            executor_id=self.config.executor_id,
            task_id=parameters.get("task_id", "unknown"),
            tool_id=tool_id,
            parameters=parameters,
        )

        job.status = ExecutorStatus.RUNNING
        job.started_at = datetime.now()
        self.active_jobs[job.job_id] = job

        try:
            if not self._connected:
                self._connect()

            payload = {
                "action": "execute",
                "tool_id": tool_id,
                "parameters": parameters,
            }
            result = self._send_request(payload)
            job.result = result.get("result")
            job.status = ExecutorStatus.STOPPED
        except Exception as e:
            job.error = str(e)
            job.status = ExecutorStatus.ERROR

        job.completed_at = datetime.now()
        job.execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000

        del self.active_jobs[job.job_id]
        self.job_history.append(job)

        return job

    def _connect(self):
        try:
            import requests
            self._client = requests.Session()
            self._connected = True
        except ImportError:
            raise ValueError("requests library not installed")

    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            raise ValueError("Not connected")

        url = f"http://{self.config.host}:{self.config.port}/execute"
        response = self._client.post(url, json=payload, timeout=self.config.timeout_seconds)
        return response.json()

    def execute_batch(self, jobs: List[Dict[str, Any]]) -> List[ExecutionJob]:
        results = []
        for job_spec in jobs:
            tool_id = job_spec.get("tool_id")
            parameters = job_spec.get("parameters", {})
            result = self.execute(tool_id, parameters)
            results.append(result)
        return results

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = ExecutorStatus.STOPPED
            job.error = "Cancelled"
            job.completed_at = datetime.now()
            del self.active_jobs[job_id]
            self.job_history.append(job)
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[ExecutionJob]:
        return self.active_jobs.get(job_id)

    def start(self) -> bool:
        try:
            self._connect()
            self.status = ExecutorStatus.RUNNING
            return True
        except Exception:
            self.status = ExecutorStatus.ERROR
            return False

    def stop(self) -> bool:
        self.status = ExecutorStatus.STOPPED
        self._connected = False
        return True

    def pause(self) -> bool:
        self.status = ExecutorStatus.PAUSED
        return True

    def resume(self) -> bool:
        self.status = ExecutorStatus.RUNNING
        return True

    def health_check(self) -> Dict[str, Any]:
        try:
            if not self._connected:
                self._connect()
            url = f"http://{self.config.host}:{self.config.port}/health"
            response = self._client.get(url, timeout=5)
            return response.json()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


class DockerExecutor(BaseExecutor):
    def __init__(self, config: ExecutorConfig):
        super().__init__(config)
        self._container_id = None
        self._image = config.config.get("image", "python:3.11-slim")

    def execute(self, tool_id: str, parameters: Dict[str, Any]) -> ExecutionJob:
        job = ExecutionJob(
            job_id=f"job_{datetime.now().timestamp()}",
            executor_id=self.config.executor_id,
            task_id=parameters.get("task_id", "unknown"),
            tool_id=tool_id,
            parameters=parameters,
        )

        job.status = ExecutorStatus.RUNNING
        job.started_at = datetime.now()
        self.active_jobs[job.job_id] = job

        try:
            result = self._execute_in_container(tool_id, parameters)
            job.result = result
            job.status = ExecutorStatus.STOPPED
        except Exception as e:
            job.error = str(e)
            job.status = ExecutorStatus.ERROR

        job.completed_at = datetime.now()
        job.execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000

        del self.active_jobs[job.job_id]
        self.job_history.append(job)

        return job

    def _execute_in_container(self, tool_id: str, parameters: Dict[str, Any]) -> Any:
        try:
            import docker
            client = docker.from_env()

            if tool_id == "python_exec":
                code = parameters.get("code", "")
                command = ["python", "-c", code]
                result = client.containers.run(
                    self._image,
                    command=command,
                    detach=False,
                    remove=True,
                    timeout=self.config.timeout_seconds,
                )
                return {"stdout": result.decode("utf-8")}

            elif tool_id == "shell_exec":
                command = parameters.get("command", "")
                result = client.containers.run(
                    self._image,
                    command=["/bin/sh", "-c", command],
                    detach=False,
                    remove=True,
                    timeout=self.config.timeout_seconds,
                )
                return {"stdout": result.decode("utf-8")}

            else:
                raise ValueError(f"Unsupported tool for Docker: {tool_id}")

        except ImportError:
            raise ValueError("docker library not installed")

    def execute_batch(self, jobs: List[Dict[str, Any]]) -> List[ExecutionJob]:
        results = []
        for job_spec in jobs:
            tool_id = job_spec.get("tool_id")
            parameters = job_spec.get("parameters", {})
            result = self.execute(tool_id, parameters)
            results.append(result)
        return results

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            job.status = ExecutorStatus.STOPPED
            job.error = "Cancelled"
            job.completed_at = datetime.now()
            del self.active_jobs[job_id]
            self.job_history.append(job)
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[ExecutionJob]:
        return self.active_jobs.get(job_id)

    def start(self) -> bool:
        try:
            import docker
            client = docker.from_env()
            client.ping()
            self.status = ExecutorStatus.RUNNING
            return True
        except Exception:
            self.status = ExecutorStatus.ERROR
            return False

    def stop(self) -> bool:
        self.status = ExecutorStatus.STOPPED
        return True

    def pause(self) -> bool:
        self.status = ExecutorStatus.PAUSED
        return True

    def resume(self) -> bool:
        self.status = ExecutorStatus.RUNNING
        return True

    def health_check(self) -> Dict[str, Any]:
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return {
                "status": "healthy",
                "image": self._image,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


class ExecutorManager:
    def __init__(self):
        self.executors: Dict[str, BaseExecutor] = {}
        self.default_executor_id: Optional[str] = None

    def register_executor(self, executor: BaseExecutor) -> bool:
        if executor.config.executor_id in self.executors:
            return False
        self.executors[executor.config.executor_id] = executor
        if not self.default_executor_id:
            self.default_executor_id = executor.config.executor_id
        return True

    def get_executor(self, executor_id: Optional[str] = None) -> Optional[BaseExecutor]:
        if executor_id:
            return self.executors.get(executor_id)
        if self.default_executor_id:
            return self.executors.get(self.default_executor_id)
        return None

    def execute(self, tool_id: str, parameters: Dict[str, Any], executor_id: Optional[str] = None) -> ExecutionJob:
        executor = self.get_executor(executor_id)
        if not executor:
            raise ValueError("No executor available")
        return executor.execute(tool_id, parameters)

    def list_executors(self) -> List[Dict[str, Any]]:
        return [executor.get_summary() for executor in self.executors.values()]

    def start_all(self):
        for executor in self.executors.values():
            executor.start()

    def stop_all(self):
        for executor in self.executors.values():
            executor.stop()

    def set_default_executor(self, executor_id: str) -> bool:
        if executor_id in self.executors:
            self.default_executor_id = executor_id
            return True
        return False

    def get_health_summary(self) -> Dict[str, Any]:
        health = {}
        for eid, executor in self.executors.items():
            health[eid] = executor.health_check()
        return health

    def create_local_executor(self, executor_id: str, name: str = "", description: str = "") -> LocalExecutor:
        config = ExecutorConfig(
            executor_id=executor_id,
            executor_type=ExecutorType.LOCAL,
            name=name,
            description=description,
        )
        executor = LocalExecutor(config)
        self.register_executor(executor)
        return executor

    def create_remote_executor(self, executor_id: str, host: str, port: int, name: str = "", description: str = "") -> RemoteExecutor:
        config = ExecutorConfig(
            executor_id=executor_id,
            executor_type=ExecutorType.REMOTE,
            name=name,
            description=description,
            host=host,
            port=port,
        )
        executor = RemoteExecutor(config)
        self.register_executor(executor)
        return executor

    def create_docker_executor(self, executor_id: str, image: str = "python:3.11-slim", name: str = "", description: str = "") -> DockerExecutor:
        config = ExecutorConfig(
            executor_id=executor_id,
            executor_type=ExecutorType.DOCKER,
            name=name,
            description=description,
            config={"image": image},
        )
        executor = DockerExecutor(config)
        self.register_executor(executor)
        return executor