"""Behavioral parity tests for topology normalization and path finding."""

from __future__ import annotations

import json
import re

import pytest

from mistmcp.topology.mermaid import graph_to_mermaid, path_to_mermaid
from mistmcp.topology.models import JsonObject, TopologyEdge, TopologyGraph
from mistmcp.topology.normalize import build_site_graph, build_wan_graph
from mistmcp.topology.path import find_path, resolve_node


def _edge_with_port(graph: TopologyGraph, port: str) -> TopologyEdge:
    return next(edge for edge in graph.edges if edge.source_port == port)


def _summary(graph: TopologyGraph) -> dict[str, int]:
    assert graph.evidence_summary is not None
    return graph.evidence_summary


def test_normalizes_devices_clients_and_lldp(
    devices: list[JsonObject],
    clients: list[JsonObject],
    infrastructure_ports: list[JsonObject],
) -> None:
    graph = build_site_graph("site-1", devices, clients, [], infrastructure_ports)
    assert len(graph.nodes) == 5
    assert any(
        edge.kind == "lldp" and edge.confidence == "observed" for edge in graph.edges
    )
    assert not any(node.kind == "dhcp_server" for node in graph.nodes)
    assert graph_to_mermaid(graph).startswith("flowchart LR")


def test_uses_port_search_as_observed_evidence(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "neighbor_system_name": "Site Gateway",
                "neighbor_port_desc": "ge-0/0/1",
                "up": True,
            }
        ],
    )
    edge = _edge_with_port(graph, "ge-0/0/47")
    assert edge.kind == "lldp"
    assert edge.confidence == "observed"
    assert edge.target_port == "ge-0/0/1"
    assert edge.evidence == "Mist port-search telemetry (up=true)"
    assert edge.operational_state == "up"


def test_categorizes_unresolved_and_external_port_neighbors() -> None:
    graph = build_site_graph(
        "site-1",
        [
            {"id": "sw-source", "type": "switch", "mac": "bb0000000001"},
            {"id": "ap-one", "type": "ap", "mac": "dd0000000001"},
            {"id": "ap-two", "type": "ap", "mac": "dd0000000001"},
        ],
        [],
        ports=[
            {"mac": "bb0000000001", "port_id": "missing", "up": True},
            {
                "mac": "bb0000000001",
                "port_id": "incomplete",
                "neighbor_mac": "invalid",
                "neighbor_system_name": "Partial LLDP neighbor",
                "up": True,
            },
            {
                "mac": "cc0000000001",
                "port_id": "unknown-source",
                "neighbor_mac": "ee0000000001",
                "up": True,
            },
            {
                "mac": "bb0000000001",
                "port_id": "ambiguous",
                "neighbor_mac": "dd0000000001",
                "up": True,
            },
            {
                "mac": "bb0000000001",
                "port_id": "unmanaged",
                "neighbor_mac": "ee0000000001",
                "neighbor_system_name": "Third-party switch",
                "up": True,
            },
        ],
    )

    assert graph.port_diagnostics is not None
    diagnostics = {item.reason: item for item in graph.port_diagnostics}
    assert set(diagnostics) == {
        "missing_lldp_neighbor",
        "incomplete_lldp_identity",
        "unresolved_source_device",
        "ambiguous_neighbor_mac",
        "unmanaged_or_uncorrelated_neighbor",
    }
    assert all(item.count == 1 for item in diagnostics.values())
    assert diagnostics["missing_lldp_neighbor"].examples == [
        "bb:00:00:00:00:01|missing"
    ]
    assert any(
        node.kind == "unknown" and node.name == "Third-party switch"
        for node in graph.nodes
    )
    summary = _summary(graph)
    assert summary["missingLldpNeighborPorts"] == 1
    assert summary["incompleteLldpIdentityPorts"] == 1
    assert summary["unresolvedSourceDevicePorts"] == 1
    assert summary["ambiguousNeighborPorts"] == 1
    assert summary["unmanagedOrUncorrelatedNeighborPorts"] == 1
    assert "portDiagnostics" in graph.model_dump(by_alias=True, exclude_none=True)


