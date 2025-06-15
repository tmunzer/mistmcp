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
from typing import Annotated
from uuid import UUID
from enum import Enum


class For_sites(Enum):
    ANY = "any"
    FALSE = "false"
    TRUE = "true"


@mcp.tool(
    enabled=True,
    name="listOrgMxEdges",
    description="""Get List of Org MxEdges""",
    tags={"Orgs MxEdges"},
    annotations={
        "title": "listOrgMxEdges",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def listOrgMxEdges(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    for_sites: Annotated[
        For_sites, Field(description="""Filter for site level mist edges""")
    ] = For_sites.ANY,
    limit: Annotated[int, Field(default=100)] = 100,
    page: Annotated[int, Field(ge=1, default=1)] = 1,
) -> dict:
    """Get List of Org MxEdges"""

    ctx = get_context()
    request: Request = get_http_request()
    cloud = request.query_params.get("cloud", None)
    apitoken = request.headers.get("X-Authorization", None)
    apisession = mistapi.APISession(
        host=cloud,
        apitoken=apitoken,
    )

    response = mistapi.api.v1.orgs.mxedges.listOrgMxEdges(
        apisession,
        org_id=str(org_id),
        for_sites=for_sites.value,
        limit=limit,
        page=page,
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
