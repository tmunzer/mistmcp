"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

from .constants_definitions import listapchannels as listapchannels
from .constants_definitions import listapleddefinition as listapleddefinition
from .constants_definitions import listfingerprinttypes as listfingerprinttypes
from .constants_definitions import listinsightmetrics as listinsightmetrics
from .constants_definitions import listlicensetypes as listlicensetypes
from .constants_definitions import listwebhooktopics as listwebhooktopics
from .orgs import getorg as getorg
from .orgs import searchorgalarms as searchorgalarms
from .orgs import searchorgevents as searchorgevents
from .orgs import listorgauditlogs as listorgauditlogs
from .orgs import getorgsettings as getorgsettings
from .templates_wan import listorgaamwprofiles as listorgaamwprofiles
from .templates_wan import listorgantivirusprofiles as listorgantivirusprofiles
from .templates_wan import listorggatewaytemplates as listorggatewaytemplates
from .templates_wan import listorgidpprofiles as listorgidpprofiles
from .templates_wan import listorgnetworks as listorgnetworks
from .templates_wan import listorgsecpolicies as listorgsecpolicies
from .templates_wan import listorgservicepolicies as listorgservicepolicies
from .templates_wan import listorgservices as listorgservices
from .templates_wan import listorgvpns as listorgvpns
from .templates_wan import listsiteapps as listsiteapps
from .templates_wan import (
    listsitegatewaytemplatederived as listsitegatewaytemplatederived,
)
from .templates_wan import listsitenetworksderived as listsitenetworksderived
from .templates_wan import (
    listsitesecintelprofilesderived as listsitesecintelprofilesderived,
)
from .templates_wan import (
    listsiteservicepoliciesderived as listsiteservicepoliciesderived,
)
from .templates_wan import listsiteservicesderived as listsiteservicesderived
from .templates_wan import searchsiteservicepathevents as searchsiteservicepathevents
from .templates_wan import listsitevpnsderived as listsitevpnsderived
from .templates_alarms import listorgalarmtemplates as listorgalarmtemplates
from .templates_alarms import listorgsuppressedalarms as listorgsuppressedalarms
from .templates_alarms import getorgalarmtemplate as getorgalarmtemplate
from .templates_devices import listorgaptemplates as listorgaptemplates
from .templates_devices import listorgdeviceprofiles as listorgdeviceprofiles
from .templates_devices import listsiteaptemplatederived as listsiteaptemplatederived
from .templates_devices import (
    listsitedeviceprofilesderived as listsitedeviceprofilesderived,
)
from .orgs_licenses import (
    getorglicenseasyncclaimstatus as getorglicenseasyncclaimstatus,
)
from .orgs_licenses import getorglicensessummary as getorglicensessummary
from .orgs_licenses import getorglicensesbysite as getorglicensesbysite
from .clients import searchorgwirelessclientevents as searchorgwirelessclientevents
from .clients import searchorgwirelessclients as searchorgwirelessclients
from .clients import searchorgwirelessclientsessions as searchorgwirelessclientsessions
from .clients import listorgguestauthorizations as listorgguestauthorizations
from .clients import searchorgguestauthorization as searchorgguestauthorization
from .clients import searchorgnacclientevents as searchorgnacclientevents
from .clients import searchorgnacclients as searchorgnacclients
from .clients import searchorgwanclientevents as searchorgwanclientevents
from .clients import searchorgwanclients as searchorgwanclients
from .clients import searchorgwiredclients as searchorgwiredclients
from .clients import listsiteallguestauthorizations as listsiteallguestauthorizations
from .clients import (
    listsiteallguestauthorizationsderived as listsiteallguestauthorizationsderived,
)
from .clients import searchsiteguestauthorization as searchsiteguestauthorization
from .devices import searchorgdeviceevents as searchorgdeviceevents
from .devices import listorgapsmacs as listorgapsmacs
from .devices import searchorgdevices as searchorgdevices
from .devices import listorgdevicessummary as listorgdevicessummary
from .devices import getorginventory as getorginventory
from .devices import searchorginventory as searchorginventory
from .devices import getorgjuniperdevicescommand as getorgjuniperdevicescommand
from .devices import listsitedevices as listsitedevices
from .devices import searchsitedeviceconfighistory as searchsitedeviceconfighistory
from .devices import searchsitedeviceevents as searchsitedeviceevents
from .devices import searchsitedevicelastconfigs as searchsitedevicelastconfigs
from .devices import searchsitedevices as searchsitedevices
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
from .templates_switches import listorgevpntopologies as listorgevpntopologies
from .templates_switches import listorgnetworktemplates as listorgnetworktemplates
from .templates_switches import listsiteevpntopologies as listsiteevpntopologies
from .templates_switches import (
    listsitenetworktemplatederived as listsitenetworktemplatederived,
)
from .orgs_sles import getorgsitessle as getorgsitessle
from .orgs_sles import getorgsle as getorgsle
from .mxedges import listorgmxedgeclusters as listorgmxedgeclusters
from .mxedges import listorgmxedges as listorgmxedges
from .mxedges import searchorgmistedgeevents as searchorgmistedgeevents
from .mxedges import searchorgmxedges as searchorgmxedges
from .mxedges import getorgmxedgeupgradeinfo as getorgmxedgeupgradeinfo
from .mxedges import listorgmxtunnels as listorgmxtunnels
from .mxedges import listsitemxedges as listsitemxedges
from .mxedges import searchsitemistedgeevents as searchsitemistedgeevents
from .orgs_nac import listorgnacrules as listorgnacrules
from .orgs_nac import listorgnactags as listorgnactags
from .orgs_nac import searchorgusermacs as searchorgusermacs
from .orgs_nac import searchorgclientfingerprints as searchorgclientfingerprints
from .orgs_wlans import listorgpsks as listorgpsks
from .orgs_wlans import listorgrftemplates as listorgrftemplates
from .orgs_wlans import listorgtemplates as listorgtemplates
from .orgs_wlans import listorgwlans as listorgwlans
from .orgs_wlans import listorgwxrules as listorgwxrules
from .orgs_wlans import listorgwxtags as listorgwxtags
from .orgs_wlans import getorgapplicationlist as getorgapplicationlist
from .orgs_wlans import (
    getorgcurrentmatchingclientsofawxtag as getorgcurrentmatchingclientsofawxtag,
)
from .orgs_sites import listorgsitegroups as listorgsitegroups
from .orgs_sites import searchorgsites as searchorgsites
from .orgs_sites import listorgsitetemplates as listorgsitetemplates
from .orgs_stats import getorgstats as getorgstats
from .orgs_stats import searchorgbgpstats as searchorgbgpstats
from .orgs_stats import listorgdevicesstats as listorgdevicesstats
from .orgs_stats import listorgmxedgesstats as listorgmxedgesstats
from .orgs_stats import getorgotherdevicestats as getorgotherdevicestats
from .orgs_stats import searchorgsworgwports as searchorgsworgwports
from .orgs_stats import listorgsitestats as listorgsitestats
from .orgs_stats import searchorgtunnelsstats as searchorgtunnelsstats
from .orgs_stats import searchorgpeerpathstats as searchorgpeerpathstats
from .marvis import troubleshootorg as troubleshootorg
from .marvis import searchsitesynthetictest as searchsitesynthetictest
from .webhooks import listorgwebhooks as listorgwebhooks
from .webhooks import searchorgwebhooksdeliveries as searchorgwebhooksdeliveries
from .webhooks import listsitewebhooks as listsitewebhooks
from .webhooks import searchsitewebhooksdeliveries as searchsitewebhooksdeliveries
from .self_account import getself as getself
from .self_account import getselfloginfailures as getselfloginfailures
from .self_account import listselfauditlogs as listselfauditlogs
from .self_account import getselfapiusage as getselfapiusage
from .sites import getsiteinfo as getsiteinfo
from .sites import listsitemaps as listsitemaps
from .sites import getsitesetting as getsitesetting
from .sites import getsitesettingderived as getsitesettingderived
from .sites_insights import (
    getsiteinsightmetricsforclient as getsiteinsightmetricsforclient,
)
from .sites_insights import (
    getsiteinsightmetricsfordevice as getsiteinsightmetricsfordevice,
)
from .sites_insights import getsiteinsightmetrics as getsiteinsightmetrics
from .sites_rogues import listsiterogueaps as listsiterogueaps
from .sites_rogues import listsiterogueclients as listsiterogueclients
from .sites_rogues import searchsiterogueevents as searchsiterogueevents
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
from .sites_stats import troubleshootsitecall as troubleshootsitecall
from .sites_stats import searchsitecalls as searchsitecalls
from .sites_stats import getsitecallssummary as getsitecallssummary
from .sites_stats import listsitetroubleshootcalls as listsitetroubleshootcalls
from .sites_stats import listsitewirelessclientsstats as listsitewirelessclientsstats
from .sites_stats import (
    searchsitediscoveredswitchesmetrics as searchsitediscoveredswitchesmetrics,
)
from .sites_stats import (
    listsitediscoveredswitchesmetrics as listsitediscoveredswitchesmetrics,
)
from .sites_stats import searchsitediscoveredswitches as searchsitediscoveredswitches
from .sites_stats import listsitemxedgesstats as listsitemxedgesstats
from .sites_stats import getsitewxrulesusage as getsitewxrulesusage
from .sites_wan_usages import searchsitewanusage as searchsitewanusage