def test_suppresses_known_virtual_mac_aliases_from_site_output() -> None:
    graph = build_site_graph(
        "site-1",
        [
            {"id": "sw-source", "type": "switch", "mac": "bb0000000001"},
            {"id": "gw-virtual-a", "type": "gateway", "mac": "02:00:00:00:00:0a"},
            {"id": "gw-virtual-b", "type": "gateway", "mac": "02:00:00:00:00:0a"},
        ],
        [{"id": "client-virtual", "mac": "00:00:00:00:00:14"}],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "virtual-neighbor",
                "neighbor_mac": "00:00:00:00:00:14",
                "up": True,
            },
            {
                "mac": "02:00:00:00:00:0a",
                "port_id": "virtual-source",
                "neighbor_mac": "ee0000000001",
                "up": True,
            },
        ],
        inventory_aliases=[
            {"id": "sw-source", "mac": "02:00:00:00:00:0a"},
        ],
    )

    serialized = json.dumps(graph.model_dump(by_alias=True, exclude_none=True)).lower()
    assert "02:00:00:00:00:0a" not in serialized
    assert "00:00:00:00:00:14" not in serialized
    assert all(node.mac is None for node in graph.nodes if "virtual" in node.id)
    assert not any("multiple managed devices" in warning for warning in graph.warnings)
    assert graph.port_diagnostics is not None
    assert any(
        item.reason == "incomplete_lldp_identity" for item in graph.port_diagnostics
    )


def test_preserves_parallel_links(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "neighbor_port_desc": "ge-0/0/1",
                "up": True,
            },
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/48",
                "neighbor_mac": "cc0000000001",
                "neighbor_port_desc": "ge-0/0/2",
                "up": True,
            },
        ],
    )
    assert len(graph.edges) == 2
    assert graph.edges[0].id != graph.edges[1].id


def test_normalizes_nested_wired_attachment(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "100000000004",
                "dhcp_hostname": "Printer",
                "vlan": "30",
                "device_mac_port": [
                    {
                        "device_mac": "bb0000000001",
                        "port_id": "ge-0/0/9",
                        "ip": "10.30.0.4",
                        "vlan": "30",
                    }
                ],
            }
        ],
    )
    printer = resolve_node(graph, "Printer")
    edge = next(edge for edge in graph.edges if edge.source == printer.id)
    assert printer.ip == "10.30.0.4"
    assert printer.vlan == "30"
    assert printer.status == "recently_reported"
    assert edge.kind == "ethernet"
    assert edge.target_port == "ge-0/0/9"


def test_managed_device_is_not_reclassified_as_client(
    devices: list[JsonObject], infrastructure_ports: list[JsonObject]
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "aa0000000001",
                "dhcp_hostname": "Misleading name",
                "ip": "192.0.2.20",
                "device_mac_port": [
                    {"device_mac": "bb0000000001", "port_id": "ge-0/0/10"}
                ],
            }
        ],
        ports=infrastructure_ports,
    )
    aps = [node for node in graph.nodes if node.mac == "aa:00:00:00:00:01"]
    assert len(aps) == 1
    assert aps[0].kind == "ap"
    assert aps[0].name == "Lobby AP"
    assert aps[0].ip is None
    assert not any(
        edge.source == aps[0].id and edge.kind == "ethernet" for edge in graph.edges
    )


def test_never_uses_client_as_transit(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        [
            *devices,
            {
                "id": "sw-2",
                "type": "switch",
                "name": "Edge Switch",
                "mac": "dd0000000001",
            },
        ],
        [
            {
                "mac": "2093390b3580",
                "hostname": "Learned MAC",
                "switch_mac": "bb0000000001",
                "wired": True,
            }
        ],
        ports=[
            {
                "mac": "dd0000000001",
                "port_id": "ge-0/0/1",
                "neighbor_mac": "2093390b3580",
                "up": True,
            }
        ],
    )
    path = find_path(graph, "Core Switch", "Edge Switch")
    assert path.found is False
    assert path.nodes == []


