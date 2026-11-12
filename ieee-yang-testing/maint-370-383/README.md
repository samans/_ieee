# IEEE 802.1Q Bridge YANG Testing — maint-370-383

Test harness for an **experimental revision of `ieee802-dot1q-bridge.yang`**
(revision `2026-11-12`) that introduces:

- `inhibit-bridge-port` — inhibits augmenting an interface with the
  `bridge-port` container (IEEE 802.1 **maintenance item 0370**), and
- an optional (non-mandatory) bridge MAC address (maintenance item **0383**).

Two scripts lint the module and run the example data files through `yanglint`
for regression testing.

## Contents

| File | Purpose |
|------|---------|
| `ieee802-dot1q-bridge.yang` | The module under test (local, newer revision). |
| `check-module.sh` | Lints the module with `pyang --strict` and `yanglint`. |
| `regression-test.sh` | Validates all example `*.json` / `*.xml` data files with `yanglint`. |
| `common.sh` | Shared config sourced by both scripts (not run directly). |
| `ex-bridge-*.json` / `ex-bridge-*.xml` | Example configuration data (4 JSON + 4 XML). |
| `yangsters-haddock-systems-with-LAG-1025-v2.pdf` | Reference material for the LAG examples. |

## Prerequisites

- **pyang** (tested with 2.7.1) — `pip install pyang`
- **yanglint** from libyang (tested with 5.8.6)
- A checkout of the published YANG tree, default `~/gits/yang`
  (the yangcatalog/yang layout with `standard/`, `vendor/`, `experimental/`).

## Usage

```bash
# Lint the module itself
./check-module.sh

# Validate every *.json and *.xml in this directory
./regression-test.sh

# Validate only specific files
./regression-test.sh ex-bridge-lag-var.json ex-bridge-lag-var.xml

# Point at a different published-YANG checkout
YANG_HOME=/path/to/yang ./check-module.sh
YANG_HOME=/path/to/yang ./regression-test.sh
```

Each script exits non-zero if anything fails, so they are safe to use in CI.

## How it works (and why the setup is non-obvious)

### Published YANG home is overridable
Both scripts default to `~/gits/yang` and honor the `YANG_HOME` environment
variable.

### Import search paths
`ieee802-dot1q-bridge.yang` imports resolve from four directories under
`$YANG_HOME/standard`, passed to pyang/yanglint as `-p` search paths:

| Module | Search dir |
|--------|-----------|
| `ieee802-types` | `ieee/published/802` |
| `ieee802-dot1q-types`, `ieee802-dot1ax-linkagg`, `ieee802-dot1ax-types` | `ieee/published/802.1` |
| `ietf-yang-types`, `ietf-interfaces` | `ietf/RFC` |
| `iana-if-type` | `iana` |

### The data files need more modules than the bridge module imports
The example data references nodes from modules the bridge module does **not**
import directly. All of these must be loaded into the `yanglint` context, or
identityref values such as `iana-if-type:ethernetCsmacd` fail to resolve:

- `ieee802-dot1ax-linkagg` (and its `ieee802-dot1ax-types`)
- `ietf-interfaces`
- `iana-if-type`

### Module load order matters
`ieee802-dot1ax-types` must be loaded **before** `ieee802-dot1ax-linkagg`.
linkagg uses an identity from dot1ax-types as a **default value**
(`port-algorithm` defaults to `ax:unspecified`), which must resolve at
schema-load time — so the providing module has to be *implemented* first.
The ordered dependency list in `common.sh` encodes this.

### Data validated as `-t config`
The example files carry **configuration only**; they omit operational-state
mandatory nodes (`oper-status`, `if-index`, `statistics`, `admin-status`,
`type` on auto-added interfaces, etc.). Validating them as a full datastore
would fail spuriously, so `yanglint -t config` is used.

### iana-if-type revision is auto-selected
`iana-if-type` is revision-stamped in the published tree
(`iana-if-type@<date>.yang`). `common.sh` picks the newest one present rather
than hardcoding a date.

## Expected result

With the current module and data files:

- `check-module.sh` → `pyang: OK`, `yanglint: OK`
- `regression-test.sh` → all 8 data files (4 JSON + 4 XML) PASS

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `published YANG tree not found at: .../standard` | Set `YANG_HOME` to your `yang` checkout root. |
| `No module named "ieee802-dot1ax-linkagg"` | A dependency module isn't being loaded into the context — check `DEP_MODULES` in `common.sh`. |
| `Invalid identityref "iana-if-type:..." ... unable to map prefix` | `iana-if-type` not implemented in the context — ensure it's in `DEP_MODULES`. |
| `identity found in non-implemented module "ieee802-dot1ax-types"` | Load order: dot1ax-types must come before dot1ax-linkagg in `DEP_MODULES`. |
| `Mandatory node "oper-status"/"if-index"/... does not exist` | Data is being validated as a datastore; use `-t config` (already set in `regression-test.sh`). |
