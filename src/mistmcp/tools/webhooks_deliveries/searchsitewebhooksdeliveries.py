""""
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
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance
#from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID
from enum import Enum


mcp = mcp_instance.get()



class Status(Enum):
    FAILURE = "failure"
    SUCCESS = "success"
    NONE = None

class Topic(Enum):
    ALARMS = "alarms"
    AUDITS = "audits"
    DEVICE_UPDOWNS = "device_updowns"
    OCCUPANCY_ALERTS = "occupancy_alerts"
    PING = "ping"
    NONE = None



@mcp.tool(
    enabled=False,
    name = "searchSiteWebhooksDeliveries",
    description = """Search Site Webhooks deliveriesTopics Supported:- alarms- audits- device-updowns- occupancy-alerts- ping""",
    tags = {"webhooks_deliveries"},
    annotations = {
        "title": "searchSiteWebhooksDeliveries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchSiteWebhooksDeliveries(
    
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    webhook_id: Annotated[UUID, Field(description="""ID of the Mist Webhook""")],
    error: Optional[str],
    status_code: Optional[int],
    status: Annotated[Optional[Status], Field(description="""Webhook delivery status""")] = Status.NONE,
    topic: Annotated[Optional[Topic], Field(description="""Webhook topic""")] = Topic.NONE,
    limit: Optional[int],
    start: Annotated[Optional[str], Field(description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')""")],
    end: Annotated[Optional[str], Field(description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')""")],
    duration: Annotated[Optional[str], Field(description="""Duration like 7d, 2w""")],
    sort: Annotated[Optional[str], Field(description="""On which field the list should be sorted, -prefix represents DESC order""")],
    search_after: Annotated[Optional[str], Field(description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed.""")],
) -> dict|list:
    """Search Site Webhooks deliveriesTopics Supported:- alarms- audits- device-updowns- occupancy-alerts- ping"""

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

    
    response = mistapi.api.v1.sites.webhooks.searchSiteWebhooksDeliveries(
            apisession,
            site_id=str(site_id),
            webhook_id=str(webhook_id),
            error=error if error else None,
            status_code=status_code if status_code else None,
            status=status.value if status else None,
            topic=topic.value if topic else None,
            limit=limit if limit else None,
            start=start if start else None,
            end=end if end else None,
            duration=duration if duration else None,
            sort=sort if sort else None,
            search_after=search_after if search_after else None,
    )


    if response.status_code != 200:
        api_error = {
            "status_code": response.status_code,
            "message": ""
        }
        if response.data:
            #await ctx.error(f"Got HTTP{response.status_code} with details {response.data}")
            api_error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(api_error)

    return response.data
