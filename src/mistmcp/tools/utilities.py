"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import asyncio
import inspect
import json
import time
from enum import Enum
from types import NoneType, UnionType
from typing import Annotated, Any, Union, get_args, get_origin
from uuid import UUID

from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistapi.device_utils import ap as ap_utils
from mistapi.device_utils import ex as ex_utils
from mistapi.device_utils import srx as srx_utils
from mistapi.device_utils import ssr as ssr_utils
from pydantic import Field

from mistmcp.config import config
from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp

UTILITY_TOOL_TIMEOUT_SECONDS = 120.0
UTILITY_WAIT_TIMEOUT_SECONDS = 75.0
EXCLUDED_DEVICE_UTILITIES = {
    "ShellSession",
    "createShellSession",
    "interactiveShell",
    "TracerouteProtocol",
    "RouteProtocol",
    "Node",
}
MUTATING_DEVICE_UTILITIES = {
    "bouncePort",
    "clearBpduError",
    "clearDot1xSessions",
    "clearHitCount",
    "clearLearnedMac",
    "clearMacTable",
    "clearSessions",
    "releaseDhcpLeases",
}
DISRUPTIVE_DEVICE_UTILITIES = {
    "bouncePort",
    "clearBpduError",
    "clearDot1xSessions",
    "clearLearnedMac",
    "clearMacTable",
    "clearSessions",
    "releaseDhcpLeases",
}


class DeviceUtilityType(Enum):
    AP = "ap"
    EX = "ex"
    SRX = "srx"
    SSR = "ssr"


SUPPORTED_DEVICE_UTILITIES: dict[DeviceUtilityType, dict[str, Any]] = {
    DeviceUtilityType.AP: {
        "ping": ap_utils.ping,
        "traceroute": ap_utils.traceroute,
        "retrieveArpTable": ap_utils.retrieveArpTable,
    },
    DeviceUtilityType.EX: {
        "retrieveArpTable": ex_utils.retrieveArpTable,
        "retrieveBgpSummary": ex_utils.retrieveBgpSummary,
        "clearBpduError": ex_utils.clearBpduError,
        "retrieveDhcpLeases": ex_utils.retrieveDhcpLeases,
        "releaseDhcpLeases": ex_utils.releaseDhcpLeases,
        "clearDot1xSessions": ex_utils.clearDot1xSessions,
        "clearLearnedMac": ex_utils.clearLearnedMac,
        "clearMacTable": ex_utils.clearMacTable,
        "retrieveMacTable": ex_utils.retrieveMacTable,
        "clearHitCount": ex_utils.clearHitCount,
        "bouncePort": ex_utils.bouncePort,
        "cableTest": ex_utils.cableTest,
        "monitorTraffic": ex_utils.monitorTraffic,
        "ping": ex_utils.ping,
        "topCommand": ex_utils.topCommand,
        "traceroute": ex_utils.traceroute,
    },
    DeviceUtilityType.SRX: {
        "retrieveArpTable": srx_utils.retrieveArpTable,
        "retrieveBgpSummary": srx_utils.retrieveBgpSummary,
        "releaseDhcpLeases": srx_utils.releaseDhcpLeases,
        "retrieveDhcpLeases": srx_utils.retrieveDhcpLeases,
        "monitorTraffic": srx_utils.monitorTraffic,
        "ping": srx_utils.ping,
        "topCommand": srx_utils.topCommand,
        "traceroute": srx_utils.traceroute,
        "retrieveOspfDatabase": srx_utils.retrieveOspfDatabase,
        "retrieveOspfNeighbors": srx_utils.retrieveOspfNeighbors,
        "retrieveOspfInterfaces": srx_utils.retrieveOspfInterfaces,
        "retrieveOspfSummary": srx_utils.retrieveOspfSummary,
        "bouncePort": srx_utils.bouncePort,
        "retrieveRoutes": srx_utils.retrieveRoutes,
        "clearSessions": srx_utils.clearSessions,
        "retrieveSessions": srx_utils.retrieveSessions,
    },
    DeviceUtilityType.SSR: {
        "retrieveArpTable": ssr_utils.retrieveArpTable,
        "retrieveBgpSummary": ssr_utils.retrieveBgpSummary,
        "releaseDhcpLeases": ssr_utils.releaseDhcpLeases,
        "retrieveDhcpLeases": ssr_utils.retrieveDhcpLeases,
        "ping": ssr_utils.ping,
        "traceroute": ssr_utils.traceroute,
        "retrieveOspfDatabase": ssr_utils.retrieveOspfDatabase,
        "retrieveOspfNeighbors": ssr_utils.retrieveOspfNeighbors,
        "retrieveOspfInterfaces": ssr_utils.retrieveOspfInterfaces,
        "retrieveOspfSummary": ssr_utils.retrieveOspfSummary,
        "bouncePort": ssr_utils.bouncePort,
        "retrieveRoutes": ssr_utils.retrieveRoutes,
        "showServicePath": ssr_utils.showServicePath,
        "clearSessions": ssr_utils.clearSessions,
        "retrieveSessions": ssr_utils.retrieveSessions,
    },
}


