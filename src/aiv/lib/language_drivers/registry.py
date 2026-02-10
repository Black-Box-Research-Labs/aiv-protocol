"""Driver registry — maps file extensions to LanguageDriver instances.

The registry is populated at import time with the built-in PythonDriver.
Tree-sitter drivers are registered lazily when their packages are available.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiv.lib.language_drivers.protocol import LanguageDriver

logger = logging.getLogger(__name__)

# extension → driver instance (e.g. ".py" → PythonDriver())
_registry: dict[str, LanguageDriver] = {}


def register_driver(driver: LanguageDriver) -> None:
    """Register a driver for all its declared extensions."""
    for ext in driver.extensions:
        _registry[ext] = driver
    logger.debug("Registered %s driver for extensions: %s", driver.name, driver.extensions)


def get_driver(file_path: str) -> LanguageDriver | None:
    """Look up the driver for a file by its extension.

    Returns None if no driver is registered for the file's extension.
    """
    for ext in sorted(_registry, key=len, reverse=True):
        if file_path.endswith(ext):
            return _registry[ext]
    return None


def registered_extensions() -> list[str]:
    """Return all registered file extensions."""
    return list(_registry.keys())


def _bootstrap() -> None:
    """Register built-in drivers. Called once at import time."""
    from aiv.lib.language_drivers.python_driver import PythonDriver

    register_driver(PythonDriver())

    # Try to register tree-sitter drivers if available
    try:
        from aiv.lib.language_drivers.treesitter_driver import TreeSitterDriver

        ts_driver = TreeSitterDriver()
        if ts_driver.available:
            register_driver(ts_driver)
        else:
            logger.debug("tree-sitter packages not installed; JS/TS driver unavailable")
    except ImportError:
        logger.debug("tree-sitter driver import failed; JS/TS driver unavailable")


_bootstrap()
