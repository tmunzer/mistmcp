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
- **⚙️ Flexible Loading Modes**: Choose from minimal, managed, all, or custom tool loading strategies
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

### Prerequisites

- Python 3.10 or higher (uv will manage this)
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Mist API credentials (API token and organization access)

### 1. Install Dependencies

```bash
uv sync
```

### 2. Generate MCP Tools (Optional)

The repository includes pre-generated tools, but you can regenerate them:

```bash
uv run python generate_from_openapi.py
```

This will:
- Parse the Mist OpenAPI specification (`mist_openapi/mist.openapi.yaml`)
- Generate categorized tool modules in `src/mistmcp/tools/`
- Create tool configuration files

### 3. Run the MCP Server

The server supports multiple modes and transport options:

#### Command Line Options

```bash
uv run mistmcp [OPTIONS]

OPTIONS:
    -h, --help              Show help message
    -t, --transport MODE    Transport mode: stdio (default) or http
    -m, --mode MODE         Tool loading mode: minimal, managed (default), all, custom
    -c, --categories LIST   Comma-separated tool categories (for custom mode)
    -d, --debug             Enable debug output

EXAMPLES:
    uv run mistmcp                                    # Default managed mode
    uv run mistmcp --mode minimal                     # Minimal tools only
    uv run mistmcp --mode all                         # All tools loaded
    uv run mistmcp --transport http --mode managed    # HTTP transport
    uv run mistmcp --mode custom --categories orgs,sites --debug
```

#### Tool Loading Modes

- **`minimal`** - Load only essential tools (`getSelf`, `manageMcpTools`)
- **`managed`** - Use dynamic tool management (default) - tools enabled on demand
- **`all`** - Load all available tools at startup
- **`custom`** - Load specific categories (requires `--categories`)

### 4. Configure MCP Client

#### STDIO Mode (Recommended for Claude Desktop)
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
            "cwd": "/path/to/mistmcp"
        }
    }
}
```

#### HTTP Mode (For remote access)
Start the server in HTTP mode:
```bash
uv run mistmcp --transport http --mode managed
```

Then configure your MCP client:
```json
{
    "mcpServers": {
        "Mist MCP Server": {
            "command": "npx",
            "args": [
                "mcp-remote",
                "http://127.0.0.1:8000/mcp/"
            ]
        }
    }
}
```

## 📋 Usage

### Multi-Client Session Management

Each MCP client that connects to the server gets its own independent session with:
- **Separate tool configurations** - Enable different tools per client
- **Session isolation** - No interference between clients
- **Dynamic tool management** - Add/remove tools at runtime per session

### Getting Started

1. **Connect your MCP client** (Claude Desktop, VS Code, etc.)
2. **Start with essential tools** - All sessions begin with `getSelf` and `manageMcpTools`
3. **Enable tools as needed** - Use `manageMcpTools` to enable tool categories
4. **Query your infrastructure** - Ask natural language questions about your Mist network

### Example Workflow

```
# 1. Get your organization info
"Show me my organization details"

# 2. Enable site management tools
"Enable site management tools so I can see my sites"
# (This will call manageMcpTools automatically)

# 3. Explore your network
"List all my sites and their status"
"Show me access points that are offline"
"What wireless clients are connected to my guest network?"
"Which devices need firmware updates?"
```

### With Claude Desktop

1. Add the server configuration to your Claude Desktop MCP settings
2. Restart Claude Desktop
3. Start a new conversation - the server begins in `managed` mode
4. Enable tools as needed using natural language:
   ```
   "I need to check my access points - enable the device management tools"
   "Show me wireless client statistics - enable those tools first"
   "Enable organization and site tools so I can manage my network"
   ```

### With VS Code MCP Extension

1. Install the MCP extension for VS Code
2. Configure the server in your workspace settings
3. Use the MCP panel to interact with your Mist infrastructure
4. Each VS Code instance maintains its own tool session

### Session Management Features

- **Independent Sessions**: Multiple clients can connect with different tool configurations
- **Session Persistence**: Tool configurations persist during the client session
- **Dynamic Updates**: Enable/disable tools without restarting the server
- **Fallback Behavior**: Graceful degradation when session context is unavailable

## 🏗️ Project Structure

```
mistmcp/
├── generate_from_openapi.py         # Tool generator script
├── mist_openapi/
│   └── mist.openapi.yaml           # Mist OpenAPI specification
├── src/mistmcp/                    # MCP Server source
│   ├── __init__.py                # Package initialization
│   ├── __main__.py                # CLI entry point
│   ├── __version.py               # Version information
│   ├── config.py                  # Server configuration system
│   ├── constants.py               # Constants and defaults
│   ├── server_factory.py          # Server creation and configuration
│   ├── session_aware_server.py    # Session-aware FastMCP implementation
│   ├── session_manager.py         # Multi-client session management
│   ├── session_middleware.py      # Session middleware components
│   ├── session_tools.py           # Session-aware tool decorators
│   ├── tool_loader.py             # Dynamic tool loading system
│   ├── tool_manager.py            # manageMcpTools implementation
│   ├── tool_helper.py            # Tool category definitions
│   ├── tools.json                 # Tool registry and configuration
│   └── tools/                     # Generated tool modules
│       ├── orgs/                  # Organization-level APIs
│       ├── sites/                 # Site-level APIs
│       ├── constants_*/           # Constants and definitions
│       └── ...                    # Other API categories
└── FASTMCP_TOOL_METHOD_INVESTIGATION.md  # Technical documentation
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
                    │  │ ┌─────┐ ┌─────────┐ │  │
                    │  │ │Sess1│ │  Sess2  │ │  │
                    │  │ │Tools│ │ Tools   │ │  │
                    │  │ └─────┘ └─────────┘ │  │
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

### Tool Loading Modes

1. **Minimal Mode** (`--mode minimal`)
   - Only `getSelf` and `manageMcpTools` loaded
   - Lowest memory footprint
   - Tools enabled on-demand via `manageMcpTools`

2. **Managed Mode** (`--mode managed`) - **Default**
   - Starts with essential tools only
   - Dynamic tool loading based on user requests
   - Optimal balance of performance and functionality

3. **All Mode** (`--mode all`)
   - All available tools loaded at startup
   - Maximum functionality, higher memory usage
   - Best for power users or automated scenarios

4. **Custom Mode** (`--mode custom --categories orgs,sites`)
   - Pre-load specific tool categories
   - Tailored configuration for specific use cases
   - Requires explicit category specification

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

### Best Practices

1. **Start Small**: Begin with essential tools and add categories as needed
2. **Session-Specific**: Each client can have different tool configurations
3. **Context Aware**: Enable tools based on your current task
4. **Clean Up**: Disable unused tools to reduce cognitive load

### Example Workflow

```
User: "I need to check my network devices"
Assistant: "I'll enable device management tools first..."
[Calls manageMcpTools with device categories]
Assistant: "Tools enabled! Now let me check your devices..."
[Proceeds with device queries]
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
