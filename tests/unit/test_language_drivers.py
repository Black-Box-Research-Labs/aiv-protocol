"""Tests for aiv.lib.language_drivers — polyglot evidence collection.

Tests the LanguageDriver protocol, PythonDriver (delegation), TreeSitterDriver
(JS/TS symbol resolution, test graph, downstream callers), and the registry.
"""

from __future__ import annotations

import pytest

from aiv.lib.language_drivers import LanguageDriver, PythonDriver, get_driver
from aiv.lib.language_drivers.registry import registered_extensions

# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_python_always_registered(self) -> None:
        exts = registered_extensions()
        assert ".py" in exts

    def test_get_driver_for_python(self) -> None:
        driver = get_driver("src/aiv/lib/config.py")
        assert driver is not None
        assert driver.name == "python"

    def test_get_driver_for_unknown_extension(self) -> None:
        driver = get_driver("README.md")
        assert driver is None

    def test_get_driver_for_nonexistent_file(self) -> None:
        driver = get_driver("/does/not/exist.py")
        assert driver is not None
        assert driver.name == "python"


# ---------------------------------------------------------------------------
# PythonDriver tests
# ---------------------------------------------------------------------------


class TestPythonDriver:
    def test_conforms_to_protocol(self) -> None:
        driver = PythonDriver()
        assert isinstance(driver, LanguageDriver)

    def test_name(self) -> None:
        assert PythonDriver().name == "python"

    def test_extensions(self) -> None:
        assert PythonDriver().extensions == (".py",)

    def test_resolve_symbols_delegates(self, tmp_path) -> None:
        src = tmp_path / "example.py"
        src.write_text("def foo():\n    return 1\n", encoding="utf-8")
        driver = PythonDriver()
        result = driver.resolve_symbols(str(src), [(1, 2)])
        assert "foo" in result

    def test_build_test_graph_delegates(self, tmp_path) -> None:
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_foo.py").write_text(
            "from mymod import bar\n\ndef test_bar():\n    bar()\n",
            encoding="utf-8",
        )
        driver = PythonDriver()
        graph = driver.build_test_graph(str(test_dir))
        assert len(graph.imports) == 1

    def test_find_downstream_callers_delegates(self, tmp_path) -> None:
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "caller.py").write_text(
            "from mymod import target\n\ndef run():\n    target()\n",
            encoding="utf-8",
        )
        driver = PythonDriver()
        callers = driver.find_downstream_callers(["target"], src_dir=str(src_dir))
        assert len(callers) == 1
        assert callers[0].function == "run"


# ---------------------------------------------------------------------------
# TreeSitterDriver tests
# ---------------------------------------------------------------------------

try:
    from aiv.lib.language_drivers.treesitter_driver import TreeSitterDriver

    _TREESITTER_AVAILABLE = TreeSitterDriver().available
except ImportError:
    _TREESITTER_AVAILABLE = False

pytestmark_ts = pytest.mark.skipif(
    not _TREESITTER_AVAILABLE,
    reason="tree-sitter packages not installed",
)


@pytestmark_ts
class TestTreeSitterDriverProtocol:
    def test_conforms_to_protocol(self) -> None:
        driver = TreeSitterDriver()
        assert isinstance(driver, LanguageDriver)

    def test_name(self) -> None:
        assert TreeSitterDriver().name == "javascript/typescript"

    def test_extensions_include_js_ts(self) -> None:
        exts = TreeSitterDriver().extensions
        assert ".js" in exts
        assert ".ts" in exts
        assert ".tsx" in exts

    def test_registered_for_js(self) -> None:
        driver = get_driver("src/app.js")
        assert driver is not None
        assert "javascript" in driver.name or "typescript" in driver.name

    def test_registered_for_ts(self) -> None:
        driver = get_driver("src/app.ts")
        assert driver is not None


# ---------------------------------------------------------------------------
# TreeSitterDriver: Symbol Resolution (P1-6)
# ---------------------------------------------------------------------------