def test_finds_client_path_and_flags_inter_vlan(
    devices: list[JsonObject],
    clients: list[JsonObject],
    infrastructure_ports: list[JsonObject],
) -> None:
    graph = build_site_graph("site-1", devices, clients, ports=infrastructure_ports)
    path = find_path(graph, "Alice Laptop", "10.20.20.20")
    assert path.found is True
    assert path.vlan_relationship == "different"
    assert path.forwarding_verified is False
    assert [node.name for node in path.nodes] == [
        "Alice Laptop",
        "Lobby AP",
        "Core Switch",
        "Build Server",
    ]
    assert any("not a routed path" in warning for warning in path.warnings)
    assert re.search(r"observed|reported", path_to_mermaid(path))


def test_rejects_ambiguous_endpoint_names(
    devices: list[JsonObject], clients: list[JsonObject]
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            *clients,
            {
                "mac": "10:00:00:00:00:03",
                "hostname": "Alice Phone",
                "ap_mac": "aa:00:00:00:00:01",
            },
        ],
    )
    with pytest.raises(ValueError, match="matches 2 nodes"):
        resolve_node(graph, "Alice")


def test_wan_graph_ignores_generic_inventory_peers_and_preserves_conflicts() -> None:
    graph = build_wan_graph(
        "org-1",
        [{"id": "site-1", "name": "Paris"}, {"id": "site-2", "name": "Lyon"}],
        [
            {
                "id": "gw-1",
                "type": "gateway",
                "name": "Gateway A",
                "site_id": "site-1",
                "mac": "cc0000000001",
                "connected": True,
                "vpn_peers": [{"device_id": "gw-2"}],
            },
            {
                "id": "gw-1",
                "type": "gateway",
                "name": "Gateway B",
                "site_id": "site-2",
                "mac": "cc0000000002",
                "connected": False,
            },
        ],
    )
    assert len(graph.nodes) == 1
    assert graph.edges == []
    assert graph.nodes[0].name == "gw-1"
    assert graph.nodes[0].mac is None
    assert graph.nodes[0].site_id is None
    assert graph.nodes[0].status is None
    assert any(
        "peer-path search returned no records" in warning for warning in graph.warnings
    )
    assert any("Conflicting site values" in warning for warning in graph.warnings)


def test_wan_graph_accepts_rows_without_connected_status() -> None:
    graph = build_wan_graph(
        "org-1",
        [{"id": "site-1", "name": "Paris"}],
        [
            {
                "id": "gw-1",
                "type": "gateway",
                "name": "Paris GW",
                "site_id": "site-1",
                "vpn_peers": [{"device_id": "gw-2", "status": "up"}],
            }
        ],
    )
    assert len(graph.nodes) == 1
    assert graph.nodes[0].status is None
    assert graph.edges == []


def test_wan_graph_builds_and_deduplicates_observed_vpn_peer_paths() -> None:
    graph = build_wan_graph(
        "org-1",
        [{"id": "site-1", "name": "Paris"}, {"id": "site-2", "name": "Lyon"}],
        [
            {
                "id": "gw-1",
                "type": "gateway",
                "name": "Paris GW",
                "site_id": "site-1",
                "mac": "cc0000000001",
            },
            {
                "id": "gw-2",
                "type": "gateway",
                "name": "Lyon GW",
                "site_id": "site-2",
                "mac": "cc0000000002",
            },
        ],
        [
            {
                "mac": "cc0000000001",
                "peer_mac": "cc0000000002",
                "site_id": "site-1",
                "peer_site_id": "site-2",
                "router_name": "Paris GW",
                "peer_router_name": "Lyon GW",
                "port_id": "ge-0/0/0",
                "peer_port_id": "ge-0/0/1",
                "type": "ipsec",
                "up": True,
                "last_seen": 1_700_000_000,
            },
            {
                "mac": "cc0000000002",
                "peer_mac": "cc0000000001",
                "site_id": "site-2",
                "peer_site_id": "site-1",
                "router_name": "Lyon GW",
                "peer_router_name": "Paris GW",
                "port_id": "ge-0/0/1",
                "peer_port_id": "ge-0/0/0",
                "type": "ipsec",
                "up": True,
                "last_seen": 1_700_000_000,
            },
        ],
    )

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    edge = graph.edges[0]
    assert edge.source == "gateway:gw-1"
    assert edge.target == "gateway:gw-2"
    assert edge.kind == "vpn"
    assert edge.confidence == "observed"
    assert edge.operational_state == "up"
    assert edge.label == "ipsec · up"
    assert edge.observed_at == "2023-11-14T22:13:20.000Z"
    assert graph.evidence_summary is not None
    assert graph.evidence_summary["vpnPeerRecordsCollected"] == 2
    assert graph.evidence_summary["vpnPeerPaths"] == 1


