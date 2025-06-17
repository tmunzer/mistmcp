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
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance

from pydantic import Field
from typing import Annotated
from uuid import UUID


mcp = mcp_instance.get()


@mcp.tool(
    enabled=True,
    name="getSiteApAutoPlacement",
    description="""This API is called to view the current status of auto placement for a given map.#### Status Descriptions| Status | Description || --- | --- || `pending` | Autoplacement has not been requested for this map || `inprogress` | Autoplacement is currently processing || `done` | The autoplacement process has completed || `data_needed` | Additional position data is required for autoplacement. Users should verify the requested anchor APs have a position on the map || `invalid_model` | Autoplacement is not supported on the model of the APs on the map || `invalid_version` | Autoplacement is not supported with the APs current firmware version || `error` | There was an error in the autoplacement process |""",
    tags={"Sites Maps - Auto-placement"},
    annotations={
        "title": "getSiteApAutoPlacement",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def getSiteApAutoPlacement(
    site_id: Annotated[UUID, Field(description="""ID of the Mist Site""")],
    map_id: Annotated[UUID, Field(description="""ID of the Mist Map""")],
) -> dict:
    """This API is called to view the current status of auto placement for a given map.#### Status Descriptions| Status | Description || --- | --- || `pending` | Autoplacement has not been requested for this map || `inprogress` | Autoplacement is currently processing || `done` | The autoplacement process has completed || `data_needed` | Additional position data is required for autoplacement. Users should verify the requested anchor APs have a position on the map || `invalid_model` | Autoplacement is not supported on the model of the APs on the map || `invalid_version` | Autoplacement is not supported with the APs current firmware version || `error` | There was an error in the autoplacement process |"""

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
        if not apitoken.startswith("Bearer "):
            raise ClientError("X-Authorization header must start with 'Bearer ' prefix")
    else:
        apitoken = config.mist_apitoken
        cloud = config.mist_host

    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.sites.maps.getSiteApAutoPlacement(
        apisession,
        site_id=str(site_id),
        map_id=str(map_id),
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
