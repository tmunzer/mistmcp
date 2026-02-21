DEVICE_CONFIGURATION_TEMPLATE = '''"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
from typing import Annotated
from uuid import UUID

import mistapi
from fastmcp import Context
from pydantic import Field

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import process_response
from mistmcp.server import mcp

NETWORK_TEMPLATE_FIELDS = [
    "auto_upgrade_linecard",
    "acl_policies",
    "acl_tags",
    "additional_config_cmds",
    "dhcp_snooping",
    "disabled_system_defined_port_usages",
    "dns_servers",
    "dns_suffix",
    "extra_routes",
    "extra_routes6",
    "fips_enabled",
    "id",
    "mist_nac",
    "networks",
    "ntp_servers",
    "port_mirroring",
    "port_usages",
    "radius_config",
    "remote_syslog",
    "snmp_config",
    "routing_policies",
    "switch_matching",
    "switch_mgmt",
    "vrf_config",
    "vrf_instances",
]


@mcp.tool(
    name="getDeviceConfiguration",
    description="""Retrieve configuration applied to a specific device. The returned configuration is a merged view of the device configuration, site-level configuration, and org-level configuration.""",
    tags={"configuration"},
    annotations={
        "title": "getDeviceConfiguration",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getDeviceConfiguration(
    org_id: Annotated[
        UUID,
        Field(description="""ID of the Mist Org"""),
    ] = UUID("9777c1a0-6ef6-11e6-8bbf-02e208b2d34f"),
    site_id: Annotated[
        UUID,
        Field(description="""ID of the site to retrieve configuration objects from."""),
    ] = UUID("978c48e6-6ef6-11e6-8bbf-02e208b2d34f"),
    device_id: Annotated[
        UUID,
        Field(description="""ID of the device to retrieve configuration for."""),
    ] = UUID("00000000-0000-0000-1000-aca09d7ada80"),
    ctx: Context | None = None,
) -> dict | list | str:
    """Retrieve configuration applied to a specific device"""

    logger.debug("Tool {operationId} called")

    apisession, response_format = get_apisession()

    device_data = mistapi.api.v1.sites.devices.getSiteDevice(
        apisession, site_id=str(site_id), device_id=str(device_id)
    )
    await process_response(device_data)

    data = {}
    match device_data.data.get("type"):
        case "ap":
            data = device_data

        case "switch":
            switch_name = device_data.data.get("name", "")
            switch_model = device_data.data.get("model", "")
            switch_role = device_data.data.get("role", "")
            switch_data = {}
            site_data = mistapi.api.v1.sites.sites.getSiteInfo(
                apisession, site_id=str(site_id)
            )
            await process_response(site_data)
            network_template_id = site_data.data.get("networktemplate_id")
            if network_template_id:
                org_config = mistapi.api.v1.orgs.networktemplates.getOrgNetworkTemplate(
                    apisession,
                    org_id=str(org_id),
                    networktemplate_id=str(network_template_id),
                )
                await process_response(org_config)
                switch_data = process_switch_template(
                    org_config.data, switch_name, switch_model, switch_role, switch_data
                )

            site_config = mistapi.api.v1.sites.setting.getSiteSetting(
                apisession, site_id=str(site_id)
            )
            await process_response(site_config)
            switch_data = process_switch_template(
                site_config.data, switch_name, switch_model, switch_role, switch_data
            )

            for key, value in device_data.data.items():
                if key == "port_config":
                    port_config = process_switch_interface(value)
                    switch_data[key] = {**data.get(key, {}), **port_config}
                elif isinstance(value, dict) and isinstance(switch_data.get(key, {}), dict):
                    switch_data[key] = {**switch_data.get(key, {}), **value}
                elif isinstance(value, list) and isinstance(switch_data.get(key, []), list):
                    switch_data[key] = switch_data.get(key, []) + value
                else:
                    switch_data[key] = value
            device_data.data = switch_data
            data = device_data
        case "gateway":
            gateway_data = {}
            site_data = mistapi.api.v1.sites.sites.getSiteInfo(
                apisession, site_id=str(site_id)
            )
            await process_response(site_data)
            gateway_template_id = site_data.data.get("gatewaytemplate_id")
            if gateway_template_id:
                response = mistapi.api.v1.orgs.gatewaytemplates.getOrgGatewayTemplate(
                    apisession,
                    org_id=str(org_id),
                    gatewaytemplate_id=str(gateway_template_id),
                )
                await process_response(response)
                gateway_data = response.data

            for key, value in device_data.data.items():
                if key in NETWORK_TEMPLATE_FIELDS:
                    if isinstance(value, dict) and isinstance(gateway_data.get(key, {}), dict):
                        gateway_data[key] = {
                            **gateway_data.get(key, {}), **value}
                    elif isinstance(value, list) and isinstance(
                        gateway_data.get(key, []), list
                    ):
                        gateway_data[key] = gateway_data.get(key, []) + value
                    else:
                        gateway_data[key] = value
            device_data.data = gateway_data
            data = device_data

        case _:
            data = device_data

    return format_response(data, response_format)



def process_switch_template(
    template: dict,
    switch_name: str,
    switch_model: str,
    switch_role: str,
    data: dict,
) -> dict:
    for key, value in template.items():
        if key in NETWORK_TEMPLATE_FIELDS:
            if key == "name":
                continue
            elif key == "switch_matching" and value.get("enable"):
                data = process_switch_rule(
                    value.get("rules", []),
                    switch_name,
                    switch_model,
                    switch_role,
                    data,
                )
            elif isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                data[key] = {**data.get(key, {}), **value}
            elif isinstance(value, list) and isinstance(data.get(key, []), list):
                data[key] = data.get(key, []) + value
            else:
                data[key] = value

    return data


def process_switch_rule(
    rules: list,
    switch_name: str,
    switch_model: str,
    switch_role: str,
    data: dict,
) -> dict:
    for rule in rules:
        rule_cleansed = rule.copy()
        del rule_cleansed["name"]

        match_name_true = False
        match_name_enabled = False
        match_model_true = False
        match_model_enabled = False
        match_role_true = False
        match_role_enabled = False
        for k, v in rule.items():
            if k.startswith("match_name"):
                match_name_enabled = True
                del rule_cleansed[k]
                match_name_true = process_switch_rule_match(switch_name, k, v)
            elif k.startswith("match_model"):
                match_model_enabled = True
                del rule_cleansed[k]
                match_model_true = process_switch_rule_match(
                    switch_model, k, v)
            elif k == "match_role":
                match_role_enabled = True
                match_role_true = process_switch_rule_match(switch_role, k, v)
        if (
            (not match_name_enabled or match_name_true)
            and (not match_model_enabled or match_model_true)
            and (not match_role_enabled or match_role_true)
        ):
            for key, value in rule_cleansed.items():
                if key == "port_config":
                    port_config = process_switch_interface(value)
                    data[key] = {**data.get(key, {}), **port_config}
                elif isinstance(value, dict) and isinstance(data.get(key, {}), dict):
                    data[key] = {**data.get(key, {}), **value}
                elif isinstance(value, list) and isinstance(data.get(key, []), list):
                    data[key] = data.get(key, []) + value
                else:
                    data[key] = value
            return data
    return data


def process_switch_rule_match(
    switch_value: str, match_key: str, match_value: str
) -> bool:
    if ":" in match_key:
        match_start, match_stop = match_key.replace(
            "]", "").split("[")[1].split(":")
        try:
            if (
                len(switch_value) > int(match_stop)
                and switch_value[int(match_start): int(match_stop)].lower()
                == match_value.lower()
            ):
                return True
        except Exception:
            return False
    elif switch_value.lower() == match_value.lower():
        return True
    return False


def process_switch_interface(port_config: dict) -> dict:
    port_config_tmp = {}
    for key, value in port_config.items():
        if "," in key:
            keys = [k.strip() for k in key.split(",")]
            for k in keys:
                port_config_tmp[k] = value
        else:
            port_config_tmp[key] = value

    port_config_cleansed = {}
    for key, value in port_config_tmp.items():
        if key.count("-") > 1:
            prefix, interfaces = key.split("-", 1)
            fpc, pic, port = interfaces.split("/")
            if "-" in fpc:
                fpc_start, fpc_end = fpc.split("-")
                for fpc_num in range(int(fpc_start), int(fpc_end) + 1):
                    port_config_cleansed[f"{prefix}-{fpc_num}/{pic}/{port}"] = value
            elif "-" in pic:
                pic_start, pic_end = pic.split("-")
                for pic_num in range(int(pic_start), int(pic_end) + 1):
                    port_config_cleansed[f"{prefix}-{fpc}/{pic_num}/{port}"] = value
            elif "-" in port:
                port_start, port_end = port.split("-")
                for port_num in range(int(port_start), int(port_end) + 1):
                    port_config_cleansed[f"{prefix}-{fpc}/{pic}/{port_num}"] = value
        else:
            port_config_cleansed[key] = value

    return port_config_cleansed

'''
