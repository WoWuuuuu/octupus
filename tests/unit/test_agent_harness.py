import sys

import pytest

from execution.base import ExecutorConfig, ExecutorStatus, ExecutorType
from execution.harness import (
    AgentProfile,
    CliAgentHarness,
    PROTOCOL_DRY_RUN,
    PROTOCOL_NOT_FOUND,
    PROTOCOL_SUCCESS,
    PROTOCOL_TIMEOUT,
    TASK_FAILED,
    TASK_NOT_STARTED,
    TASK_SUCCESS,
)
from execution.agent_executor import (
    CliAgentExecutor,
    TOOL_AGENT_LIST,
    TOOL_AGENT_RUN,
)
from execution.executors import ExecutorManager


def echo_profile(agent_id="fake_echo", prompt_mode="arg"):
    """A real, cross-platform 'agent' backed by the current Python interpreter."""
    return AgentProfile(
        agent_id=agent_id,
        name="Fake Echo Agent",
        command=[sys.executable, "-c", "import sys; print('AGENT_OK:' + sys.argv[1])"],
        prompt_mode=prompt_mode,
    )


def fail_profile():
    return AgentProfile(
        agent_id="fake_fail",
        name="Fake Failing Agent",
        command=[sys.executable, "-c", "import sys; sys.exit(3)"],
        prompt_mode="arg",
    )


def sleep_profile():
    return AgentProfile(
        agent_id="fake_sleep",
        name="Fake Slow Agent",
        command=[sys.executable, "-c", "import time; time.sleep(30)"],
        prompt_mode="arg",
    )


class TestDryRun:
    def test_dry_run_is_the_default(self):
        harness = CliAgentHarness(profiles={"fake_echo": echo_profile()})
        result = harness.run("fake_echo", "hello")

        assert result.dry_run is True
        assert result.protocol_status == PROTOCOL_DRY_RUN
        assert result.task_status == TASK_NOT_STARTED
        assert result.stdout == ""
        assert result.command[-1] == "hello"
        assert result.command[0] == sys.executable

    def test_dry_run_does_not_require_the_executable_to_exist(self):
        profile = AgentProfile(
            agent_id="ghost", name="Ghost", command=["definitely-not-a-real-binary"]
        )
        harness = CliAgentHarness(profiles={"ghost": profile})
        result = harness.run("ghost", "hi")

        assert result.protocol_status == PROTOCOL_DRY_RUN
        assert result.error is None


class TestExecution:
    def test_successful_run(self):
        harness = CliAgentHarness(profiles={"fake_echo": echo_profile()})
        result = harness.run("fake_echo", "hello world", dry_run=False)

        assert result.protocol_status == PROTOCOL_SUCCESS
        assert result.task_status == TASK_SUCCESS
        assert result.exit_code == 0
        assert "AGENT_OK:hello world" in result.stdout
        assert result.ok is True
        assert result.duration_ms > 0

    def test_nonzero_exit_is_task_failure_not_protocol_failure(self):
        harness = CliAgentHarness(profiles={"fake_fail": fail_profile()})
        result = harness.run("fake_fail", "x", dry_run=False)

        assert result.protocol_status == PROTOCOL_SUCCESS
        assert result.task_status == TASK_FAILED
        assert result.exit_code == 3
        assert result.ok is False

    def test_missing_executable_reports_not_found(self):
        profile = AgentProfile(
            agent_id="ghost", name="Ghost", command=["definitely-not-a-real-binary"]
        )
        harness = CliAgentHarness(profiles={"ghost": profile})
        result = harness.run("ghost", "hi", dry_run=False)

        assert result.protocol_status == PROTOCOL_NOT_FOUND
        assert result.task_status == TASK_NOT_STARTED
        assert "definitely-not-a-real-binary" in result.error

    def test_timeout_is_reported(self):
        harness = CliAgentHarness(profiles={"fake_sleep": sleep_profile()})
        result = harness.run("fake_sleep", "x", timeout_seconds=1, dry_run=False)

        assert result.protocol_status == PROTOCOL_TIMEOUT
        assert result.timed_out is True
        assert result.task_status == TASK_NOT_STARTED

    def test_stdin_prompt_mode(self):
        profile = AgentProfile(
            agent_id="stdin_echo",
            name="Stdin Echo",
            command=[sys.executable, "-c", "import sys; print('GOT:' + sys.stdin.read())"],
            prompt_mode="stdin",
        )
        harness = CliAgentHarness(profiles={"stdin_echo": profile})
        result = harness.run("stdin_echo", "piped prompt", dry_run=False)

        assert result.task_status == TASK_SUCCESS
        assert "GOT:piped prompt" in result.stdout
        assert result.command[-1] != "piped prompt"

    def test_output_is_truncated(self):
        harness = CliAgentHarness(
            profiles={"fake_echo": echo_profile()}, max_output_chars=5
        )
        result = harness.run("fake_echo", "abcdefghij", dry_run=False)

        assert result.truncated is True
        assert len(result.stdout) == 5

    def test_unknown_agent_raises(self):
        harness = CliAgentHarness(profiles={})
        with pytest.raises(KeyError):
            harness.run("nope", "hi")


