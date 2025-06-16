# Mist MCP Server

A Model Context Protocol (MCP) server that provides AI-powered access to Juniper Mist networking APIs with **multi-client session management**. This project enables Large Language Models (LLMs) like Claude to interact with Mist cloud-managed network infrastructure through a comprehensive set of tools, with each client maintaining independent tool configurations.

## 📖 Overview

The Mist MCP Server is a **session-aware, multi-client MCP server** that consists of:

1. **Tool Generator** (`generate_from_openapi.py`) - Automatically generates MCP-compatible tools from the Mist OpenAPI specification
2. **Multi-Client MCP Server** (`src/mistmcp/`) - Session-aware MCP server supporting multiple clients with independent tool configurations
3. **Dynamic Tool Management** - Runtime tool enabling/disabling per client session

### Key Features

- **🌐 Multi-Client Support**: Each client maintains independent tool configurations and session state
- **🔧 Dynamic Tool Management**: Enable/disable tool categories at runtime using `manageMcpTools`
- **📊 Session Isolation**: Complete isolation between different MCP clients
- **⚙️ Flexible Loading Modes**: Choose from managed, all, or custom tool loading strategies
- **🚀 Transport Flexibility**: Supports both stdio and HTTP transport modes

## 🚀 Features

- **🌍 Multi-Client Architecture**: Multiple MCP clients can connect simultaneously with independent tool configurations
- **🔄 Dynamic Tool Management**: Enable/disable tool categories at runtime per client session
- **📊 Session Awareness**: Complete isolation between different client sessions
- **🎯 Flexible Loading Modes**:
  - **Minimal**: Only essential tools (`getSelf`, `manageMcpTools`)
  - **Managed**: Dynamic tool management (default)
  - **All**: All tools loaded at startup
  - **Custom**: Specific tool categories pre-loaded
- **🚀 Comprehensive API Coverage**: Auto-generated tools for all major Mist API endpoints
- **📡 Transport Flexibility**: Supports both stdio and HTTP transport modes
- **🏗️ Intelligent Organization**: Tools grouped by functionality (orgs, sites, devices, clients, etc.)
- **🛡️ Type Safety**: Full type validation using Pydantic models
- **⚠️ Robust Error Handling**: Comprehensive error handling and logging
- **🤖 AI-Optimized**: Designed specifically for LLM interaction patterns

## 🛠️ Installation & Setup

## Prerequisites

- Python 3.10 or higher (uv will manage this)
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Mist API credentials (API token and organization access)

## 1. Install Dependencies

```bash
uv sync
```

## 2. Generate MCP Tools (Optional)

The repository includes pre-generated tools, but you can regenerate them:

```bash
uv run python generate_from_openapi.py
```

This will:
- Parse the Mist OpenAPI specification (`mist_openapi/mist.openapi.yaml`)
- Generate categorized tool modules in `src/mistmcp/tools/`
- Create tool configuration files

## 3. Run the MCP Server

The server supports multiple modes and transport options:

### Command Line Options

```bash
uv run mistmcp [OPTIONS]

OPTIONS:
    -h, --help              Show help message
    -t, --transport MODE    Transport mode: stdio (default) or http
    -m, --mode MODE         Tool loading mode: managed (default), all, custom
    -c, --categories LIST   Comma-separated tool categories (for custom mode)
    -d, --debug             Enable debug output
    --host HOST             HTTP server host (default: 127.0.0.1, HTTP mode only)
    --port PORT             HTTP server port (default: 8000, HTTP mode only)

STDIO MODE EXAMPLES:
    uv run mistmcp                                    # Default managed mode (stdio)
    uv run mistmcp --mode all --debug                 # All tools with debug logging
    uv run mistmcp --mode custom --categories orgs,sites,orgs_devices

HTTP MODE EXAMPLES:
    uv run mistmcp --transport http                   # HTTP mode, localhost:8000
    uv run mistmcp --transport http --port 9000       # HTTP mode, custom port
    uv run mistmcp --transport http --host 0.0.0.0    # HTTP mode, all interfaces
    uv run mistmcp --transport http --mode all --debug --port 8080
```

### Tool Loading Modes

### Tool Loading Modes

1. **Managed Mode** (`--mode managed`) - **Default**
   - Only `getSelf` and `manageMcpTools` loaded
   - Lowest memory footprint
   - Tools enabled on-demand via `manageMcpTools`

2. **All Mode** (`--mode all`)
   - All available tools loaded at startup
   - Maximum functionality, higher memory usage
   - Best for power users or automated scenarios

