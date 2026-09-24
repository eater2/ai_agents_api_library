"""Daily availability probe of each service's API base URL and hosted MCP endpoint.

    python scripts/probe_uptime.py

One probe per target per run (the GitHub Action runs daily from a US runner). A target counts as up when
the server answers with any HTTP status below 500: 401/403/404 on a bare base URL still means the API
host is reachable. Down = 5xx, timeout, DNS or connection failure. Hosted MCP endpoints get a POST
`initialize`, like a real client. Results keep a rolling 30-day history in data/uptime.json, which
build.py summarises into the `uptime` field of each entry.
"""
import concurrent.futures as cf
import json
import re
import socket
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "uptime.json"
WINDOW_DAYS = 30
UA = "Mozilla/5.0 (compatible; ai-agents-api-library-uptime/1.0; +https://github.com/eater2/ai_agents_api_library)"
INIT = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "uptime-probe", "version": "1.0"}}}).encode()


def probe(url, mcp=False):
    """Return (up, latency_ms, detail): detail is the HTTP status or an error class."""
    headers = {"User-Agent": UA, "Accept": "application/json, text/event-stream, */*"}
    if mcp:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=INIT if mcp else None, headers=headers)
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except (socket.timeout, TimeoutError):
        return False, None, "timeout"
    except urllib.error.URLError as e:
        reason = str(getattr(e, "reason", e)).lower()
        kind = "timeout" if "timed out" in reason else "dns" if "getaddrinfo" in reason or "name or service" in reason \
            else "tls" if "ssl" in reason or "certificate" in reason else "connection"
        return False, None, kind
    except Exception as e:  # noqa: BLE001 - one bad target must not stop the run
        return False, None, type(e).__name__
    ms = round((time.monotonic() - t0) * 1000)
    return code < 500, ms, code


def concrete(url):
    """First URL in the field, or None when it is a per-account template (<region>, {subdomain}, example host)."""
    if not isinstance(url, str) or not url.startswith("http"):
        return None
    url = url.split()[0]
    return None if re.search(r"[<>{}]|\bexample\b|your[-_]", url) else url


def targets():
    items = json.loads((ROOT / "data" / "catalog.json").read_text("utf-8"))
    for e in items:
        if base := concrete(e.get("base_url")):
            yield e["id"], "api", base
        if remote := concrete((e.get("mcp") or {}).get("remote_url")):
            yield e["id"], "mcp", remote


def main():
    data = json.loads(OUT.read_text("utf-8")) if OUT.exists() else {}
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%MZ")
    jobs = list(targets())
    with cf.ThreadPoolExecutor(24) as ex:
        results = list(ex.map(lambda t: (t, probe(t[2], mcp=t[1] == "mcp")), jobs))
    live = {(eid, kind) for eid, kind, _ in jobs}
    for (eid, kind, url), (up, ms, detail) in results:
        rec = data.setdefault(eid, {}).setdefault(kind, {"url": url, "history": []})
        if rec.get("url") != url:  # a new URL starts a new history
            rec.update(url=url, history=[])
        rec["history"].append({"at": stamp, "up": up, "ms": ms, "detail": detail})
        cutoff = now.timestamp() - WINDOW_DAYS * 86400
        rec["history"] = [h for h in rec["history"]
                          if datetime.strptime(h["at"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).timestamp() >= cutoff]
    for eid in list(data):  # drop targets that left the catalog
        for kind in list(data[eid]):
            if (eid, kind) not in live:
                del data[eid][kind]
        if not data[eid]:
            del data[eid]
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    down = [(eid, kind, d) for (eid, kind, _), (up, _, d) in results if not up]
    print(f"probed {len(results)} targets, {len(results) - len(down)} up, {len(down)} down")
    for eid, kind, d in down:
        print(f"  down: {eid} {kind} {d}")


if __name__ == "__main__":
    main()
