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
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

from pydantic import Field
from typing import Annotated, Optional
from uuid import UUID


@mcp.tool(
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
    org_id: Annotated[UUID, Field(description="""Organization ID""")],
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
    limit: Annotated[
        int, Field(description="""Max number of results per page""", default=100)
    ] = 100,
    start: Annotated[
        Optional[str | None],
        Field(description="""Start of time range (epoch seconds)"""),
    ] = None,
    end: Annotated[
        Optional[str | None], Field(description="""End of time range (epoch seconds)""")
    ] = None,
    duration: Annotated[
        Optional[str | None],
        Field(description="""Time range duration (e.g. 1d, 1h, 10m)"""),
    ] = None,
    sort: Annotated[Optional[str | None], Field(description="""Sort field""")] = None,
    search_after: Annotated[
        Optional[str | None],
        Field(
            description="""Pagination cursor from '_next' URL of previous response"""
        ),
    ] = None,
    ctx: Context | None = None,
) -> dict | list | str:
    """Search Sites"""

    logger.debug("Tool searchOrgSites called")

    apisession, response_format = get_apisession()

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
        limit=limit,
        start=start if start else None,
        end=end if end else None,
        duration=duration if duration else None,
        sort=sort if sort else None,
        search_after=search_after if search_after else None,
    )
    await process_response(response)

    return format_response(response, response_format)
