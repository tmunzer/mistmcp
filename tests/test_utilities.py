"""Tests for the mistmcp device utilities dispatcher."""

import threading
from enum import Enum
from types import SimpleNamespace
from uuid import UUID

import pytest
from fastmcp.exceptions import ToolError

import mistmcp.tools.utilities as utilities_module
from mistmcp.config import config


class FakeContext:
    def __init__(self) -> None:
        self.progress_updates: list[tuple[float,
                                          float | None, str | None]] = []
        self.info_messages: list[str] = []
        self.warning_messages: list[str] = []
        self.state: dict[str, bool] = {}
        self.elicit_calls: list[tuple[str, object | None]] = []

    async def report_progress(
        self,
        progress: float,
        total: float | None = None,
        message: str | None = None,
    ) -> None:
        self.progress_updates.append((progress, total, message))

    async def info(self, message: str) -> None:
        self.info_messages.append(message)

    async def warning(self, message: str) -> None:
        self.warning_messages.append(message)

    async def get_state(self, key: str) -> bool | None:
        return self.state.get(key)

    async def elicit(self, message: str, response_type=None):
        self.elicit_calls.append((message, response_type))
        raise AssertionError(
            "ctx.elicit should not be called when elicitation is disabled")


class FakeUtilityResponse:
    def __init__(
        self,
        *,
        done: bool = True,
        ws_required: bool = True,
        ws_data: list[str] | None = None,
    ) -> None:
        self.done = done
        self.ws_required = ws_required
        self.ws_data = ws_data or []
        self.trigger_api_response = SimpleNamespace(
            status_code=200, data={"ok": True})
        self.disconnected = False

    def disconnect(self) -> None:
        self.disconnected = True


def test_describe_supported_device_utilities_exposes_expected_actions() -> None:
    description = utilities_module.describe_supported_device_utilities(
        utilities_module.DeviceUtilityType.EX
    )

    utility_names = [utility["name"] for utility in description["utilities"]]
    utilities_by_name = {
        utility["name"]: utility for utility in description["utilities"]
    }

    assert description["device_type"] == "ex"
    assert "ping" in utility_names
    assert "bouncePort" in utility_names
    assert "createShellSession" not in utility_names
    assert utilities_by_name["bouncePort"]["requires_write_tools"] is True
    assert utilities_by_name["bouncePort"]["requires_elicitation"] is True
    assert utilities_by_name["clearHitCount"]["requires_write_tools"] is True
    assert utilities_by_name["clearHitCount"]["requires_elicitation"] is False


def test_build_utility_kwargs_converts_enum_and_list_values() -> None:
    class ProbeProtocol(Enum):
        ICMP = "icmp"
        UDP = "udp"

    def fake_utility(
        apisession,
        site_id,
        device_id,
        host: str,
        protocol: ProbeProtocol | None = None,
        port_ids: list[str] | None = None,
        timeout: int = 3,
        on_message=None,
    ):
        del apisession, site_id, device_id, host, protocol, port_ids, timeout, on_message
        return None

    kwargs = utilities_module.build_utility_kwargs(
        fake_utility,
        {
            "host": "1.1.1.1",
            "protocol": "udp",
            "port_ids": ["ge-0/0/1", "ge-0/0/2"],
        },
        15,
    )

    assert kwargs == {
        "host": "1.1.1.1",
        "protocol": ProbeProtocol.UDP,
        "port_ids": ["ge-0/0/1", "ge-0/0/2"],
        "timeout": 15,
    }


@pytest.mark.asyncio
async def test_run_utilities_executes_supported_command(monkeypatch) -> None:
    ctx = FakeContext()
    recorded_call: dict[str, object] = {}

    def fake_ping(
        apisession,
        site_id,
        device_id,
        host: str,
        timeout: int = 3,
    ) -> FakeUtilityResponse:
        recorded_call.update(
            {
                "apisession": apisession,
                "site_id": site_id,
                "device_id": device_id,
                "host": host,
                "timeout": timeout,
            }
        )
        return FakeUtilityResponse(ws_data=["pong"])

    async def fake_get_apisession():
        return object(), "json"

    async def fake_process_response(response) -> None:
        assert response.status_code == 200

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.AP: {"ping": fake_ping}},
    )
    monkeypatch.setattr(utilities_module, "get_apisession",
                        fake_get_apisession)
    monkeypatch.setattr(utilities_module, "process_response",
                        fake_process_response)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.AP,
        "ping",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"host": "8.8.8.8"},
        25,
    )

    assert recorded_call["host"] == "8.8.8.8"
    assert recorded_call["timeout"] == 25
    assert result["completed"] is True
    assert result["stream_output"] == ["pong"]
    assert ctx.progress_updates


