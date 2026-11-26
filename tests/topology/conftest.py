"""Shared topology fixtures."""

from __future__ import annotations

import pytest

from mistmcp.topology.models import JsonObject


@pytest.fixture
def devices() -> list[JsonObject]:
    return [
        {
            "id": "ap-1",
            "type": "ap",
            "name": "Lobby AP",
            "mac": "aa:00:00:00:00:01",
        },
        {
            "id": "sw-1",
            "type": "switch",
            "name": "Core Switch",
            "mac": "bb:00:00:00:00:01",
        },
        {
            "id": "gw-1",
            "type": "gateway",
            "name": "Site Gateway",
            "mac": "cc:00:00:00:00:01",
        },
    ]


@pytest.fixture
def clients() -> list[JsonObject]:
    return [
        {
            "mac": "10:00:00:00:00:01",
            "hostname": "Alice Laptop",
            "ip": "10.10.10.10",
            "vlan": 10,
            "ap_mac": "aa:00:00:00:00:01",
        },
        {
            "mac": "10:00:00:00:00:02",
            "hostname": "Build Server",
            "ip": "10.20.20.20",
            "vlan": 20,
            "switch_mac": "bb:00:00:00:00:01",
            "wired": True,
            "port_id": "ge-0/0/8",
        },
    ]


@pytest.fixture
def infrastructure_ports() -> list[JsonObject]:
    return [
        {
            "mac": "aa0000000001",
            "port_id": "eth0",
            "neighbor_mac": "bb0000000001",
            "neighbor_system_name": "Core Switch",
            "neighbor_port_desc": "ge-0/0/1",
            "up": True,
            "active": True,
            "timestamp": 100,
        }
    ]