def _normalize_utility_name(name: str) -> str:
    return "".join(character for character in name.lower() if character.isalnum())


def _strip_optional(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin in (Union, UnionType):
        args = [arg for arg in get_args(annotation) if arg is not NoneType]
        if len(args) == 1:
            return args[0]
    return annotation


def _annotation_description(annotation: Any) -> str:
    if annotation in (inspect.Signature.empty, Any):
        return "any"

    target = _strip_optional(annotation)
    origin = get_origin(target)

    if origin is list:
        inner_type = get_args(target)[0] if get_args(target) else Any
        return f"list[{_annotation_description(inner_type)}]"

    if inspect.isclass(target) and issubclass(target, Enum):
        values = ", ".join(member.value for member in target)
        return f"enum[{values}]"

    if hasattr(target, "__name__"):
        return target.__name__

    return str(target)


def _convert_parameter_value(name: str, value: Any, annotation: Any) -> Any:
    if annotation in (inspect.Signature.empty, Any):
        return value

    target = _strip_optional(annotation)
    origin = get_origin(target)

    if origin is list:
        if not isinstance(value, list):
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Parameter '{name}' must be a list.",
                }
            )
        inner_type = get_args(target)[0] if get_args(target) else Any
        return [_convert_parameter_value(name, item, inner_type) for item in value]

    if inspect.isclass(target) and issubclass(target, Enum):
        if isinstance(value, target):
            return value
        try:
            return target(value)
        except ValueError as exc:
            valid_values = ", ".join(member.value for member in target)
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid value for '{name}': {value!r}. Expected one of: {valid_values}.",
                }
            ) from exc

    if target in (str, int, float, bool):
        if isinstance(value, target):
            return value
        try:
            return target(value)
        except (TypeError, ValueError) as exc:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid value for '{name}': {value!r}. Expected {_annotation_description(annotation)}.",
                }
            ) from exc

    return value


def build_utility_kwargs(
    utility_callable: Any,
    parameters: dict[str, Any],
    timeout_seconds: int | None,
) -> dict[str, Any]:
    signature = inspect.signature(utility_callable)
    utility_kwargs: dict[str, Any] = {}
    required_parameters: list[str] = []
    supported_parameters: list[str] = []

    for name, parameter in signature.parameters.items():
        if name in {"apisession", "site_id", "device_id", "on_message", "timeout"}:
            continue

        supported_parameters.append(name)
        if parameter.default is inspect.Signature.empty:
            required_parameters.append(name)

        if name in parameters:
            utility_kwargs[name] = _convert_parameter_value(
                name,
                parameters[name],
                parameter.annotation,
            )

    unknown_parameters = sorted(set(parameters) - set(supported_parameters))
    if unknown_parameters:
        supported = ", ".join(sorted(supported_parameters)) or "none"
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Unsupported parameters for this utility: {', '.join(unknown_parameters)}. Supported parameters: {supported}.",
            }
        )

    missing_parameters = sorted(set(required_parameters) - set(utility_kwargs))
    if missing_parameters:
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Missing required parameters for this utility: {', '.join(missing_parameters)}.",
            }
        )

    if "timeout" in signature.parameters and timeout_seconds is not None:
        if timeout_seconds <= 0:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "'timeout_seconds' must be greater than 0.",
                }
            )
        utility_kwargs["timeout"] = timeout_seconds

    return utility_kwargs


