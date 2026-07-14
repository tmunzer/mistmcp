"""Tests for workflow-oriented facade tools."""

from types import ModuleType, SimpleNamespace
from typing import Callable
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastmcp.exceptions import ToolError
from fastmcp.tools import FunctionTool, ToolResult

from mistmcp.tools import describe as describe_tool
from mistmcp.tools import get_account as account_tool
from mistmcp.tools import get_configuration as configuration_tool
from mistmcp.tools import get_site_insights as insights_tool
from mistmcp.tools import search_activity as activity_tool
from mistmcp.tools import search_assets as assets_tool
from mistmcp.tools import search_security as security_tool


ORG_ID = UUID("11111111-1111-1111-1111-111111111111")
SITE_ID = UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def runner(monkeypatch) -> Callable[[ModuleType], AsyncMock]:
    def patch(module: ModuleType) -> AsyncMock:
        mock = AsyncMock(return_value=ToolResult(content=[]))
        monkeypatch.setattr(module, "run_internal_tool", mock)
        return mock

    return patch


async def test_get_account_dispatches_account_info(runner) -> None:
    run = runner(account_tool)
    await account_tool.get_account(account_tool.AccountInformation.ACCOUNT_INFO)
    run.assert_awaited_once_with(
        account_tool._GET_SELF, {"action_type": "account_info"}
    )


async def test_get_account_dispatches_license_summary(runner) -> None:
    run = runner(account_tool)
    await account_tool.get_account(
        account_tool.AccountInformation.LICENSE_SUMMARY, ORG_ID
    )
    run.assert_awaited_once_with(
        account_tool._GET_ORG_LICENSES,
        {"org_id": ORG_ID, "response_type": "summary"},
    )


async def test_get_account_requires_org_for_licenses() -> None:
    with pytest.raises(ToolError, match="org_id is required"):
        await account_tool.get_account(account_tool.AccountInformation.LICENSES_BY_SITE)


async def test_describe_dispatches_both_subjects(runner) -> None:
    run = runner(describe_tool)
    await describe_tool.describe(
        describe_tool.DescriptionSubject.CONSTANT, "device_models"
    )
    run.assert_awaited_once_with(
        describe_tool._GET_CONSTANTS, {"object_type": "device_models"}
    )

    run.reset_mock()
    await describe_tool.describe(
        describe_tool.DescriptionSubject.CONFIGURATION_SCHEMA,
        "OrgWlan",
        verbose=True,
    )
    run.assert_awaited_once_with(
        describe_tool._GET_CONFIGURATION_SCHEMA,
        {"schema_name": "OrgWlan", "verbose": True},
    )


async def test_describe_lists_valid_names_without_dispatch(runner) -> None:
    run = runner(describe_tool)
    result = await describe_tool.describe(describe_tool.DescriptionSubject.CONSTANT)

    assert "device_models" in result["names"]
    run.assert_not_awaited()


async def test_search_assets_dispatches_device_and_client(runner) -> None:
    run = runner(assets_tool)
    await assets_tool.search_assets(
        assets_tool.AssetType.DEVICE,
        ORG_ID,
        text="edge*",
        device_type=assets_tool.DeviceType.GATEWAY,
    )
    run.assert_awaited_once_with(
        assets_tool._SEARCH_DEVICE,
        {
            "org_id": ORG_ID,
            "text": "edge*",
            "limit": 20,
            "device_type": "gateway",
        },
    )

    run.reset_mock()
    await assets_tool.search_assets(
        assets_tool.AssetType.WIRELESS_CLIENT,
        ORG_ID,
        site_id=SITE_ID,
        mac="aabbcc*",
        ssid="corp",
    )
    run.assert_awaited_once_with(
        assets_tool._SEARCH_CLIENT,
        {
            "org_id": ORG_ID,
            "site_id": SITE_ID,
            "mac": "aabbcc*",
            "limit": 20,
            "client_type": "wireless",
            "ssid": "corp",
        },
    )


