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
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response
from mistmcp.server import get_mcp

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )


@mcp.tool(
    enabled=True,
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
        Field(
            description="""Site name. Case insensitive. Add a wildcard (`*`) at the end for partial search"""
        ),
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

    apisession = get_apisession()
    data = {}

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
    await process_response(response)

    data = response.data

    return data
