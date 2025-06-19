"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from .constants_events import listalarmdefinitions as listalarmdefinitions
from .constants_events import listclienteventsdefinitions as listclienteventsdefinitions
from .constants_events import listdeviceeventsdefinitions as listdeviceeventsdefinitions
from .constants_events import listmxedgeeventsdefinitions as listmxedgeeventsdefinitions
from .constants_events import listnaceventsdefinitions as listnaceventsdefinitions
from .constants_events import (
    listotherdeviceeventsdefinitions as listotherdeviceeventsdefinitions,
)
from .constants_events import listsystemeventsdefinitions as listsystemeventsdefinitions
from .constants_definitions import listapchannels as listapchannels
from .constants_definitions import listapleddefinition as listapleddefinition
from .constants_definitions import listfingerprinttypes as listfingerprinttypes
from .constants_definitions import listinsightmetrics as listinsightmetrics
from .constants_definitions import listlicensetypes as listlicensetypes
from .constants_definitions import listwebhooktopics as listwebhooktopics
from .constants_models import listdevicemodels as listdevicemodels
from .constants_models import listmxedgemodels as listmxedgemodels
from .constants_models import (
    listsupportedotherdevicemodels as listsupportedotherdevicemodels,
)
from .orgs import getorg as getorg
from .orgs import searchorgevents as searchorgevents
from .orgs import getorgsettings as getorgsettings
from .orgs_wan import listorgaamwprofiles as listorgaamwprofiles
from .orgs_wan import listorgantivirusprofiles as listorgantivirusprofiles
from .orgs_wan import listorggatewaytemplates as listorggatewaytemplates
from .orgs_wan import listorgidpprofiles as listorgidpprofiles
from .orgs_wan import listorgnetworks as listorgnetworks
from .orgs_wan import listorgsecpolicies as listorgsecpolicies
from .orgs_wan import listorgservicepolicies as listorgservicepolicies
from .orgs_wan import listorgservices as listorgservices
from .orgs_wan import listorgvpns as listorgvpns
from .orgs_alarms import countorgalarms as countorgalarms
from .orgs_alarms import searchorgalarms as searchorgalarms
from .orgs_alarm_templates import listorgalarmtemplates as listorgalarmtemplates
from .orgs_alarm_templates import listorgsuppressedalarms as listorgsuppressedalarms
from .orgs_alarm_templates import getorgalarmtemplate as getorgalarmtemplate
from .devices_config import listorgaptemplates as listorgaptemplates
from .devices_config import listorgdeviceprofiles as listorgdeviceprofiles
from .devices_config import listsiteaptemplatederived as listsiteaptemplatederived
from .devices_config import (
    listsitedeviceprofilesderived as listsitedeviceprofilesderived,
)
from .orgs_licenses import (
    getorglicenseasyncclaimstatus as getorglicenseasyncclaimstatus,
)
from .orgs_licenses import getorglicensessummary as getorglicensessummary
from .orgs_licenses import getorglicensesbysite as getorglicensesbysite
from .orgs_clients import countorgwirelessclients as countorgwirelessclients
from .orgs_clients import searchorgwirelessclientevents as searchorgwirelessclientevents
from .orgs_clients import searchorgwirelessclients as searchorgwirelessclients
from .orgs_clients import (
    countorgwirelessclientssessions as countorgwirelessclientssessions,
)
from .orgs_clients import (
    searchorgwirelessclientsessions as searchorgwirelessclientsessions,
)
from .orgs_clients import listorgguestauthorizations as listorgguestauthorizations
from .orgs_clients import countorgguestauthorizations as countorgguestauthorizations
from .orgs_clients import searchorgguestauthorization as searchorgguestauthorization
from .orgs_clients import getorgguestauthorization as getorgguestauthorization
from .orgs_clients import countorgnacclients as countorgnacclients
from .orgs_clients import countorgnacclientevents as countorgnacclientevents
from .orgs_clients import searchorgnacclientevents as searchorgnacclientevents
from .orgs_clients import searchorgnacclients as searchorgnacclients
from .orgs_clients import countorgwanclientevents as countorgwanclientevents
from .orgs_clients import countorgwanclients as countorgwanclients
from .orgs_clients import searchorgwanclientevents as searchorgwanclientevents
from .orgs_clients import searchorgwanclients as searchorgwanclients
from .orgs_clients import countorgwiredclients as countorgwiredclients
from .orgs_clients import searchorgwiredclients as searchorgwiredclients
from .orgs_devices import listorgdevices as listorgdevices
from .orgs_devices import countorgdevices as countorgdevices
from .orgs_devices import countorgdeviceevents as countorgdeviceevents
from .orgs_devices import searchorgdeviceevents as searchorgdeviceevents
from .orgs_devices import countorgdevicelastconfigs as countorgdevicelastconfigs
from .orgs_devices import searchorgdevicelastconfigs as searchorgdevicelastconfigs
from .orgs_devices import listorgapsmacs as listorgapsmacs
from .orgs_devices import searchorgdevices as searchorgdevices
from .orgs_devices import listorgdevicessummary as listorgdevicessummary
from .orgs_devices import getorgjuniperdevicescommand as getorgjuniperdevicescommand
from .utilities_upgrade import listorgdeviceupgrades as listorgdeviceupgrades
from .utilities_upgrade import (
    listorgavailabledeviceversions as listorgavailabledeviceversions,
)
from .utilities_upgrade import listorgmxedgeupgrades as listorgmxedgeupgrades
from .utilities_upgrade import listorgssrupgrades as listorgssrupgrades
from .utilities_upgrade import (
    listorgavailablessrversions as listorgavailablessrversions,
)
from .utilities_upgrade import listsitedeviceupgrades as listsitedeviceupgrades
from .utilities_upgrade import (
    listsiteavailabledeviceversions as listsiteavailabledeviceversions,
)
from .utilities_upgrade import getsitessrupgrade as getsitessrupgrade
from .orgs_events import countorgsystemevents as countorgsystemevents
from .orgs_events import searchorgsystemevents as searchorgsystemevents
from .orgs_lan import listorgevpntopologies as listorgevpntopologies
from .orgs_lan import listorgnetworktemplates as listorgnetworktemplates
from .orgs_sles import getorgsitessle as getorgsitessle
from .orgs_sles import getorgsle as getorgsle
from .orgs_inventory import getorginventory as getorginventory
from .orgs_inventory import countorginventory as countorginventory
from .orgs_inventory import searchorginventory as searchorginventory
from .orgs_logs import listorgauditlogs as listorgauditlogs
from .orgs_logs import countorgauditlogs as countorgauditlogs
from .orgs_mxedges import listorgmxedgeclusters as listorgmxedgeclusters
from .orgs_mxedges import listorgmxedges as listorgmxedges
from .orgs_mxedges import countorgmxedges as countorgmxedges
from .orgs_mxedges import countorgsitemxedgeevents as countorgsitemxedgeevents
from .orgs_mxedges import searchorgmistedgeevents as searchorgmistedgeevents
from .orgs_mxedges import searchorgmxedges as searchorgmxedges
from .orgs_mxedges import getorgmxedgeupgradeinfo as getorgmxedgeupgradeinfo
from .orgs_mxedges import listorgmxtunnels as listorgmxtunnels
from .orgs_nac import listorgnacrules as listorgnacrules
from .orgs_nac import listorgnactags as listorgnactags
from .orgs_nac import searchorgusermacs as searchorgusermacs
from .orgs_nac import getorgusermac as getorgusermac
from .orgs_nac import countorgclientfingerprints as countorgclientfingerprints
from .orgs_nac import searchorgclientfingerprints as searchorgclientfingerprints
from .orgs_devices___others import listorgotherdevices as listorgotherdevices
from .orgs_devices___others import (
    countorgotherdeviceevents as countorgotherdeviceevents,
)
from .orgs_devices___others import (
    searchorgotherdeviceevents as searchorgotherdeviceevents,
)
from .orgs_devices___others import getorgotherdevice as getorgotherdevice
from .orgs_wlans import listorgpsks as listorgpsks
from .orgs_wlans import listorgrftemplates as listorgrftemplates
from .orgs_wlans import listorgtemplates as listorgtemplates
from .orgs_wlans import listorgwlans as listorgwlans
from .orgs_wlans import getorgwlan as getorgwlan
from .orgs_wlans import listorgwxrules as listorgwxrules
from .orgs_wlans import listorgwxtags as listorgwxtags
from .orgs_wlans import getorgapplicationlist as getorgapplicationlist
from .orgs_wlans import (
    getorgcurrentmatchingclientsofawxtag as getorgcurrentmatchingclientsofawxtag,
)
from .orgs_sitegroups import listorgsitegroups as listorgsitegroups
from .orgs_sitegroups import getorgsitegroup as getorgsitegroup
from .orgs_sites import countorgsites as countorgsites
from .orgs_sites import searchorgsites as searchorgsites
from .orgs_sites import listorgsitetemplates as listorgsitetemplates
from .orgs_stats import getorgstats as getorgstats
from .orgs_stats import countorgbgpstats as countorgbgpstats
from .orgs_stats import searchorgbgpstats as searchorgbgpstats
from .orgs_stats import listorgdevicesstats as listorgdevicesstats
from .orgs_stats import listorgmxedgesstats as listorgmxedgesstats
from .orgs_stats import getorgotherdevicestats as getorgotherdevicestats
from .orgs_stats import countorgsworgwports as countorgsworgwports
from .orgs_stats import searchorgsworgwports as searchorgsworgwports
from .orgs_stats import listorgsitestats as listorgsitestats
from .orgs_stats import countorgtunnelsstats as countorgtunnelsstats
from .orgs_stats import searchorgtunnelsstats as searchorgtunnelsstats
from .orgs_stats import countorgpeerpathstats as countorgpeerpathstats
from .orgs_stats import searchorgpeerpathstats as searchorgpeerpathstats
from .orgs_marvis import troubleshootorg as troubleshootorg
from .orgs_webhooks import listorgwebhooks as listorgwebhooks
from .orgs_webhooks import countorgwebhooksdeliveries as countorgwebhooksdeliveries
from .orgs_webhooks import searchorgwebhooksdeliveries as searchorgwebhooksdeliveries
from .self_account import getself as getself
from .self_account import getselfloginfailures as getselfloginfailures
from .self_account import listselfauditlogs as listselfauditlogs
from .self_account import getselfapiusage as getselfapiusage
from .sites import getsiteinfo as getsiteinfo
from .sites import getsitesetting as getsitesetting
from .sites import getsitesettingderived as getsitesettingderived
from .sites_wan import listsiteapps as listsiteapps
from .sites_wan import listsitegatewaytemplatederived as listsitegatewaytemplatederived
from .sites_wan import listsitenetworksderived as listsitenetworksderived
from .sites_wan import (
    listsitesecintelprofilesderived as listsitesecintelprofilesderived,
)
from .sites_wan import listsiteservicepoliciesderived as listsiteservicepoliciesderived
from .sites_wan import listsiteservicesderived as listsiteservicesderived
from .sites_wan import countsiteservicepathevents as countsiteservicepathevents
from .sites_wan import searchsiteservicepathevents as searchsiteservicepathevents
from .sites_wan import listsitevpnsderived as listsitevpnsderived
from .sites_clients import countsitewirelessclients as countsitewirelessclients
from .sites_clients import (
    countsitewirelessclientevents as countsitewirelessclientevents,
)
from .sites_clients import (
    searchsitewirelessclientevents as searchsitewirelessclientevents,
)
from .sites_clients import searchsitewirelessclients as searchsitewirelessclients
from .sites_clients import (
    countsitewirelessclientsessions as countsitewirelessclientsessions,
)
from .sites_clients import (
    searchsitewirelessclientsessions as searchsitewirelessclientsessions,
)
from .sites_clients import getsiteeventsforclient as getsiteeventsforclient
from .sites_clients import (
    listsiteallguestauthorizations as listsiteallguestauthorizations,
)
from .sites_clients import countsiteguestauthorizations as countsiteguestauthorizations
from .sites_clients import (
    listsiteallguestauthorizationsderived as listsiteallguestauthorizationsderived,
)
from .sites_clients import searchsiteguestauthorization as searchsiteguestauthorization
from .sites_clients import getsiteguestauthorization as getsiteguestauthorization
from .sites_clients import countsitenacclients as countsitenacclients
from .sites_clients import countsitenacclientevents as countsitenacclientevents
from .sites_clients import searchsitenacclientevents as searchsitenacclientevents
from .sites_clients import searchsitenacclients as searchsitenacclients
from .sites_clients import countsitewanclientevents as countsitewanclientevents
from .sites_clients import countsitewanclients as countsitewanclients
from .sites_clients import searchsitewanclientevents as searchsitewanclientevents
from .sites_clients import searchsitewanclients as searchsitewanclients
from .sites_clients import countsitewiredclients as countsitewiredclients
from .sites_clients import searchsitewiredclients as searchsitewiredclients
from .sites_devices import listsitedevices as listsitedevices
from .sites_devices import countsitedeviceconfighistory as countsitedeviceconfighistory
from .sites_devices import (
    searchsitedeviceconfighistory as searchsitedeviceconfighistory,
)
from .sites_devices import countsitedevices as countsitedevices
from .sites_devices import countsitedeviceevents as countsitedeviceevents
from .sites_devices import searchsitedeviceevents as searchsitedeviceevents
from .sites_devices import exportsitedevices as exportsitedevices
from .sites_devices import countsitedevicelastconfig as countsitedevicelastconfig
from .sites_devices import searchsitedevicelastconfigs as searchsitedevicelastconfigs
from .sites_devices import searchsitedevices as searchsitedevices
from .sites_synthetic_tests import (
    getsitedevicesynthetictest as getsitedevicesynthetictest,
)
from .sites_synthetic_tests import searchsitesynthetictest as searchsitesynthetictest
from .sites_events import countsitesystemevents as countsitesystemevents
from .sites_events import searchsitesystemevents as searchsitesystemevents
from .sites_lan import listsiteevpntopologies as listsiteevpntopologies
from .sites_lan import listsitenetworktemplatederived as listsitenetworktemplatederived
from .sites_insights import (
    getsiteinsightmetricsforclient as getsiteinsightmetricsforclient,
)
from .sites_insights import (
    getsiteinsightmetricsfordevice as getsiteinsightmetricsfordevice,
)
from .sites_insights import getsiteinsightmetrics as getsiteinsightmetrics
from .sites_rogues import listsiterogueaps as listsiterogueaps
from .sites_rogues import listsiterogueclients as listsiterogueclients
from .sites_rogues import countsiterogueevents as countsiterogueevents
from .sites_rogues import searchsiterogueevents as searchsiterogueevents
from .sites_rogues import getsiterogueap as getsiterogueap
from .sites_maps import listsitemaps as listsitemaps
from .sites_mxedges import listsitemxedges as listsitemxedges
from .sites_mxedges import countsitemxedgeevents as countsitemxedgeevents
from .sites_mxedges import searchsitemistedgeevents as searchsitemistedgeevents
from .sites_wlans import listsitepsks as listsitepsks
from .sites_wlans import listsiterftemplatederived as listsiterftemplatederived
from .sites_wlans import listsitewlans as listsitewlans
from .sites_wlans import listsitewlanderived as listsitewlanderived
from .sites_wlans import listsitewxrules as listsitewxrules
from .sites_wlans import listsitewxrulesderived as listsitewxrulesderived
from .sites_wlans import listsitewxtags as listsitewxtags
from .sites_wlans import getsiteapplicationlist as getsiteapplicationlist
from .sites_rfdiags import getsitesiterfdiagrecording as getsitesiterfdiagrecording
from .sites_rfdiags import getsiterfdiagrecording as getsiterfdiagrecording
from .sites_rfdiags import downloadsiterfdiagrecording as downloadsiterfdiagrecording
from .sites_rrm import getsitecurrentchannelplanning as getsitecurrentchannelplanning
from .sites_rrm import (
    getsitecurrentrrmconsiderations as getsitecurrentrrmconsiderations,
)
from .sites_rrm import listsiterrmevents as listsiterrmevents
from .sites_rrm import listsitecurrentrrmneighbors as listsitecurrentrrmneighbors
from .sites_sles import getsitesleclassifierdetails as getsitesleclassifierdetails
from .sites_sles import listsiteslemetricclassifiers as listsiteslemetricclassifiers
from .sites_sles import getsiteslehistogram as getsiteslehistogram
from .sites_sles import getsitesleimpactsummary as getsitesleimpactsummary
from .sites_sles import (
    listsitesleimpactedapplications as listsitesleimpactedapplications,
)
from .sites_sles import listsitesleimpactedaps as listsitesleimpactedaps
from .sites_sles import listsitesleimpactedchassis as listsitesleimpactedchassis
from .sites_sles import (
    listsitesleimpactedwiredclients as listsitesleimpactedwiredclients,
)
from .sites_sles import listsitesleimpactedgateways as listsitesleimpactedgateways
from .sites_sles import listsitesleimpactedinterfaces as listsitesleimpactedinterfaces
from .sites_sles import listsitesleimpactedswitches as listsitesleimpactedswitches
from .sites_sles import (
    listsitesleimpactedwirelessclients as listsitesleimpactedwirelessclients,
)
from .sites_sles import getsiteslesummary as getsiteslesummary
from .sites_sles import getsiteslethreshold as getsiteslethreshold
from .sites_sles import listsiteslesmetrics as listsiteslesmetrics
from .sites_stats import getsitestats as getsitestats
from .sites_stats import countsiteapps as countsiteapps
from .sites_stats import troubleshootsitecall as troubleshootsitecall
from .sites_stats import countsitecalls as countsitecalls
from .sites_stats import searchsitecalls as searchsitecalls
from .sites_stats import getsitecallssummary as getsitecallssummary
from .sites_stats import listsitetroubleshootcalls as listsitetroubleshootcalls
from .sites_stats import listsitewirelessclientsstats as listsitewirelessclientsstats
from .sites_stats import (
    searchsitediscoveredswitchesmetrics as searchsitediscoveredswitchesmetrics,
)
from .sites_stats import countsitediscoveredswitches as countsitediscoveredswitches
from .sites_stats import (
    listsitediscoveredswitchesmetrics as listsitediscoveredswitchesmetrics,
)
from .sites_stats import searchsitediscoveredswitches as searchsitediscoveredswitches
from .sites_stats import (
    getsitewirelessclientsstatsbymap as getsitewirelessclientsstatsbymap,
)
from .sites_stats import (
    listsiteunconnectedclientstats as listsiteunconnectedclientstats,
)
from .sites_stats import listsitemxedgesstats as listsitemxedgesstats
from .sites_stats import getsitewxrulesusage as getsitewxrulesusage
from .sites_wan_usages import countsitewanusage as countsitewanusage
from .sites_wan_usages import searchsitewanusage as searchsitewanusage
from .sites_webhooks import listsitewebhooks as listsitewebhooks
from .sites_webhooks import countsitewebhooksdeliveries as countsitewebhooksdeliveries
from .sites_webhooks import searchsitewebhooksdeliveries as searchsitewebhooksdeliveries
