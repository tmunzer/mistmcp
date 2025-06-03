# Mist MCP Server

A Model Context Protocol (MCP) server that provides AI-powered access to Juniper Mist networking APIs. This project enables Large Language Models (LLMs) like Claude to interact with Mist cloud-managed network infrastructure through a comprehensive set of tools.

## 📖 Overview

The Mist MCP Server consists of two main components:

1. **Code Generator** (`generate_mcp_tools.py`) - Automatically generates/updates MCP-compatible tools from the Mist OpenAPI specification
2. **MCP Server** (`src/`) - The actual MCP server that provides AI assistants with access to Mist APIs

This early-stage but functional project allows network engineers to interact with their Mist-managed infrastructure using natural language through AI assistants.

## 🚀 Features

- **Comprehensive API Coverage**: Auto-generated tools for all major Mist API endpoints
- **Dynamic Tool Management**: Enable/disable tool categories based on your needs
- **Intelligent Organization**: Tools are grouped by functionality (orgs, sites, devices, clients, etc.)
- **Type Safety**: Full type validation using Pydantic models
- **Error Handling**: Robust error handling and logging
- **AI-Optimized**: Designed specifically for LLM interaction patterns

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Mist API credentials (API token and organization access)

### 1. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### 2. Generate MCP Tools (Optional)

The repository includes pre-generated tools, but you can regenerate them:

```bash
python generate_mcp_tools.py
```

This will:
- Parse the Mist OpenAPI specification (`mist.openapi.yaml`)
- Generate categorized tool modules in `src/mistmcp/tools/`
- Create tool configuration files

### 3. Configure MCP Server

The server can be run in two modes:

#### STDIO Mode (Recommended for Claude Desktop)
```json
{
    "mcpServers": {
        "Mist MCP Server": {
            "command": "python",
            "args": [
                "-m",
                "mistmcp"
            ]
        }
    }
}
```

#### HTTP Mode (For remote access)
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

### With Claude Desktop

1. Add the server configuration to your Claude Desktop MCP settings
2. Restart Claude Desktop
3. Start a new conversation and ask about your Mist infrastructure:

```
"Show me the status of all my access points"
"What devices are having connectivity issues?"
"List all wireless clients on my guest network"
```

### With VS Code

1. Install the MCP extension for VS Code
2. Configure the server in your workspace settings
3. Use the MCP panel to interact with your Mist infrastructure

## 🏗️ Project Structure

```
mistmcp/
├── generate_mcp_tools.py          # Tool generator script
├── mist.openapi.yaml             # Mist OpenAPI specification
├── src/mistmcp/                  # MCP Server source
    ├── __init__.py              # Package initialization
    ├── __main__.py              # CLI entry point
    ├── __server.py              # FastMCP server implementation
    ├── __mistapi.py             # Mist API client wrapper
    ├── __ctools.py              # Tool configuration management
    ├── tools.json               # Tool registry
    └── tools/                   # Generated tool modules
        ├── orgs/               # Organization-level APIs
        ├── sites/              # Site-level APIs
        ├── constants_*/        # Constants and definitions
        └── ...                 # Other API categories
```

## 🔧 Tool Categories

The MCP server organizes tools into logical categories based on Mist API structure:

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

Use the `manageMcpTools` function to enable only the categories you need for your specific use case.

## ⚠️ Current Limitations

- **Early Development Stage**: This is a beta-quality project under active development
- **API Authentication**: Requires manual Mist API token configuration
- **Rate Limiting**: No built-in rate limiting for API calls
- **Error Recovery**: Limited retry logic for failed API calls
- **Documentation**: Tool documentation is auto-generated and may be incomplete
- **Testing**: Limited test coverage for generated tools
- **Caching**: No response caching implemented yet

## 🤝 Contributing

Contributions are welcome! This project is in early development and could benefit from:

- Bug reports and fixes
- Feature requests and implementations
- Documentation improvements
- Test coverage expansion
- Performance optimizations

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

*This project provides a bridge between AI assistants and Juniper Mist networking infrastructure, enabling natural language network management and monitoring.*