def test_wan_graph_keeps_down_paths_and_creates_explicit_stats_nodes() -> None:
    graph = build_wan_graph(
        "org-1",
        [{"id": "site-1", "name": "Paris"}, {"id": "site-2", "name": "Lyon"}],
        [],
        [
            {
                "mac": "cc0000000001",
                "peer_mac": "cc0000000002",
                "site_id": "site-1",
                "peer_site_id": "site-2",
                "router_name": "Paris GW",
                "peer_router_name": "Lyon GW",
                "type": "svr",
                "up": False,
                "last_seen": 1_700_000_000,
            }
        ],
    )

    assert {node.name for node in graph.nodes} == {"Paris GW", "Lyon GW"}
    assert graph.edges[0].operational_state == "down"
    assert any("currently reported down" in warning for warning in graph.warnings)


def test_wan_graph_suppresses_known_virtual_mac_aliases() -> None:
    graph = build_wan_graph(
        "org-1",
        [{"id": "site-1", "name": "Paris"}],
        [
            {
                "id": "gw-1",
                "type": "gateway",
                "site_id": "site-1",
                "mac": "02:00:00:00:00:0a",
            },
            {
                "id": "gw-2",
                "type": "gateway",
                "site_id": "site-1",
                "mac": "00:00:00:00:00:14",
            },
        ],
        [
            {
                "mac": "02:00:00:00:00:0a",
                "peer_mac": "00:00:00:00:00:14",
                "up": True,
            }
        ],
    )

    serialized = json.dumps(graph.model_dump(by_alias=True, exclude_none=True)).lower()
    assert "02:00:00:00:00:0a" not in serialized
    assert "00:00:00:00:00:14" not in serialized
    assert graph.edges == []
    assert all(node.mac is None for node in graph.nodes)
    assert graph.evidence_summary is not None
    assert graph.evidence_summary["malformedVpnPeerRecords"] == 1


def test_selects_newest_wired_attachment(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "100000000005",
                "dhcp_hostname": "Camera",
                "timestamp": 200,
                "device_mac_port": [
                    {"device_mac": "cc0000000001", "port_id": "old", "when": "100"},
                    {"device_mac": "bb0000000001", "port_id": "new", "when": "200"},
                ],
            }
        ],
    )
    camera = resolve_node(graph, "Camera")
    edge = next(edge for edge in graph.edges if edge.source == camera.id)
    assert edge.target == resolve_node(graph, "Core Switch").id
    assert edge.target_port == "new"
    assert camera.status == "recently_reported"


def test_ignores_active_and_omits_down_and_malformed(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "neighbor_mac": "cc0000000001",
                "port_id": "down",
                "up": False,
            },
            {
                "mac": "bb0000000001",
                "neighbor_mac": "cc0000000001",
                "port_id": "active-is-ignored",
                "up": True,
                "active": False,
                "stp_state": "forwarding",
            },
            {
                "mac": "bb0000000001",
                "neighbor_mac": "not-a-mac",
                "port_id": "invalid",
                "up": True,
            },
        ],
    )
    assert len(graph.edges) == 1
    assert graph.edges[0].source_port == "active-is-ignored"
    assert graph.edges[0].source_stp_state == "forwarding"
    assert _summary(graph)["downPorts"] == 1


def test_stp_blocked_link_is_visible_but_not_routable(
    devices: list[JsonObject],
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": True,
                "stp_state": "blocking",
            }
        ],
    )
    assert graph.edges[0].source_stp_state == "blocking"
    assert _summary(graph)["nonForwardingStpEdges"] == 1
    assert find_path(graph, "Core Switch", "Site Gateway").found is False
    assert "STP blocking" in graph_to_mermaid(graph)


def test_unsupported_stp_state_is_omitted(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": True,
                "stp_state": "unknown-new-state",
            }
        ],
    )
    assert graph.edges == []
    assert _summary(graph)["invalidStpStatePorts"] == 1