async def test_get_configuration_dispatches_both_operations(runner) -> None:
    run = runner(configuration_tool)
    await configuration_tool.get_configuration(
        configuration_tool.ConfigurationOperation.OBJECTS,
        org_id=ORG_ID,
        object_type=configuration_tool.ConfigurationObjectType.ORG_SITES,
        name="Paris*",
    )
    run.assert_awaited_once_with(
        configuration_tool._GET_CONFIGURATION_OBJECTS,
        {
            "org_id": ORG_ID,
            "object_type": "org_sites",
            "name": "Paris*",
            "limit": 20,
        },
    )

    run.reset_mock()
    await configuration_tool.get_configuration(
        configuration_tool.ConfigurationOperation.DEVICE_HISTORY,
        site_id=SITE_ID,
        query_type=configuration_tool.HistoryQueryType.HISTORY,
        device_type=configuration_tool.HistoryDeviceType.AP,
    )
    run.assert_awaited_once_with(
        configuration_tool._SEARCH_DEVICE_CONFIG_HISTORY,
        {
            "site_id": SITE_ID,
            "query_type": "history",
            "device_type": "ap",
            "limit": 20,
        },
    )


async def test_search_activity_dispatches_event_and_audit(runner) -> None:
    run = runner(activity_tool)
    await activity_tool.search_activity(
        activity_tool.ActivityType.EVENT,
        org_id=ORG_ID,
        source=activity_tool.EventSource.DEVICE,
        query="reboot",
        event_type="AP_RESTARTED",
    )
    run.assert_awaited_once_with(
        activity_tool._SEARCH_EVENTS,
        {
            "search_type": "event",
            "org_id": ORG_ID,
            "event_source": "device",
            "text": "reboot",
            "limit": 20,
            "event_type": "AP_RESTARTED",
        },
    )

    run.reset_mock()
    await activity_tool.search_activity(
        activity_tool.ActivityType.AUDIT,
        org_id=ORG_ID,
        query="wlan",
    )
    run.assert_awaited_once_with(
        activity_tool._SEARCH_AUDIT_LOGS,
        {
            "scope": "org",
            "org_id": ORG_ID,
            "message": "wlan",
            "limit": 20,
        },
    )


async def test_search_security_dispatches_both_subjects(runner) -> None:
    run = runner(security_tool)
    await security_tool.search_security(
        security_tool.SecuritySubject.NAC_USER_MAC,
        org_id=ORG_ID,
        mac="aabb*",
    )
    run.assert_awaited_once_with(
        security_tool._SEARCH_NAC_USER_MACS,
        {"org_id": ORG_ID, "mac": "aabb*", "limit": 20},
    )

    run.reset_mock()
    await security_tool.search_security(
        security_tool.SecuritySubject.ROGUE_DEVICE,
        site_id=SITE_ID,
        rogue_type=security_tool.RogueType.AP,
    )
    run.assert_awaited_once_with(
        security_tool._LIST_ROGUE_DEVICES,
        {"site_id": SITE_ID, "limit": 20, "rogue_type": "ap"},
    )


async def test_get_site_insights_dispatches_both_types(runner) -> None:
    run = runner(insights_tool)
    await insights_tool.get_site_insights(
        insights_tool.SiteInsightType.METRIC,
        SITE_ID,
        object_type=insights_tool.InsightObjectType.SITE,
        metric="num_clients",
    )
    run.assert_awaited_once_with(
        insights_tool._GET_INSIGHT_METRICS,
        {
            "site_id": SITE_ID,
            "object_type": "site",
            "metric": "num_clients",
        },
    )

    run.reset_mock()
    await insights_tool.get_site_insights(
        insights_tool.SiteInsightType.RRM,
        SITE_ID,
        rrm_info_type=insights_tool.RrmInfoType.CURRENT_CHANNEL_PLANNING,
    )
    run.assert_awaited_once_with(
        insights_tool._GET_SITE_RRM_INFO,
        {
            "site_id": SITE_ID,
            "rrm_info_type": "current_channel_planning",
            "limit": 0,
            "page": 0,
        },
    )


async def test_configuration_requires_operation_specific_parameters() -> None:
    with pytest.raises(ToolError, match="org_id and object_type"):
        await configuration_tool.get_configuration(
            configuration_tool.ConfigurationOperation.OBJECTS
        )


