yanglint -i -i \
   -t data \
   -f json \
   ./D3.1/i01.xml \
   -o ./D3.1/i01.json \
   -F ieee802-dot1as-ftt:* \
   -F ieee1588-ptp-tt:* \
   -p ~/gits/yang/standard/ietf/RFC \
   -p ~/gits/yang/standard/ieee/published/802 \
   -p ~/gits/yang/standard/ieee/published/802.1 \
   -p ~/gits/yang/standard/ieee/published/1588 \
   -p ~/gits/yang/standard/iana \
   ~/gits/yang/standard/ieee/published/1588/ieee1588-ptp-tt.yang \
   ./D3.1/ieee802-dot1as-ftt.yang