3. **Custom Mode** (`--mode custom --categories orgs,sites`)
   - Pre-load specific tool categories
   - Tailored configuration for specific use cases
   - Requires explicit category specification

### Transport Mode Comparison

| Feature | STDIO Mode | HTTP Mode |
|---------|------------|-----------|
| **Performance** | Fastest (direct IPC) | Network latency |
| **Security** | Process isolation | Network authentication |
| **Remote Access** | Local only | Network accessible |
| **Configuration** | Simple | Requires network setup |
| **Query Parameters** | Not supported | Supported (`?mode=all&categories=orgs`) |
| **Scaling** | One client per process | Multiple clients per server |
| **Debugging** | Process logs | HTTP logs + process logs |
| **Use Cases** | Claude Desktop, VS Code | Remote clients (Claude Desktop, VS Code), microservices |



## 4. Configure MCP Client

The server supports two transport modes with different configuration requirements:

### STDIO Mode (Recommended for Local Usage)

STDIO mode runs the server as a subprocess and communicates via standard input/output. This is the recommended mode for local MCP clients like Claude Desktop.

**Features:**
- Direct process communication (fastest)
- No network configuration required
- Automatic process lifecycle management
- Built-in security (no exposed ports)

**Claude Desktop (`~/.claude_desktop/claude_desktop_config.json`) or VS Code MCP Extension:**
```json
{
    "mcpServers": {
        "Mist MCP Server": {
            "command": "uv",
            "args": [
                "run",
                "mistmcp",
                "--mode",
                "managed"
            ],
            "cwd": "/absolute/path/to/mistmcp",
            "env": {
                "MIST_ENV_FILE": "path-to-your-env-file"
            }
        },
        "mist-mcp": {
            "command": "uv",
            "args": [
                "run",
                "mistmcp",
                "--transport",
                "stdio",
                "--mode",
                "custom",
                "--categories",
                "orgs,sites,orgs_devices"
            ],
            "cwd": "/absolute/path/to/mistmcp",
            "env": {
                "MIST_API_TOKEN": "your-api-token",
                "MIST_ORG_ID": "your-org-id"
            }
        }
    }
}
```

### HTTP Mode (For Remote Access & Integration)

HTTP mode runs the server as a web service, enabling access from remote clients and integration scenarios.

**Features:**
- Network-accessible (remote clients)
- RESTful MCP-over-HTTP protocol
- Query parameter support for dynamic configuration
- Suitable for microservice architectures

**Starting the HTTP Server:**
```bash
# Basic HTTP mode
uv run mistmcp --transport http --mode managed

# Custom port and host
uv run mistmcp --transport http --mode managed --port 8080 --host 0.0.0.0

# With debug logging
uv run mistmcp --transport http --mode all --debug
```

**HTTP Mode Query Parameters:**
- `cloud` - Mist API Cloud to use (e.g. `api.mist.com`, `api.gc1.mist.com`, `api.gc2.mist.com`, etc.)
- `mode` - Tool loading mode: `managed` (default), `all`, `custom`
- `categories` - Comma-separated tool categories (when `mode=custom`)

**Authentication:**
- Use `X-Authorization` header with your Mist API token
- Format: `X-Authorization: your-mist-api-token`
- The token is passed directly (not as Bearer token)

**Examples:**
```bash
# All tools mode via HTTP with authentication
curl -H "X-Authorization: your-mist-api-token" \
  "http://localhost:8000/mcp/tools?cloud=api.mist.com&mode=all"

# Custom categories via HTTP
curl -H "X-Authorization: your-mist-api-token" \
  "http://localhost:8000/mcp/tools?cloud=api.mist.com&mode=custom&categories=orgs,sites,orgs_devices"

# Test MCP endpoint
curl -H "X-Authorization: your-mist-api-token" \
  -H "Content-Type: application/json" \
  -d '{"method": "call_tool", "params": {"name": "getSelf", "arguments": {}}}' \
  "http://localhost:8000/mcp/?cloud=api.mist.com"
```

**Claude Desktop with HTTP Mode:**
```json
{
    "mcpServers": {
        "Mist MCP Server (HTTP - Managed Mode)": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "http://localhost:8000/mcp/?cloud=api.mist.com&mode=managed",
                "--header",
                "X-Authorization:${MIST_API_TOKEN}",
                "--transport",
                "http-only"
            ],
            "env": {
                "MIST_API_TOKEN": "your-mist-api-token-here"
            }
        },
        "Mist MCP Server (HTTP - Custom Categories)": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "http://localhost:8000/mcp/?cloud=api.mist.com&mode=custom&categories=sites,orgs,orgs_devices",
                "--header",
                "X-Authorization:${MIST_API_TOKEN}",
                "--transport",
                "http-only"
            ],
            "env": {
                "MIST_API_TOKEN": "your-mist-api-token-here"
            }
        }
    }
}
```