async def test_insights_requires_operation_specific_parameters() -> None:
    with pytest.raises(ToolError, match="object_type and metric"):
        await insights_tool.get_site_insights(
            insights_tool.SiteInsightType.METRIC,
            SITE_ID,
        )

    with pytest.raises(ToolError, match="only be used with rrm_info_type='events'"):
        await insights_tool.get_site_insights(
            insights_tool.SiteInsightType.RRM,
            SITE_ID,
            rrm_info_type=insights_tool.RrmInfoType.CURRENT_CHANNEL_PLANNING,
            limit=20,
        )


def test_configuration_schema_advertises_supported_object_types() -> None:
    tool = FunctionTool.from_function(configuration_tool.get_configuration)
    schema = tool.parameters

    object_types = schema["$defs"]["Object_type"]["enum"]
    assert "org_wlans" in object_types
    assert "org_networktemplates" in object_types
    assert "site_devices" in object_types
    assert "site_guest_authorizations" in object_types
    assert "guest_mac" in schema["properties"]
    assert "complete\nlists of supported values" in tool.description


def test_configuration_description_covers_every_supported_object_type() -> None:
    assert set(configuration_tool._CONFIGURATION_OBJECT_DESCRIPTIONS) == {
        item.value for item in configuration_tool.ConfigurationObjectType
    }
    description = FunctionTool.from_function(
        configuration_tool.get_configuration
    ).description
    for object_type, meaning in configuration_tool._CONFIGURATION_OBJECT_DESCRIPTIONS.items():
        assert f"`{object_type}`" in description
        assert meaning in description


def test_describe_only_claims_constants_it_supports() -> None:
    description = FunctionTool.from_function(describe_tool.describe).description
    assert "fingerprint types" in description
    assert "webhook topics" in description
    assert "countries" not in description
    assert "applications" not in description


def test_optional_facade_parameters_do_not_use_anyof_schemas() -> None:
    facade_functions = [
        account_tool.get_account,
        describe_tool.describe,
        assets_tool.search_assets,
        configuration_tool.get_configuration,
        activity_tool.search_activity,
        security_tool.search_security,
        insights_tool.get_site_insights,
    ]
    for function in facade_functions:
        schema = FunctionTool.from_function(function).parameters
        anyof_parameters = [
            name
            for name, parameter_schema in schema["properties"].items()
            if "anyOf" in parameter_schema
        ]
        assert anyof_parameters == [], f"{function.__name__}: {anyof_parameters}"


async def test_wireless_client_band_uses_api_value(monkeypatch) -> None:
    calls = []
    response = SimpleNamespace(data={})

    def search_wireless_clients(*args, **kwargs):
        calls.append(kwargs)
        return response

    monkeypatch.setattr(
        assets_tool.mistapi.api.v1.orgs.clients,
        "searchOrgWirelessClients",
        search_wireless_clients,
    )
    monkeypatch.setattr(
        assets_tool, "get_apisession", AsyncMock(return_value=(object(), "json"))
    )
    monkeypatch.setattr(assets_tool, "process_response", AsyncMock())
    monkeypatch.setattr(assets_tool, "format_response", lambda value, _format: value)

    await assets_tool.search_client(
        assets_tool.Client_type.WIRELESS,
        ORG_ID,
        site_id=None,
        device_mac=None,
        band=assets_tool.Band.B5,
        mac=None,
        hostname=None,
        ip=None,
        ssid=None,
        text=None,
        start=None,
        end=None,
        limit=20,
    )

    assert calls[0]["band"] == "5"


@pytest.mark.parametrize(
    ("object_type", "helper_name"),
    [("site_devices", "_get_site_devices"), ("site_wlans", "_get_site_wlans")],
)
async def test_site_configuration_list_paths_do_not_require_id_or_name(
    monkeypatch, object_type: str, helper_name: str
) -> None:
    expected = object()
    helper = AsyncMock(return_value=expected)
    monkeypatch.setattr(configuration_tool, helper_name, helper)

    result = await configuration_tool._site_configuration_objects_getter(
        object(), object_type, str(ORG_ID), str(SITE_ID), None, None, None, False, 20
    )

    assert result is expected
    helper.assert_awaited_once()


