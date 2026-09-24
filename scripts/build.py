"""Generate every published file from data/*.json.

    python scripts/build.py

Inputs : data/catalog.json, data/categories.json, data/directories.json
Outputs: README.md, README.pl.md, llms.txt, llms-full.txt, catalog/*.json,
         docs/index.html, docs/pl/index.html, docs/catalog.json, docs/llms.txt,
         docs/robots.txt, docs/sitemap.xml
"""
import base64
import hashlib
import html
import io
import json
import zipfile
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlparse

REPO = "eater2/ai_agents_api_library"
BRANCH = "main"
TITLE = "AI Agents Accessible APIs"
PAGES = f"https://{REPO.split('/')[0]}.github.io/{REPO.split('/')[1]}/"
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/"
GH = f"https://github.com/{REPO}"

MCP_URL = "https://ai-agents-api-library.vercel.app/mcp"
SMITHERY = "https://smithery.ai/servers/eater2/ai-agents-api-library"
REGISTRY = "https://registry.modelcontextprotocol.io/v0/servers?search=io.github.eater2/ai-agents-api-library"


def badges():
    """Listings as proof under the title: (alt, image, link). Smithery's own badge endpoint returns 500, so shields.io + its logo."""
    sm = base64.b64encode((ROOT / "scripts/logos/smithery.svg").read_bytes()).decode()
    sh = "https://img.shields.io/badge/"
    return [
        ("Official MCP Registry", sh + "MCP_Registry-io.github.eater2%2Fai--agents--api--library-0A66C2?logo=modelcontextprotocol&logoColor=white", REGISTRY),
        ("Smithery", sh + "Smithery-eater2%2Fai--agents--api--library-FF5601?logo=data:image/svg%2bxml;base64," + quote(sm), SMITHERY),
        ("Claude Code plugin", sh + "Claude_Code-plugin-D97757?logo=claude&logoColor=white", GH + "#claude-skill-and-plugin"),
        ("Remote MCP endpoint", sh + "remote_MCP-no_key-000000?logo=vercel&logoColor=white", GH + "#mcp-server"),
    ]
STALE_DAYS = 90
MAX_CATEGORY_BYTES = 60 * 1024  # ~15k tokens; compact JSON (one entry per line) since call/unit_price were added

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SOURCES = [
    ("GetStream — AI Agent Tools Catalog", "https://github.com/GetStream/ai-agent-tools-catalog"),
    ("StackOne — AI Agent Tools Landscape 2026", "https://www.stackone.com/blog/ai-agent-tools-landscape-2026/"),
    ("Mastra — Best AI agent search tools", "https://mastra.ai/articles/best-ai-agent-search-tools"),
    ("abitwise — AI-tools", "https://github.com/abitwise/AI-tools"),
    ("Sylus — Top-rated connectors for AI tool integrations", "https://www.sylus.ai/feeds/blog/top-rated-connectors-ai-tool-integrations"),
]

