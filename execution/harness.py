"""
CLI Agent Harness - drive an external CLI coding agent from Octopus.

A *harness* is the thin driver layer wrapped around an external agent.
The agent (Claude Code, Codex, ...) stays a black box; the harness only:

  1. builds the command line for that agent
  2. feeds the prompt in the way that agent expects (arg or stdin)
  3. enforces a timeout and an output budget
  4. captures stdout / stderr / exit code / duration
  5. reports a two-level status (protocol level vs task level)

The harness never decides *what* should be done. That is the decision layer's
job. The harness only carries out an already-decided handoff.

Safety default: `dry_run=True`. Running a real coding agent against a workspace
is a side-effecting action, so the caller must opt in explicitly.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------- statuses

# protocol_status: did the harness manage to hand the task over and get a reply?
PROTOCOL_SUCCESS = "success"
PROTOCOL_FAILED = "failed"
PROTOCOL_TIMEOUT = "timeout"
PROTOCOL_NOT_FOUND = "not_found"
PROTOCOL_DRY_RUN = "dry_run"

# task_status: did the agent actually accomplish the task?
TASK_SUCCESS = "success"
TASK_FAILED = "failed"
TASK_NOT_STARTED = "not_started"


# ------------------------------------------------------------------ profile

@dataclass
class AgentProfile:
    """How to invoke one external CLI agent."""

    agent_id: str
    name: str
    command: List[str]
    description: str = ""
    prompt_mode: str = "arg"          # "arg" -> append prompt | "stdin" -> pipe prompt
    output_format: str = "text"       # "text" | "json"
    env: Dict[str, str] = field(default_factory=dict)
    extra_args: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def executable(self) -> str:
        return self.command[0] if self.command else ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "command": self.command,
            "description": self.description,
            "prompt_mode": self.prompt_mode,
            "output_format": self.output_format,
            "extra_args": self.extra_args,
            "executable": self.executable,
            "notes": self.notes,
        }


# ------------------------------------------------------------------- result

@dataclass
class HarnessResult:
    """Normalised outcome of one harness run."""

    agent_id: str
    command: List[str]
    protocol_status: str
    task_status: str
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    timed_out: bool = False
    dry_run: bool = False
    truncated: bool = False
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.task_status == TASK_SUCCESS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "command": self.command,
            "protocol_status": self.protocol_status,
            "task_status": self.task_status,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "timed_out": self.timed_out,
            "dry_run": self.dry_run,
            "truncated": self.truncated,
            "error": self.error,
        }


# ---------------------------------------------------------- built-in agents

BUILTIN_PROFILES: Dict[str, AgentProfile] = {
    "claude_code": AgentProfile(
        agent_id="claude_code",
        name="Claude Code",
        command=["claude", "-p"],
        description="Anthropic Claude Code CLI (print / non-interactive mode).",
        prompt_mode="arg",
        notes="需本机已安装 claude CLI；具体参数请按实际版本调整。",
    ),
    "codex": AgentProfile(
        agent_id="codex",
        name="Codex",
        command=["codex", "exec"],
        description="OpenAI Codex CLI (non-interactive exec mode).",
        prompt_mode="arg",
        notes="需本机已安装 codex CLI；具体参数请按实际版本调整。",
    ),
}


class CliAgentHarness:
    """Driver layer that runs external CLI agents in a controlled way."""

    def __init__(
        self,
        profiles: Optional[Dict[str, AgentProfile]] = None,
        max_output_chars: int = 20000,
        default_timeout_seconds: int = 300,
    ):
        self.profiles: Dict[str, AgentProfile] = dict(profiles or BUILTIN_PROFILES)
        self.max_output_chars = max_output_chars
        self.default_timeout_seconds = default_timeout_seconds

    # ------------------------------------------------------------ profiles

    def register_profile(self, profile: AgentProfile) -> None:
        self.profiles[profile.agent_id] = profile

    def list_profiles(self) -> List[AgentProfile]:
        return list(self.profiles.values())

    def resolve_profile(self, agent_id: str) -> AgentProfile:
        profile = self.profiles.get(agent_id)
        if profile is None:
            raise KeyError(
                f"未知的 agent: {agent_id}（可用: {', '.join(sorted(self.profiles))}）"
            )
        return profile

    def is_available(self, agent_id: str) -> bool:
        """Whether the agent's executable can be found on PATH."""
        try:
            profile = self.resolve_profile(agent_id)
        except KeyError:
            return False
        return bool(profile.executable) and shutil.which(profile.executable) is not None

    def discover(self) -> List[Dict[str, Any]]:
        """List every known agent together with its local availability."""
        return [
            {**profile.to_dict(), "available": self.is_available(profile.agent_id)}
            for profile in self.list_profiles()
        ]

    # ------------------------------------------------------------- command

    def build_command(
        self,
        profile: AgentProfile,
        prompt: str,
        extra_args: Optional[List[str]] = None,
    ) -> List[str]:
        command = list(profile.command) + list(profile.extra_args)
        if extra_args:
            command += list(extra_args)
        if profile.prompt_mode == "arg":
            command.append(prompt)
        return command

    # ----------------------------------------------------------------- run

    def run(
        self,
        agent_id: str,
        prompt: str,
        workspace: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        dry_run: bool = True,
        extra_args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> HarnessResult:
        """Run one agent invocation.

        `dry_run=True` (the default) only builds the command and returns it
        without executing anything.
        """
        profile = self.resolve_profile(agent_id)
        command = self.build_command(profile, prompt, extra_args)
        timeout = timeout_seconds or self.default_timeout_seconds

        if dry_run:
            return HarnessResult(
                agent_id=agent_id,
                command=command,
                protocol_status=PROTOCOL_DRY_RUN,
                task_status=TASK_NOT_STARTED,
                dry_run=True,
            )

        if not profile.executable or shutil.which(profile.executable) is None:
            return HarnessResult(
                agent_id=agent_id,
                command=command,
                protocol_status=PROTOCOL_NOT_FOUND,
                task_status=TASK_NOT_STARTED,
                error=f"找不到可执行文件: {profile.executable}",
            )

        merged_env = dict(os.environ)
        merged_env.update(profile.env)
        if env:
            merged_env.update(env)

        stdin_input = prompt if profile.prompt_mode == "stdin" else None

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=workspace or None,
                env=merged_env,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            return HarnessResult(
                agent_id=agent_id,
                command=command,
                protocol_status=PROTOCOL_TIMEOUT,
                task_status=TASK_NOT_STARTED,
                stdout=self._truncate(exc.stdout or ""),
                stderr=self._truncate(exc.stderr or ""),
                duration_ms=duration_ms,
                timed_out=True,
                error=f"执行超时（>{timeout}s）",
            )
        except OSError as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            return HarnessResult(
                agent_id=agent_id,
                command=command,
                protocol_status=PROTOCOL_FAILED,
                task_status=TASK_NOT_STARTED,
                duration_ms=duration_ms,
                error=f"无法启动进程: {exc}",
            )

        duration_ms = (time.perf_counter() - started) * 1000
        stdout, truncated = self._truncate(completed.stdout or "")
        stderr, _ = self._truncate(completed.stderr or "")

        return HarnessResult(
            agent_id=agent_id,
            command=command,
            protocol_status=PROTOCOL_SUCCESS,
            task_status=TASK_SUCCESS if completed.returncode == 0 else TASK_FAILED,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            truncated=truncated,
        )

    # ------------------------------------------------------------- helpers

    def _truncate(self, text: str):
        if len(text) <= self.max_output_chars:
            return text, False
        return text[: self.max_output_chars], True
