"""Centralised loading of user-defined environment secrets from ``~/.jarvis/.env``.

The file uses standard dotenv syntax::

    # Comment
    PPLX_API_KEY=sk-xxx
    DEEPSEEK_API_KEY=sk-yyy
    export MY_VAR="quoted value"

Values are injected into CLI subprocesses (host and Docker) but never
override variables that are already set in the environment.

The file is re-read automatically when its mtime changes, so edits take
effect on the next CLI invocation without a bot restart.
"""

from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")

_cache: dict[str, str] | None = None
_cache_path: Path | None = None
_cache_mtime: float = 0.0


def _parse_dotenv(path: Path) -> dict[str, str]:
    """Parse a ``.env`` file into a ``{key: value}`` dict.

    Supports ``#`` comments, ``export`` prefix, single/double quotes.
    """
    result: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return result

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        key, sep, value = line.partition("=")
        if sep != "=":
            continue
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        # Strip matching quotes.
        if len(value) >= 2 and value[0] in {'"', "'"} and value[-1] == value[0]:
            value = value[1:-1]
        else:
            # Remove inline comment (unquoted values only).
            value = value.split("#", 1)[0].strip()
        result[key] = value

    return result


def _current_mtime(path: Path) -> float:
    """Return mtime of *path*, or ``0.0`` if the file does not exist."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def load_env_secrets(env_file: Path) -> dict[str, str]:
    """Load secrets from *env_file*, re-reading when the file changes.

    Uses mtime-based cache invalidation so edits to ``.env`` take effect
    on the next CLI invocation without a bot restart.
    """
    global _cache, _cache_path, _cache_mtime  # noqa: PLW0603

    mtime = _current_mtime(env_file)

    # Cache hit: same path and file unchanged.
    if _cache is not None and _cache_path == env_file and mtime == _cache_mtime:
        return _cache

    # File missing or deleted.
    if mtime == 0.0:
        if _cache_mtime != 0.0 and _cache_path == env_file:
            logger.info("Env file removed: %s", env_file)
        _cache = {}
        _cache_path = env_file
        _cache_mtime = 0.0
        return _cache

    # (Re-)parse.
    _cache = _parse_dotenv(env_file)
    _cache_path = env_file
    _cache_mtime = mtime
    if _cache:
        logger.info("Loaded %d secret(s) from %s", len(_cache), env_file)
    return _cache


def clear_cache() -> None:
    """Reset the cached secrets (for tests)."""
    global _cache, _cache_path, _cache_mtime  # noqa: PLW0603
    _cache = None
    _cache_path = None
    _cache_mtime = 0.0


def resolve_env_placeholders(data: object, env_file: Path) -> object:
    """Recursively resolve ``"${VAR_NAME}"`` string values in *data*.

    Looks up ``VAR_NAME`` in the real process environment first, then in
    *env_file* (``~/.jarvis/.env``). Unresolved placeholders are replaced
    with ``""`` so config validation fails loudly (missing token) instead
    of silently keeping the literal ``${...}`` string.

    Only exact whole-string matches (``"${VAR}"``, not ``"foo ${VAR}"``)
    are treated as placeholders — this keeps normal config strings safe.
    """
    if isinstance(data, dict):
        return {key: resolve_env_placeholders(value, env_file) for key, value in data.items()}
    if isinstance(data, list):
        return [resolve_env_placeholders(item, env_file) for item in data]
    if isinstance(data, str):
        match = _PLACEHOLDER_RE.match(data)
        if match is None:
            return data
        var_name = match.group(1)
        if var_name in os.environ:
            return os.environ[var_name]
        secrets = load_env_secrets(env_file)
        if var_name in secrets:
            return secrets[var_name]
        logger.warning("Config placeholder ${%s} not found in environment or %s", var_name, env_file)
        return ""
    return data
