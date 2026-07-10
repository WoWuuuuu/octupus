from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import sys
import os
import importlib


class CheckStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class CheckResult:
    check_id: str
    name: str
    status: CheckStatus
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseChecker:
    def __init__(self):
        self.results: List[CheckResult] = []

    def run(self) -> List[CheckResult]:
        self.results = []
        self._run_checks()
        return self.results

    def _run_checks(self):
        pass

    def _add_result(self, check_id: str, name: str, status: CheckStatus, message: str = "", details: Dict[str, Any] = None):
        self.results.append(CheckResult(
            check_id=check_id,
            name=name,
            status=status,
            message=message,
            details=details or {},
        ))


class SystemChecker(BaseChecker):
    def _run_checks(self):
        self._check_python_version()
        self._check_operating_system()
        self._check_environment_variables()
        self._check_disk_space()
        self._check_memory_usage()

    def _check_python_version(self):
        version = sys.version_info
        if version >= (3, 10):
            self._add_result(
                "python_version",
                "Python Version",
                CheckStatus.PASSED,
                f"Python {version.major}.{version.minor}.{version.micro}",
                {"major": version.major, "minor": version.minor, "micro": version.micro},
            )
        else:
            self._add_result(
                "python_version",
                "Python Version",
                CheckStatus.FAILED,
                f"Python {version.major}.{version.minor}.{version.micro} - Requires >= 3.10",
            )

    def _check_operating_system(self):
        platform = sys.platform
        os_name = os.name
        self._add_result(
            "operating_system",
            "Operating System",
            CheckStatus.PASSED,
            f"{platform} ({os_name})",
            {"platform": platform, "os_name": os_name},
        )

    def _check_environment_variables(self):
        env_vars = {}
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]:
            env_vars[key] = "set" if key in os.environ else "not set"

        self._add_result(
            "environment_variables",
            "Environment Variables",
            CheckStatus.PASSED,
            "API keys checked",
            env_vars,
        )

    def _check_disk_space(self):
        try:
            disk = os.statvfs("/") if os.name == "posix" else os.statvfs(".")
            free_mb = (disk.f_bavail * disk.f_frsize) / (1024 * 1024)
            total_mb = (disk.f_blocks * disk.f_frsize) / (1024 * 1024)
            percent_free = (free_mb / total_mb) * 100

            if percent_free > 10:
                status = CheckStatus.PASSED
            elif percent_free > 5:
                status = CheckStatus.WARNING
            else:
                status = CheckStatus.FAILED

            self._add_result(
                "disk_space",
                "Disk Space",
                status,
                f"{free_mb:.1f} MB free of {total_mb:.1f} MB ({percent_free:.1f}%)",
                {"free_mb": free_mb, "total_mb": total_mb, "percent_free": percent_free},
            )
        except Exception as e:
            self._add_result(
                "disk_space",
                "Disk Space",
                CheckStatus.SKIPPED,
                f"Unable to check: {str(e)}",
            )

    def _check_memory_usage(self):
        try:
            import psutil
            process = psutil.Process()
            memory = process.memory_info()
            memory_mb = memory.rss / (1024 * 1024)

            self._add_result(
                "memory_usage",
                "Memory Usage",
                CheckStatus.PASSED,
                f"{memory_mb:.1f} MB",
                {"rss_mb": memory_mb},
            )
        except ImportError:
            self._add_result(
                "memory_usage",
                "Memory Usage",
                CheckStatus.SKIPPED,
                "psutil not installed",
            )
        except Exception as e:
            self._add_result(
                "memory_usage",
                "Memory Usage",
                CheckStatus.SKIPPED,
                f"Unable to check: {str(e)}",
            )


