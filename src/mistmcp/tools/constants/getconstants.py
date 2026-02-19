"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import mcp

from pydantic import Field
from typing import Annotated
from enum import Enum


class Object_type(Enum):
    FINGERPRINT_TYPES = "fingerprint_types"
    INSIGHT_METRICS = "insight_metrics"
    LICENSE_TYPES = "license_types"
    WEBHOOK_TOPICS = "webhook_topics"
    DEVICE_MODELS = "device_models"
    MXEDGE_MODELS = "mxedge_models"
    ALARM_DEFINITIONS = "alarm_definitions"
    CLIENT_EVENTS = "client_events"
    MXEDGE_EVENTS = "mxedge_events"
    NAC_EVENTS = "nac_events"


@mcp.tool(
    name="getConstants",
    description="""Get Mist Constants (insight metrics, webhook topics, alarm definitions, ...)""",
    tags={"constants"},
    annotations={
        "title": "getConstants",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getConstants(
    object_type: Annotated[
        Object_type, Field(description="""Type of object to retrieve metrics for.""")
    ],
    ctx: Context | None = None,
) -> dict | list | str:
    """Get Mist Constants (insight metrics, webhook topics, alarm definitions, ...)"""

    apisession, response_format = get_apisession()
    data = {}

    match object_type.value:
        case "fingerprint_types":
            response = mistapi.api.v1.const.fingerprint_types.listFingerprintTypes(
                apisession
            )
            await process_response(response)
            data = response.data
        case "insight_metrics":
            response = mistapi.api.v1.const.insight_metrics.listInsightMetrics(
                apisession
            )
            await process_response(response)
            data = response.data
        case "license_types":
            response = mistapi.api.v1.const.license_types.listLicenseTypes(apisession)
            await process_response(response)
            data = response.data
        case "webhook_topics":
            response = mistapi.api.v1.const.webhook_topics.listWebhookTopics(apisession)
            await process_response(response)
            data = response.data
        case "device_models":
            response = mistapi.api.v1.const.device_models.listDeviceModels(apisession)
            await process_response(response)
            data = response.data
        case "mxedge_models":
            response = mistapi.api.v1.const.mxedge_models.listMxEdgeModels(apisession)
            await process_response(response)
            data = response.data
        case "alarm_definitions":
            response = mistapi.api.v1.const.alarm_defs.listAlarmDefinitions(apisession)
            await process_response(response)
            data = response.data
        case "client_events":
            response = mistapi.api.v1.const.client_events.listClientEventsDefinitions(
                apisession
            )
            await process_response(response)
            data = response.data
        case "mxedge_events":
            response = mistapi.api.v1.const.mxedge_events.listMxEdgeEventsDefinitions(
                apisession
            )
            await process_response(response)
            data = response.data
        case "nac_events":
            response = mistapi.api.v1.const.nac_events.listNacEventsDefinitions(
                apisession
            )
            await process_response(response)
            data = response.data

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    if response_format == "string":
        return json.dumps(data)
    else:
        return data
