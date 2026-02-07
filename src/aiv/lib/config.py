"""
aiv/lib/config.py

Configuration models for customizing validation behavior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from .errors import ConfigurationError

if TYPE_CHECKING:
    from pathlib import Path


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
        """Load configuration from YAML file."""
        import yaml

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
