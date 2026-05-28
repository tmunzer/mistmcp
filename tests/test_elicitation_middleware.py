from types import SimpleNamespace

from mistmcp.config import config
from mistmcp.elicitation_middleware import ElicitationMiddleware
from mistmcp.elicitation_processor import config_elicitation_handler


class FakeFastMCPContext:
    def __init__(self) -> None:
        self.state: dict[str, bool] = {}
        self.enabled_calls: list[dict[str, set[str]]] = []
        self.disabled_calls: list[dict[str, set[str]]] = []
        self.elicit_calls: list[tuple[str, None]] = []

    async def set_state(self, key: str, value: bool) -> None:
        self.state[key] = value

    async def get_state(self, key: str) -> bool | None:
        return self.state.get(key)

    async def enable_components(self, **kwargs) -> None:
        self.enabled_calls.append(kwargs)

    async def disable_components(self, **kwargs) -> None:
        self.disabled_calls.append(kwargs)

    async def elicit(self, message: str, response_type=None):
        self.elicit_calls.append((message, response_type))
        raise AssertionError(
            "ctx.elicit should not be called when elicitation is disabled")


class FakeMiddlewareContext:
    def __init__(self, fastmcp_context: FakeFastMCPContext) -> None:
        self.fastmcp_context = fastmcp_context
        self.message = SimpleNamespace(
            params=SimpleNamespace(
                capabilities=SimpleNamespace(elicitation=None),
            )
        )


async def test_stdio_disable_elicitation_sets_state_and_skips_prompt(
    monkeypatch,
) -> None:
    monkeypatch.setattr(config, "enable_write_tools", True)
    monkeypatch.setattr(config, "disable_elicitation", True)
    monkeypatch.setattr(config, "transport_mode", "stdio")

    fastmcp_context = FakeFastMCPContext()
    context = FakeMiddlewareContext(fastmcp_context)
    middleware = ElicitationMiddleware()

    async def call_next(_context):
        return "ok"

    result = await middleware.on_initialize(context, call_next)

    assert result == "ok"
    assert fastmcp_context.state == {"disable_elicitation": True}
    assert fastmcp_context.enabled_calls == [
        {"tags": {"write"}, "components": {"tool"}}
    ]
    assert fastmcp_context.disabled_calls == [
        {"tags": {"write_delete"}, "components": {"tool"}}
    ]

    elicitation_result = await config_elicitation_handler("test", fastmcp_context)

    assert elicitation_result.action == "accept"
    assert fastmcp_context.elicit_calls == []
