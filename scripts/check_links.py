"""Check every URL in the catalog and record the result in data/link-status.json.

    python scripts/check_links.py

Status per URL:
  ok         2xx/3xx
  reachable  server answered but refused us (401/403/405/406/429...): typical for
             bot protection and for MCP endpoints that need auth or POST
  broken     404/410, DNS failure, connection refused
  error      5xx or timeout (transient; re-check before acting on it)
Exit code 1 if any docs URL is broken, so CI flags it.
"""
import concurrent.futures as cf
import json
import socket
import ssl
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ("docs", "mcp", "openapi", "llms_txt")
UA = "Mozilla/5.0 (compatible; ai-agents-api-library-linkcheck/1.0; +https://github.com/eater2/ai_agents_api_library)"


INIT = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "linkcheck", "version": "1.0"}}}).encode()


def probe_mcp(url):
    """Remote MCP endpoints often 404 on GET but answer a POST initialize."""
    status, code = probe(url)
    if status != "broken" or code != 404:
        return status, code
    req = urllib.request.Request(url, data=INIT, headers={
        "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    return probe(req)


def probe(url):
    req = url if isinstance(url, urllib.request.Request) else urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            return "ok", r.status
    except urllib.error.HTTPError as e:
        if e.code in (404, 410):
            return "broken", e.code
        if e.code >= 500:
            return "error", e.code
        return "reachable", e.code
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ssl.SSLError) as e:
        reason = getattr(e, "reason", e)
        if isinstance(reason, (socket.timeout, TimeoutError, ssl.SSLError)) or "timed out" in str(reason):
            return "error", "timeout"
        return "broken", str(reason)[:80]
    except Exception as e:
        return "error", str(e)[:80]


def urls(e):
    for f in FIELDS:
        u = (e.get("mcp") or {}).get("url") if f == "mcp" else e.get(f)
        if u and u.startswith("http"):
            yield f, u


def main():
    items = json.loads((ROOT / "data" / "catalog.json").read_text("utf-8"))
    jobs = [(e["id"], f, u) for e in items for f, u in urls(e)]
    today = date.today().isoformat()
    out = {e["id"]: {"checked_at": today} for e in items}
    with cf.ThreadPoolExecutor(24) as ex:
        for (id_, f, u), (status, code) in zip(jobs, ex.map(lambda j: (probe_mcp if j[1] == "mcp" else probe)(j[2]), jobs)):
            out[id_][f] = status
            if status in ("broken", "error"):
                out[id_][f + "_detail"] = code
    (ROOT / "data" / "link-status.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    counts = {}
    for id_, r in out.items():
        for f in FIELDS:
            if f in r:
                counts.setdefault(f, {}).setdefault(r[f], 0)
                counts[f][r[f]] += 1
    print(json.dumps(counts, indent=1))
    broken = [(i, f, r.get(f + "_detail")) for i, r in out.items() for f in FIELDS if r.get(f) == "broken"]
    for b in broken:
        print("BROKEN", *b)
    return 1 if any(f == "docs" for _, f, _ in broken) else 0


if __name__ == "__main__":
    raise SystemExit(main())