T = {
    "en": {
        "lang_name": "English", "other": "pl", "other_label": "Polski",
        "readme": "README.md", "other_readme": "README.pl.md",
        "tagline": "A curated, machine-readable encyclopedia of third-party APIs and MCP servers that AI agents can call on a user's behalf.",
        "hatnote": "This article is about services an AI agent can operate programmatically, not AI products used by humans through a web UI.",
        "lead": (
            "**{title}** is an open, bilingual (English/Polish) catalog of **{n} services** (each with a last-checked date) in **{c} categories** "
            "that an autonomous AI agent — such as Claude, ChatGPT, Gemini or a custom LLM agent — can use "
            "**without a human in the loop**, after a one-time human step: registering an account and handing the agent "
            "an **API key**, an **OAuth token**, or a connection to an **MCP (Model Context Protocol) server**. "
            "Every entry records the documentation URL, the authentication method, the availability of an official or community MCP server, "
            "and the free tier. The list is not a directory of products with “AI” in their name; the criterion is agent operability, not branding."
        ),
        "infobox": [("Type", "API & MCP catalog"), ("Entries", "{n}"), ("Categories", "{c}"), ("Official MCP servers", "{mcp}"),
                    ("Languages", "English, Polish"), ("Format", "JSON, Markdown, HTML, llms.txt"), ("Last checked", "{date}"), ("License", "CC BY 4.0 (data), MIT (code)")],
        "contents": "Contents",
        "h_agents": "Machine-readable access (for AI agents)",
        "agents_intro": "AI agents should not parse this page. Fetch one of these stable files instead:",
        "files_head": "| File | Raw URL |",
        "files": [
            ("llms.txt", "short index for LLMs, links to everything below"),
            ("llms-full.txt", "the whole catalog as compact plain text, one line per service"),
            ("catalog/all.json", "full catalog, one JSON array"),
            ("catalog/&lt;category&gt;.json", "one file per category, for small context windows"),
            ("data/schema.json", "JSON Schema of an entry"),
        ],
        "agents_recipe": "Recommended agent workflow: (1) pick the category file, (2) filter by `auth` and `mcp.type`, (3) read `docs` (or `llms_txt` / `openapi` when present), (4) ask the user for the credential named in `auth_hint`.",
        "h_criteria": "Inclusion criteria",
        "criteria": [
            "The service exposes a **public, self-serve** programmatic interface (REST, GraphQL, SDK) **or** an MCP server.",
            "A human needs to act **at most once** — sign up and create a key or approve OAuth. After that the agent works unattended.",
            "The interface is **documented** and **currently active** (links last checked on the date shown in the infobox).",
            "Consumer-only apps, waitlists, sales-gated enterprise products, agent frameworks and IDEs are **excluded** — they are agents or tools for building agents, not services an agent calls.",
        ],
        "h_legend": "Legend",
        "legend": [("MCP ✅", "official MCP server maintained by the vendor"), ("MCP ◐", "community-maintained MCP server"),
                   ("MCP —", "no MCP server known; use the REST API"), ("🆓", "free tier or free usage without payment"),
                   ("★ (date)", "proof under the service name: SourceForge rating and review count, GitHub stars, Smithery uses — linked, with the date fetched")],
        "cols": ["Service", "What an agent can do", "Auth", "MCP", "Free tier", "Docs"],
        "h_directories": "Related directories and registries",
        "directories_intro": "Other machine-readable sources agents can use to discover tools:",
        "h_contrib": "Contributing",
        "contrib": "Edit only the files in `data/` (usually `data/catalog.json`), run `python scripts/build.py` to regenerate the English, Polish and LLM files, and open a pull request. Every new entry must link to the vendor's official API documentation. Step-by-step guide: `CONTRIBUTING.md`.",
        "h_sources": "References",
        "sources_intro": "The initial candidate list was compiled from:",
        "h_see": "See also",
        "see": [("Model Context Protocol", "https://modelcontextprotocol.io"), ("Official MCP Registry", "https://registry.modelcontextprotocol.io"),
                ("llms.txt proposal", "https://llmstxt.org")],
        "auth": {"api_key": "API key", "oauth2": "OAuth 2.0", "api_key+oauth2": "API key / OAuth", "none": "none", "cloud_iam": "cloud IAM"},
        "docs": "docs", "reason": "reason", "count": "{n} services",
        "filter": "Filter services…", "mcp_only": "MCP only", "free_only": "free tier only",
        "footer": "Generated from data/catalog.json on {date}.",
    },
    "pl": {
        "lang_name": "Polski", "other": "en", "other_label": "English",
        "readme": "README.pl.md", "other_readme": "README.md",
        "tagline": "Wyselekcjonowana, czytelna maszynowo encyklopedia zewnętrznych API i serwerów MCP, z których agenci AI mogą korzystać w imieniu użytkownika.",
        "hatnote": "Ten artykuł dotyczy usług, które agent AI może obsługiwać programowo, a nie produktów AI używanych przez ludzi przez interfejs WWW.",
        "lead": (
            "**{title}** (pol. *API dostępne dla agentów AI*) to otwarty, dwujęzyczny (angielski/polski) katalog **{n} usług** (każda z datą ostatniego sprawdzenia) "
            "w **{c} kategoriach**, z których autonomiczny agent AI — np. Claude, ChatGPT, Gemini lub własny agent LLM — może korzystać "
            "**bez udziału człowieka**, po jednorazowym kroku wykonanym przez człowieka: rejestracji konta i przekazaniu agentowi "
            "**klucza API**, **tokenu OAuth** lub połączenia z **serwerem MCP (Model Context Protocol)**. "
            "Każdy wpis zawiera adres dokumentacji, metodę uwierzytelniania, dostępność oficjalnego lub społecznościowego serwera MCP "
            "oraz darmowy limit. Nie jest to spis produktów z „AI” w nazwie — kryterium jest możliwość obsługi przez agenta, a nie marketing."
        ),
        "infobox": [("Typ", "katalog API i MCP"), ("Wpisy", "{n}"), ("Kategorie", "{c}"), ("Oficjalne serwery MCP", "{mcp}"),
                    ("Języki", "angielski, polski"), ("Format", "JSON, Markdown, HTML, llms.txt"), ("Ostatnie sprawdzenie", "{date}"), ("Licencja", "CC BY 4.0 (dane), MIT (kod)")],
        "contents": "Spis treści",
        "h_agents": "Dostęp maszynowy (dla agentów AI)",
        "agents_intro": "Agenci AI nie powinni parsować tej strony. Zamiast tego należy pobrać jeden ze stałych plików:",
        "files_head": "| Plik | Adres (raw) |",
        "files": [
            ("llms.txt", "krótki indeks dla LLM z odnośnikami do poniższych plików"),
            ("llms-full.txt", "cały katalog jako zwięzły tekst, jedna linia na usługę"),
            ("data/catalog.json", "pełny katalog jako jedna tablica JSON"),
            ("catalog/&lt;kategoria&gt;.json", "osobny plik dla każdej kategorii (małe okno kontekstu)"),
            ("data/schema.json", "JSON Schema pojedynczego wpisu"),
        ],
        "agents_recipe": "Zalecany sposób pracy agenta: (1) wybierz plik kategorii, (2) filtruj po `auth` i `mcp.type`, (3) przeczytaj `docs` (lub `llms_txt` / `openapi`, jeśli są), (4) poproś użytkownika o dane uwierzytelniające wskazane w `auth_hint`.",
        "h_criteria": "Kryteria włączenia",
        "criteria": [
            "Usługa udostępnia **publiczny, samoobsługowy** interfejs programowy (REST, GraphQL, SDK) **lub** serwer MCP.",
            "Człowiek musi działać **najwyżej raz** — założyć konto i wygenerować klucz lub zatwierdzić OAuth. Potem agent działa samodzielnie.",
            "Interfejs jest **udokumentowany** i **aktywny** (linki sprawdzono w dniu podanym w infoboksie).",
            "Aplikacje wyłącznie konsumenckie, listy oczekujących, produkty dostępne tylko przez dział sprzedaży, frameworki agentów i IDE są **wykluczone** — to agenci lub narzędzia do ich budowy, a nie usługi wywoływane przez agenta.",
        ],
        "h_legend": "Legenda",
        "legend": [("MCP ✅", "oficjalny serwer MCP utrzymywany przez dostawcę"), ("MCP ◐", "serwer MCP utrzymywany przez społeczność"),
                   ("MCP —", "brak znanego serwera MCP; należy użyć REST API"), ("🆓", "darmowy limit lub użycie bez opłat"),
                   ("★ (data)", "dowód pod nazwą usługi: ocena i liczba opinii z SourceForge, gwiazdki GitHub, użycia w Smithery — z linkiem i datą pobrania")],
        "cols": ["Usługa", "Co agent może zrobić", "Autoryzacja", "MCP", "Darmowy limit", "Dokumentacja"],
        "h_directories": "Powiązane katalogi i rejestry",
        "directories_intro": "Inne czytelne maszynowo źródła, w których agenci mogą wyszukiwać narzędzia:",
        "h_contrib": "Współtworzenie",
        "contrib": "Edytuj tylko pliki w `data/` (zwykle `data/catalog.json`), uruchom `python scripts/build.py`, który odtworzy wersję angielską, polską i pliki dla LLM, i otwórz pull request. Każdy nowy wpis musi wskazywać oficjalną dokumentację API dostawcy. Instrukcja krok po kroku: `CONTRIBUTING.pl.md`.",
        "h_sources": "Przypisy",
        "sources_intro": "Początkowa lista kandydatów została zebrana z:",
        "h_see": "Zobacz też",
        "see": [("Model Context Protocol", "https://modelcontextprotocol.io"), ("Oficjalny rejestr MCP", "https://registry.modelcontextprotocol.io"),
                ("Propozycja llms.txt", "https://llmstxt.org")],
        "auth": {"api_key": "klucz API", "oauth2": "OAuth 2.0", "api_key+oauth2": "klucz API / OAuth", "none": "brak", "cloud_iam": "IAM chmury"},
        "docs": "dokumentacja", "reason": "powód", "count": "{n} usług",
        "filter": "Filtruj usługi…", "mcp_only": "tylko MCP", "free_only": "tylko darmowe",
        "footer": "Wygenerowano z data/catalog.json dnia {date}.",
    },
}


def slug(s):
    s = s.lower()
    for a, b in zip("ąćęłńóśźż", "acelnoszz"):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def gh_slug(s):
    """Anchor GitHub generates for a Markdown heading (keeps non-ASCII letters)."""
    return re.sub(r"[^\w\- ]", "", s.lower()).replace(" ", "-")


def load():
    cats = json.loads((DATA / "categories.json").read_text("utf-8"))
    items = json.loads((DATA / "catalog.json").read_text("utf-8"))
    dirs = json.loads((DATA / "directories.json").read_text("utf-8"))
    order = {c["id"]: i for i, c in enumerate(cats)}
    items.sort(key=lambda e: (order[e["category"]], e["name"].lower()))
    return cats, items, dirs


def is_free(e):
    # The researched free_plan.kind wins over parsing the free_tier text (which read "free trial…" as a free tier).
    kind = (e.get("free_plan") or {}).get("kind")
    if kind:
        return kind in ("free_tier", "no_key")
    f = (e.get("free_tier") or "").lower()
    if f.startswith("unavailable"):
        return False
    if re.match(r"free[- ]trial|trial\b", f):
        return False
    recurring = re.search(r"/(day|mo|month|year)\b|per (day|month)|monthly|daily|always free|perpetual", f)
    if f.startswith(("no key", "free")) or re.search(r"free [\w ]*/(day|mo|month)\b", f):
        return True
    # One-off signup credits ("50 signup credits", "valid 30 days", "one-time") are a trial, not a free tier.
    if not recurring and re.search(r"sign[- ]?up|on sign|one[- ]time|valid \d+ days|first \d+ days|after account verification", f):
        return False
    if not f or f.startswith(("paid", "no ", "check pricing", "requires")):
        return False
    return not any(w in f for w in ("paid only", "no free", "no permanent free", "no confirmed free", "free plan retired", "trial"))


