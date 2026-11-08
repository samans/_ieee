#!/usr/bin/env python3
"""
yc_ieee_metadata_sync.py

Check that every IEEE YANG module in the YangModels/yang "published" directory
has up-to-date metadata in the YANG Catalog (https://www.yangcatalog.org), and
optionally push corrected metadata using the procedure described at
https://www.yangcatalog.org/contribute.html:

    PUT  https://www.yangcatalog.org/api/modules       (module-metadata JSON)
    GET  https://www.yangcatalog.org/api/job/{job-id}  (poll job status)

Metadata is derived from each .yang file itself (module name, latest revision,
contact e-mail, namespace, prefix, yang-version) plus fixed IEEE values
(organization "ieee", maturity-level "ratified" for published modules).

Usage examples
--------------
  # Report only (default, no writes)
  ./yc_ieee_metadata_sync.py ~/src/yang

  # Report, write JSON payload to a file, and push updates for stale modules
  export YC_USER=myuser YC_PASSWORD='secret'
  ./yc_ieee_metadata_sync.py ~/src/yang --payload-out ieee-metadata.json --apply

  # Push metadata for every module, stale or not
  ./yc_ieee_metadata_sync.py ~/src/yang --apply --force

Requires: Python 3.8+, requests  (pip install requests)
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

API = "https://www.yangcatalog.org/api"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


# --------------------------------------------------------------------------
# Minimal YANG parser (enough to read top-level statements reliably)
# --------------------------------------------------------------------------
def _tokenize(text):
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif c in "{};":
            yield c
            i += 1
        elif c in "\"'":
            parts = []
            while True:  # handle "a" + "b" concatenation
                q = text[i]
                i += 1
                buf = []
                while i < n and text[i] != q:
                    if q == '"' and text[i] == "\\" and i + 1 < n:
                        buf.append({"n": "\n", "t": "\t"}.get(text[i + 1], text[i + 1]))
                        i += 2
                    else:
                        buf.append(text[i])
                        i += 1
                i += 1
                parts.append("".join(buf))
                k = i
                while k < n and text[k].isspace():
                    k += 1
                if k < n and text[k] == "+":
                    k += 1
                    while k < n and text[k].isspace():
                        k += 1
                    if k < n and text[k] in "\"'":
                        i = k
                        continue
                break
            yield ("STR", "".join(parts))
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "{};" \
                    and not text.startswith("//", j) and not text.startswith("/*", j):
                j += 1
            yield ("STR", text[i:j])
            i = j


def _parse(tokens):
    """Return list of (keyword, argument, children)."""
    stmts = []
    for tok in tokens:
        if tok == "}":
            return stmts
        if tok in ("{", ";"):
            continue
        kw = tok[1]
        arg, children = None, []
        nxt = next(tokens, None)
        if isinstance(nxt, tuple):
            arg = nxt[1]
            nxt = next(tokens, None)
        if nxt == "{":
            children = _parse(tokens)
        stmts.append((kw, arg, children))
    return stmts


def parse_yang(path):
    tree = _parse(_tokenize(path.read_text(encoding="utf-8", errors="replace")))
    top = next((s for s in tree if s[0] in ("module", "submodule")), None)
    if top is None:
        raise ValueError("no module/submodule statement found")
    kw, name, body = top

    def first(k):
        return next((a for (kk, a, _) in body if kk == k), None)

    revisions = sorted((a for (kk, a, _) in body if kk == "revision" and a), reverse=True)
    info = {
        "kind": kw,
        "name": name,
        "revision": revisions[0] if revisions else None,
        "namespace": first("namespace"),
        "prefix": first("prefix"),
        "yang-version": first("yang-version") or "1.0",
        "organization-stmt": first("organization"),
        "contact": first("contact") or "",
        "reference": first("reference"),
    }
    if kw == "submodule":
        bt = next((c for c in body if c[0] == "belongs-to"), None)
        info["belongs-to"] = bt[1] if bt else None
    return info


def pick_email(contact):
    """Prefer the WG mailing list (WG-EMail / E-mail line); else first address."""
    for line in contact.splitlines():
        if re.search(r"(wg-)?e-?mail\s*:", line, re.I):
            m = EMAIL_RE.search(line)
            if m:
                return m.group(0)
    m = EMAIL_RE.search(contact)
    return m.group(0) if m else None


# --------------------------------------------------------------------------
# Build expected metadata
# --------------------------------------------------------------------------
def build_expected(info, rel_path, args, overrides):
    md = {
        "name": info["name"],
        "revision": info["revision"],
        "organization": args.organization,
        "maturity-level": args.maturity_level,
        "module-classification": args.classification,
        "source-file": {
            "owner": args.owner,
            "repository": args.repository,
            "path": rel_path,
            "branch": args.branch,
        },
    }
    email = pick_email(info["contact"])
    if email:
        md["author-email"] = email
    md.update(overrides.get(info["name"], {}))  # e.g. document-name, reference
    return md


# --------------------------------------------------------------------------
# YANG Catalog API helpers
# --------------------------------------------------------------------------
def get_catalog_entry(session, name, revision, org):
    url = f"{API}/search/modules/{name},{revision},{org}"
    r = session.get(url, headers={"Accept": "application/json"}, timeout=60)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    data = r.json()
    mods = data.get("module") or data.get("yang-catalog:module") or []
    return mods[0] if isinstance(mods, list) and mods else (data if "name" in data else None)


def compare(expected, info, catalog):
    """Return list of human-readable differences (empty = up to date)."""
    if catalog is None:
        return ["not in catalog (name/revision/organization missing)"]
    diffs = []
    checks = {
        "organization": expected["organization"],
        "maturity-level": expected["maturity-level"],
        "module-classification": expected["module-classification"],
        "author-email": expected.get("author-email"),
        "namespace": info["namespace"] if info["kind"] == "module" else None,
        "prefix": info["prefix"] if info["kind"] == "module" else None,
        "yang-version": info["yang-version"],
    }
    for k in ("document-name", "reference"):
        if k in expected:
            checks[k] = expected[k]
    for field, want in checks.items():
        if want is None:
            continue
        have = catalog.get(field)
        if field == "yang-version":
            want, have = str(want).replace("1.0", "1"), str(have or "").replace("1.0", "1")
        if str(have or "").strip().lower() != str(want).strip().lower():
            diffs.append(f"{field}: catalog={have!r} expected={want!r}")
    schema = catalog.get("schema") or ""
    if schema and not schema.endswith(expected["source-file"]["path"]):
        diffs.append(f"schema: catalog={schema!r} expected path ...{expected['source-file']['path']}")
    return diffs


def put_metadata(session, modules, user, password):
    payload = {"modules": {"module": modules}}
    r = session.put(f"{API}/modules", data=json.dumps(payload), auth=(user, password),
                    headers={"Accept": "application/json", "Content-type": "application/json"},
                    timeout=300)
    if r.status_code >= 400:
        raise RuntimeError(f"PUT failed {r.status_code}: {r.text[:500]}")
    return r.json().get("job-id")


def wait_job(session, job_id, poll, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = session.get(f"{API}/job/{job_id}", headers={"Accept": "application/json"}, timeout=60)
        r.raise_for_status()
        info = r.json().get("info", r.json())
        status = info.get("job-status") or info.get("status") or str(info)
        if status not in ("In progress", "In Progress"):
            return status, info.get("reason")
        time.sleep(poll)
    return "Timeout", None


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", type=Path, help="path to local clone of YangModels/yang")
    ap.add_argument("--published-dir", default="standard/ieee/published",
                    help="directory (relative to repo) to scan [%(default)s]")
    ap.add_argument("--organization", default="ieee")
    ap.add_argument("--maturity-level", default="ratified")
    ap.add_argument("--classification", default="network-element")
    ap.add_argument("--owner", default="YangModels")
    ap.add_argument("--repository", default="yang")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--overrides", type=Path,
                    help='JSON file {"module-name": {"document-name": "...", "reference": "..."}}')
    ap.add_argument("--payload-out", type=Path, help="write PUT payload JSON here")
    ap.add_argument("--report-out", type=Path, help="write check report JSON here")
    ap.add_argument("--apply", action="store_true", help="PUT updated metadata to YANG Catalog")
    ap.add_argument("--force", action="store_true", help="with --apply, push all modules, not just stale")
    ap.add_argument("--batch-size", type=int, default=20)
    ap.add_argument("--poll", type=int, default=15, help="job poll interval (s)")
    ap.add_argument("--job-timeout", type=int, default=1800)
    ap.add_argument("--offline", action="store_true", help="skip catalog lookups (just build payload)")
    args = ap.parse_args()

    base = args.repo / args.published_dir
    if not base.is_dir():
        sys.exit(f"Not a directory: {base}")
    overrides = json.loads(args.overrides.read_text()) if args.overrides else {}

    session = requests.Session()
    seen, report, to_push = {}, [], []
    files = sorted(base.rglob("*.yang"))
    print(f"Scanning {len(files)} .yang files under {base}\n")

    for f in files:
        rel = f.relative_to(args.repo).as_posix()
        try:
            info = parse_yang(f)
        except Exception as e:
            print(f"[PARSE-ERR] {rel}: {e}")
            report.append({"path": rel, "status": "parse-error", "detail": str(e)})
            continue
        if not info["revision"]:
            print(f"[NO-REV]    {rel}: no revision statement, skipped")
            report.append({"path": rel, "status": "no-revision"})
            continue
        key = (info["name"], info["revision"])
        if key in seen:
            print(f"[DUP]       {rel}: same as {seen[key]}, skipped")
            continue
        seen[key] = rel

        expected = build_expected(info, rel, args, overrides)
        if args.offline:
            diffs, status = [], "unchecked"
        else:
            try:
                cat = get_catalog_entry(session, info["name"], info["revision"], args.organization)
                diffs = compare(expected, info, cat)
                status = "ok" if not diffs else ("missing" if cat is None else "stale")
            except requests.RequestException as e:
                diffs, status = [f"lookup error: {e}"], "error"

        tag = {"ok": "OK", "missing": "MISSING", "stale": "STALE",
               "error": "ERROR", "unchecked": "PAYLOAD"}[status]
        print(f"[{tag:<9}] {info['name']}@{info['revision']}  ({rel})")
        for d in diffs:
            print(f"              - {d}")
        report.append({"path": rel, "name": info["name"], "revision": info["revision"],
                       "status": status, "differences": diffs})
        if args.force or args.offline or status in ("missing", "stale"):
            to_push.append(expected)

    counts = {}
    for r in report:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\nSummary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"Modules needing metadata update: {len(to_push)}")

    if args.report_out:
        args.report_out.write_text(json.dumps(report, indent=2))
        print(f"Report written to {args.report_out}")
    if args.payload_out:
        args.payload_out.write_text(json.dumps({"modules": {"module": to_push}}, indent=2))
        print(f"PUT payload written to {args.payload_out}")

    if not args.apply:
        if to_push:
            print("\nDry run. Re-run with --apply (and YC_USER / YC_PASSWORD set) to update.")
        return 0 if not to_push else 1

    user, pwd = os.environ.get("YC_USER"), os.environ.get("YC_PASSWORD")
    if not (user and pwd):
        sys.exit("Set YC_USER and YC_PASSWORD environment variables for --apply")
    failures = 0
    for i in range(0, len(to_push), args.batch_size):
        batch = to_push[i:i + args.batch_size]
        names = ", ".join(m["name"] for m in batch)
        print(f"\nPUT batch {i // args.batch_size + 1} ({len(batch)} modules): {names}")
        try:
            job = put_metadata(session, batch, user, pwd)
            print(f"  job-id {job}")
            status, reason = wait_job(session, job, args.poll, args.job_timeout)
            print(f"  result: {status}" + (f"  reason: {reason}" if reason else ""))
            failures += status != "Finished"
        except Exception as e:
            print(f"  FAILED: {e}")
            failures += 1
    print("\nDone. Re-run without --apply to verify the catalog now matches.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
