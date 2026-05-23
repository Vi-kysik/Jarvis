"""Regression tests for ModelRegistry.provider_for full Claude model IDs.

Claude Code accepts both short aliases (opus/sonnet/haiku) and full Claude
model IDs (claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5-20251001).
The registry historically matched only the short aliases, so a full ID fell
through to the codex branch and broke Claude routing for clients that pass
the canonical model name.
"""

from __future__ import annotations

import pytest

from ductor_bot.config import ModelRegistry


@pytest.mark.parametrize(
    "model_id",
    [
        "claude-opus-4-7",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    ],
)
def test_provider_for_full_claude_model_ids(model_id: str) -> None:
    assert ModelRegistry.provider_for(model_id) == "claude"


def test_provider_for_short_aliases_still_claude() -> None:
    assert ModelRegistry.provider_for("opus") == "claude"
    assert ModelRegistry.provider_for("sonnet") == "claude"
    assert ModelRegistry.provider_for("haiku") == "claude"


def test_provider_for_non_claude_unchanged() -> None:
    assert ModelRegistry.provider_for("gpt-5.2-codex") == "codex"
    assert ModelRegistry.provider_for("gemini-2.5-pro") == "gemini"
