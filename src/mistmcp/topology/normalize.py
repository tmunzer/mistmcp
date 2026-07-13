"""Conservative normalization of Mist telemetry into evidence-aware graphs."""

from __future__ import annotations

import ipaddress
import math
import re
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any, Literal, cast

from mistmcp.topology.models import (
    JsonObject,
    PortDiagnostic,
    TopologyEdge,
    TopologyGraph,
    TopologyNode,
)

_MAC_PATTERN = re.compile(
    r"^(?:[0-9a-f]{12}|(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}|"
    r"[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})$"
)
_NON_TOPOLOGY_MACS = {
    "00:00:00:00:00:14",
    "02:00:00:00:00:0a",
}
_VLAN_PATTERN = re.compile(r"^\d{1,4}$")
_STP_STATES = {"blocking", "disabled", "forwarding", "learning", "listening"}
_MAX_VLAN = 4094
_MILLISECONDS_EPOCH_THRESHOLD = 100_000_000_000
_MAX_DATETIME_MILLISECONDS = 8_640_000_000_000_000
_MAX_WARNINGS = 100
_MAX_DIAGNOSTIC_EXAMPLES = 5
StpState = Literal["blocking", "disabled", "forwarding", "learning", "listening"]


def _text(record: JsonObject, *keys: str) -> str | None:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
    return None


def _normalized_mac(value: str | None) -> str | None:
    raw = value.strip().lower() if value else ""
    if not _MAC_PATTERN.fullmatch(raw):
        return None
    compact = re.sub(r"[.:-]", "", raw)
    normalized = ":".join(compact[index : index + 2] for index in range(0, 12, 2))
    return None if normalized in _NON_TOPOLOGY_MACS else normalized


