#! /bin/sh
echo "generating iecieee60802-ethernet-interface"
pyang iecieee60802-ethernet-interface.yang -f tree --tree-no-expand-uses -o iecieee60802-ethernet-interface.tree
pyang iecieee60802-ethernet-interface.yang -f yang -o iecieee60802-ethernet-interface.pp
echo "generating iecieee60802-bridge"
pyang iecieee60802-bridge.yang -f tree --tree-no-expand-uses -o iecieee60802-bridge.tree
pyang iecieee60802-bridge.yang -f yang -o iecieee60802-bridge.pp
echo "generating iecieee60802-sched-bridge"
pyang iecieee60802-sched-bridge.yang -f tree --tree-no-expand-uses -o iecieee60802-sched-bridge.tree 
pyang iecieee60802-sched-bridge.yang -f yang -o iecieee60802-sched-bridge.pp
echo "generating iecieee60802-factory-default"
pyang iecieee60802-factory-default.yang -f tree --tree-no-expand-uses -o iecieee60802-factory-default.tree
pyang iecieee60802-factory-default.yang -f yang -o iecieee60802-factory-default.pp
echo "generating iecieee60802-tsn-config-uni"
pyang iecieee60802-tsn-config-uni.yang -f tree --tree-no-expand-uses -o iecieee60802-tsn-config-uni.tree
pyang iecieee60802-tsn-config-uni.yang -f yang -o iecieee60802-tsn-config-uni.pp
echo "generating iecieee60802-ia-station"
pyang iecieee60802-ia-station.yang -f tree --tree-no-expand-uses -o iecieee60802-ia-station.tree
pyang iecieee60802-ia-station.yang -f yang -o iecieee60802-ia-station.pp
echo "generating iecieee60802-subscribed-notifications"
pyang iecieee60802-subscribed-notifications.yang -f tree --tree-no-expand-uses -o iecieee60802-subscribed-notifications.tree
pyang iecieee60802-subscribed-notifications.yang -f yang -o iecieee60802-subscribed-notifications.pp

