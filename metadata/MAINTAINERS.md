# Maintainer / knowledge guide

A guide for understanding and modifying this project. Read this before changing
the code. The user-facing usage documentation is in `README.md`; this file is
about the internals, the design decisions, and how to make changes safely.

## What this project is

Two Python scripts that keep IEEE YANG module metadata in sync with the public
[YANG Catalog](https://www.yangcatalog.org):

- `yc_ieee_metadata_sync.py` — the main program. Scans a local YangModels/yang
  clone, compares each module's metadata against the catalog, and optionally
  pushes corrections.
- `yc_check_credentials.py` — a small helper that verifies YANG Catalog API
  credentials with a harmless empty PUT.

Supporting files:

- `payload*.json` — generated PUT payloads (`{"modules": {"module": [...]}}`).
- `report*.json` — per-module diff reports written by `--report-out`.
- `*-orig.*` — baseline copies kept for reference; do not edit in place.
- Timestamped copies (`*-YYYY-MM-DD-HHMM.json`) are working snapshots.

## How the main program is structured

`yc_ieee_metadata_sync.py` is a single file. Read it top to bottom in these
blocks:

1. **YANG parser** — `_tokenize`, `_parse`, `parse_yang`. A deliberately minimal
   hand-rolled tokenizer/parser that reads only top-level statements (name,
   revision, namespace, prefix, yang-version, contact, reference). It is not a
   full YANG parser and does not need to be. If a module fails to parse, extend
   the tokenizer rather than reaching for an external dependency, to keep the
   script dependency-light (only `requests`).
2. **Email selection** — `pick_email`. Prefers the WG mailing list line in the
   `contact` statement, falls back to the first address found.
3. **Expected metadata** — `build_expected`. Combines parsed fields with fixed
   IEEE values (organization, maturity-level, classification) and the
   `source-file` block, then applies per-module `--overrides`.
4. **Payload handling** — `load_payload` (validation), `run_from_payload`
   (`--payload-in` mode).
5. **Catalog API helpers** — `new_session`, `get_catalog_entry`, `compare`,
   `put_metadata`, `wait_job`, `push_modules`.
6. **`main`** — argument parsing and the scan-mode loop.

Two modes:

- **Scan mode** (default): derive metadata from `.yang` files, compare, report,
  optionally push. Needs the `repo` positional argument.
- **Payload mode** (`--payload-in`): push a hand-reviewed payload as-is, no scan.

## Things to know before you change the comparison logic

These are the non-obvious facts about the live catalog that drive the current
design. They were confirmed against the live API, not assumed.

- **The search response has no `source-file` object.** A lookup of
  `GET /api/search/modules/{name},{revision},{organization}` returns fields like
  `name`, `revision`, `organization`, `maturity-level`,
  `module-classification`, `author-email`, `namespace`, `prefix`,
  `yang-version`, and `schema` — but **not** `source-file`. Do not try to
  compare against `catalog["source-file"]`; it does not exist.
- **`schema` is a flat download URL**, e.g.
  `https://www.yangcatalog.org/all_modules/ieee1588-ptp-ms@2023-08-14.yang`.
  It has no repo directory structure, so it must **never** be compared against
  the repo `source-file.path` (e.g.
  `standard/ieee/published/1588/ieee1588-ptp-ms.yang`). Doing so was the cause
  of a false-positive bug where every module reported `STALE` on a `schema:`
  difference. `compare()` now only checks that the URL ends with
  `<name>@<revision>.yang`.
- **The default `python-requests` User-Agent gets `403 Forbidden`.** The catalog
  accepts requests that send an explicit `User-Agent`. All sessions are created
  through `new_session()`, which sets one. If you add a new call site, create
  the session with `new_session()`, not `requests.Session()` directly.
- **`yang-version` normalization.** `compare()` treats `1.0` and `1` as equal.
  The catalog may report either form.
- **Fields compared but not sent.** namespace, prefix, and yang-version are
  compared for drift but not included in the PUT payload; the catalog derives
  them from the source file. `build_expected` reflects this.

## How to make a change safely

1. Edit `yc_ieee_metadata_sync.py`.
2. Byte-compile: `python3 -m py_compile yc_ieee_metadata_sync.py`.
3. Exercise the real code path against the live catalog without needing a repo
   clone by importing the module and calling `new_session()`,
   `get_catalog_entry()` and `compare()` directly on a few known modules (this
   is how the schema fix was verified). Use modules from an existing
   `report*.json` as test input.
4. For a full end-to-end check you need a local YangModels/yang clone:
   `./yc_ieee_metadata_sync.py ~/src/yang --report-out report-new.json --payload-out payload-new.json`
5. Never run `--apply` casually. It writes to the public catalog and requires an
   approved account. Start with a single-module payload and `--batch-size 1`.
6. Keep the dependency surface at just `requests` + the standard library.

## Common modification points

- **Add/relax a compared field** → `compare()` (the `checks` dict) and, if it
  should be pushed, `build_expected()`.
- **Change which email is chosen** → `pick_email()`.
- **Support a new catalog endpoint shape** → `get_catalog_entry()`.
- **Change job polling / batching** → `wait_job()`, `push_modules()`, and the
  `--batch-size` / `--poll` / `--job-timeout` options in `main()`.
- **New per-module metadata that can't be derived** → `--overrides` file plus
  the `checks` additions in `compare()`.

## Change history (notable)

- Fixed `schema`/`source-file.path` false-positive `STALE` in `compare()`.
- Added explicit `User-Agent` via `new_session()` to avoid catalog `403`s.

## Provenance / AI engine used

This question was investigated directly on the machine where the project lives.
The honest answer: **the AI engine (if any) that originally created these files
could not be determined from the available evidence.**

- The source files contain no generator signature, and the git history
  (authored by human committers) has no AI co-author trailers.
- Searching the local tool histories and session stores on this machine
  (`~/.bash_history`, `~/.kiro`, `~/.claude`) found **no** Kiro CLI or Claude
  Code session rooted at this directory prior to the maintenance session that
  produced these edits. Both tools were used elsewhere on the machine, but under
  Linux-home paths (`~/pp26`, `~/aws/...`), not this Dropbox/`/mnt/c` path.
- The one AI session ever rooted here is the maintenance session documented
  under "Change history" above (Kiro CLI), which made the `compare()` /
  `new_session()` fixes and wrote this file. That session did **not** create the
  original scripts; they already existed.

In short: the bug fixes and this knowledge file were produced with **Kiro CLI**.
The authorship of the original program is unverified — treat it as
human-authored unless better evidence turns up.