class TestDiscovery:
    def test_discover_reports_availability(self):
        harness = CliAgentHarness(profiles={"fake_echo": echo_profile()})
        entries = {e["agent_id"]: e for e in harness.discover()}

        assert entries["fake_echo"]["available"] is True
        assert entries["fake_echo"]["executable"] == sys.executable

    def test_is_available_false_for_unknown(self):
        harness = CliAgentHarness(profiles={})
        assert harness.is_available("nope") is False

    def test_builtin_profiles_include_claude_code_and_codex(self):
        harness = CliAgentHarness()
        ids = {p.agent_id for p in harness.list_profiles()}
        assert {"claude_code", "codex"} <= ids

    def test_register_profile(self):
        harness = CliAgentHarness(profiles={})
        harness.register_profile(echo_profile("added"))
        assert harness.is_available("added") is True


class TestCliAgentExecutor:
    def make_executor(self):
        config = ExecutorConfig(
            executor_id="agent_exec",
            executor_type=ExecutorType.AGENT,
            name="Agent Executor",
        )
        return CliAgentExecutor(config, harness=CliAgentHarness(profiles={"fake_echo": echo_profile()}))

    def test_agent_run_defaults_to_dry_run(self):
        executor = self.make_executor()
        job = executor.execute(TOOL_AGENT_RUN, {"agent_id": "fake_echo", "prompt": "hi"})

        assert job.status == ExecutorStatus.STOPPED
        assert job.result["dry_run"] is True
        assert job.result["protocol_status"] == PROTOCOL_DRY_RUN

    def test_agent_run_executes_when_asked(self):
        executor = self.make_executor()
        job = executor.execute(
            TOOL_AGENT_RUN,
            {"agent_id": "fake_echo", "prompt": "go", "dry_run": False},
        )

        assert job.status == ExecutorStatus.STOPPED
        assert job.result["task_status"] == TASK_SUCCESS
        assert "AGENT_OK:go" in job.result["stdout"]

    def test_agent_list(self):
        executor = self.make_executor()
        job = executor.execute(TOOL_AGENT_LIST, {})

        assert job.status == ExecutorStatus.STOPPED
        assert "fake_echo" in job.result["stdout"]

    def test_protocol_failure_marks_job_error(self):
        executor = self.make_executor()
        job = executor.execute(
            TOOL_AGENT_RUN,
            {"agent_id": "fake_echo", "prompt": "hi", "dry_run": True},
        )
        assert job.error is None

        ghost = AgentProfile(agent_id="ghost", name="Ghost", command=["no-such-binary-xyz"])
        executor.harness.register_profile(ghost)
        failed = executor.execute(
            TOOL_AGENT_RUN,
            {"agent_id": "ghost", "prompt": "hi", "dry_run": False},
        )
        assert failed.status == ExecutorStatus.ERROR
        assert failed.result["protocol_status"] == PROTOCOL_NOT_FOUND

    def test_missing_required_parameters(self):
        executor = self.make_executor()
        job = executor.execute(TOOL_AGENT_RUN, {"agent_id": "fake_echo"})
        assert job.status == ExecutorStatus.ERROR
        assert "prompt" in job.error

    def test_health_check_lists_agents(self):
        executor = self.make_executor()
        health = executor.health_check()

        assert health["type"] == "agent"
        assert "fake_echo" in health["available_agents"]

    def test_execute_batch(self):
        executor = self.make_executor()
        jobs = executor.execute_batch([
            {"tool_id": TOOL_AGENT_RUN, "parameters": {"agent_id": "fake_echo", "prompt": "a"}},
            {"tool_id": TOOL_AGENT_RUN, "parameters": {"agent_id": "fake_echo", "prompt": "b"}},
        ])
        assert len(jobs) == 2
        assert all(j.status == ExecutorStatus.STOPPED for j in jobs)


class TestExecutorManager:
    def test_create_agent_executor(self):
        manager = ExecutorManager()
        executor = manager.create_agent_executor("agent_1")

        assert executor.config.executor_type == ExecutorType.AGENT
        assert manager.get_executor("agent_1") is executor
        assert manager.list_executors()[0]["executor_type"] == "agent"

    def test_agent_executor_is_selectable(self):
        manager = ExecutorManager()
        manager.create_agent_executor("agent_1")
        manager.executors["agent_1"].harness = CliAgentHarness(
            profiles={"fake_echo": echo_profile()}
        )

        job = manager.execute(
            TOOL_AGENT_RUN,
            {"agent_id": "fake_echo", "prompt": "via manager"},
            executor_id="agent_1",
        )
        assert job.result["command"][-1] == "via manager"
