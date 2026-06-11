# Template for individual tool files
UTILITIES_TEMPLATE = '''
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
from types import NoneType, SimpleNamespace, UnionType
from typing import Annotated, Any, Union, get_args, get_origin
from uuid import UUID

from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistapi.device_utils.__tools.__ws_wrapper import UtilResponse, WebSocketWrapper
from mistapi.device_utils import ap as ap_utils
from mistapi.device_utils import ex as ex_utils
from mistapi.device_utils import srx as srx_utils
from mistapi.device_utils import ssr as ssr_utils
from mistapi.websockets.sites import DeviceCmdEvents
from pydantic import Field

from mistmcp.config import config
from mistmcp.elicitation_processor import config_elicitation_handler
from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp

UTILITY_TOOL_TIMEOUT_SECONDS = 120.0
UTILITY_WAIT_TIMEOUT_SECONDS = 75.0
UTILITY_DEFAULT_FOREGROUND_WAIT_SECONDS = 3.0
UTILITY_STREAM_POLL_SECONDS = 0.25
UTILITY_DRAIN_SHUTDOWN_SECONDS = 0.2
UTILITY_SESSION_RETENTION_SECONDS = 600.0
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
UTILITY_SESSION_STORE: dict[str, dict[str, Any]] = {}


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


def _build_example_value(name: str, annotation: Any) -> Any:
    target = _strip_optional(annotation)
    origin = get_origin(target)

    if inspect.isclass(target) and issubclass(target, Enum):
        return next(iter(target)).value

    if origin is list:
        inner_type = get_args(target)[0] if get_args(target) else Any
        return [_build_example_value(name, inner_type)]

    if target is bool:
        return True
    if target is int:
        return 1
    if target is float:
        return 1.0
    if target is str:
        lowered_name = name.lower()
        if "host" in lowered_name:
            return "8.8.8.8"
        if "port_id" in lowered_name:
            return "ge-0/0/1"
        if "node" in lowered_name:
            return "node0"
        if "service" in lowered_name:
            return "internet"
        if "protocol" in lowered_name:
            return "udp"
        return "value"

    return "value"


def _format_default_value(default: Any, annotation: Any) -> Any:
    if default is None:
        return None

    target = _strip_optional(annotation)
    if (
        inspect.isclass(target)
        and issubclass(target, Enum)
        and isinstance(default, target)
    ):
        return default.value
    return default


def _build_parameters_field_description() -> str:
    lines = ["Utility-specific arguments as a JSON object."]

    utility_names = sorted(
        {
            utility_name
            for device_utilities in SUPPORTED_DEVICE_UTILITIES.values()
            for utility_name in device_utilities
            if utility_name not in EXCLUDED_DEVICE_UTILITIES
        }
    )
    lines.append(f"Supported utilities: {', '.join(utility_names)}.")
    lines.append("Parameter schemas (deduplicated by utility signature):")

    grouped_schemas: dict[tuple[str, tuple[tuple[Any, ...], ...]], dict[str, Any]] = {}

    for device_type, device_utilities in SUPPORTED_DEVICE_UTILITIES.items():
        for utility_name, utility_callable in device_utilities.items():
            if utility_name in EXCLUDED_DEVICE_UTILITIES:
                continue

            signature = inspect.signature(utility_callable)
            parameter_descriptions: list[str] = []
            signature_parts: list[tuple[Any, ...]] = []
            example_payload: dict[str, Any] = {}

            for parameter_name, parameter in signature.parameters.items():
                if parameter_name in {
                    "apisession",
                    "site_id",
                    "device_id",
                    "on_message",
                    "timeout",
                }:
                    continue

                annotation = parameter.annotation
                type_description = _annotation_description(annotation)
                required = parameter.default is inspect.Signature.empty
                requirement_text = "required" if required else "optional"
                default_value = None
                if parameter.default is not inspect.Signature.empty:
                    default_value = _format_default_value(parameter.default, annotation)

                details = f"{parameter_name} ({type_description}, {requirement_text})"
                if default_value is not None:
                    details += f", default={default_value}"
                parameter_descriptions.append(details)

                signature_parts.append(
                    (parameter_name, type_description, required, default_value)
                )

                if required:
                    example_payload[parameter_name] = _build_example_value(
                        parameter_name,
                        annotation,
                    )

            schema_key = (utility_name, tuple(signature_parts))
            schema_data = grouped_schemas.setdefault(
                schema_key,
                {
                    "utility_name": utility_name,
                    "parameters": parameter_descriptions,
                    "example": example_payload,
                    "device_types": set(),
                },
            )
            schema_data["device_types"].add(device_type.value)

    sorted_schema_items = sorted(
        grouped_schemas.values(),
        key=lambda item: (item["utility_name"], sorted(item["device_types"])),
    )

    for item in sorted_schema_items:
        utility_name = item["utility_name"]
        device_types = ", ".join(sorted(item["device_types"]))
        parameter_descriptions = item["parameters"]
        example_payload = item["example"]

        if not parameter_descriptions:
            lines.append(
                f"- {utility_name} [{device_types}]: no parameters. Example: {{}}"
            )
            continue

        parameter_summary = "; ".join(parameter_descriptions)
        example_text = json.dumps(example_payload, ensure_ascii=True)
        lines.append(
            f"- {utility_name} [{device_types}]: {parameter_summary}. "
            f"Example: `{example_text}`"
        )

    return "\n".join(lines)


PARAMETERS_FIELD_DESCRIPTION = _build_parameters_field_description()


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
            "timeout_seconds": "Optional. Overrides the underlying device/WebSocket idle timeout when supported; high values can delay completed=true.",
            "wait_seconds": "Optional. Controls how long the MCP foreground request waits for streaming output before returning partial output.",
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


def _get_utility_session_keys(utility_response: Any) -> list[str]:
    trigger_response = getattr(utility_response, "trigger_api_response", None)
    trigger_data = getattr(trigger_response, "data", None)
    if not isinstance(trigger_data, dict):
        return []

    keys: list[str] = []
    session_id = trigger_data.get("session")
    capture_id = trigger_data.get("id")
    if session_id:
        keys.append(str(session_id))
    if capture_id:
        keys.append(str(capture_id))
    return keys


def _cleanup_utility_session_store() -> None:
    now = time.monotonic()
    expired_records = {
        id(record): record
        for record in UTILITY_SESSION_STORE.values()
        if now - record["updated_at"] > UTILITY_SESSION_RETENTION_SECONDS
    }
    if not expired_records:
        return

    expired_keys = [
        key
        for key, record in UTILITY_SESSION_STORE.items()
        if id(record) in expired_records
    ]
    for key in expired_keys:
        UTILITY_SESSION_STORE.pop(key, None)
    for record in expired_records.values():
        if not record["response"].done:
            record["response"].disconnect()


def _store_device_utility_session(
    device_type: DeviceUtilityType,
    utility_name: str,
    site_id: UUID,
    device_id: UUID,
    utility_response: Any,
) -> bool:
    keys = _get_utility_session_keys(utility_response)
    if not keys:
        return False

    _cleanup_utility_session_store()
    record = {
        "device_type": device_type,
        "utility_name": utility_name,
        "site_id": site_id,
        "device_id": device_id,
        "response": utility_response,
        "updated_at": time.monotonic(),
    }
    for key in keys:
        UTILITY_SESSION_STORE[key] = record
    return True


def _get_stored_device_utility_session(
    session_id: str | None,
    capture_id: str | None,
) -> dict[str, Any] | None:
    _cleanup_utility_session_store()
    for key in (session_id, capture_id):
        if key and key in UTILITY_SESSION_STORE:
            record = UTILITY_SESSION_STORE[key]
            record["updated_at"] = time.monotonic()
            return record
    return None


async def _wait_for_device_utility(
    ctx: Context,
    utility_name: str,
    utility_response: Any,
    wait_seconds: float | None = None,
    stream_from_index: int = 0,
    keep_alive_on_timeout: bool = False,
) -> bool:
    started_at = time.monotonic()
    effective_wait_seconds = (
        min(UTILITY_DEFAULT_FOREGROUND_WAIT_SECONDS, UTILITY_WAIT_TIMEOUT_SECONDS)
        if wait_seconds is None
        else max(wait_seconds, 0.0)
    )
    progress_denominator = max(effective_wait_seconds, 1.0)
    deadline = started_at + effective_wait_seconds

    # Phase 1: wait for the trigger response / WS flag
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
        progress = 5 + int((elapsed / progress_denominator) * 10)
        await ctx.report_progress(
            min(progress, 15),
            100,
            f"Waiting for '{utility_name}' trigger response",
        )
        await asyncio.sleep(0.25)

    msg_count = 0
    seen_count = max(stream_from_index, 0)

    while time.monotonic() < deadline:
        stream_output = list(getattr(utility_response, "ws_data", []))
        if len(stream_output) > seen_count:
            for msg in stream_output[seen_count:]:
                msg_count += 1
                await ctx.info(f"[{utility_name}] {msg}")
            seen_count = len(stream_output)

            elapsed = time.monotonic() - started_at
            progress = 10 + int((elapsed / progress_denominator) * 85)
            await ctx.report_progress(
                min(progress, 95),
                100,
                f"Received {msg_count} message(s) from '{utility_name}'",
            )
        elif utility_response.done:
            break

        elapsed = time.monotonic() - started_at
        progress = 10 + int((elapsed / progress_denominator) * 85)
        await ctx.report_progress(
            min(progress, 95),
            100,
            f"Waiting for '{utility_name}' output",
        )
        await asyncio.sleep(UTILITY_STREAM_POLL_SECONDS)

    completed = utility_response.done
    if not completed:
        if not (keep_alive_on_timeout and _get_utility_session_keys(utility_response)):
            utility_response.disconnect()
        await ctx.warning(
            f"Device utility '{utility_name}' is still running after "
            f"{effective_wait_seconds:g}s. Returning partial output."
        )

    await ctx.report_progress(
        100,
        100,
        (
            f"Device utility '{utility_name}' completed ({msg_count} message(s))"
            if completed
            else f"Device utility '{utility_name}' foreground wait expired ({msg_count} message(s))"
        ),
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
            "The device utility did not close before the foreground wait deadline. "
            "Partial output may be returned."
        )

    return result


def _open_device_utility_session_response(
    apisession: Any,
    site_id: UUID,
    device_id: UUID,
    session_id: str,
    capture_id: str | None,
    timeout_seconds: int | None,
) -> Any:
    trigger_data = {"session": session_id}
    if capture_id:
        trigger_data["id"] = capture_id

    utility_response = UtilResponse()
    utility_response.trigger_api_response = SimpleNamespace(
        status_code=200,
        data=trigger_data,
    )
    websocket_timeout = timeout_seconds or 10
    return WebSocketWrapper(
        apisession,
        utility_response,
        timeout=websocket_timeout,
        max_duration=max(websocket_timeout, int(UTILITY_TOOL_TIMEOUT_SECONDS)),
    ).start(
        DeviceCmdEvents(
            apisession,
            site_id=str(site_id),
            device_ids=[str(device_id)],
        )
    )


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
    wait_seconds: float | None = None,
    session_id: str | None = None,
    capture_id: str | None = None,
) -> dict[str, Any] | str:
    if session_id or capture_id:
        if site_id is None or device_id is None:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": "'site_id' and 'device_id' are required when reading a device utility session.",
                }
            )
        return await run_read_utility_session(
            ctx,
            device_type,
            utility,
            site_id,
            device_id,
            session_id or "",
            capture_id,
            wait_seconds,
            timeout_seconds,
        )

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

    canonical_utility, utility_callable = _resolve_utility(device_type, utility)
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
        "Tool utilities called for device_type=%s utility=%s site_id=%s device_id=%s parameters=%s timeout_seconds=%s wait_seconds=%s",
        device_type.value,
        canonical_utility,
        site_id,
        device_id,
        parameters,
        timeout_seconds,
        wait_seconds,
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
            wait_seconds,
            keep_alive_on_timeout=True,
        )
        if getattr(utility_response, "trigger_api_response", None) is None:
            raise ToolError(
                {
                    "status_code": 503,
                    "message": "The device utility did not return a trigger response from Mist.",
                }
            )
        await process_response(utility_response.trigger_api_response)
        stored_session = False
        if not completed:
            stored_session = _store_device_utility_session(
                device_type,
                canonical_utility,
                site_id,
                device_id,
                utility_response,
            )
        output = _format_device_utility_result(
            device_type,
            canonical_utility,
            site_id,
            device_id,
            utility_response,
            completed,
        )
        if stored_session:
            output["session_buffered"] = True
            output["message"] = (
                "Returned partial output after the foreground wait deadline. "
                "The MCP server is still buffering this utility session; use "
                "`mist_utilities` with `session_id=trigger_response.session` to read more output."
            )
        return _serialize_output(output, response_format)
    except ToolError:
        raise
    except Exception as exc:
        await handle_network_error(exc)
        raise AssertionError("unreachable") from exc


async def run_read_utility_session(
    ctx: Context,
    device_type: DeviceUtilityType,
    utility: str | None,
    site_id: UUID,
    device_id: UUID,
    session_id: str,
    capture_id: str | None,
    wait_seconds: float | None,
    timeout_seconds: int | None,
) -> dict[str, Any] | str:
    if not session_id and not capture_id:
        raise ToolError(
            {
                "status_code": 400,
                "message": "'session_id' or 'capture_id' is required to read a utility session.",
            }
        )

    apisession, response_format = await get_apisession()
    utility_name = utility or "utility_session"

    logger.debug(
        "Tool read utility session called for device_type=%s utility=%s site_id=%s device_id=%s session_id=%s capture_id=%s wait_seconds=%s timeout_seconds=%s",
        device_type.value,
        utility_name,
        site_id,
        device_id,
        session_id,
        capture_id,
        wait_seconds,
        timeout_seconds,
    )

    try:
        stored_session = _get_stored_device_utility_session(session_id, capture_id)
        stream_from_index = 0
        if stored_session is not None:
            utility_response = stored_session["response"]
            utility_name = utility or stored_session["utility_name"]
            stream_from_index = len(getattr(utility_response, "ws_data", []))
            await ctx.info(
                f"Reading buffered device utility session '{session_id or capture_id}' on {device_type.value}."
            )
            await ctx.report_progress(5, 100, "Reading buffered utility session")
        else:
            await ctx.info(
                f"Reading active device utility session '{session_id or capture_id}' on {device_type.value}."
            )
            await ctx.report_progress(5, 100, "Connecting to device utility session")
            utility_response = await asyncio.to_thread(
                _open_device_utility_session_response,
                apisession,
                site_id,
                device_id,
                session_id,
                capture_id,
                timeout_seconds,
            )
        completed = await _wait_for_device_utility(
            ctx,
            utility_name,
            utility_response,
            wait_seconds,
            stream_from_index=stream_from_index,
            keep_alive_on_timeout=stored_session is not None,
        )
        output = _format_device_utility_result(
            device_type,
            utility_name,
            site_id,
            device_id,
            utility_response,
            completed,
        )
        if stored_session is not None:
            output["session_buffered"] = True
        if not output.get("stream_output"):
            output["message"] = (
                "No output was received while reading this utility session. "
                "The session may have already completed, or the MCP wait window may have expired before new events arrived."
            )
        return _serialize_output(output, response_format)
    except ToolError:
        raise
    except Exception as exc:
        await handle_network_error(exc)
        raise AssertionError("unreachable") from exc


@mcp.tool(
    name="mist_utilities",
    description="""Run or continue device-side Mist utilities for AP, EX, SRX, and SSR devices. Call this tool with `device_type` only to list the supported utilities and their extra parameters for that platform. To start a utility, set `utility`, `site_id`, `device_id`, and pass any utility-specific arguments inside `parameters`. To continue reading a previous streaming utility, provide the same `device_type`, `site_id`, and `device_id`, plus `session_id` from the prior result's `trigger_response.session`; provide `capture_id` from `trigger_response.id` when present. State-changing utilities require the server to be started with write tools enabled. Utilities that may disrupt live traffic or active sessions also trigger elicitation confirmation before the API call is sent. Utilities such as `ping` and `traceroute` stream output over WebSocket; by default the tool returns partial output quickly to avoid MCP client request timeouts, and that short default is often not enough for a complete diagnostic result. `wait_seconds` controls how long this MCP tool call waits for foreground WebSocket output and must be lower than the MCP client/request timeout. Some clients time out after only a few seconds, so use a small value such as 3-5 when you need a quick partial result. Use 30-60 seconds only when the MCP client is configured to allow long-running tool calls. A result with `completed: false` can be normal when `wait_seconds` expires and partial output is returned; it does not necessarily mean the utility failed. If a full result is required and the MCP client timeout is short, repeat this tool with `session_id` to read the MCP server's buffered output from the original utility WebSocket in follow-up calls. Buffered sessions are in-memory and only available on the same running MCP server process for a limited retention window. Use `timeout_seconds` separately to control the underlying device/WebSocket command timeout when supported; setting it high can keep the WebSocket open longer and delay `completed: true` even after useful output appears.""",
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
        str,
        Field(
            description="""Utility name to execute for the selected device platform. Leave this empty to list the supported utilities and required parameters for that platform, or when using `session_id` to continue a previous utility session. Examples: `ping`, `traceroute`, `retrieveArpTable`, `retrieveBgpSummary`, `retrieveRoutes`, `showServicePath`, `bouncePort`, `cableTest`.""",
            default=None,
        ),
    ],
    site_id: Annotated[
        UUID,
        Field(
            description="""Site ID of the target device. Required when `utility` is set.""",
            default=None,
        ),
    ],
    device_id: Annotated[
        UUID,
        Field(
            description="""Device ID of the target device. Required when `utility` is set. Retrieve it with `mist_search_device`.""",
            default=None,
        ),
    ],
    parameters: Annotated[
        dict[str, Any],
        Field(
            description=PARAMETERS_FIELD_DESCRIPTION,
            default=None,
        ),
    ],
    timeout_seconds: Annotated[
        int,
        Field(
            description="""Optional device/WebSocket command timeout in seconds. This is passed to the underlying mistapi utility when supported; it does not control how long the MCP request waits before returning partial output. Use `wait_seconds` for the foreground MCP wait. Larger values can keep the underlying WebSocket/session open longer and delay `completed: true`; avoid setting this high unless you need a longer device-side idle timeout.""",
            default=None,
        ),
    ],
    wait_seconds: Annotated[
        float,
        Field(
            description="""Optional number of seconds to keep the MCP request open while collecting streaming output. This must be lower than the MCP client/request timeout. Defaults to a short wait so long-running utilities return partial output before MCP clients cancel the request; this default is often not enough for complete ping/traceroute results. Use a small value such as 3-5 for quick partial output when the client timeout is short. Use 30-60 seconds only when the MCP client is configured to allow long-running tool calls. If this wait expires, `completed` may be false even though the returned partial output is valid and the utility did not necessarily fail.""",
            default=None,
        ),
    ],
    session_id: Annotated[
        str,
        Field(
            description="""Optional Mist utility session ID from a previous result's `trigger_response.session`. When provided, this tool continues reading that utility session instead of starting a new utility.""",
            default=None,
        ),
    ],
    capture_id: Annotated[
        str,
        Field(
            description="""Optional capture/session ID from a previous result's `trigger_response.id`, when present. Used with `session_id` to continue reading a utility session.""",
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
        wait_seconds,
        session_id,
        capture_id,
    )

'''
