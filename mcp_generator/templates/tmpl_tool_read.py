# Template for individual tool files
TOOL_TEMPLATE_READ = '''"""
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

{imports}
{models}
{enums}


@mcp.tool(
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
    {parameters}    ctx: Context|None = None,
    ) -> dict | list | str:
    \"\"\"{description}\"\"\"

    logger.debug("Tool {operationId} called")
    
    apisession, response_format = get_apisession()
    
    {request}

    return format_response(response, response_format)
'''
