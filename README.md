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

| Parameter | STDIO Mode | HTTP Mode | Default Value | Description |
|-----------|------------|-----------|---------------|-------------|
| `MIST_APITOKEN` | **Required** | Not used | - | Your Mist API token for authentication |
| `MIST_HOST` | **Required** | Not used | - | Mist API host (e.g., `api.mist.com`, `api.eu.mist.com`) |
| `MIST_ENV_FILE` | Optional | Optional | - | Path to .env file containing Mist credentials |
| `MISTMCP_TRANSPORT_MODE` | Optional | **Required** | `stdio` | Transport mode: `stdio` or `http` |
| `MISTMCP_TOOL_LOADING_MODE` | Optional | Optional | `managed` | Tool loading strategy: `managed`, `all`, or `custom` |
| `MISTMCP_TOOL_CATEGORIES` | Optional | Optional | - | Comma-separated list of tool categories (for `custom` mode) |
| `MISTMCP_HOST` | Not used | Optional | `127.0.0.1` | HTTP server bind address |
| `MISTMCP_PORT` | Not used | Optional | `8000` | HTTP server port |
| `MISTMCP_DEBUG` | Optional | Optional | `false` | Enable debug logging: `true` or `false` |

> **💡 Note:** `MIST_APITOKEN` and `MIST_HOST` can be provided either directly or via a `.env` file specified in `MIST_ENV_FILE`.


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
        },
        "mist-mcp-two": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/mistmcp",
                "run",
                "mistmcp",
                "--mode",
                "custom",
                "--categories",
                "orgs,sites"
            ],
            "env": {
                "MIST_ENV_FILE": ".env"
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
            ...
            "env": {
                "NODE_EXTRA_CA_CERTS": "{your CA certificate file path}.pem"
            }
        }
    }
}
```


## 🔧 Tool Categories

The server organizes tools into logical categories. Use `manageMcpTools` to enable categories as needed:

### Essential Tools (Always Available)
- **`getSelf`** - User and organization information
- **`manageMcpTools`** - Enable/disable tool categories dynamically (only in managed mode)

### Available Tool Categories

| Category | Description | Tools | Tool List |
|----------|-------------|-------|-----------|
| **clients** | Clients related objects for the sites and organizations. | 25 | `countOrgWirelessClients`, `countOrgWirelessClientEvents`, `searchOrgWirelessClientEvents`, `searchOrgWirelessClients`, `countOrgWirelessClientsSessions`, `searchOrgWirelessClientSessions`, `listOrgGuestAuthorizations`, `countOrgGuestAuthorizations`, `searchOrgGuestAuthorization`, `getOrgGuestAuthorization`, `countOrgNacClients`, `countOrgNacClientEvents`, `searchOrgNacClientEvents`, `searchOrgNacClients`, `countOrgWanClientEvents`, `countOrgWanClients`, `searchOrgWanClientEvents`, `searchOrgWanClients`, `countOrgWiredClients`, `searchOrgWiredClients`, `listSiteAllGuestAuthorizations`, `countSiteGuestAuthorizations`, `listSiteAllGuestAuthorizationsDerived`, `searchSiteGuestAuthorization`, `getSiteGuestAuthorization` |
| **constants_definitions** | tools to retrieve constant values that can be used in different parts of the configuration | 6 | `listApChannels`, `listApLedDefinition`, `listFingerprintTypes`, `listInsightMetrics`, `listLicenseTypes`, `listWebhookTopics` |
| **devices** | Devices are any Network device managed or monitored by Juniper Mist. | 15 | `countOrgDevices`, `countOrgDeviceEvents`, `searchOrgDeviceEvents`, `listOrgApsMacs`, `searchOrgDevices`, `listOrgDevicesSummary`, `getOrgJuniperDevicesCommand`, `listSiteDevices`, `countSiteDeviceConfigHistory`, `searchSiteDeviceConfigHistory`, `searchSiteDeviceEvents`, `exportSiteDevices`, `countSiteDeviceLastConfig`, `searchSiteDeviceLastConfigs`, `searchSiteDevices` |
| **marvis** | Marvis is a virtual network assistant that provides insights and analytics for the Mist network. | 2 | `troubleshootOrg`, `searchSiteSyntheticTest` |
| **mxedges** | MX Edge related objects for the organizations. It provides access to Mist Edges, Mist Clusters, and Mist Tunnels. | 11 | `listOrgMxEdgeClusters`, `listOrgMxEdges`, `countOrgMxEdges`, `countOrgSiteMxEdgeEvents`, `searchOrgMistEdgeEvents`, `searchOrgMxEdges`, `getOrgMxEdgeUpgradeInfo`, `listOrgMxTunnels`, `listSiteMxEdges`, `countSiteMxEdgeEvents`, `searchSiteMistEdgeEvents` |
| **orgs** | An organization usually represents a customer - which has inventories, licenses. | 5 | `getOrg`, `countOrgAlarms`, `searchOrgAlarms`, `searchOrgEvents`, `getOrgSettings` |
| **orgs_inventory** | The Org Inventory allows administrators to view and manage all devices registered (claimed) to the Organization. | 3 | `getOrgInventory`, `countOrgInventory`, `searchOrgInventory` |
| **orgs_licenses** | Licenses are a type of service or access that customers can purchase for various features or services offered by a company. | 3 | `GetOrgLicenseAsyncClaimStatus`, `getOrgLicensesSummary`, `getOrgLicensesBySite` |
| **orgs_logs** | Audit Logs are records of activities initiated by users, providing a history of actions such as accessing, creating, updating, or deleting resources... | 2 | `listOrgAuditLogs`, `countOrgAuditLogs` |
| **orgs_nac** | NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules. | 5 | `listOrgNacRules`, `listOrgNacTags`, `searchOrgUserMacs`, `countOrgClientFingerprints`, `searchOrgClientFingerprints` |
| **orgs_sites** | tools to Create or Get the Organization Sites. | 4 | `listOrgSiteGroups`, `countOrgSites`, `searchOrgSites`, `listOrgSiteTemplates` |
| **orgs_sles** | Org SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network. | 2 | `getOrgSitesSle`, `getOrgSle` |
| **orgs_stats** | Statistics for the organizations. It provides access to various statistics related to the organization, such as BGP peers, devices, MX edges, other devices, ports, sites, tunnels, and VPN peers. | 13 | `getOrgStats`, `countOrgBgpStats`, `searchOrgBgpStats`, `listOrgDevicesStats`, `listOrgMxEdgesStats`, `getOrgOtherDeviceStats`, `countOrgSwOrGwPorts`, `searchOrgSwOrGwPorts`, `listOrgSiteStats`, `countOrgTunnelsStats`, `searchOrgTunnelsStats`, `countOrgPeerPathStats`, `searchOrgPeerPathStats` |
| **orgs_wlans** | An Org Wlan is a wireless local area network that is configured at the Org level and applied to a WLAN template. | 8 | `listOrgPsks`, `listOrgRfTemplates`, `listOrgTemplates`, `listOrgWlans`, `listOrgWxRules`, `listOrgWxTags`, `getOrgApplicationList`, `getOrgCurrentMatchingClientsOfAWxTag` |
| **self_account** | tools related to the currently connected user account. | 4 | `getSelf`, `getSelfLoginFailures`, `listSelfAuditLogs`, `getSelfApiUsage` |
| **sites** | A site represents a project, a deployment. For MSP, it can be as small as a coffee shop or a five-star 600-room hotel. A site contains a set of Maps, Wlans, Policies, Zones. | 4 | `getSiteInfo`, `listSiteMaps`, `getSiteSetting`, `getSiteSettingDerived` |
| **sites_insights** | Insights is a feature that provides an overview of network experience across the entire site, access points, or clients. | 3 | `getSiteInsightMetricsForClient`, `getSiteInsightMetricsForDevice`, `getSiteInsightMetrics` |
| **sites_rfdiags** | Rf Diags is a feature in Juniper Mist location services that allows users to replay recorded sessions of the RF (radio frequency) environment. | 2 | `getSiteSiteRfdiagRecording`, `getSiteRfdiagRecording` |
| **sites_rogues** | Rogues are unauthorized wireless access points that are installed on a network without authorization. | 4 | `listSiteRogueAPs`, `listSiteRogueClients`, `countSiteRogueEvents`, `searchSiteRogueEvents` |
| **sites_rrm** | RRM, or Radio Resource Management, is a tool used by large multi-site organizations to efficiently manage their RF spectrum. | 4 | `getSiteCurrentChannelPlanning`, `getSiteCurrentRrmConsiderations`, `listSiteRrmEvents`, `listSiteCurrentRrmNeighbors` |
| **sites_sles** | Site SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network. | 15 | `getSiteSleClassifierDetails`, `listSiteSleMetricClassifiers`, `getSiteSleHistogram`, `getSiteSleImpactSummary`, `listSiteSleImpactedApplications`, `listSiteSleImpactedAps`, `listSiteSleImpactedChassis`, `listSiteSleImpactedWiredClients`, `listSiteSleImpactedGateways`, `listSiteSleImpactedInterfaces`, `listSiteSleImpactedSwitches`, `listSiteSleImpactedWirelessClients`, `getSiteSleSummary`, `getSiteSleThreshold`, `listSiteSlesMetrics` |
| **sites_stats** | Statistics for the sites. It provides access to various statistics related to the site, such as application statistics, call statistics, client statistics, and more. | 14 | `getSiteStats`, `countSiteApps`, `troubleshootSiteCall`, `countSiteCalls`, `searchSiteCalls`, `getSiteCallsSummary`, `listSiteTroubleshootCalls`, `listSiteWirelessClientsStats`, `searchSiteDiscoveredSwitchesMetrics`, `countSiteDiscoveredSwitches`, `listSiteDiscoveredSwitchesMetrics`, `searchSiteDiscoveredSwitches`, `listSiteMxEdgesStats`, `getSiteWxRulesUsage` |
| **sites_wan_usages** | tools to retrieve WAN Assurance statistics about the WAN Usage | 2 | `countSiteWanUsage`, `searchSiteWanUsage` |
| **sites_wlans** | A Site Wlan is a wireless local area network that is configured and applied to a specific site within an organization. | 8 | `listSitePsks`, `listSiteRfTemplateDerived`, `listSiteWlans`, `listSiteWlanDerived`, `listSiteWxRules`, `ListSiteWxRulesDerived`, `listSiteWxTags`, `getSiteApplicationList` |
| **templates_alarms** | Alarm templates at the sites and organizations level. It provides access to alarm templates, which can be used to configure alarms in a consistent manner. | 3 | `listOrgAlarmTemplates`, `listOrgSuppressedAlarms`, `getOrgAlarmTemplate` |
| **templates_devices** | Device profiles at the sites and organizations level. It provides access to device templates and profiles, which can be used to configure devices in a consistent manner. | 4 | `listOrgAptemplates`, `listOrgDeviceProfiles`, `listSiteApTemplateDerived`, `listSiteDeviceProfilesDerived` |
| **templates_switches** | Switches Configuration related objects for the sites and organizations. | 4 | `listOrgEvpnTopologies`, `listOrgNetworkTemplates`, `listSiteEvpnTopologies`, `listSiteNetworkTemplateDerived` |
| **templates_wan** | WAN Configuration related objects for the sites and organizations. | 18 | `listOrgAAMWProfiles`, `listOrgAntivirusProfiles`, `listOrgGatewayTemplates`, `listOrgIdpProfiles`, `listOrgNetworks`, `listOrgSecPolicies`, `listOrgServicePolicies`, `listOrgServices`, `listOrgVpns`, `listSiteApps`, `listSiteGatewayTemplateDerived`, `listSiteNetworksDerived`, `listSiteSecIntelProfilesDerived`, `listSiteServicePoliciesDerived`, `listSiteServicesDerived`, `countSiteServicePathEvents`, `searchSiteServicePathEvents`, `listSiteVpnsDerived` |
| **utilities_upgrade** | tools used to manage device upgrades for a single device, at the site level or at the organization level. | 8 | `listOrgDeviceUpgrades`, `listOrgAvailableDeviceVersions`, `listOrgMxEdgeUpgrades`, `listOrgSsrUpgrades`, `listOrgAvailableSsrVersions`, `listSiteDeviceUpgrades`, `listSiteAvailableDeviceVersions`, `getSiteSsrUpgrade` |
| **webhooks** | A Webhook is a configuration that allows real-time events and data from the Org to be pushed to a provided url. | 6 | `listOrgWebhooks`, `countOrgWebhooksDeliveries`, `searchOrgWebhooksDeliveries`, `listSiteWebhooks`, `countSiteWebhooksDeliveries`, `searchSiteWebhooksDeliveries` |

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