async def test_site_wlan_name_filter_searches_ssids(monkeypatch) -> None:
    listed = SimpleNamespace(
        data=[
            {"id": "1", "ssid": "Corporate"},
            {"id": "2", "ssid": "Guest"},
        ]
    )
    monkeypatch.setattr(
        configuration_tool.mistapi.api.v1.sites.wlans,
        "listSiteWlans",
        lambda *args, **kwargs: listed,
    )
    monkeypatch.setattr(
        configuration_tool.mistapi, "get_all", lambda _session, response: response.data
    )
    monkeypatch.setattr(configuration_tool, "process_response", AsyncMock())

    response = await configuration_tool._get_site_wlans(
        object(), str(ORG_ID), str(SITE_ID), None, "Corp*", False, 20
    )

    assert response.data == [{"id": "1", "ssid": "Corporate"}]


def test_facade_schemas_expose_operation_specific_parameters() -> None:
    facade_functions = [
        assets_tool.search_assets,
        configuration_tool.get_configuration,
        activity_tool.search_activity,
        security_tool.search_security,
        insights_tool.get_site_insights,
    ]
    schemas = [
        FunctionTool.from_function(function).parameters for function in facade_functions
    ]

    for schema in schemas:
        assert "filters" not in schema["properties"]
        assert "parameters" not in schema["properties"]

    assert {"serial", "device_type", "hostname", "ssid"} <= schemas[0][
        "properties"
    ].keys()
    assert {"event_type", "severity", "alarm_type", "acked"} <= schemas[2][
        "properties"
    ].keys()
    assert {"usermac_id", "labels", "rogue_type", "rogue_ap_type"} <= schemas[3][
        "properties"
    ].keys()
    assert {"object_type", "metric", "rrm_info_type", "band"} <= schemas[4][
        "properties"
    ].keys()


def test_every_facade_description_covers_every_input() -> None:
    facade_functions = [
        account_tool.get_account,
        describe_tool.describe,
        assets_tool.search_assets,
        configuration_tool.get_configuration,
        activity_tool.search_activity,
        security_tool.search_security,
        insights_tool.get_site_insights,
    ]

    for function in facade_functions:
        tool = FunctionTool.from_function(function)
        missing = [
            parameter
            for parameter in tool.parameters["properties"]
            if parameter not in tool.description
        ]
        assert missing == [], (
            f"{tool.name} description does not explain parameters: {missing}"
        )


def test_facade_descriptions_include_critical_workflow_constraints() -> None:
    descriptions = {
        tool.name: tool.description
        for tool in [
            FunctionTool.from_function(account_tool.get_account),
            FunctionTool.from_function(describe_tool.describe),
            FunctionTool.from_function(assets_tool.search_assets),
            FunctionTool.from_function(configuration_tool.get_configuration),
            FunctionTool.from_function(activity_tool.search_activity),
            FunctionTool.from_function(security_tool.search_security),
            FunctionTool.from_function(insights_tool.get_site_insights),
        ]
    }

    assert "License operations require `org_id`" in descriptions["mist_get_account"]
    assert "Omit `name` to list every valid name" in descriptions["mist_describe"]
    assert "`site_guest` requires `site_id`" in descriptions["mist_search_assets"]
    assert "maximum of 1000" in descriptions["mist_get_configuration"]
    assert "roaming and rogue require" in descriptions["mist_search_activity"]
    assert "other filters are then ignored" in descriptions["mist_search_security"]
    assert "event-only for RRM" in descriptions["mist_get_site_insights"]


def test_absorbed_endpoint_implementations_live_in_workflow_modules() -> None:
    absorbed = {
        account_tool: {"get_self", "get_org_licenses"},
        describe_tool: {"get_constants", "get_configuration_object_schema"},
        assets_tool: {"search_device", "search_client"},
        configuration_tool: {
            "get_configuration_objects",
            "search_device_config_history",
        },
        activity_tool: {"search_events", "search_audit_logs"},
        security_tool: {"search_nac_user_macs", "list_rogue_devices"},
        insights_tool: {"get_insight_metrics", "get_site_rrm_info"},
    }

    for module, function_names in absorbed.items():
        assert all(callable(getattr(module, name, None)) for name in function_names)
