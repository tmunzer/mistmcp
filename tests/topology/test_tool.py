"""MistMCP registration and topology workflow integration tests."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from mistmcp.server import _CUSTOM_TOOL_MODULES, mcp
from mistmcp.topology.models import JsonObject
from mistmcp.topology.tool import _run_topology_action, mist_topology

ORG_ID = "11111111-1111-1111-1111-111111111111"
SITE_ID = "22222222-2222-2222-2222-222222222222"


class FakeTopologyDataSource:
    def __init__(self) -> None:
        self.inventory_requests: list[tuple[str, str]] = []

    async def list_sites(self, org_id: str) -> list[JsonObject]:
        return [{"id": SITE_ID, "org_id": org_id, "name": "Test Site"}]

    async def site_devices(self, site_id: str) -> list[JsonObject]:
        return [{"id": "switch-1", "type": "switch", "site_id": site_id}]

    async def site_clients(self, site_id: str) -> list[JsonObject]:
        del site_id
        return []

    async def org_gateway_inventory(self, org_id: str) -> list[JsonObject]:
        del org_id
        return []

    async def org_site_inventory(self, org_id: str, site_id: str) -> list[JsonObject]:
        self.inventory_requests.append((org_id, site_id))
        return []

    async def org_sites(self, org_id: str) -> list[JsonObject]:
        return await self.list_sites(org_id)

    async def org_vpn_peers(self, org_id: str) -> list[JsonObject]:
        del org_id
        return []

    async def site_ports(self, site_id: str) -> list[JsonObject]:
        del site_id
        return []

    async def site_wired_clients(self, site_id: str) -> list[JsonObject]:
        del site_id
        return []


async def test_registers_read_only_topology_tool() -> None:
    tool = next(item for item in await mcp.list_tools() if item.name == "mist_topology")

    assert tool.parameters["required"] == ["action", "org_id"]
    assert tool.parameters["properties"]["action"]["enum"] == [
        "get_site_topology",
        "find_path",
        "get_wan_topology",
    ]
    assert tool.parameters["properties"]["org_id"]["format"] == "uuid"
    assert tool.parameters["properties"]["source"]["anyOf"][0]["minLength"] == 1
    assert tool.annotations is not None
    assert tool.annotations.readOnlyHint is True
    assert tool.annotations.destructiveHint is False


def test_topology_package_is_outside_generator_owned_tools() -> None:
    import mistmcp.topology.tool as topology_tool

    module_path = Path(inspect.getfile(topology_tool)).resolve()

    assert _CUSTOM_TOOL_MODULES["mist_topology"] == "mistmcp.topology.tool"
    assert module_path.parent.name == "topology"
    assert module_path.parent.parent.name == "mistmcp"


async def test_site_topology_uses_org_id_from_tool_parameters() -> None:
    source = FakeTopologyDataSource()

    result = await _run_topology_action(
        source,
        action="get_site_topology",
        org_id=ORG_ID,
        site_id=SITE_ID,
        include_clients=False,
    )

    assert isinstance(result, dict)
    assert result["graph"]["scopeId"] == SITE_ID
    assert source.inventory_requests == [(ORG_ID, SITE_ID)]


async def test_rejects_parameters_from_another_action() -> None:
    with pytest.raises(
        ValueError, match="Invalid parameters for action 'get_wan_topology'"
    ):
        await _run_topology_action(
            FakeTopologyDataSource(),
            action="get_wan_topology",
            org_id=ORG_ID,
            site_id=SITE_ID,
        )


async def test_tool_uses_mistmcp_request_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    request_session = object()
    source = FakeTopologyDataSource()
    client_factory = Mock()
    get_session = AsyncMock(return_value=(request_session, "json"))

    def build_client(session: Any) -> FakeTopologyDataSource:
        client_factory(session)
        return source

    monkeypatch.setattr("mistmcp.topology.tool.get_apisession", get_session)
    monkeypatch.setattr("mistmcp.topology.tool.MistAPIClient", build_client)

    result = await mist_topology(
        action="get_wan_topology",
        org_id=UUID(ORG_ID),
    )

    assert isinstance(result, dict)
    assert result["graph"]["scope"] == "wan"
    get_session.assert_awaited_once_with()
    client_factory.assert_called_once_with(request_session)
