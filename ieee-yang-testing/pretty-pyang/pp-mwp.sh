
pyang -o ieee802-dot1as-ptp.yang.txt -f yang --yang-canonical --yang-remove-unused-imports --yang-remove-comments --yang-line-length=68 -p ~/yang/standard/ietf/RFC -p ~/yang/standard/ieee/draft/1588 -p ~/yang/standard/iana ieee802-dot1as-ptp.yang
