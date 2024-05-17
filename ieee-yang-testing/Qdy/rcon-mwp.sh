
pyang -f yang -o rstp-yang.out --canonical -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/iana ieee802-dot1q-rstp.yang 
pyang -f yang -o mstp-yang.out --canonical -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/published/802 -p ~/yang/standard/ieee/published/802.1 -p ~/yang/standard/iana ieee802-dot1q-mstp.yang 
