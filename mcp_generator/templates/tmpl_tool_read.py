# Template for individual tool files
TOOL_TEMPLATE_READ = '''"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""
import mistapi
from fastmcp import Context
from fastmcp.exceptions import ToolError
from mistmcp.request_processor import get_apisession
from mistmcp.response_processor import process_response, handle_network_error
from mistmcp.response_formatter import format_response
from mistmcp.server import mcp
from mistmcp.logger import logger

{imports}
{models}
{enums}


@mcp.tool(
    name = "mist_{operationId}",
    description = """{description}""",
    tags = {{"{tag}"}},
    annotations = {{
        "title": "{title}",
        "readOnlyHint": {readOnlyHint},
        "destructiveHint": {destructiveHint},
        "openWorldHint": True,
        "idempotentHint": True,
    }},
)
async def {operationId}(
    {parameters}    ctx: Context|None = None,
    ) -> dict | list | str:
    \"\"\"{description}\"\"\"

    logger.debug("Tool {operationId} called")

    apisession, response_format = await get_apisession()

    {request}

    return format_response(response, response_format)
'''
