"""LanguageDriver Protocol — interface for polyglot evidence collection.

Each language driver provides AST-level analysis for a specific language
family. The protocol defines three capabilities that mirror the existing
Python-only functions in evidence_collector.py:

1. resolve_symbols — map diff line ranges to enclosing symbol names
2. build_test_graph — build import + call graph from test files
3. find_downstream_callers — find production callers of changed symbols
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from aiv.lib.evidence_collector import DownstreamCaller, TestGraph


@runtime_checkable
class LanguageDriver(Protocol):
    """Protocol for language-specific AST analysis.

    Implementations must handle all file extensions they claim to support
    (registered via the extension registry in __init__.py).
    """

    @property
    def name(self) -> str:
        """Human-readable driver name (e.g. 'python', 'typescript')."""
        ...

    @property
    def extensions(self) -> tuple[str, ...]:
        """File extensions this driver handles (e.g. ('.py',), ('.ts', '.tsx', '.js', '.jsx'))."""
        ...

    def resolve_symbols(
        self,
        file_path: str,
        line_ranges: list[tuple[int, int]],
    ) -> list[str]:
        """Map line ranges from diff hunks to enclosing function/class names.

        Args:
            file_path: Absolute or relative path to the source file.
            line_ranges: List of (start_line, end_line) tuples from diff hunks.

        Returns:
            De-duplicated list of symbol names (e.g. ["loadConfig", "UserService"]).
            Returns ["<module>"] if changes are at module level.
            Returns ["<parse-error>"] on parse failure.
        """
        ...

    def build_test_graph(self, test_dir: str) -> TestGraph:
        """Build import + call graph from test files in the given directory.

        Scans all files with matching extensions under test_dir, extracting:
        - Which symbols each test file imports
        - Which symbols each test function calls

        Args:
            test_dir: Root directory containing test files.

        Returns:
            A TestGraph with imports and calls dictionaries.
        """
        ...

    def find_downstream_callers(
        self,
        changed_symbols: list[str],
        src_dir: str = "src/",
        exclude_file: str = "",
    ) -> list[DownstreamCaller]:
        """Find functions in src/ that call any of the changed symbols.

        Args:
            changed_symbols: Symbol names from resolve_symbols.
            src_dir: Root directory to scan for callers.
            exclude_file: File path to exclude (the file being committed).

        Returns:
            List of DownstreamCaller records.
        """
        ...
