from mistmcp.__ctools import McpToolsCategory, manageMcpTools
from mistmcp.tools.sites_sles import listsiteslesmetrics
from uuid import UUID

async def main():
    # Enable the orgs_sites category using the proper enum
    await manageMcpTools(
        enable_mcp_tools_categories=[McpToolsCategory.ORGS_SITES],  # Use the enum value, not a string
        disable_mcp_tools_categories=[],  # Use the enum value, not a string
        configuration_required=False
    )
    print("Tools enabled successfully!")
    
    # Example: Search for sites in an organization
    # Note: Replace this with your actual org_id
    org_id = UUID("9777c1a0-6ef6-11e6-8bbf-02e208b2d34f")
    site_id = UUID("8c22581b-a855-407f-b695-d6bb245899b6")
    # Search for sites. All parameters except org_id are optional
    result = await listsiteslesmetrics.listSiteSlesMetrics(
        site_id=site_id,
        scope=listsiteslesmetrics.Scope.SITE,
        scope_id=str(site_id)
        # Optional parameters:
        # analytic_enabled=True,  # If Advanced Analytic feature is enabled
        # app_waking=True,       # If App Waking feature is enabled
        # asset_enabled=True,    # If Asset Tracking is enabled
        # etc...
    )
    print(f"Search results: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())