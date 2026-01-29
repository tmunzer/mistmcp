"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
from enum import Enum
from typing import Annotated

import mistapi
from fastmcp.exceptions import ClientError, NotFoundError, ToolError
from fastmcp.server.dependencies import get_context, get_http_request

# from mistmcp.server_factory import mcp
from pydantic import Field
from starlette.requests import Request

from mistmcp.config import config
from mistmcp.server_factory import mcp_instance

mcp = mcp_instance.get()


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
    enabled=False,
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
) -> dict | list:
    """Get Mist Constants (insight metrics, webhook topics, alarm definitions, ...)"""

    ctx = get_context()
    if config.transport_mode == "http":
        try:
            request: Request = get_http_request()
            cloud = request.query_params.get("cloud", None)
            apitoken = request.headers.get("X-Authorization", None)
        except NotFoundError as exc:
            raise ClientError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from exc
        if not cloud or not apitoken:
            raise ClientError(
                "Missing required parameters: 'cloud' and 'X-Authorization' header"
            )
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    if not apitoken:
        raise ClientError(
            "Missing required parameter: 'X-Authorization' header or mist_apitoken in config"
        )
    if not cloud:
        raise ClientError(
            "Missing required parameter: 'cloud' query parameter or mist_host in config"
        )

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    match object_type.value:
        case "fingerprint_types":
            response = mistapi.api.v1.const.fingerprint_types.listFingerprintTypes(
                apisession
            )
        case "insight_metrics":
            response = mistapi.api.v1.const.insight_metrics.listInsightMetrics(
                apisession
            )
        case "license_types":
            response = mistapi.api.v1.const.license_types.listLicenseTypes(apisession)
        case "webhook_topics":
            response = mistapi.api.v1.const.webhook_topics.listWebhookTopics(apisession)
        case "device_models":
            response = mistapi.api.v1.const.device_models.listDeviceModels(apisession)
        case "mxedge_models":
            response = mistapi.api.v1.const.mxedge_models.listMxEdgeModels(apisession)
        case "alarm_definitions":
            response = mistapi.api.v1.const.alarm_defs.listAlarmDefinitions(apisession)
        case "client_events":
            response = mistapi.api.v1.const.client_events.listClientEventsDefinitions(
                apisession
            )
        case "mxedge_events":
            response = mistapi.api.v1.const.mxedge_events.listMxEdgeEventsDefinitions(
                apisession
            )
        case "nac_events":
            response = mistapi.api.v1.const.nac_events.listNacEventsDefinitions(
                apisession
            )

        case _:
            raise ToolError(
                {
                    "status_code": 400,
                    "message": f"Invalid object_type: {object_type.value}. Valid values are: {[e.value for e in Object_type]}",
                }
            )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            # await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            api_error["message"] = json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given"
            )
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Not found. The API endpoint doesn't exist or resource doesn't exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    data = []
    for item in response.data:
        if isinstance(item, dict) and "example" in item:
            del item["example"]
        data.append(item)

    return data
