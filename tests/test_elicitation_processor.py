"""Tests for the elicitation handler's stateless fail-closed guard"""

import pytest

from mistmcp.config import config
from mistmcp.elicitation_processor import (
    ElicitationUnavailableError,
    config_elicitation_handler,
)


class FakeCtx:
    def __init__(self, state=None, elicit_exc=None) -> None:
        self._state = state or {}
        self._elicit_exc = elicit_exc
        self.elicit_calls: list = []

    async def get_state(self, key):
        return self._state.get(key)

    async def elicit(self, message, response_type=None):
        self.elicit_calls.append((message, response_type))
        if self._elicit_exc is not None:
            raise self._elicit_exc
        return None


async def test_auto_accepts_when_state_true(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", True)
    monkeypatch.setattr(config, "transport_mode", "http")
    ctx = FakeCtx(state={"disable_elicitation": True})

    result = await config_elicitation_handler("msg", ctx)

    assert result.action == "accept"
    assert ctx.elicit_calls == []  # state check returns before the guard


async def test_raises_unavailable_in_stateless_http(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", True)
    monkeypatch.setattr(config, "transport_mode", "http")
    ctx = FakeCtx(state={})  # disable_elicitation not set

    with pytest.raises(ElicitationUnavailableError):
        await config_elicitation_handler("msg", ctx)

    assert ctx.elicit_calls == []  # guard fired BEFORE ctx.elicit


async def test_calls_elicit_in_stateful(monkeypatch) -> None:
    monkeypatch.setattr(config, "stateless", False)
    monkeypatch.setattr(config, "transport_mode", "http")
    sentinel = RuntimeError("elicit-reached")
    ctx = FakeCtx(state={}, elicit_exc=sentinel)

    # In stateful mode the guard must NOT fire; ctx.elicit is reached (and here
    # raises our sentinel, proving the handler proceeded past the guard).
    with pytest.raises(RuntimeError, match="elicit-reached"):
        await config_elicitation_handler("msg", ctx)

    assert len(ctx.elicit_calls) == 1