def is_trial(e):
    """No lasting free tier, but one-off trial credits to test without paying."""
    kind = (e.get("free_plan") or {}).get("kind")
    if kind:
        return kind == "trial"
    f = (e.get("free_tier") or "").lower()
    if f.startswith("unavailable"):
        return False
    one_off = re.search(r"trial|sign[- ]?up|on sign|one[- ]time|valid \d+ days|after account verification", f)
    return not is_free(e) and bool(one_off) and "no free-plan" not in f


RATINGS = {}  # id -> list of signals from data/ratings.json (scripts/fetch_ratings.py)
OPERATIONS = json.loads((DATA / "operations.json").read_text("utf-8"))  # id -> definition; vocabulary of the operations field
SOURCE_NAMES = {"sourceforge": "SourceForge", "github": "GitHub", "smithery": "Smithery"}


def short_count(n):
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.1f}k" if n >= 1e4 else f"{n:,}"


def proof_items(e):
    """(label, url, fetched_at) per signal, e.g. ("SourceForge 4.6★/250 reviews", url, "2026-09-24")."""
    out = []
    for r in RATINGS.get(e["id"], []):
        src = SOURCE_NAMES.get(r["source"], r["source"])
        if r["source"] == "sourceforge" and r.get("reviews"):
            label = f"{src} {r['rating']}★/{short_count(r['reviews'])} review{'s' if r['reviews'] > 1 else ''}"
        elif r["source"] == "github":
            label = f"{src} {short_count(r['stars'])}★ {r['repo']}"
        elif r["source"] == "smithery" and r.get("uses"):
            label = f"{src} {short_count(r['uses'])} uses"
        else:
            continue
        out.append((label, r["url"], r["fetched_at"]))
    return out


def stamp(ts):
    """'2026-09-24T17:05Z' -> '2026-09-24 17:05 UTC'; a bare date stays as is."""
    return ts.replace("T", " ").replace("Z", " UTC")


def proof_html(e):
    return "".join(f'<br><small class="proof"><a href="{html.escape(u)}">{html.escape(l)}</a> '
                   f'<time datetime="{d}">({stamp(d)})</time></small>' for l, u, d in proof_items(e))


def ratings_note(lang):
    """Line above the tables: when the ratings were fetched (newest and oldest timestamp)."""
    ts = sorted({r["fetched_at"] for rs in RATINGS.values() for r in rs})
    if not ts:
        return ""
    span = stamp(ts[-1]) if ts[0] == ts[-1] else f"{stamp(ts[0])} – {stamp(ts[-1])}"
    text = {"en": "Ratings and usage (★) fetched", "pl": "Oceny i użycie (★) pobrane"}[lang]
    return f'<p class="proof-note">{text}: <time datetime="{ts[-1]}">{span}</time>.</p>'


def base_domain(url):
    host = urlparse(url or "").netloc.lower().split(":")[0]
    parts = host.removeprefix("www.").split(".")
    # keep three labels for second-level country domains such as example.co.uk
    return ".".join(parts[-3:] if len(parts) > 2 and len(parts[-2]) <= 3 and len(parts[-1]) == 2 else parts[-2:])


def mcp_details(e):
    """Derived MCP fields for agents: kind (vendor-hosted / official / community / none) and domain_verified,
    true when the hosted endpoint is on the vendor's own domain (homepage or docs)."""
    m = dict(e.get("mcp") or {})
    remote = m.get("remote_url")
    url = m.get("url") or ""
    if not remote and url.startswith("https://") and "github.com" not in url and re.search(r"mcp|/sse", url):
        remote = url  # entries not yet researched: url that looks like a hosted endpoint
    vendor = m.get("maintainer") == "vendor" or m.get("type") == "official"
    own = {base_domain(e.get("homepage")), base_domain(e.get("docs"))} - {""}
    m["domain_verified"] = base_domain(remote) in own if remote else None
    if m.get("type") == "none" and m.get("maintainer") in (None, "none"):
        m["kind"] = "none"
    elif vendor and remote and m["domain_verified"]:
        m["kind"] = "vendor-hosted"
    elif vendor:
        m["kind"] = "official"
    else:
        m["kind"] = "community"
    return m


def mcp_config(e, m, usage):
    """Connection snippet for the MCP server: researched (data/usage.json) or derived from a hosted endpoint."""
    if "mcp_config" in usage:
        return usage["mcp_config"]
    remote = m.get("remote_url") or (m.get("url") if m.get("domain_verified") is not None else None)
    if not remote:
        return None
    return {"transport": "sse" if re.search(r"/sse/?$", remote) else "streamable-http", "url": remote,
            "derived": True}  # from the endpoint URL only: auth (OAuth or header) not researched yet


def load_usage(ids):
    """data/usage.json: per-entry `call`, `unit_price`, `mcp_config`, `mcp_issue` (see data/schema.json)."""
    f = DATA / "usage.json"
    usage = json.loads(f.read_text("utf-8")) if f.exists() else {}
    for eid, u in usage.items():
        assert eid in ids, f"data/usage.json: unknown id {eid}"
        assert set(u) <= {"call", "unit_price", "mcp_config", "mcp_issue"}, f"data/usage.json {eid}: {set(u)}"
        c = u.get("call")
        if c:
            assert c.get("method") and re.match(r"https?://|\{", c.get("url", "")) and c.get("example") and c.get("source_url"), f"usage {eid}: call"
        mc = u.get("mcp_config")
        if mc:
            assert mc.get("transport") in ("streamable-http", "sse", "stdio", None), f"usage {eid}: transport"
            assert mc.get("url") or mc.get("command"), f"usage {eid}: url or command"
    return usage


def details_items(e):
    """(label, text, source_url) for the researched structured fields."""
    out = []
    if e.get("base_url"):
        out.append(("Base URL", e["base_url"], None))
    fp = e.get("free_plan") or {}
    if fp.get("quota") or fp.get("kind"):
        bits = [fp.get("quota") or fp.get("kind")]
        if fp.get("period") and fp["period"] not in (fp.get("quota") or ""):
            bits.append(f"per {fp['period']}" if fp["period"] != "one_time" else "one-time")
        if fp.get("requires_card") is not None:
            bits.append("card required" if fp["requires_card"] else "no card")
        if fp.get("watermark"):
            bits.append("watermarked")
        out.append(("Free plan", ", ".join(bits), fp.get("source_url")))
    for key, label in (("rate_limits", "Rate limits"), ("data_policy", "Data policy")):
        if (e.get(key) or {}).get("summary"):
            out.append((label, e[key]["summary"], e[key].get("source_url")))
    aj = e.get("async_jobs") or {}
    if aj.get("value"):
        out.append(("Async jobs", aj.get("how") or "yes", aj.get("source_url")))
    sc = (e.get("oauth_scopes") or {}).get("scopes")
    if sc:
        out.append(("OAuth scopes", ", ".join(sc[:8]), e["oauth_scopes"].get("source_url")))
    u = USAGE.get(e.get("id"), {})
    if u.get("call"):
        out.append(("Example call", f"{u['call'].get('operation', '')}: {u['call']['method']} {u['call']['url']}".lstrip(": "), u["call"].get("source_url")))
    if u.get("unit_price"):
        out.append(("Unit price", u["unit_price"]["summary"], u["unit_price"].get("source_url")))
    if (u.get("mcp_config") or {}).get("docs_only"):
        out.append(("MCP", "docs-only: the server searches documentation, it cannot call the API", u["mcp_config"].get("source_url")))
    tools = (e.get("mcp") or {}).get("tools")
    if tools:
        out.append(("MCP tools", f"{len(tools)}: " + ", ".join(tools[:6]) + (" …" if len(tools) > 6 else ""), (e.get("mcp") or {}).get("source_url")))
    return out


