# Mist MCP Server

A Model Context Protocol (MCP) server that provides AI-powered access to Juniper Mist networking APIs. This project enables Large Language Models (LLMs) like Claude to interact with Mist cloud-managed network infrastructure through a comprehensive set of **256 optimized tools** across **29 categories**.

Key innovation: **Intelligent tool consolidation** reduces what would be 300+ individual API tools to 256 optimized tools through advanced consolidation strategies, including two powerful **Configuration Object Consolidation** tools that replace 80+ individual configuration management tools.


## 📑 Table of Contents

- [🚀 Features](#-features)
- [🛠️ Installation & Setup](#️-installation--setup)
    - [Prerequisites](#prerequisites)
    - [1. Install Dependencies](#1-install-dependencies)
- [🚀 Usage](#-usage)
    - [Command Line Options](#command-line-options)
    - [HTTP Mode Query Parameters](#http-mode-query-parameters)
    - [Environment Variables](#environment-variables)
    - [Transport Modes](#transport-modes)
- [🔧 Configuration](#-configuration)
    - [STDIO Mode (Recommended)](#stdio-mode-recommended)
    - [HTTP Mode (Remote Access)](#http-mode-remote-access)
- [🔧 Tool Categories](#-tool-categories)
    - [Essential Tools](#essential-tools)
    - [Configuration Object Consolidation](#configuration-object-consolidation)
    - [Remaining Tool Categories](#remaining-tool-categories)
- [⚠️ Current Limitations](#️-current-limitations)
- [🤝 Contributing](#-contributing)
    - [Development Setup](#development-setup)
- [📄 License](#-license)
- [👤 Author](#-author)


## 🚀 Features

- **🤖 AI-Optimized Tool Design**: Advanced tool consolidation with 98% reduction in configuration management tools
- **🔧 256 Specialized Tools** across 29 categories covering all Mist APIs
- **⚡ Configuration Object Consolidation**: Two powerful tools replace 80+ individual configuration management tools
- **📡 Transport Flexibility**: Supports both STDIO and HTTP transport modes
- **🏗️ Intelligent Organization**: Tools grouped by functionality (orgs, sites, devices, clients, etc.)
- **🛡️ Type Safety**: Full type validation using Pydantic models
- **🌟 Derived Configuration Support**: Site-level templates with resolved Jinja2 variables


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
    --host HOST             HTTP server host (default: 127.0.0.1)
    -p, --port PORT         HTTP server port (default: 8000)
    -e, --env-file PATH     Path to .env file
    -d, --debug             Enable debug output
    -h, --help              Show help message

EXAMPLES:
    uv run mistmcp                                    # Default: stdio mode
    uv run mistmcp --debug                            # With debug output
    uv run mistmcp --transport http --host 0.0.0.0    # HTTP on all interfaces
```

### HTTP Mode Query Parameters

When using HTTP transport, configure the server via URL query parameters:

**Required:**
- `cloud` - Mist API host (e.g., `api.mist.com`)

**Optional:**
- `debug` - Enable debug output: `true` or `false`

**Example URLs:**
```bash
# Default
http://localhost:8000/mcp/?cloud=api.mist.com

# With debug enabled
http://localhost:8000/mcp/?cloud=api.mist.com&debug=true
```

### Environment Variables

Configure via environment variables or `.env` files:

| Parameter | STDIO Mode | HTTP Mode | Default Value | Description |
|-----------|------------|-----------|---------------|-------------|
| `MIST_APITOKEN` | **Required** | Not used | - | Your Mist API token for authentication |
| `MIST_HOST` | **Required** | Not used | - | Mist API host (e.g., `api.mist.com`, `api.eu.mist.com`) |
| `MIST_ENV_FILE` | Optional | Optional | - | Path to .env file containing Mist credentials |
| `MISTMCP_TRANSPORT_MODE` | Optional | **Required** | `stdio` | Transport mode: `stdio` or `http` |
| `MISTMCP_HOST` | Not used | Optional | `127.0.0.1` | HTTP server bind address |
| `MISTMCP_PORT` | Not used | Optional | `8000` | HTTP server port |
> **💡 Note:** `MIST_APITOKEN` and `MIST_HOST` can be provided either directly or via a `.env` file specified in `MIST_ENV_FILE`.

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
        "mist-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "/absolute/path/to/mistmcp",
                "run",
                "mistmcp"
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
            ...
            "env": {
                "NODE_EXTRA_CA_CERTS": "{your CA certificate file path}.pem"
            }
        }
    }
}
```


## 🔧 Tool Categories

The server provides **256 specialized tools** organized across **29 categories**. A key innovation is **Configuration Object Consolidation** - two powerful tools replace what would otherwise be 80+ individual configuration management tools.

### Essential Tools
- **`getSelf`** - User and organization information

### Configuration Object Consolidation ⭐

**Revolutionary optimization**: Instead of 80+ individual configuration tools, we provide 2 powerful consolidated tools:

| Tool | Scope | Object Types | Description |
|------|-------|--------------|-------------|
| **`getOrgConfigurationObjects`** | Organization | 26 types | Access all org-level configuration objects (templates, policies, devices, networks, etc.) |
| **`getSiteConfigurationObjects`** | Site | 19 types | Access all site-level configuration objects + derived configurations with Jinja2 resolution |

**Usage Examples:**
```python
# Organization WLAN management - replaces listOrgWlans + getOrgWlan
getOrgConfigurationObjects(org_id="...", object_type="wlans")  # List all
getOrgConfigurationObjects(org_id="...", object_type="wlans", object_id="...")  # Get specific

# Site device management with derived configs
getSiteConfigurationObjects(site_id="...", object_type="devices")  # Site devices
getSiteConfigurationObjects(site_id="...", object_type="aptemplates_derived")  # Org templates + site variables
```

**Supported Object Types:**
- **Organization (26 types)**: `alarmtemplates`, `wlans`, `sitegroups`, `aptemplates`, `avprofiles`, `devices`, `deviceprofiles`, `evpn_topologies`, `gatewaytemplates`, `idpprofiles`, `aamwprofiles`, `mxclusters`, `mxedges`, `mxtunnels`, `nactags`, `nacrules`, `networktemplates`, `networks`, `psks`, `rftemplates`, `secpolicies`, `services`, `servicepolicies`, `sites`, `sitetemplates`, `templates`, `vpns`, `webhooks`, `wxrules`, `wxtags`
- **Site (19 types)**: `devices`, `evpn_topologies`, `maps`, `mxedges`, `psks`, `webhooks`, `wlans`, `wxrules`, `wxtags` + **10 derived types**: `rftemplates_derived`, `wlans_derived`, `wxrules_derived`, `aptemplates_derived`, `networktemplates_derived`, `gatewaytemplates_derived`, `deviceprofiles_derived`, `networks_derived`, `services_derived`, `servicepolicies_derived`, `vpns_derived`

**Consolidation Benefits:**
- **98% Tool Reduction**: 80+ configuration tools → 2 consolidated tools
- **Consistent Interface**: Same parameter pattern (`object_type`, optional `object_id`) across all configuration types
- **Enhanced Functionality**: Single tool handles both list and get operations
- **Derived Configuration Support**: Site-level access to org templates with resolved Jinja2 variables
- **Future-Proof**: Easily extensible to new configuration object types

### Remaining Tool Categories

The following categories contain specialized tools that complement the configuration object consolidation:

| Category | Description | Tools | Tool List |
|----------|-------------|-------|-----------|
| **clients** | Clients related objects for the sites and organizations. | 12 | `searchOrgWirelessClientEvents`, `searchOrgWirelessClients`, `searchOrgWirelessClientSessions`, `searchOrgGuestAuthorization`, `getOrgGuestAuthorization`, `searchOrgNacClientEvents`, `searchOrgNacClients`, `searchOrgWanClientEvents`, `searchOrgWanClients`, `searchOrgWiredClients`, `searchSiteGuestAuthorization`, `getSiteGuestAuthorization` |
| **configuration** | Configuration related objects for the sites and organizations. | 2 | `getOrgConfigurationObjects`, `getSiteConfigurationObjects` |
| **constants_definitions** | tools to retrieve constant values that can be used in different parts of the configuration | 4 | `listFingerprintTypes`, `listInsightMetrics`, `listLicenseTypes`, `listWebhookTopics` |
| **devices** | Devices are any Network device managed or monitored by Juniper Mist. | 11 | `searchOrgDeviceEvents`, `listOrgApsMacs`, `searchOrgDevices`, `listOrgDevicesSummary`, `getOrgInventory`, `searchOrgInventory`, `getOrgJuniperDevicesCommand`, `searchSiteDeviceConfigHistory`, `searchSiteDeviceEvents`, `searchSiteDeviceLastConfigs`, `searchSiteDevices` |
| **marvis** | Marvis is a virtual network assistant that provides insights and analytics for the Mist network. | 3 | `troubleshootOrg`, `getSiteDeviceSyntheticTest`, `searchSiteSyntheticTest` |
| **mxedges** | MX Edge related objects for the organizations. It provides access to Mist Edges, Mist Clusters, and Mist Tunnels. | 4 | `searchOrgMistEdgeEvents`, `searchOrgMxEdges`, `getOrgMxEdgeUpgradeInfo`, `searchSiteMistEdgeEvents` |
| **orgs** | An organization usually represents a customer - which has inventories, licenses. | 5 | `getOrg`, `searchOrgAlarms`, `searchOrgEvents`, `listOrgAuditLogs`, `getOrgSettings` |
| **orgs_alarm_templates** | An Alarm Template is a set of Alarm Rules that could be applied to one or more sites (while each site can only pick one Alarm Template), or to the... | 1 | `listOrgSuppressedAlarms` |
| **orgs_licenses** | Licenses are a type of service or access that customers can purchase for various features or services offered by a company. | 3 | `GetOrgLicenseAsyncClaimStatus`, `getOrgLicensesSummary`, `getOrgLicensesBySite` |
| **orgs_nac** | NAC related objects for the organizations. It provides access to NAC Endpoints, NAC fingerprints, tags, and rules. | 3 | `searchOrgUserMacs`, `getOrgUserMac`, `searchOrgClientFingerprints` |
| **orgs_sites** | tools to Create or Get the Organization Sites. | 1 | `searchOrgSites` |
| **orgs_sles** | Org SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network. | 2 | `getOrgSitesSle`, `getOrgSle` |
| **orgs_stats** | Statistics for the organizations. It provides access to various statistics related to the organization, such as BGP peers, devices, MX edges, other devices, ports, sites, tunnels, and VPN peers. | 10 | `getOrgStats`, `searchOrgBgpStats`, `listOrgDevicesStats`, `listOrgMxEdgesStats`, `getOrgMxEdgeStats`, `getOrgOtherDeviceStats`, `searchOrgSwOrGwPorts`, `listOrgSiteStats`, `searchOrgTunnelsStats`, `searchOrgPeerPathStats` |
| **orgs_wxtags** | Wxtags are tags or groups that can be created and used within the Org. | 2 | `getOrgApplicationList`, `getOrgCurrentMatchingClientsOfAWxTag` |
| **self_account** | tools related to the currently connected user account. | 4 | `getSelf`, `getSelfLoginFailures`, `listSelfAuditLogs`, `getSelfApiUsage` |
| **sites** | A site represents a project, a deployment. For MSP, it can be as small as a coffee shop or a five-star 600-room hotel. A site contains a set of Maps, Wlans, Policies, Zones. | 3 | `getSiteInfo`, `getSiteSetting`, `getSiteSettingDerived` |
| **sites_applications** | Applications contains a list of applications users are interested in monitoring / routing / policing | 1 | `listSiteApps` |
| **sites_events** | Site events are issues or incidents that affect site-assigned access points (aps) and radius, dhcp, and dns servers. | 1 | `listSiteRoamingEvents` |
| **sites_insights** | Insights is a feature that provides an overview of network experience across the entire site, access points, or clients. | 3 | `getSiteInsightMetricsForClient`, `getSiteInsightMetricsForDevice`, `getSiteInsightMetrics` |
| **sites_rfdiags** | Rf Diags is a feature in Juniper Mist location services that allows users to replay recorded sessions of the RF (radio frequency) environment. | 2 | `getSiteSiteRfdiagRecording`, `getSiteRfdiagRecording` |
| **sites_rogues** | Rogues are unauthorized wireless access points that are installed on a network without authorization. | 4 | `listSiteRogueAPs`, `listSiteRogueClients`, `searchSiteRogueEvents`, `getSiteRogueAP` |
| **sites_rrm** | RRM, or Radio Resource Management, is a tool used by large multi-site organizations to efficiently manage their RF spectrum. | 4 | `getSiteCurrentChannelPlanning`, `getSiteCurrentRrmConsiderations`, `listSiteRrmEvents`, `listSiteCurrentRrmNeighbors` |
| **sites_services** | A Service represents an a traffic destination or an application that network users connect to. | 1 | `searchSiteServicePathEvents` |
| **sites_sles** | Site SLEs, or Service-Level Expectations, are metrics used to monitor and report on the user experience of a Wireless, Wired or Wan network. | 15 | `getSiteSleClassifierDetails`, `listSiteSleMetricClassifiers`, `getSiteSleHistogram`, `getSiteSleImpactSummary`, `listSiteSleImpactedApplications`, `listSiteSleImpactedAps`, `listSiteSleImpactedChassis`, `listSiteSleImpactedWiredClients`, `listSiteSleImpactedGateways`, `listSiteSleImpactedInterfaces`, `listSiteSleImpactedSwitches`, `listSiteSleImpactedWirelessClients`, `getSiteSleSummary`, `getSiteSleThreshold`, `listSiteSlesMetrics` |
| **sites_stats** | Statistics for the sites. It provides access to various statistics related to the site, such as application statistics, call statistics, client statistics, and more. | 13 | `getSiteStats`, `troubleshootSiteCall`, `searchSiteCalls`, `getSiteCallsSummary`, `listSiteTroubleshootCalls`, `listSiteWirelessClientsStats`, `getSiteWirelessClientStats`, `searchSiteDiscoveredSwitchesMetrics`, `listSiteDiscoveredSwitchesMetrics`, `searchSiteDiscoveredSwitches`, `listSiteMxEdgesStats`, `getSiteMxEdgeStats`, `getSiteWxRulesUsage` |
| **sites_wan_usages** | tools to retrieve WAN Assurance statistics about the WAN Usage | 1 | `searchSiteWanUsage` |
| **sites_wxtags** | Wxtags are tags or groups that can be created and used within a specific site. | 1 | `getSiteApplicationList` |
| **utilities_upgrade** | tools used to manage device upgrades for a single device, at the site level or at the organization level. | 10 | `listOrgDeviceUpgrades`, `getOrgDeviceUpgrade`, `listOrgAvailableDeviceVersions`, `listOrgMxEdgeUpgrades`, `getOrgMxEdgeUpgrade`, `listOrgSsrUpgrades`, `listOrgAvailableSsrVersions`, `listSiteDeviceUpgrades`, `getSiteDeviceUpgrade`, `getSiteSsrUpgrade` |
| **webhooks** | A Webhook is a configuration that allows real-time events and data from the Org to be pushed to a provided url. | 2 | `searchOrgWebhooksDeliveries`, `searchSiteWebhooksDeliveries` |

Each client session maintains independent tool configurations for complete isolation.

## ⚠️ Current Limitations

- **API Authentication**: Requires manual Mist API token configuration
- **Rate Limiting**: No built-in rate limiting for API calls
- **Error Handling**: Limited retry logic for transient API failures

## 🤝 Contributing

Contributions welcome! Priority areas:
- **Performance optimization** and caching
- **API rate limiting and retry logic** implementation
- **Test coverage** expansion
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

*AI-powered bridge between LLMs and Juniper Mist networking infrastructure.*