def test_ambiguous_attachment_omits_attachment_ip_and_vlan(
    devices: list[JsonObject],
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "100000000006",
                "hostname": "Ambiguous Client",
                "device_mac_port": [
                    {
                        "device_mac": "bb0000000001",
                        "port_id": "one",
                        "ip": "10.1.0.6",
                        "vlan": "10",
                    },
                    {
                        "device_mac": "cc0000000001",
                        "port_id": "two",
                        "ip": "10.2.0.6",
                        "vlan": "20",
                    },
                ],
            }
        ],
    )
    client = resolve_node(graph, "Ambiguous Client")
    assert client.ip is None
    assert client.vlan is None
    assert not any(edge.source == client.id for edge in graph.edges)
    assert any("Conflicting or untimestamped" in warning for warning in graph.warnings)


def test_attachment_keeps_ip_and_vlan_coherent(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "100000000007",
                "hostname": "Coherent Client",
                "ip": "192.0.2.7",
                "vlan": "999",
                "device_mac_port": [
                    {
                        "device_mac": "bb0000000001",
                        "port_id": "ge-0/0/7",
                        "ip": "10.7.0.7",
                        "vlan": "70",
                        "when": 100,
                    }
                ],
            }
        ],
    )
    client = resolve_node(graph, "Coherent Client")
    edge = next(edge for edge in graph.edges if edge.source == client.id)
    assert (client.ip, client.vlan, edge.vlan, edge.target_port) == (
        "10.7.0.7",
        "70",
        "70",
        "ge-0/0/7",
    )


def test_virtual_chassis_aliases_are_collapsed(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        [
            *devices,
            {
                "id": "vc-1",
                "type": "switch",
                "name": "Virtual Chassis",
                "mac": "dd0000000001",
                "vc_mac": "dd00000000ff",
            },
        ],
        [],
        ports=[
            {
                "mac": "dd00000000ff",
                "port_id": "xe-0/0/0",
                "neighbor_mac": "cc0000000001",
                "up": True,
            }
        ],
    )
    vc = resolve_node(graph, "Virtual Chassis")
    assert sum(node.name == "Virtual Chassis" for node in graph.nodes) == 1
    assert any(edge.source == vc.id and edge.kind == "lldp" for edge in graph.edges)


def test_inventory_enriches_but_does_not_create_devices(
    devices: list[JsonObject],
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb00000000ff",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": True,
            }
        ],
        inventory_aliases=[
            {
                "id": "different-inventory-id",
                "type": "switch",
                "name": "Stale inventory name",
                "mac": "bb0000000001",
                "chassis_mac": "bb00000000ff",
            }
        ],
    )
    edge = _edge_with_port(graph, "ge-0/0/47")
    assert edge.source == resolve_node(graph, "Core Switch").id
    assert not any(node.name == "Stale inventory name" for node in graph.nodes)


def test_ambiguous_interface_mac_is_not_correlated(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_mac": "ee0000000001",
                "port_id": "ge-0/0/1",
                "up": True,
            },
            {
                "mac": "cc0000000001",
                "port_mac": "ee0000000001",
                "port_id": "ge-0/0/1",
                "up": True,
            },
            {
                "mac": "aa0000000001",
                "port_id": "eth0",
                "neighbor_mac": "ee0000000001",
                "up": True,
            },
        ],
    )
    assert _summary(graph)["ambiguousPortMacAliases"] == 1
    assert not any(node.mac == "ee:00:00:00:00:01" for node in graph.nodes)
    assert not any(edge.source_port == "eth0" for edge in graph.edges)


def test_fresh_down_observation_suppresses_old_up(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": True,
                "timestamp": 100,
            },
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": False,
                "timestamp": 200,
            },
        ],
    )
    assert not any(edge.source_port == "ge-0/0/47" for edge in graph.edges)


def test_unknown_freshness_conflict_omits_port(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": True,
            },
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "aa0000000001",
                "up": True,
            },
        ],
    )
    assert not any(edge.source_port == "ge-0/0/47" for edge in graph.edges)
    assert any("this port was omitted" in warning for warning in graph.warnings)


