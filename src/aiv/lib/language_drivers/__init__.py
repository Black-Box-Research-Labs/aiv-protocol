"""Language-specific drivers for polyglot evidence collection.

Each driver implements the LanguageDriver protocol, providing:
- Symbol resolution (map diff line ranges to enclosing function/class names)
- Test graph building (import + call graph for test files)
- Downstream caller analysis (find production callers of changed symbols)

The registry maps file extensions to driver instances.
"""

from __future__ import annotations

from aiv.lib.language_drivers.protocol import LanguageDriver
from aiv.lib.language_drivers.python_driver import PythonDriver
from aiv.lib.language_drivers.registry import get_driver, register_driver

__all__ = [
    "LanguageDriver",
    "PythonDriver",
    "get_driver",
    "register_driver",
]
