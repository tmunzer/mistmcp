"""
This module generates Python tool files for the Mist MCP (Model Context Protocol) server based on the Mist OpenAPI specification.
It creates a structured set of Python modules that provide programmatic access to Mist's REST APIs with proper validation and error handling.

Key Features:
- Processes Mist OpenAPI specification to generate MCP-compatible tools
- Creates organized directory structure by API categories
- Generates proper parameter validation with Pydantic
- Handles type conversions between OpenAPI and Python types
- Provides comprehensive error handling for API responses
- Manages tool registration and configuration
- Excludes deprecated or internal API endpoints
- Generates configuration files for dynamic tool management

The generated tools support:
- Proper type hints and validation
- Automatic error handling and logging
- Dynamic tool registration/unregistration
- Category-based tool organization
- User confirmation for destructive operations

Author: Thomas Munzer (tmunzer@juniper.net)
License: MIT License
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List

import yaml

# Configuration Constants
OPENAPI_PATH = (
    "./mist_openapi/mist.openapi.yaml"  # Path to the OpenAPI specification file
)
OUTPUT_DIR = Path(
    "./src/mistmcp/tools"
)  # Directory where generated tool files will be placed
TOOLS_MODULE = "mistmcp.tools"  # Base module name for imports
INIT_FILE = Path("./src/mistmcp//tools/__init__.py")  # Path to package __init__ file
# TOOLS_FILE = Path("./src/mistmcp/tools.json")  # File storing tool configuration
TOOLS_HELPER_FILE = Path("./src/mistmcp/tool_helper.py")  # Helper file for tools
# List of API tags that should be excluded from tool generation
# These tags represent endpoints that are either deprecated, internal,
# or not relevant for general API usage
EXCLUDED_TAGS = [
    "Admins Login",
    "Admins Logout",
    "Admins Lookup",
    "Admins Recover Password",
    "Admins Login - OAuth2",
    "Installer",
    "MSPs",
    "MSPs Admins",
    "MSPs Inventory",
    "MSPs Logo",
    "MSPs Logs",
    "MSPs Licenses",
    "MSPs Marvis",
    "MSPs Org Groups",
    "MSPs Orgs",
    "MSPs SLEs",
    "MSPs SSO Roles",
    "MSPs SSO",
    "MSPs Tickets",
    "Orgs Admins",
    "Orgs API Tokens",
    "Orgs Assets",
    "Orgs Asset Filters",
    "Orgs Clients - Marvis",
    "Orgs Clients - SDK",
    "Orgs Cert",
    "Orgs Devices - SSR",
    "Orgs Maps",
    "Orgs Marvis Invites",
    "Orgs Integration Cradlepoint",
    "Orgs CRL",
    "Orgs Integration Juniper",
    "Orgs Integration Zscaler",
    "Orgs SCEP",
    "Orgs Integration JSE",
    "Orgs JSI",
    "Orgs Linked Applications",
    "Orgs NAC IDP",
    "Orgs NAC Portals",
    "Orgs NAC CRL",
    "Orgs Premium Analytics",
    "Orgs Psk Portals",
    "Orgs SecIntel Profiles",
    "Orgs SDK Invites",
    "Orgs SDK Templates",
    "Orgs SSO Roles",
    "Orgs SSO",
    "Orgs Tickets",
    "Orgs Vars",
    "Sites Anomaly",
    "Sites Asset Filters",
    "Sites Assets",
    "Sites Devices - Wired",
    "Sites Beacons",
    "Sites JSE",
    "Sites Licenses",
    "Sites Location",
    "Sites RSSI Zones",
    "Sites UI Settings",
    "Sites vBeacons",
    "Sites Zones",
    "Sites Stats - Assets",
    "Sites Stats - Beacons",
    "Sites Stats - Clients SDK",
    "Sites Stats - Zones",
    "Self API Token",
    "Self OAuth2",
    "Self MFA",
    "Samples Webhooks",
    "Utilities Common",
    "Utilities WAN",
    "Utilities LAN",
    "Utilities Wi-Fi",
    "Utilities PCAPs",
    "Utilities Location",
    "Utilities MxEdge",
    # In addition, exclude some site level tags that are redundant with the Org API calls
    # or not useful for MCP
    "Orgs Stats - Assets",
    "Orgs WxTunnels",
    "Sites Stats - BGP Peers",
    "Sites Stats - Devices",
    "Sites Stats - Ports",
    "Sites Devices - Wireless",
    "Sites Devices - WAN Cluster",
    "Sites Alarms",
    "Sites Devices - Others",
    "Sites Devices - Wired - Virtual Chassis",
    "Sites Maps - Auto-placement",
    "Sites Maps - Auto-zone",
    "Sites Vpns",
    "Sites WxTunnels",
]

CUSTOM_TAGS_DEFS = {
    "sites_derived_config": "Derived configuration for the sites. It provides access to configuration objects derived from the Org level templates and configuration objects and the Site level configuration",
}

CUSTOM_TAGS = {
    "sites applications": "sites_derived_config",
    "sites ap templates": "sites_derived_config",
    "sites device profiles": "sites_derived_config",
    "sites gateway templates": "sites_derived_config",
    "sites networks": "sites_derived_config",
    "sites network templates": "sites_derived_config",
    "sites rf templates": "sites_derived_config",
    "sites skyatp": "sites_derived_config",
    "sites secintel profiles": "sites_derived_config",
    "sites service policies": "sites_derived_config",
    "sites services": "sites_derived_config",
    "sites site templates": "sites_derived_config",
}

# Type translation mapping from OpenAPI types to Python types
# This dictionary maps OpenAPI type definitions to their Python equivalents
# Used during code generation to ensure correct parameter types in generated code
TRANSLATION = {
    "integer": "int",  # OpenAPI integer type maps to Python int
    "number": "float",  # OpenAPI number/float type maps to Python float
    "string": "str",  # OpenAPI string type maps to Python str
    "array": "list",  # OpenAPI array type maps to Python list
    "boolean": "bool",  # OpenAPI boolean type maps to Python bool
}

# Template for the main __init__.py file
INIT_TEMPLATE = """\"\"\"
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
\"\"\"