def test_descriptive_conflict_retains_adjacency(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "neighbor_port_desc": "ge-0/0/1",
                "neighbor_system_name": "Gateway A",
                "up": True,
            },
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "neighbor_port_desc": "ge-0/0/2",
                "neighbor_system_name": "Gateway B",
                "up": True,
            },
        ],
    )
    edge = _edge_with_port(graph, "ge-0/0/47")
    assert edge.kind == "lldp"
    assert edge.target_port is None
    assert edge.label is None
    assert _summary(graph)["portMetadataConflicts"] == 1


def test_reciprocal_lldp_is_deduplicated_with_both_stp_states(
    devices: list[JsonObject],
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "neighbor_port_desc": "ge-0/0/1",
                "up": True,
                "stp_state": "forwarding",
                "timestamp": 100,
            },
            {
                "mac": "cc0000000001",
                "port_id": "ge-0/0/1",
                "neighbor_mac": "bb0000000001",
                "neighbor_port_desc": "ge-0/0/47",
                "up": True,
                "stp_state": "blocking",
                "timestamp": 100,
            },
        ],
    )
    assert len(graph.edges) == 1
    assert graph.edges[0].source_stp_state == "forwarding"
    assert graph.edges[0].target_stp_state == "blocking"
    assert find_path(graph, "Core Switch", "Site Gateway").found is False


def test_timestamp_provenance_and_validation(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "100000000008",
                "hostname": "Wireless Client",
                "device_mac": "aa0000000001",
                "_topology_source": "wireless",
            },
            {
                "mac": "100000000009",
                "hostname": "Invalid Fields",
                "ip": "not-an-ip",
                "vlan": "4095",
                "ap_mac": "xxaa0000000001",
            },
        ],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "up": True,
                "timestamp": 1_700_000_000_000,
            }
        ],
    )
    assert _edge_with_port(graph, "ge-0/0/47").observed_at == "2023-11-14T22:13:20.000Z"
    wireless = resolve_node(graph, "Wireless Client")
    assert (
        next(edge for edge in graph.edges if edge.source == wireless.id).kind
        == "wireless"
    )
    assert wireless.metadata is not None
    assert wireless.metadata["associationSource"] == "wireless_client_stats_10m"
    invalid = resolve_node(graph, "Invalid Fields")
    assert invalid.ip is None
    assert invalid.vlan is None


def test_vlan_canonicalization_and_unknown_relationship(
    devices: list[JsonObject],
) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [
            {
                "mac": "10000000000a",
                "hostname": "VLAN A",
                "vlan": "0010",
                "ap_mac": "aa0000000001",
            },
            {
                "mac": "10000000000b",
                "hostname": "VLAN B",
                "vlan": 10,
                "ap_mac": "aa0000000001",
            },
        ],
    )
    assert find_path(graph, "VLAN A", "VLAN B").vlan_relationship == "same"
    assert find_path(graph, "VLAN A", "Lobby AP").vlan_relationship == "unknown"


def test_mermaid_sanitizes_edge_delimiters(devices: list[JsonObject]) -> None:
    graph = build_site_graph(
        "site-1",
        devices,
        [],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "cc0000000001",
                "neighbor_system_name": "Gateway | injected",
                "up": True,
            }
        ],
    )
    assert "Gateway | injected" not in graph_to_mermaid(graph)


def test_ambiguous_managed_alias_is_not_recreated(
    devices: list[JsonObject],
) -> None:
    ambiguous_devices = [
        *devices,
        {
            "id": "sw-2",
            "type": "switch",
            "name": "Second Switch",
            "mac": "dd0000000002",
            "vc_mac": "ee00000000ff",
        },
        {
            "id": "sw-3",
            "type": "switch",
            "name": "Third Switch",
            "mac": "dd0000000003",
            "chassis_mac": "ee00000000ff",
        },
    ]
    graph = build_site_graph(
        "site-1",
        ambiguous_devices,
        [
            {
                "mac": "ee00000000ff",
                "hostname": "False Client",
                "switch_mac": "bb0000000001",
            }
        ],
        ports=[
            {
                "mac": "bb0000000001",
                "port_id": "ge-0/0/47",
                "neighbor_mac": "ee00000000ff",
                "up": True,
            }
        ],
    )
    assert not any(node.name == "False Client" for node in graph.nodes)
    assert not any(
        node.kind == "unknown" and node.mac == "ee:00:00:00:00:ff"
        for node in graph.nodes
    )
    assert not any(edge.source_port == "ge-0/0/47" for edge in graph.edges)
    assert any("ambiguous neighbor MAC" in warning for warning in graph.warnings)


