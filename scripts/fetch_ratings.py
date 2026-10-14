"""Fetch public ratings, review counts and usage signals for catalog entries.

Sources (only ones that allow automated access):
  github       stars, forks, last push of repos referenced by the entry (REST API, GITHUB_TOKEN)
  github_issues  open vs resolved issues, median days to fix, last 90 days' intake and closes, issue_health 0-100,
               for those repos and the official SDK repos named in npm/PyPI package metadata (GraphQL API, GITHUB_TOKEN)
  smithery     use count of the verified Smithery server with the same name (public registry API)
  sourceforge  rating, review count and review texts from sourceforge.net/software/product/<slug>/
               (allowed by robots.txt; product slugs come from its sitemap; a match must link the
               entry's homepage domain)

  npm          monthly downloads of the vendor's official JS/TS SDK (api.npmjs.org)
  pypi         monthly downloads of the vendor's official Python SDK (pypistats.org API)
  stackoverflow  question count of the product's tag (Stack Exchange API)
  appstore     rating and rating count of the vendor's own iOS app for the same product (Apple iTunes Lookup API)

Package names, tags and app ids come from data/popularity-ids.json, researched from vendor docs (not guessed:
registry search returns third-party wrappers). It can also name a SourceForge product page the sitemap match misses.

G2, Capterra, GetApp and Product Hunt block automated clients, and Google Play has no public API and its terms
forbid automated access, so they are not fetched.

Writes data/ratings.json (aggregates) and catalog/reviews/<id>.json (review texts, reviewer names
dropped; served to agents via GitHub raw and the MCP tool get_reviews, not shown on the website). Usage: python scripts/fetch_ratings.py [--only id,id] [--reviews N]
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 ai-agents-api-library/1.0 (+https://github.com/eater2/ai_agents_api_library)"
SF = "https://sourceforge.net"
SF_DELAY = 1.5  # seconds between SourceForge requests
SF_PER_PAGE = 20


def get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def domain(url):
    host = urllib.parse.urlparse(url or "").netloc.lower()
    return host[4:] if host.startswith("www.") else host


def base_domain(url):
    parts = domain(url).split(".")
    return ".".join(parts[-3:] if len(parts) > 2 and len(parts[-2]) <= 3 else parts[-2:])


# ---------- GitHub ----------

def github_token():
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not tok and sys.platform == "win32":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                tok = winreg.QueryValueEx(k, "GITHUB_TOKEN")[0]
        except OSError:
            pass
    return tok


def repos_of(e):
    fields = [e.get("homepage"), e.get("docs"), e.get("openapi"), (e.get("mcp") or {}).get("url")]
    found = []
    for v in fields:
        for m in re.findall(r"github\.com/([\w.-]+)/([\w.-]+)", v or ""):
            repo = f"{m[0]}/{m[1].removesuffix('.git')}"
            if repo not in found:
                found.append(repo)
    return found


def github(repo, token):
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = json.loads(get(f"https://api.github.com/repos/{repo}", headers))
    except urllib.error.HTTPError:
        return None
    return {"source": "github", "repo": r["full_name"], "stars": r["stargazers_count"], "forks": r["forks_count"],
            "pushed_at": r["pushed_at"][:10], "archived": r["archived"], "url": r["html_url"]}


# ---------- GitHub issues: how the vendor resolves reported problems ----------

def sdk_repo(registry, pkg):
    """GitHub repo named in the official package's metadata (npm repository field, PyPI project URLs)."""
    if registry == "npm":
        d = jget(f"https://registry.npmjs.org/{urllib.parse.quote(pkg, safe='@')}/latest")
        rep = (d or {}).get("repository")
        urls = [rep.get("url") if isinstance(rep, dict) else rep]
    else:
        info = (jget(f"https://pypi.org/pypi/{pkg}/json") or {}).get("info") or {}
        links = info.get("project_urls") or {}
        # Source/Repository links first; an "Issues" or "Changelog" link names the same repo anyway.
        urls = sorted(links.values(), key=lambda u: "/issues" in u or "/blob/" in u) + [info.get("home_page")]
    for u in urls:
        m = re.search(r"github\.com[/:]([\w.-]+)/([\w.-]+)", u or "")
        if m:
            return f"{m[1]}/{m[2].removesuffix('.git')}"
    return None