def _describe_device_utility(name: str, utility_callable: Any) -> dict[str, Any]:
    signature = inspect.signature(utility_callable)
    parameters: list[dict[str, Any]] = []

    for parameter_name, parameter in signature.parameters.items():
        if parameter_name in {
            "apisession",
            "site_id",
            "device_id",
            "on_message",
            "timeout",
        }:
            continue

        parameter_description: dict[str, Any] = {
            "name": parameter_name,
            "required": parameter.default is inspect.Signature.empty,
            "type": _annotation_description(parameter.annotation),
        }
        if parameter.default is not inspect.Signature.empty:
            parameter_description["default"] = parameter.default
        parameters.append(parameter_description)

    return {
        "name": name,
        "requires_write_tools": name in MUTATING_DEVICE_UTILITIES,
        "requires_elicitation": name in DISRUPTIVE_DEVICE_UTILITIES,
        "parameters": parameters,
        "timeout_parameter": "timeout_seconds"
        if "timeout" in signature.parameters
        else None,
    }


def describe_supported_device_utilities(
    device_type: DeviceUtilityType,
) -> dict[str, Any]:
    device_utilities = SUPPORTED_DEVICE_UTILITIES[device_type]
    return {
        "device_type": device_type.value,
        "usage": {
            "site_id": "Required when executing a utility.",
            "device_id": "Required when executing a utility. Retrieve it with mist_search_device.",
            "parameters": "Pass utility-specific arguments as a JSON object.",
            "timeout_seconds": "Optional. Overrides the underlying websocket utility timeout when supported.",
        },
        "utilities": [
            _describe_device_utility(name, utility_callable)
            for name, utility_callable in device_utilities.items()
            if name not in EXCLUDED_DEVICE_UTILITIES
        ],
    }


def _resolve_utility(
    device_type: DeviceUtilityType,
    utility: str,
) -> tuple[str, Any]:
    device_utilities = SUPPORTED_DEVICE_UTILITIES[device_type]
    if utility in device_utilities:
        return utility, device_utilities[utility]

    lookup = {
        _normalize_utility_name(name): name
        for name in device_utilities
        if name not in EXCLUDED_DEVICE_UTILITIES
    }
    canonical_name = lookup.get(_normalize_utility_name(utility))
    if canonical_name is None:
        available = ", ".join(device_utilities)
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Unsupported utility '{utility}' for device_type '{device_type.value}'. Supported utilities: {available}.",
            }
        )
    return canonical_name, device_utilities[canonical_name]


async def _wait_for_device_utility(
    ctx: Context,
    utility_name: str,
    utility_response: Any,
) -> bool:
    started_at = time.monotonic()
    deadline = started_at + UTILITY_WAIT_TIMEOUT_SECONDS

    while not getattr(utility_response, "ws_required", False):
        if utility_response.done:
            await ctx.report_progress(
                100, 100, f"Device utility '{utility_name}' completed"
            )
            return True
        if time.monotonic() >= deadline:
            utility_response.disconnect()
            await ctx.warning(
                f"Device utility '{utility_name}' did not start streaming before the wait deadline. Returning partial output."
            )
            await ctx.report_progress(
                100,
                100,
                f"Device utility '{utility_name}' completed",
            )
            return False

        elapsed = time.monotonic() - started_at
        progress = 5 + int((elapsed / UTILITY_WAIT_TIMEOUT_SECONDS) * 10)
        await ctx.report_progress(
            min(progress, 15),
            100,
            f"Waiting for '{utility_name}' trigger response",
        )
        await asyncio.sleep(0.25)

    while not utility_response.done and time.monotonic() < deadline:
        elapsed = time.monotonic() - started_at
        progress = 10 + int((elapsed / UTILITY_WAIT_TIMEOUT_SECONDS) * 85)
        await ctx.report_progress(
            min(progress, 95),
            100,
            f"Waiting for '{utility_name}' websocket output",
        )
        await asyncio.sleep(2)

    completed = utility_response.done
    if not completed:
        utility_response.disconnect()
        await ctx.warning(
            f"Device utility '{utility_name}' did not close before the wait deadline. Returning partial output."
        )

    await ctx.report_progress(
        100,
        100,
        f"Device utility '{utility_name}' completed",
    )
    return completed


