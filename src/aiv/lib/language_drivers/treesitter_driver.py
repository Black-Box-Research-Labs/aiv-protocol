"""Tree-sitter language driver for JavaScript/TypeScript evidence collection.

Provides symbol resolution, test graph building, and downstream caller analysis
for .js, .jsx, .ts, and .tsx files using tree-sitter Python bindings.

Requires optional dependencies:
    pip install tree-sitter tree-sitter-javascript tree-sitter-typescript
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tree_sitter import Language, Node, Parser

    from aiv.lib.evidence_collector import DownstreamCaller, TestGraph

logger = logging.getLogger(__name__)

# Node types that define named symbols in JS/TS
_FUNCTION_TYPES = frozenset(
    {
        "function_declaration",
        "method_definition",
        "generator_function_declaration",
    }
)

_CLASS_TYPES = frozenset(
    {
        "class_declaration",
    }
)

# Arrow functions and variable-assigned functions:
#   const foo = () => {}
#   const foo = function() {}
_VARIABLE_DECLARATOR = "variable_declarator"
_ARROW_FUNCTION = "arrow_function"
_FUNCTION_EXPRESSION = "function"


@dataclass
class _SymbolSpan:
    """A named symbol with its line range in the source file."""

    name: str
    start_line: int  # 1-indexed
    end_line: int  # 1-indexed
    parent_class: str | None = None

    @property
    def qualified_name(self) -> str:
        if self.parent_class:
            return f"{self.parent_class}.{self.name}"
        return self.name


@dataclass
class _FileAnalysis:
    """Extracted imports and function calls from a single file."""

    imports: set[str] = field(default_factory=set)
    # function_name → set of called symbol names
    calls: dict[str, set[str]] = field(default_factory=dict)


def _try_load_languages() -> dict[str, Language] | None:
    """Attempt to load tree-sitter language grammars.

    Returns a dict mapping extension to Language, or None if unavailable.
    """
    try:
        import tree_sitter_javascript as ts_js
        import tree_sitter_typescript as ts_ts
        from tree_sitter import Language

        js_lang = Language(ts_js.language())
        ts_lang = Language(ts_ts.language_typescript())
        tsx_lang = Language(ts_ts.language_tsx())

        return {
            ".js": js_lang,
            ".jsx": js_lang,
            ".mjs": js_lang,
            ".ts": ts_lang,
            ".tsx": tsx_lang,
        }
    except (ImportError, OSError) as e:
        logger.debug("tree-sitter languages unavailable: %s", e)
        return None


def _create_parser(language: Language) -> Parser:
    """Create a tree-sitter Parser for the given language."""
    from tree_sitter import Parser

    parser = Parser(language)
    return parser


def _extract_name(node: Node) -> str | None:
    """Extract the identifier name from a node."""
    for child in node.children:
        if child.type in ("identifier", "property_identifier", "type_identifier"):
            return child.text.decode("utf-8") if child.text else None
    return None


def _extract_symbols(root: Node) -> list[_SymbolSpan]:
    """Walk the tree and extract all named function/class symbols with their line spans."""
    symbols: list[_SymbolSpan] = []
    _walk_for_symbols(root, None, symbols)
    return symbols


def _walk_for_symbols(
    node: Node,
    parent_class: str | None,
    symbols: list[_SymbolSpan],
) -> None:
    """Recursively walk tree-sitter nodes to find symbol definitions."""
    if node.type in _FUNCTION_TYPES:
        name = _extract_name(node)
        if name:
            symbols.append(
                _SymbolSpan(
                    name=name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    parent_class=parent_class,
                )
            )
        # Don't recurse into nested functions for symbol extraction
        return

    if node.type in _CLASS_TYPES:
        class_name = _extract_name(node)
        if class_name:
            symbols.append(
                _SymbolSpan(
                    name=class_name,
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                )
            )
            # Recurse into class body with class context
            for child in node.children:
                if child.type == "class_body":
                    for member in child.children:
                        _walk_for_symbols(member, class_name, symbols)
            return

    # Handle: const foo = () => {} or const foo = function() {}
    if node.type == _VARIABLE_DECLARATOR:
        name = _extract_name(node)
        if name:
            for child in node.children:
                if child.type in (_ARROW_FUNCTION, _FUNCTION_EXPRESSION, "function"):
                    symbols.append(
                        _SymbolSpan(
                            name=name,
                            start_line=node.start_point[0] + 1,
                            end_line=node.end_point[0] + 1,
                            parent_class=parent_class,
                        )
                    )
                    return

    # Recurse into children
    for child in node.children:
        _walk_for_symbols(child, parent_class, symbols)


def _extract_imports(root: Node) -> set[str]:
    """Extract imported symbol names from import statements.

    Handles:
        import { foo, bar } from 'module'
        import foo from 'module'
        import * as foo from 'module'
        const { foo } = require('module')
    """
    imports: set[str] = set()
    _walk_for_imports(root, imports)
    return imports


def _walk_for_imports(node: Node, imports: set[str]) -> None:
    """Recursively find import statements and extract imported names."""
    if node.type == "import_statement":
        for child in node.children:
            if child.type == "import_clause":
                _extract_import_clause(child, imports)
            elif child.type == "named_imports":
                _extract_named_imports(child, imports)
        return

    # Handle: const { foo } = require('module')
    if node.type == "lexical_declaration" or node.type == "variable_declaration":
        text = node.text.decode("utf-8") if node.text else ""
        if "require(" in text:
            for child in node.children:
                if child.type == "variable_declarator":
                    name = _extract_name(child)
                    if name:
                        imports.add(name)
                    # Also extract destructured names
                    for sub in child.children:
                        if sub.type == "object_pattern":
                            _extract_object_pattern(sub, imports)

    for child in node.children:
        _walk_for_imports(child, imports)


def _extract_import_clause(node: Node, imports: set[str]) -> None:
    """Extract names from an import clause."""
    for child in node.children:
        if child.type == "identifier":
            name = child.text.decode("utf-8") if child.text else None
            if name:
                imports.add(name)
        elif child.type == "named_imports":
            _extract_named_imports(child, imports)
        elif child.type == "namespace_import":
            # import * as foo
            for sub in child.children:
                if sub.type == "identifier":
                    name = sub.text.decode("utf-8") if sub.text else None
                    if name:
                        imports.add(name)


def _extract_named_imports(node: Node, imports: set[str]) -> None:
    """Extract names from { foo, bar as baz } import syntax."""
    for child in node.children:
        if child.type == "import_specifier":
            # Use the alias if present, otherwise the original name
            names = [c for c in child.children if c.type == "identifier"]
            if len(names) >= 2:
                # import { foo as bar } → use "bar"
                imports.add(names[1].text.decode("utf-8") if names[1].text else "")
            elif len(names) == 1:
                imports.add(names[0].text.decode("utf-8") if names[0].text else "")


def _extract_object_pattern(node: Node, imports: set[str]) -> None:
    """Extract names from destructuring: const { foo, bar } = ..."""
    for child in node.children:
        if child.type == "shorthand_property_identifier_pattern":
            name = child.text.decode("utf-8") if child.text else None
            if name:
                imports.add(name)
        elif child.type == "pair_pattern":
            # { foo: bar } → use "bar"
            for sub in child.children:
                if sub.type == "identifier":
                    name = sub.text.decode("utf-8") if sub.text else None
                    if name:
                        imports.add(name)


def _extract_calls(node: Node) -> set[str]:
    """Extract all called function/method names from a function body."""
    calls: set[str] = set()
    _walk_for_calls(node, calls)
    return calls


def _walk_for_calls(node: Node, calls: set[str]) -> None:
    """Recursively find call expressions and extract called names."""
    if node.type == "call_expression":
        func = node.children[0] if node.children else None
        if func:
            if func.type == "identifier":
                name = func.text.decode("utf-8") if func.text else None
                if name:
                    calls.add(name)
            elif func.type == "member_expression":
                # obj.method() → extract "method"
                for child in func.children:
                    if child.type == "property_identifier":
                        name = child.text.decode("utf-8") if child.text else None
                        if name:
                            calls.add(name)

    for child in node.children:
        _walk_for_calls(child, calls)


def _analyze_file(root: Node) -> _FileAnalysis:
    """Full analysis of a single file: imports + per-function calls."""
    analysis = _FileAnalysis()
    analysis.imports = _extract_imports(root)

    # Find all function/method definitions and extract their calls
    symbols = _extract_symbols(root)
    for sym in symbols:
        # Find the node spanning this symbol's lines
        func_node = _find_node_at_range(root, sym.start_line - 1, sym.end_line - 1)
        if func_node:
            analysis.calls.setdefault(sym.name, set()).update(_extract_calls(func_node))

    return analysis


def _find_node_at_range(node: Node, start_row: int, end_row: int) -> Node | None:
    """Find the most specific node that spans the given row range."""
    if node.start_point[0] == start_row and node.end_point[0] == end_row:
        return node
    for child in node.children:
        if child.start_point[0] <= start_row and child.end_point[0] >= end_row:
            result = _find_node_at_range(child, start_row, end_row)
            if result:
                return result
    if node.start_point[0] <= start_row and node.end_point[0] >= end_row:
        return node
    return None


class TreeSitterDriver:
    """LanguageDriver implementation for JavaScript/TypeScript using tree-sitter.

    Gracefully degrades if tree-sitter packages are not installed — the
    `available` property indicates whether the driver is functional.
    """

    def __init__(self) -> None:
        self._languages = _try_load_languages()

    @property
    def available(self) -> bool:
        return self._languages is not None

    @property
    def name(self) -> str:
        return "javascript/typescript"

    @property
    def extensions(self) -> tuple[str, ...]:
        if self._languages:
            return tuple(self._languages.keys())
        return (".js", ".jsx", ".mjs", ".ts", ".tsx")

    def _get_parser(self, file_path: str) -> Parser | None:
        """Get a parser for the file's extension, or None."""
        if not self._languages:
            return None
        for ext, lang in self._languages.items():
            if file_path.endswith(ext):
                return _create_parser(lang)
        return None

    def _parse_file(self, file_path: str) -> Node | None:
        """Parse a file and return the root node, or None on failure."""
        parser = self._get_parser(file_path)
        if not parser:
            return None
        try:
            source = Path(file_path).read_text(encoding="utf-8")
            tree = parser.parse(source.encode("utf-8"))
            return tree.root_node
        except Exception:
            logger.debug("Failed to parse %s", file_path, exc_info=True)
            return None

    def resolve_symbols(
        self,
        file_path: str,
        line_ranges: list[tuple[int, int]],
    ) -> list[str]:
        root = self._parse_file(file_path)
        if root is None:
            return ["<parse-error>"]

        symbols = _extract_symbols(root)

        matched: list[str] = []
        for hunk_start, hunk_end in line_ranges:
            for sym in symbols:
                if sym.start_line <= hunk_end and sym.end_line >= hunk_start:
                    qname = sym.qualified_name
                    if qname not in matched:
                        matched.append(qname)

        if not matched:
            matched.append("<module>")
        return matched

    def build_test_graph(self, test_dir: str = "tests/") -> TestGraph:
        from aiv.lib.evidence_collector import TestGraph

        graph = TestGraph()
        test_root = Path(test_dir)
        if not test_root.exists():
            return graph

        for ext in self.extensions:
            pattern = f"*{ext}"
            for test_file in test_root.rglob(pattern):
                rel_path = str(test_file).replace("\\", "/")
                root = self._parse_file(str(test_file))
                if root is None:
                    continue

                analysis = _analyze_file(root)
                graph.imports[rel_path] = analysis.imports

                # Filter to test functions (test_ or it/describe/test patterns)
                test_calls: dict[str, set[str]] = {}
                all_func_calls = analysis.calls
                for func_name, called in all_func_calls.items():
                    if self._is_test_function(func_name):
                        resolved = set(called)
                        # One level of helper indirection
                        for helper_name in called:
                            if helper_name in all_func_calls:
                                resolved |= all_func_calls[helper_name]
                        test_calls[func_name] = resolved

                if test_calls:
                    graph.calls[rel_path] = test_calls

        return graph

    def find_downstream_callers(
        self,
        changed_symbols: list[str],
        src_dir: str = "src/",
        exclude_file: str = "",
    ) -> list[DownstreamCaller]:
        from aiv.lib.evidence_collector import DownstreamCaller

        callers: list[DownstreamCaller] = []
        src_root = Path(src_dir)
        if not src_root.exists():
            return callers

        exclude_posix = exclude_file.replace("\\", "/")

        for ext in self.extensions:
            pattern = f"*{ext}"
            for src_file in src_root.rglob(pattern):
                rel_path = str(src_file).replace("\\", "/")
                if rel_path == exclude_posix:
                    continue

                root = self._parse_file(str(src_file))
                if root is None:
                    continue

                analysis = _analyze_file(root)

                for func_name, called in analysis.calls.items():
                    for symbol in changed_symbols:
                        bare = symbol.split(".")[-1] if "." in symbol else symbol
                        if bare in called and bare in analysis.imports:
                            callers.append(
                                DownstreamCaller(
                                    file=rel_path,
                                    function=func_name,
                                    symbol_called=symbol,
                                )
                            )

        return callers

    @staticmethod
    def _is_test_function(name: str) -> bool:
        """Check if a function name looks like a test function.

        Covers Python-style (test_*), Jest/Vitest (it, test, describe),
        and Mocha patterns.
        """
        return name.startswith("test_") or name.startswith("test") or name in ("it", "test", "describe")