ISSUES_Q = """query($o:String!,$n:String!,$np:String!,$o90:String!,$c90:String!,$s:String!){
 repository(owner:$o,name:$n){nameWithOwner hasIssuesEnabled isArchived url
  open:issues(states:OPEN){totalCount} closed:issues(states:CLOSED){totalCount}}
 np:search(type:ISSUE,query:$np){issueCount} o90:search(type:ISSUE,query:$o90){issueCount}
 c90:search(type:ISSUE,query:$c90){issueCount}
 s:search(type:ISSUE,query:$s,first:100){nodes{... on Issue{createdAt closedAt}}}}"""
MIN_ISSUES = 10  # fewer reported issues say nothing about how they are handled


def issue_health(resolved, median_days, closed_90d, opened_90d, open_now):
    """0-100: share of issues resolved (40%), speed of fixing (40%, 14-day median = half), keeping up lately (20%).
    No fix in 12 months scores no speed while issues stay open; a repo with nothing open is neutral."""
    speed = 1 / (1 + median_days / 14) if median_days is not None else 0.0 if open_now else 0.5
    flow = min(1.0, closed_90d / opened_90d) if opened_90d else 1.0
    return round(100 * (0.4 * resolved + 0.4 * speed + 0.2 * flow))


def github_issues(repo, role, token):
    """Open vs resolved issues now, median days from report to fix (last 12 months), last 90 days' intake and closes."""
    if not token:
        return None
    today = datetime.now(timezone.utc).date()
    d90, d365 = (today - timedelta(days=90)).isoformat(), (today - timedelta(days=365)).isoformat()
    q = f"repo:{repo} is:issue"
    owner, name = repo.split("/", 1)
    body = json.dumps({"query": ISSUES_Q, "variables": {
        "o": owner, "n": name, "np": f'{q} is:closed reason:"not planned"', "o90": f"{q} created:>={d90}",
        "c90": f"{q} closed:>={d90}", "s": f"{q} is:closed reason:completed closed:>={d365} sort:updated-desc"}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body,
                                 {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read()).get("data") or {}
    except (urllib.error.URLError, ValueError, TimeoutError):
        return None
    rp = d.get("repository")
    if not rp or not rp["hasIssuesEnabled"]:
        return None
    open_, closed = rp["open"]["totalCount"], rp["closed"]["totalCount"]
    # Closed as "not planned" (wontfix, duplicate, stale bot) is not a fix; the reason exists only since 2022.
    fixed = max(0, closed - d["np"]["issueCount"])
    if open_ + fixed < MIN_ISSUES:
        return None
    days = sorted((datetime.fromisoformat(n["closedAt"][:19]) - datetime.fromisoformat(n["createdAt"][:19])).total_seconds() / 86400
                  for n in d["s"]["nodes"] if n.get("closedAt"))
    median = round(days[len(days) // 2] if len(days) % 2 else (days[len(days) // 2 - 1] + days[len(days) // 2]) / 2, 1) if days else None
    resolved = fixed / (fixed + open_)
    o90, c90 = d["o90"]["issueCount"], d["c90"]["issueCount"]
    return {"source": "github_issues", "repo": rp["nameWithOwner"], "role": role, "open": open_, "resolved": fixed,
            "not_planned": closed - fixed, "resolved_pct": round(100 * resolved), "median_days_to_fix": median,
            "fix_sample": len(days), "opened_90d": o90, "closed_90d": c90,
            "issue_health": issue_health(resolved, median, c90, o90, open_), "archived": rp["isArchived"], "url": rp["url"] + "/issues"}


# ---------- Smithery ----------

def short_name(e):
    return re.sub(r"\s*\(.*?\)|\s+(API|APIs|Platform|MCP)$", "", e["name"])


def smithery(e):
    q = urllib.parse.quote(short_name(e))
    try:
        servers = json.loads(get(f"https://registry.smithery.ai/servers?q={q}&pageSize=10"))["servers"]
    except (urllib.error.URLError, KeyError, ValueError):
        return None
    names = {norm(e["name"]), norm(short_name(e))}
    for s in servers:
        if s.get("verified") and norm(s.get("displayName", "")) in names:
            return {"source": "smithery", "uses": s.get("useCount", 0),
                    "url": f"https://smithery.ai/servers/{s['qualifiedName']}"}
    return None


# ---------- SourceForge ----------

def sf_products():
    cache = DATA / ".cache" / "sourceforge-products.txt"
    if cache.exists() and time.time() - cache.stat().st_mtime < 7 * 86400:
        return cache.read_text(encoding="utf-8").split()
    index = re.findall(r"<loc>([^<]+)</loc>", get(f"{SF}/software_sitemap.xml"))
    products = set()
    for u in index:
        products.update(re.findall(r"<loc>(https://sourceforge\.net/software/product/[^/<]+/)</loc>", get(u)))
        time.sleep(0.3)
    cache.parent.mkdir(exist_ok=True)
    cache.write_text("\n".join(sorted(products)), encoding="utf-8", newline="\n")
    return sorted(products)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


SF_TOO_BROAD = {"google", "amazon", "aws", "microsoft", "azure", "github", "gitlab", "meta", "apple"}


def sf_candidates(e, by_norm):
    # Vendor words widen the match, but not to a page for a whole company or a code host (Google, Amazon, GitHub).
    names = [e["name"], short_name(e), *(vendor_terms(e) - SF_TOO_BROAD)]
    out = []
    for n in names:
        for url in by_norm.get(norm(n), []):
            if url not in out:
                out.append(url)
    return out


def text_of(fragment):
    fragment = re.sub(r"<br\s*/?>", "\n", fragment)
    return re.sub(r"\n\s*\n\s*", "\n\n", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def sf_reviews(page_html, url):
    reviews = []
    for block in page_html.split('itemprop="review"')[1:]:
        rid = re.search(r'id="review-([0-9a-f]+)"', block)
        rating = re.search(r'itemprop="ratingValue" content="(\d)"', block)
        published = re.search(r'itemprop="datePublished" content="(\d\d)/(\d\d)/(\d{4})"', block)
        title = re.search(r'class="review-title">(.*?)</h', block, re.S)
        body = re.search(r'class="ext-review-content">(.*?)(?:<a href="#" class="link-read-more"|</div>)', block, re.S)
        if not body:
            continue
        parts = {}
        for label, txt in re.findall(r"<b>\s*([\w ]+):\s*</b>(.*?)</p>", body.group(1), re.S):
            parts[label.strip().lower()] = text_of(txt)
        if not parts:
            parts["text"] = text_of(body.group(1))
        role = re.search(r'class="ext-review-meta">\s*<div>.*?</div>\s*<div class="value-value">(.*?)</div>', block, re.S)
        size = re.search(r"Company Size:</span>\s*<span class=\"value-value\">(.*?)</span>", block)
        reviews.append({
            "id": rid.group(1) if rid else None,
            "date": f"{published.group(3)}-{published.group(1)}-{published.group(2)}" if published else None,
            "rating": int(rating.group(1)) if rating else None,
            "title": text_of(title.group(1)).strip('"') if title else None,
            **parts,
            "reviewer_role": text_of(role.group(1)) if role else None,  # job title only, no name
            "company_size": text_of(size.group(1)) if size else None,
            "url": f"{url}#review-{rid.group(1)}" if rid else url,
        })
    return reviews


def sourceforge(e, candidates, max_reviews):
    want = base_domain(e["homepage"])
    for url in candidates[:3]:
        time.sleep(SF_DELAY)
        try:
            page = get(url)
        except urllib.error.URLError:
            continue
        if want not in page:  # page must reference the vendor's own domain
            continue
        rating = re.search(r'itemprop="ratingValue">([\d.]+)<', page)
        count = (re.search(r'itemprop="reviewCount" content="(\d+)"', page)
                 or re.search(r"\((\d[\d,]*) Reviews? &(?:amp;)? Ratings\)", page))
        result = {"source": "sourceforge", "rating": float(rating.group(1)) if rating else None,
                  "reviews": int(count.group(1).replace(",", "")) if count else 0, "url": url}
        reviews = sf_reviews(page, url)
        pages = min(-(-result["reviews"] // SF_PER_PAGE), -(-max_reviews // SF_PER_PAGE))
        for n in range(2, pages + 1):
            time.sleep(SF_DELAY)
            try:
                reviews += sf_reviews(get(f"{url}?page={n}"), url)
            except urllib.error.URLError:
                break
        return result, reviews[:max_reviews]
    return None, []


# ---------- SDK downloads, Stack Overflow, App Store ----------

def vendor_terms(e):
    """Words that name the vendor: first word of the name, words in brackets, homepage domain stem (3+ letters)."""
    words = [short_name(e).split()[0], *re.findall(r"\(([^)]+)\)", e["name"]), base_domain(e["homepage"]).split(".")[0]]
    return {norm(w) for w in words if len(norm(w)) >= 3}


def jget(url, tries=3):
    for n in range(tries):
        try:
            return json.loads(get(url))
        except urllib.error.HTTPError as ex:
            if ex.code == 404:
                return None
            if ex.code == 429 and n + 1 < tries:
                time.sleep(10 * (n + 1))
                continue
            return None
        except (urllib.error.URLError, ValueError, TimeoutError):
            return None


def npm(pkg):
    d = jget(f"https://api.npmjs.org/downloads/point/last-month/{urllib.parse.quote(pkg, safe='@')}")
    if not d or "downloads" not in d:
        return None
    return {"source": "npm", "package": pkg, "downloads_month": d["downloads"], "url": f"https://www.npmjs.com/package/{pkg}"}


def pypi(pkg):
    time.sleep(1)  # pypistats asks for gentle use
    d = jget(f"https://pypistats.org/api/packages/{pkg.lower()}/recent")
    if not d or "data" not in d:
        return None
    return {"source": "pypi", "package": pkg, "downloads_month": d["data"]["last_month"], "url": f"https://pypi.org/project/{pkg}/"}


def stackoverflow(tags):
    """tag -> question count, 20 tags per request (Stack Exchange API, 300 requests/day without a key)."""
    out = {}
    for i in range(0, len(tags), 20):
        part = ";".join(urllib.parse.quote(t) for t in tags[i:i + 20])
        d = jget(f"https://api.stackexchange.com/2.3/tags/{part}/info?site=stackoverflow&pagesize=100")
        for it in (d or {}).get("items", []):
            out[it["name"]] = {"count": it["count"]}
        time.sleep(1)
        w = jget(f"https://api.stackexchange.com/2.3/tags/{part}/wikis?site=stackoverflow&pagesize=100")
        for it in (w or {}).get("items", []):
            if it["tag_name"] in out:
                out[it["tag_name"]]["excerpt"] = it.get("excerpt") or ""
        time.sleep(1)
    return out


def appstore(ids):
    """app id -> rating summary (Apple iTunes Lookup API, many ids per request)."""
    out = {}
    for i in range(0, len(ids), 50):
        d = jget("https://itunes.apple.com/lookup?id=" + ",".join(str(x) for x in ids[i:i + 50]))
        for a in (d or {}).get("results", []):
            if a.get("userRatingCount"):
                out[str(a["trackId"])] = {"seller": (a.get("sellerUrl") or "") + " " + (a.get("artistName") or ""),
                                          "source": "appstore", "app": a["trackName"], "rating": round(a["averageUserRating"], 2),
                                          "ratings": a["userRatingCount"], "url": a["trackViewUrl"].split("?")[0]}
        time.sleep(1)
    return out


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated entry ids")
    ap.add_argument("--reviews", type=int, default=100, help="max review texts per entry")
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: github,github_issues,smithery,sourceforge,npm,pypi,stackoverflow,appstore")
    args = ap.parse_args()
    skip = set(filter(None, args.skip.split(",")))

    catalog = json.loads((DATA / "catalog.json").read_text(encoding="utf-8"))
    if args.only:
        ids = set(args.only.split(","))
        catalog = [e for e in catalog if e["id"] in ids]
    out_file = DATA / "ratings.json"
    ratings = json.loads(out_file.read_text(encoding="utf-8")) if out_file.exists() else {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")  # fetched_at: UTC timestamp
    fresh = {e["id"]: [] for e in catalog}
    ids_file = DATA / "popularity-ids.json"
    pop = json.loads(ids_file.read_text(encoding="utf-8")) if ids_file.exists() else {}

    if "github" not in skip:
        token = github_token()
        jobs = [(e["id"], r) for e in catalog for r in repos_of(e)]
        with ThreadPoolExecutor(8) as pool:
            for (eid, _), res in zip(jobs, pool.map(lambda j: github(j[1], token), jobs)):
                if res:
                    fresh[eid].append(res)
        print(f"github: {sum(1 for v in fresh.values() for x in v if x['source'] == 'github')} repos", flush=True)

    if "smithery" not in skip:
        with ThreadPoolExecutor(4) as pool:
            for e, res in zip(catalog, pool.map(smithery, catalog)):
                if res:
                    fresh[e["id"]].append(res)
        print(f"smithery: {sum(1 for v in fresh.values() for x in v if x['source'] == 'smithery')} servers", flush=True)

    if "sourceforge" not in skip:
        by_norm = {}
        for url in sf_products():
            by_norm.setdefault(norm(urllib.parse.unquote(url.rstrip("/").rsplit("/", 1)[1])), []).append(url)
        reviews_dir = ROOT / "catalog" / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)
        found = 0
        for i, e in enumerate(catalog, 1):
            known = (pop.get(e["id"]) or {}).get("sourceforge_url")
            res, reviews = sourceforge(e, ([known] if known else []) + sf_candidates(e, by_norm), args.reviews)
            if res and res["rating"]:  # a listing without any rating proves nothing
                found += 1
                fresh[e["id"]].append(res)
                if reviews:
                    (reviews_dir / f"{e['id']}.json").write_text(json.dumps(
                        {"id": e["id"], "source": "sourceforge", "url": res["url"], "fetched_at": now,
                         "rating": res["rating"], "reviews_total": res["reviews"], "reviews": reviews},
                        ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
                print(f"  [{i}/{len(catalog)}] {e['id']}: {res['rating']} / {res['reviews']} reviews, {len(reviews)} texts", flush=True)
        print(f"sourceforge: {found} products", flush=True)

    for src, fetch in (("npm", npm), ("pypi", pypi)):
        if src in skip:
            continue
        jobs = [(e["id"], p) for e in catalog for p in (pop.get(e["id"]) or {}).get(src) or []]
        with ThreadPoolExecutor(4 if src == "npm" else 1) as pool:
            for (eid, _), res in zip(jobs, pool.map(lambda j: fetch(j[1]), jobs)):
                if res:
                    fresh[eid].append(res)
        print(f"{src}: {sum(1 for v in fresh.values() for x in v if x['source'] == src)} of {len(jobs)} packages", flush=True)

    if "github_issues" not in skip:
        token = github_token()
        jobs, seen = [], {}
        for e in catalog:
            mcp_url = (e.get("mcp") or {}).get("url") or ""
            mine = [(r, "mcp" if r.lower() in mcp_url.lower() else "spec" if r.lower() in (e.get("openapi") or "").lower() else "repo")
                    for r in repos_of(e)]
            for reg in ("npm", "pypi"):
                for pkg in (pop.get(e["id"]) or {}).get(reg) or []:
                    if (reg, pkg) not in seen:
                        seen[(reg, pkg)] = sdk_repo(reg, pkg)
                    r = seen[(reg, pkg)]
                    if r and all(r.lower() != m[0].lower() for m in mine):
                        mine.append((r, "sdk"))
            jobs += [(e["id"], r, role) for r, role in mine]
        stats = {}
        for _, r, role in jobs:  # sequential: GraphQL search has a secondary rate limit
            if r.lower() not in stats:
                stats[r.lower()] = github_issues(r, role, token)
                time.sleep(0.5)
        for eid, r, role in jobs:
            if stats[r.lower()]:
                fresh[eid].append({**stats[r.lower()], "role": role})
        print(f"github_issues: {sum(1 for v in fresh.values() for x in v if x['source'] == 'github_issues')} repos "
              f"({sum(1 for v in stats.values() if v)} distinct of {len(stats)})", flush=True)

    # One SDK or repo can serve several entries (openai for chat, images and audio; awslabs/mcp for many AWS services):
    # name the others, so a count is not read as per-entry.
    key = lambda x: (x["source"], x["package"]) if x["source"] in ("npm", "pypi") else (x["source"], x["repo"].lower())  # noqa: E731
    users = {}
    for eid, items in fresh.items():
        for x in items:
            if x["source"] in ("npm", "pypi", "github_issues"):
                users.setdefault(key(x), []).append(eid)
    for eid, items in fresh.items():
        for x in items:
            if x["source"] in ("npm", "pypi", "github_issues") and len(users[key(x)]) > 1:
                x["shared_with"] = [i for i in users[key(x)] if i != eid]

    if "stackoverflow" not in skip:
        tags = {e["id"]: pop[e["id"]]["stackoverflow_tag"] for e in catalog if (pop.get(e["id"]) or {}).get("stackoverflow_tag")}
        counts = stackoverflow(sorted(set(tags.values())))
        for eid, tag in tags.items():
            e = next(x for x in catalog if x["id"] == eid)
            c = counts.get(tag) or {}
            # The tag wiki must name the product, so a generic tag (playwright, rest) does not count.
            if c.get("count") and any(t in norm(c.get("excerpt", "")) or t in norm(tag) for t in vendor_terms(e)):
                fresh[eid].append({"source": "stackoverflow", "tag": tag, "questions": c["count"],
                                   "url": f"https://stackoverflow.com/questions/tagged/{urllib.parse.quote(tag)}"})
        print(f"stackoverflow: {sum(1 for v in fresh.values() for x in v if x['source'] == 'stackoverflow')} of {len(tags)} tags", flush=True)

    if "appstore" not in skip:
        apps = {e["id"]: str(pop[e["id"]]["ios_app_id"]) for e in catalog if (pop.get(e["id"]) or {}).get("ios_app_id")}
        found = appstore(sorted(set(apps.values())))
        for eid, app in apps.items():
            e = next(x for x in catalog if x["id"] == eid)
            hit = dict(found.get(app) or {})
            seller = hit.pop("seller", "").lower()
            # The app must be published by the vendor: seller URL on its domain, or seller name = vendor name.
            if hit and (base_domain(e["homepage"]) in seller or any(t in norm(seller) for t in vendor_terms(e))):
                fresh[eid].append(hit)
        print(f"appstore: {sum(1 for v in fresh.values() for x in v if x['source'] == 'appstore')} of {len(apps)} apps", flush=True)

    for eid, items in fresh.items():
        kept = [x for x in ratings.get(eid, []) if x["source"] in skip]
        for x in items:
            x["fetched_at"] = now
        if kept or items:
            ratings[eid] = kept + items
        else:
            ratings.pop(eid, None)
    out_file.write_text(json.dumps(dict(sorted(ratings.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_file.relative_to(ROOT)}: {len(ratings)} entries with signals")


if __name__ == "__main__":
    main()
