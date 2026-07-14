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
| Account and navigation | `mist_get_account`, `mist_describe`, `mist_get_next_page` | Resolve account details, discover IDs, follow pagination, and look up fixed Mist constants or configuration schemas. |
| Device and client lookup | `mist_search_assets` | Find devices and clients by name, MAC, IP, serial, model, or other filters. |
| Configuration read | `mist_get_configuration` | Inspect org or site configuration and review recent device configuration history. |
| Configuration changes | `mist_update_configuration_objects`, `mist_change_configuration_objects` | Create, update, and delete supported configuration objects. These tools require `--enable-write-tools`. |
| Monitoring and events | `mist_search_activity`, `mist_get_stats` | Investigate events, audit history, alarms, and operational statistics across organizations, sites, devices, clients, and ports. |
| Network topology | `mist_topology` | Build evidence-aware site or WAN topology and find candidate physical adjacency paths. Site actions require both `org_id` and `site_id`. |
| Assurance and AI insights | `mist_get_sle`, `mist_get_site_insights`, `mist_troubleshoot` | Explore SLEs, Mist AI insight metrics, radio resource management state, and Marvis troubleshooting output. |
| Device operations | `mist_utilities`, `mist_upgrades` | Run device-side diagnostics and maintenance helpers or inspect upgrade information. Call `mist_utilities` with only `device_type` to list the supported platform-specific utilities. Some state-changing utility actions require write tools, and the disruptive ones also trigger elicitation. |
| Inventory and security context | `mist_get_account`, `mist_search_security` | Review organization license usage, NAC user MACs, and rogue devices. |

### Workflow-oriented catalog

The server exposes seven workflow-oriented facade tools in place of fourteen
endpoint-oriented tools. `mist_topology` and `mist_get_next_page` remain independent,
and pagination behavior is unchanged.

| Workflow tool | Covers |
| - | - |
| `mist_get_account` | Current account information and organization licenses |
| `mist_describe` | Mist constants and configuration schemas |
| `mist_search_assets` | Devices and clients |
| `mist_get_configuration` | Configuration objects and device configuration history |
| `mist_search_activity` | Events, alarms, and audit logs |
| `mist_search_security` | NAC user MACs and rogue devices |
| `mist_get_site_insights` | Site insight metrics and RRM information |

Each workflow module contains its own validation and Mist API implementation; the
replaced endpoint-tool modules are no longer retained. `make generate` preserves the
workflow source files, removes any regenerated replaced modules, and rebuilds
`tool_helper.py` with only the workflow-oriented public catalog.

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
    --stateless             Only when transport==http, serve statelessly so clients survive a server restart (no server->client push)
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
| MISTMCP_DISABLE_ELICITATION | No | DANGER ZONE! true/false (default: false) |

### HTTP Mode

| Variable         | Required | Description                         |
|------------------|----------|-------------------------------------|
| MISTMCP_TRANSPORT_MODE | Yes | http                                |
| MISTMCP_HOST     | No       | HTTP bind address (default: 127.0.0.1) |
| MISTMCP_PORT     | No       | HTTP port (default: 8000)           |
| MISTMCP_DEBUG    | No       | true/false (default: false)         |
| MISTMCP_ENABLE_WRITE_TOOLS | No | true/false (default: false)     |
| MISTMCP_DISABLE_ELICITATION | No | DANGER ZONE! true/false (default: false) |
| MISTMCP_STATELESS | No | true/false (default: false) — survive server restart, no server->client push |

> **Note:** In HTTP mode, Mist API credentials are provided by the client (e.g. Claude, VS Code) via HTTP headers or query parameters, not as environment variables.

### Stateless HTTP mode

Set `MISTMCP_STATELESS=true` (or `--stateless`) with `--transport http` to serve each
request on a fresh transport. There is no server session id to go stale, so an
already-connected MCP client survives a server restart without reconnecting.

Trade-offs:

- **No server→client push.** Notifications and in-band elicitation are disabled.
- **Writes require an explicit DANGER ZONE.** Because elicitation can't prompt, the
  standard update tool is only available with `--enable-write-tools` **and**
  `--disable-elicitation` (or `MISTMCP_DISABLE_ELICITATION=true`), which auto-accepts.
  Starting stateless + http + `--enable-write-tools` without `--disable-elicitation` is
  refused at startup. The delete-capable change tool remains hidden.
- **Read-only stays safe.** Without write tools, destructive upgrade/utility actions
  fail closed with a clear error.

Example:

```bash
uv run mistmcp --transport http --stateless                       # read-only, restart-safe
uv run mistmcp --transport http --stateless \
    --enable-write-tools --disable-elicitation                    # writes (DANGER ZONE)
```


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
