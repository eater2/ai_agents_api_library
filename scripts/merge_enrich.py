"""Merge researched structured fields from data/enrich/*.json into data/catalog.json.

Each enrich file maps entry id -> record (see data/enrich/SPEC.md). Structured fields replace the
entry's previous values; `mcp` sub-fields are merged into the existing mcp object (type and url stay).
Reported corrections are collected in data/enrich/corrections.md for a human or agent to apply.
Usage: python scripts/merge_enrich.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIELDS = ("free_plan", "auth_scheme", "base_url", "rate_limits", "oauth_scopes", "async_jobs", "data_policy")
MCP_FIELDS = ("maintainer", "remote_url", "repo", "tools", "covers_full_api", "source_url", "checked_at")
URL = re.compile(r"^https?://\S+$")
PATCHABLE = ("docs", "homepage", "auth", "auth_hint", "mcp", "free_tier", "openapi", "llms_txt", "notes", "desc_en")
AUTH = {"api_key", "oauth2", "api_key+oauth2", "none", "cloud_iam"}
MCP_TYPES = {"official", "community", "none"}


def apply_fixes(by_id, today):
    """Apply data/enrich/fix_*.json: confirmed corrections of existing fields (see FIX_SPEC.md)."""
    patched, rejected = 0, []
    for f in sorted((DATA / "enrich").glob("fix_*.json")):
        for eid, patch in json.loads(f.read_text("utf-8")).items():
            e = by_id.get(eid)
            if not e:
                rejected.append(f"{eid}: unknown id")
                continue
            changed = False
            for field, value in patch.items():
                if field == "free_plan_kind" and value in ("free_tier", "trial", "none") and e.get("free_plan"):
                    if e["free_plan"].get("kind") != value:
                        e["free_plan"]["kind"] = value
                        changed = True
                    continue
                if field not in PATCHABLE:
                    continue
                if field == "auth" and value not in AUTH:
                    rejected.append(f"{eid}: auth {value!r}")
                    continue
                if field == "mcp":
                    if not isinstance(value, dict) or value.get("type") not in MCP_TYPES:
                        rejected.append(f"{eid}: mcp {value!r}")
                        continue
                    value = {**e.get("mcp", {}), "type": value["type"], "url": value.get("url")}
                if field in ("docs", "homepage", "openapi", "llms_txt") and value is not None and not URL.match(str(value)):
                    rejected.append(f"{eid}: {field} {value!r}")
                    continue
                if e.get(field) != value:
                    e[field] = value
                    changed = True
            if changed:
                e["verified"] = today
                patched += 1
    return patched, rejected


def clean(v):
    """Drop empty containers and records that carry no value besides provenance."""
    if isinstance(v, dict):
        v = {k: clean(x) for k, x in v.items()}
        v = {k: x for k, x in v.items() if x not in (None, "", [], {})}
        return v if set(v) - {"source_url", "checked_at"} else None
    if isinstance(v, list):
        v = [clean(x) for x in v if x not in (None, "")]
        return v or None
    if isinstance(v, str):
        v = v.strip()
    return v


def valid(field, v):
    """Keep a researched value only when it has a usable source URL (base_url is a URL itself)."""
    if field == "base_url":
        return isinstance(v, str) and bool(URL.match(v))
    return isinstance(v, dict) and bool(URL.match(v.get("source_url") or ""))


def main():
    catalog = json.loads((DATA / "catalog.json").read_text("utf-8"))
    by_id = {e["id"]: e for e in catalog}
    corrections, merged, unknown, dropped = [], 0, [], 0
    for f in sorted((DATA / "enrich").glob("b*.json")):
        for eid, rec in json.loads(f.read_text("utf-8")).items():
            e = by_id.get(eid)
            if not e:
                unknown.append(f"{f.name}:{eid}")
                continue
            for field in FIELDS:
                v = clean(rec.get(field))
                if v is None:
                    continue
                if valid(field, v):
                    e[field] = v
                else:
                    dropped += 1
            m = rec.get("mcp") or {}
            extra = {k: m[k] for k in MCP_FIELDS if m.get(k) not in (None, "", [])}
            if extra.get("source_url") and URL.match(extra["source_url"]):
                e["mcp"] = {"type": e["mcp"].get("type", "none"), "url": e["mcp"].get("url"), **extra}
            for c in rec.get("corrections") or []:
                corrections.append(f"- `{eid}`: {c}")
            merged += 1
    from datetime import date
    patched, rejected = apply_fixes(by_id, date.today().isoformat())
    print(f"fixes: {patched} entries patched, rejected: {rejected}")
    (DATA / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (DATA / "enrich" / "corrections.md").write_text(
        "# Corrections reported by research agents\n\nApply to data/catalog.json after checking the source.\n\n"
        + "\n".join(corrections) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {merged} entries, {len(corrections)} corrections, {dropped} values dropped (no source), unknown ids: {unknown}")


if __name__ == "__main__":
    main()