def test_dnt_device_aliases_resolve_direct_lldp_path() -> None:
    devices = [
        {"id": "gw", "type": "gateway", "name": "SSR400C", "mac": "6c62fec222b0"},
        {
            "id": "swb-1",
            "type": "switch",
            "name": "DNT-NTR-SWB-1",
            "mac": "6c78c1de3380",
        },
        {
            "id": "swb-2",
            "type": "switch",
            "name": "DNT-NTR-SWB-2",
            "mac": "2093390f6200",
        },
        {
            "id": "swb-3",
            "type": "switch",
            "name": "DNT-NTR-SWB-3",
            "mac": "2093390b3580",
        },
        {"id": "apb", "type": "ap", "name": "DNT-NTR-APB", "mac": "04a92439fb75"},
        {"id": "apt", "type": "ap", "name": "DNT-NTR-APT", "mac": "5c5b35f1b6b8"},
        {"id": "ape", "type": "ap", "name": "DNT-NTR-APE", "mac": "04cdc023ac50"},
    ]
    clients = [
        {"mac": "6c78c1de3380"},
        {"mac": "6c62fec222b5"},
        {
            "mac": "2093390f6200",
            "device_mac_port": [{"device_mac": "6c78c1de3380", "port_id": "mge-0/0/1"}],
        },
        {
            "mac": "2093390b3580",
            "device_mac_port": [{"device_mac": "2093390f6200", "port_id": "xe-0/1/2"}],
        },
        {
            "mac": "04a92439fb75",
            "device_mac_port": [{"device_mac": "2093390b3580", "port_id": "mge-0/0/1"}],
        },
    ]
    ports = [
        {
            "mac": "2093390f6200",
            "port_id": "xe-0/1/2",
            "neighbor_mac": "2093390b3580",
            "neighbor_port_desc": "xe-0/1/2",
            "up": True,
            "stp_state": "forwarding",
        },
        {
            "mac": "2093390f6200",
            "port_id": "xe-0/1/3",
            "neighbor_mac": "6c78c1de3380",
            "neighbor_port_desc": "xe-0/1/3",
            "up": True,
            "stp_state": "forwarding",
        },
        {
            "mac": "6c78c1de3380",
            "port_id": "ge-0/0/10",
            "neighbor_mac": "6c62fec222b5",
            "neighbor_port_desc": "ge-0/0/3",
            "up": True,
            "stp_state": "forwarding",
        },
        {
            "mac": "6c62fec222b0",
            "port_mac": "6c62fec222b5",
            "port_id": "ge-0/0/3",
            "neighbor_mac": "6c78c1de3380",
            "neighbor_port_desc": "ge-0/0/10",
            "up": True,
        },
        {
            "mac": "6c78c1de3380",
            "port_id": "mge-0/0/2",
            "neighbor_mac": "5c5b35f1b6b8",
            "up": True,
            "stp_state": "forwarding",
        },
        {
            "mac": "6c78c1de3380",
            "port_id": "mge-0/0/3",
            "neighbor_mac": "04cdc023ac50",
            "up": True,
            "stp_state": "forwarding",
        },
        {
            "mac": "2093390b3580",
            "port_id": "mge-0/0/0",
            "neighbor_mac": "04a92439fb75",
            "up": True,
            "stp_state": "forwarding",
        },
    ]
    graph = build_site_graph("dnt-ntr", devices, clients, ports=ports)
    path = find_path(graph, "DNT-NTR-SWB-2", "DNT-NTR-SWB-3")
    assert [node.name for node in path.nodes] == ["DNT-NTR-SWB-2", "DNT-NTR-SWB-3"]
    assert path.edges[0].source_port == "xe-0/1/2"
    assert len(graph.nodes) == 7
    assert _summary(graph)["infrastructureEdges"] == 6
    assert _summary(graph)["portMacAliases"] == 1
    assert not any(node.mac == "6c:62:fe:c2:22:b5" for node in graph.nodes)
