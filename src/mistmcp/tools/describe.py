"""Platform-constant and configuration-schema discovery facade tool."""

from enum import Enum
from typing import Annotated, Any

import mistapi
from fastmcp.exceptions import ToolError
from fastmcp.tools import ToolResult
from pydantic import Field

from mistmcp.logger import logger
from mistmcp.request_processor import get_apisession
from mistmcp.response_formatter import format_response
from mistmcp.response_processor import handle_network_error, process_response
from mistmcp.server import mcp
from mistmcp.tools import schemas_data as _schemas_data_module
from mistmcp.tools._facade import internal_tool, run_internal_tool


class DescriptionSubject(Enum):
    CONSTANT = "constant"
    CONFIGURATION_SCHEMA = "configuration_schema"


class Object_type(Enum):
    FINGERPRINT_TYPES = "fingerprint_types"
    INSIGHT_METRICS = "insight_metrics"
    LICENSE_TYPES = "license_types"
    WEBHOOK_TOPICS = "webhook_topics"
    DEVICE_MODELS = "device_models"
    DEVICE_EVENTS = "device_events"
    MXEDGE_MODELS = "mxedge_models"
    ALARM_DEFINITIONS = "alarm_definitions"
    CLIENT_EVENTS = "client_events"
    MXEDGE_EVENTS = "mxedge_events"
    NAC_EVENTS = "nac_events"


