#!/usr/bin/env bash
# common.sh - shared configuration for the IEEE 802.1Q bridge YANG test scripts.
#
# Sourced by check-module.sh and regression-test.sh. Not meant to be run directly.
#
# It resolves:
#   * the published-YANG home directory (overridable with $YANG_HOME),
#   * the yanglint/pyang search paths for all imports,
#   * the ordered list of dependency modules that must be loaded into the
#     yanglint context so the example data files validate.
#
# The module under test (ieee802-dot1q-bridge.yang) lives alongside these
# scripts; the dependencies are pulled from the published tree.

set -euo pipefail

# Directory containing this script (and the module under test / data files).
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Published YANG home. Override with:  YANG_HOME=/path/to/yang ./check-module.sh
YANG_HOME="${YANG_HOME:-$HOME/gits/yang}"
STD="$YANG_HOME/standard"

# The module under test (the newer, local revision).
MODULE="$HERE/ieee802-dot1q-bridge.yang"

# --- sanity checks ---------------------------------------------------------
if [[ ! -d "$STD" ]]; then
  echo "ERROR: published YANG tree not found at: $STD" >&2
  echo "       Set YANG_HOME to the root of your 'yang' checkout." >&2
  exit 1
fi
if [[ ! -f "$MODULE" ]]; then
  echo "ERROR: module under test not found: $MODULE" >&2
  exit 1
fi

# --- search paths ----------------------------------------------------------
# These directories hold every module imported (directly or transitively) by
# ieee802-dot1q-bridge and by the example data files:
#   ieee802-types            -> ieee/published/802
#   ieee802-dot1q-types,
#   ieee802-dot1ax-linkagg,
#   ieee802-dot1ax-types     -> ieee/published/802.1
#   ietf-yang-types,
#   ietf-interfaces          -> ietf/RFC
#   iana-if-type             -> iana
SEARCH_DIRS=(
  "$STD/ieee/published/802"
  "$STD/ieee/published/802.1"
  "$STD/ietf/RFC"
  "$STD/iana"
)

# Build repeated "-p <dir>" arguments for yanglint / pyang.
SEARCH_ARGS=()
for d in "${SEARCH_DIRS[@]}"; do
  if [[ ! -d "$d" ]]; then
    echo "ERROR: expected search directory is missing: $d" >&2
    exit 1
  fi
  SEARCH_ARGS+=(-p "$d")
done

# iana-if-type is revision-stamped in the published tree; pick the newest one
# that is present rather than hardcoding a date.
IANA_IF_TYPE="$(ls -1 "$STD"/iana/iana-if-type@*.yang 2>/dev/null | sort | tail -n1 || true)"
if [[ -z "$IANA_IF_TYPE" ]]; then
  echo "ERROR: no iana-if-type@<rev>.yang found under $STD/iana" >&2
  exit 1
fi

# --- dependency modules, in load order -------------------------------------
# Order matters for yanglint: a module that supplies identities used in a
# *default* value of another module (here ieee802-dot1ax-types -> linkagg)
# must be implemented first, so it is listed before the module that uses it.
# The module under test is listed last.
DEP_MODULES=(
  "$IANA_IF_TYPE"
  "$STD/ietf/RFC/ietf-interfaces.yang"
  "$STD/ieee/published/802.1/ieee802-dot1ax-types.yang"
  "$STD/ieee/published/802.1/ieee802-dot1ax-linkagg.yang"
  "$MODULE"
)

for m in "${DEP_MODULES[@]}"; do
  if [[ ! -f "$m" ]]; then
    echo "ERROR: required module not found: $m" >&2
    exit 1
  fi
done
