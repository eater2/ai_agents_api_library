"""Fetch public ratings, review counts and usage signals for catalog entries.

Sources (only ones that allow automated access):
  github       stars, forks, last push of repos referenced by the entry (REST API, GITHUB_TOKEN)
  smithery     use count of the verified Smithery server with the same name (public registry API)
  sourceforge  rating, review count and review texts from sourceforge.net/software/product/<slug>/
               (allowed by robots.txt; product slugs come from its sitemap; a match must link the
               entry's homepage domain)

G2, Capterra, GetApp and Product Hunt block automated clients, so they are not fetched.

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
from datetime import datetime, timezone
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
    cache.write_text("\n".join(sorted(products)), encoding="utf-8")
    return sorted(products)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def sf_candidates(e, by_norm):
    names = [e["name"], short_name(e)]
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


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated entry ids")
    ap.add_argument("--reviews", type=int, default=100, help="max review texts per entry")
    ap.add_argument("--skip", default="", help="comma-separated sources to skip: github,smithery,sourceforge")
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
            res, reviews = sourceforge(e, sf_candidates(e, by_norm), args.reviews)
            if res and res["rating"]:  # a listing without any rating proves nothing
                found += 1
                fresh[e["id"]].append(res)
                if reviews:
                    (reviews_dir / f"{e['id']}.json").write_text(json.dumps(
                        {"id": e["id"], "source": "sourceforge", "url": res["url"], "fetched_at": now,
                         "rating": res["rating"], "reviews_total": res["reviews"], "reviews": reviews},
                        ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"  [{i}/{len(catalog)}] {e['id']}: {res['rating']} / {res['reviews']} reviews, {len(reviews)} texts", flush=True)
        print(f"sourceforge: {found} products", flush=True)

    for eid, items in fresh.items():
        kept = [x for x in ratings.get(eid, []) if x["source"] in skip]
        for x in items:
            x["fetched_at"] = now
        if kept or items:
            ratings[eid] = kept + items
        else:
            ratings.pop(eid, None)
    out_file.write_text(json.dumps(dict(sorted(ratings.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out_file.relative_to(ROOT)}: {len(ratings)} entries with signals")


if __name__ == "__main__":
    main()
