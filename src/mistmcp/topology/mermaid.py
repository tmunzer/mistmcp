"""Context-efficient Mermaid rendering for topology graphs and paths."""

from __future__ import annotations

import base64
import re

from mistmcp.topology.models import PathResult, TopologyGraph, TopologyNode

_UNSAFE_LABEL = re.compile(r'[\x00-\x1f"|<>`]')


def _safe_id(node_id: str) -> str:
    encoded = base64.urlsafe_b64encode(node_id.encode()).decode().rstrip("=")
    return f"n_{encoded}"


def _safe_label(value: str) -> str:
    return _UNSAFE_LABEL.sub(" ", value)[:100]


def _shape(node: TopologyNode, label: str) -> str:
    node_id = _safe_id(node.id)
    if node.kind == "client":
        return f'{node_id}(["{label}"])'
    if node.kind == "gateway":
        return f'{node_id}{{{{"{label}"}}}}'
    if node.kind == "dhcp_server":
        return f'{node_id}[("{label}")]'
    return f'{node_id}["{label}"]'


def _node_shape(node: TopologyNode) -> str:
    return _shape(node, _safe_label(f"{node.name}{chr(10)}{node.kind}"))


def graph_to_mermaid(graph: TopologyGraph) -> str:
    """Render a complete topology graph as a left-to-right Mermaid flowchart."""
    lines = ["flowchart LR"]
    lines.extend(f"  {_node_shape(node)}" for node in graph.nodes)
    for edge in graph.edges:
        states = [
            state for state in (edge.source_stp_state, edge.target_stp_state) if state
        ]
        stp = f" · STP {'/'.join(states)}" if states else ""
        label = _safe_label(f"{edge.label or edge.kind}{stp}")
        lines.append(
            f'  {_safe_id(edge.source)} ---|"{label}"| {_safe_id(edge.target)}'
        )
    return "\n".join(lines)


def path_to_mermaid(path: PathResult) -> str:
    """Render a candidate path as a left-to-right Mermaid flowchart."""
    lines = ["flowchart LR"]
    lines.extend(f"  {_node_shape(node)}" for node in path.nodes)
    for edge in path.edges:
        states = [
            state for state in (edge.source_stp_state, edge.target_stp_state) if state
        ]
        stp = f" · STP {'/'.join(states)}" if states else ""
        label = _safe_label(f"{edge.kind} · {edge.confidence}{stp}")
        lines.append(
            f'  {_safe_id(edge.source)} ---|"{label}"| {_safe_id(edge.target)}'
        )
    return "\n".join(lines)