def details_html(e):
    rows = []
    for label, text, src in details_items(e):
        link = f' <a href="{html.escape(src)}" title="source">↗</a>' if src else ""
        rows.append(f"<b>{html.escape(label)}:</b> {html.escape(text)}{link}")
    return "<br>".join(rows) or "—"


def mcp_mark(e, fmt="md"):
    m = e.get("mcp") or {}
    sym = {"official": "✅", "community": "◐"}.get(m.get("type"), "—")
    if m.get("url") and sym != "—":
        return f"[{sym}]({m['url']})" if fmt == "md" else f'<a href="{html.escape(m["url"])}">{sym}</a>'
    return sym


def md_cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def stats(cats, items):
    return dict(n=len(items), c=len(cats), mcp=sum(1 for e in items if (e.get("mcp") or {}).get("type") == "official"),
                date=VERIFIED, title=TITLE)


# ---------------------------------------------------------------- Markdown

def readme(lang, cats, items, dirs):
    t = T[lang]
    st = stats(cats, items)
    by = {c["id"]: [e for e in items if e["category"] == c["id"]] for c in cats}
    o = []
    o.append(f'<p align="right"><a href="{t["other_readme"]}">{t["other_label"]}</a> · <a href="{PAGES}">HTML</a> · '
             f'<a href="llms.txt">llms.txt</a> · <a href="catalog/all.json">catalog.json</a></p>\n')
    o.append(f"# {TITLE}\n")
    o.append(" ".join(f'<a href="{u}"><img alt="{a}" src="{i}"></a>' for a, i, u in badges()) + "\n")
    o.append(f"<em>{t['tagline']}</em>\n")
    o.append("> " + t["hatnote"] + "\n")
    o.append('<table align="right" width="300">')
    o.append(f'<tr><th colspan="2" align="center">{TITLE}</th></tr>')
    for k, v in t["infobox"]:
        o.append(f"<tr><td><b>{k}</b></td><td>{v.format(**st)}</td></tr>")
    o.append("</table>\n")
    o.append(t["lead"].format(**st) + "\n")

    o.append(f"## {t['contents']}\n")
    toc = ([t["h_agents"]] if lang == "en" else []) + [t["h_criteria"], t["h_legend"]]
    lines = [f"{i}. [{h}](#{gh_slug(h)})" for i, h in enumerate(toc, 1)]
    lines.append(f"{len(lines)+1}. " + " · ".join(f"[{c[lang]}](#{gh_slug(c[lang])}) ({len(by[c['id']])})" for c in cats))
    for h in (t["h_directories"], t["h_contrib"], t["h_see"], t["h_sources"]):
        lines.append(f"{len(lines)+1}. [{h}](#{gh_slug(h)})")
    o.append("\n".join(lines) + "\n")

    if lang == "en":
        o.append(f"## {t['h_agents']}\n\n{t['agents_intro']}\n")
        o.append(t["files_head"] + "\n|---|---|")
        for f, d in t["files"]:
            path = f.replace("&lt;", "<").replace("&gt;", ">")
            url = RAW + path if "<" not in path else RAW + "catalog/"
            o.append(f"| `{path}` — {d} | {url} |")
        o.append(f"\n{t['agents_recipe']}\n")
        o.append("### MCP server\n\nThe catalog is also an MCP server with four tools: `search_apis` (filters: `query`, `category`, "
                 "`mcp` (official/remote/any), `no_auth`, `free_tier`, `no_card`, `auth`), `get_api`, `get_reviews` (user reviews with pros and cons) and `list_categories`. No key needed. Add it to your MCP client:\n")
        o.append('```json\n{\n  "mcpServers": {\n    "ai-agents-api-library": {\n      "command": "npx",\n'
                 f'      "args": ["-y", "github:{REPO}"]\n    }}\n  }}\n}}\n```\n')
        o.append(f"Claude Code: `claude mcp add ai-agents-api-library -- npx -y github:{REPO}`\n")
        o.append(f"No install: remote endpoint (Streamable HTTP, no key) `{MCP_URL}`, e.g. "
                 f"`claude mcp add --transport http ai-agents-api-library {MCP_URL}`. "
                 "Listed in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=ai-agents-api-library) "
                 "as `io.github.eater2/ai-agents-api-library`.\n")
        o.append("### Claude skill and plugin\n\nThe skill tells Claude when to reach for the catalog and how to pick a service. "
                 "The plugin bundles the skill with the MCP server:\n")
        o.append(f"- **Claude Code plugin** (skill + MCP server):\n  ```\n  /plugin marketplace add {REPO}\n"
                 "  /plugin install ai-agents-api-library@eater2\n  ```")
        o.append("- **Skill only, Claude Code:** copy [`skills/ai-agents-api-library/`](skills/ai-agents-api-library/SKILL.md) "
                 "to `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).")
        o.append(f"- **Skill only, claude.ai / Claude Desktop:** download [the skill zip]({PAGES}ai-agents-api-library-skill.zip) "
                 "and upload it under Settings → Capabilities → Skills.\n")

    o.append(f"## {t['h_criteria']}\n")
    o.append("\n".join(f"- {x}" for x in t["criteria"]) + "\n")
    o.append(f"## {t['h_legend']}\n")
    o.append("\n".join(f"- **{a}** — {b}" for a, b in t["legend"]) + "\n")

    for c in cats:
        rows = by[c["id"]]
        if not rows:
            continue
        o.append(f"## {c[lang]}\n")
        o.append(f"*{c['desc_' + lang]}* — {t['count'].format(n=len(rows))}. "
                 f"JSON: [`catalog/{c['id']}.json`](catalog/{c['id']}.json)\n")
        o.append("| " + " | ".join(t["cols"]) + " |\n|---|---|---|:-:|---|---|")
        for e in rows:
            free = ("🆓 " if is_free(e) else "") + md_cell(e.get("free_tier"))
            name = f"[{md_cell(e['name'])}]({e['homepage']})" if e.get("homepage") else md_cell(e["name"])
            o.append(f"| {name} | {md_cell(e['desc_' + lang])} | {t['auth'].get(e['auth'], e['auth'])} | "
                     f"{mcp_mark(e)} | {free} | [{t['docs']}]({e['docs']}) |")
        o.append("")

    o.append(f"## {t['h_directories']}\n\n{t['directories_intro']}\n")
    for d in dirs:
        mr = f" — machine-readable: <{d['machine_readable_url']}>" if d.get("machine_readable_url") else ""
        o.append(f"- [{d['name']}]({d['url']}) — {d['desc_' + lang]}{mr}")
    o.append("")

    o.append(f"## {t['h_contrib']}\n\n{t['contrib']}\n")
    o.append(f"## {t['h_see']}\n")
    o.append("\n".join(f"- [{a}]({b})" for a, b in t["see"]) + "\n")
    o.append(f"## {t['h_sources']}\n\n{t['sources_intro']}\n")
    o.append("\n".join(f"{i}. [{a}]({b})" for i, (a, b) in enumerate(SOURCES, 1)) + "\n")
    o.append(f"<sub>{t['footer'].format(date=VERIFIED)}</sub>\n")
    o.append("<!-- keywords: AI agent tools, agent-accessible APIs, MCP servers list, Model Context Protocol directory, "
             "tool calling APIs, LLM tools catalog, API keys for agents, Claude tools, ChatGPT actions, function calling, "
             "katalog API dla agentów AI, serwery MCP -->\n")
    return "\n".join(o)


# ---------------------------------------------------------------- llms.txt

