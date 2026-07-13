"""Tests for the composable mistapi-backed data source."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

import pytest

from mistmcp.topology.client import MistAPIClient, MistApiError

if TYPE_CHECKING:
    import mistapi


@dataclass
class FakeResponse:
    data: dict[str, Any] | list[Any]
    next: str | None = None
    status_code: int | None = 200
    url: str = "https://api.example/request"


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = iter(responses)
        self.requests: list[tuple[str, dict[str, str] | None]] = []

    def mist_get(self, uri: str, query: dict[str, str] | None = None) -> FakeResponse:
        self.requests.append((uri, query))
        return next(self.responses)


def client_for(session: FakeSession) -> MistAPIClient:
    return MistAPIClient(cast("mistapi.APISession", session))


@pytest.mark.asyncio
async def test_follows_mistapi_next_pagination() -> None:
    session = FakeSession(
        [
            FakeResponse(
                {"results": [{"mac": "aa"}], "total": 2},
                next="/api/v1/sites/site-1/stats/ports/search?search_after=cursor-2",
            ),
            FakeResponse({"results": [{"mac": "bb"}], "total": 2}),
        ]
    )

    ports = await client_for(session).site_ports("site-1")

    assert [port["mac"] for port in ports] == ["aa", "bb"]
    assert session.requests == [
        (
            "/api/v1/sites/site-1/stats/ports/search",
            {"device_type": "all", "limit": "1000", "sort": "-timestamp"},
        ),
        (
            "/api/v1/sites/site-1/stats/ports/search?search_after=cursor-2",
            None,
        ),
    ]


@pytest.mark.asyncio
async def test_paginates_gateway_inventory_through_mistapi() -> None:
    session = FakeSession(
        [
            FakeResponse(
                [{"id": "gateway-1"}],
                next="/api/v1/orgs/org-1/inventory?type=gateway&page=2",
            ),
            FakeResponse([{"id": "gateway-2"}]),
        ]
    )

    devices = await client_for(session).org_gateway_inventory("org-1")

    assert [device["id"] for device in devices] == ["gateway-1", "gateway-2"]
    assert session.requests[0] == (
        "/api/v1/orgs/org-1/inventory",
        {"type": "gateway", "limit": "1000"},
    )
    assert session.requests[1][0].endswith("page=2")


@pytest.mark.asyncio
async def test_collects_recent_org_vpn_peer_paths() -> None:
    session = FakeSession(
        [
            FakeResponse(
                {
                    "results": [
                        {
                            "mac": "cc0000000001",
                            "peer_mac": "cc0000000002",
                            "up": True,
                        }
                    ]
                }
            )
        ]
    )

    peers = await client_for(session).org_vpn_peers("org-1")

    assert len(peers) == 1
    assert session.requests == [
        (
            "/api/v1/orgs/org-1/stats/vpn_peers/search",
            {
                "limit": "1000",
                "duration": "1d",
                "sort": "-last_seen",
            },
        )
    ]


@pytest.mark.asyncio
async def test_filters_site_inventory_for_alias_enrichment() -> None:
    session = FakeSession([FakeResponse([{"id": "switch-1", "type": "switch"}])])

    devices = await client_for(session).org_site_inventory("org-1", "site-1")

    assert len(devices) == 1
    assert session.requests == [
        (
            "/api/v1/orgs/org-1/inventory",
            {"site_id": "site-1", "vc": "True", "limit": "1000"},
        )
    ]


@pytest.mark.asyncio
async def test_reports_http_and_repeated_cursor_errors() -> None:
    denied = FakeSession([FakeResponse({"error": "denied"}, status_code=403)])
    with pytest.raises(MistApiError, match="read access"):
        await client_for(denied).list_sites("org-1")

    repeated = "/api/v1/search?search_after=repeated"
    looping = FakeSession(
        [
            FakeResponse({"results": []}, next=repeated),
            FakeResponse({"results": []}, next=repeated),
        ]
    )
    with pytest.raises(MistApiError, match="repeated pagination cursor"):
        await client_for(looping).site_ports("site-1")
