
pyang -f tree --tree-line-length=68 -o ieee802-ethernet-interface-half-duplex.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-interface-half-duplex.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-interface.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-interface.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-link-oam.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-link-oam.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-lldp.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-lldp.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-mac-merge.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-mac-merge.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-pon.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-pon.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-pse.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana ieee802-ethernet-pse.yang

pyang -f tree --tree-line-length=68 -o ieee802-ethernet-all.tree -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/ieee/published/802.3 -p ~/yang/standard/iana *.yang
