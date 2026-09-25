"""MCP handshake check of every hosted MCP endpoint in the catalog.

    python scripts/probe_mcp.py

Sends a real JSON-RPC `initialize` (Streamable HTTP, like an MCP client) and classifies the answer:
  ok            - an MCP server answered (JSON-RPC result, possibly as an SSE event)
  auth_oauth    - 401 with OAuth protected-resource metadata (RFC 9728) or a Bearer challenge: the client signs in
  auth_required - 401/403 without an OAuth hint: an API key or token in a header is needed
  not_mcp       - the URL answers, but not as an MCP server (HTML page, 404/405, other JSON)
  blocked       - 403 with an HTML page (bot protection): unknown, neither confirmed nor refuted
  down          - 5xx, timeout, DNS or TLS failure
Results go to data/mcp-handshake.json; build.py keeps a connection snippet derived from a URL only when the
handshake shows an MCP server there (ok / auth_*), and adds `handshake` to `mcp` for agents.
"""
import concurrent.futures as cf
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "mcp-handshake.json"
UA = "ai-agents-api-library-mcp-probe/1.0 (+https://github.com/eater2/ai_agents_api_library)"
INIT = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "catalog-probe", "version": "1.0"}}}).encode()


def classify(url, hops=0):
    req = urllib.request.Request(url, data=INIT, headers={
        "User-Agent": UA, "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
            code, headers, body = r.status, r.headers, r.read(20000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (307, 308) and e.headers.get("Location") and hops < 2:  # urllib does not re-POST on redirects
            return classify(urllib.parse.urljoin(url, e.headers["Location"]), hops + 1)
        code, headers = e.code, e.headers
        try:
            body = e.read(20000).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = ""
    except Exception as e:  # noqa: BLE001 - network errors are a result, not a crash
        return {"status": "down", "detail": type(e).__name__}
    auth = headers.get("WWW-Authenticate", "") if headers else ""
    if code >= 500:
        return {"status": "down", "detail": code}
    if code in (401, 403):
        if "resource_metadata" in auth or auth.lower().startswith("bearer"):
            return {"status": "auth_oauth" if "resource_metadata" in auth else "auth_required", "detail": code}
        if code == 403 and not body.lstrip().startswith("{"):
            return {"status": "blocked", "detail": "403 html"}  # bot protection or a web page: cannot tell
        if "<html" in body[:2000].lower():
            return {"status": "not_mcp", "detail": f"{code} html"}
        return {"status": "auth_required", "detail": code}
    if code < 300 and re.search(r'"jsonrpc"\s*:\s*"2\.0"', body) and ('"result"' in body or '"serverInfo"' in body):
        return {"status": "ok", "detail": code}
    if code < 300 and re.search(r'"jsonrpc"\s*:\s*"2\.0"', body) and '"error"' in body:
        return {"status": "ok", "detail": f"{code} jsonrpc error"}  # an MCP server that rejected the probe's parameters
    kind = "html" if "<html" in body[:2000].lower() else "other"
    return {"status": "not_mcp", "detail": f"{code} {kind}"}


def targets():
    for e in json.loads((ROOT / "catalog" / "all.json").read_text("utf-8")):  # built file: has domain_verified
        m = e.get("mcp") or {}
        url = m.get("remote_url") or (m.get("url") if m.get("domain_verified") is not None else None)
        if isinstance(url, str) and url.startswith("http") and "github.com" not in url and not re.search(r"[<>{}]", url):
            yield e["id"], url


def main():
    jobs = list(targets())
    with cf.ThreadPoolExecutor(16) as ex:
        results = list(ex.map(lambda t: (t, classify(t[1])), jobs))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    data = {eid: {"url": url, "checked_at": stamp, **res} for (eid, url), res in results}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    counts = {}
    for r in data.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"probed {len(data)} MCP endpoints: {counts}")
    for eid, r in sorted(data.items()):
        if r["status"] in ("not_mcp", "down"):
            print(f"  {r['status']}: {eid} {r['url']} ({r['detail']})")


if __name__ == "__main__":
    main()
