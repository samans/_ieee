#!/usr/bin/env bash
# check-module.sh - lint the local ieee802-dot1q-bridge.yang module.
#
# Runs both pyang (with --strict) and yanglint against the module, resolving
# all imports from the published YANG tree. Use this to sanity-check the module
# itself before validating example data with regression-test.sh.
#
# Usage:
#   ./check-module.sh
#   YANG_HOME=/path/to/yang ./check-module.sh
#
# Exit status is non-zero if either tool reports an error.

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
source "./common.sh"

rc=0

echo "========================================================================"
echo "Module under test : $MODULE"
echo "YANG home         : $YANG_HOME"
echo "========================================================================"

# --- pyang -----------------------------------------------------------------
echo
echo ">>> pyang --strict"
if pyang --strict "${SEARCH_ARGS[@]}" "$MODULE"; then
  echo "    pyang: OK"
else
  echo "    pyang: FAILED" >&2
  rc=1
fi

# --- yanglint --------------------------------------------------------------
# Load the module together with its implemented dependencies so identity and
# default-value resolution matches how the data files are validated.
echo
echo ">>> yanglint (schema parse)"
if yanglint "${SEARCH_ARGS[@]}" "${DEP_MODULES[@]}"; then
  echo "    yanglint: OK"
else
  echo "    yanglint: FAILED" >&2
  rc=1
fi

echo
if [[ $rc -eq 0 ]]; then
  echo "RESULT: module checks PASSED"
else
  echo "RESULT: module checks FAILED" >&2
fi
exit $rc