{tools_import}
"""

# Template for individual tool files
TOOL_TEMPLATE = """"\"\"\"
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
\"\"\"
import json
import mistapi
from fastmcp.server.dependencies import get_context, get_http_request
from fastmcp.exceptions import ToolError, ClientError, NotFoundError
from starlette.requests import Request
from mistmcp.config import config
from mistmcp.server_factory import mcp_instance

{imports}

mcp = mcp_instance.get()

{models}
{enums}


@mcp.tool(
    enabled=True,
    name = "{operationId}",
    description = \"\"\"{description}\"\"\",
    tags = {{"{tag}"}},
    annotations = {{
        "title": "{operationId}",
        "readOnlyHint": {readOnlyHint},
        "destructiveHint": {destructiveHint},
        "openWorldHint": True,
    }},
)
async def {operationId}(
    {parameters}) -> dict:
    \"\"\"{description}\"\"\"

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

    response = {mistapi_request}

    if response.status_code != 200:
        api_error = {{
            "status_code": response.status_code,
            "message": ""
        }}
        if response.data:
            await ctx.error(f"Got HTTP{{response.status_code}} with details {{response.data}}")
            api_error["message"] =json.dumps(response.data)
        elif response.status_code == 400:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            api_error["message"] =json.dumps("Bad Request. The API endpoint exists but its syntax/payload is incorrect, detail may be given")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            api_error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 403:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            api_error["message"] =json.dumps("Unauthorized")
        elif response.status_code == 401:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            api_error["message"] =json.dumps("Permission Denied")
        elif response.status_code == 404:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            api_error["message"] =json.dumps("Not found. The API endpoint doesn’t exist or resource doesn’t exist")
        elif response.status_code == 429:
            await ctx.error(f"Got HTTP{{response.status_code}}")
            api_error["message"] =json.dumps("Too Many Request. The API Token used for the request reached the 5000 API Calls per hour threshold")
        raise ToolError(api_error)

    return response.data
"""

TOOLS_HELPER = """"\"\"\"
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
\"\"\"
from enum import Enum

class McpToolsCategory(Enum):
{enums}

