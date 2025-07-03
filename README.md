# Mist MCP Server

A Model Context Protocol (MCP) server that provides AI-powered access to Juniper Mist networking APIs. This project enables Large Language Models (LLMs) like Claude to interact with Mist cloud-managed network infrastructure through a comprehensive set of tools.

## ⚠️ Important Notice

**Claude Desktop Compatibility**: There is a [known issue](https://github.com/anthropics/claude-code/issues/2230) where Claude Desktop may display a blank screen when MCP tools return large data payloads. This can occur with Mist API calls that return extensive device lists, client information, or statistics. If you experience a blank screen, refresh Claude Desktop to restore the interface. Consider using more specific filters or smaller data requests to minimize this issue.

## 📑 Table of Contents

- [⚠️ Important Notice](#️-important-notice)
- [🚀 Features](#-features)
- [🛠️ Installation & Setup](#️-installation--setup)
  - [Prerequisites](#prerequisites)
  - [1. Install Dependencies](#1-install-dependencies)
- [🚀 Usage](#-usage)
  - [Command Line Options](#command-line-options)
  - [Environment Variables](#environment-variables)
  - [Tool Loading Modes](#tool-loading-modes)
  - [Transport Modes](#transport-modes)
- [🔧 Configuration](#-configuration)
  - [STDIO Mode (Recommended)](#stdio-mode-recommended)
  - [HTTP Mode (Remote Access)](#http-mode-remote-access)
  - [HTTP Mode Query Parameters](#http-mode-query-parameters)
- [🔧 Tool Categories](#-tool-categories)
- [⚠️ Current Limitations](#️-current-limitations)
- [🤝 Contributing](#-contributing)
  - [Development Setup](#development-setup)
- [📄 License](#-license)
- [👤 Author](#-author)

## 🚀 Features

- **📡 Transport Flexibility**: Supports both STDIO and HTTP transport modes
- **🎯 Simple Loading Modes**: Managed or All tool loading (both load all tools at startup)
- **🏗️ Intelligent Organization**: Tools grouped by functionality (orgs, sites, devices, clients, etc.)
- **🛡️ Type Safety**: Full type validation using Pydantic models
- **🤖 AI-Optimized**: Designed specifically for LLM interaction patterns
- **⚡ Simplified Architecture**: Single-user, stateless server design

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+ (managed by uv)
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer
- Mist API credentials (API token)

### 1. Install Dependencies

```bash
make init # Installs project dependencies and extracts the git submodule for mist_openapi
```

## 🚀 Usage

Before running the server ensure that the mist_openapi submodule is available and that the generated code is up to date. You can do this by running:

```bash
make generate
```

### Command Line Options

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

EXAMPLES:
    uv run mistmcp                                    # Default: stdio + managed mode
    uv run mistmcp --mode all --debug                 # All tools with debug
    uv run mistmcp --transport http --host 0.0.0.0    # HTTP on all interfaces
    uv run mistmcp --env-file ~/.mist.env             # Custom env file
```

### Environment Variables

Configure via environment variables or `.env` files:

| Parameter | STDIO Mode | HTTP Mode | Default Value | Description |
|-----------|------------|-----------|---------------|-------------|
| `MIST_APITOKEN` | **Required** | Not used | - | Your Mist API token for authentication |
| `MIST_HOST` | **Required** | Not used | - | Mist API host (e.g., `api.mist.com`, `api.eu.mist.com`) |
| `MIST_ENV_FILE` | Optional | Not used | - | Path to .env file containing Mist credentials |
| `MISTMCP_TOOL_LOADING_MODE` | Optional | Not used | `all` | Tool loading strategy: `managed` or `all` |
| `MISTMCP_TRANSPORT_MODE` | Optional | **Required**  | `stdio` | Transport mode: `stdio` or `http` |
| `MISTMCP_HOST` | Not used | Optional | `127.0.0.1` | HTTP server bind address |
| `MISTMCP_PORT` | Not used | Optional | `8000` | HTTP server port |
| `MISTMCP_DEBUG` | Optional | Optional | `false` | Enable debug logging: `true` or `false` |

> **💡 Note:** `MIST_APITOKEN` and `MIST_HOST` can be provided either directly or via a `.env` file specified in `MIST_ENV_FILE`.

### Tool Loading Modes

| Mode | Description | Memory Usage | Use Case |
|------|-------------|--------------|----------|
| **managed** (default) | Essential tools loaded at startup, others available on demand | Low | Most users |
| **all** | All tools loaded at startup | High | Power users, automation |

> **Note:** In managed mode, only essential tools like `getSelf` are loaded initially. In all mode, all 110+ tools are loaded at startup.

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

> ~/Library/Application Support/Claude Desktop/claude_desktop_config.json - on 'Claude for Mac Version 0.11.6'

**Claude Desktop (`~/.claude_desktop/claude_desktop_config.json`) or VS Code MCP Extension (`.vscode/settings.json`):**

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
                "managed"
            ],
            "env": {
                "MIST_APITOKEN": "your-api-token",
                "MIST_HOST": "api.mist.com"
            }
        }
    }
}
```

⚠️ **WARNING** ⚠️

If you're application is not able to run `uv` commands, you can use the full path to the `uv` executable in the `command` field, e.g. `/Users/username/.local/bin/uv`.

### HTTP Mode (Remote Access)

Since most of the LLM Applications are not supporting the streamable-http transport mode natively, you can use the `mcp-remote` package to create a remote HTTP server that can be used by these applications.

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
                "-y",
                "mcp-remote",
                "http://127.0.0.1:8000/mcp/?cloud=api.mist.com",
                "--header",
                "X-Authorization:${MIST_APITOKEN}",
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

⚠️ **WARNING** ⚠️

If your laptop has SSL interception enabled (e.g. corporate network), you may need to add the following environment variable to your configuration:

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
                "X-Authorization:${MIST_APITOKEN}",
                "--transport",
                "http-only"
            ],
            "env": {
                "MIST_APITOKEN": "your-api-token"
                "NODE_EXTRA_CA_CERTS": "{your CA certificate file path}.pem"
            }
        }
    }
}
```

#### HTTP Mode Query Parameters

When using HTTP transport, configure the server via URL query parameters:

**Required:**

- `cloud` - Mist API host (e.g., `api.mist.com`)

**Example URLs:**

```bash
# Default managed mode
http://localhost:8000/mcp/?cloud=api.mist.com

# All tools with debug enabled
http://localhost:8000/mcp/?cloud=api.mist.com&mode=all&debug=true
```

## 🔧 Tool Categories

The server organizes tools into logical categories. Use `manageMcpTools` to enable categories as needed:

### Essential Tools (Always Available)

- **`getSelf`** - User and organization information
- **`manageMcpTools`** - Enable/disable tool categories dynamically (only in managed mode)

### Available Tool Categories

| Category | Description | Tools | Tool List |
|----------|-------------|-------|-----------|
| **clients** | Clients related objects for the sites and organizations. | 11 | `searchOrgWirelessClientEvents`, `searchOrgWirelessClients`, `searchOrgWirelessClientSessions`, `searchOrgGuestAuthorization`, `searchOrgNacClientEvents`, `searchOrgNacClients`, `searchOrgWanClientEvents`, `searchOrgWanClients`, `searchOrgWiredClients`, `listSiteRoamingEvents`, `searchSiteGuestAuthorization` |
| **configuration** | Configuration related objects for the sites and organizations. | 2 | `getOrgConfigurationObjects`, `getSiteConfigurationObjects` |
| **constants_definitions** | tools to retrieve constant values that can be used in different parts of the configuration | 4 | `listFingerprintTypes`, `listInsightMetrics`, `listLicenseTypes`, `listWebhookTopics` |
| **devices** | Devices are any Network device managed or monitored by Juniper Mist. | 11 | `searchOrgDeviceEvents`, `listOrgApsMacs`, `searchOrgDevices`, `listOrgDevicesSummary`, `getOrgInventory`, `searchOrgMistEdgeEvents`, `searchSiteDeviceConfigHistory`, `searchSiteDeviceEvents`, `searchSiteDeviceLastConfigs`, `searchSiteDevices`, `searchSiteMistEdgeEvents` |
| **marvis** | Marvis is a virtual network assistant that provides insights and analytics for the Mist network. | 3 | `troubleshootOrg`, `getSiteDeviceSyntheticTest`, `searchSiteSyntheticTest` |
| **orgs** | An organization usually represents a customer - which has inventories, licenses. | 10 | `getOrg`, `searchOrgAlarms`, `listOrgSuppressedAlarms`, `GetOrgLicenseAsyncClaimStatus`, `searchOrgEvents`, `getOrgLicensesSummary`, `getOrgLicensesBySite`, `listOrgAuditLogs`, `getOrgSettings`, `searchOrgSites` |
| **orgs_nac** | NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules. | 2 | `searchOrgUserMacs`, `searchOrgClientFingerprints` |
| **orgs_stats** | Statistics for the organizations. It provides access to various statistics related to the organization, such as BGP peers, devices, MX edges, other devices, ports, sites, tunnels, and VPN peers. | 10 | `getOrgStats`, `searchOrgBgpStats`, `listOrgDevicesStats`, `listOrgMxEdgesStats`, `getOrgMxEdgeStats`, `getOrgOtherDeviceStats`, `searchOrgSwOrGwPorts`, `listOrgSiteStats`, `searchOrgTunnelsStats`, `searchOrgPeerPathStats` |
| **orgs_wxtags** | Wxtags are tags or groups that can be created and used within the Org. | 2 | `getOrgApplicationList`, `getOrgCurrentMatchingClientsOfAWxTag` |
| **self_account** | tools related to the currently connected user account. | 4 | `getSelf`, `getSelfLoginFailures`, `listSelfAuditLogs`, `getSelfApiUsage` |
| **sites** | A site represents a project, a deployment. For MSP, it can be as small as a coffee shop or a five-star 600-room hotel. A site contains a set of Maps, Wlans, Policies, Zones. | 3 | `getSiteInfo`, `getSiteSetting`, `getSiteSettingDerived` |
| **sites_insights** | Insights is a feature that provides an overview of network experience across the entire site, access points, or clients. | 3 | `getSiteInsightMetricsForClient`, `getSiteInsightMetricsForDevice`, `getSiteInsightMetrics` |
| **sites_rfdiags** | Rf Diags is a feature in Juniper Mist location services that allows users to replay recorded sessions of the RF (radio frequency) environment. | 2 | `getSiteSiteRfdiagRecording`, `getSiteRfdiagRecording` |
| **sites_rogues** | Rogues are unauthorized wireless access points that are installed on a network without authorization. | 3 | `listSiteRogueAPs`, `listSiteRogueClients`, `searchSiteRogueEvents` |
| **sites_rrm** | RRM, or Radio Resource Management, is a tool used by large multi-site organizations to efficiently manage their RF spectrum. | 4 | `getSiteCurrentChannelPlanning`, `getSiteCurrentRrmConsiderations`, `listSiteRrmEvents`, `listSiteCurrentRrmNeighbors` |
| **sites_services** | A Service represents an a traffic destination or an application that network users connect to. | 1 | `searchSiteServicePathEvents` |
| **sites_stats** | Statistics for the sites. It provides access to various statistics related to the site, such as application statistics, call statistics, client statistics, and more. | 13 | `getSiteStats`, `troubleshootSiteCall`, `searchSiteCalls`, `getSiteCallsSummary`, `listSiteTroubleshootCalls`, `listSiteWirelessClientsStats`, `searchSiteDiscoveredSwitchesMetrics`, `listSiteDiscoveredSwitchesMetrics`, `searchSiteDiscoveredSwitches`, `listSiteMxEdgesStats`, `getSiteWxRulesUsage`, `searchSiteWanUsage`, `getSiteApplicationList` |
| **sles** | SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network. | 17 | `getOrgSitesSle`, `getOrgSle`, `getSiteSleClassifierDetails`, `listSiteSleMetricClassifiers`, `getSiteSleHistogram`, `getSiteSleImpactSummary`, `listSiteSleImpactedApplications`, `listSiteSleImpactedAps`, `listSiteSleImpactedChassis`, `listSiteSleImpactedWiredClients`, `listSiteSleImpactedGateways`, `listSiteSleImpactedInterfaces`, `listSiteSleImpactedSwitches`, `listSiteSleImpactedWirelessClients`, `getSiteSleSummary`, `getSiteSleThreshold`, `listSiteSlesMetrics` |
| **utilities_upgrade** | tools used to manage device upgrades for a single device, at the site level or at the organization level. | 3 | `listUpgrades`, `listOrgAvailableDeviceVersions`, `listOrgAvailableSsrVersions` |
| **webhooks_deliveries** | A Webhook is a configuration that allows real-time events and data from the Org to be pushed to a provided url. | 2 | `searchOrgWebhooksDeliveries`, `searchSiteWebhooksDeliveries` |

Each client session maintains independent tool configurations for complete isolation.

## ⚠️ Current Limitations

- **API Authentication**: Requires manual Mist API token configuration
- **Rate Limiting**: No built-in rate limiting for API calls

## 🤝 Contributing

Contributions welcome! Priority areas:

- **Performance optimization**
- **API rate limiting and caching** implementation
- **Test coverage** improvements
- **Documentation** improvements and examples

### Development Setup

1. Clone the repository
2. Install dependencies: `uv sync`
3. Run tests: `uv run python -m pytest`

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**Thomas Munzer** (<tmunzer@juniper.net>)

- GitHub: [@tmunzer](https://github.com/tmunzer)

---

*AI-powered bridge between LLMs and Juniper Mist networking infrastructure.*
