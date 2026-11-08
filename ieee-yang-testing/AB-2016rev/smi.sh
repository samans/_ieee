export SMIPATH=/home/samans/rwsl/gits/libsmi/mibs/ietf:/home/samans/rwsl/gits/libsmi/mibs/iana:/home/samans/rwsl/gits/_ieee/ieee-mib-testing

smilint -l5 D23p/IEEE8021-LLDP-V2-TC-MIB-202609250000Z.mib >& IEEE8021-LLDP-V2-TC-MIB-202603270000Z.out
smilint -l5 D23p/IEEE8021-LLDP-V2-MIB-202609250000Z.mib >& IEEE8021-LLDP-V2-MIB-202603270000Z.out