def _format_device_utility_result(
    device_type: DeviceUtilityType,
    utility_name: str,
    site_id: UUID,
    device_id: UUID,
    utility_response: Any,
    completed: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "device_type": device_type.value,
        "utility": utility_name,
        "site_id": str(site_id),
        "device_id": str(device_id),
        "completed": completed,
        "websocket_stream": bool(getattr(utility_response, "ws_required", False)),
        "trigger_response": utility_response.trigger_api_response.data,
        "stream_output": list(getattr(utility_response, "ws_data", [])),
    }

    if result["stream_output"] and all(
        isinstance(item, str) for item in result["stream_output"]
    ):
        result["stream_output_text"] = "\n".join(result["stream_output"])

    if not completed:
        result["message"] = (
            "The device utility did not close cleanly before the wait deadline. "
            "Partial output may be returned."
        )

    return result


def _serialize_output(
    output: dict[str, Any], response_format: str
) -> dict[str, Any] | str:
    if response_format == "string":
        return json.dumps(output, indent=2, default=str)
    return output


async def _confirm_disruptive_utility(
    ctx: Context,
    device_type: DeviceUtilityType,
    utility_name: str,
    device_id: UUID,
) -> dict[str, str] | None:
    try:
        elicitation_response = await config_elicitation_handler(
            message=(
                f"The LLM wants to run the disruptive device utility '{utility_name}' "
                f"on {device_type.value} device {device_id}. This may disrupt live traffic or active sessions. "
                "Do you accept to trigger the API call?"
            ),
            ctx=ctx,
        )
    except Exception as exc:
        raise ToolError(
            {
                "status_code": 400,
                "message": (
                    "AI App does not support elicitation. You cannot use it to "
                    "run disruptive device utilities. Please use the Mist API "
                    "directly or use an AI App with elicitation support."
                ),
            }
        ) from exc

    if elicitation_response.action == "decline":
        return {"message": "Action declined by user."}
    if elicitation_response.action == "cancel":
        return {"message": "Action canceled by user."}
    return None


