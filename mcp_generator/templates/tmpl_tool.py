# Template for individual tool files
TOOL_TEMPLATE = '''"""
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

{imports}


mcp = get_mcp()

if not mcp:
    raise RuntimeError(
        "MCP instance not found. Make sure to initialize the MCP server before defining tools."
    )

{models}
{enums}


@mcp.tool(
    enabled=True,
    name = "{operationId}",
    description = """{description}""",
    tags = {{"{tag}"}},
    annotations = {{
        "title": "{operationId}",
        "readOnlyHint": {readOnlyHint},
        "destructiveHint": {destructiveHint},
        "openWorldHint": True,
    }},
)
async def {operationId}(
    {parameters}) -> dict|list:
    \"\"\"{description}\"\"\"

    apisession = get_apisession()
    data = {{}}
    
    {request}

    return data
'''
