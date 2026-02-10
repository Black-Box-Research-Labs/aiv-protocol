"""
aiv/lib/config.py

Configuration models for customizing validation behavior.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

try:
    import yaml
except ImportError as _yaml_err:
    raise ImportError("PyYAML is required for AIV configuration. Install it with: pip install PyYAML") from _yaml_err

from pathlib import Path

from .errors import ConfigurationError


class ZeroTouchConfig(BaseModel):
    """Configuration for Zero-Touch validation."""

    # Patterns that indicate non-zero-touch reproduction
    prohibited_patterns: list[str] = Field(
        default=[
            r"^(git clone|git checkout|git pull)",
            r"(npm|yarn|pip|poetry|uv)\s+install",
            r"(python|node|npm run|yarn|pytest|cargo|go run)\s+",
            r"^cd\s+",
            r"(docker|podman)\s+run",
            r"open\s+(browser|terminal|app)",
            r"(click|tap|press|select)\s+",
        ]
    )

    # Patterns that are always acceptable
    allowed_patterns: list[str] = Field(
        default=[
            r"^N/?A$",
            r"^CI\s+(Automation|automation)",
            r"^See\s+CI",
            r"^Link\s+above",
            r"^Automated\s+via",
            r"^https?://",
        ]
    )

    # Multi-step separators
    step_separators: list[str] = Field(
        default=[
            ";",
            " && ",
            " then ",
            r"\d+\.",
            r"step\s+\d",
        ]
    )

    max_steps: int = Field(default=1, ge=1)


class AntiCheatConfig(BaseModel):
    """Configuration for Anti-Cheat detection."""

    # File patterns to analyze for test modifications
    test_file_patterns: list[str] = Field(
        default=[
            r"test_.*\.py$",
            r".*_test\.py$",
            r"tests?/.*\.py$",
            r".*\.test\.(js|ts|jsx|tsx)$",
            r".*\.spec\.(js|ts|jsx|tsx)$",
        ]
    )

    # Patterns indicating assertion deletion
    assertion_patterns: list[str] = Field(
        default=[
            r"^\-\s*assert\s+",
            r"^\-\s*self\.assert",
            r"^\-\s*expect\(",
            r"^\-\s*should\.",
        ]
    )

    # Patterns indicating test skipping
    skip_patterns: list[str] = Field(
        default=[
            r"@pytest\.mark\.skip",
            r"@unittest\.skip",
            r"\.skip\(",
            r"xit\(",
            r"xdescribe\(",
        ]
    )

    # Patterns indicating mock/bypass
    bypass_patterns: list[str] = Field(
        default=[
            r"MOCK[_\s]*=\s*True",
            r"SKIP[_\s]*=\s*True",
            r"--force",
            r"--no-verify",
            r"if\s+DEBUG",
        ]
    )


class MutableBranchConfig(BaseModel):
    """Configuration for immutability checking."""

    # Branch names that are always mutable
    mutable_branches: set[str] = Field(
        default={
            "main",
            "master",
            "develop",
            "dev",
            "staging",
            "trunk",
            "HEAD",
        }
    )

    # Minimum SHA length to accept
    min_sha_length: int = Field(default=7, ge=7, le=40)


class HookConfig(BaseModel):
    """Configuration for the pre-commit hook.

    Controls which files are treated as "functional" (requiring a verification
    packet) vs "non-functional" (docs, config — no packet required).
    """

    functional_prefixes: list[str] = Field(
        default=[
            "src/",
            "lib/",
            "app/",
            "pkg/",
            "cmd/",
            "internal/",
            "engine/",
            "infrastructure/",
            "scripts/",
            "tests/",
            ".github/workflows/",
            ".husky/",
        ],
        description="Directory prefixes that mark files as functional code",
    )

    functional_root_files: list[str] = Field(
        default=[
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "package.json",
            "package-lock.json",
            ".gitignore",
            ".env.example",
        ],
        description="Root-level files that are treated as functional code",
    )


class AIVConfig(BaseSettings):
    """
    Main configuration for the AIV Protocol Suite.

    Can be loaded from environment variables or .aiv.yml file.
    """

    model_config = {"env_prefix": "AIV_"}

    # Validation strictness
    strict_mode: bool = Field(default=True, description="If True, warnings are treated as errors")

    # Component configs
    zero_touch: ZeroTouchConfig = Field(default_factory=ZeroTouchConfig)
    anti_cheat: AntiCheatConfig = Field(default_factory=AntiCheatConfig)
    mutable_branches: MutableBranchConfig = Field(default_factory=MutableBranchConfig)
    hook: HookConfig = Field(default_factory=HookConfig)

    # Fast-track configuration
    fast_track_patterns: list[str] = Field(
        default=[
            r"\.md$",
            r"\.txt$",
            r"\.gitignore$",
            r"\.editorconfig$",
            r"LICENSE",
            r"README",
        ],
        description="File patterns eligible for fast-track (Addendum 2.3)",
    )

    @classmethod
    def from_file(cls, path: Path) -> AIVConfig:
        """
        Load AIV configuration from a YAML file.

        If the file does not exist, returns a default AIVConfig instance.
        On successful parse and validation, returns an AIVConfig populated
        from the YAML contents.

        Parameters:
            path (Path): Filesystem path to the YAML configuration file.

        Returns:
            AIVConfig: Configuration loaded from the file, or a default instance if the file is missing.

        Raises:
            ConfigurationError: If the YAML cannot be parsed or the file contents are invalid for AIVConfig.
        """
        if not path.exists():
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse {path}: {e}") from e

        try:
            return cls(**data)
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration in {path}: {e}") from e


# ---------------------------------------------------------------------------
# Shared hook config loader (single source of truth for all enforcement layers)
# ---------------------------------------------------------------------------

_DEFAULT_FUNCTIONAL_PREFIXES: tuple[str, ...] = tuple(HookConfig().functional_prefixes)
_DEFAULT_FUNCTIONAL_ROOT_FILES: set[str] = set(HookConfig().functional_root_files)


def load_hook_config(
    config_path: Path | None = None,
) -> tuple[tuple[str, ...], set[str]]:
    """
    Load functional file prefixes and root-file names from an AIV hook configuration.

    If a YAML file exists at `config_path` (or `./.aiv.yml` when `None`),
    extract the `hook.functional_prefixes` and `hook.functional_root_files`
    values; otherwise, return the built-in HookConfig defaults.

    Parameters:
        config_path (Path | None): Path to the `.aiv.yml` file; when `None`, defaults to `./.aiv.yml`.

    Returns:
        tuple[tuple[str, ...], set[str]]: A pair where the first element
            is a tuple of functional prefixes and the second is a set of
            functional root-file names.
    """
    try:
        path = config_path or Path(".aiv.yml")
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            hook_data = data.get("hook", {})
            raw_prefixes = hook_data.get("functional_prefixes", _DEFAULT_FUNCTIONAL_PREFIXES)
            raw_root_files = hook_data.get("functional_root_files", _DEFAULT_FUNCTIONAL_ROOT_FILES)
            if not isinstance(raw_prefixes, (list, tuple)):
                raw_prefixes = _DEFAULT_FUNCTIONAL_PREFIXES
            if not isinstance(raw_root_files, (list, tuple, set)):
                raw_root_files = _DEFAULT_FUNCTIONAL_ROOT_FILES
            return tuple(raw_prefixes), set(raw_root_files)
    except Exception:
        pass
    return _DEFAULT_FUNCTIONAL_PREFIXES, _DEFAULT_FUNCTIONAL_ROOT_FILES