@pytest.mark.asyncio
async def test_run_utilities_returns_partial_output_when_stream_stalls(
    monkeypatch,
) -> None:
    ctx = FakeContext()
    response = FakeUtilityResponse(done=False, ws_data=["partial"])

    def fake_ping(
        apisession,
        site_id,
        device_id,
        host: str,
        timeout: int = 3,
    ) -> FakeUtilityResponse:
        del apisession, site_id, device_id, host, timeout
        return response

    async def fake_get_apisession():
        return object(), "json"

    async def fake_process_response(response_arg) -> None:
        assert response_arg.status_code == 200

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.AP: {"ping": fake_ping}},
    )
    monkeypatch.setattr(utilities_module, "get_apisession",
                        fake_get_apisession)
    monkeypatch.setattr(utilities_module, "process_response",
                        fake_process_response)
    monkeypatch.setattr(utilities_module, "UTILITY_WAIT_TIMEOUT_SECONDS", 0)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.AP,
        "ping",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"host": "8.8.8.8"},
        25,
    )

    assert result["completed"] is False
    assert result["stream_output"] == ["partial"]
    assert response.disconnected is True
    assert ctx.warning_messages


@pytest.mark.asyncio
async def test_run_utilities_waits_for_async_trigger_response(monkeypatch) -> None:
    ctx = FakeContext()
    response = FakeUtilityResponse(done=False, ws_required=False)
    response.trigger_api_response = None

    def fake_cable_test(
        apisession,
        site_id,
        device_id,
        port_id: str,
        timeout: int = 10,
    ) -> FakeUtilityResponse:
        del apisession, site_id, device_id, port_id, timeout

        def complete_trigger() -> None:
            response.trigger_api_response = SimpleNamespace(
                status_code=200,
                data={"session": "abc", "id": "capture"},
            )
            response.ws_required = True
            response.done = True
            response.ws_data.append("cable test complete")

        threading.Timer(0.05, complete_trigger).start()
        return response

    async def fake_get_apisession():
        return object(), "json"

    async def fake_process_response(response_arg) -> None:
        assert response_arg.status_code == 200

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.EX: {"cableTest": fake_cable_test}},
    )
    monkeypatch.setattr(utilities_module, "get_apisession",
                        fake_get_apisession)
    monkeypatch.setattr(utilities_module, "process_response",
                        fake_process_response)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.EX,
        "cableTest",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"port_id": "mge-0/0/1"},
        None,
    )

    assert result["completed"] is True
    assert result["trigger_response"] == {"session": "abc", "id": "capture"}
    assert result["stream_output"] == ["cable test complete"]


@pytest.mark.asyncio
async def test_run_utilities_blocks_mutating_actions_without_write_tools(
    monkeypatch,
) -> None:
    ctx = FakeContext()

    def fake_bounce(
        apisession,
        site_id,
        device_id,
        port_ids: list[str],
        timeout: int = 5,
    ) -> FakeUtilityResponse:
        del apisession, site_id, device_id, port_ids, timeout
        return FakeUtilityResponse()

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.EX: {"bouncePort": fake_bounce}},
    )
    monkeypatch.setattr(config, "enable_write_tools", False)

    with pytest.raises(ToolError):
        await utilities_module.run_utilities(
            ctx,
            utilities_module.DeviceUtilityType.EX,
            "bouncePort",
            UUID("00000000-0000-0000-0000-000000000001"),
            UUID("00000000-0000-0000-0000-000000000002"),
            {"port_ids": ["ge-0/0/1"]},
            None,
        )


@pytest.mark.asyncio
async def test_run_utilities_prompts_before_mutating_action(monkeypatch) -> None:
    ctx = FakeContext()
    recorded_call: dict[str, object] = {}

    def fake_bounce(
        apisession,
        site_id,
        device_id,
        port_ids: list[str],
        timeout: int = 5,
    ) -> FakeUtilityResponse:
        recorded_call.update(
            {
                "apisession": apisession,
                "site_id": site_id,
                "device_id": device_id,
                "port_ids": port_ids,
                "timeout": timeout,
            }
        )
        return FakeUtilityResponse(ws_data=["done"])

    async def fake_get_apisession():
        return object(), "json"

    async def fake_process_response(response) -> None:
        assert response.status_code == 200

    async def fake_elicitation_handler(*, message: str, ctx) -> SimpleNamespace:
        assert "bouncePort" in message
        assert ctx is not None
        return SimpleNamespace(action="accept")

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.EX: {"bouncePort": fake_bounce}},
    )
    monkeypatch.setattr(utilities_module, "get_apisession",
                        fake_get_apisession)
    monkeypatch.setattr(utilities_module, "process_response",
                        fake_process_response)
    monkeypatch.setattr(
        utilities_module,
        "config_elicitation_handler",
        fake_elicitation_handler,
    )
    monkeypatch.setattr(config, "enable_write_tools", True)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.EX,
        "bouncePort",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"port_ids": ["ge-0/0/1"]},
        12,
    )

    assert recorded_call["port_ids"] == ["ge-0/0/1"]
    assert recorded_call["timeout"] == 12
    assert result["completed"] is True


