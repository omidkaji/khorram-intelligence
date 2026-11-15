#!/usr/bin/env python3
"""Sync explicitly approved public Google Sheets data for GitHub Pages."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

url = os.environ["KHORRAM_API_URL"]
req = Request(url, headers={"User-Agent": "Khorram-Intelligence-Sync/1.0"})
with urlopen(req, timeout=35) as response:
    if response.status != 200:
        raise RuntimeError(f"HTTP {response.status}")
    payload = response.read(3_000_000)
print("HTTP response preview:", repr(payload[:500].decode("utf-8", errors="replace")))
print("Response size:", len(payload))
data = json.loads(payload)
if not isinstance(data, dict) or data.get("error"):
    raise ValueError("Apps Script returned invalid or error data")
allowed = ("Prices", "News", "Borders", "Dairy")
if not isinstance(data.get("updated_at"), str):
    raise ValueError("Missing updated_at")
out = {"updated_at": data["updated_at"]}
for name in allowed:
    rows = data.get(name)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"Invalid {name} rows")
    if len(rows) > 20000:
        raise ValueError(f"Too many {name} rows")
    out[name] = rows
target = Path("data/public.json")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Synced public rows:", {key: len(out[key]) for key in allowed})
