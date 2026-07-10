import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory


console = Console()


class Command(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, args: List[str]) -> Any:
        pass


class HelpCommand(Command):
    def __init__(self, command_registry: Dict[str, Command]):
        self.command_registry = command_registry

    def name(self) -> str:
        return "help"

    def description(self) -> str:
        return "Show this help message"

    def execute(self, args: List[str]) -> Any:
        table = Table(title="Octopus Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="green")
        
        for cmd_name, cmd in self.command_registry.items():
            table.add_row(cmd_name, cmd.description())
        
        console.print(table)


class ExitCommand(Command):
    def name(self) -> str:
        return "exit"

    def description(self) -> str:
        return "Exit the Octopus shell"

    def execute(self, args: List[str]) -> Any:
        console.print("[yellow]Goodbye![/yellow]")
        sys.exit(0)


class VersionCommand(Command):
    def name(self) -> str:
        return "version"

    def description(self) -> str:
        return "Show Octopus version"

    def execute(self, args: List[str]) -> Any:
        console.print(Panel("Octopus v0.2.0\n\nDecision-Execution Framework", title="Version"))


class ReadFileCommand(Command):
    def __init__(self, perceiver):
        self.perceiver = perceiver

    def name(self) -> str:
        return "read"

    def description(self) -> str:
        return "Read a file: read <file_path>"

    def execute(self, args: List[str]) -> Any:
        if not args:
            console.print("[red]Usage: read <file_path>[/red]")
            return
        
        filepath = args[0]
        result = self.perceiver.read_file(filepath)
        
        if result.success:
            console.print(Panel(result.data, title=f"File: {filepath}"))
        else:
            console.print(f"[red]Error: {result.error}[/red]")


class RepoMapCommand(Command):
    def __init__(self, perceiver):
        self.perceiver = perceiver

    def name(self) -> str:
        return "ls"

    def description(self) -> str:
        return "List directory structure: ls [depth]"

    def execute(self, args: List[str]) -> Any:
        depth = int(args[0]) if args else 3
        result = self.perceiver.repo_map(depth=depth)
        
        if result.success:
            self._print_tree(result.data)
        else:
            console.print(f"[red]Error: {result.error}[/red]")

    def _print_tree(self, node: Dict[str, Any], indent: str = ""):
        name = node.get("name", "")
        node_type = node.get("type", "")
        
        if node_type == "directory":
            console.print(f"{indent}[bold blue]📁 {name}[/bold blue]")
            for child in node.get("children", []):
                self._print_tree(child, indent + "  ")
        elif node_type == "file":
            size = node.get("size", 0)
            size_str = f" ({size} bytes)" if size else ""
            console.print(f"{indent}[green]📄 {name}{size_str}[/green]")
        elif node_type == "truncated":
            console.print(f"{indent}[yellow]...[/yellow]")


class SearchCommand(Command):
    def __init__(self, perceiver):
        self.perceiver = perceiver

    def name(self) -> str:
        return "search"

    def description(self) -> str:
        return "Search for text in files: search <query>"

    def execute(self, args: List[str]) -> Any:
        if not args:
            console.print("[red]Usage: search <query>[/red]")
            return
        
        query = " ".join(args)
        result = self.perceiver.search(query)
        
        if result.success:
            if not result.data:
                console.print("[yellow]No results found[/yellow]")
                return
            
            for item in result.data:
                console.print(f"\n[bold cyan]File: {item['file_path']}[/bold cyan]")
                console.print(f"Total matches: {item['total_matches']}")
                for match in item["matches"]:
                    console.print(f"  [green]Line {match['line']}:[/green] {match['content']}")
        else:
            console.print(f"[red]Error: {result.error}[/red]")


class GitStatusCommand(Command):
    def __init__(self, perceiver):
        self.perceiver = perceiver

    def name(self) -> str:
        return "git status"

    def description(self) -> str:
        return "Show git status"

    def execute(self, args: List[str]) -> Any:
        result = self.perceiver.git_status()
        
        if result.success:
            data = result.data
            table = Table(title="Git Status")
            
            if data.get("branch"):
                console.print(f"[bold]Branch:[/bold] {data['branch']}")
            
            if data.get("staged"):
                console.print("\n[bold green]Staged Changes:[/bold green]")
                for item in data["staged"]:
                    console.print(f"  {item['change_type']}: {item['file']}")
            
            if data.get("unstaged"):
                console.print("\n[bold yellow]Unstaged Changes:[/bold yellow]")
                for item in data["unstaged"]:
                    console.print(f"  {item['change_type']}: {item['file']}")
            
            if data.get("untracked"):
                console.print("\n[bold red]Untracked Files:[/bold red]")
                for item in data["untracked"]:
                    console.print(f"  {item}")
        else:
            console.print(f"[red]Error: {result.error}[/red]")


class GitDiffCommand(Command):
    def __init__(self, perceiver):
        self.perceiver = perceiver

    def name(self) -> str:
        return "git diff"

    def description(self) -> str:
        return "Show git diff: git diff [file_path]"

    def execute(self, args: List[str]) -> Any:
        filepath = args[0] if args else None
        result = self.perceiver.git_diff(filepath)
        
        if result.success:
            if result.data:
                console.print(Panel(result.data, title="Git Diff", style="blue"))
            else:
                console.print("[green]No changes[/green]")
        else:
            console.print(f"[red]Error: {result.error}[/red]")


class GitLogCommand(Command):
    def __init__(self, perceiver):
        self.perceiver = perceiver

    def name(self) -> str:
        return "git log"

    def description(self) -> str:
        return "Show git log: git log [limit]"

    def execute(self, args: List[str]) -> Any:
        limit = int(args[0]) if args else 10
        result = self.perceiver.git_log(limit=limit)
        
        if result.success:
            table = Table(title="Git Log")
            table.add_column("Hash", style="cyan", width=10)
            table.add_column("Message", style="green")
            table.add_column("Author", style="yellow")
            table.add_column("Date", style="blue", width=20)
            
            for commit in result.data:
                short_hash = commit["hash"][:8]
                message = commit["message"].split("\n")[0][:50]
                table.add_row(short_hash, message, commit["author"], commit["date"][:19])
            
            console.print(table)
        else:
            console.print(f"[red]Error: {result.error}[/red]")


class DecideCommand(Command):
    def __init__(self, decision_engine):
        self.decision_engine = decision_engine
        from core.decision_card import DecisionCardRenderer
        self.renderer = DecisionCardRenderer()

    def name(self) -> str:
        return "decide"

    def description(self) -> str:
        return "Make a decision: decide <goal>"

    def execute(self, args: List[str]) -> Any:
        if not args:
            console.print("[red]Usage: decide <goal>[/red]")
            return
        
        goal = " ".join(args)
        
        context = {"goal": goal, "priority": "normal"}
        options = [
            {
                "option_id": "option_1",
                "name": "Quick Action",
                "description": "Fast but limited solution",
                "actions": [{"type": "quick_action", "parameters": {}}],
                "scores": {"outcome_value": 0.7, "risk_reduction": 0.5, "reversibility": 0.8, "confidence_alignment": 0.8},
            },
            {
                "option_id": "option_2",
                "name": "Comprehensive Action",
                "description": "Thorough solution with full analysis",
                "actions": [{"type": "analyze", "parameters": {}}, {"type": "execute", "parameters": {}}],
                "scores": {"outcome_value": 0.9, "risk_reduction": 0.7, "reversibility": 0.6, "confidence_alignment": 0.9},
            },
        ]
        
        result = self.decision_engine.make_decision(context, options)
        
        if result.status.value == "decided":
            card = self.renderer.render_from_decision(result)
            self.renderer.render(card)
        else:
            console.print(f"[red]Decision failed: {result.reasoning}[/red]")


class SessionCommand(Command):
    def __init__(self, session_store):
        self.session_store = session_store

    def name(self) -> str:
        return "session"

    def description(self) -> str:
        return "Session management: session <create/list/show/switch/archive/search>"

    def execute(self, args: List[str]) -> Any:
        if not args:
            console.print("[red]Usage: session <create/list/show/switch/archive/search>[/red]")
            return
        
        subcmd = args[0]
        
        if subcmd == "create":
            if len(args) < 2:
                console.print("[red]Usage: session create <title> [description][/red]")
                return
            title = args[1]
            description = " ".join(args[2:]) if len(args) > 2 else ""
            session = self.session_store.create(title, description)
            console.print(f"[green]Created session: {session.session_id}[/green]")
            console.print(f"Title: {session.title}")
        
        elif subcmd == "list":
            sessions = self.session_store.list()
            if not sessions:
                console.print("[yellow]No sessions found[/yellow]")
                return
            
            table = Table(title="Sessions")
            table.add_column("ID", style="cyan", width=30)
            table.add_column("Title", style="green")
            table.add_column("Status", style="yellow", width=12)
            table.add_column("Created", style="blue", width=20)
            
            for s in sessions:
                table.add_row(s.session_id[-20:], s.title, s.status.value, s.created_at.strftime("%Y-%m-%d %H:%M"))
            
            console.print(table)
        
        elif subcmd == "show":
            if len(args) < 2:
                console.print("[red]Usage: session show <session_id>[/red]")
                return
            session_id = args[1]
            session = self.session_store.get(session_id)
            if not session:
                console.print(f"[red]Session not found: {session_id}[/red]")
                return
            
            console.print(Panel(
                f"[bold]ID:[/bold] {session.session_id}\n"
                f"[bold]Title:[/bold] {session.title}\n"
                f"[bold]Description:[/bold] {session.description}\n"
                f"[bold]Status:[/bold] {session.status.value}\n"
                f"[bold]Type:[/bold] {session.session_type.value}\n"
                f"[bold]Created:[/bold] {session.created_at}\n"
                f"[bold]Updated:[/bold] {session.updated_at}\n"
                f"[bold]Tags:[/bold] {', '.join(session.tags) if session.tags else 'None'}",
                title="Session Details",
                style="blue"
            ))
            
            if session.events:
                console.print("\n[bold]Timeline:[/bold]")
                for event in sorted(session.events, key=lambda e: e.timestamp):
                    console.print(f"  {event.timestamp.strftime('%H:%M:%S')} - {event.event_type}: {event.description}")
        
        elif subcmd == "switch":
            if len(args) < 2:
                console.print("[red]Usage: session switch <session_id>[/red]")
                return
            session_id = args[1]
            if self.session_store.set_current(session_id):
                console.print(f"[green]Switched to session: {session_id}[/green]")
            else:
                console.print(f"[red]Failed to switch session[/red]")
        
        elif subcmd == "archive":
            if len(args) < 2:
                console.print("[red]Usage: session archive <session_id>[/red]")
                return
            session_id = args[1]
            session = self.session_store.get(session_id)
            if session:
                session.archive()
                self.session_store.update(session_id, status=session.status)
                console.print(f"[green]Archived session: {session_id}[/green]")
            else:
                console.print(f"[red]Session not found[/red]")
        
        elif subcmd == "search":
            if len(args) < 2:
                console.print("[red]Usage: session search <query>[/red]")
                return
            query = " ".join(args[1:])
            results = self.session_store.search(query)
            if not results:
                console.print("[yellow]No sessions found[/yellow]")
                return
            
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("ID", style="cyan", width=30)
            table.add_column("Title", style="green")
            table.add_column("Status", style="yellow", width=12)
            
            for s in results:
                table.add_row(s.session_id[-20:], s.title, s.status.value)
            
            console.print(table)
        
        elif subcmd == "current":
            session = self.session_store.get_current()
            if session:
                console.print(f"[green]Current session:[/green] {session.session_id} - {session.title}")
            else:
                console.print("[yellow]No current session[/yellow]")
        
        else:
            console.print(f"[red]Unknown subcommand: {subcmd}[/red]")


class ApprovalCommand(Command):
    def __init__(self, approval_manager):
        self.approval_manager = approval_manager

    def name(self) -> str:
        return "approval"

    def description(self) -> str:
        return "Approval management: approval <list/approve/reject/create>"

    def execute(self, args: List[str]) -> Any:
        if not args:
            console.print("[red]Usage: approval <list/approve/reject/create>[/red]")
            return
        
        subcmd = args[0]
        
        if subcmd == "list":
            approvals = self.approval_manager.list_all()
            if not approvals:
                console.print("[yellow]No approvals found[/yellow]")
                return
            
            table = Table(title="Approvals")
            table.add_column("ID", style="cyan", width=30)
            table.add_column("Decision", style="green", width=30)
            table.add_column("Level", style="yellow", width=12)
            table.add_column("Status", style="magenta", width=12)
            table.add_column("Created", style="blue", width=20)
            
            for a in approvals:
                table.add_row(a.approval_id[-20:], a.decision_id[-20:], a.level.value, a.status.value, a.created_at.strftime("%Y-%m-%d %H:%M"))
            
            console.print(table)
        
        elif subcmd == "pending":
            approvals = self.approval_manager.list_pending()
            if not approvals:
                console.print("[green]No pending approvals[/green]")
                return
            
            table = Table(title="Pending Approvals")
            table.add_column("ID", style="cyan", width=30)
            table.add_column("Summary", style="green")
            table.add_column("Level", style="yellow", width=12)
            table.add_column("Requested By", style="blue", width=15)
            
            for a in approvals:
                table.add_row(a.approval_id[-20:], a.decision_summary[:40], a.level.value, a.requested_by)
            
            console.print(table)
        
        elif subcmd == "approve":
            if len(args) < 2:
                console.print("[red]Usage: approval approve <approval_id> [reason][/red]")
                return
            approval_id = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else None
            if self.approval_manager.approve(approval_id, reason=reason):
                console.print(f"[green]Approved: {approval_id}[/green]")
            else:
                console.print(f"[red]Failed to approve[/red]")
        
        elif subcmd == "reject":
            if len(args) < 2:
                console.print("[red]Usage: approval reject <approval_id> [reason][/red]")
                return
            approval_id = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else None
            if self.approval_manager.reject(approval_id, reason=reason):
                console.print(f"[red]Rejected: {approval_id}[/red]")
            else:
                console.print(f"[red]Failed to reject[/red]")
        
        elif subcmd == "create":
            if len(args) < 3:
                console.print("[red]Usage: approval create <decision_id> <summary> [level][/red]")
                return
            decision_id = args[1]
            summary = args[2]
            level = args[3] if len(args) > 3 else "low"
            from core.approval import ApprovalLevel
            try:
                level_enum = ApprovalLevel(level)
            except ValueError:
                console.print(f"[red]Invalid level: {level}[/red]")
                return
            approval = self.approval_manager.create_approval(decision_id, summary, level_enum)
            console.print(f"[green]Created approval: {approval.approval_id}[/green]")
        
        elif subcmd == "stats":
            stats = self.approval_manager.get_statistics()
            table = Table(title="Approval Statistics")
            for key, value in stats.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            console.print(table)
        
        else:
            console.print(f"[red]Unknown subcommand: {subcmd}[/red]")


class CompareCommand(Command):
    def __init__(self, decision_engine):
        self.decision_engine = decision_engine
        from core.decision_card import DecisionCardRenderer, DecisionComparator
        self.renderer = DecisionCardRenderer()
        self.comparator = DecisionComparator()

    def name(self) -> str:
        return "compare"

    def description(self) -> str:
        return "Compare multiple decisions"

    def execute(self, args: List[str]) -> Any:
        if not args or len(args) < 2:
            console.print("[red]Usage: compare <goal1> <goal2> [goal3...]")
            return
        
        goals = args
        
        cards = []
        for goal in goals:
            context = {"goal": goal, "priority": "normal"}
            options = [
                {
                    "option_id": "option_1",
                    "name": "Quick Action",
                    "description": "Fast but limited",
                    "scores": {"outcome_value": 0.7, "risk_reduction": 0.5, "reversibility": 0.8, "confidence_alignment": 0.8},
                },
                {
                    "option_id": "option_2",
                    "name": "Comprehensive Action",
                    "description": "Thorough analysis",
                    "scores": {"outcome_value": 0.9, "risk_reduction": 0.7, "reversibility": 0.6, "confidence_alignment": 0.9},
                },
            ]
            result = self.decision_engine.make_decision(context, options)
            if result.status.value == "decided":
                card = self.renderer.render_from_decision(result)
                cards.append(card)
        
        if cards:
            self.comparator.compare(cards)
        else:
            console.print("[red]No decisions to compare[/red]")


class Shell:
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.session = PromptSession(history=InMemoryHistory())
        self.completer = WordCompleter([])

    def register_command(self, command: Command):
        self.commands[command.name()] = command
        self._update_completer()

    def _update_completer(self):
        self.completer = WordCompleter(list(self.commands.keys()))

    def run(self):
        console.print(Panel(
            "Octopus Interactive Shell\n"
            "Type 'help' for available commands\n"
            "Type 'exit' to quit",
            title="Welcome",
            style="blue"
        ))
        
        while True:
            try:
                command_line = self.session.prompt(
                    "[bold cyan]octopus>[/bold cyan] ",
                    completer=self.completer
                ).strip()
                
                if not command_line:
                    continue
                
                parts = command_line.split()
                cmd_name = parts[0]
                args = parts[1:]
                
                if cmd_name in self.commands:
                    self.commands[cmd_name].execute(args)
                else:
                    console.print(f"[red]Unknown command: {cmd_name}[/red]")
                    console.print("Type 'help' for available commands")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="octopus",
            description="Octopus Decision-Execution Framework",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self.subparsers = self.parser.add_subparsers(dest="command", help="Available commands")
        
        self._register_commands()

    def _register_commands(self):
        self.subparsers.add_parser("shell", help="Start interactive shell")
        self.subparsers.add_parser("version", help="Show version")
        
        read_parser = self.subparsers.add_parser("read", help="Read a file")
        read_parser.add_argument("file_path", help="Path to the file")
        
        ls_parser = self.subparsers.add_parser("ls", help="List directory structure")
        ls_parser.add_argument("depth", type=int, nargs="?", default=3, help="Directory depth")
        
        search_parser = self.subparsers.add_parser("search", help="Search for text")
        search_parser.add_argument("query", nargs="+", help="Search query")
        
        self.subparsers.add_parser("git-status", help="Show git status")
        
        diff_parser = self.subparsers.add_parser("git-diff", help="Show git diff")
        diff_parser.add_argument("file_path", nargs="?", default=None, help="File path")
        
        log_parser = self.subparsers.add_parser("git-log", help="Show git log")
        log_parser.add_argument("limit", type=int, nargs="?", default=10, help="Number of commits")
        
        decide_parser = self.subparsers.add_parser("decide", help="Make a decision")
        decide_parser.add_argument("goal", nargs="+", help="Decision goal")
        
        self.subparsers.add_parser("session", help="Session management")
        
        self.subparsers.add_parser("approval", help="Approval management")
        
        compare_parser = self.subparsers.add_parser("compare", help="Compare decisions")
        compare_parser.add_argument("goals", nargs="+", help="Goals to compare")

    def parse(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        return self.parser.parse_args(args)


def main():
    cli = CLI()
    args = cli.parse()
    
    from perception import LocalWorkspacePerceiver
    from core.decision_engine import DecisionEngine, DecisionPolicy, DecisionCriteria
    from core.session import SessionStore
    from core.approval import ApprovalManager
    
    perceiver = LocalWorkspacePerceiver()
    decision_engine = DecisionEngine()
    session_store = SessionStore()
    approval_manager = ApprovalManager()
    
    policy = DecisionPolicy(
        policy_id="default_policy",
        name="Default Decision Policy",
        description="Standard decision criteria",
        criteria=[
            DecisionCriteria("outcome_value", 0.40, "Value of outcome"),
            DecisionCriteria("risk_reduction", 0.25, "Risk reduction"),
            DecisionCriteria("reversibility", 0.20, "Ease of reversal"),
            DecisionCriteria("confidence_alignment", 0.15, "Confidence match"),
        ],
    )
    decision_engine.add_policy(policy)
    
    if args.command == "shell":
        shell = Shell()
        shell.register_command(HelpCommand(shell.commands))
        shell.register_command(ExitCommand())
        shell.register_command(VersionCommand())
        shell.register_command(ReadFileCommand(perceiver))
        shell.register_command(RepoMapCommand(perceiver))
        shell.register_command(SearchCommand(perceiver))
        shell.register_command(GitStatusCommand(perceiver))
        shell.register_command(GitDiffCommand(perceiver))
        shell.register_command(GitLogCommand(perceiver))
        shell.register_command(DecideCommand(decision_engine))
        shell.register_command(SessionCommand(session_store))
        shell.register_command(ApprovalCommand(approval_manager))
        shell.register_command(CompareCommand(decision_engine))
        shell.run()
    
    elif args.command == "version":
        console.print(Panel("Octopus v0.3.1", title="Version"))
    
    elif args.command == "read":
        result = perceiver.read_file(args.file_path)
        if result.success:
            console.print(Panel(result.data, title=f"File: {args.file_path}"))
        else:
            console.print(f"[red]Error: {result.error}[/red]")
    
    elif args.command == "ls":
        result = perceiver.repo_map(depth=args.depth)
        if result.success:
            RepoMapCommand(perceiver)._print_tree(result.data)
        else:
            console.print(f"[red]Error: {result.error}[/red]")
    
    elif args.command == "search":
        query = " ".join(args.query)
        result = perceiver.search(query)
        if result.success:
            if not result.data:
                console.print("[yellow]No results found[/yellow]")
            else:
                for item in result.data:
                    console.print(f"\n[bold cyan]File: {item['file_path']}[/bold cyan]")
                    for match in item["matches"]:
                        console.print(f"  [green]Line {match['line']}:[/green] {match['content']}")
        else:
            console.print(f"[red]Error: {result.error}[/red]")
    
    elif args.command == "git-status":
        result = perceiver.git_status()
        if result.success:
            GitStatusCommand(perceiver).execute([])
        else:
            console.print(f"[red]Error: {result.error}[/red]")
    
    elif args.command == "git-diff":
        result = perceiver.git_diff(args.file_path)
        if result.success:
            console.print(Panel(result.data, title="Git Diff"))
        else:
            console.print(f"[red]Error: {result.error}[/red]")
    
    elif args.command == "git-log":
        result = perceiver.git_log(limit=args.limit)
        if result.success:
            GitLogCommand(perceiver).execute([])
        else:
            console.print(f"[red]Error: {result.error}[/red]")
    
    elif args.command == "decide":
        goal = " ".join(args.goal)
        context = {"goal": goal, "priority": "normal"}
        options = [
            {
                "option_id": "option_1",
                "name": "Quick Action",
                "description": "Fast but limited solution",
                "actions": [{"type": "quick_action", "parameters": {}}],
                "scores": {"outcome_value": 0.7, "risk_reduction": 0.5, "reversibility": 0.8, "confidence_alignment": 0.8},
            },
            {
                "option_id": "option_2",
                "name": "Comprehensive Action",
                "description": "Thorough solution with full analysis",
                "actions": [{"type": "analyze", "parameters": {}}, {"type": "execute", "parameters": {}}],
                "scores": {"outcome_value": 0.9, "risk_reduction": 0.7, "reversibility": 0.6, "confidence_alignment": 0.9},
            },
        ]
        result = decision_engine.make_decision(context, options)
        if result.status.value == "decided":
            console.print(Panel(
                f"[bold]Selected:[/bold] {result.selected_option.name}\n"
                f"[bold]Confidence:[/bold] {result.confidence:.2f}",
                title="Decision Result",
                style="green"
            ))
        else:
            console.print(f"[red]Decision failed[/red]")
    
    elif args.command == "compare":
        CompareCommand(decision_engine).execute(args.goals)
    
    else:
        cli.parser.print_help()


if __name__ == "__main__":
    main()