def llms(cats, items, dirs):
    st = stats(cats, items)
    o = [f"# {TITLE}", "",
         f"> Catalog of {st['n']} third-party APIs and MCP servers that AI agents can call on a user's behalf "
         f"after a one-time API key / OAuth / MCP setup. {st['c']} categories. Last checked {VERIFIED}; each entry has its own `verified` (last-checked) date and a `link_check`; confirm pricing and task fit in `docs`. "
         "Each entry: docs URL, auth method + header hint, MCP server (official/community), free tier, SDKs, OpenAPI and llms.txt links.",
         "", "Use the JSON files; fields: id, name, category, homepage, docs, auth, auth_hint, mcp{type,url}, free_tier, sdk, openapi, llms_txt, desc_en, notes, verified, "
         "plus derived booleans has_free_tier, has_trial, no_auth, stale, link_check{checked_at, docs, mcp} and "
         "ratings[] (proof of use: SourceForge rating and review count, GitHub stars, Smithery uses; each with url and fetched_at) "
         "and reviews_url (up to 100 user reviews with pros/cons, reviewer names removed; also via the MCP tool get_reviews). "
         "Researched on vendor pages, each with source_url and checked_at: free_plan{kind, requires_card, quota, period, watermark}, "
         "auth_scheme (OpenAPI securityScheme: type, in, name, scheme, format), base_url, rate_limits, oauth_scopes, async_jobs, data_policy, "
         "mcp{maintainer, remote_url, repo, tools, covers_full_api} plus derived mcp.kind (vendor-hosted/official/community/none) "
         "and mcp.domain_verified, mcp.config (connection snippet: transport, url or command/args, headers, env, oauth, docs_only; "
         "derived: true when built from the endpoint URL alone), mcp.issue. "
         "For popular services also call{operation, method, url, example (curl), response_fields, async} and unit_price{summary}, each with source_url and checked_at.",
         "", "## Data", "",
         f"- [Full catalog (JSON)]({RAW}catalog/all.json): all entries in one array",
         f"- [Full catalog (text)]({RAW}llms-full.txt): one line per service",
         f"- [JSON Schema]({RAW}data/schema.json): entry schema",
         "- Uptime (`uptime` in JSON): our own daily probe of each `base_url` and hosted MCP endpoint from GitHub Actions (US), "
         "30-day window; up = any HTTP status below 500 (MCP: POST initialize); `probes`, `up`, `median_ms` and the last result",
         f"- [Operations]({RAW}catalog/operations.json): vocabulary of the `operations` field (what an agent can do with a service, e.g. text-to-video, sms, street-geocoding); match your task to these ids",
         f"- [SHA256SUMS]({RAW}SHA256SUMS): checksums of llms.txt, llms-full.txt, schema and catalog/*.json (`sha256sum -c SHA256SUMS`)",
         f"- [MCP server]({GH}#mcp-server): `npx -y github:{REPO}` or remote {MCP_URL} (Streamable HTTP) — tools search_apis, get_api, get_reviews, list_categories",
         "", "## Start free", "",
         f"{sum(map(is_free, items))} of {len(items)} services have a lasting free tier or free usage (JSON field `has_free_tier`; "
         f"exact limits in `free_tier`), and {sum(map(is_trial, items))} more give one-off free trial credits (`has_trial`). "
         f"{sum(e['auth'] == 'none' for e in items)} work with no key at all (`no_auth`), "
         "so you can call them immediately without asking the user for credentials:", ""]
    for e in (e for e in items if e["auth"] == "none"):
        o.append(f"- {e['name']} ({e['category']}): {e['desc_en']} Docs: {e['docs']}")
    o += ["", "## Categories", "", "Counts per category: services / with free tier / no key needed / official MCP server.", ""]
    for c in cats:
        rows = [e for e in items if e["category"] == c["id"]]
        free = sum(map(is_free, rows))
        nokey = sum(e["auth"] == "none" for e in rows)
        mcp = sum((e.get("mcp") or {}).get("type") == "official" for e in rows)
        o.append(f"- [{c['en']}]({RAW}catalog/{c['id']}.json): {len(rows)} services / {free} free tier / {nokey} no key / "
                 f"{mcp} official MCP. {c['desc_en']}")
    o += ["", "## Optional", "",
          f"- [README]({GH}#readme)", f"- [HTML version]({PAGES})"]
    for d in dirs:
        o.append(f"- [{d['name']}]({d.get('machine_readable_url') or d['url']}): {d['desc_en']}")
    return "\n".join(o) + "\n"


def llms_full(cats, items):
    o = [f"# {TITLE} — full list ({len(items)} services, last checked {VERIFIED})",
         "# format: [tags] name | what it does | auth (hint) | mcp | free tier | docs",
         "# tags: [FREE] lasting free tier or free usage, [TRIAL] one-off free trial credits, "
         "[NO-KEY] callable without any credential, [MCP] official MCP server",
         "# proof: public ratings and usage (SourceForge rating/reviews, GitHub stars, Smithery uses), date = when fetched",
         "# base url, free plan, rate limits, data policy, async jobs, oauth scopes: researched on vendor pages; sources in the JSON", ""]
    for c in cats:
        rows = [e for e in items if e["category"] == c["id"]]
        o.append(f"## {c['en']} [{c['id']}]")
        for e in rows:
            m = e.get("mcp") or {}
            mcp = f"mcp:{m.get('type')}" + (f" {m['url']}" if m.get("url") else "") if m.get("type") != "none" else "mcp:none"
            hint = f" ({e['auth_hint']})" if e.get("auth_hint") else ""
            note = f" | note: {e['notes']}" if e.get("notes") else ""
            tags = "".join(tag for tag, on in (("[FREE]", is_free(e)), ("[TRIAL]", is_trial(e)), ("[NO-KEY]", e["auth"] == "none"),
                                                ("[MCP]", m.get("type") == "official")) if on)
            proof = proof_items(e)
            proof = f" | proof: {'; '.join(l for l, _, _ in proof)} (fetched {stamp(proof[0][2])})" if proof else ""
            extra = "".join(f" | {label.lower()}: {text}" for label, text, _ in details_items(e) if label != "MCP tools")
            o.append(f"- {tags + ' ' if tags else ''}{e['name']} | {e['desc_en']} | auth:{e['auth']}{hint} | {mcp} | "
                     f"{e.get('free_tier') or '?'} | {e['docs']}{extra}{proof}{note}")
        o.append("")
    return "\n".join(o)


# ---------------------------------------------------------------- HTML

