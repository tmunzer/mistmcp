"""Composable, asynchronous adapter around the public ``mistapi`` package."""

from __future__ import annotations

from typing import Any, Protocol, cast

import mistapi
from mistapi.api.v1.orgs import inventory as org_inventory_api
from mistapi.api.v1.orgs import sites as org_sites_api
from mistapi.api.v1.orgs import stats as org_stats_api
from mistapi.api.v1.sites import stats as site_stats_api
from mistapi.api.v1.sites import wired_clients as wired_clients_api

from mistmcp.topology.models import JsonObject

PAGE_SIZE = 1_000
MAX_ITEMS = 10_000
HTTP_ERROR_STATUS = 400


class MistApiError(RuntimeError):
    """A safe, actionable error returned by the Mist API adapter."""

    def __init__(
        self, message: str, status: int | None = None, path: str | None = None
    ) -> None:
        super().__init__(message)
        self.status = status
        self.path = path


class TopologyDataSource(Protocol):
    """Minimal data-source contract required by the topology tool.

    An existing Mist MCP server may implement this protocol instead of using
    :class:`MistAPIClient` directly.
    """

    async def list_sites(self, org_id: str) -> list[JsonObject]: ...

    async def site_devices(self, site_id: str) -> list[JsonObject]: ...

    async def site_clients(self, site_id: str) -> list[JsonObject]: ...

    async def org_gateway_inventory(self, org_id: str) -> list[JsonObject]: ...

    async def org_site_inventory(
        self, org_id: str, site_id: str
    ) -> list[JsonObject]: ...

    async def org_sites(self, org_id: str) -> list[JsonObject]: ...

    async def org_vpn_peers(self, org_id: str) -> list[JsonObject]: ...

    async def site_ports(self, site_id: str) -> list[JsonObject]: ...

    async def site_wired_clients(self, site_id: str) -> list[JsonObject]: ...


class _APIResponse(Protocol):
    data: dict[str, Any] | list[Any]
    next: str | None
    status_code: int | None
    url: str


class APICall(Protocol):
    __name__: str

    def __call__(self, *args: Any, **kwargs: Any) -> _APIResponse: ...


class MistAPIClient:
    """Read-only topology data source backed by a reusable ``mistapi.APISession``.

    The host server owns authentication and supplies a request-scoped session.
    """

    def __init__(
        self,
        session: mistapi.APISession,
        *,
        max_items: int = MAX_ITEMS,
    ) -> None:
        self._session = session
        self._max_items = max_items

    @property
    def session(self) -> mistapi.APISession:
        """Return the request-scoped Mist API session."""
        return self._session

    async def list_sites(self, org_id: str) -> list[JsonObject]:
        return await self._collect(org_sites_api.listOrgSites, org_id, limit=PAGE_SIZE)

    async def site_devices(self, site_id: str) -> list[JsonObject]:
        return await self._collect(
            site_stats_api.listSiteDevicesStats,
            site_id,
            type="all",
            limit=PAGE_SIZE,
        )

    async def site_clients(self, site_id: str) -> list[JsonObject]:
        return await self._collect(
            site_stats_api.listSiteWirelessClientsStats,
            site_id,
            duration="10m",
            limit=PAGE_SIZE,
        )

    async def org_gateway_inventory(self, org_id: str) -> list[JsonObject]:
        return await self._collect(
            org_inventory_api.getOrgInventory,
            org_id,
            type="gateway",
            limit=PAGE_SIZE,
        )

    async def org_site_inventory(self, org_id: str, site_id: str) -> list[JsonObject]:
        return await self._collect(
            org_inventory_api.getOrgInventory,
            org_id,
            site_id=site_id,
            vc=True,
            limit=PAGE_SIZE,
        )

    async def org_sites(self, org_id: str) -> list[JsonObject]:
        return await self.list_sites(org_id)

    async def org_vpn_peers(self, org_id: str) -> list[JsonObject]:
        return await self._collect(
            org_stats_api.searchOrgPeerPathStats,
            org_id,
            duration="1d",
            sort="-last_seen",
            limit=PAGE_SIZE,
        )

    async def site_ports(self, site_id: str) -> list[JsonObject]:
        return await self._collect(
            site_stats_api.searchSiteSwOrGwPorts,
            site_id,
            device_type="all",
            sort="-timestamp",
            limit=PAGE_SIZE,
        )

    async def site_wired_clients(self, site_id: str) -> list[JsonObject]:
        return await self._collect(
            wired_clients_api.searchSiteWiredClients,
            site_id,
            duration="10m",
            sort="-timestamp",
            limit=PAGE_SIZE,
        )

    async def _collect(
        self, endpoint: APICall, *args: Any, **kwargs: Any
    ) -> list[JsonObject]:
        try:
            response = cast(
                "_APIResponse",
                await mistapi.arun(endpoint, self._session, *args, **kwargs),
            )
            items: list[JsonObject] = []
            seen_next: set[str] = set()
            while True:
                _raise_for_response(response, endpoint.__name__)
                batch = _response_items(response.data)
                if len(items) + len(batch) > self._max_items:
                    raise MistApiError(
                        f"Mist API operation {endpoint.__name__} exceeded the "
                        f"{self._max_items}-record safety limit. Narrow the scope or time window.",
                        path=response.url,
                    )
                items.extend(batch)
                next_page = response.next
                if not next_page:
                    return items
                if next_page in seen_next:
                    raise MistApiError(
                        f"Mist API operation {endpoint.__name__} returned a repeated pagination cursor.",
                        path=response.url,
                    )
                seen_next.add(next_page)
                next_response = await mistapi.arun(
                    mistapi.get_next, self._session, response
                )
                if next_response is None:
                    return items
                response = cast("_APIResponse", next_response)
        except MistApiError:
            raise
        except Exception as error:
            raise MistApiError(
                f"Mist API operation {endpoint.__name__} failed. Check connectivity and credentials."
            ) from error


def _raise_for_response(response: _APIResponse, operation: str) -> None:
    status = response.status_code
    has_error = isinstance(response.data, dict) and bool(response.data.get("error"))
    if (status is None or status < HTTP_ERROR_STATUS) and not has_error:
        return
    hint = {
        401: " Check the mistapi session credentials.",
        403: " The session needs read access to this organization or site.",
        404: " Check the organization or site identifier.",
        429: " Mist rate-limited the request; retry later.",
    }.get(status, "")
    raise MistApiError(
        f"Mist API operation {operation} returned HTTP {status or 'error'}.{hint}",
        status=status,
        path=response.url,
    )


def _response_items(data: dict[str, Any] | list[Any]) -> list[JsonObject]:
    values = data if isinstance(data, list) else data.get("results", [])
    return [cast("JsonObject", item) for item in values if isinstance(item, dict)]
