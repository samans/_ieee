#!/usr/bin/env python3
"""
yc_check_credentials.py - check YANG Catalog API credentials without changing anything.

It sends an authenticated PUT to /api/modules with an empty module list.
The server checks the credentials before it reads the body, so:
  401           -> credentials rejected
  400 / 2xx     -> credentials accepted (the empty payload is rejected or ignored)

Usage:
  export YC_USER=... YC_PASSWORD=...     # or you'll be prompted
  ./yc_check_credentials.py
"""
import getpass
import json
import os
import sys

import requests

API = "https://www.yangcatalog.org/api/modules"

user = os.environ.get("YC_USER") or input("YANG Catalog username: ")
pwd = os.environ.get("YC_PASSWORD") or getpass.getpass("Password: ")

try:
    r = requests.put(
        API,
        data=json.dumps({"modules": {"module": []}}),
        auth=(user, pwd),
        headers={"Accept": "application/json", "Content-type": "application/json"},
        timeout=60,
    )
except requests.RequestException as e:
    sys.exit(f"Connection error: {e}")

print(f"HTTP {r.status_code}: {r.text.strip()[:300]}")

if r.status_code == 401:
    sys.exit("FAIL: credentials rejected (wrong username/password or account not approved).")
if r.status_code == 403:
    sys.exit("FAIL: authenticated but not authorized for this operation.")
if r.status_code in (400, 200, 202) or r.status_code < 300:
    print("OK: credentials accepted. Permissions for specific IEEE paths are checked "
          "when a real update job runs.")
    sys.exit(0)
sys.exit("UNKNOWN: unexpected response - check the output above.")
