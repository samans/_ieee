# yc_ieee_metadata_sync.py

Checks that every IEEE YANG module in the `standard/ieee/published` directory of the
[YangModels/yang](https://github.com/YangModels/yang) repository has up-to-date
metadata in the [YANG Catalog](https://www.yangcatalog.org), and optionally pushes
corrected metadata using the procedure described at
<https://www.yangcatalog.org/contribute.html>.

The script has two modes:

| Mode | Source of metadata | Typical use |
|---|---|---|
| **Scan** (default) | Derived from the `.yang` files in the repo, compared with the catalog | Find and fix stale or missing entries |
| **Payload** (`--payload-in`) | Taken as-is from a payload JSON file | Push a reviewed or hand-edited payload |

A companion script, `yc_check_credentials.py`, checks your YANG Catalog login
before you push anything.

## Prerequisites

- Python 3.8 or later
- `requests` package
- A local clone (or fork) of YangModels/yang (scan mode only)
- For pushing updates: a YANG Catalog API account approved for the IEEE SDO paths
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

# 3. Make the scripts executable
chmod +x yc_ieee_metadata_sync.py yc_check_credentials.py
```

## Recommended workflow

```bash
# 1. Check your credentials
export YC_USER='your-yc-username'
export YC_PASSWORD='your-yc-password'
./yc_check_credentials.py

# 2. Scan the repo, compare with the catalog, and save the payload
./yc_ieee_metadata_sync.py ~/src/yang --report-out report.json --payload-out payload.json

# 3. Review / edit payload.json (add document-name, fix author-email, remove entries, ...)

# 4. Preview what will be pushed (no changes made)
./yc_ieee_metadata_sync.py --payload-in payload.json

# 5. Push it
./yc_ieee_metadata_sync.py --payload-in payload.json --apply

# 6. Verify (allow time for catalog processing)
./yc_ieee_metadata_sync.py ~/src/yang
```

## Scan mode

### What it does

1. Recursively scans `standard/ieee/published/**/*.yang` in the local clone.
2. Parses each module/submodule and extracts the name, latest `revision`,
   `namespace`, `prefix`, `yang-version` and the author e-mail from `contact`
   (WG mailing list preferred).
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
   - **OK**: catalog matches the module
   - **STALE**: entry exists but one or more fields differ (differences listed)
   - **MISSING**: no catalog entry for that name/revision/organization
   - **ERROR / PARSE-ERR / NO-REV / DUP**: lookup or parsing problems, skipped files
5. With `--apply`, pushes stale and missing modules in batches and waits for each job.

### Commands

```bash
# Check only (no changes)
./yc_ieee_metadata_sync.py ~/src/yang

# Save the report and the payload that would be sent
./yc_ieee_metadata_sync.py ~/src/yang --report-out report.json --payload-out payload.json

# Build a payload for every module without contacting the catalog
./yc_ieee_metadata_sync.py ~/src/yang --offline --payload-out payload.json

# Push stale/missing modules directly
./yc_ieee_metadata_sync.py ~/src/yang --apply

# Push every module, stale or not
./yc_ieee_metadata_sync.py ~/src/yang --apply --force
```

The exit code is `0` when everything is up to date and `1` when updates are needed,
so the check can run in CI.

## Payload mode (`--payload-in`)

Pushes the metadata in a payload file exactly as written. The repo is not scanned
and nothing is regenerated from the `.yang` files, so hand edits are preserved.
No repo path is needed.

```bash
# Preview (dry run)
./yc_ieee_metadata_sync.py --payload-in payload.json

# Push
./yc_ieee_metadata_sync.py --payload-in payload.json --apply
```

### Payload format

```json
{
  "modules": {
    "module": [
      {
        "name": "ieee802-ethernet-interface",
        "revision": "2025-09-10",
        "organization": "ieee",
        "maturity-level": "ratified",
        "module-classification": "network-element",
        "author-email": "STDS-802-3-YANG@LISTSERV.IEEE.ORG",
        "document-name": "IEEE Std 802.3.2-2025",
        "source-file": {
          "owner": "YangModels",
          "repository": "yang",
          "path": "standard/ieee/published/802.3/ieee802-ethernet-interface.yang",
          "branch": "main"
        }
      }
    ]
  }
}
```

### Validation

Before anything is sent, the file is checked. If any check fails, every problem
is listed and nothing is pushed.

- Top-level structure must be `{"modules": {"module": [ ... ]}}`
- Each entry needs `name`, `revision`, `organization`, and
  `source-file.owner`, `source-file.repository`, `source-file.path`
- `revision` must be in `YYYY-MM-DD` format
- No duplicate `name@revision` entries

`--batch-size`, `--max-passes`, `--poll` and `--job-timeout` apply in this mode too.

## Checking credentials

```bash
export YC_USER='your-yc-username'
export YC_PASSWORD='your-yc-password'    # or leave unset to be prompted
./yc_check_credentials.py
```

It sends an authenticated `PUT` with an empty module list, so no data is changed.

| Response | Meaning |
|---|---|
| 401 | Credentials rejected, or account not yet approved |
| 403 | Logged in, but not authorized for this operation |
| 400 or 2xx | Credentials accepted |

A pass confirms the login only. Write access to the IEEE paths is checked when a
real update job runs. To test it, push a single module:
`--payload-in one-module.json --apply --batch-size 1`.

## Options

| Option | Default | Description |
|---|---|---|
| `repo` (positional) | — | Path to the YangModels/yang clone (not needed with `--payload-in`) |
| `--payload-in FILE` | — | Push metadata from this payload file instead of scanning |
| `--published-dir` | `standard/ieee/published` | Directory to scan, relative to `repo` |
| `--organization` | `ieee` | Organization value |
| `--maturity-level` | `ratified` | Maturity level for published modules |
| `--classification` | `network-element` | `module-classification` value |
| `--owner` | `YangModels` | `source-file.owner` |
| `--repository` | `yang` | `source-file.repository` |
| `--branch` | `main` | `source-file.branch` |
| `--overrides FILE` | — | JSON file with per-module extra fields (scan mode) |
| `--payload-out FILE` | — | Write the PUT payload JSON (scan mode) |
| `--report-out FILE` | — | Write the check report JSON (scan mode) |
| `--apply` | off | Send updates to YANG Catalog |
| `--force` | off | With `--apply` in scan mode, push every module |
| `--batch-size N` | `20` | Modules per PUT request |
| `--max-passes N` | `3` | With `--apply`, re-push modules still stale after ingest, up to this many passes (a new module lands as `maturity-level: not-applicable` on first ingest) |
| `--poll SECONDS` | `15` | Job status poll interval |
| `--job-timeout SECONDS` | `1800` | Give up waiting on a job after this time |
| `--offline` | off | Skip catalog lookups; just build the payload |

## Per-module overrides (scan mode)

Add fields that can't be derived from the module, such as `document-name` or
`reference`:

```json
{
  "ieee802-ethernet-interface": {
    "document-name": "IEEE Std 802.3.2-2025",
    "reference": "https://standards.ieee.org/"
  }
}
```

```bash
./yc_ieee_metadata_sync.py ~/src/yang --overrides overrides.json
```

Fields in the overrides file are also compared during the check. Alternatively,
edit `payload.json` directly and push it with `--payload-in`.

## Example output (illustrative)

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
| `repo is required unless --payload-in is given` | Give the repo path, or use `--payload-in FILE` |
| `Payload validation failed` | Fix the listed entries in the payload file |
| `Cannot read payload` | File missing or not valid JSON |
| `Set YC_USER and YC_PASSWORD` | Export both variables before `--apply` |
| PUT fails with 401 | Wrong credentials, or account not yet approved |
| PUT fails with 403 / job `Failed` | Account lacks rights for the IEEE paths; ask a YANG Catalog admin |
| Every module shows `ERROR` with `403` | The catalog rejects the default `python-requests` User-Agent. The scripts now send an explicit `User-Agent` (see `new_session()`); if you see this, make sure you are on the patched version |
| Every module shows `ERROR` | Catalog search endpoint unreachable or changed; check the [API docs](https://www.yangcatalog.org/doc/) |
| Every module shows `STALE` with only a `schema:` difference | Fixed. Older versions compared the catalog `schema` download URL against the repo `source-file.path`, which can never match. The check now only confirms the URL references the module's `name@revision` |
| `DUP` lines | Same `name@revision` in more than one directory; only the first file is used |
| `NO-REV` | Module has no `revision` statement and is skipped |
| A newly pushed (`MISSING`) module comes back `STALE` with `maturity-level: catalog='not-applicable' expected='ratified'` | Expected on first ingest: the catalog stores a brand-new module as `not-applicable` and only accepts the real `maturity-level` on a second push. `--apply` now re-pushes still-stale modules automatically (up to `--max-passes`, default 3), so a single `--apply` converges. Older versions required you to run scan → apply → scan → apply by hand |
| `--apply` hangs forever printing `... In progress` until you kill it | Fixed. The `/api/job/{id}` endpoint returns `result: "In progress"` with an empty `reason` even for a finished-and-dropped (or unknown) job id, so the poller never saw a terminal state. `wait_job()` now treats a bounded run of empty-`reason` "In progress" polls as a completed job instead of looping until `--job-timeout` |

## Notes

- The catalog lookup uses `GET /api/search/modules/{name},{revision},{organization}`.
  If YANG Catalog changes this endpoint, update `get_catalog_entry()`.
- Namespace, prefix and yang-version are compared but not sent. The catalog
  derives them from the source file when it processes the PUT.
- The catalog's search response does **not** include a `source-file` object. Its
  only location field is `schema`, a normalized download URL of the form
  `https://www.yangcatalog.org/all_modules/<name>@<revision>.yang` with no repo
  directory structure. The comparison therefore only checks that this URL
  references the module's `name@revision`; it does not (and cannot) compare it
  against the GitHub `source-file.path`.
- All HTTP requests send an explicit `User-Agent` (`new_session()`). The live
  catalog returns `403 Forbidden` to the default `python-requests` User-Agent.
- A brand-new module is stored by the catalog with `maturity-level:
  not-applicable` on first ingest, so it reports `STALE` on the next check and
  only becomes `ratified` after a second push. Under `--apply` the push loop
  (`push_modules()`) re-checks each pushed module and re-pushes the ones still
  stale, up to `--max-passes` passes, so a single `--apply` converges instead of
  needing a manual scan/apply/scan/apply cycle.
- Job polling (`wait_job()`) must tolerate the catalog dropping finished jobs:
  `GET /api/job/{id}` returns `result: "In progress"` with an empty `reason` for
  both a genuinely running job and an unknown/expired one. The poller resets its
  patience whenever it sees a non-empty `reason` (real progress) and, after a
  bounded run of empty-`reason` polls, concludes the job finished rather than
  looping until `--job-timeout`.
- The comparison logic and the live search endpoint have been exercised against
  the live catalog; full `--apply` pushes to the IEEE paths still depend on an
  approved account, so start with a single-module payload.