class DependencyChecker(BaseChecker):
    REQUIRED_PACKAGES = [
        ("rich", ">=15.0.0"),
        ("prompt_toolkit", ">=3.0.0"),
        ("gitpython", ">=3.1.0"),
        ("jsonschema", ">=4.0.0"),
        ("beautifulsoup4", ">=4.0.0"),
    ]

    OPTIONAL_PACKAGES = [
        ("requests", ">=2.0.0"),
        ("docker", ">=6.0.0"),
        ("psutil", ">=5.0.0"),
    ]

    def _run_checks(self):
        self._check_required_packages()
        self._check_optional_packages()
        self._check_octopus_modules()

    def _check_package(self, name: str, min_version: str) -> CheckResult:
        try:
            pkg = importlib.import_module(name)
            version = getattr(pkg, "__version__", "unknown")
            return CheckResult(
                check_id=f"pkg_{name}",
                name=f"{name} ({min_version})",
                status=CheckStatus.PASSED,
                message=f"Version: {version}",
                details={"installed_version": version},
            )
        except ImportError:
            return CheckResult(
                check_id=f"pkg_{name}",
                name=f"{name} ({min_version})",
                status=CheckStatus.FAILED,
                message=f"Not installed",
            )

    def _check_required_packages(self):
        for name, min_version in self.REQUIRED_PACKAGES:
            result = self._check_package(name, min_version)
            self.results.append(result)

    def _check_optional_packages(self):
        for name, min_version in self.OPTIONAL_PACKAGES:
            result = self._check_package(name, min_version)
            if result.status == CheckStatus.FAILED:
                result.status = CheckStatus.WARNING
                result.message = f"Optional package not installed"
            self.results.append(result)

    def _check_octopus_modules(self):
        modules = [
            "core",
            "perception",
            "protocol",
            "execution",
            "octopus",
        ]

        for module in modules:
            try:
                importlib.import_module(module)
                self._add_result(
                    f"module_{module}",
                    f"Octopus Module: {module}",
                    CheckStatus.PASSED,
                    f"Successfully imported",
                )
            except Exception as e:
                self._add_result(
                    f"module_{module}",
                    f"Octopus Module: {module}",
                    CheckStatus.FAILED,
                    f"Failed to import: {str(e)}",
                )


