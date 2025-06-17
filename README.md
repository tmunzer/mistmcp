# Mist MCP Server

A Model Context Protocol (MCP) server that provides AI-powered access to Juniper Mist networking APIs with **multi-client session management**. This project enables Large Language Models (LLMs) like Claude to interact with Mist cloud-managed network infrastructure through a comprehensive set of tools.


## 📑 Table of Contents

- [🚀 Features](#-features)
- [⚠️ Compatibility Notice](#️-compatibility-notice)
    - [Alternative Configurations](#alternative-configurations)
- [🛠️ Installation & Setup](#️-installation--setup)
    - [Prerequisites](#prerequisites)
    - [1. Install Dependencies](#1-install-dependencies)
- [🚀 Usage](#-usage)
    - [Command Line Options](#command-line-options)
    - [HTTP Mode Query Parameters](#http-mode-query-parameters)
    - [Environment Variables](#environment-variables)
    - [Tool Loading Modes](#tool-loading-modes)
    - [Transport Modes](#transport-modes)
- [🔧 Configuration](#-configuration)
    - [STDIO Mode (Recommended)](#stdio-mode-recommended)
    - [HTTP Mode (Remote Access)](#http-mode-remote-access)
    - [Example .env File](#example-env-file)
- [📊 Getting Started](#-getting-started)
    - [Quick Start Workflow](#quick-start-workflow)
    - [Example Usage](#example-usage)
- [🔄 Dynamic Tool Management](#-dynamic-tool-management)
- [🔧 Tool Categories](#-tool-categories)
    - [Essential Tools (Always Available)](#essential-tools-always-available)
    - [Core Categories](#core-categories)
    - [Device Management](#device-management)
    - [Client Monitoring](#client-monitoring)
    - [Network & Security](#network--security)
    - [Monitoring & Analytics](#monitoring--analytics)
    - [Advanced Features](#advanced-features)
- [⚠️ Current Limitations](#️-current-limitations)
- [🤝 Contributing](#-contributing)
    - [Development Setup](#development-setup)
- [📄 License](#-license)
- [👤 Author](#-author)


## 🚀 Features

- **🌍 Multi-Client Architecture**: Multiple MCP clients can connect simultaneously with independent tool configurations
- **🔄 Dynamic Tool Management**: Enable/disable tool categories at runtime per client session
- **📊 Session Isolation**: Complete isolation between different client sessions
- **🎯 Flexible Loading Modes**: Managed (default), All, or Custom tool loading strategies
- **📡 Transport Flexibility**: Supports both STDIO and HTTP transport modes
- **🏗️ Intelligent Organization**: Tools grouped by functionality (orgs, sites, devices, clients, etc.)
- **🛡️ Type Safety**: Full type validation using Pydantic models
- **🤖 AI-Optimized**: Designed specifically for LLM interaction patterns

## ⚠️ Compatibility Notice

**Dynamic Tool Management Requirement**: The managed mode (default) leverages MCP's dynamic tool discovery feature for optimal performance and memory usage. However, this feature has limited client support.

**Important**: Before using managed mode, verify your MCP client supports dynamic tool discovery in the [official MCP client feature matrix](https://modelcontextprotocol.io/clients#feature-support-matrix).

### Alternative Configurations

If your client doesn't support dynamic discovery:

```bash
# Use 'all' mode to load all tools at startup
uv run mistmcp --mode all

# Or use 'custom' mode with specific categories
uv run mistmcp --mode custom --categories orgs,sites,devices
```


## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+ (managed by uv)
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer
- Mist API credentials (API token)

### 1. Install Dependencies

```bash
uv sync
```

## 🚀 Usage

### Command Line Options

```bash
uv run mistmcp [OPTIONS]

OPTIONS:
    -t, --transport MODE    Transport mode: stdio (default) or http
    -m, --mode MODE         Tool loading mode: managed (default), all, custom
    -c, --categories LIST   Comma-separated tool categories (for custom mode)
    --host HOST             HTTP server host (default: 127.0.0.1)
    -e, --env-file PATH     Path to .env file
    -d, --debug             Enable debug output
    -h, --help              Show help message

EXAMPLES:
    uv run mistmcp                                    # Default: stdio + managed mode
    uv run mistmcp --mode all --debug                 # All tools with debug
    uv run mistmcp --transport http --host 0.0.0.0    # HTTP on all interfaces
    uv run mistmcp --mode custom --categories orgs,sites
```

### HTTP Mode Query Parameters

When using HTTP transport, configure the server via URL query parameters:

**Required:**
- `cloud` - Mist API host (e.g., `api.mist.com`)

**Optional:**
- `mode` - Tool loading mode: `managed` (default), `all`, or `custom`
- `categories` - Comma-separated tool categories (for custom mode)
- `debug` - Enable debug output: `true` or `false`

**Example URLs:**
```bash
# Default managed mode
http://localhost:8000/mcp/?cloud=api.mist.com

# All tools with debug enabled
http://localhost:8000/mcp/?cloud=api.mist.com&mode=all&debug=true

# Custom mode with specific categories
http://localhost:8000/mcp/?cloud=api.mist.com&mode=custom&categories=orgs,sites,devices
```

### Environment Variables

Configure via environment variables or `.env` files:

**Required for STDIO mode:**
- `MIST_APITOKEN` - Your Mist API token
- `MIST_HOST` - Mist API host (e.g., `api.mist.com`)

**Optional configuration:**
- `MIST_ENV_FILE` - Path to .env file
- `MISTMCP_TRANSPORT_MODE` - `stdio` or `http`
- `MISTMCP_TOOL_LOADING_MODE` - `managed`, `all`, or `custom`
- `MISTMCP_TOOL_CATEGORIES` - Comma-separated categories
- `MISTMCP_HOST` - HTTP server host
- `MISTMCP_DEBUG` - `true` or `false`


**Getting your Mist API Token:**
1. Log into Mist Dashboard → Organization → Settings → API Tokens
2. Create a new token with appropriate permissions

### Tool Loading Modes

| Mode | Description | Memory Usage | Use Case |
|------|-------------|--------------|----------|
| **managed** (default) | Only essential tools loaded, others enabled on-demand | Lowest | Recommended for most users |
| **all** | All tools loaded at startup | Highest | Power users, automation |
| **custom** | Pre-load specific categories | Medium | Tailored configurations |

### Transport Modes

| Feature | STDIO | HTTP |
|---------|-------|------|
| **Performance** | Fastest | Network latency |
| **Access** | Local only | Remote accessible |
| **Setup** | Simple | Network configuration |
| **Security** | Process isolation | Network security required |
| **Use Case** | Claude Desktop, VS Code | Remote clients, web services |



## 🔧 Configuration

### STDIO Mode (Recommended)

Best for local usage with Claude Desktop or VS Code.

**Claude Desktop (`~/.claude_desktop/claude_desktop_config.json`) or VS Code MCP Extension (`.vscode/settings.json`):**
```json
{
    "mcpServers": {
        "mist-mcp-one": {
            "command": "uv",
            "args": ["run", "mistmcp", "--mode", "managed"],
            "cwd": "/absolute/path/to/mistmcp",
            "env": {
                "MIST_APITOKEN": "your-api-token",
                "MIST_HOST": "api.mist.com"
            }
        },
        "mist-mcp-two": {
            "command": "uv",
            "args": ["run", "mistmcp", "--mode", "custom", "--categories", "orgs,sites"],
            "cwd": "/absolute/path/to/mistmcp",
            "env": {
                "MIST_ENV_FILE": ".env"
            }
        }
    }
}
```

### HTTP Mode (Remote Access)

**Start HTTP Server:**
```bash
uv run mistmcp --transport http --host 0.0.0.0 --mode managed
```

**Claude Desktop HTTP Configuration:**
```json
{
    "mcpServers": {
        "mist-http": {
            "command": "npx",
            "args": [
                "-y", "mcp-remote",
                "http://localhost:8000/mcp/?cloud=api.mist.com&mode=managed",
                "--header", "X-Authorization:${MIST_APITOKEN}",
                "--transport", "http-only"
            ],
            "env": {
                "MIST_APITOKEN": "your-api-token"
            }
        }
    }
}
```

### Example .env File

Create a `.env` file in your project root:

```bash
# Required for STDIO mode
MIST_APITOKEN=your-mist-api-token-here
MIST_HOST=api.mist.com

# Optional configurations
MISTMCP_TRANSPORT_MODE=stdio
MISTMCP_TOOL_LOADING_MODE=managed
MISTMCP_DEBUG=false
MISTMCP_HOST=127.0.0.1
```


## 📊 Getting Started

### Quick Start Workflow

1. **Configure your MCP client** (Claude Desktop, VS Code, etc.)
2. **Start with managed mode** - All sessions begin with `getSelf` and `manageMcpTools`
3. **Enable tools dynamically** - Use `manageMcpTools` to enable tool categories as needed
4. **Query your network** - Ask natural language questions about your Mist infrastructure

### Example Usage

```
# 1. Get organization info
User: "Show me my organization details"

# 2. Enable and use device tools
User: "Find all offline access points"
Assistant: "I'll enable device management tools first..."
[Calls manageMcpTools with device categories]
Assistant: "Tools enabled! Do you want to continue?"
User: "Yes"
[Assistant will use the enabled tools to find the information]

# 3. Network troubleshooting
User: "Why users on the guest network can't access the internet?"
[Calls manageMcpTools with device categories]
Assistant: "Tools enabled! Do you want to continue?"
User: "Yes"
[Assistant will use the enabled tools to find the information]
```

## 🔄 Dynamic Tool Management

Use `manageMcpTools` to enable tool categories during your session:

```python
# Enable organization and site management
manageMcpTools(enable_mcp_tools_categories=["orgs", "sites"])

# Enable wireless client monitoring
manageMcpTools(enable_mcp_tools_categories=["orgs_clients___wireless"])

# Enable comprehensive device management
manageMcpTools(enable_mcp_tools_categories=["orgs_devices", "sites_devices"])
```


## 🔧 Tool Categories

The server organizes tools into logical categories. Use `manageMcpTools` to enable categories as needed:

### Essential Tools (Always Available)
- **`getSelf`** - User and organization information
- **`manageMcpTools`** - Enable/disable tool categories dynamically

### Core Categories
- **`orgs`** - Organization management
- **`sites`** - Site-level configuration
- **`admins`** - Administrator management

### Device Management
- **`orgs_devices`** - Organization-wide device management
- **`sites_devices`** - Site-specific device management
- **`orgs_inventory`** - Device inventory and assets

### Client Monitoring
- **`orgs_clients___wireless`** - Wi-Fi client statistics
- **`orgs_clients___wired`** - Wired client monitoring
- **`orgs_clients___wan`** - WAN client monitoring
- **`orgs_clients___nac`** - NAC client management

### Network & Security
- **`orgs_networks`** - Network and VLAN configuration
- **`orgs_security_policies`** - Security policy management
- **`orgs_templates`** - WLAN, AP, Gateway templates

### Monitoring & Analytics
- **`orgs_alarms`** - Alarm monitoring
- **`sites_insights`** - Network performance insights
- **`orgs_stats___devices`** - Device statistics
- **`sites_stats___calls`** - Call quality analytics

### Advanced Features
- **`orgs_marvis`** - AI-powered network assistant
- **`sites_maps___auto_placement`** - AI-powered AP placement
- **`orgs_integration_skyatp`** - Sky ATP security integration

Each client session maintains independent tool configurations for complete isolation.

## ⚠️ Current Limitations

- **Beta Quality**: Multi-client architecture is stable but under active development
- **API Authentication**: Requires manual Mist API token configuration
- **Rate Limiting**: No built-in rate limiting for API calls
- **Memory Usage**: "All" mode loads all tools, consuming significant memory

## 🤝 Contributing

Contributions welcome! Priority areas:
- **Performance optimization** for multi-client scenarios
- **API rate limiting and caching** implementation
- **Test coverage** for session isolation
- **Documentation** improvements and examples

### Development Setup

1. Clone the repository
2. Install dependencies: `uv sync`
3. Run tests: `uv run python -m pytest`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**Thomas Munzer** (tmunzer@juniper.net)
- GitHub: [@tmunzer](https://github.com/tmunzer)

---

*AI-powered bridge between LLMs and Juniper Mist networking infrastructure with multi-client session support.*
