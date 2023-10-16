module iecieee60802-factory-default {
  yang-version 1.1;
  namespace "urn:ieee:std:60802:yang:iecieee60802-factory-default";
  prefix ia-fd;

  import ietf-datastores {
    prefix ds;
    reference
      "RFC 8342: Network Management Datastore Architecture
       (NMDA)";
  }
  import ietf-netconf-acm {
    prefix nacm;
    reference
      "RFC 8341: Network Configuration Access Control Model";
  }

  organization
    "IEEE 802.1 Working Group";
  contact
    "WG-URL: http://ieee802.org/1/
     WG-EMail: stds-802-1-l@ieee.org

     Contact: IEEE 802.1 Working Group Chair
              Postal: C/O IEEE 802.1 Working Group
              IEEE Standards Association
              445 Hoes Lane
              Piscataway, NJ 08854
              USA

     E-mail: stds-802-1-chairs@ieee.org";
  description
    "Reset to factory defaults functionality for IEC/IEEE 60802 IA-Stations as specified in IEC/IEEE 60802 IEC/IEEE 60802.

     Copyright (C) IEC/IEEE (2023).
     This version of this YANG module is part of IEC/IEEE Std 60802;
     see the standard itself for full legal notices.";

  revision 2023-05-17 {
    description
      "Initial version.";
    reference
      "IEC/IEEE 60802 - YANG Data Model";
  }

  feature ia-factory-default-datastore {
    description
      "Indicates that the factory default configuration is
       available as a datastore.";
  }

  rpc ia-factory-reset {
    nacm:default-deny-all;
    description
      "The server resets all datastores to their factory
       default contents and any nonvolatile storage back to
       factory condition, deleting all dynamically
       generated files, including those containing keys,
       certificates, logs, and other temporary files.

       Depending on the factory default configuration, after
       being reset, the device may become unreachable on the
       network.

       In contrast to the original factory-reset RPC in RFC 8808,
       this RPC puts the device into a state where a subsequent
       configuration by a CNC component results in a funcioning
       60802 IA-station";
  }

  identity ia-factory-default {
    if-feature "ia-factory-default-datastore";
    base ds:datastore;
    description
      "This read-only datastore contains the factory default
       configuration for the device that will be used to replace
       the contents of the read-write conventional configuration
       datastores during a 'ia-factory-reset' RPC operation.";
  }
}
