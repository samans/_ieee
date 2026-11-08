# yc_ieee_metadata_sync.py

Checks that every IEEE YANG module in the `standard/ieee/published` directory of the
[YangModels/yang](https://github.com/YangModels/yang) repository has up-to-date
metadata in the [YANG Catalog](https://www.yangcatalog.org). Optionally pushes
corrected metadata, derived from the `.yang` files themselves, using the procedure
described at <https://www.yangcatalog.org/contribute.html>.

## What it does

1. Recursively scans `standard/ieee/published/**/*.yang` in a local clone.
2. Parses each module/submodule and extracts:
   - name, latest `revision`, `namespace`, `prefix`, `yang-version`
   - author e-mail from the `contact` statement (WG mailing list preferred)
3. Builds the expected module-metadata entry:

   | Field | Value |
   |---|---|
   | `organization` | `ieee` |
   | `maturity-level` | `ratified` |
   | `module-classification` | `network-element` |
   | `source-file.owner` / `repository` | `YangModels` / `yang` |
   | `source-file.path` | path of the file relative to the repo root |
   | `source-file.branch` | `main` |
   | `author-email` | from `contact` |

4. Looks up each `name@revision` in the catalog and reports:
   - **OK** – catalog matches the module
   - **STALE** – entry exists but one or more fields differ (differences listed)
   - **MISSING** – no catalog entry for that name/revision/organization
   - **ERROR / PARSE-ERR / NO-REV / DUP** – lookup or parsing problems, skipped files
5. With `--apply`, sends `PUT https://www.yangcatalog.org/api/modules` for stale and
   missing modules (in batches), then polls `GET /api/job/{job-id}` until each job
   reports `Finished` or `Failed`.

## Prerequisites

- Python 3.8 or later
- `requests` package
- A local clone (or fork) of YangModels/yang
- For `--apply` only: a YANG Catalog API account approved for the IEEE SDO paths
  (request one at <https://www.yangcatalog.org/create.html> and wait for admin approval)

## Setup (Linux / WSL)

```bash
# 1. Get the YANG repository (skip if you already have a fork)
git clone https://github.com/YangModels/yang.git ~/src/yang
cd ~/src/yang && git pull            # make sure it is current

# 2. Create a virtual environment and install requests
python3 -m venv ~/venvs/yc
source ~/venvs/yc/bin/activate
pip install requests

# 3. Make the script executable
chmod +x yc_ieee_metadata_sync.py
```

## Running

### 1. Check only (default, makes no changes)

```bash
./yc_ieee_metadata_sync.py ~/src/yang
```

Save the results and the payload that would be sent, for review:

```bash
./yc_ieee_metadata_sync.py ~/src/yang \
    --report-out report.json \
    --payload-out payload.json
```

The exit code is `0` if everything is up to date and `1` if updates are needed,
so the check can be used in CI.

### 2. Build the payload without contacting the catalog

```bash
./yc_ieee_metadata_sync.py ~/src/yang --offline --payload-out payload.json
```

### 3. Push updates

Set credentials as environment variables (they are not accepted on the command line):

```bash
export YC_USER='your-yc-username'
export YC_PASSWORD='your-yc-password'

./yc_ieee_metadata_sync.py ~/src/yang --apply
```

Push metadata for **all** modules, not only stale or missing ones:

```bash
./yc_ieee_metadata_sync.py ~/src/yang --apply --force
```

### 4. Verify

Re-run the check without `--apply`. Catalog processing can take a while after a
job finishes, so allow some time before verifying.

```bash
./yc_ieee_metadata_sync.py ~/src/yang
```

## Options

| Option | Default | Description |
|---|---|---|
| `repo` (positional) | — | Path to the local YangModels/yang clone |
| `--published-dir` | `standard/ieee/published` | Directory to scan, relative to `repo` |
| `--organization` | `ieee` | Organization value |
| `--maturity-level` | `ratified` | Maturity level for published modules |
| `--classification` | `network-element` | `module-classification` value |
| `--owner` | `YangModels` | `source-file.owner` |
| `--repository` | `yang` | `source-file.repository` |
| `--branch` | `main` | `source-file.branch` |
| `--overrides FILE` | — | JSON file with per-module extra fields |
| `--payload-out FILE` | — | Write the PUT payload JSON |
| `--report-out FILE` | — | Write the check report JSON |
| `--apply` | off | Send updates to YANG Catalog |
| `--force` | off | With `--apply`, push every module |
| `--batch-size N` | `20` | Modules per PUT request |
| `--poll SECONDS` | `15` | Job status poll interval |
| `--job-timeout SECONDS` | `1800` | Give up waiting on a job after this time |
| `--offline` | off | Skip catalog lookups; just build the payload |

## Per-module overrides

Use an overrides file to add fields that cannot be derived from the module, such
as `document-name` or `reference`:

```json
{
  "ieee802-ethernet-interface": {
    "document-name": "IEEE Std 802.3.2-2025",
    "reference": "https://standards.ieee.org/"
  },
  "ieee802-dot1q-bridge": {
    "document-name": "IEEE Std 802.1Q"
  }
}
```

```bash
./yc_ieee_metadata_sync.py ~/src/yang --overrides overrides.json
```

Fields in the overrides file are also compared during the check.

## Example output

```
Scanning 142 .yang files under /home/user/src/yang/standard/ieee/published

[OK       ] ieee802-types@2020-06-04  (standard/ieee/published/802/ieee802-types.yang)
[STALE    ] ieee802-ethernet-interface@2025-09-10  (standard/ieee/published/802.3/...)
              - maturity-level: catalog='initial' expected='ratified'
              - author-email: catalog=None expected='STDS-802-3-YANG@LISTSERV.IEEE.ORG'
[MISSING  ] ieee802-dot1q-xyz@2026-01-15  (standard/ieee/published/802.1/...)

Summary: missing=1, ok=1, stale=1
Modules needing metadata update: 2
```

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Not a directory` | Wrong `repo` path, or use `--published-dir` |
| `Set YC_USER and YC_PASSWORD` | Export both variables before `--apply` |
| PUT fails with 401 | Wrong credentials, or the account is not yet approved |
| PUT fails with 403 / job `Failed` | Account lacks rights for the IEEE paths; ask a YANG Catalog admin |
| Every module shows `ERROR` | Catalog search endpoint is unreachable or has changed; check the [API docs](https://www.yangcatalog.org/doc/) |
| `DUP` lines | The same `name@revision` exists in more than one directory; only the first file is used |
| `NO-REV` | The module has no `revision` statement and is skipped |

## Notes

- The lookup uses `GET /api/search/modules/{name},{revision},{organization}`. If
  YANG Catalog changes this endpoint, update `get_catalog_entry()`.
- Namespace, prefix and yang-version are compared but not sent. The catalog
  derives them from the source file when it processes the PUT.
