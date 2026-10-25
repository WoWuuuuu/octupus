"""
CLI Agent Executor - expose external CLI agents as a regular Octopus executor.

This is the adapter layer. It turns a decided handoff into a concrete agent
invocation through the CLI Agent Harness, and reports the outcome using the
same ExecutionJob shape as LocalExecutor / RemoteExecutor / DockerExecutor.

Two tools are exposed:

  agent_run   run one external agent with a prompt
  agent_list  list known agents and whether they are installed locally

Safety: `agent_run` defaults to `dry_run=True`. A real invocation must be
requested explicitly with `{"dry_run": False}`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from execution.base import (
    BaseExecutor,
    ExecutionJob,
    ExecutorConfig,
    ExecutorStatus,
)
from execution.harness import (
    CliAgentHarness,
    HarnessResult,
    PROTOCOL_DRY_RUN,
    PROTOCOL_FAILED,
    PROTOCOL_NOT_FOUND,
    PROTOCOL_TIMEOUT,
)


TOOL_AGENT_RUN = "agent_run"
TOOL_AGENT_LIST = "agent_list"

_FAILED_PROTOCOL_STATUSES = (PROTOCOL_FAILED, PROTOCOL_NOT_FOUND, PROTOCOL_TIMEOUT)


class CliAgentExecutor(BaseExecutor):
    def __init__(self, config: ExecutorConfig, harness: Optional[CliAgentHarness] = None):
        super().__init__(config)
        self.harness = harness or CliAgentHarness()

    # ------------------------------------------------------------- execute

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
            result = self._run_tool(tool_id, parameters)
            job.result = result.to_dict()
            if result.protocol_status in _FAILED_PROTOCOL_STATUSES:
                job.error = result.error or result.protocol_status
                job.status = ExecutorStatus.ERROR
            else:
                job.status = ExecutorStatus.STOPPED
        except Exception as exc:
            job.error = str(exc)
            job.status = ExecutorStatus.ERROR

        job.completed_at = datetime.now()
        job.execution_time_ms = (job.completed_at - job.started_at).total_seconds() * 1000

        self.active_jobs.pop(job.job_id, None)
        self.job_history.append(job)

        return job

    def _run_tool(self, tool_id: str, parameters: Dict[str, Any]) -> HarnessResult:
        if tool_id == TOOL_AGENT_LIST:
            return self._list_agents()

        if tool_id != TOOL_AGENT_RUN:
            raise ValueError(
                f"不支持的 tool_id: {tool_id}（可用: {TOOL_AGENT_RUN}, {TOOL_AGENT_LIST}）"
            )

        agent_id = parameters.get("agent_id")
        if not agent_id:
            raise ValueError("agent_run 需要参数 'agent_id'")

        prompt = parameters.get("prompt")
        if not prompt:
            raise ValueError("agent_run 需要参数 'prompt'")

        return self.harness.run(
            agent_id=agent_id,
            prompt=prompt,
            workspace=parameters.get("workspace"),
            timeout_seconds=parameters.get("timeout_seconds", self.config.timeout_seconds),
            dry_run=parameters.get("dry_run", True),
            extra_args=parameters.get("extra_args"),
            env=parameters.get("env"),
        )

    def _list_agents(self) -> HarnessResult:
        import json

        return HarnessResult(
            agent_id="*",
            command=[],
            protocol_status=PROTOCOL_DRY_RUN,
            task_status="success",
            stdout=json.dumps(self.harness.discover(), ensure_ascii=False, indent=2),
            dry_run=True,
        )

    # -------------------------------------------------------------- batch

    def execute_batch(self, jobs: List[Dict[str, Any]]) -> List[ExecutionJob]:
        results = []
        for job_spec in jobs:
            results.append(
                self.execute(
                    job_spec.get("tool_id", TOOL_AGENT_RUN),
                    job_spec.get("parameters", {}),
                )
            )
        return results

    def cancel_job(self, job_id: str) -> bool:
        if job_id in self.active_jobs:
            job = self.active_jobs.pop(job_id)
            job.status = ExecutorStatus.STOPPED
            job.error = "Cancelled"
            job.completed_at = datetime.now()
            self.job_history.append(job)
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[ExecutionJob]:
        return self.active_jobs.get(job_id)

    # --------------------------------------------------------- lifecycle

    def start(self) -> bool:
        self.status = ExecutorStatus.RUNNING
        return True

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
        agents = self.harness.discover()
        available = [a["agent_id"] for a in agents if a["available"]]
        return {
            "status": "healthy",
            "executor_id": self.config.executor_id,
            "type": "agent",
            "known_agents": [a["agent_id"] for a in agents],
            "available_agents": available,
            "active_jobs": len(self.active_jobs),
            "total_jobs": len(self.job_history),
        }
