"""Candidate physical path resolution over normalized topology graphs."""

from __future__ import annotations

import re
from collections import deque

from mistmcp.topology.models import (
    PathResult,
    TopologyEdge,
    TopologyGraph,
    TopologyNode,
)


def _canonical(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def resolve_node(graph: TopologyGraph, selector: str) -> TopologyNode:
    """Resolve an exact identifier or a unique partial display name."""
    needle = _canonical(selector)
    exact = [
        node
        for node in graph.nodes
        if any(
            value and _canonical(value) == needle
            for value in (node.id, node.name, node.mac, node.ip)
        )
    ]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise ValueError(
            f"'{selector}' matches multiple nodes; use the Mist ID or MAC address."
        )
    partial = [node for node in graph.nodes if needle in _canonical(node.name)]
    if len(partial) == 1:
        return partial[0]
    if len(partial) > 1:
        raise ValueError(
            f"'{selector}' matches {len(partial)} nodes; use a full name, IP, MAC, or Mist ID."
        )
    raise ValueError(
        f"No topology node matches '{selector}'. Query the site topology first to see valid identifiers."
    )


def find_path(
    graph: TopologyGraph, source_selector: str, destination_selector: str
) -> PathResult:
    """Find an evidence-prioritized candidate physical chain between two nodes."""
    source = resolve_node(graph, source_selector)
    destination = resolve_node(graph, destination_selector)
    by_id = {node.id: node for node in graph.nodes}
    adjacency: dict[str, list[tuple[str, TopologyEdge]]] = {}
    for edge in graph.edges:
        if any(
            state is not None and state != "forwarding"
            for state in (edge.source_stp_state, edge.target_stp_state)
        ):
            continue
        adjacency.setdefault(edge.source, []).append((edge.target, edge))
        adjacency.setdefault(edge.target, []).append((edge.source, edge))

    def evidence_priority(edge: TopologyEdge) -> int:
        if edge.kind == "lldp" and edge.confidence == "observed":
            return 0
        if edge.confidence == "observed":
            return 1
        if edge.confidence == "reported":
            return 2
        return 3

    for neighbors in adjacency.values():
        neighbors.sort(key=lambda item: evidence_priority(item[1]))
    queue = deque([source.id])
    previous: dict[str, tuple[str, TopologyEdge]] = {}
    seen = {source.id}
    while queue and destination.id not in seen:
        current = queue.popleft()
        for next_id, edge in adjacency.get(current, []):
            if next_id in seen:
                continue
            next_node = by_id.get(next_id)
            if (
                next_id != destination.id
                and next_node
                and next_node.kind in {"client", "dhcp_server"}
            ):
                continue
            seen.add(next_id)
            previous[next_id] = (current, edge)
            queue.append(next_id)

    vlan_relationship = (
        "unknown"
        if not source.vlan or not destination.vlan
        else "same"
        if source.vlan == destination.vlan
        else "different"
    )
    if destination.id not in seen:
        return PathResult(
            found=False,
            source=source,
            destination=destination,
            nodes=[],
            edges=[],
            vlan_relationship=vlan_relationship,
            explanation=(
                "No candidate physical topology path can be supported by the evidence returned by "
                "Mist. Traffic forwarding was not tested."
            ),
            warnings=graph.warnings,
        )

    node_ids = [destination.id]
    edges: list[TopologyEdge] = []
    while node_ids[0] != source.id:
        step = previous.get(node_ids[0])
        if not step:
            break
        prior_id, edge = step
        node_ids.insert(0, prior_id)
        edges.insert(0, edge)
    nodes = [by_id[node_id] for node_id in node_ids if node_id in by_id]
    has_gateway = any(node.kind == "gateway" for node in nodes)
    warnings = list(graph.warnings)
    if vlan_relationship == "different" and not has_gateway:
        warnings.append(
            "The endpoints are on different VLANs and no gateway adjacency is present. The "
            "candidate physical chain is not a routed path."
        )
    if vlan_relationship == "unknown":
        warnings.append(
            "VLAN relationship is unknown because one or both endpoints have no unambiguous VLAN value."
        )
    if any(
        edge.kind == "lldp" and (not edge.source_stp_state or not edge.target_stp_state)
        for edge in edges
    ):
        warnings.append(
            "STP state was not reported for one or both ends of at least one LLDP adjacency in "
            "this path; only known non-forwarding STP states were excluded."
        )
    warnings.append(
        "This is a candidate physical topology chain only. VLAN forwarding, STP state, routes, "
        "VRFs, and policy were not verified."
    )
    return PathResult(
        found=True,
        source=source,
        destination=destination,
        nodes=nodes,
        edges=edges,
        vlan_relationship=vlan_relationship,
        explanation=(
            f"Candidate physical topology: {' → '.join(node.name for node in nodes)}. "
            "Traffic forwarding is not verified."
        ),
        warnings=warnings,
    )
