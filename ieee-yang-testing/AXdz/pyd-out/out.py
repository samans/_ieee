from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel
from typing_extensions import Annotated


class LinkNumbersLeafList(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    root: Annotated[int, Field(ge=0, le=65535)]
    """
    List of zero or more Link Numbers that can
    potentially be selected for distribution of frames
    with this CID.
    """


class ServiceIdsLeafList(RootModel[int]):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    root: Annotated[int, Field(ge=0, le=4294967295)]
    """
    List of zero or more SIDs that map to the CID.
    """


class EnumerationEnum(Enum):
    force_true = 'force-true'
    force_false = 'force-false'
    auto = 'auto'


class AggSystemListEntry(BaseModel):
    """
    List of aggregation systems.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    name: Annotated[str, Field(alias='ieee802-dot1ax-linkagg:name')]
    """
    Name for the aggregation system.
    """
    actor_system: Annotated[
        Optional[str],
        Field(
            alias='ieee802-dot1ax-linkagg:actor-system',
            pattern='^(?=^[0-9a-fA-F]{2}(-[0-9a-fA-F]{2}){5}$).*$',
        ),
    ] = None
    """
    The part of the System Identifier that is a globally
    unique MAC address.  This leaf provides the ability to
    administratively override the initial value provided
    by the system.
    """
    actor_system_priority: Annotated[
        Optional[int],
        Field(alias='ieee802-dot1ax-linkagg:actor-system-priority', ge=0, le=65535),
    ] = 32768
    """
    The part of the System Identifier that is the
    priority of the system.
    """


class CidListListEntry(BaseModel):
    """
    Data structure to map service identifiers to
    conversation identifiers.  Each entry consists of a
    Conversation ID (CID) and a list of zero or more
    Service Identifiers (SIDs) that map to it. An empty
    list of SIDs means there are no SIDs that map to this
    CID, and results in the same behavior as not having an
    entry for this CID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    cid: Annotated[int, Field(alias='ieee802-dot1ax-linkagg:cid', ge=0, le=4095)]
    """
    Port Conversation Identifier
    """
    service_ids: Annotated[
        Optional[List[ServiceIdsLeafList]],
        Field(alias='ieee802-dot1ax-linkagg:service-ids'),
    ] = []
    """
    List of zero or more SIDs that map to the CID.
    """


class CidListListEntry2(BaseModel):
    """
    Data structure to map a Conversation Identifier
    (CID) to a Link Number. Each entry consists of a CID
    and a list of link numbers that can potentially be
    selected for that CID. An empty list of link-numbers
    means that no links are selected for the CID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    cid: Annotated[int, Field(alias='ieee802-dot1ax-linkagg:cid', ge=0, le=4095)]
    """
    Port Conversation Identifier
    """
    link_numbers: Annotated[
        Optional[List[LinkNumbersLeafList]],
        Field(alias='ieee802-dot1ax-linkagg:link-numbers'),
    ] = []
    """
    List of zero or more Link Numbers that can
    potentially be selected for distribution of frames
    with this CID.
    """


class PatternCase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    pattern: Annotated[Optional[str], Field(alias='ieee802-dot1ax-linkagg:pattern')] = (
        None
    )
    """
    Use a predefined pattern to fill the map.
    """


class PatternCase2(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    pattern: Annotated[Optional[str], Field(alias='ieee802-dot1ax-linkagg:pattern')] = (
        None
    )
    """
    Use a predefined pattern to fill the map.
    """


class CidListCase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    cid_list: Annotated[
        Optional[List[CidListListEntry]], Field(alias='ieee802-dot1ax-linkagg:cid-list')
    ] = None


class CidListCase2(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    cid_list: Annotated[
        Optional[List[CidListListEntry2]],
        Field(alias='ieee802-dot1ax-linkagg:cid-list'),
    ] = None


class AdminConvLinkMapContainer(BaseModel):
    """
    Data structure to map a Conversation Identifier
    (CID) to a Link Number. Each entry consists of a CID
    and a list of link numbers that can potentially be
    selected for that CID. An empty list of link-numbers
    means that no links are selected for the CID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    method: Annotated[
        Optional[Union[PatternCase2, CidListCase2]],
        Field(alias='ieee802-dot1ax-linkagg:method'),
    ] = None


class AdminConvServiceMapContainer(BaseModel):
    """
    Data structure to map service identifiers to
    conversation identifiers.  Each entry consists of a
    Conversation ID (CID) and a list of zero or more
    Service Identifiers (SIDs) that map to it. An empty
    list of SIDs means there are no SIDs that map to this
    CID, and results in the same behavior as not having an
    entry for this CID.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    method: Annotated[
        Optional[Union[PatternCase, CidListCase]],
        Field(alias='ieee802-dot1ax-linkagg:method'),
    ] = None


class CscdContainer(BaseModel):
    """
    Contains CSCD parameters that need to be consistent for
    all aggregation ports and aggregators in the key group.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    admin_conv_service_map: Annotated[
        Optional[AdminConvServiceMapContainer],
        Field(alias='ieee802-dot1ax-linkagg:admin-conv-service-map'),
    ] = None
    admin_conv_service_digest: Annotated[
        Optional[bytes],
        Field(
            alias='ieee802-dot1ax-linkagg:admin-conv-service-digest',
            max_length=18446744073709551615,
        ),
    ] = None
    """
    The MD5 Digest of the admin-conv-service-map. The
    value is NULL (AAAAAAAAAAAAAAAAAAAAAA== in base64) when
    the distribution algorithm specified
    specified by agg-port-algorithm does not use the
    admin-conv-service-map.
    """
    admin_conv_link_map: Annotated[
        Optional[AdminConvLinkMapContainer],
        Field(alias='ieee802-dot1ax-linkagg:admin-conv-link-map'),
    ] = None
    admin_conv_link_digest: Annotated[
        Optional[bytes],
        Field(
            alias='ieee802-dot1ax-linkagg:admin-conv-link-digest',
            max_length=18446744073709551615,
        ),
    ] = None
    """
    The MD5 Digest of the admin-conv-link-map. The value
    value is NULL (AAAAAAAAAAAAAAAAAAAAAA== in base64) when
    the distribution algorithm specified
    agg-port-algorithm does not use the
    admin-conv-link-map.
    """
    admin_discard_wrong_conv: Annotated[
        Optional[EnumerationEnum],
        Field(alias='ieee802-dot1ax-linkagg:admin-discard-wrong-conv'),
    ] = 'force-false'
    """
    Indicates whether an Aggregator discards a
    frame that is collected from an Aggregation Port
    that is different from the Aggregation Port to which
    the Aggregator would distribute a frame with the
    same Port Conversation ID.
    """


class KeyGroupListEntry(BaseModel):
    """
    List of key groups.  A key group is the set of aggregators
    and aggregation ports that share the same system priority,
    system identifier, and aggregation key, and therefore can
    potentially form a Link Aggregation Group.  Each entry in
    the key group list contains the parameters common to all
    aggregation ports and/or aggregators in the key group.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    name: Annotated[str, Field(alias='ieee802-dot1ax-linkagg:name')]
    """
    Name for the key group.
    """
    actor_admin_key: Annotated[
        int, Field(alias='ieee802-dot1ax-linkagg:actor-admin-key', ge=1, le=65535)
    ]
    """
    The administrative value of the key used by the
    Aggregators and Aggregation Ports in this key-group.
    """
    agg_system_name: Annotated[
        str, Field(alias='ieee802-dot1ax-linkagg:agg-system-name')
    ]
    """
    Specifies the aggregation system for this key
    group.
    """
    actor_protocol_da: Annotated[
        Optional[str],
        Field(
            alias='ieee802-dot1ax-linkagg:actor-protocol-da',
            pattern='^(?=^[0-9a-fA-F]{2}(-[0-9a-fA-F]{2}){5}$).*$',
        ),
    ] = '01-80-c2-00-00-02'
    """
    A 6-octet read-write MAC Address value specifying the DA
    to be used when sending Link Aggregation Control and
    Marker PDUs.  Valid addresses are the Nearest Customer
    Bridge, Slow_Protocols_Multicast, and Nearest non-TPMR
    Bridge group addresses.  The default value
    is the Slow_Protocols_Multicast address.
    """
    collector_max_delay: Annotated[
        Optional[int],
        Field(alias='ieee802-dot1ax-linkagg:collector-max-delay', ge=0, le=65535),
    ] = None
    """
    Specifies the maximum delay, in tens of microseconds,
    between receiving a frame from an Aggregator Port, and
    either delivering the frame to the Aggregator Client or
    discarding the frame. A value of zero means the delay
    is less than the minimum increment (< 10us).
    This leaf provides the ability to administratively
    override the initial value provided by the system.
    """
    actor_admin_state: Annotated[
        Optional[str],
        Field(
            alias='ieee802-dot1ax-linkagg:actor-admin-state',
            pattern='^(lacp-activity|lacp-timeout|aggregation|synchronization|collecting|distributing|defaulted|expired|\\s)*$',
        ),
    ] = ['lacp-activity', 'lacp-timeout', 'aggregation']
    """
    Provides administrative control over the values of the
    LACP_Activity, LACP_Timeout, and Aggregation state.
    """
    partner_admin_system: Annotated[
        Optional[str],
        Field(
            alias='ieee802-dot1ax-linkagg:partner-admin-system',
            pattern='^(?=^[0-9a-fA-F]{2}(-[0-9a-fA-F]{2}){5}$).*$',
        ),
    ] = '00-00-00-00-00-00'
    """
    The administrative value of the MAC address portion of
    the Partner's System Identifier.
    The assigned value is used, along with the value of
    port-partner-admin-system, partner-admin-key,
    partner-admin-port, and partner-admin-port-priority,
    to achieve administratively configured Link
    Aggregation Groups with a partner that does not run
    LACP.
    """
    partner_admin_system_priority: Annotated[
        Optional[int],
        Field(
            alias='ieee802-dot1ax-linkagg:partner-admin-system-priority', ge=0, le=65535
        ),
    ] = 0
    """
    The administrative value of priority portion of the
    the Partner's System Identifier. The assigned
    value is used, along with the value of
    port-partner-admin-system, partner-admin-key,
    partner-admin-port, and partner-admin-port-priority,
    to achieve administratively configured Link
    Aggregation Groups with a partner that does not run
    LACP.
    """
    port_algorithm: Annotated[
        Optional[str], Field(alias='ieee802-dot1ax-linkagg:port-algorithm')
    ] = 'unspecified'
    """
    Identifies the algorithm used by the Aggregator to
    assign frames to a Port Conversation ID.  Default is
    the value for an unspecified distribution algorithm.
    When the identity description specifies a 4 octet value,
    this value will be used for cscd purposes, and included
    in LACPDUs. Otherwise this leaf is used purely for
    local selection of a distribution algorithm, and the
    unspecified distribution algorithm is used for cscd
    purposes.
    """
    lags: Annotated[Optional[List[str]], Field(alias='ieee802-dot1ax-linkagg:lags')] = (
        []
    )
    """
    A list of the if:name of aggregators assigned to this
    key group.
    """
    aggports: Annotated[
        Optional[List[str]], Field(alias='ieee802-dot1ax-linkagg:aggports')
    ] = []
    """
    A list of the if:name of aggregation ports assigned to
    this key group.
    """
    cscd: Annotated[
        Optional[CscdContainer], Field(alias='ieee802-dot1ax-linkagg:cscd')
    ] = None


class LinkaggContainer(BaseModel):
    """
    Link Aaggregation System specific configuration nodes.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    agg_system: Annotated[
        Optional[List[AggSystemListEntry]],
        Field(alias='ieee802-dot1ax-linkagg:agg-system'),
    ] = None
    key_group: Annotated[
        Optional[List[KeyGroupListEntry]],
        Field(alias='ieee802-dot1ax-linkagg:key-group'),
    ] = None


class Model(BaseModel):
    """
    Initialize an instance of this class and serialize it to JSON; this results in a RESTCONF payload.

    ## Tips
    Initialization:
    - all values have to be set via keyword arguments
    - if a class contains only a `root` field, it can be initialized as follows:
        - `member=MyNode(root=<value>)`
        - `member=<value>`

    Serialziation:
    - `exclude_defaults=True` omits fields set to their default value (recommended)
    - `by_alias=True` ensures qualified names are used (necessary)
    """

    model_config = ConfigDict(
        populate_by_name=True,
        regex_engine="python-re",
    )
    linkagg: Annotated[
        Optional[LinkaggContainer], Field(alias='ieee802-dot1ax-linkagg:linkagg')
    ] = None


if __name__ == "__main__":
    model = Model(
        # <Initialize model here>
    )

    restconf_payload = model.model_dump_json(
        exclude_defaults=True, by_alias=True, indent=2
    )

    print(f"Generated output: {restconf_payload}")

    # Send config to network device:
    # from pydantify.utility import restconf_patch_request
    # restconf_patch_request(url='...', user_pw_auth=('usr', 'pw'), data=restconf_payload)