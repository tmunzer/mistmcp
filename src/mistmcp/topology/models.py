"""Validated input and output models for Mist topology workflows."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(word.capitalize() for word in rest)


class OutputModel(BaseModel):
    """Base model that serializes public output fields like the original server."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)


class ResponseFormat(str, Enum):
    """Human- or machine-readable response text format."""

    MARKDOWN = "markdown"
    JSON = "json"


class TopologyNode(OutputModel):
    """A managed device, client, or unresolved physical neighbor."""

    id: str
    kind: Literal[
        "client", "ap", "switch", "gateway", "dhcp_server", "wan", "internet", "unknown"
    ]
    name: str
    site_id: str | None = None
    mac: str | None = None
    ip: str | None = None
    vlan: str | None = None
    subnet: str | None = None
    model: str | None = None
    status: str | None = None
    metadata: dict[str, str | int | float | bool] | None = None


class TopologyEdge(OutputModel):
    """An evidence-backed relationship between two topology nodes."""

    id: str
    source: str
    target: str
    kind: Literal[
        "wireless",
        "ethernet",
        "lldp",
        "routes_via",
        "wan",
        "vpn",
        "serves_dhcp",
        "inferred",
    ]
    confidence: Literal["observed", "reported", "inferred"]
    label: str | None = None
    source_port: str | None = None
    target_port: str | None = None
    vlan: str | None = None
    evidence: str | None = None
    observed_at: str | None = None
    operational_state: Literal["up", "down"] | None = None
    source_stp_state: (
        Literal["blocking", "disabled", "forwarding", "learning", "listening"] | None
    ) = None
    target_stp_state: (
        Literal["blocking", "disabled", "forwarding", "learning", "listening"] | None
    ) = None


class PortDiagnostic(OutputModel):
    """Categorized explanation for unresolved or externally resolved port observations."""

    reason: Literal[
        "missing_lldp_neighbor",
        "incomplete_lldp_identity",
        "unresolved_source_device",
        "ambiguous_neighbor_mac",
        "unmanaged_or_uncorrelated_neighbor",
    ]
    count: int = Field(ge=1)
    explanation: str
    examples: list[str] = Field(default_factory=list, max_length=5)


class TopologyGraph(OutputModel):
    """A conservative site or WAN topology graph with evidence diagnostics."""

    scope: Literal["site", "wan"]
    scope_id: str
    generated_at: str
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]
    warnings: list[str]
    port_diagnostics: list[PortDiagnostic] | None = None
    evidence_summary: dict[str, int] | None = None


class PathResult(OutputModel):
    """A candidate physical chain that never asserts traffic forwarding."""

    found: bool
    path_type: Literal["candidate_physical_topology"] = "candidate_physical_topology"
    forwarding_verified: Literal[False] = False
    source: TopologyNode | None = None
    destination: TopologyNode | None = None
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]
    vlan_relationship: Literal["same", "different", "unknown"]
    explanation: str
    warnings: list[str]


class _ActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class GetSiteTopologyInput(_ActionInput):
    action: Literal["get_site_topology"]
    org_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    include_clients: bool = True
    include_mermaid: bool = False
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class FindPathInput(_ActionInput):
    action: Literal["find_path"]
    org_id: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    include_mermaid: bool = False
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class GetWanTopologyInput(_ActionInput):
    action: Literal["get_wan_topology"]
    org_id: str = Field(min_length=1)
    include_mermaid: bool = False
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


TopologyAction: TypeAlias = Annotated[
    GetSiteTopologyInput | FindPathInput | GetWanTopologyInput,
    Field(discriminator="action"),
]
JsonObject: TypeAlias = dict[str, Any]
