
# Mist MCP Server



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
    -m, --mode MODE         Only when `transport`==`stdio`, Tool loading mode: managed, all (default)
    --host HOST             Only when `transport`==`http`, HTTP server host (default: 127.0.0.1)
    -p, --port PORT         Only when `transport`==`http`, HTTP server port (default: 8000)
    -e, --env-file PATH     Path to .env file
    -d, --debug             Enable debug output
    -h, --help              Show help message

TOOL LOADING MODES:
    managed    - All tools loaded at startup (default)
    all        - All tools loaded at startup (same as managed)

TRANSPORT MODES:
    stdio      - Standard input/output (for Claude Desktop, VS Code)
    http       - HTTP server (for remote access)
```

Examples:

```bash
    uv run mistmcp                                    # Default: stdio + managed mode
    uv run mistmcp --mode all --debug                 # All tools with debug
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
| MISTMCP_TOOL_LOADING_MODE | No | managed or all (default: managed) |
| MISTMCP_DEBUG    | No       | true/false (default: false)         |

### HTTP Mode

| Variable         | Required | Description                         |
|------------------|----------|-------------------------------------|
| MISTMCP_TRANSPORT_MODE | Yes | http                                |
| MISTMCP_HOST     | No       | HTTP bind address (default: 127.0.0.1) |
| MISTMCP_PORT     | No       | HTTP port (default: 8000)           |
| MISTMCP_TOOL_LOADING_MODE | No | managed or all (default: managed) |
| MISTMCP_DEBUG    | No       | true/false (default: false)         |

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
                "--mode",
                "all"
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
        "http://127.0.0.1:8000/mcp/?cloud=api.mist.com",
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