TOOLS = {tools}
"""


def snake_case(s: str) -> str:
    """Convert a string to snake_case format."""
    return s.lower().replace(" ", "_").replace("-", "_")


def class_name_from_operation_id(operation_id: str) -> str:
    """Convert an operation ID to a proper class name in PascalCase."""
    return "".join(word.capitalize() for word in operation_id.split("_"))


########
# Parameter Processing Functions


def _extract_param(data: dict):
    """Extract and normalize parameter information from OpenAPI spec."""
    tmp = {}
    if data:
        if data["schema"].get("$ref"):
            ref_name = data["schema"]["$ref"].split("/")[-1:][0]
            ref = openapi_schemas.get(ref_name)
            tmp = {
                "name": data["name"].replace(" ", "_").replace("-", "_"),
                "required": data.get("required", False),
                "format": ref.get("format", None),
                "enum": ref.get("enum", None),
                "type": ref.get("type"),
                "description": data.get("description"),
                "default": ref.get("default"),
                "minimum": ref.get("minimum"),
                "maximum": ref.get("maximum"),
                "minLength": ref.get("minLength"),
                "maxLength": ref.get("maxLength"),
            }
        else:
            tmp = {
                "name": data["name"].replace(" ", "_").replace("-", "_"),
                "required": data.get("required", False),
                "format": data["schema"].get("format", None),
                "enum": data["schema"].get("enum", None),
                "type": data["schema"].get("type"),
                "description": data.get("description"),
                "default": data["schema"].get("default"),
                "minimum": data["schema"].get("minimum"),
                "maximum": data["schema"].get("maximum"),
                "minLength": data["schema"].get("minLength"),
                "maxLength": data["schema"].get("maxLength"),
            }
    return tmp


def _add_import(imports: dict, package: str, module: str = "") -> None:
    """Add an import statement to the imports dictionary."""
    if not imports.get(package):
        if module:
            imports[package] = [module]
        else:
            imports[package] = None
    elif module not in imports[package]:
        imports[package].append(module)


def _process_params(
    endpoint_params: list,
    imports: dict,
    models: str,
    enums: str,
    parameters: str,
    mistapi_parameters: str,
    force_default: bool = False,
):
    """Process endpoint parameters and generate corresponding Python code."""
    for parameter in endpoint_params:
        if parameter.get("$ref"):
            ref_name = parameter["$ref"].split("/")[-1:][0]
            data = openapi_parameters.get(ref_name)
            tmp_param = _extract_param(data)
        else:
            tmp_param = _extract_param(parameter)

        tmp_type = TRANSLATION.get(tmp_param["type"])
        tmp_optional = ""
        tmp_default = ""
        tmp_mistapi_parameters = ""
        annotations = []

        if tmp_param["description"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            description = tmp_param["description"]
            r = r"\[.*\]\(\$e/.*/([^\)]*)\)"
            r_tmp = re.findall(r, description)
            if r_tmp:
                description = re.sub(r, f"`{r_tmp[0]}`", description)
            annotations.append(
                f'description="""{description.replace('"', "'").replace("\n", " ")}"""'
            )
        elif tmp_param["name"].endswith("_id"):
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(
                f'description="""ID of the Mist {tmp_param["name"].replace("_id", "").capitalize()}"""'
            )
        if tmp_param["minLength"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"min_length={tmp_param['minLength']}")
        if tmp_param["maxLength"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"max_length={tmp_param['maxLength']}")
        if tmp_param["minimum"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"ge={tmp_param['minimum']}")
        if tmp_param["maximum"]:
            _add_import(imports, "pydantic", "Field")
            _add_import(imports, "typing", "Annotated")
            annotations.append(f"le={tmp_param['maximum']}")

        if tmp_param["type"] == "string":
            if tmp_param["format"] == "uuid":
                _add_import(imports, "uuid", "UUID")
                tmp_type = "UUID"
                tmp_mistapi_parameters = (
                    f"            {tmp_param['name']}=str({tmp_param['name']}),\n"
                )

            elif tmp_param["enum"]:
                _add_import(imports, "enum", "Enum")
                tmp_enum = f"\nclass {tmp_param['name'].capitalize()}(Enum):\n"
                tmp_choices = []
                for e in tmp_param["enum"]:
                    tmp_choices.append(e.lower())
                    e_tmp = snake_case(e)
                    if e_tmp in ["24", "5", "6"]:
                        e_tmp = f"B{e_tmp}"
                    tmp_enum += f'    {e_tmp.upper()} = "{e}"\n'
                if (
                    not tmp_param["required"]
                    and not tmp_param["default"]
                    and "none" not in tmp_choices
                    and force_default
                ):
                    tmp_enum += "    NONE = None\n"
                enums += tmp_enum
                tmp_type = tmp_param["name"].capitalize()
                if tmp_param["default"]:
                    tmp_default = f" = {tmp_param['name'].capitalize()}.{tmp_param['default'].upper()}"
                elif force_default:
                    tmp_default = f" = {tmp_param['name'].capitalize()}.NONE"
                tmp_mistapi_parameters = (
                    f"            {tmp_param['name']}={tmp_param['name']}.value,\n"
                )

        if not tmp_default:
            if tmp_param["required"]:
                tmp_optional = ""
            elif tmp_param["default"]:
                tmp_optional = ""
                if tmp_param["type"] == "string":
                    tmp_default = f' = "{tmp_param["default"]}"'
                    annotations.append(f'default="{tmp_param["default"]}"')
                else:
                    tmp_default = f" = {tmp_param['default']}"
                    annotations.append(f"default={tmp_param['default']}")
            else:
                _add_import(imports, "typing", "Optional")
                tmp_type = f"Optional[{tmp_type}]"
                # tmp_optional = " | None"
                tmp_default = " = None"

        if annotations:
            _add_import(imports, "typing", "Annotated")
            _add_import(imports, "pydantic", "Field")
            tmp_type = f"Annotated[{tmp_type}, Field({','.join(annotations)})]"

        if not tmp_mistapi_parameters:
            tmp_mistapi_parameters = (
                f"            {tmp_param['name']}={tmp_param['name']},\n"
            )

        parameters += (
            f"    {tmp_param['name']}: {tmp_type}{tmp_optional}{tmp_default},\n"
        )
        mistapi_parameters += tmp_mistapi_parameters
    return imports, models, enums, parameters, mistapi_parameters


def gen_endpoint_parameters(path_parameters: list, endpoint: dict):
    """Generate complete parameter definitions for an endpoint."""
    imports = ""
    models = ""
    enums = ""
    parameters = ""
    mistapi_parameters = ""
    tmp_imports: dict = {}
    tmp_imports, models, enums, parameters, mistapi_parameters = _process_params(
        path_parameters,
        tmp_imports,
        models,
        enums,
        parameters,
        mistapi_parameters,
        False,
    )
    tmp_imports, models, enums, parameters, mistapi_parameters = _process_params(
        endpoint.get("parameters", []),
        tmp_imports,
        models,
        enums,
        parameters,
        mistapi_parameters,
        True,
    )
    for package, modules in tmp_imports.items():
        if modules:
            imports += f"from {package} import {', '.join(modules)}\n"
        else:
            imports += f"import {package}\n"
    if parameters:
        parameters = f"\n{parameters}"
    return imports, models, enums, parameters, mistapi_parameters


def _gen_folder_and_file_paths(endpoint: str):
    """Generate appropriate folder and file paths for an endpoint."""
    endpoint_path = endpoint.split("/")
    # remove vars from endpoint path
    tmp = []
    installer = False
    for part in endpoint_path:
        if part == "installer":
            installer = True
        if part != "" and not part.startswith("{"):
            tmp.append(part)
    endpoint_path = tmp

    if installer and len(endpoint_path) > 4:
        folder_path_parts = endpoint_path[0:4]
        file_name = endpoint_path[4:5][0]
    elif len(endpoint_path) > 3:
        folder_path_parts = endpoint_path[0:3]
        file_name = endpoint_path[3:4][0]
    else:
        folder_path_parts = endpoint_path[0:3]
        file_name = endpoint_path[2:3][0]

    if file_name == "128routers":
        file_name = "ssr"
    return folder_path_parts, file_name


def _get_tag_defs() -> dict:
    defs = {}
    for tag in openapi_tags:
        if tag.get("name") in EXCLUDED_TAGS or CUSTOM_TAGS.get(tag.get("name").lower()):
            continue
        else:
            defs[snake_case(tag.get("name")).lower()] = {
                "tools": [],
                "description": re.sub(
                    r"API Call", "tool", tag.get("description", ""), flags=re.IGNORECASE
                ),
            }
    for tag in CUSTOM_TAGS_DEFS:
        defs[snake_case(tag).lower()] = {
            "tools": [],
            "description": CUSTOM_TAGS_DEFS[tag],
        }
    return defs


def _gen_tools_init(tools_import: dict):
    """Generate import statements for the __init__.py file."""
    tmp = []
    for tag, modules in tools_import.items():
        for module in modules:
            # tmp.append(f"from {TOOLS_MODULE}.{tag}.{module} import {module}")
            tmp.append(f"from .{tag} import {module} as {module}")
        # tmp.append(f"from {TOOLS_MODULE}.{tag} import {", ".join(modules)}")
        # tmp.append(f"from .{tag} import {', '.join(modules)}")
        # tmp.append(f"from .{tag} import *")
    return "\n".join(tmp)


def main() -> None:
    """Main function to process the OpenAPI spec and generate tool files.

    This function:
    1. Processes each path in the OpenAPI specification
    2. Generates appropriate Python code for each endpoint
    3. Creates organized directory structure for tools
    4. Generates necessary files with proper imports and configurations
    """
    tag_to_tools: Dict[str, List[str]] = {}
    root_tag_defs = _get_tag_defs()
    root_tools_import: dict = {}
    root_enums: list = []
    root_functions: dict = {}

    for path, methods in openapi_paths.items():
        for method, details in methods.items():
            if method.lower() == "get":
                readOnlyHint = True
                destructiveHint = False
            elif method.lower() == "delete":
                destructiveHint = True
                readOnlyHint = False
                continue
            elif method.lower() in ["post", "put"]:
                destructiveHint = True
                readOnlyHint = False
                continue
            else:
                continue

            tags = details.get("tags", ["Untagged"])
            if len(tags) > 0 and tags[0] in EXCLUDED_TAGS:
                continue

            operation_id = details.get("operationId") or snake_case(
                path.strip("/").replace("/", "_")
            )
            description = details.get("description", "")

            tag = tags[0]
            if CUSTOM_TAGS.get(tag.lower()):
                tag = CUSTOM_TAGS[tag.lower()]

            imports = ""
            models = ""
            enums = ""
            parameters = ""
            mistapi_parameters = ""

            imports, models, enums, parameters, mistapi_parameters = (
                gen_endpoint_parameters(methods.get("parameters", []), details)
            )

            folder_path_parts, file_name = _gen_folder_and_file_paths(path)
            mistapi_request = f"""mistapi.{".".join(folder_path_parts)}.{file_name}.{operation_id}(
            apisession,
{mistapi_parameters}    )"""

            tool_code = TOOL_TEMPLATE.format(
                class_name=operation_id.capitalize(),
                imports=imports,
                models=models,
                enums=enums,
                operationId=operation_id,
                description=description.replace("\n", ""),
                tag=tag,
                readOnlyHint=readOnlyHint,
                destructiveHint=destructiveHint,
                parameters=parameters,
                mistapi_request=mistapi_request,
            )

            tag_dir = OUTPUT_DIR / snake_case(tag)
            tag_dir.mkdir(parents=True, exist_ok=True)
            init_file = tag_dir / "__init__.py"
            init_file.write_text("")
            tool_file = tag_dir / f"{snake_case(operation_id)}.py"
            tool_file.write_text(tool_code)
            tag_to_tools.setdefault(tag, []).append(str(tool_file))

            ## tool_tools_import
            if not root_tools_import.get(snake_case(tag)):
                root_tools_import[snake_case(tag)] = []
            root_tools_import[snake_case(tag)].append(snake_case(operation_id))
            ## root_enums
            if (
                f'    {snake_case(tag).upper()} = "{snake_case(tag).lower()}"'
                not in root_enums
            ):
                root_enums.append(
                    f'    {snake_case(tag).upper()} = "{snake_case(tag).lower()}"'
                )
            ## root_functions
            if not root_functions.get(snake_case(snake_case(tag))):
                root_functions[snake_case(snake_case(tag))] = []
            root_functions[snake_case(snake_case(tag))].append(
                f"{snake_case(operation_id)}.add_tool()"
            )
            root_functions[snake_case(snake_case(tag))].append(
                f"TOOL_REMOVE_FCT.append({snake_case(operation_id)}.remove_tool)"
            )
            ## root_tag_defs
            root_tag_defs[snake_case(snake_case(tag))]["tools"].append(operation_id)

    print("Generated tools grouped by tag:")
    for tag, files in tag_to_tools.items():
        print(f"{tag}:")
        for f in files:
            print(f"  - {f}")

    print("Generated tools grouped by tag:")
    for tag, files in tag_to_tools.items():
        print(f'{snake_case(tag).upper()} = "{snake_case(tag).lower()}"')

    with open(INIT_FILE, "w") as f_init:
        f_init.write(
            INIT_TEMPLATE.format(tools_import=_gen_tools_init(root_tools_import))
        )

    with open(TOOLS_HELPER_FILE, "w") as f_tool:
        f_tool.write(
            TOOLS_HELPER.format(
                enums="\n".join(root_enums),
                tools=json.dumps(root_tag_defs),
            )
        )

    print(" TAGS SUMMARY ".center(80, "-"))
    tools = 0
    for tag, tag_data in root_tag_defs.items():
        tools += len(tag_data["tools"])
        print(f"{tag}: {len(tag_data['tools'])} tools")

    print(" CATEGORY SUMMARY ".center(80, "-"))
    print(f"Total categories: {len(root_tag_defs)}")
    print(f"Total tools: {tools}")


if __name__ == "__main__":
    # Clean up existing tools directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    # Load and parse the OpenAPI specification
    with open(OPENAPI_PATH, "r") as f:
        openapi_json = yaml.safe_load(f)
    openapi_paths = openapi_json.get("paths")
    openapi_tags = openapi_json.get("tags")
    openapi_parameters = openapi_json.get("components", {}).get("parameters")
    openapi_schemas = openapi_json.get("components", {}).get("schemas")

    main()