CSS = """
:root{--bg:#f8f9fa;--page:#fff;--text:#202122;--muted:#54595d;--link:#3366cc;--visited:#795cb2;--border:#a2a9b1;--soft:#eaecf0;--head:#eaecf0;--hat:#f8f9fa;--accent:#36c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#101418;--page:#16191d;--text:#eaecf0;--muted:#a2a9b1;--link:#88a3e8;--visited:#b79ce0;--border:#54595d;--soft:#27292d;--head:#202326;--hat:#1b1e22;--accent:#88a3e8}}
:root[data-theme="dark"]{--bg:#101418;--page:#16191d;--text:#eaecf0;--muted:#a2a9b1;--link:#88a3e8;--visited:#b79ce0;--border:#54595d;--soft:#27292d;--head:#202326;--hat:#1b1e22;--accent:#88a3e8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.6 -apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
header.top{border-bottom:1px solid var(--border);background:var(--page)}
header.top .in{max-width:1180px;margin:0 auto;padding:10px 16px;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.brand{font-family:"Linux Libertine","Georgia","Times",serif;font-size:20px;color:var(--text)}
.brand small{display:block;font:12px/1.2 sans-serif;color:var(--muted)}
.tabs a{margin-left:14px;font-size:14px}
main{max-width:1180px;margin:0 auto;padding:16px 16px 48px;background:var(--page);border-left:1px solid var(--soft);border-right:1px solid var(--soft)}
h1,h2{font-family:"Linux Libertine","Georgia","Times",serif;font-weight:400;border-bottom:1px solid var(--border);margin:1.2em 0 .5em;line-height:1.3}
h1{font-size:2em;margin-top:.3em}h2{font-size:1.5em}
.sub{color:var(--muted);font-size:13px;margin-top:-6px}
.badges{margin:4px 0 10px;display:flex;flex-wrap:wrap;gap:6px}.badges img{display:block}
.hatnote{font-style:italic;padding-left:1.6em;color:var(--muted);margin:.5em 0 1em}
.infobox{float:right;clear:right;width:300px;margin:0 0 1em 1.4em;border:1px solid var(--border);background:var(--hat);font-size:13px;border-collapse:collapse}
.infobox caption{font-weight:700;font-size:15px;padding:6px;background:var(--head);border:1px solid var(--border);border-bottom:0}
.infobox th,.infobox td{text-align:left;vertical-align:top;padding:4px 8px;border-top:1px solid var(--soft)}
.toc{display:inline-block;border:1px solid var(--border);background:var(--hat);padding:8px 16px;font-size:14px;margin:1em 0}
.toc b{display:block;text-align:center}.toc ol{margin:.4em 0;padding-left:1.4em}.toc ol ol{columns:2;column-gap:28px}
.wikitable{border-collapse:collapse;width:100%;font-size:14px;margin:.6em 0 1.2em;background:var(--hat)}
.wikitable th,.wikitable td{border:1px solid var(--border);padding:5px 8px;vertical-align:top}
.wikitable th{background:var(--head);text-align:left}
.wikitable td.c{text-align:center}
.tw{overflow-x:auto}
code{background:var(--soft);padding:1px 4px;border-radius:2px;font-size:13px}
.filter{position:sticky;top:0;z-index:2;background:var(--page);padding:8px 0;border-bottom:1px solid var(--soft);display:flex;gap:14px;flex-wrap:wrap;align-items:center;font-size:14px}
.filter input[type=search]{flex:1;min-width:200px;padding:6px 8px;border:1px solid var(--border);background:var(--page);color:var(--text);border-radius:2px;font-size:14px}
.cat-desc{font-style:italic;color:var(--muted)}
.refs{font-size:13px}
.det{font-size:13px;min-width:260px}
.proof{color:var(--muted);white-space:nowrap}.proof time{font-size:11px}.proof-note{color:var(--muted);font-size:13px}
footer{color:var(--muted);font-size:12px;margin-top:2em;border-top:1px solid var(--soft);padding-top:8px}
@media (max-width:720px){.infobox{float:none;width:100%;margin:0 0 1em}.toc ol ol{columns:1}.tabs a{margin:0 12px 0 0}}
"""

JS = """
(function(){var q=document.getElementById('q'),m=document.getElementById('mcp'),f=document.getElementById('free');
function run(){var s=q.value.trim().toLowerCase();document.querySelectorAll('section.cat').forEach(function(sec){var shown=0;
sec.querySelectorAll('tbody tr').forEach(function(tr){var ok=(!s||tr.textContent.toLowerCase().indexOf(s)>-1)&&(!m.checked||tr.dataset.mcp!=='none')&&(!f.checked||tr.dataset.free==='1');
tr.style.display=ok?'':'none';if(ok)shown++;});sec.style.display=shown?'':'none';});}
[q,m,f].forEach(function(el){el.addEventListener('input',run);el.addEventListener('change',run);});})();
"""


def md_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", s)


