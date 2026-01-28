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
# from mistmcp.server_factory import mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID


mcp = mcp_instance.get()


@mcp.tool(
    enabled=False,
    name="searchOrgSites",
    description="""Search Sites""",
    tags={"orgs"},
    annotations={
        "title": "searchOrgSites",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": True,
    },
)
async def searchOrgSites(
    org_id: Annotated[UUID, Field(description="""ID of the Mist Org""")],
    analytic_enabled: Annotated[
        Optional[bool | None],
        Field(description="""If Advanced Analytic feature is enabled"""),
    ] = None,
    app_waking: Annotated[
        Optional[bool | None], Field(description="""If App Waking feature is enabled""")
    ] = None,
    asset_enabled: Annotated[
        Optional[bool | None], Field(description="""If Asset Tracking is enabled""")
    ] = None,
    auto_upgrade_enabled: Annotated[
        Optional[bool | None],
        Field(description="""If Auto Upgrade feature is enabled"""),
    ] = None,
    auto_upgrade_version: Annotated[
        Optional[str | None],
        Field(description="""If Auto Upgrade feature is enabled"""),
    ] = None,
    country_code: Annotated[
        Optional[str | None], Field(description="""Site country code""")
    ] = None,
    honeypot_enabled: Annotated[
        Optional[bool | None], Field(description="""If Honeypot detection is enabled""")
    ] = None,
    id: Annotated[Optional[str | None], Field(description="""Site id""")] = None,
    locate_unconnected: Annotated[
        Optional[bool | None],
        Field(description="""If unconnected client are located"""),
    ] = None,
    mesh_enabled: Annotated[
        Optional[bool | None], Field(description="""If Mesh feature is enabled""")
    ] = None,
    name: Annotated[
        Optional[str | None],
        Field(description="""Site name. Adds '*' at the end for partial match"""),
    ] = None,
    rogue_enabled: Annotated[
        Optional[bool | None], Field(description="""If Rogue detection is enabled""")
    ] = None,
    remote_syslog_enabled: Annotated[
        Optional[bool | None], Field(description="""If Remote Syslog is enabled""")
    ] = None,
    rtsa_enabled: Annotated[
        Optional[bool | None],
        Field(description="""If managed mobility feature is enabled"""),
    ] = None,
    vna_enabled: Annotated[
        Optional[bool | None],
        Field(description="""If Virtual Network Assistant is enabled"""),
    ] = None,
    wifi_enabled: Annotated[
        Optional[bool | None], Field(description="""If Wi-Fi feature is enabled""")
    ] = None,
    limit: Optional[int | None] = None,
    start: Annotated[
        Optional[str | None],
        Field(
            description="""Start time (epoch timestamp in seconds, or relative string like '-1d', '-1w')"""
        ),
    ] = None,
    end: Annotated[
        Optional[str | None],
        Field(
            description="""End time (epoch timestamp in seconds, or relative string like '-1d', '-2h', 'now')"""
        ),
    ] = None,
    duration: Annotated[
        Optional[str | None], Field(description="""Duration like 7d, 2w""")
    ] = None,
    sort: Annotated[
        Optional[str | None],
        Field(
            description="""On which field the list should be sorted, -prefix represents DESC order"""
        ),
    ] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor for retrieving subsequent pages of results. This value is automatically populated by Mist in the `next` URL from the previous response and should not be manually constructed."""
        ),
    ] = None,
) -> dict | list:
    """Search Sites"""

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

    response = mistapi.api.v1.orgs.sites.searchOrgSites(
        apisession,
        org_id=str(org_id),
        analytic_enabled=analytic_enabled if analytic_enabled else None,
        app_waking=app_waking if app_waking else None,
        asset_enabled=asset_enabled if asset_enabled else None,
        auto_upgrade_enabled=auto_upgrade_enabled if auto_upgrade_enabled else None,
        auto_upgrade_version=auto_upgrade_version if auto_upgrade_version else None,
        country_code=country_code if country_code else None,
        honeypot_enabled=honeypot_enabled if honeypot_enabled else None,
        id=id if id else None,
        locate_unconnected=locate_unconnected if locate_unconnected else None,
        mesh_enabled=mesh_enabled if mesh_enabled else None,
        name=name if name else None,
        rogue_enabled=rogue_enabled if rogue_enabled else None,
        remote_syslog_enabled=remote_syslog_enabled if remote_syslog_enabled else None,
        rtsa_enabled=rtsa_enabled if rtsa_enabled else None,
        vna_enabled=vna_enabled if vna_enabled else None,
        wifi_enabled=wifi_enabled if wifi_enabled else None,
        limit=limit if limit else None,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
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
                "Not found. The API endpoint doesn’t exist or resource doesn’t exist"
            )
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{response.status_code}")
            api_error["message"] = json.dumps(
                "Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold"
            )
        raise ToolError(api_error)

    return response.data