async def get_constants(
    object_type: Annotated[
        Object_type,
        Field(
            description="Type of constant to retrieve: fingerprint_types, insight_metrics, license_types, webhook_topics, device_models, device_events, mxedge_models, alarm_definitions, client_events, mxedge_events, or nac_events"
        ),
    ],
) -> dict | list | str:
    """Retrieve Mist platform constants including insight metrics, webhook topics, alarm definitions, device models, events definitions, and license types. Use this to understand available options and configurations for the Mist API."""
    logger.debug("Tool get_constants called")
    logger.debug("Input Parameters: object_type: %s", object_type)
    apisession, response_format = await get_apisession()
    try:
        match object_type.value:
            case "fingerprint_types":
                response = mistapi.api.v1.const.fingerprint_types.listFingerprintTypes(
                    apisession
                )
                await process_response(response)
            case "insight_metrics":
                response = mistapi.api.v1.const.insight_metrics.listInsightMetrics(
                    apisession
                )
                await process_response(response)
            case "license_types":
                response = mistapi.api.v1.const.license_types.listLicenseTypes(
                    apisession
                )
                await process_response(response)
            case "webhook_topics":
                response = mistapi.api.v1.const.webhook_topics.listWebhookTopics(
                    apisession
                )
                await process_response(response)
            case "device_models":
                response = mistapi.api.v1.const.device_models.listDeviceModels(
                    apisession
                )
                await process_response(response)
            case "device_events":
                response = (
                    mistapi.api.v1.const.device_events.listDeviceEventsDefinitions(
                        apisession
                    )
                )
                await process_response(response)
            case "mxedge_models":
                response = mistapi.api.v1.const.mxedge_models.listMxEdgeModels(
                    apisession
                )
                await process_response(response)
            case "alarm_definitions":
                response = mistapi.api.v1.const.alarm_defs.listAlarmDefinitions(
                    apisession
                )
                await process_response(response)
            case "client_events":
                response = (
                    mistapi.api.v1.const.client_events.listClientEventsDefinitions(
                        apisession
                    )
                )
                await process_response(response)
            case "mxedge_events":
                response = (
                    mistapi.api.v1.const.mxedge_events.listMxEdgeEventsDefinitions(
                        apisession
                    )
                )
                await process_response(response)
            case "nac_events":
                response = mistapi.api.v1.const.nac_events.listNacEventsDefinitions(
                    apisession
                )
                await process_response(response)
            case _:
                raise ToolError(
                    {
                        "status_code": 400,
                        "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                    }
                )
    except ToolError:
        raise
    except Exception as _exc:
        await handle_network_error(_exc)
    return format_response(response, response_format)


_SCHEMAS_DATA: dict = _schemas_data_module.SCHEMAS_DATA
SchemaName = Enum("SchemaName", {name: name for name in _SCHEMAS_DATA})


def _compact_schema(schema: dict) -> dict:
    """Return a token-efficient summary of a JSON schema.

    Required fields are returned in full detail.  Optional fields are reduced
    to name, type, and description only — nested sub-schemas and constraint
    keywords are omitted.  A hint key tells the caller how to obtain the full
    schema.
    """
    required_fields: set = set(schema.get("required", []))
    properties: dict = schema.get("properties", {})
    compact_required: dict = {}
    compact_optional: dict = {}
    for field_name, field_schema in properties.items():
        if field_name in required_fields:
            compact_required[field_name] = field_schema
        else:
            compact_entry: dict = {}
            if field_schema.get("type"):
                compact_entry["type"] = field_schema["type"]
            if field_schema.get("description"):
                compact_entry["description"] = field_schema["description"]
            compact_optional[field_name] = compact_entry
    result: dict = {}
    for key, value in schema.items():
        if key != "properties":
            result[key] = value
    result["properties"] = {**compact_required, **compact_optional}
    optional_count = len(compact_optional)
    if optional_count:
        result["x-hint"] = (
            f"{optional_count} optional field(s) shown in compact form (name + type + description only). Pass verbose=True for full schema."
        )
    return result


async def get_configuration_object_schema(
    schema_name: Annotated[
        SchemaName,
        Field(description="Name of the configuration object schema to retrieve."),
    ],
    verbose: Annotated[
        bool,
        Field(
            description="Return the full schema with all constraints and nested sub-schemas. When False (default), returns a compact summary with required fields in full and optional fields as name+type+description only."
        ),
    ] = False,
) -> dict[str, Any] | str:
    """Retrieve the pre-resolved JSON schema for a Mist configuration object."""
    logger.debug("Tool get_configuration_object_schema called")
    logger.debug("Input Parameters: schema_name=%s, verbose=%s",
                 schema_name, verbose)
    entry = _SCHEMAS_DATA.get(schema_name.value)
    if entry is None:
        raise ValueError(
            f"Schema '{schema_name.value}' not found. Re-run the generator to rebuild schemas_data.py."
        )
    resolved: dict = dict(entry["schema"])
    if not resolved:
        raise ValueError(
            f"No schema found for '{schema_name.value}'. Re-run the generator to rebuild schemas_data.py."
        )
    resolved["x-schema-name"] = entry["_schema_name"]
    if not verbose:
        resolved = _compact_schema(resolved)
    return resolved


ConstantType = Object_type

_GET_CONSTANTS = internal_tool(get_constants)
_GET_CONFIGURATION_SCHEMA = internal_tool(get_configuration_object_schema)


@mcp.tool(
    name="mist_describe",
    description="""Discover Mist platform constants or configuration-object JSON schemas.

Choose `subject=constant` for platform values or `subject=configuration_schema` for
configuration-object schemas. Omit `name` to list every valid name for that subject.
Constants provide accepted values for fingerprint types, insight metrics, license
types, webhook topics, device and Mist Edge models, alarm definitions, and device,
client, Mist Edge, or NAC event types. Configuration schemas describe supported
fields before a write; use
`verbose=true` only for configuration schemas and only when the complete unabridged
schema is needed.""",
    tags={"constants"},
    annotations={
        "title": "Describe Mist metadata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
        "idempotentHint": True,
    },
)
async def describe(
    subject: Annotated[
        DescriptionSubject,
        Field(
            description="Whether to retrieve a platform constant or configuration schema."
        ),
    ],
    name: Annotated[
        str,
        Field(
            description="Constant type or configuration schema name to retrieve. Omit to list valid names.",
            default=None,
        ),
    ],
    verbose: Annotated[
        bool,
        Field(
            description="Return the full configuration schema instead of its compact form."
        ),
    ],
) -> ToolResult | dict[str, list[str]]:
    if name is None:
        names = (
            [item.value for item in ConstantType]
            if subject is DescriptionSubject.CONSTANT
            else [item.value for item in SchemaName]
        )
        return {"subject": subject.value, "names": names}
    if subject is DescriptionSubject.CONSTANT:
        return await run_internal_tool(_GET_CONSTANTS, {"object_type": name})
    return await run_internal_tool(
        _GET_CONFIGURATION_SCHEMA,
        {"schema_name": name, "verbose": verbose},
    )