def page(lang, cats, items, dirs):
    t = T[lang]
    st = stats(cats, items)
    e_ = html.escape
    by = {c["id"]: [e for e in items if e["category"] == c["id"]] for c in cats}
    base = "" if lang == "en" else "../"
    self_url = PAGES if lang == "en" else PAGES + "pl/"
    other_url = PAGES + "pl/" if lang == "en" else PAGES
    desc = t["tagline"]
    ld = {
        "@context": "https://schema.org", "@type": "Dataset", "name": TITLE, "description": desc,
        "url": self_url, "inLanguage": lang, "dateModified": VERIFIED, "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": ["AI agents", "MCP", "Model Context Protocol", "API", "tool calling", "LLM tools", "API catalog"],
        "creator": {"@type": "Person", "name": "Marek Papis"},
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": RAW + "catalog/all.json"},
            {"@type": "DataDownload", "encodingFormat": "text/plain", "contentUrl": RAW + "llms.txt"},
        ],
        "variableMeasured": ["docs", "auth", "mcp", "free_tier"],
    }
    o = [f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f"<title>{e_(TITLE)}</title>",
         f'<meta name="description" content="{e_(desc)}">',
         f'<link rel="canonical" href="{self_url}">']
    if lang == "en":
        o += [f'<link rel="alternate" type="application/json" title="catalog.json" href="{base}catalog.json">',
              f'<link rel="alternate" type="text/plain" title="llms.txt" href="{base}llms.txt">',
              f'<meta property="og:title" content="{e_(TITLE)}"><meta property="og:description" content="{e_(desc)}"><meta property="og:type" content="website">',
              f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>']
    else:
        # Polish page is for human readers only; agents and crawlers use the English home page.
        o.append('<meta name="robots" content="noindex, follow">')
    o += [f"<style>{CSS}</style></head><body>",
         f'<header class="top"><div class="in"><a class="brand" href="{self_url}">{e_(TITLE)}<small>{e_(t["tagline"][:80])}…</small></a>',
         f'<nav class="tabs"><a href="{other_url}">{t["other_label"]}</a><a href="{base}catalog.json">JSON</a>'
         f'<a href="{base}llms.txt">llms.txt</a><a href="{GH}">GitHub</a></nav></div></header><main>',
         f"<h1>{e_(TITLE)}</h1>",
         '<p class="badges">' + " ".join(f'<a href="{e_(u)}"><img alt="{e_(a)}" src="{e_(i)}" height="20"></a>' for a, i, u in badges()) + "</p>",
         f'<div class="sub">{e_(t["tagline"])}</div>',
         f'<div class="hatnote">{t["hatnote"]}</div>',
         f'<table class="infobox"><caption>{e_(TITLE)}</caption>']
    for k, v in t["infobox"]:
        o.append(f"<tr><th>{e_(k)}</th><td>{e_(v.format(**st))}</td></tr>")
    o.append("</table>")
    o.append(f"<p>{md_inline(t['lead'].format(**st))}</p>")

    o.append(f'<nav class="toc"><b>{t["contents"]}</b><ol>')
    toc = ([(t["h_agents"], "agents")] if lang == "en" else []) + [(t["h_criteria"], "criteria"), (t["h_legend"], "legend")]
    for h, a in toc:
        o.append(f'<li><a href="#{a}">{e_(h)}</a></li>')
    o.append("<li>" + ("Kategorie" if lang == "pl" else "Categories") + "<ol>")
    for c in cats:
        o.append(f'<li><a href="#{c["id"]}">{e_(c[lang])}</a> ({len(by[c["id"]])})</li>')
    o.append("</ol></li>")
    for h, a in ((t["h_directories"], "directories"), (t["h_contrib"], "contributing"), (t["h_sources"], "references")):
        o.append(f'<li><a href="#{a}">{e_(h)}</a></li>')
    o.append("</ol></nav>")

    if lang == "en":
        o.append(f'<h2 id="agents">{e_(t["h_agents"])}</h2><p>{e_(t["agents_intro"])}</p><ul>')
        for f, d in t["files"]:
            path = html.unescape(f)
            url = RAW + (path if "<" not in path else "catalog/")
            o.append(f'<li><a href="{e_(url)}"><code>{f}</code></a> — {e_(d)}</li>')
        o.append(f"</ul><p>{md_inline(t['agents_recipe'])}</p>")

    o.append(f'<h2 id="criteria">{e_(t["h_criteria"])}</h2><ol>' + "".join(f"<li>{md_inline(x)}</li>" for x in t["criteria"]) + "</ol>")
    o.append(f'<h2 id="legend">{e_(t["h_legend"])}</h2><ul>' + "".join(f"<li><b>{e_(a)}</b> — {e_(b)}</li>" for a, b in t["legend"]) + "</ul>")

    o.append(ratings_note(lang))
    o.append(f'<div class="filter"><input type="search" id="q" placeholder="{e_(t["filter"])}" aria-label="{e_(t["filter"])}">'
             f'<label><input type="checkbox" id="mcp"> {e_(t["mcp_only"])}</label><label><input type="checkbox" id="free"> {e_(t["free_only"])}</label></div>')

    for c in cats:
        rows = by[c["id"]]
        if not rows:
            continue
        o.append(f'<section class="cat"><h2 id="{c["id"]}">{e_(c[lang])}</h2>')
        o.append(f'<p><span class="cat-desc">{e_(c["desc_" + lang])}</span> — {t["count"].format(n=len(rows))}. '
                 f'JSON: <a href="{RAW}catalog/{c["id"]}.json"><code>catalog/{c["id"]}.json</code></a>'
                 + (f' · <a href="c/{c["id"]}/">details page</a>' if lang == "en" else "") + "</p>")
        o.append('<div class="tw"><table class="wikitable"><thead><tr>' + "".join(f"<th>{e_(x)}</th>" for x in t["cols"]) + "</tr></thead><tbody>")
        for e in rows:
            mtype = (e.get("mcp") or {}).get("type", "none")
            free = is_free(e)
            name = (f'<a href="{e_(e["homepage"])}">{e_(e["name"])}</a>' if e.get("homepage") else e_(e["name"])) + proof_html(e)
            o.append(f'<tr id="{e["id"]}" data-mcp="{mtype}" data-free="{int(free)}"><td>{name}</td><td>{e_(e["desc_" + lang])}</td>'
                     f'<td>{e_(t["auth"].get(e["auth"], e["auth"]))}</td><td class="c">{mcp_mark(e, "html")}</td>'
                     f'<td>{"🆓 " if free else ""}{e_(e.get("free_tier") or "")}</td><td><a href="{e_(e["docs"])}">{t["docs"]}</a></td></tr>')
        o.append("</tbody></table></div></section>")

    o.append(f'<h2 id="directories">{e_(t["h_directories"])}</h2><p>{e_(t["directories_intro"])}</p><ul>')
    for d in dirs:
        mr = f' — <a href="{e_(d["machine_readable_url"])}">JSON/API</a>' if d.get("machine_readable_url") else ""
        o.append(f'<li><a href="{e_(d["url"])}">{e_(d["name"])}</a> — {e_(d["desc_" + lang])}{mr}</li>')
    o.append("</ul>")
    o.append(f'<h2 id="contributing">{e_(t["h_contrib"])}</h2><p>{md_inline(t["contrib"])}</p>')
    o.append(f'<h2>{e_(t["h_see"])}</h2><ul>' + "".join(f'<li><a href="{b}">{e_(a)}</a></li>' for a, b in t["see"]) + "</ul>")
    o.append(f'<h2 id="references">{e_(t["h_sources"])}</h2><p>{e_(t["sources_intro"])}</p><ol class="refs">'
             + "".join(f'<li><a href="{b}">{e_(a)}</a></li>' for a, b in SOURCES) + "</ol>")
    o.append(f'<footer>{e_(t["footer"].format(date=VERIFIED))} · <a href="{GH}">{GH}</a></footer></main><script>{JS}</script></body></html>')
    return "\n".join(o)


def category_page(c, rows, cats):
    """One page per category, titled after the queries agents actually run
    (e.g. "video generation API MCP server free tier")."""
    t, e_ = T["en"], html.escape
    url = f"{PAGES}c/{c['id']}/"
    title = f"{c['en']} APIs and MCP servers for AI agents"
    n_mcp = sum(1 for e in rows if (e.get("mcp") or {}).get("type") == "official")
    n_free = sum(1 for e in rows if is_free(e))
    desc = (f"{len(rows)} {c['en'].lower()} APIs an AI agent can call: auth method and header, "
            f"official MCP server ({n_mcp}), free tier ({n_free}), docs links. Machine-readable JSON included.")
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": title, "description": desc, "url": url,
          "numberOfItems": len(rows),
          "itemListElement": [{"@type": "ListItem", "position": i, "name": e["name"], "url": e["docs"]} for i, e in enumerate(rows, 1)]}
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         f"<title>{e_(title)}</title>", f'<meta name="description" content="{e_(desc)}">',
         f'<link rel="canonical" href="{url}">',
         f'<link rel="alternate" type="application/json" href="{RAW}catalog/{c["id"]}.json">',
         f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>',
         f"<style>{CSS}</style></head><body>",
         f'<header class="top"><div class="in"><a class="brand" href="../../">{e_(TITLE)}<small>{e_(c["en"])}</small></a>',
         f'<nav class="tabs"><a href="../../">All categories</a><a href="{RAW}catalog/{c["id"]}.json">JSON</a>'
         f'<a href="../../llms.txt">llms.txt</a><a href="{GH}">GitHub</a></nav></div></header><main>',
         f"<h1>{e_(title)}</h1>", f'<div class="sub">{e_(c["desc_en"])}</div>',
         f"<p>{e_(desc)} Agents: fetch <a href=\"{RAW}catalog/{c['id']}.json\"><code>catalog/{c['id']}.json</code></a> "
         f"instead of parsing this page. Last checked {VERIFIED}.</p>",
         ratings_note("en"),
         '<div class="tw"><table class="wikitable"><thead><tr><th>Service</th><th>What an agent can do</th><th>Auth</th>'
         '<th>MCP server</th><th>Free tier</th><th>Details (with sources)</th><th>Notes</th><th>Proof (ratings, usage)</th></tr></thead><tbody>']
    for e in rows:
        m = e.get("mcp") or {}
        mcp = {"official": "official", "community": "community"}.get(m.get("type"), "—")
        if m.get("url") and mcp != "—":
            mcp = f'<a href="{e_(m["url"])}">{mcp}</a>'
        auth = e_(t["auth"].get(e["auth"], e["auth"])) + (f'<br><code>{e_(e["auth_hint"])}</code>' if e.get("auth_hint") else "")
        o.append(f'<tr id="{e["id"]}"><td><a href="{e_(e["docs"])}"><b>{e_(e["name"])}</b></a></td><td>{e_(e["desc_en"])}</td>'
                 f'<td>{auth}</td><td class="c">{mcp}</td><td>{e_(e.get("free_tier") or "")}</td><td class="det">{details_html(e)}</td>'
                 f'<td>{e_(e.get("notes") or "")}</td><td>{proof_html(e).removeprefix("<br>") or "—"}</td></tr>')
    o.append("</tbody></table></div>")
    o.append("<h2>Other categories</h2><ul>" + "".join(
        f'<li><a href="../{x["id"]}/">{e_(x["en"])}</a></li>' for x in cats if x["id"] != c["id"]) + "</ul>")
    o.append(f'<footer>{e_(t["footer"].format(date=VERIFIED))} · <a href="{GH}">{GH}</a></footer></main></body></html>')
    return "\n".join(o)