@pytestmark_ts
class TestTreeSitterSymbolResolution:
    def test_function_declaration(self, tmp_path) -> None:
        src = tmp_path / "example.js"
        src.write_text(
            "function loadConfig(path) {\n    return JSON.parse(path);\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(1, 2)])
        assert "loadConfig" in result

    def test_arrow_function(self, tmp_path) -> None:
        src = tmp_path / "example.js"
        src.write_text(
            "const processData = (input) => {\n    return input.map(x => x * 2);\n};\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(1, 3)])
        assert "processData" in result

    def test_class_and_methods(self, tmp_path) -> None:
        src = tmp_path / "service.ts"
        src.write_text(
            "class UserService {\n"
            "    constructor(db: any) {\n"
            "        this.db = db;\n"
            "    }\n"
            "\n"
            "    getUser(id: string) {\n"
            "        return this.db.find(id);\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        # Class declaration spans all lines
        result = driver.resolve_symbols(str(src), [(1, 9)])
        assert "UserService" in result
        assert "UserService.constructor" in result
        assert "UserService.getUser" in result

    def test_method_only(self, tmp_path) -> None:
        src = tmp_path / "service.ts"
        src.write_text(
            "class UserService {\n"
            "    getUser(id: string) {\n"
            "        return this.db.find(id);\n"
            "    }\n"
            "\n"
            "    deleteUser(id: string) {\n"
            "        return this.db.remove(id);\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(2, 4)])
        assert "UserService.getUser" in result
        assert "UserService.deleteUser" not in result

    def test_module_level_returns_module(self, tmp_path) -> None:
        src = tmp_path / "constants.js"
        src.write_text("const X = 1;\nconst Y = 2;\n", encoding="utf-8")
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(1, 2)])
        assert "<module>" in result

    def test_parse_error_returns_marker(self) -> None:
        driver = TreeSitterDriver()
        result = driver.resolve_symbols("/nonexistent/file.js", [(1, 5)])
        assert "<parse-error>" in result

    def test_typescript_file(self, tmp_path) -> None:
        src = tmp_path / "utils.ts"
        src.write_text(
            "export function formatDate(d: Date): string {\n    return d.toISOString();\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(1, 3)])
        assert "formatDate" in result

    def test_tsx_file(self, tmp_path) -> None:
        src = tmp_path / "Component.tsx"
        src.write_text(
            "function MyComponent(props: any) {\n    return <div>{props.name}</div>;\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(1, 3)])
        assert "MyComponent" in result

    def test_multi_symbol_hunk(self, tmp_path) -> None:
        src = tmp_path / "multi.js"
        src.write_text(
            "function alpha() {\n    return 1;\n}\n\n"
            "function beta() {\n    return 2;\n}\n\n"
            "function gamma() {\n    return 3;\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        result = driver.resolve_symbols(str(src), [(1, 11)])
        assert "alpha" in result
        assert "beta" in result
        assert "gamma" in result


# ---------------------------------------------------------------------------
# TreeSitterDriver: Test Graph (P1-7)
# ---------------------------------------------------------------------------


@pytestmark_ts
class TestTreeSitterTestGraph:
    def test_imports_extracted(self, tmp_path) -> None:
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "user.test.ts").write_text(
            "import { UserService, createService } from '../src/user-service';\n\n"
            "function testCreate() {\n    createService({});\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        graph = driver.build_test_graph(str(test_dir))
        values = list(graph.imports.values())
        assert len(values) == 1
        assert "UserService" in values[0]
        assert "createService" in values[0]

    def test_calls_extracted(self, tmp_path) -> None:
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "calc.test.js").write_text(
            "import { add } from '../src/calc';\n\n"
            "function testAdd() {\n    const r = add(1, 2);\n    console.log(r);\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        graph = driver.build_test_graph(str(test_dir))
        calls = list(graph.calls.values())
        assert len(calls) == 1
        test_calls = calls[0]
        assert "testAdd" in test_calls
        assert "add" in test_calls["testAdd"]

    def test_empty_test_dir(self, tmp_path) -> None:
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        driver = TreeSitterDriver()
        graph = driver.build_test_graph(str(test_dir))
        assert len(graph.imports) == 0
        assert len(graph.calls) == 0

    def test_nonexistent_test_dir(self) -> None:
        driver = TreeSitterDriver()
        graph = driver.build_test_graph("/nonexistent/tests/")
        assert len(graph.imports) == 0


# ---------------------------------------------------------------------------
# TreeSitterDriver: Downstream Callers (P1-8)
# ---------------------------------------------------------------------------


@pytestmark_ts
class TestTreeSitterDownstreamCallers:
    def test_finds_caller(self, tmp_path) -> None:
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "service.ts").write_text(
            "import { loadConfig } from './config';\n\n"
            "function startService() {\n    const cfg = loadConfig();\n    return cfg;\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        callers = driver.find_downstream_callers(["loadConfig"], src_dir=str(src_dir))
        assert len(callers) == 1
        assert callers[0].function == "startService"
        assert callers[0].symbol_called == "loadConfig"

    def test_excludes_committed_file(self, tmp_path) -> None:
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        target = src_dir / "config.ts"
        target.write_text(
            "import { readFile } from 'fs';\n\n"
            "export function loadConfig() {\n    return readFile('config.json');\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        callers = driver.find_downstream_callers(
            ["readFile"],
            src_dir=str(src_dir),
            exclude_file=str(target).replace("\\", "/"),
        )
        assert len(callers) == 0

    def test_no_callers_returns_empty(self, tmp_path) -> None:
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "other.ts").write_text(
            "function unrelated() {\n    return 42;\n}\n",
            encoding="utf-8",
        )
        driver = TreeSitterDriver()
        callers = driver.find_downstream_callers(["nonexistent"])
        assert len(callers) == 0

    def test_nonexistent_src_dir(self) -> None:
        driver = TreeSitterDriver()
        callers = driver.find_downstream_callers(["foo"], src_dir="/nonexistent/src/")
        assert len(callers) == 0
