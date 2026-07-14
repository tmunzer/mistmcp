"""Read-only topology workflow tool integrated with MistMCP."""

from __future__ import annotations

import asyncio
import json
from collections import Counter
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, Literal, TypeVar
from uuid import UUID

from fastmcp.exceptions import ToolError
from pydantic import Field, TypeAdapter, ValidationError

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.server import mcp
from mistmcp.topology.client import MistAPIClient, MistApiError, TopologyDataSource
from mistmcp.topology.mermaid import graph_to_mermaid, path_to_mermaid
from mistmcp.topology.models import (
    FindPathInput,
    GetSiteTopologyInput,
    GetWanTopologyInput,
    PathResult,
    ResponseFormat,
    TopologyAction,
    TopologyGraph,
)
from mistmcp.topology.normalize import build_site_graph, build_wan_graph
from mistmcp.topology.path import find_path

TOOL_DESCRIPTION = """Read-only access to Mist topology workflows through one action-based tool.

Actions:
- get_site_topology: build a site graph for org_id and site_id.
- find_path: find a candidate physical adjacency chain for org_id and site_id.
- get_wan_topology: build WAN topology for org_id.

Site topology uses up port/LLDP and STP observations and ignores the Mist `active` field.
WAN topology uses reported VPN peer paths and their latest operational state. Known
non-forwarding STP links are excluded from paths. No result claims VLAN forwarding, routing,
VRFs, policy, reachability, or DHCP configuration.
"""
_ACTION_ADAPTER = TypeAdapter(TopologyAction)
T = TypeVar("T")
ActionName = Annotated[
    Literal["get_site_topology", "find_path", "get_wan_topology"],
    Field(description="Topology workflow to execute."),
]
OrgId = Annotated[
    UUID,
    Field(
        description="Mist organization ID. Resolve it with mist_get_account(information=account_info) first."
    ),
]
SiteId = Annotated[
    UUID | None,
    Field(description="Mist site ID. Required for site topology and path actions."),
]
IncludeClients = Annotated[
    bool | None,
    Field(
        description="For get_site_topology only. Include recent clients; defaults to true."
    ),
]
IncludeMermaid = Annotated[
    bool | None,
    Field(
        description="For topology and path actions. Include Mermaid; defaults to false."
    ),
]
EndpointSelector = Annotated[
    str | None,
    Field(
        description="For find_path only. Exact or unique name, IP, MAC, or Mist ID.",
        min_length=1,
    ),
]


def _graph_text(
    graph: TopologyGraph, response_format: ResponseFormat, mermaid: str | None
) -> str:
    graph_data = graph.model_dump(by_alias=True, exclude_none=True)
    if response_format == ResponseFormat.JSON:
        return json.dumps(
            {**graph_data, **({"mermaid": mermaid} if mermaid else {})}, indent=2
        )
    grouped = Counter(node.kind for node in graph.nodes)
    counts = ", ".join(f"{count} {kind}" for kind, count in grouped.items())
    lines = [
        f"# {'Site topology' if graph.scope == 'site' else 'WAN topology'}",
        "",
        f"{len(graph.nodes)} nodes ({counts}); {len(graph.edges)} links.",
    ]
    if graph.port_diagnostics:
        lines.extend(["", "## Port diagnostics"])
        for diagnostic in graph.port_diagnostics:
            examples = (
                f" Examples: {', '.join(diagnostic.examples)}."
                if diagnostic.examples
                else ""
            )
            lines.append(
                f"- `{diagnostic.reason}`: {diagnostic.count}. {diagnostic.explanation}{examples}"
            )
    if graph.warnings:
        lines.extend(
            ["", "## Caveats", *(f"- {warning}" for warning in graph.warnings)]
        )
    if mermaid:
        lines.extend(["", "```mermaid", mermaid, "```"])
    return "\n".join(lines)


def _path_text(
    path: PathResult, response_format: ResponseFormat, mermaid: str | None
) -> str:
    path_data = path.model_dump(by_alias=True, exclude_none=True)
    if response_format == ResponseFormat.JSON:
        return json.dumps(
            {**path_data, **({"mermaid": mermaid} if mermaid else {})}, indent=2
        )
    lines = [
        "# Candidate physical topology path",
        "",
        path.explanation,
        "",
        "Forwarding verified: no",
        f"VLAN relationship: {path.vlan_relationship}",
    ]
    if path.edges:
        lines.extend(["", "## Adjacencies"])
        for index, edge in enumerate(path.edges):
            states = [
                state
                for state in (edge.source_stp_state, edge.target_stp_state)
                if state
            ]
            stp = f", STP {'/'.join(states)}" if states else ""
            lines.append(
                f"{index + 1}. {path.nodes[index].name} → {path.nodes[index + 1].name} "
                f"({edge.kind}, {edge.confidence}{stp})"
            )
    if path.warnings:
        lines.extend(["", "## Caveats", *(f"- {warning}" for warning in path.warnings)])
    if mermaid:
        lines.extend(["", "```mermaid", mermaid, "```"])
    return "\n".join(lines)


async def _optional(
    load: Callable[[], Awaitable[T]], warning: str, fallback: T, warnings: list[str]
) -> T:
    try:
        return await load()
    except MistApiError as error:
        if error.status not in {403, 404}:
            raise
        warnings.append(warning)
        return fallback


