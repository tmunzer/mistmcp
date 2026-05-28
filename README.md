> [!IMPORTANT]
> This MCP server is mostly used as a sandbox to explore the MCP protocol. For a more stable and optimized Mist MCP Server, please refer to the [Official Mist MCP Server](https://www.juniper.net/documentation/us/en/software/mist/mist-aiops/shared-content/topics/concept/juniper-mist-mcp-claude.html)

# Mist MCP Server

MCP Server providing Mist API access to LLM applications like Claude Desktop and VS Code Copilot.

## Tool Safety

By default, **only read-only tools are enabled** for safety. This allows AI assistants to query and analyze your Mist environment without risk of accidental modifications.

To enable tools that can modify your configuration (create, update, delete operations), use the `--enable-write-tools` flag. Write tools are protected by **elicitation** - a confirmation mechanism that requires user approval before any configuration change is applied. This ensures you maintain full control over what changes the AI can make to your network. If the AI App doesn't support elicitation, write tools will be disabled for this client to prevent unintended consequences.

> ⚠️ The `--disable-elicitation` flag removes this safety mechanism and should only be used in controlled testing environments with trusted AI applications.

## Tool Overview

The server exposes a focused set of tools grouped by workflow. This is the quickest way to understand what is available before diving into each tool's parameters.

| Workflow | Main tools | What they are used for |
| - | - | - |
| Account and navigation | `mist_get_self`, `mist_get_org_or_site_info`, `mist_get_next_page`, `mist_get_constants` | Resolve account details, discover IDs, follow pagination, and look up fixed Mist constants before making deeper queries. |
| Device and client lookup | `mist_search_device`, `mist_search_client`, `mist_search_guest_authorization`, `mist_search_nac_user_macs` | Find devices, clients, guest authorizations, and NAC-related client entries by name, MAC, IP, serial, model, or other filters. |
| Configuration read | `mist_get_configuration_objects`, `mist_get_configuration_object_schema`, `mist_search_device_config_history` | Inspect org or site configuration, discover valid schema fields, and review recent configuration history on devices. |
| Configuration changes | `mist_update_configuration_objects`, `mist_change_configuration_objects` | Create, update, and delete supported configuration objects. These tools require `--enable-write-tools`. |
| Monitoring and events | `mist_search_events`, `mist_search_audit_logs`, `mist_search_alarms`, `mist_get_stats` | Investigate events, audit history, alarms, and operational statistics across organizations, sites, devices, clients, and ports. |
| Assurance and AI insights | `mist_get_site_sle`, `mist_list_site_sle_info`, `mist_get_org_sle`, `mist_get_org_sites_sle`, `mist_get_insight_metrics`, `mist_get_site_rrm_info`, `mist_troubleshoot` | Explore SLEs, Mist AI insight metrics, radio resource management state, and Marvis troubleshooting output. |
| Device operations | `mist_utilities`, `mist_list_upgrades` | Run device-side diagnostics and maintenance helpers or inspect upgrade information. Call `mist_utilities` with only `device_type` to list the supported platform-specific utilities. Some state-changing utility actions require write tools, and the disruptive ones also trigger elicitation. |
| Inventory and security context | `mist_get_org_licenses`, `mist_list_rogue_devices` | Review organization license usage and detect or inspect rogue AP activity seen by a site. |

## Installation

**Requirements:**
- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Mist API credentials (API token)

Install dependencies:

```bash
make init # Installs project dependencies and extracts the git submodule for mist_openapi
```

## Usage

Run the server (STDIO mode, default):

```bash
uv run mistmcp
```

Options:

```bash
uv run mistmcp [OPTIONS]

OPTIONS:
    -t, --transport MODE    Transport mode: stdio (default) or http
    --host HOST             Only when `transport`==`http`, HTTP server host (default: 127.0.0.1)
    -p, --port PORT         Only when `transport`==`http`, HTTP server port (default: 8000)
    -r, --response_format   Only when `transport`==`http`, Response format: json (default) or string
    -e, --env-file PATH     Path to .env file
    -d, --debug             Enable debug output
    --enable-write-tools    Enable write tools (by default only read tools are enabled for safety)
    --disable-elicitation   DANGER ZONE! Disable elicitation for write tools
    -h, --help              Show help message

TRANSPORT MODES:
    stdio      - Standard input/output (for Claude Desktop, VS Code)
    http       - HTTP server (for remote access)
```

Examples:

```bash
    uv run mistmcp                                    # Default: stdio mode, read-only tools
    uv run mistmcp --enable-write-tools --debug       # Enable write tools with debug
    uv run mistmcp --transport http --host 0.0.0.0    # HTTP on all interfaces
    uv run mistmcp --env-file ~/.mist.env             # Custom env file
```


## Usage
Set environment variables directly or via a `.env` file. Requirements differ by transport mode:

### STDIO Mode (default)

| Variable         | Required | Description                         |
|------------------|----------|-------------------------------------|
| MIST_APITOKEN    | Yes      | Mist API token                      |
| MIST_HOST        | Yes      | Mist API host (e.g. api.mist.com)   |
| MIST_ENV_FILE    | No       | Path to .env file                   |
| MISTMCP_DEBUG    | No       | true/false (default: false)         |
| MISTMCP_ENABLE_WRITE_TOOLS | No | true/false (default: false)     |

### HTTP Mode

| Variable         | Required | Description                         |
|------------------|----------|-------------------------------------|
| MISTMCP_TRANSPORT_MODE | Yes | http                                |
| MISTMCP_HOST     | No       | HTTP bind address (default: 127.0.0.1) |
| MISTMCP_PORT     | No       | HTTP port (default: 8000)           |
| MISTMCP_DEBUG    | No       | true/false (default: false)         |
| MISTMCP_ENABLE_WRITE_TOOLS | No | true/false (default: false)     |

> **Note:** In HTTP mode, Mist API credentials are provided by the client (e.g. Claude, VS Code) via HTTP headers or query parameters, not as environment variables.


## Example: Claude Desktop / VS Code MCP Client

### STDIO Mode

Best for local usage with Claude Desktop or VS Code.

Configure the client (Claude Desktop, VS Code MCP extension):

```json
{
    "mcpServers": {
        "mist-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/mistmcp",
                "run",
                "mistmcp",
                "--enable-write-tools"
            ],
            "env": {
                "MIST_APITOKEN": "your-api-token",
                "MIST_HOST": "api.mist.com"
            }
        }
    }
}
```

### HTTP Mode

Since most of the LLM Applications are not supporting the streamable-http transport mode natively, you can use the mcp-remote package to create a remote HTTP server that can be used by these applications.

Start the server:

```bash
uv run mistmcp --transport http --host 0.0.0.0
```

Configure the client (Claude Desktop, VS Code MCP extension):

```json
{
  "mcpServers": {
    "mist-http": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://127.0.0.1:8000/mcp?cloud=api.mist.com",
        "--header",
        "Authorization:Bearer ${MIST_APITOKEN}",
        "--transport",
        "http-only"
      ],
      "env": {
        "MIST_APITOKEN": "your-api-token"
      }
    }
  }
}
```

> If your network uses SSL interception, add `"NODE_OPTIONS": "--use-system-ca"` to the `env` section to trust the system CA certificates.
> It is also possible to add `"NODE_TLS_REJECT_UNAUTHORIZED": "0"` to disable TLS verification, but this is not recommended for production use.


## License

MIT License. See [LICENSE](LICENSE).

## Author

Thomas Munzer (tmunzer@juniper.net)
GitHub: [@tmunzer](https://github.com/tmunzer)
