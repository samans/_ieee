#! /bin/sh
echo Generating 60802 Digital Datasheet Skeleton file
pyang --format=sample-xml-skeleton --sample-xml-skeleton-doctype=data --sample-xml-skeleton-defaults -o dds-skeleton.xml ieee802-dot1ab-lldp.yang ieee1588-ptp.yang ietf-system-capabilities.yang ietf-yang-library.yang ietf-notification-capabilities.yang ietf-netconf-monitoring.yang ietf-hardware.yang ietf-interfaces.yang ieee802-dot1q-bridge.yang iecieee60802-ethernet-interface.yang ietf-subscribed-notifications.yang iecieee60802-subscribed-notifications.yang iecieee60802-bridge.yang