async def collect_site_graph(
    client: TopologyDataSource,
    org_id: str,
    site_id: str,
    *,
    include_clients: bool = True,
) -> TopologyGraph:
    """Collect recent Mist telemetry and normalize it into one site graph."""
    warnings = [
        "DHCP server enrichment is unavailable until a documented per-device DHCP "
        "configuration collector is implemented."
    ]
    device_stats, wireless_clients, wired_clients, ports = await asyncio.gather(
        client.site_devices(site_id),
        _optional(
            lambda: client.site_clients(site_id),
            "Wireless-client statistics are unavailable for this site.",
            [],
            warnings,
        )
        if include_clients
        else asyncio.sleep(0, result=[]),
        _optional(
            lambda: client.site_wired_clients(site_id),
            "Wired-client search is unavailable for this site.",
            [],
            warnings,
        )
        if include_clients
        else asyncio.sleep(0, result=[]),
        _optional(
            lambda: client.site_ports(site_id),
            "Switch/gateway port-search telemetry is unavailable; infrastructure links may be incomplete.",
            [],
            warnings,
        ),
    )
    device_inventory = await _optional(
        lambda: client.org_site_inventory(org_id, site_id),
        "Organization inventory is unavailable; virtual-chassis MAC correlation may be incomplete.",
        [],
        warnings,
    )
    clients = [
        *({**record, "_topology_source": "wireless"} for record in wireless_clients),
        *({**record, "_topology_source": "wired"} for record in wired_clients),
    ]
    return build_site_graph(
        site_id, device_stats, clients, warnings, ports, device_inventory
    )


def _validation_message(action: str, error: ValidationError) -> ValueError:
    details = "; ".join(
        f"{'.'.join(str(part) for part in item['loc'][1:]) or 'input'}: {item['msg']}"
        for item in error.errors()
    )
    return ValueError(f"Invalid parameters for action '{action}': {details}")


async def _run_topology_action(
    data_source: TopologyDataSource,
    *,
    action: str,
    org_id: str,
    site_id: str | None = None,
    include_clients: bool | None = None,
    include_mermaid: bool | None = None,
    source: str | None = None,
    destination: str | None = None,
    response_format: str = "json",
) -> dict[str, Any] | str:
    """Validate and execute a topology action against a supplied data source."""
    model_response_format = (
        ResponseFormat.MARKDOWN if response_format == "string" else ResponseFormat.JSON
    )
    raw: dict[str, Any] = {
        "action": action,
        "org_id": org_id,
        **({"site_id": site_id} if site_id is not None else {}),
        **({"include_clients": include_clients} if include_clients is not None else {}),
        **({"include_mermaid": include_mermaid} if include_mermaid is not None else {}),
        **({"source": source} if source is not None else {}),
        **({"destination": destination} if destination is not None else {}),
    }
    raw["response_format"] = model_response_format

    try:
        params = _ACTION_ADAPTER.validate_python(raw)
    except ValidationError as error:
        raise _validation_message(action, error) from error

    if isinstance(params, GetSiteTopologyInput):
        graph = await collect_site_graph(
            data_source,
            params.org_id,
            params.site_id,
            include_clients=params.include_clients,
        )
        mermaid = graph_to_mermaid(graph) if params.include_mermaid else None
        output = {
            "graph": graph.model_dump(by_alias=True, exclude_none=True),
            **({"mermaid": mermaid} if mermaid else {}),
        }
        return (
            _graph_text(graph, params.response_format, mermaid)
            if response_format == "string"
            else output
        )

    if isinstance(params, FindPathInput):
        graph = await collect_site_graph(data_source, params.org_id, params.site_id)
        path = find_path(graph, params.source, params.destination)
        mermaid = (
            path_to_mermaid(path) if params.include_mermaid and path.found else None
        )
        output = {
            "path": path.model_dump(by_alias=True, exclude_none=True),
            **({"mermaid": mermaid} if mermaid else {}),
        }
        return (
            _path_text(path, params.response_format, mermaid)
            if response_format == "string"
            else output
        )

    if isinstance(params, GetWanTopologyInput):
        wan_warnings: list[str] = []
        sites, devices, vpn_peers = await asyncio.gather(
            data_source.org_sites(params.org_id),
            data_source.org_gateway_inventory(params.org_id),
            _optional(
                lambda: data_source.org_vpn_peers(params.org_id),
                "Organization VPN peer-path statistics are unavailable; WAN overlay "
                "relationships could not be collected.",
                [],
                wan_warnings,
            ),
        )
        graph = build_wan_graph(
            params.org_id,
            sites,
            devices,
            vpn_peers,
            wan_warnings,
        )
        mermaid = graph_to_mermaid(graph) if params.include_mermaid else None
        output = {
            "graph": graph.model_dump(by_alias=True, exclude_none=True),
            **({"mermaid": mermaid} if mermaid else {}),
        }
        return (
            _graph_text(graph, params.response_format, mermaid)
            if response_format == "string"
            else output
        )

    raise ValueError(f"Unsupported topology action: {action}")


@mcp.tool(
    name="mist_topology",
    description=TOOL_DESCRIPTION,
    tags={"topology"},
    annotations={
        "title": "Query Mist Network Topology",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def mist_topology(
    action: ActionName,
    org_id: OrgId,
    site_id: SiteId = None,
    include_clients: IncludeClients = None,
    include_mermaid: IncludeMermaid = None,
    source: EndpointSelector = None,
    destination: EndpointSelector = None,
) -> dict[str, Any] | str:
    """Run one strictly validated, read-only Mist topology action."""
    logger.debug("Tool mist_topology called with action=%s", action)
    apisession, response_format = await get_apisession()
    try:
        return await _run_topology_action(
            MistAPIClient(apisession),
            action=action,
            org_id=str(org_id),
            site_id=str(site_id) if site_id else None,
            include_clients=include_clients,
            include_mermaid=include_mermaid,
            source=source,
            destination=destination,
            response_format=response_format,
        )
    except MistApiError as error:
        raise ToolError(
            {
                "status_code": error.status or 503,
                "message": str(error),
            }
        ) from error
    except ValueError as error:
        raise ToolError({"status_code": 400, "message": str(error)}) from error