async def run_utilities(
    ctx: Context,
    device_type: DeviceUtilityType,
    utility: str | None,
    site_id: UUID | None,
    device_id: UUID | None,
    parameters: dict[str, Any] | None,
    timeout_seconds: int | None,
) -> dict[str, Any] | str:
    if utility is None:
        return _serialize_output(
            describe_supported_device_utilities(device_type),
            config.response_format,
        )

    if site_id is None or device_id is None:
        raise ToolError(
            {
                "status_code": 400,
                "message": "'site_id' and 'device_id' are required when executing a device utility.",
            }
        )

    canonical_utility, utility_callable = _resolve_utility(
        device_type, utility)
    if canonical_utility in MUTATING_DEVICE_UTILITIES and not config.enable_write_tools:
        raise ToolError(
            {
                "status_code": 403,
                "message": f"Utility '{canonical_utility}' modifies device state and is disabled unless the server is started with --enable-write-tools.",
            }
        )
    if canonical_utility in DISRUPTIVE_DEVICE_UTILITIES:
        confirmation_result = await _confirm_disruptive_utility(
            ctx,
            device_type,
            canonical_utility,
            device_id,
        )
        if confirmation_result is not None:
            return confirmation_result

    apisession, response_format = await get_apisession()
    parameters = parameters or {}

    logger.debug(
        "Tool utilities called for device_type=%s utility=%s site_id=%s device_id=%s parameters=%s timeout_seconds=%s",
        device_type.value,
        canonical_utility,
        site_id,
        device_id,
        parameters,
        timeout_seconds,
    )

    try:
        utility_kwargs = build_utility_kwargs(
            utility_callable,
            parameters,
            timeout_seconds,
        )
        await ctx.info(
            f"Running device utility '{canonical_utility}' on {device_type.value}. Some commands stream over WebSocket and may take up to about a minute."
        )
        await ctx.report_progress(5, 100, f"Triggered '{canonical_utility}'")
        utility_response = await asyncio.to_thread(
            utility_callable,
            apisession,
            str(site_id),
            str(device_id),
            **utility_kwargs,
        )
        completed = await _wait_for_device_utility(
            ctx,
            canonical_utility,
            utility_response,
        )
        if getattr(utility_response, "trigger_api_response", None) is None:
            raise ToolError(
                {
                    "status_code": 503,
                    "message": "The device utility did not return a trigger response from Mist.",
                }
            )
        await process_response(utility_response.trigger_api_response)
        output = _format_device_utility_result(
            device_type,
            canonical_utility,
            site_id,
            device_id,
            utility_response,
            completed,
        )
        return _serialize_output(output, response_format)
    except ToolError:
        raise
    except Exception as exc:
        await handle_network_error(exc)
        raise AssertionError("unreachable") from exc


@mcp.tool(
    name="mist_utilities",
    description="""Run device-side Mist utilities for AP, EX, SRX, and SSR devices. Call this tool with `device_type` only to list the supported utilities and their extra parameters for that platform. To execute a utility, set `utility`, `site_id`, `device_id`, and pass any utility-specific arguments inside `parameters`. State-changing utilities require the server to be started with write tools enabled. Utilities that may disrupt live traffic or active sessions also trigger elicitation confirmation before the API call is sent. This tool sets a longer MCP timeout because many device utilities stream their result over WebSocket and can take some time to finish.""",
    tags={"utilities"},
    timeout=UTILITY_TOOL_TIMEOUT_SECONDS,
    annotations={
        "title": "Device utilities",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": True,
        "idempotentHint": False,
    },
)
async def utilities(
    device_type: Annotated[
        DeviceUtilityType,
        Field(
            description="""Device platform to target. Use `ap`, `ex`, `srx`, or `ssr`."""
        ),
    ],
    utility: Annotated[
        str | None,
        Field(
            description="""Utility name to execute for the selected device platform. Leave this empty to list the supported utilities and required parameters for that platform. Examples: `ping`, `traceroute`, `retrieveArpTable`, `retrieveBgpSummary`, `retrieveRoutes`, `showServicePath`, `bouncePort`, `cableTest`.""",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID | None,
        Field(
            description="""Site ID of the target device. Required when `utility` is set.""",
            default=None,
        ),
    ],
    device_id: Annotated[
        UUID | None,
        Field(
            description="""Device ID of the target device. Required when `utility` is set. Retrieve it with `mist_search_device`.""",
            default=None,
        ),
    ],
    parameters: Annotated[
        dict[str, Any] | None,
        Field(
            description="""Utility-specific arguments as a JSON object. Examples: {"host": "8.8.8.8"}, {"port_ids": ["ge-0/0/1"]}, {"protocol": "udp", "port": 33434}, {"node": "node0", "service_name": "internet"}.""",
            default=None,
        ),
    ],
    timeout_seconds: Annotated[
        int | None,
        Field(
            description="""Optional websocket command timeout in seconds. This is passed to the underlying mistapi utility when supported.""",
            default=None,
        ),
    ],
    ctx: Context,
) -> dict[str, Any] | str:
    return await run_utilities(
        ctx,
        device_type,
        utility,
        site_id,
        device_id,
        parameters,
        timeout_seconds,
    )
