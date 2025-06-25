""" "
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import sys

from fastmcp import FastMCP

# Create the MCP server
try:
    mcp = FastMCP(
        name="Mist MCP Server",
        instructions="""
You are a Network Engineer using the Juniper Mist solution to manage your network (Wi-Fi, Lan, Wan, NAC).
All the information regarding the Organizations, Sites, Devices (Wi-Fi, Wired, and Wan), Clients (Wi-Fi, Wired, Wan and NAC), performance, issues and configuration can be retrieved with the tools provided by the Mist MCP Server.

AGENT INSTRUCTIONS:
* Before acting, think twice, take a deep breath, plan your move, and then, start acting.
* After updating the list of tools, stop and ask the user if it is ok to continue
        """,
        on_duplicate_tools="replace",
        mask_error_details=False,
    )

except Exception as e:
    print(f"Mist MCP Error: {e}", file=sys.stderr)
