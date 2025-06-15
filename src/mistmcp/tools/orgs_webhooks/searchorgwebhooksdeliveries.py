""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import json
import mistapi
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError
from starlette.requests import Request
from mistmcp.server_factory import _CURRENT_MCP_INSTANCE as mcp
from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


class Status(Enum):
    FAILURE = "failure"
    SUCCESS = "success"
    NONE = None


class Topic(Enum):
    ALARMS = "alarms"
    AUDITS = "audits"
    DEVICE_UPDOWNS = "device-updowns"
    OCCUPANCY_ALERTS = "occupancy-alerts"
    PING = "ping"
    NONE = None


@mcp.tool(
    enabled=True,
    name="searchOrgWebhooksDeliveries",
    description="""Search Org Webhooks deliveriesTopics Supported:- alarms- audits- device-updowns- occupancy-alerts- ping""",
    tags={"Orgs Webhooks"},
    annotations={
        "title": "searchOrgWebhooksDeliveries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgWebhooksDeliveries(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    webhook_id: Annotated[UUID, Field(description="""ID of the Mist Webhook""")],
    error: Optional[str] = None,
    status_code: Optional[int] = None,
    status: Annotated[
        Status, Field(description="""Webhook delivery status""")
    ] = Status.NONE,
    topic: Annotated[Topic, Field(description="""Webhook topic""")] = Topic.NONE,
    start: Annotated[
        Optional[int],
        Field(
            description="""Start datetime, can be epoch or relative time like -1d, -1w; -1d if not specified"""
        ),
    ] = None,
    end: Annotated[
        Optional[int],
        Field(
            description="""End datetime, can be epoch or relative time like -1d, -2h; now if not specified"""
        ),
    ] = None,
    duration: Annotated[
        str, Field(description="""Duration like 7d, 2w""", default="1d")
    ] = "1d",
    limit: Annotated[int, Field(default=100)] = 100,
) -> dict:
    """Search Org Webhooks deliveriesTopics Supported:- alarms- audits- device-updowns- occupancy-alerts- ping"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.webhooks.searchOrgWebhooksDeliveries(
        apisession,
        org_id=str(org_id),
        webhook_id=str(webhook_id),
        error=error,
        status_code=status_code,
        status=status.value,
        topic=topic.value,
        start=start,
        end=end,
        duration=duration,
        limit=limit,
    )

    if response.status_code != 200:
        api_error = {"status_code": response.status_code, "message": ""}
        if response.data:
            await ctx.error(
                f"Got HTTP{response.status_code} with details {response.data}"
            )
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
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
