from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import fnmatch


@dataclass
class PerceptionResult:
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class BudgetConfig:
    max_files: int = 100
    max_chars_per_file: int = 10000
    max_total_chars: int = 100000
    max_search_results: int = 50
    allowed_extensions: List[str] = field(default_factory=lambda: ["*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml"])
    excluded_patterns: List[str] = field(default_factory=lambda: ["__pycache__", ".git", "*.pyc", "*.pyo", "*.egg-info"])

    def is_file_allowed(self, filepath: Path) -> bool:
        if filepath.is_dir():
            for pattern in self.excluded_patterns:
                if fnmatch.fnmatch(filepath.name, pattern) or fnmatch.fnmatch(str(filepath), pattern):
                    return False
            return True
        filename = filepath.name
        for pattern in self.excluded_patterns:
            if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(str(filepath), pattern):
                return False
        if not self.allowed_extensions:
            return True
        for ext in self.allowed_extensions:
            if fnmatch.fnmatch(filename, ext):
                return True
        return False


class WorkspacePerceiver(ABC):
    def __init__(self, root_path: Optional[str] = None, budget: Optional[BudgetConfig] = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.budget = budget or BudgetConfig()

    @abstractmethod
    def read_file(self, filepath: str) -> PerceptionResult:
        pass

    @abstractmethod
    def repo_map(self, depth: int = 3) -> PerceptionResult:
        pass

    @abstractmethod
    def search(self, query: str, case_sensitive: bool = False) -> PerceptionResult:
        pass

    @abstractmethod
    def git_status(self) -> PerceptionResult:
        pass

    @abstractmethod
    def git_diff(self, filepath: Optional[str] = None) -> PerceptionResult:
        pass

    @abstractmethod
    def git_log(self, limit: int = 10) -> PerceptionResult:
        pass

    @abstractmethod
    def read_url(self, url: str) -> PerceptionResult:
        pass


class LocalWorkspacePerceiver(WorkspacePerceiver):
    def read_file(self, filepath: str) -> PerceptionResult:
        try:
            full_path = self.root_path / filepath
            if not full_path.exists():
                return PerceptionResult(success=False, error=f"File not found: {filepath}")
            
            if not self.budget.is_file_allowed(full_path):
                return PerceptionResult(success=False, error=f"File type not allowed: {filepath}")

            content = full_path.read_text(encoding="utf-8")
            if len(content) > self.budget.max_chars_per_file:
                content = content[:self.budget.max_chars_per_file]
                return PerceptionResult(
                    success=True,
                    data=content,
                    metadata={"truncated": True, "original_length": len(content) + len(content)}
                )
            
            return PerceptionResult(
                success=True,
                data=content,
                metadata={"file_path": str(full_path), "size": len(content)}
            )
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))

    def repo_map(self, depth: int = 3) -> PerceptionResult:
        try:
            tree = self._build_tree(self.root_path, depth, 0)
            return PerceptionResult(
                success=True,
                data=tree,
                metadata={"root": str(self.root_path), "depth": depth}
            )
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))

    def _build_tree(self, path: Path, max_depth: int, current_depth: int) -> Dict[str, Any]:
        if current_depth > max_depth:
            return {}

        result = {"name": path.name, "type": "directory", "children": []}
        file_count = 0

        try:
            entries = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            for entry in entries:
                if not self.budget.is_file_allowed(entry):
                    continue
                
                if entry.is_file():
                    result["children"].append({
                        "name": entry.name,
                        "type": "file",
                        "size": entry.stat().st_size if entry.exists() else 0
                    })
                    file_count += 1
                    if file_count >= self.budget.max_files:
                        result["children"].append({"name": "...", "type": "truncated"})
                        break
                elif entry.is_dir() and current_depth < max_depth:
                    child_tree = self._build_tree(entry, max_depth, current_depth + 1)
                    if child_tree["children"]:
                        result["children"].append(child_tree)
        except PermissionError:
            result["error"] = "Permission denied"

        return result

    def search(self, query: str, case_sensitive: bool = False) -> PerceptionResult:
        try:
            results = []
            total_chars = 0
            
            for filepath in self.root_path.rglob("*"):
                if not filepath.is_file():
                    continue
                if not self.budget.is_file_allowed(filepath):
                    continue
                
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    search_content = content if case_sensitive else content.lower()
                    search_query = query if case_sensitive else query.lower()
                    
                    if search_query in search_content:
                        lines = content.splitlines()
                        matching_lines = []
                        for i, line in enumerate(lines, 1):
                            search_line = line if case_sensitive else line.lower()
                            if search_query in search_line:
                                matching_lines.append({"line": i, "content": line.strip()})
                                if len(matching_lines) >= 5:
                                    break
                        
                        results.append({
                            "file_path": str(filepath.relative_to(self.root_path)),
                            "matches": matching_lines,
                            "total_matches": content.count(query)
                        })
                        
                        total_chars += len(content)
                        if len(results) >= self.budget.max_search_results or total_chars >= self.budget.max_total_chars:
                            break
                except Exception:
                    continue

            return PerceptionResult(
                success=True,
                data=results,
                metadata={"query": query, "results_count": len(results)}
            )
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))

    def git_status(self) -> PerceptionResult:
        try:
            from git import Repo
            repo = Repo(self.root_path)
            
            status = {
                "branch": repo.active_branch.name if repo.active_branch else None,
                "ahead": repo.head.commit.count(repo.active_branch.tracking_branch()) if repo.active_branch.tracking_branch() else 0,
                "behind": repo.active_branch.tracking_branch().count(repo.head.commit) if repo.active_branch.tracking_branch() else 0,
                "staged": [],
                "unstaged": [],
                "untracked": [],
            }

            for item in repo.index.diff(None):
                status["unstaged"].append({
                    "file": item.a_path,
                    "change_type": item.change_type
                })
            
            for item in repo.index.diff(repo.head.commit):
                status["staged"].append({
                    "file": item.a_path,
                    "change_type": item.change_type
                })
            
            status["untracked"] = repo.untracked_files

            return PerceptionResult(
                success=True,
                data=status,
                metadata={"repo_path": str(self.root_path)}
            )
        except ImportError:
            return PerceptionResult(success=False, error="gitpython not installed")
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))

    def git_diff(self, filepath: Optional[str] = None) -> PerceptionResult:
        try:
            from git import Repo
            repo = Repo(self.root_path)
            
            if filepath:
                diff_output = repo.git.diff("--", filepath)
            else:
                diff_output = repo.git.diff()

            return PerceptionResult(
                success=True,
                data=diff_output,
                metadata={"file_path": filepath}
            )
        except ImportError:
            return PerceptionResult(success=False, error="gitpython not installed")
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))

    def git_log(self, limit: int = 10) -> PerceptionResult:
        try:
            from git import Repo
            repo = Repo(self.root_path)
            
            commits = []
            for commit in repo.iter_commits(max_count=limit):
                commits.append({
                    "hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "date": commit.authored_datetime.isoformat(),
                    "files_changed": len(commit.stats.files) if commit.stats else 0
                })

            return PerceptionResult(
                success=True,
                data=commits,
                metadata={"limit": limit, "total": len(commits)}
            )
        except ImportError:
            return PerceptionResult(success=False, error="gitpython not installed")
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))

    def read_url(self, url: str) -> PerceptionResult:
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text(separator="\n", strip=True)
            
            if len(text_content) > self.budget.max_chars_per_file:
                text_content = text_content[:self.budget.max_chars_per_file]
                return PerceptionResult(
                    success=True,
                    data=text_content,
                    metadata={"url": url, "truncated": True}
                )
            
            return PerceptionResult(
                success=True,
                data=text_content,
                metadata={"url": url, "size": len(text_content)}
            )
        except ImportError:
            return PerceptionResult(success=False, error="requests or beautifulsoup4 not installed")
        except Exception as e:
            return PerceptionResult(success=False, error=str(e))