@pytest.mark.asyncio
async def test_run_utilities_skips_elicitation_for_non_disruptive_mutation(
    monkeypatch,
) -> None:
    ctx = FakeContext()
    recorded_call: dict[str, object] = {}

    def fake_clear_hit_count(
        apisession,
        site_id,
        device_id,
        policy_name: str,
    ) -> FakeUtilityResponse:
        recorded_call.update(
            {
                "apisession": apisession,
                "site_id": site_id,
                "device_id": device_id,
                "policy_name": policy_name,
            }
        )
        return FakeUtilityResponse(ws_required=False)

    async def fake_get_apisession():
        return object(), "json"

    async def fake_process_response(response) -> None:
        assert response.status_code == 200

    async def unexpected_elicitation_handler(*, message: str, ctx) -> SimpleNamespace:
        raise AssertionError(
            f"Elicitation should not be requested for clearHitCount: {message}"
        )

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.EX: {
            "clearHitCount": fake_clear_hit_count}},
    )
    monkeypatch.setattr(utilities_module, "get_apisession",
                        fake_get_apisession)
    monkeypatch.setattr(utilities_module, "process_response",
                        fake_process_response)
    monkeypatch.setattr(
        utilities_module,
        "config_elicitation_handler",
        unexpected_elicitation_handler,
    )
    monkeypatch.setattr(config, "enable_write_tools", True)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.EX,
        "clearHitCount",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"policy_name": "block-social"},
        None,
    )

    assert recorded_call["policy_name"] == "block-social"
    assert result["completed"] is True


@pytest.mark.asyncio
async def test_run_utilities_returns_decline_before_mutating_action(
    monkeypatch,
) -> None:
    ctx = FakeContext()
    utility_called = False

    def fake_bounce(
        apisession,
        site_id,
        device_id,
        port_ids: list[str],
        timeout: int = 5,
    ) -> FakeUtilityResponse:
        del apisession, site_id, device_id, port_ids, timeout
        nonlocal utility_called
        utility_called = True
        return FakeUtilityResponse()

    async def fake_elicitation_handler(*, message: str, ctx) -> SimpleNamespace:
        del message, ctx
        return SimpleNamespace(action="decline")

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.EX: {"bouncePort": fake_bounce}},
    )
    monkeypatch.setattr(
        utilities_module,
        "config_elicitation_handler",
        fake_elicitation_handler,
    )
    monkeypatch.setattr(config, "enable_write_tools", True)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.EX,
        "bouncePort",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"port_ids": ["ge-0/0/1"]},
        None,
    )

    assert result == {"message": "Action declined by user."}
    assert utility_called is False


@pytest.mark.asyncio
async def test_run_utilities_skips_elicitation_when_disabled_in_context(
    monkeypatch,
) -> None:
    ctx = FakeContext()
    ctx.state["disable_elicitation"] = True
    recorded_call: dict[str, object] = {}

    def fake_bounce(
        apisession,
        site_id,
        device_id,
        port_ids: list[str],
        timeout: int = 5,
    ) -> FakeUtilityResponse:
        recorded_call.update(
            {
                "apisession": apisession,
                "site_id": site_id,
                "device_id": device_id,
                "port_ids": port_ids,
                "timeout": timeout,
            }
        )
        return FakeUtilityResponse(ws_data=["done"])

    async def fake_get_apisession():
        return object(), "json"

    async def fake_process_response(response) -> None:
        assert response.status_code == 200

    monkeypatch.setattr(
        utilities_module,
        "SUPPORTED_DEVICE_UTILITIES",
        {utilities_module.DeviceUtilityType.EX: {"bouncePort": fake_bounce}},
    )
    monkeypatch.setattr(utilities_module, "get_apisession",
                        fake_get_apisession)
    monkeypatch.setattr(utilities_module, "process_response",
                        fake_process_response)
    monkeypatch.setattr(config, "enable_write_tools", True)

    result = await utilities_module.run_utilities(
        ctx,
        utilities_module.DeviceUtilityType.EX,
        "bouncePort",
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        {"port_ids": ["ge-0/0/1"]},
        12,
    )

    assert recorded_call["port_ids"] == ["ge-0/0/1"]
    assert result["completed"] is True
    assert ctx.elicit_calls == []
