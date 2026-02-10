"""Python language driver — wraps existing ast-based analysis from evidence_collector.

This driver delegates to the existing resolve_changed_symbols, build_test_graph,
and find_downstream_callers functions, keeping backward compatibility while
conforming to the LanguageDriver protocol.
"""

from __future__ import annotations

from aiv.lib.evidence_collector import (
    DownstreamCaller,
    TestGraph,
)
from aiv.lib.evidence_collector import (
    build_test_graph as _build_test_graph,
)
from aiv.lib.evidence_collector import (
    find_downstream_callers as _find_downstream_callers,
)
from aiv.lib.evidence_collector import (
    resolve_changed_symbols as _resolve_changed_symbols,
)


class PythonDriver:
    """LanguageDriver implementation for Python (.py) files.

    Delegates to the existing ast-based functions in evidence_collector.py.
    """

    @property
    def name(self) -> str:
        return "python"

    @property
    def extensions(self) -> tuple[str, ...]:
        return (".py",)

    def resolve_symbols(
        self,
        file_path: str,
        line_ranges: list[tuple[int, int]],
    ) -> list[str]:
        return _resolve_changed_symbols(file_path, line_ranges)

    def build_test_graph(self, test_dir: str = "tests/") -> TestGraph:
        return _build_test_graph(test_dir)

    def find_downstream_callers(
        self,
        changed_symbols: list[str],
        src_dir: str = "src/",
        exclude_file: str = "",
    ) -> list[DownstreamCaller]:
        return _find_downstream_callers(changed_symbols, src_dir, exclude_file)