**Remote HTTP Configuration with Authentication:**
```json
{
    "mcpServers": {
        "Mist MCP Server (Remote Production)": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "https://your-server.com:8000/mcp/?cloud=api.mist.com&mode=all",
                "--header",
                "X-Authorization:${MIST_API_TOKEN}",
                "--transport",
                "http-only"
            ],
            "env": {
                "MIST_API_TOKEN": "your-mist-api-token-here"
            }
        }
    }
}
```

**Production HTTP Deployment:**
```bash
# Run with environment variables
uv run mistmcp --transport http --mode managed --host 0.0.0.0 --port 8000

# Or with Docker (if available)
docker run -p 8000:8000 \
  mistmcp:latest --transport http --mode managed
```

## 📋 Usage

### Transport Mode Selection

Choose the appropriate transport mode based on your use case:

**Use STDIO mode when:**
- Running locally with Claude Desktop or VS Code
- You want maximum performance and security
- You don't need remote access
- You prefer simple configuration

**Use HTTP mode when:**
- You need remote access to the MCP server
- Building microservice architectures
- Multiple remote clients need access
- You want to use query parameters for dynamic configuration
- Integration with web applications or services

### HTTP Mode Advanced Configuration

#### Security Headers

When deploying in production, consider adding security headers:

```bash
# Run with custom headers (if supported by your deployment)
uv run mistmcp --transport http --mode managed \
  --header "X-Frame-Options: DENY" \
  --header "X-Content-Type-Options: nosniff"
```

#### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name your-mist-mcp.example.com;

    location /mcp/ {
        proxy_pass http://127.0.0.1:8000/mcp/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```


### Multi-Client Session Management

Each MCP client that connects to the server gets its own independent session with:
- **Separate tool configurations** - Enable different tools per client
- **Session isolation** - No interference between clients
- **Dynamic tool management** - Add/remove tools at runtime per session

### Complete Configuration Examples

#### Claude Desktop - Full Configuration

Create or edit `~/.claude_desktop/claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "mist-network-stdio": {
            "command": "uv",
            "args": [
                "run",
                "mistmcp",
                "--transport",
                "stdio",
                "--mode",
                "managed",
                "--debug"
            ],
            "cwd": "/Users/yourname/Projects/mistmcp",
            "env": {
                "MIST_API_TOKEN": "your-mist-api-token-here",
                "MIST_ORG_ID": "your-organization-id-optional"
            }
        },
        "mist-network-http": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "http://127.0.0.1:8000/mcp/?cloud=api.mist.com&mode=managed",
                "--header",
                "X-Authorization:${MIST_API_TOKEN}",
                "--transport",
                "http-only"
            ],
            "env": {
                "MIST_API_TOKEN": "your-mist-api-token-here"
            }
        }
    }
}
```

#### VS Code MCP Extension - Multiple Configurations

Add to your workspace `.vscode/settings.json`:

```json
{
    "mcp.servers": {
        "mist-managed": {
            "command": "uv",
            "args": [
                "run",
                "mistmcp",
                "--mode",
                "managed"
            ],
            "cwd": "${workspaceFolder}/../mistmcp",
            "env": {
                "MIST_ENV_FILE": "path-to-your-env-file"
            }
        },
        "mist-devices": {
            "command": "uv",
            "args": [
                "run",
                "mistmcp",
                "--mode",
                "custom",
                "--categories",
                "orgs_devices,sites_devices,orgs_stats___devices"
            ],
            "cwd": "${workspaceFolder}/../mistmcp",
            "env": {
                "MIST_ENV_FILE": "path-to-your-env-file"
            }
        },
        "mist-remote-http": {
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                "https://your-server.com:8000/mcp/?cloud=api.mist.com&mode=all",
                "--header",
                "X-Authorization:${MIST_API_TOKEN}",
                "--transport",
                "http-only"
            ],
            "env": {
                "MIST_API_TOKEN": "your-mist-api-token-here"
            }
        }
    }
}
```

#### Continue.dev Configuration

Add to your `~/.continue/config.json`:

```json
{
    "mcpServers": [
        {
            "name": "mist-network",
            "transport": {
                "type": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "mistmcp",
                    "--mode",
                    "managed"
                ],
                "cwd": "/path/to/mistmcp"
            },
            "env": {
                "MIST_ENV_FILE": "path-to-your-env-file"
            }
        }
    ]
}
```


### Getting Started

1. **Connect your MCP client** (Claude Desktop, VS Code, etc.)
2. **Start with essential tools** - All sessions begin with `getSelf` and `manageMcpTools`
3. **Enable tools as needed** - Use `manageMcpTools` to enable tool categories
4. **Query your infrastructure** - Ask natural language questions about your Mist network

### Example Workflow

```sh
# 1. Get your organization info
"Show me my organization details"

# 2. Locate a wi-fi/wired/wan client withing the Mist Organization
# (This will call manageMcpTools to enable the required tools, ask for confirmation, and start to look for the client)
User: "Locate the client xyz"
Assistant: "I'll enable device management tools first..."
[Calls manageMcpTools with device categories]
Assistant: "Tools enabled! Do you want me to continue?"
User: "yes"
[Proceeds with device queries]

# 3. Explore your network
"List all my sites and their status"
"Show me access points that are offline"
"What wireless clients are connected to my guest network?"
"Which devices need firmware updates?"
"On the xyz site, why the users connected to the abc network don't have access to the fileserver resource?"
```


## 🏗️ Project Structure

```
mistmcp/
├── generate_from_openapi.py         # Tool generator script
├── mist_openapi/
│   └── mist.openapi.yaml           # Mist OpenAPI specification
└── src/mistmcp/                    # MCP Server source
    ├── __init__.py                # Package initialization
    ├── __main__.py                # CLI entry point
    ├── __version.py               # Version information
    ├── config.py                  # Server configuration system
    ├── constants.py               # Constants and defaults
    ├── server_factory.py          # Server creation and configuration
    ├── session_aware_server.py    # Session-aware FastMCP implementation
    ├── session_manager.py         # Multi-client session management
    ├── session_middleware.py      # Session middleware components
    ├── session_tools.py           # Session-aware tool decorators
    ├── tool_loader.py             # Dynamic tool loading system
    ├── tool_manager.py            # manageMcpTools implementation
    ├── tool_helper.py            # Tool category definitions
    ├── tools.json                 # Tool registry and configuration
    └── tools/                     # Generated tool modules
        ├── orgs/                  # Organization-level APIs
        ├── sites/                 # Site-level APIs
        ├── constants_*/           # Constants and definitions
        └── ...                    # Other API categories

```

## 🔧 Architecture Overview

### Multi-Client Session Management

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client 1  │    │   MCP Client 2  │    │   MCP Client N  │
│   (Claude)      │    │   (VS Code)     │    │   (Other)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │  Session-Aware MCP Server │
                   │                           │
                   │  ┌─────────────────────┐  │
                   │  │   Session Manager   │  │
                   │  │                     │  │
                   │  │ ┌───────┐ ┌───────┐ │  │
                   │  │ │ Sess1 │ │ Sess2 │ │  │
                   │  │ │ Tools │ │ Tools │ │  │
                   │  │ └───────┘ └───────┘ │  │
                   │  └─────────────────────┘  │
                   │                           │
                   │  ┌─────────────────────┐  │
                   │  │   Tool Loader       │  │
                   │  │   & Manager         │  │
                   │  └─────────────────────┘  │
                   └───────────────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │     Mist Cloud APIs       │
                   └───────────────────────────┘
```

## 🔧 Tool Categories

The MCP server organizes tools into logical categories based on Mist API structure. Use `manageMcpTools` to enable categories as needed:

### Essential Tools (Always Available)
- **`getSelf`** - Get current user and organization information
- **`manageMcpTools`** - Enable/disable tool categories dynamically

### Core Categories
- **`orgs`** - Organization management and configuration
- **`sites`** - Site-level configuration and monitoring
- **`admins`** - Administrator management and authentication

### Organization-Level Resources
- **`orgs_devices`** - Access points, switches, gateways, and device management
- **`orgs_clients___wireless`** - Wi-Fi client monitoring and statistics
- **`orgs_clients___wired`** - Wired client monitoring and statistics
- **`orgs_clients___wan`** - WAN client monitoring and statistics
- **`orgs_clients___nac`** - NAC (Network Access Control) client management
- **`orgs_alarms`** - Alarm monitoring and management
- **`orgs_inventory`** - Device inventory and asset management
- **`orgs_licenses`** - License management and tracking
- **`orgs_templates`** - WLAN, AP, Gateway, and RF templates
- **`orgs_networks`** - Network configuration and VLAN management
- **`orgs_security_policies`** - Security policy management
- **`orgs_webhooks`** - Webhook configuration and monitoring

### Site-Level Resources
- **`sites_devices`** - Site-specific device management
- **`sites_clients___wireless`** - Site wireless client statistics
- **`sites_clients___wired`** - Site wired client statistics
- **`sites_maps`** - Floor plans and location services
- **`sites_insights`** - Network performance insights
- **`sites_sles`** - Service Level Expectations monitoring
- **`sites_alarms`** - Site-specific alarm management

### Statistics & Analytics
- **`orgs_stats___devices`** - Organization device statistics
- **`orgs_stats___sites`** - Cross-site analytics
- **`orgs_stats___bgp_peers`** - BGP peer statistics (WAN)
- **`sites_stats___devices`** - Site device performance metrics
- **`sites_stats___calls`** - Call quality analytics (Zoom/Teams)

### Advanced Features
- **`orgs_marvis`** - AI-powered network assistant and troubleshooting
- **`orgs_mxedges`** - Mist Edge appliance management
- **`orgs_integration_skyatp`** - Sky ATP security integration
- **`sites_maps___auto_placement`** - AI-powered AP placement
- **`sites_rfdiags`** - RF diagnostic and analysis tools

### Reference Data
- **`constants_definitions`** - API constants and definitions
- **`constants_events`** - Event type definitions and examples
- **`constants_models`** - Hardware model specifications

### User Account
- **`self_account`** - Current user account information
- **`self_alarms`** - Personal alarm subscriptions

Use the `manageMcpTools` function to enable only the categories you need for your specific use case. Each client session maintains independent tool configurations.

## 🔄 Dynamic Tool Management

### Using manageMcpTools

The `manageMcpTools` function allows you to dynamically enable tool categories during your session:

```python
# Enable organization and site management tools
manageMcpTools(enable_mcp_tools_categories=["orgs", "sites"])

# Enable specific categories for wireless client monitoring
manageMcpTools(enable_mcp_tools_categories=["orgs_clients___wireless", "sites_clients___wireless"])

# Enable all device management tools
manageMcpTools(enable_mcp_tools_categories=["orgs_devices", "sites_devices", "orgs_stats___devices"])
```

## ⚠️ Current Limitations

- **Beta Quality**: Multi-client architecture is stable but still under active development
- **API Authentication**: Requires manual Mist API token configuration in client environment
- **Session Cleanup**: Long-running sessions may accumulate over time (automatic cleanup implemented)
- **Rate Limiting**: No built-in rate limiting for API calls
- **Error Recovery**: Limited retry logic for failed API calls
- **Tool Documentation**: Auto-generated documentation may be incomplete
- **Memory Usage**: All mode loads all tools, which may consume significant memory
- **Transport Limitations**: HTTP mode requires additional configuration for remote access

## 🆕 Recent Improvements

- **✅ Multi-Client Support**: Full session isolation between different MCP clients
- **✅ Dynamic Tool Loading**: Runtime tool management with `manageMcpTools`
- **✅ Flexible Modes**: Minimal, managed, all, and custom loading strategies
- **✅ Circular Import Fix**: Resolved architecture issues for stable startup
- **✅ Session Persistence**: Tool configurations persist during client sessions
- **✅ Transport Options**: Both stdio and HTTP transport modes
- **✅ Configuration System**: Robust server configuration and tool management

## 🤝 Contributing

Contributions are welcome! This project has evolved from a basic MCP server to a sophisticated multi-client platform. Areas where we'd appreciate help:

### Priority Areas
- **Performance optimization** for multi-client scenarios
- **Enhanced session management** features
- **API rate limiting and caching** implementation
- **Test coverage** for session isolation and tool management
- **Documentation** improvements and examples

### General Contributions
- Bug reports and fixes
- Feature requests and implementations
- Tool category refinements
- Client integration examples
- Performance benchmarking

### Development Setup

1. Clone the repository
2. Install development dependencies: `uv sync`
3. Run tests: `uv run python -m pytest`
4. Check the `FASTMCP_TOOL_METHOD_INVESTIGATION.md` for technical details

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Thomas Munzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Author

**Thomas Munzer** (tmunzer@juniper.net)
- GitHub: [@tmunzer](https://github.com/tmunzer)

---

*This project provides a bridge between AI assistants and Juniper Mist networking infrastructure, enabling natural language network management and monitoring with full multi-client session support.*
