#!/usr/bin/env bash
# regression-test.sh - validate every example data file with yanglint.
#
# Loads ieee802-dot1q-bridge.yang and its dependencies into a yanglint context,
# then validates each *.json and *.xml example file in this directory as
# configuration data (-t config). A summary is printed and the script exits
# non-zero if any file fails.
#
# Usage:
#   ./regression-test.sh                 # validate all *.json and *.xml here
#   ./regression-test.sh file1 file2 ... # validate only the given files
#   YANG_HOME=/path/to/yang ./regression-test.sh
#
# Data type: the example files carry configuration only (they omit
# operational-state mandatory nodes such as oper-status/if-index), so they are
# validated with "-t config".

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
source "./common.sh"

# Collect target data files: explicit args, or every *.json/*.xml here.
declare -a FILES
if [[ $# -gt 0 ]]; then
  FILES=("$@")
else
  shopt -s nullglob
  FILES=( *.json *.xml )
  shopt -u nullglob
fi

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "No data files (*.json / *.xml) found to validate." >&2
  exit 1
fi

echo "========================================================================"
echo "Regression test : ${#FILES[@]} data file(s)"
echo "Module          : $MODULE"
echo "YANG home       : $YANG_HOME"
echo "Data type       : config"
echo "========================================================================"

pass=0
fail=0
declare -a FAILED

for f in "${FILES[@]}"; do
  printf '%-36s ' "$f"
  if [[ ! -f "$f" ]]; then
    echo "MISSING"
    fail=$((fail + 1))
    FAILED+=("$f (missing)")
    continue
  fi
  if err="$(yanglint "${SEARCH_ARGS[@]}" -t config "${DEP_MODULES[@]}" "$f" 2>&1)"; then
    echo "PASS"
    pass=$((pass + 1))
  else
    echo "FAIL"
    # Indent yanglint's diagnostics under the failing file name.
    printf '%s\n' "$err" | sed 's/^/    /'
    fail=$((fail + 1))
    FAILED+=("$f")
  fi
done

echo "------------------------------------------------------------------------"
echo "Passed: $pass   Failed: $fail"
if [[ $fail -gt 0 ]]; then
  echo "Failing files:"
  printf '  - %s\n' "${FAILED[@]}"
  exit 1
fi
echo "RESULT: all data files validated successfully"