# ---------------------------------------------------------------- main

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


def uptime_summary(rec):
    """Rolling availability from scripts/probe_uptime.py: probes, how many answered, median latency, last result."""
    out = {"window_days": 30}  # method: see llms.txt and scripts/probe_uptime.py
    for kind, name in (("api", "api"), ("mcp", "mcp_remote")):
        h = (rec.get(kind) or {}).get("history") or []
        if not h:
            continue
        ms = sorted(x["ms"] for x in h if x.get("ms") is not None)
        last = h[-1]
        out[name] = {"url": rec[kind]["url"], "probes": len(h), "up": sum(1 for x in h if x["up"]),
                     "median_ms": ms[len(ms) // 2] if ms else None,
                     "last": {"at": last["at"], "up": last["up"], "detail": last["detail"]}}
    return out


def main():
    global VERIFIED, RATINGS, USAGE
    cats, items, dirs = load()
    USAGE = load_usage({e.get("id") for e in items})
    uptime_file = DATA / "uptime.json"
    uptime = json.loads(uptime_file.read_text("utf-8")) if uptime_file.exists() else {}
    ratings_file = DATA / "ratings.json"
    RATINGS = json.loads(ratings_file.read_text("utf-8")) if ratings_file.exists() else {}
    VERIFIED = max((e.get("verified") or "" for e in items), default="") or date.today().isoformat()
    ids = set()
    for e in items:
        e.setdefault("id", slug(e["name"]))
        assert e["id"] not in ids, f"duplicate id {e['id']}"
        ids.add(e["id"])
        assert e["category"] in {c["id"] for c in cats}, e["name"]
        unknown = set(e.get("operations") or []) - set(OPERATIONS)
        assert not unknown, f"{e['id']}: operations not in data/operations.json: {sorted(unknown)}"
    for lang in ("en", "pl"):
        write(T[lang]["readme"], readme(lang, cats, items, dirs))
    write("docs/index.html", page("en", cats, items, dirs))
    write("docs/pl/index.html", page("pl", cats, items, dirs))
    lt, lf = llms(cats, items, dirs), llms_full(cats, items)
    for base in ("", "docs/"):
        write(base + "llms.txt", lt)
        write(base + "llms-full.txt", lf)
    # data/catalog.json is the bilingual source; agent-facing JSON is English-only.
    write("data/catalog.json", json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    status_file = DATA / "link-status.json"
    links = json.loads(status_file.read_text("utf-8")) if status_file.exists() else {}
    today = date.today()
    en = []
    for e in items:
        x = {k: v for k, v in e.items() if k != "desc_pl"}
        # Derived fields agents asked for in the discovery interviews.
        x["no_auth"] = e["auth"] == "none"
        x["mcp"] = mcp_details(e)
        u = USAGE.get(e["id"], {})
        x["mcp"]["config"] = mcp_config(e, x["mcp"], u) if x["mcp"]["kind"] != "none" else None
        if u.get("mcp_issue"):
            x["mcp"]["issue"] = u["mcp_issue"]
        for k in ("call", "unit_price"):
            if u.get(k):
                x[k] = u[k]
        x["has_free_tier"] = is_free(e)
        x["has_trial"] = is_trial(e)
        # Usable for free without a payment card: no key at all, or a free/trial plan confirmed card-free.
        x["no_card"] = e["auth"] == "none" or ((is_free(e) or is_trial(e)) and (e.get("free_plan") or {}).get("requires_card") is False)
        x["stale"] = bool(e.get("verified")) and (today - date.fromisoformat(e["verified"])).days > STALE_DAYS
        if e["id"] in links:
            x["link_check"] = links[e["id"]]
        if RATINGS.get(e["id"]):
            x["ratings"] = RATINGS[e["id"]]
        if uptime.get(e["id"]):
            x["uptime"] = uptime_summary(uptime[e["id"]])
        if (ROOT / "catalog" / "reviews" / f"{e['id']}.json").exists():
            x["reviews_url"] = f"{RAW}catalog/reviews/{e['id']}.json"  # review texts: JSON and MCP only, not on the website
        en.append(x)
    dump = json.dumps(en, ensure_ascii=False, indent=2) + "\n"
    write("catalog/all.json", dump)
    write("catalog/operations.json", json.dumps(OPERATIONS, ensure_ascii=False, indent=1) + "\n")
    write("docs/catalog.json", dump)
    for c in cats:
        rows = [{k: v for k, v in e.items() if k != "category"} for e in en if e["category"] == c["id"]]
        cat = {"id": c["id"], "name": c["en"], "description": c["desc_en"]}
        # Compact, one entry per line: indentation costs an agent tokens, one line per entry keeps diffs readable
        compact = lambda v: json.dumps(v, ensure_ascii=False, separators=(",", ":"))  # noqa: E731
        text = ('{"category":' + compact(cat) + ',"entries":[\n' + ",\n".join(compact(r) for r in rows) + "\n]}\n")
        if len(text.encode()) > MAX_CATEGORY_BYTES:
            print(f"WARNING: catalog/{c['id']}.json is {len(text.encode()) // 1024} KB (limit {MAX_CATEGORY_BYTES // 1024} KB)")
        write(f"catalog/{c['id']}.json", text)
        write(f"docs/c/{c['id']}/index.html", category_page(c, [e for e in items if e["category"] == c["id"]], cats))
    # Skill as a zip for uploading to claude.ai. Fixed timestamp and no compression keep it byte-identical
    # across builds and platforms (zlib versions compress differently, create_system is OS-specific).
    skill_dir = ROOT / "skills" / "ai-agents-api-library"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file():
                info = zipfile.ZipInfo(f"ai-agents-api-library/{f.relative_to(skill_dir).as_posix()}", (2026, 1, 1, 0, 0, 0))
                info.create_system = 3  # Unix; Python's default depends on the OS the build runs on
                info.external_attr = 0o644 << 16
                z.writestr(info, f.read_bytes(), zipfile.ZIP_STORED)
    (ROOT / "docs" / "ai-agents-api-library-skill.zip").write_bytes(buf.getvalue())
    write("docs/.nojekyll", "")
    write("docs/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {PAGES}sitemap.xml\n")
    write("docs/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"<url><loc>{u}</loc><lastmod>{VERIFIED}</lastmod></url>\n" for u in
                    [PAGES, PAGES + "catalog.json", PAGES + "llms.txt"] + [f"{PAGES}c/{c['id']}/" for c in cats])
          + "</urlset>\n")
    checksums()
    print(f"{len(items)} entries, {len(cats)} categories -> built")


def checksums():
    """SHA256SUMS for the files agents download, in `sha256sum -c` format (repo root and the Pages copy)."""
    def sums(base, paths):
        rows = [f"{hashlib.sha256((base / q).read_bytes()).hexdigest()}  {q}" for q in sorted(paths)]
        return "\n".join(rows) + "\n"
    root = ["llms.txt", "llms-full.txt", "data/schema.json"] + [p.relative_to(ROOT).as_posix() for p in (ROOT / "catalog").rglob("*.json")]
    write("SHA256SUMS", sums(ROOT, root))
    docs = ["llms.txt", "llms-full.txt", "catalog.json", "ai-agents-api-library-skill.zip"]
    write("docs/SHA256SUMS", sums(ROOT / "docs", docs))


VERIFIED = ""
USAGE = {}
if __name__ == "__main__":
    main()