class ConfigurationChecker(BaseChecker):
    def _run_checks(self):
        self._check_config_files()
        self._check_logging_config()
        self._check_data_directories()

    def _check_config_files(self):
        config_files = [
            "config/application.yml",
            ".env.example",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                self._add_result(
                    f"config_{config_file}",
                    f"Config File: {config_file}",
                    CheckStatus.PASSED,
                    f"Found",
                    {"path": config_file},
                )
            else:
                self._add_result(
                    f"config_{config_file}",
                    f"Config File: {config_file}",
                    CheckStatus.WARNING,
                    f"Not found",
                    {"path": config_file},
                )

    def _check_logging_config(self):
        try:
            import logging
            root_logger = logging.getLogger()
            level = logging.getLevelName(root_logger.level)
            handlers = len(root_logger.handlers)

            self._add_result(
                "logging_config",
                "Logging Configuration",
                CheckStatus.PASSED,
                f"Level: {level}, Handlers: {handlers}",
                {"level": level, "handlers": handlers},
            )
        except Exception as e:
            self._add_result(
                "logging_config",
                "Logging Configuration",
                CheckStatus.FAILED,
                f"Error: {str(e)}",
            )

    def _check_data_directories(self):
        data_dirs = [
            "data/sessions",
            "data/approvals",
        ]

        for data_dir in data_dirs:
            if os.path.exists(data_dir):
                writable = os.access(data_dir, os.W_OK)
                if writable:
                    self._add_result(
                        f"data_{data_dir}",
                        f"Data Directory: {data_dir}",
                        CheckStatus.PASSED,
                        f"Exists and writable",
                        {"path": data_dir, "writable": True},
                    )
                else:
                    self._add_result(
                        f"data_{data_dir}",
                        f"Data Directory: {data_dir}",
                        CheckStatus.WARNING,
                        f"Exists but not writable",
                        {"path": data_dir, "writable": False},
                    )
            else:
                self._add_result(
                    f"data_{data_dir}",
                    f"Data Directory: {data_dir}",
                    CheckStatus.WARNING,
                    f"Will be created on first use",
                    {"path": data_dir, "exists": False},
                )


class NetworkChecker(BaseChecker):
    def _run_checks(self):
        self._check_internet_connectivity()
        self._check_dns_resolution()

    def _check_internet_connectivity(self):
        try:
            import urllib.request
            urllib.request.urlopen("https://www.google.com", timeout=5)
            self._add_result(
                "internet_connectivity",
                "Internet Connectivity",
                CheckStatus.PASSED,
                "Connected",
            )
        except Exception as e:
            self._add_result(
                "internet_connectivity",
                "Internet Connectivity",
                CheckStatus.WARNING,
                f"Unable to connect: {str(e)}",
            )

    def _check_dns_resolution(self):
        try:
            import socket
            socket.gethostbyname("github.com")
            self._add_result(
                "dns_resolution",
                "DNS Resolution",
                CheckStatus.PASSED,
                "Resolved github.com",
            )
        except Exception as e:
            self._add_result(
                "dns_resolution",
                "DNS Resolution",
                CheckStatus.WARNING,
                f"Failed: {str(e)}",
            )


class Doctor:
    def __init__(self):
        self.checkers: List[BaseChecker] = [
            SystemChecker(),
            DependencyChecker(),
            ConfigurationChecker(),
            NetworkChecker(),
        ]

    def run_all(self) -> List[CheckResult]:
        all_results = []
        for checker in self.checkers:
            results = checker.run()
            all_results.extend(results)
        return all_results

    def run_checker(self, checker_name: str) -> List[CheckResult]:
        for checker in self.checkers:
            if checker.__class__.__name__.lower() == checker_name.lower():
                return checker.run()
        raise ValueError(f"Checker not found: {checker_name}")

    def get_summary(self, results: List[CheckResult]) -> Dict[str, Any]:
        passed = sum(1 for r in results if r.status == CheckStatus.PASSED)
        failed = sum(1 for r in results if r.status == CheckStatus.FAILED)
        warning = sum(1 for r in results if r.status == CheckStatus.WARNING)
        skipped = sum(1 for r in results if r.status == CheckStatus.SKIPPED)

        return {
            "total_checks": len(results),
            "passed": passed,
            "failed": failed,
            "warning": warning,
            "skipped": skipped,
            "overall_status": "healthy" if failed == 0 else "unhealthy",
        }

    def format_results(self, results: List[CheckResult], format_type: str = "rich") -> str:
        if format_type == "json":
            return self._format_json(results)
        elif format_type == "text":
            return self._format_text(results)
        else:
            return self._format_rich(results)

    def _format_json(self, results: List[CheckResult]) -> str:
        import json
        data = {
            "results": [r.to_dict() for r in results],
            "summary": self.get_summary(results),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_text(self, results: List[CheckResult]) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append("Octopus Doctor - System Health Check")
        lines.append("=" * 70)

        for result in results:
            status_icon = {
                CheckStatus.PASSED: "✓",
                CheckStatus.FAILED: "✗",
                CheckStatus.WARNING: "⚠",
                CheckStatus.SKIPPED: "-",
            }.get(result.status, "?")

            lines.append(f"\n{status_icon} {result.name}")
            lines.append(f"  Status: {result.status.value}")
            if result.message:
                lines.append(f"  Message: {result.message}")
            if result.details:
                for key, value in result.details.items():
                    lines.append(f"  {key}: {value}")

        summary = self.get_summary(results)
        lines.append("\n" + "=" * 70)
        lines.append("Summary:")
        lines.append(f"  Total: {summary['total_checks']}")
        lines.append(f"  Passed: {summary['passed']}")
        lines.append(f"  Failed: {summary['failed']}")
        lines.append(f"  Warning: {summary['warning']}")
        lines.append(f"  Overall: {summary['overall_status']}")

        return "\n".join(lines)

    def _format_rich(self, results: List[CheckResult]) -> str:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text

        console = Console()

        summary = self.get_summary(results)

        header = Panel(
            f"[bold]Octopus Doctor[/bold]\n"
            f"[green]Total:[/green] {summary['total_checks']}  "
            f"[green]✓ Passed:[/green] {summary['passed']}  "
            f"[red]✗ Failed:[/red] {summary['failed']}  "
            f"[yellow]⚠ Warning:[/yellow] {summary['warning']}",
            title="System Health Check",
            style="blue" if summary["overall_status"] == "healthy" else "red",
        )
        console.print(header)

        categories = {}
        for result in results:
            category = result.check_id.split("_")[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)

        for category, cat_results in categories.items():
            table = Table(title=category.capitalize())
            table.add_column("Check", style="cyan", width=35)
            table.add_column("Status", style="yellow", width=12)
            table.add_column("Message", style="green")

            for result in cat_results:
                status_style = {
                    CheckStatus.PASSED: "green",
                    CheckStatus.FAILED: "red",
                    CheckStatus.WARNING: "yellow",
                    CheckStatus.SKIPPED: "dim",
                }.get(result.status, "white")

                table.add_row(
                    result.name,
                    f"[{status_style}]{result.status.value}[/{status_style}]",
                    result.message,
                )
            console.print(table)

        return ""