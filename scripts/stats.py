"""Weekly usage snapshot of the catalog itself, appended to data/stats.json.

Signals that need no admin rights: GitHub stars/forks/watchers and release downloads,
Smithery use count of our MCP server, and npm downloads once the package is published.
GitHub traffic (views, clones) is added when the token has repository Administration: read.
MCP tool calls on the remote endpoint are logged as {"evt":"mcp",...} lines in Vercel runtime logs.
"""
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "eater2/ai_agents_api_library"
UA = "ai-agents-api-library-stats/1.0"


def get(url, token=None):
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, ValueError):
        return None


def main():
    token = os.environ.get("GITHUB_TOKEN")
    snap = {"at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}
    repo = get(f"https://api.github.com/repos/{REPO}", token)
    if repo:
        snap["github"] = {k: repo[k] for k in ("stargazers_count", "forks_count", "subscribers_count", "open_issues_count")}
    releases = get(f"https://api.github.com/repos/{REPO}/releases", token) or []
    snap["release_downloads"] = sum(a["download_count"] for r in releases for a in r.get("assets", []))
    for kind in ("views", "clones"):
        t = get(f"https://api.github.com/repos/{REPO}/traffic/{kind}", token)
        if t and "count" in t:
            snap[f"github_{kind}_14d"] = {"count": t["count"], "uniques": t["uniques"]}
    smithery = get("https://registry.smithery.ai/servers/eater2/ai-agents-api-library")
    if smithery:
        snap["smithery_uses"] = smithery.get("useCount")
    npm = get("https://api.npmjs.org/downloads/point/last-week/ai-agents-api-library")
    if npm and "downloads" in npm:
        snap["npm_downloads_week"] = npm["downloads"]

    path = ROOT / "data" / "stats.json"
    history = json.loads(path.read_text("utf-8")) if path.exists() else []
    history.append(snap)
    path.write_text(json.dumps(history, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(snap))


if __name__ == "__main__":
    main()
