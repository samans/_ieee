
pyang --lint --ieee -f tree -o full.tree -p . ieee802-dot1ab-lldp.yang ieee802-dot1ab-types.yang ieee802-dot1dc-ats-if.yang ieee802-dot1dc-psfp-sys.yang ieee802-dot1q-ats-bridge.yang ieee802-dot1q-ats.yang ieee802-dot1q-bridge.yang ieee802-dot1q-congestion-isolation-bridge.yang ieee802-dot1q-congestion-isolation.yang ieee802-dot1q-lldp-ci-tlv.yang ieee802-dot1q-psfp-bridge.yang ieee802-dot1q-psfp.yang ieee802-dot1q-stream-filters-gates-bridge.yang ieee802-dot1q-stream-filters-gates.yang ieee802-dot1q-types.yang ieee802-types.yang

pyang --lint --ieee -f tree -o full-ats-component-only.tree -p . ieee802-dot1q-ats-bridge.yang ieee802-dot1q-ats.yang ieee802-dot1q-bridge.yang ieee802-dot1q-stream-filters-gates-bridge.yang ieee802-dot1q-stream-filters-gates.yang 
