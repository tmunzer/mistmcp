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
from .constants_definitions import listapleslversions as listapleslversions
from .constants_definitions import listapleddefinition as listapleddefinition
from .constants_definitions import (
    listappcategorydefinitions as listappcategorydefinitions,
)
from .constants_definitions import (
    listappsubcategorydefinitions as listappsubcategorydefinitions,
)
from .constants_definitions import listapplications as listapplications
from .constants_definitions import listcountrycodes as listcountrycodes
from .constants_definitions import listfingerprinttypes as listfingerprinttypes
from .constants_definitions import listgatewayapplications as listgatewayapplications
from .constants_definitions import listinsightmetrics as listinsightmetrics
from .constants_definitions import listsitelanguages as listsitelanguages
from .constants_definitions import listlicensetypes as listlicensetypes
from .constants_definitions import listmarvisclientversions as listmarvisclientversions
from .constants_definitions import liststates as liststates
from .constants_definitions import listtraffictypes as listtraffictypes
from .constants_definitions import listwebhooktopics as listwebhooktopics
from .constants_models import getgatewaydefaultconfig as getgatewaydefaultconfig
from .constants_models import listdevicemodels as listdevicemodels
from .constants_models import listmxedgemodels as listmxedgemodels
from .constants_models import (
    listsupportedotherdevicemodels as listsupportedotherdevicemodels,
)
from .orgs import getorg as getorg
from .orgs import searchorgevents as searchorgevents
from .orgs_advanced_anti_malware_profiles import (
    listorgaamwprofiles as listorgaamwprofiles,
)
from .orgs_advanced_anti_malware_profiles import getorgaamwprofile as getorgaamwprofile
from .orgs_alarms import countorgalarms as countorgalarms
from .orgs_alarms import searchorgalarms as searchorgalarms
from .orgs_alarm_templates import listorgalarmtemplates as listorgalarmtemplates
from .orgs_alarm_templates import listorgsuppressedalarms as listorgsuppressedalarms
from .orgs_alarm_templates import getorgalarmtemplate as getorgalarmtemplate
from .orgs_ap_templates import listorgaptemplates as listorgaptemplates
from .orgs_ap_templates import getorgaptemplate as getorgaptemplate
from .orgs_antivirus_profiles import (
    listorgantivirusprofiles as listorgantivirusprofiles,
)
from .orgs_antivirus_profiles import getorgantivirusprofile as getorgantivirusprofile
from .orgs_licenses import (
    getorglicenseasyncclaimstatus as getorglicenseasyncclaimstatus,
)
from .orgs_licenses import getorglicensessummary as getorglicensessummary
from .orgs_licenses import getorglicensesbysite as getorglicensesbysite
from .orgs_clients___wireless import countorgwirelessclients as countorgwirelessclients
from .orgs_clients___wireless import (
    searchorgwirelessclientevents as searchorgwirelessclientevents,
)
from .orgs_clients___wireless import (
    searchorgwirelessclients as searchorgwirelessclients,
)
from .orgs_clients___wireless import (
    countorgwirelessclientssessions as countorgwirelessclientssessions,
)
from .orgs_clients___wireless import (
    searchorgwirelessclientsessions as searchorgwirelessclientsessions,
)
from .orgs_device_profiles import listorgdeviceprofiles as listorgdeviceprofiles
from .orgs_device_profiles import getorgdeviceprofile as getorgdeviceprofile
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
from .utilities_upgrade import getorgdeviceupgrade as getorgdeviceupgrade
from .utilities_upgrade import (
    listorgavailabledeviceversions as listorgavailabledeviceversions,
)
from .utilities_upgrade import listorgmxedgeupgrades as listorgmxedgeupgrades
from .utilities_upgrade import getorgmxedgeupgrade as getorgmxedgeupgrade
from .utilities_upgrade import listorgssrupgrades as listorgssrupgrades
from .utilities_upgrade import (
    listorgavailablessrversions as listorgavailablessrversions,
)
from .utilities_upgrade import listsitedeviceupgrades as listsitedeviceupgrades
from .utilities_upgrade import getsitedeviceupgrade as getsitedeviceupgrade
from .utilities_upgrade import (
    listsiteavailabledeviceversions as listsiteavailabledeviceversions,
)
from .utilities_upgrade import getsitessrupgrade as getsitessrupgrade
from .orgs_events import countorgsystemevents as countorgsystemevents
from .orgs_events import searchorgsystemevents as searchorgsystemevents
from .orgs_evpn_topologies import listorgevpntopologies as listorgevpntopologies
from .orgs_evpn_topologies import getorgevpntopology as getorgevpntopology
from .orgs_gateway_templates import listorggatewaytemplates as listorggatewaytemplates
from .orgs_gateway_templates import getorggatewaytemplate as getorggatewaytemplate
from .orgs_guests import listorgguestauthorizations as listorgguestauthorizations
from .orgs_guests import countorgguestauthorizations as countorgguestauthorizations
from .orgs_guests import searchorgguestauthorization as searchorgguestauthorization
from .orgs_guests import getorgguestauthorization as getorgguestauthorization
from .orgs_idp_profiles import listorgidpprofiles as listorgidpprofiles
from .orgs_idp_profiles import getorgidpprofile as getorgidpprofile
from .orgs_sles import getorgsitessle as getorgsitessle
from .orgs_sles import getorgsle as getorgsle
from .orgs_inventory import getorginventory as getorginventory
from .orgs_inventory import countorginventory as countorginventory
from .orgs_inventory import searchorginventory as searchorginventory
from .orgs_logs import listorgauditlogs as listorgauditlogs
from .orgs_logs import countorgauditlogs as countorgauditlogs
from .orgs_mxclusters import listorgmxedgeclusters as listorgmxedgeclusters
from .orgs_mxclusters import getorgmxedgecluster as getorgmxedgecluster
from .orgs_mxedges import listorgmxedges as listorgmxedges
from .orgs_mxedges import countorgmxedges as countorgmxedges
from .orgs_mxedges import countorgsitemxedgeevents as countorgsitemxedgeevents
from .orgs_mxedges import searchorgmistedgeevents as searchorgmistedgeevents
from .orgs_mxedges import searchorgmxedges as searchorgmxedges
from .orgs_mxedges import getorgmxedgeupgradeinfo as getorgmxedgeupgradeinfo
from .orgs_mxedges import getorgmxedge as getorgmxedge
from .orgs_mxtunnels import listorgmxtunnels as listorgmxtunnels
from .orgs_mxtunnels import getorgmxtunnel as getorgmxtunnel
from .orgs_clients___nac import countorgnacclients as countorgnacclients
from .orgs_clients___nac import countorgnacclientevents as countorgnacclientevents
from .orgs_clients___nac import searchorgnacclientevents as searchorgnacclientevents
from .orgs_clients___nac import searchorgnacclients as searchorgnacclients
from .orgs_nac_rules import listorgnacrules as listorgnacrules
from .orgs_nac_rules import getorgnacrule as getorgnacrule
from .orgs_nac_tags import listorgnactags as listorgnactags
from .orgs_nac_tags import getorgnactag as getorgnactag
from .orgs_networks import listorgnetworks as listorgnetworks
from .orgs_networks import getorgnetwork as getorgnetwork
from .orgs_network_templates import listorgnetworktemplates as listorgnetworktemplates
from .orgs_network_templates import getorgnetworktemplate as getorgnetworktemplate
from .orgs_devices___others import listorgotherdevices as listorgotherdevices
from .orgs_devices___others import (
    countorgotherdeviceevents as countorgotherdeviceevents,
)
from .orgs_devices___others import (
    searchorgotherdeviceevents as searchorgotherdeviceevents,
)
from .orgs_devices___others import getorgotherdevice as getorgotherdevice
from .orgs_psks import listorgpsks as listorgpsks
from .orgs_psks import getorgpsk as getorgpsk
from .orgs_rf_templates import listorgrftemplates as listorgrftemplates
from .orgs_rf_templates import getorgrftemplate as getorgrftemplate
from .orgs_security_policies import listorgsecpolicies as listorgsecpolicies
from .orgs_security_policies import getorgsecpolicy as getorgsecpolicy
from .orgs_service_policies import listorgservicepolicies as listorgservicepolicies
from .orgs_service_policies import getorgservicepolicy as getorgservicepolicy
from .orgs_services import listorgservices as listorgservices
from .orgs_services import getorgservice as getorgservice
from .orgs_setting import getorgsettings as getorgsettings
from .orgs_integration_skyatp import getorgskyatpintegration as getorgskyatpintegration
from .orgs_sitegroups import listorgsitegroups as listorgsitegroups
from .orgs_sitegroups import getorgsitegroup as getorgsitegroup
from .orgs_sites import listorgsites as listorgsites
from .orgs_sites import countorgsites as countorgsites
from .orgs_sites import searchorgsites as searchorgsites
from .orgs_site_templates import listorgsitetemplates as listorgsitetemplates
from .orgs_site_templates import getorgsitetemplate as getorgsitetemplate
from .orgs_stats import getorgstats as getorgstats
from .orgs_stats___bgp_peers import countorgbgpstats as countorgbgpstats
from .orgs_stats___bgp_peers import searchorgbgpstats as searchorgbgpstats
from .orgs_stats___devices import listorgdevicesstats as listorgdevicesstats
from .orgs_stats___mxedges import listorgmxedgesstats as listorgmxedgesstats
from .orgs_stats___mxedges import getorgmxedgestats as getorgmxedgestats
from .orgs_stats___other_devices import getorgotherdevicestats as getorgotherdevicestats
from .orgs_stats___ports import countorgsworgwports as countorgsworgwports
from .orgs_stats___ports import searchorgsworgwports as searchorgsworgwports
from .orgs_stats___sites import listorgsitestats as listorgsitestats
from .orgs_stats___tunnels import countorgtunnelsstats as countorgtunnelsstats
from .orgs_stats___tunnels import searchorgtunnelsstats as searchorgtunnelsstats
from .orgs_stats___vpn_peers import countorgpeerpathstats as countorgpeerpathstats
from .orgs_stats___vpn_peers import searchorgpeerpathstats as searchorgpeerpathstats
from .orgs_wlan_templates import listorgtemplates as listorgtemplates
from .orgs_wlan_templates import getorgtemplate as getorgtemplate
from .orgs_marvis import troubleshootorg as troubleshootorg
from .orgs_user_macs import searchorgusermacs as searchorgusermacs
from .orgs_user_macs import getorgusermac as getorgusermac
from .orgs_vpns import listorgvpns as listorgvpns
from .orgs_vpns import getorgvpn as getorgvpn
from .orgs_clients___wan import countorgwanclientevents as countorgwanclientevents
from .orgs_clients___wan import countorgwanclients as countorgwanclients
from .orgs_clients___wan import searchorgwanclientevents as searchorgwanclientevents
from .orgs_clients___wan import searchorgwanclients as searchorgwanclients
from .orgs_webhooks import listorgwebhooks as listorgwebhooks
from .orgs_webhooks import getorgwebhook as getorgwebhook
from .orgs_webhooks import countorgwebhooksdeliveries as countorgwebhooksdeliveries
from .orgs_webhooks import searchorgwebhooksdeliveries as searchorgwebhooksdeliveries
from .orgs_clients___wired import countorgwiredclients as countorgwiredclients
from .orgs_clients___wired import searchorgwiredclients as searchorgwiredclients
from .orgs_wlans import listorgwlans as listorgwlans
from .orgs_wlans import getorgwlan as getorgwlan
from .orgs_wxrules import listorgwxrules as listorgwxrules
from .orgs_wxrules import getorgwxrule as getorgwxrule
from .orgs_wxtags import listorgwxtags as listorgwxtags
from .orgs_wxtags import getorgapplicationlist as getorgapplicationlist
from .orgs_wxtags import getorgwxtag as getorgwxtag
from .orgs_wxtags import (
    getorgcurrentmatchingclientsofawxtag as getorgcurrentmatchingclientsofawxtag,
)
from .admins import getadminregistrationinfo as getadminregistrationinfo
from .self_account import getself as getself
from .self_account import getselfloginfailures as getselfloginfailures
from .self_account import verifyselfemail as verifyselfemail
from .self_account import getselfapiusage as getselfapiusage
from .self_audit_logs import listselfauditlogs as listselfauditlogs
from .self_alarms import listalarmsubscriptions as listalarmsubscriptions
from .sites import getsiteinfo as getsiteinfo
from .sites_derived_config import listsiteapps as listsiteapps
from .sites_derived_config import listsiteaptemplatederived as listsiteaptemplatederived
from .sites_derived_config import (
    listsitedeviceprofilesderived as listsitedeviceprofilesderived,
)
from .sites_derived_config import (
    listsitegatewaytemplatederived as listsitegatewaytemplatederived,
)
from .sites_derived_config import listsitenetworksderived as listsitenetworksderived
from .sites_derived_config import (
    listsitenetworktemplatederived as listsitenetworktemplatederived,
)
from .sites_derived_config import listsiterftemplatederived as listsiterftemplatederived
from .sites_derived_config import (
    listsitesecintelprofilesderived as listsitesecintelprofilesderived,
)
from .sites_derived_config import (
    listsiteservicepoliciesderived as listsiteservicepoliciesderived,
)
from .sites_derived_config import listsiteservicesderived as listsiteservicesderived
from .sites_derived_config import (
    countsiteservicepathevents as countsiteservicepathevents,
)
from .sites_derived_config import (
    searchsiteservicepathevents as searchsiteservicepathevents,
)
from .sites_derived_config import (
    listsitesitetemplatederived as listsitesitetemplatederived,
)
from .sites_derived_config import countsiteskyatpevents as countsiteskyatpevents
from .sites_derived_config import searchsiteskyatpevents as searchsiteskyatpevents
from .sites_clients___wireless import (
    countsitewirelessclients as countsitewirelessclients,
)
from .sites_clients___wireless import (
    countsitewirelessclientevents as countsitewirelessclientevents,
)
from .sites_clients___wireless import (
    searchsitewirelessclientevents as searchsitewirelessclientevents,
)
from .sites_clients___wireless import (
    searchsitewirelessclients as searchsitewirelessclients,
)
from .sites_clients___wireless import (
    countsitewirelessclientsessions as countsitewirelessclientsessions,
)
from .sites_clients___wireless import (
    searchsitewirelessclientsessions as searchsitewirelessclientsessions,
)
from .sites_clients___wireless import getsiteeventsforclient as getsiteeventsforclient
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
from .sites_devices import getsitedevice as getsitedevice
from .sites_synthetic_tests import (
    getsitedevicesynthetictest as getsitedevicesynthetictest,
)
from .sites_synthetic_tests import searchsitesynthetictest as searchsitesynthetictest
from .sites_events import listsiteroamingevents as listsiteroamingevents
from .sites_events import countsitesystemevents as countsitesystemevents
from .sites_events import searchsitesystemevents as searchsitesystemevents
from .sites_evpn_topologies import listsiteevpntopologies as listsiteevpntopologies
from .sites_evpn_topologies import getsiteevpntopology as getsiteevpntopology
from .sites_guests import (
    listsiteallguestauthorizations as listsiteallguestauthorizations,
)
from .sites_guests import countsiteguestauthorizations as countsiteguestauthorizations
from .sites_guests import (
    listsiteallguestauthorizationsderived as listsiteallguestauthorizationsderived,
)
from .sites_guests import searchsiteguestauthorization as searchsiteguestauthorization
from .sites_guests import getsiteguestauthorization as getsiteguestauthorization
from .sites_insights import (
    getsiteinsightmetricsforclient as getsiteinsightmetricsforclient,
)
from .sites_insights import (
    getsiteinsightmetricsfordevice as getsiteinsightmetricsfordevice,
)
from .sites_insights import getsiteinsightmetrics as getsiteinsightmetrics
from .orgs_nac_fingerprints import (
    countorgclientfingerprints as countorgclientfingerprints,
)
from .orgs_nac_fingerprints import (
    searchorgclientfingerprints as searchorgclientfingerprints,
)
from .sites_rogues import listsiterogueaps as listsiterogueaps
from .sites_rogues import listsiterogueclients as listsiterogueclients
from .sites_rogues import countsiterogueevents as countsiterogueevents
from .sites_rogues import searchsiterogueevents as searchsiterogueevents
from .sites_rogues import getsiterogueap as getsiterogueap
from .sites_maps import listsitemaps as listsitemaps
from .sites_maps import getsitemap as getsitemap
from .sites_maps___auto_zone import getsitemapautozonestatus as getsitemapautozonestatus
from .sites_mxedges import listsitemxedges as listsitemxedges
from .sites_mxedges import countsitemxedgeevents as countsitemxedgeevents
from .sites_mxedges import searchsitemistedgeevents as searchsitemistedgeevents
from .sites_mxedges import getsitemxedge as getsitemxedge
from .sites_clients___nac import countsitenacclients as countsitenacclients
from .sites_clients___nac import countsitenacclientevents as countsitenacclientevents
from .sites_clients___nac import searchsitenacclientevents as searchsitenacclientevents
from .sites_clients___nac import searchsitenacclients as searchsitenacclients
from .sites_psks import listsitepsks as listsitepsks
from .sites_psks import getsitepsk as getsitepsk
from .sites_rfdiags import getsitesiterfdiagrecording as getsitesiterfdiagrecording
from .sites_rfdiags import getsiterfdiagrecording as getsiterfdiagrecording
from .sites_rfdiags import downloadsiterfdiagrecording as downloadsiterfdiagrecording
from .sites_rrm import getsitecurrentchannelplanning as getsitecurrentchannelplanning
from .sites_rrm import (
    getsitecurrentrrmconsiderations as getsitecurrentrrmconsiderations,
)
from .sites_rrm import listsiterrmevents as listsiterrmevents
from .sites_rrm import listsitecurrentrrmneighbors as listsitecurrentrrmneighbors
from .sites_setting import getsitesetting as getsitesetting
from .sites_setting import getsitesettingderived as getsitesettingderived
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
from .sites_stats___apps import countsiteapps as countsiteapps
from .sites_stats___calls import troubleshootsitecall as troubleshootsitecall
from .sites_stats___calls import countsitecalls as countsitecalls
from .sites_stats___calls import searchsitecalls as searchsitecalls
from .sites_stats___calls import getsitecallssummary as getsitecallssummary
from .sites_stats___calls import listsitetroubleshootcalls as listsitetroubleshootcalls
from .sites_stats___clients_wireless import (
    listsitewirelessclientsstats as listsitewirelessclientsstats,
)
from .sites_stats___clients_wireless import (
    getsitewirelessclientstats as getsitewirelessclientstats,
)
from .sites_stats___clients_wireless import (
    getsitewirelessclientsstatsbymap as getsitewirelessclientsstatsbymap,
)
from .sites_stats___clients_wireless import (
    listsiteunconnectedclientstats as listsiteunconnectedclientstats,
)
from .sites_stats___discovered_switches import (
    searchsitediscoveredswitchesmetrics as searchsitediscoveredswitchesmetrics,
)
from .sites_stats___discovered_switches import (
    countsitediscoveredswitches as countsitediscoveredswitches,
)
from .sites_stats___discovered_switches import (
    listsitediscoveredswitchesmetrics as listsitediscoveredswitchesmetrics,
)
from .sites_stats___discovered_switches import (
    searchsitediscoveredswitches as searchsitediscoveredswitches,
)
from .sites_stats___mxedges import listsitemxedgesstats as listsitemxedgesstats
from .sites_stats___mxedges import getsitemxedgestats as getsitemxedgestats
from .sites_stats___wxrules import getsitewxrulesusage as getsitewxrulesusage
from .sites_vpns import listsitevpnsderived as listsitevpnsderived
from .sites_clients___wan import countsitewanclientevents as countsitewanclientevents
from .sites_clients___wan import countsitewanclients as countsitewanclients
from .sites_clients___wan import searchsitewanclientevents as searchsitewanclientevents
from .sites_clients___wan import searchsitewanclients as searchsitewanclients
from .sites_wan_usages import countsitewanusage as countsitewanusage
from .sites_wan_usages import searchsitewanusage as searchsitewanusage
from .sites_webhooks import listsitewebhooks as listsitewebhooks
from .sites_webhooks import getsitewebhook as getsitewebhook
from .sites_webhooks import countsitewebhooksdeliveries as countsitewebhooksdeliveries
from .sites_webhooks import searchsitewebhooksdeliveries as searchsitewebhooksdeliveries
from .sites_clients___wired import countsitewiredclients as countsitewiredclients
from .sites_clients___wired import searchsitewiredclients as searchsitewiredclients
from .sites_wlans import listsitewlans as listsitewlans
from .sites_wlans import listsitewlanderived as listsitewlanderived
from .sites_wlans import getsitewlan as getsitewlan
from .sites_wxrules import listsitewxrules as listsitewxrules
from .sites_wxrules import listsitewxrulesderived as listsitewxrulesderived
from .sites_wxrules import getsitewxrule as getsitewxrule
from .sites_wxtags import listsitewxtags as listsitewxtags
from .sites_wxtags import getsiteapplicationlist as getsiteapplicationlist
from .sites_wxtags import getsitewxtag as getsitewxtag