def _valid_ip(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return None


def _valid_vlan(value: str | None) -> str | None:
    if not value or not _VLAN_PATTERN.fullmatch(value):
        return None
    vlan = int(value)
    return str(vlan) if 0 <= vlan <= _MAX_VLAN else None


def _node_id(kind: str, identity: str) -> str:
    return f"{kind}:{identity.lower()}"


def _edge_id(source: str, target: str, kind: str, discriminator: str = "") -> str:
    suffix = f":{discriminator}" if discriminator else ""
    return f"{kind}:{source}->{target}{suffix}"


def _stp_state(port: JsonObject) -> StpState | None:
    value = (_text(port, "stp_state") or "").strip().lower()
    return cast("StpState", value) if value in _STP_STATES else None


def _device_kind(device: JsonObject) -> Literal["ap", "switch", "gateway", "unknown"]:
    value = (_text(device, "type", "device_type") or "").lower()
    return (
        cast("Literal['ap', 'switch', 'gateway']", value)
        if value in {"ap", "switch", "gateway"}
        else "unknown"
    )


def _iso_timestamp(seconds: float) -> str:
    return (
        datetime.fromtimestamp(seconds, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _timestamp(value: Any) -> float | None:
    def normalize_epoch(raw: float) -> float | None:
        if not math.isfinite(raw) or raw <= 0:
            return None
        seconds = raw / 1000 if raw >= _MILLISECONDS_EPOCH_THRESHOLD else raw
        return seconds if seconds * 1000 <= _MAX_DATETIME_MILLISECONDS else None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return normalize_epoch(float(value))
    if not isinstance(value, str) or not value:
        return None
    try:
        return normalize_epoch(float(value))
    except ValueError:
        try:
            return datetime.fromisoformat(value).timestamp()
        except ValueError:
            return None


def _attachments_of(client: JsonObject) -> list[JsonObject]:
    value = client.get("device_mac_port")
    return (
        [item for item in value if isinstance(item, dict)]
        if isinstance(value, list)
        else []
    )


def _attachment_timestamp(attachment: JsonObject) -> float:
    return (
        _timestamp(attachment.get("when")) or _timestamp(attachment.get("start")) or 0
    )


def _client_timestamp(client: JsonObject) -> float:
    attachment_times = [_attachment_timestamp(item) for item in _attachments_of(client)]
    return max(
        _timestamp(client.get("timestamp")) or 0,
        _timestamp(client.get("last_seen")) or 0,
        *attachment_times,
    )


def _array_value(value: Any) -> str | None:
    if not isinstance(value, list):
        return None
    unique = {str(item) for item in value if isinstance(item, (str, int, float))}
    return next(iter(unique)) if len(unique) == 1 else None


def _select_attachment(client: JsonObject) -> tuple[JsonObject | None, bool]:
    attachments = _attachments_of(client)
    if not attachments:
        return None, False
    newest_time = max(_attachment_timestamp(item) for item in attachments)
    newest = (
        [
            item
            for item in attachments
            if _attachment_timestamp(item) in {newest_time, 0}
        ]
        if newest_time > 0
        else attachments
    )
    fingerprints = {
        "|".join(
            _text(item, key) or "" for key in ("device_mac", "port_id", "ip", "vlan")
        )
        for item in newest
    }
    selected = next(
        (item for item in newest if _attachment_timestamp(item) == newest_time),
        newest[0],
    )
    return (selected, False) if len(fingerprints) == 1 else (None, True)


def _record_fingerprint(client: JsonObject) -> str:
    attachment, ambiguous = _select_attachment(client)
    if ambiguous:
        return "ambiguous"
    if attachment:
        fields = [
            _text(attachment, key) or ""
            for key in ("device_mac", "port_id", "ip", "vlan")
        ]
        return "wired|" + "|".join(fields)
    raw_device_macs = client.get("device_mac")
    device_macs = (
        {value for value in raw_device_macs if isinstance(value, str)}
        if isinstance(raw_device_macs, list)
        else set()
    )
    upstream = (
        _text(client, "ap_mac", "switch_mac", "gateway_mac")
        or (
            next(iter(device_macs))
            if len(device_macs) == 1
            else _text(client, "device_mac")
        )
        or ""
    )
    vlan = (
        _text(client, "vlan", "vlan_id", "last_vlan")
        or _array_value(client.get("vlan"))
        or ""
    )
    return "reported|" + "|".join(
        [
            upstream,
            _text(client, "port_id") or "",
            _text(client, "ip", "ip_address") or "",
            vlan,
        ]
    )


def _unique_warnings(warnings: Iterable[str]) -> list[str]:
    unique = list(dict.fromkeys(warnings))
    if len(unique) <= _MAX_WARNINGS:
        return unique
    return [
        *unique[:99],
        f"{len(unique) - 99} additional caveat(s) were omitted from this response.",
    ]


def build_site_graph(  # noqa: PLR0915
    site_id: str,
    devices: list[JsonObject],
    clients: list[JsonObject],
    collector_warnings: list[str] | None = None,
    ports: list[JsonObject] | None = None,
    inventory_aliases: list[JsonObject] | None = None,
) -> TopologyGraph:
    """Build a site graph while omitting ambiguous or unsupported facts."""
    ports = ports or []
    inventory_aliases = inventory_aliases or []
    nodes: dict[str, TopologyNode] = {}
    edges: dict[str, TopologyEdge] = {}
    by_mac: dict[str, str] = {}
    ambiguous_macs: set[str] = set()
    warnings = list(collector_warnings or [])

    def add_example(examples: list[str], value: str) -> None:
        if value not in examples and len(examples) < _MAX_DIAGNOSTIC_EXAMPLES:
            examples.append(value)

    def register_mac(mac: str, node_id: str) -> None:
        if mac in ambiguous_macs:
            return
        existing = by_mac.get(mac)
        if existing and existing != node_id:
            by_mac.pop(mac, None)
            ambiguous_macs.add(mac)
            warnings.append(
                f"MAC {mac} is reported for multiple managed devices; correlation through this alias was omitted."
            )
            return
        by_mac[mac] = node_id

    def add_node(node: TopologyNode) -> None:
        current = nodes.get(node.id)
        values = current.model_dump() if current else {}
        values.update(node.model_dump(exclude_none=True))
        nodes[node.id] = TopologyNode.model_validate(values)
        if node.mac:
            register_mac(node.mac, node.id)

    def add_edge(**values: Any) -> None:
        if values["source"] == values["target"]:
            return
        discriminator = (
            f"{values.get('source_port', '')}->{values.get('target_port', '')}"
        )
        edge = TopologyEdge(
            id=_edge_id(
                values["source"], values["target"], values["kind"], discriminator
            ),
            **values,
        )
        edges[edge.id] = edge

    device_kinds: dict[str, str] = {}
    by_device_identity: dict[str, str] = {}
    identity_by_vc_mac: dict[str, str] = {}
    ambiguous_vc_macs: set[str] = set()
    vc_candidates: dict[str, set[str]] = {}
    for device in devices:
        identity = _text(device, "id", "device_id")
        vc_mac = _normalized_mac(_text(device, "vc_mac"))
        if _device_kind(device) == "switch" and identity and vc_mac:
            vc_candidates.setdefault(vc_mac, set()).add(identity)
    for vc_mac, identities in vc_candidates.items():
        if len(identities) == 1:
            identity_by_vc_mac[vc_mac] = next(iter(identities))
        else:
            ambiguous_vc_macs.add(vc_mac)
            warnings.append(
                f"Virtual-chassis MAC {vc_mac} maps to multiple Mist device IDs; "
                "member-only records using this alias were omitted."
            )

    def device_identity(device: JsonObject) -> str | None:
        explicit = _text(device, "id", "device_id")
        vc_mac = (
            _normalized_mac(_text(device, "vc_mac"))
            if _device_kind(device) == "switch"
            else None
        )
        if explicit:
            return explicit
        if vc_mac in ambiguous_vc_macs:
            return None
        if vc_mac:
            return identity_by_vc_mac.get(vc_mac, vc_mac)
        return _normalized_mac(_text(device, "mac"))

    skipped_device_records = 0
    for device in devices:
        identity = device_identity(device)
        if not identity:
            skipped_device_records += 1
            continue
        kind = _device_kind(device)
        previous = device_kinds.get(identity.lower())
        if not previous or (previous == "unknown" and kind != "unknown"):
            device_kinds[identity.lower()] = kind
    if skipped_device_records:
        warnings.append(
            f"{skipped_device_records} device record(s) without an unambiguous managed-device identity were omitted."
        )

    for device in devices:
        detected_kind = _device_kind(device)
        raw_mac = _normalized_mac(_text(device, "mac"))
        vc_mac = (
            _normalized_mac(_text(device, "vc_mac"))
            if detected_kind == "switch"
            else None
        )
        mac = vc_mac or raw_mac
        identity = device_identity(device)
        if not identity:
            continue
        kind = device_kinds.get(identity.lower(), detected_kind)
        node_id = _node_id(kind, identity)
        status = _text(device, "status")
        if status is None and isinstance(device.get("connected"), bool):
            status = "connected" if device["connected"] else "disconnected"
        add_node(
            TopologyNode(
                id=node_id,
                kind=cast("Literal['ap', 'switch', 'gateway', 'unknown']", kind),
                name=_text(device, "name", "hostname")
                or (nodes[node_id].name if node_id in nodes else None)
                or mac
                or identity,
                site_id=site_id,
                mac=mac,
                ip=_valid_ip(_text(device, "ip", "ip_address")),
                model=_text(device, "model"),
                status=status,
            )
        )
        by_device_identity[identity.lower()] = node_id
        if raw_mac:
            register_mac(raw_mac, node_id)
        for alias_key in ("vc_mac", "chassis_mac"):
            if alias_key == "vc_mac" and kind != "switch":
                continue
            alias = _normalized_mac(_text(device, alias_key))
            if alias:
                register_mac(alias, node_id)

    uncorrelated_inventory_aliases = 0
    ambiguous_inventory_aliases = 0
    for inventory in inventory_aliases:
        candidates: set[str] = set()
        explicit = _text(inventory, "id", "device_id")
        explicit_target = by_device_identity.get(explicit.lower()) if explicit else None
        if explicit_target:
            candidates.add(explicit_target)
        aliases = [
            alias
            for key in ("mac", "vc_mac", "chassis_mac")
            if (alias := _normalized_mac(_text(inventory, key)))
        ]
        for alias in aliases:
            if target := by_mac.get(alias):
                candidates.add(target)
        if len(candidates) == 1:
            target = next(iter(candidates))
            for alias in aliases:
                register_mac(alias, target)
        elif aliases and not candidates:
            uncorrelated_inventory_aliases += 1
        elif len(candidates) > 1:
            ambiguous_inventory_aliases += 1
    if uncorrelated_inventory_aliases:
        warnings.append(
            f"{uncorrelated_inventory_aliases} organization-inventory record(s) could not be correlated "
            "to a site-stat device; their MAC aliases were omitted."
        )
    if ambiguous_inventory_aliases:
        warnings.append(
            f"{ambiguous_inventory_aliases} organization-inventory record(s) matched multiple "
            "site-stat devices; their MAC aliases were omitted."
        )

    port_mac_targets: dict[str, set[str]] = {}
    port_mac_aliases = 0
    ambiguous_port_mac_aliases = 0
    unresolved_port_mac_alias_records = 0
    for port in ports:
        device_mac = _normalized_mac(_text(port, "mac"))
        interface_mac = _normalized_mac(_text(port, "port_mac"))
        if not interface_mac or interface_mac == device_mac:
            continue
        target = by_mac.get(device_mac) if device_mac else None
        if not target:
            unresolved_port_mac_alias_records += 1
            continue
        port_mac_targets.setdefault(interface_mac, set()).add(target)
    for interface_mac, targets in port_mac_targets.items():
        if len(targets) != 1:
            by_mac.pop(interface_mac, None)
            ambiguous_macs.add(interface_mac)
            ambiguous_port_mac_aliases += 1
            warnings.append(
                f"Port interface MAC {interface_mac} is reported for multiple managed devices; "
                "correlation through this alias was omitted."
            )
            continue
        target = next(iter(targets))
        existing = by_mac.get(interface_mac)
        register_mac(interface_mac, target)
        if not existing and by_mac.get(interface_mac) == target:
            port_mac_aliases += 1
        elif existing and existing != target:
            ambiguous_port_mac_aliases += 1
    if unresolved_port_mac_alias_records:
        warnings.append(
            f"{unresolved_port_mac_alias_records} port record(s) exposed an interface MAC but "
            "their device MAC could not be correlated; those aliases were omitted."
        )

    client_groups: dict[str, list[JsonObject]] = {}
    skipped_client_records = 0
    for client in clients:
        key = _normalized_mac(_text(client, "mac")) or _text(client, "id")
        if not key:
            skipped_client_records += 1
            continue
        client_groups.setdefault(key, []).append(client)
    if skipped_client_records:
        warnings.append(
            f"{skipped_client_records} client record(s) without a valid Mist ID or MAC were omitted."
        )

    for client_key, records in client_groups.items():
        newest_time = max(_client_timestamp(record) for record in records)
        newest_records = (
            [
                record
                for record in records
                if _client_timestamp(record) in {newest_time, 0}
            ]
            if newest_time > 0
            else records
        )
        fingerprints = {_record_fingerprint(record) for record in newest_records}
        client = next(
            (
                record
                for record in newest_records
                if _client_timestamp(record) == newest_time
            ),
            newest_records[0],
        )
        selected_attachment, attachment_ambiguous = _select_attachment(client)
        association_ambiguous = (
            attachment_ambiguous or len(fingerprints) > 1 or "ambiguous" in fingerprints
        )
        mac = _normalized_mac(_text(client, "mac"))
        identity = _text(client, "id") or mac
        if not identity:
            continue
        if mac in ambiguous_macs:
            warnings.append(
                f"Client record {mac} matches an ambiguous managed-device MAC alias and was omitted."
            )
            continue
        existing_id = by_mac.get(mac) if mac else None
        existing_node = nodes.get(existing_id) if existing_id else None
        is_managed = bool(
            existing_node and existing_node.kind in {"ap", "switch", "gateway"}
        )
        client_id = (
            existing_id if is_managed and existing_id else _node_id("client", identity)
        )
        attachment = None if association_ambiguous else selected_attachment
        source = _text(client, "_topology_source")
        wired = source == "wired" or (
            source != "wireless"
            and (
                bool(client.get("wired"))
                or _text(client, "type") == "wired"
                or "port_id" in client
                or bool(_attachments_of(client))
                or "device_mac" in client
            )
        )
        raw_vlan = (
            _text(attachment, "vlan")
            if wired and attachment
            else _text(client, "vlan", "vlan_id", "last_vlan")
            or _array_value(client.get("vlan"))
        )
        raw_ip = (
            _text(attachment, "ip")
            if wired and attachment
            else _text(client, "ip", "ip_address")
        )
        vlan = None if association_ambiguous else _valid_vlan(raw_vlan)
        client_ip = None if association_ambiguous else _valid_ip(raw_ip)
        seen_at = _client_timestamp(client)
        names = {
            value
            for record in newest_records
            if (
                value := _text(
                    record, "name", "hostname", "dhcp_hostname", "dhcp_fqdn", "username"
                )
            )
        }
        if not is_managed:
            add_node(
                TopologyNode(
                    id=client_id,
                    kind="client",
                    name=next(iter(names)) if len(names) == 1 else mac or identity,
                    site_id=site_id,
                    mac=mac,
                    ip=client_ip,
                    vlan=vlan,
                    status="recently_reported" if wired else "reported_by_mist",
                    metadata={
                        "associationSource": (
                            "wired_client_search_10m"
                            if wired
                            else "wireless_client_stats_10m"
                        ),
                        "associationAmbiguous": association_ambiguous,
                        **({"lastSeen": seen_at} if seen_at > 0 else {}),
                    },
                )
            )
        raw_device_macs = client.get("device_mac")
        device_macs = (
            {value for value in raw_device_macs if isinstance(value, str)}
            if isinstance(raw_device_macs, list)
            else set()
        )
        raw_device_mac = (
            next(iter(device_macs))
            if len(device_macs) == 1
            else _text(client, "device_mac")
        )
        upstream_mac = (
            None
            if association_ambiguous
            else _normalized_mac(
                (_text(attachment, "device_mac") if attachment else None)
                or _text(client, "ap_mac", "switch_mac", "gateway_mac")
                or raw_device_mac
            )
        )
        upstream = by_mac.get(upstream_mac) if upstream_mac else None
        if upstream and not is_managed:
            port = (
                _text(attachment, "port_id") if attachment else _text(client, "port_id")
            )
            add_edge(
                source=client_id,
                target=upstream,
                kind="ethernet" if wired else "wireless",
                confidence="reported",
                target_port=port,
                vlan=vlan,
                evidence=(
                    "Mist wired-client search (last 10 minutes)"
                    if wired
                    else "Mist wireless-client association statistics (last 10 minutes)"
                ),
                observed_at=_iso_timestamp(seen_at) if seen_at > 0 else None,
            )
        elif not is_managed:
            if association_ambiguous:
                warnings.append(
                    f"Conflicting or untimestamped associations were reported for client "
                    f"{mac or client_key}; attachment, IP, and VLAN were omitted."
                )
            elif upstream_mac:
                warnings.append(
                    f"Reported upstream MAC {upstream_mac} for client {mac or identity} could not "
                    "be correlated to a managed device; attachment is unknown."
                )
            else:
                warnings.append(
                    f"No recent upstream association was reported for client {mac or identity}; attachment is unknown."
                )

    def port_fingerprint(port: JsonObject) -> str:
        return "|".join(
            [
                _normalized_mac(_text(port, "neighbor_mac")) or "",
                str(port.get("up")).lower(),
                _stp_state(port) or (_text(port, "stp_state") or "").strip().lower(),
            ]
        )

    def unique_port_text(records: list[JsonObject], *keys: str) -> str | None:
        values = {value for record in records if (value := _text(record, *keys))}
        return next(iter(values)) if len(values) == 1 else None

    port_groups: dict[str, list[JsonObject]] = {}
    malformed_port_records = 0
    malformed_port_examples: list[str] = []
    for port in ports:
        source_mac = _normalized_mac(_text(port, "mac"))
        port_id = _text(port, "port_id")
        if not source_mac or not port_id:
            malformed_port_records += 1
            add_example(
                malformed_port_examples,
                f"{source_mac or 'invalid-or-non-topology'}|{port_id or 'unknown'}",
            )
            continue
        port_groups.setdefault(f"{source_mac}|{port_id}", []).append(port)
    if malformed_port_records:
        warnings.append(
            f"{malformed_port_records} port observation(s) without a valid source MAC or port ID were omitted."
        )

    selected_ports: list[
        tuple[JsonObject, str | None, str | None, StpState | None]
    ] = []
    ambiguous_port_groups = 0
    port_metadata_conflicts = 0
    invalid_stp_state_ports = 0
    for key, records in port_groups.items():
        newest_time = max(
            _timestamp(record.get("timestamp")) or 0 for record in records
        )
        port_candidates = (
            [
                record
                for record in records
                if (_timestamp(record.get("timestamp")) or 0) in {newest_time, 0}
            ]
            if newest_time > 0
            else records
        )
        if len({port_fingerprint(record) for record in port_candidates}) != 1:
            ambiguous_port_groups += 1
            warnings.append(
                f"Conflicting adjacency or operational-state observations were reported for {key}; this port was omitted."
            )
            continue
        target_port = unique_port_text(port_candidates, "neighbor_port_desc")
        neighbor_name = unique_port_text(port_candidates, "neighbor_system_name")
        port_usage = unique_port_text(port_candidates, "port_usage")
        if (
            any(_text(record, "neighbor_port_desc") for record in port_candidates)
            and not target_port
        ) or (
            any(_text(record, "neighbor_system_name") for record in port_candidates)
            and not neighbor_name
        ):
            port_metadata_conflicts += 1
        label = neighbor_name or port_usage
        record = next(
            (
                item
                for item in port_candidates
                if (_timestamp(item.get("timestamp")) or 0) == newest_time
            ),
            port_candidates[0],
        )
        raw_stp = _text(record, "stp_state")
        selected_stp = _stp_state(record)
        if raw_stp and not selected_stp:
            invalid_stp_state_ports += 1
            warnings.append(
                f"Port observation {key} reported unsupported STP state '{raw_stp}'; this port was omitted."
            )
            continue
        selected_ports.append((record, target_port, label, selected_stp))
    if port_metadata_conflicts:
        warnings.append(
            f"{port_metadata_conflicts} selected port observation(s) had conflicting descriptive LLDP fields; "
            "the adjacency was retained but conflicting labels or peer-port descriptions were omitted."
        )

    unresolved_port_records = 0
    unresolved_source_device_ports = 0
    missing_lldp_neighbor_ports = 0
    incomplete_lldp_identity_ports = 0
    down_ports = 0
    ambiguous_neighbor_ports = 0
    unmanaged_neighbor_ports = 0
    unresolved_source_examples: list[str] = []
    missing_lldp_examples: list[str] = []
    incomplete_lldp_examples: list[str] = []
    ambiguous_neighbor_examples: list[str] = []
    unmanaged_neighbor_examples: list[str] = []
    for port, target_port, label, selected_stp in selected_ports:
        if port.get("up") is not True:
            down_ports += 1
            continue
        source_mac = _normalized_mac(_text(port, "mac"))
        neighbor_mac = _normalized_mac(_text(port, "neighbor_mac"))
        port_ref = f"{source_mac or 'unknown'}|{_text(port, 'port_id') or 'unknown'}"
        source = by_mac.get(source_mac) if source_mac else None
        if not source:
            unresolved_port_records += 1
            unresolved_source_device_ports += 1
            add_example(unresolved_source_examples, port_ref)
            continue
        if not neighbor_mac:
            unresolved_port_records += 1
            has_partial_lldp = any(
                _text(port, key)
                for key in (
                    "neighbor_mac",
                    "neighbor_system_name",
                    "neighbor_port_desc",
                )
            )
            if has_partial_lldp:
                incomplete_lldp_identity_ports += 1
                add_example(incomplete_lldp_examples, port_ref)
            else:
                missing_lldp_neighbor_ports += 1
                add_example(missing_lldp_examples, port_ref)
            continue
        if neighbor_mac in ambiguous_macs:
            ambiguous_neighbor_ports += 1
            add_example(ambiguous_neighbor_examples, port_ref)
            warnings.append(
                f"Port {source_mac}|{_text(port, 'port_id') or 'unknown'} reports ambiguous "
                f"neighbor MAC {neighbor_mac}; this adjacency was omitted."
            )
            continue
        target = by_mac.get(neighbor_mac)
        if not target:
            unmanaged_neighbor_ports += 1
            add_example(unmanaged_neighbor_examples, port_ref)
            target = _node_id("unknown", neighbor_mac)
            add_node(
                TopologyNode(
                    id=target,
                    kind="unknown",
                    name=label or neighbor_mac,
                    site_id=site_id,
                    mac=neighbor_mac,
                )
            )
        seen_at = _timestamp(port.get("timestamp"))
        evidence_stp = f", stp_state={selected_stp}" if selected_stp else ""
        add_edge(
            source=source,
            target=target,
            kind="ethernet" if nodes[target].kind == "client" else "lldp",
            confidence="observed",
            source_port=_text(port, "port_id"),
            target_port=target_port,
            label=label,
            evidence=f"Mist port-search telemetry (up=true{evidence_stp})",
            operational_state="up",
            source_stp_state=selected_stp,
            observed_at=_iso_timestamp(seen_at) if seen_at else None,
        )
    if unresolved_port_records:
        reasons = ", ".join(
            part
            for count, part in (
                (
                    unresolved_source_device_ports,
                    f"{unresolved_source_device_ports} unresolved source device(s)",
                ),
                (
                    missing_lldp_neighbor_ports,
                    f"{missing_lldp_neighbor_ports} without LLDP neighbor data",
                ),
                (
                    incomplete_lldp_identity_ports,
                    f"{incomplete_lldp_identity_ports} with incomplete LLDP identity",
                ),
            )
            if count
        )
        warnings.append(
            f"{unresolved_port_records} up port observation(s) were omitted: {reasons}."
        )

    reciprocal_links: dict[str, str] = {}
    for edge_id, edge in list(edges.items()):
        if edge.kind != "lldp" or not edge.source_port or not edge.target_port:
            continue
        key = "<->".join(
            sorted(
                [
                    f"{edge.source}|{edge.source_port}",
                    f"{edge.target}|{edge.target_port}",
                ]
            )
        )
        reciprocal_id = reciprocal_links.get(key)
        if reciprocal_id:
            reciprocal = edges.get(reciprocal_id)
            if (
                reciprocal
                and reciprocal.source == edge.target
                and reciprocal.target == edge.source
            ):
                edges[reciprocal_id] = reciprocal.model_copy(
                    update={"target_stp_state": edge.source_stp_state}
                    if edge.source_stp_state
                    else {}
                )
            edges.pop(edge_id, None)
        else:
            reciprocal_links[key] = edge_id

    infrastructure_edges = sum(edge.kind == "lldp" for edge in edges.values())
    client_association_edges = sum(
        edge.kind == "wireless"
        or (edge.kind == "ethernet" and edge.confidence == "reported")
        for edge in edges.values()
    )
    non_forwarding_stp_edges = sum(
        any(
            state is not None and state != "forwarding"
            for state in (edge.source_stp_state, edge.target_stp_state)
        )
        for edge in edges.values()
    )
    if non_forwarding_stp_edges:
        warnings.append(
            f"{non_forwarding_stp_edges} up physical adjacency edge(s) have a known non-forwarding "
            "STP state; they are shown in site topology but excluded from path finding."
        )
    if not ports:
        warnings.append(
            "Mist port search returned no records; infrastructure topology is unavailable."
        )
    elif not infrastructure_edges:
        warnings.append(
            f"No infrastructure LLDP adjacency could be built from {len(ports)} collected port record(s): "
            f"{malformed_port_records} malformed, {ambiguous_port_groups} conflicting port group(s), "
            f"{invalid_stp_state_ports} invalid STP state(s), {down_ports} down selected port(s), "
            f"{unresolved_port_records} unresolved selected port(s), and "
            f"{ambiguous_neighbor_ports} ambiguous neighbor(s)."
        )

    port_diagnostics = [
        PortDiagnostic(
            reason=reason, count=count, explanation=explanation, examples=examples
        )
        for reason, count, explanation, examples in (
            (
                "missing_lldp_neighbor",
                missing_lldp_neighbor_ports,
                "Port is up but Mist reported no LLDP neighbor identity; the attached endpoint "
                "may not run LLDP.",
                missing_lldp_examples,
            ),
            (
                "incomplete_lldp_identity",
                incomplete_lldp_identity_ports,
                "Mist reported partial LLDP neighbor fields but no valid neighbor MAC, so the "
                "adjacency cannot be identified safely.",
                incomplete_lldp_examples,
            ),
            (
                "unresolved_source_device",
                unresolved_source_device_ports,
                "The port's source MAC could not be correlated to one managed device.",
                unresolved_source_examples,
            ),
            (
                "ambiguous_neighbor_mac",
                ambiguous_neighbor_ports,
                "The neighbor MAC is an alias of multiple managed devices, so the adjacency was omitted.",
                ambiguous_neighbor_examples,
            ),
            (
                "unmanaged_or_uncorrelated_neighbor",
                unmanaged_neighbor_ports,
                "The valid LLDP neighbor MAC did not match managed inventory; it remains visible "
                "as an unknown node.",
                unmanaged_neighbor_examples,
            ),
        )
        if count
    ]

    return TopologyGraph(
        scope="site",
        scope_id=site_id,
        generated_at=_now_iso(),
        nodes=list(nodes.values()),
        edges=list(edges.values()),
        warnings=_unique_warnings(warnings),
        port_diagnostics=port_diagnostics or None,
        evidence_summary={
            "portRecordsCollected": len(ports),
            "portMacAliases": port_mac_aliases,
            "ambiguousPortMacAliases": ambiguous_port_mac_aliases,
            "unresolvedPortMacAliasRecords": unresolved_port_mac_alias_records,
            "portGroups": len(port_groups),
            "portGroupsSelected": len(selected_ports),
            "malformedPortRecords": malformed_port_records,
            "ambiguousPortGroups": ambiguous_port_groups,
            "portMetadataConflicts": port_metadata_conflicts,
            "invalidStpStatePorts": invalid_stp_state_ports,
            "downPorts": down_ports,
            "unresolvedPortRecords": unresolved_port_records,
            "unresolvedSourceDevicePorts": unresolved_source_device_ports,
            "missingLldpNeighborPorts": missing_lldp_neighbor_ports,
            "incompleteLldpIdentityPorts": incomplete_lldp_identity_ports,
            "ambiguousNeighborPorts": ambiguous_neighbor_ports,
            "unmanagedOrUncorrelatedNeighborPorts": unmanaged_neighbor_ports,
            "infrastructureEdges": infrastructure_edges,
            "nonForwardingStpEdges": non_forwarding_stp_edges,
            "clientAssociationEdges": client_association_edges,
        },
    )


def build_wan_graph(  # noqa: PLR0915
    org_id: str,
    sites: list[JsonObject],
    devices: list[JsonObject],
    vpn_peers: list[JsonObject] | None = None,
    collector_warnings: list[str] | None = None,
) -> TopologyGraph:
    """Build WAN topology from inventory and explicit VPN peer-path statistics."""
    vpn_peers = vpn_peers or []
    nodes: dict[str, TopologyNode] = {}
    edges: dict[str, TopologyEdge] = {}
    warnings = list(collector_warnings or [])
    site_names = {
        site_id: _text(site, "name") or site_id
        for site in sites
        if (site_id := _text(site, "id"))
    }
    gateway_groups: dict[str, list[JsonObject]] = {}
    skipped_gateways = 0
    for device in devices:
        if _device_kind(device) != "gateway":
            continue
        identity = _text(device, "id") or _normalized_mac(_text(device, "mac"))
        if not identity:
            skipped_gateways += 1
            continue
        gateway_groups.setdefault(identity.lower(), []).append(device)

    def unique(values: list[str | None]) -> str | None:
        present = {value for value in values if value}
        return next(iter(present)) if len(present) == 1 else None

    def gateway_status(record: JsonObject) -> str | None:
        status = _text(record, "status")
        connected = record.get("connected")
        if status or not isinstance(connected, bool):
            return status
        return "connected" if connected else "disconnected"

    for identity, records in gateway_groups.items():
        names = [_text(record, "name") for record in records]
        macs = [_normalized_mac(_text(record, "mac")) for record in records]
        site_ids = [_text(record, "site_id") for record in records]
        models = [_text(record, "model") for record in records]
        statuses = [gateway_status(record) for record in records]
        name, mac, site_id, model, status = map(
            unique, (names, macs, site_ids, models, statuses)
        )
        for field, values in (
            ("name", names),
            ("MAC", macs),
            ("site", site_ids),
            ("model", models),
            ("status", statuses),
        ):
            if len({value for value in values if value}) > 1:
                warnings.append(
                    f"Conflicting {field} values were reported for gateway {identity}; this field was omitted."
                )
        node = TopologyNode(
            id=_node_id("gateway", identity),
            kind="gateway",
            name=name or mac or identity,
            site_id=site_id,
            mac=mac,
            model=model,
            status=status,
            metadata={
                "site": site_names.get(site_id, site_id) if site_id else "Unknown"
            },
        )
        nodes[node.id] = node
    if skipped_gateways:
        warnings.append(
            f"{skipped_gateways} gateway inventory record(s) without a valid Mist ID or MAC were omitted."
        )

    by_mac: dict[str, str] = {}
    ambiguous_gateway_macs: set[str] = set()
    for node in nodes.values():
        if not node.mac:
            continue
        existing = by_mac.get(node.mac)
        if existing and existing != node.id:
            by_mac.pop(node.mac, None)
            ambiguous_gateway_macs.add(node.mac)
            warnings.append(
                f"Gateway MAC {node.mac} belongs to multiple inventory nodes; VPN peer records "
                "using this MAC were omitted."
            )
        elif node.mac not in ambiguous_gateway_macs:
            by_mac[node.mac] = node.id

    gateways_from_peer_stats = 0

    def peer_gateway(mac: str, name: str | None, site_id: str | None) -> str | None:
        nonlocal gateways_from_peer_stats
        if mac in ambiguous_gateway_macs:
            return None
        existing_id = by_mac.get(mac)
        if existing_id:
            current = nodes[existing_id]
            updates: dict[str, Any] = {}
            if not current.site_id and site_id:
                updates["site_id"] = site_id
            if (
                current.name in {current.mac, current.id.removeprefix("gateway:")}
                and name
            ):
                updates["name"] = name
            if updates:
                resolved_site = cast(
                    "str | None", updates.get("site_id", current.site_id)
                )
                updates["metadata"] = {
                    **(current.metadata or {}),
                    "site": site_names.get(resolved_site, resolved_site)
                    if resolved_site
                    else "Unknown",
                }
                nodes[existing_id] = current.model_copy(update=updates)
            return existing_id
        node_id = _node_id("gateway", mac)
        nodes[node_id] = TopologyNode(
            id=node_id,
            kind="gateway",
            name=name or mac,
            site_id=site_id,
            mac=mac,
            status="reported_by_vpn_peer_stats",
            metadata={
                "site": site_names.get(site_id, site_id) if site_id else "Unknown",
                "source": "vpn_peer_stats",
            },
        )
        by_mac[mac] = node_id
        gateways_from_peer_stats += 1
        return node_id

    peer_groups: dict[str, list[JsonObject]] = {}
    malformed_peer_records = 0
    ambiguous_peer_records = 0
    for peer in vpn_peers:
        local_mac = _normalized_mac(_text(peer, "mac"))
        remote_mac = _normalized_mac(_text(peer, "peer_mac"))
        if not local_mac or not remote_mac or local_mac == remote_mac:
            malformed_peer_records += 1
            continue
        endpoints = sorted(
            [
                f"{local_mac}|{_text(peer, 'port_id') or ''}",
                f"{remote_mac}|{_text(peer, 'peer_port_id') or ''}",
            ]
        )
        peer_groups.setdefault("<->".join(endpoints), []).append(peer)

    for key, records in peer_groups.items():
        newest_time = max(
            _timestamp(record.get("last_seen")) or 0 for record in records
        )
        candidates = (
            [
                record
                for record in records
                if (_timestamp(record.get("last_seen")) or 0) in {newest_time, 0}
            ]
            if newest_time > 0
            else records
        )

        def peer_fingerprint(record: JsonObject) -> str:
            local_mac = _normalized_mac(_text(record, "mac")) or ""
            remote_mac = _normalized_mac(_text(record, "peer_mac")) or ""
            endpoints = sorted(
                [
                    f"{local_mac}|{_text(record, 'site_id') or ''}",
                    f"{remote_mac}|{_text(record, 'peer_site_id') or ''}",
                ]
            )
            state = record.get("up")
            return "|".join([*endpoints, _text(record, "type") or "", str(state)])

        if len({peer_fingerprint(record) for record in candidates}) != 1:
            ambiguous_peer_records += 1
            warnings.append(
                f"Conflicting latest VPN peer-path observations were returned for {key}; "
                "this WAN edge was omitted."
            )
            continue
        record = next(
            (
                item
                for item in candidates
                if (_timestamp(item.get("last_seen")) or 0) == newest_time
            ),
            candidates[0],
        )
        local_mac = _normalized_mac(_text(record, "mac"))
        remote_mac = _normalized_mac(_text(record, "peer_mac"))
        if not local_mac or not remote_mac:
            malformed_peer_records += 1
            continue
        source = peer_gateway(
            local_mac,
            _text(record, "router_name"),
            _text(record, "site_id"),
        )
        target = peer_gateway(
            remote_mac,
            _text(record, "peer_router_name"),
            _text(record, "peer_site_id"),
        )
        if not source or not target:
            ambiguous_peer_records += 1
            continue
        raw_up = record.get("up")
        state = "up" if raw_up is True else "down" if raw_up is False else None
        vpn_type = _text(record, "type")
        source_port = _text(record, "port_id")
        target_port = _text(record, "peer_port_id")
        if (source, source_port or "") > (target, target_port or ""):
            source, target = target, source
            source_port, target_port = target_port, source_port
        edge = TopologyEdge(
            id=_edge_id(
                source,
                target,
                "vpn",
                f"{source_port or ''}->{target_port or ''}",
            ),
            source=source,
            target=target,
            kind="vpn",
            confidence="observed",
            label=" · ".join(
                value for value in (vpn_type, state or "state unknown") if value
            ),
            source_port=source_port,
            target_port=target_port,
            evidence="Mist organization VPN peer-path statistics (last 1 day)",
            observed_at=_iso_timestamp(newest_time) if newest_time else None,
            operational_state=state,
        )
        edges[edge.id] = edge

    up_peer_paths = sum(edge.operational_state == "up" for edge in edges.values())
    down_peer_paths = sum(edge.operational_state == "down" for edge in edges.values())
    unknown_peer_paths = len(edges) - up_peer_paths - down_peer_paths
    if malformed_peer_records:
        warnings.append(
            f"{malformed_peer_records} VPN peer-path record(s) lacked distinct valid local and "
            "peer MAC addresses and were omitted."
        )
    if not vpn_peers:
        warnings.append(
            "Mist VPN peer-path search returned no records for the last day; no WAN overlay "
            "relationships could be observed."
        )
    elif not edges:
        warnings.append(
            "VPN peer-path records were returned, but no unambiguous WAN overlay edge could be built."
        )
    if down_peer_paths:
        warnings.append(
            f"{down_peer_paths} observed VPN peer path(s) are currently reported down; they remain "
            "visible as topology relationships."
        )
    if not nodes:
        warnings.append(
            "No gateways were returned by inventory or VPN peer statistics; WAN topology is inconclusive."
        )
    return TopologyGraph(
        scope="wan",
        scope_id=org_id,
        generated_at=_now_iso(),
        nodes=list(nodes.values()),
        edges=list(edges.values()),
        warnings=_unique_warnings(warnings),
        evidence_summary={
            "gatewayInventoryNodes": len(gateway_groups),
            "gatewaysFromVpnPeerStats": gateways_from_peer_stats,
            "vpnPeerRecordsCollected": len(vpn_peers),
            "vpnPeerPathGroups": len(peer_groups),
            "vpnPeerPaths": len(edges),
            "upVpnPeerPaths": up_peer_paths,
            "downVpnPeerPaths": down_peer_paths,
            "unknownStateVpnPeerPaths": unknown_peer_paths,
            "malformedVpnPeerRecords": malformed_peer_records,
            "ambiguousVpnPeerPaths": ambiguous_peer_records,
        },
    )
