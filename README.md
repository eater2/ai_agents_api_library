<p align="right"><a href="README.pl.md">Polski</a> · <a href="https://eater2.github.io/ai_agents_api_library/">HTML</a> · <a href="llms.txt">llms.txt</a> · <a href="catalog/all.json">catalog.json</a></p>

# AI Agents Accessible APIs

<em>A curated, machine-readable encyclopedia of third-party APIs and MCP servers that AI agents can call on a user's behalf.</em>

> This article is about services an AI agent can operate programmatically. For AI products used by humans through a web UI, see the <a href="#excluded-services">Excluded services</a> section.

<table align="right" width="300">
<tr><th colspan="2" align="center">AI Agents Accessible APIs</th></tr>
<tr><td><b>Type</b></td><td>API & MCP catalog</td></tr>
<tr><td><b>Entries</b></td><td>301</td></tr>
<tr><td><b>Categories</b></td><td>26</td></tr>
<tr><td><b>Official MCP servers</b></td><td>150</td></tr>
<tr><td><b>Languages</b></td><td>English, Polish</td></tr>
<tr><td><b>Format</b></td><td>JSON, Markdown, HTML, llms.txt</td></tr>
<tr><td><b>Last verified</b></td><td>2026-09-24</td></tr>
<tr><td><b>License</b></td><td>CC BY 4.0 (data), MIT (code)</td></tr>
</table>

**AI Agents Accessible APIs** is an open, bilingual (English/Polish) catalog of **301 verified services** in **26 categories** that an autonomous AI agent — such as Claude, ChatGPT, Gemini or a custom LLM agent — can use **without a human in the loop**, after a one-time human step: registering an account and handing the agent an **API key**, an **OAuth token**, or a connection to an **MCP (Model Context Protocol) server**. Every entry records the documentation URL, the authentication method, the availability of an official or community MCP server, and the free tier. The list is not a directory of products with “AI” in their name; the criterion is agent operability, not branding.

## Contents

1. [Machine-readable access (for AI agents)](#machine-readable-access-for-ai-agents)
2. [Inclusion criteria](#inclusion-criteria)
3. [Legend](#legend)
4. [Web search](#web-search) (14) · [Web scraping and browser automation](#web-scraping-and-browser-automation) (18) · [Knowledge and research data](#knowledge-and-research-data) (12) · [Image generation and editing](#image-generation-and-editing) (10) · [Video generation and editing](#video-generation-and-editing) (15) · [Speech and audio](#speech-and-audio) (13) · [Music generation](#music-generation) (6) · [3D generation and assets](#3d-generation-and-assets) (7) · [Architecture, CAD and BIM](#architecture-cad-and-bim) (9) · [Diagrams and software architecture](#diagrams-and-software-architecture) (9) · [Design and UI](#design-and-ui) (6) · [Documents, OCR and presentations](#documents-ocr-and-presentations) (14) · [Translation and language](#translation-and-language) (6) · [Code execution sandboxes](#code-execution-sandboxes) (10) · [Developer platforms and DevOps](#developer-platforms-and-devops) (17) · [Databases, vector stores and memory](#databases-vector-stores-and-memory) (18) · [Email, messaging and chat](#email-messaging-and-chat) (13) · [Voice agents and telephony](#voice-agents-and-telephony) (8) · [Productivity and workspace](#productivity-and-workspace) (16) · [CRM, support and marketing](#crm-support-and-marketing) (8) · [Social media](#social-media) (10) · [Maps, geolocation and weather](#maps-geolocation-and-weather) (11) · [Finance, payments and market data](#finance-payments-and-market-data) (13) · [E-commerce](#e-commerce) (7) · [Automation and integration platforms](#automation-and-integration-platforms) (14) · [Model APIs and inference](#model-apis-and-inference) (17)
5. [Excluded services](#excluded-services)
6. [Related directories and registries](#related-directories-and-registries)
7. [Contributing](#contributing)
8. [See also](#see-also)
9. [References](#references)

## Machine-readable access (for AI agents)

AI agents should not parse this page. Fetch one of these stable files instead:

| File | Raw URL |
|---|---|
| `llms.txt` — short index for LLMs, links to everything below | https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/llms.txt |
| `llms-full.txt` — the whole catalog as compact plain text, one line per service | https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/llms-full.txt |
| `catalog/all.json` — full catalog, one JSON array | https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/all.json |
| `catalog/<category>.json` — one file per category, for small context windows | https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/catalog/ |
| `data/schema.json` — JSON Schema of an entry | https://raw.githubusercontent.com/eater2/ai_agents_api_library/main/data/schema.json |

Recommended agent workflow: (1) pick the category file, (2) filter by `auth` and `mcp.type`, (3) read `docs` (or `llms_txt` / `openapi` when present), (4) ask the user for the credential named in `auth_hint`.

### MCP server

The catalog is also an MCP server with three tools: `search_apis` (filters: `query`, `category`, `mcp`, `no_auth`, `free_tier`, `auth`), `get_api` and `list_categories`. No key needed. Add it to your MCP client:

```json
{
  "mcpServers": {
    "ai-agents-api-library": {
      "command": "npx",
      "args": ["-y", "github:eater2/ai_agents_api_library"]
    }
  }
}
```

Claude Code: `claude mcp add ai-agents-api-library -- npx -y github:eater2/ai_agents_api_library`

No install: remote endpoint (Streamable HTTP, no key) `https://ai-agents-api-library.vercel.app/mcp`, e.g. `claude mcp add --transport http ai-agents-api-library https://ai-agents-api-library.vercel.app/mcp`. Listed in the [official MCP Registry](https://registry.modelcontextprotocol.io/v0/servers?search=ai-agents-api-library) as `io.github.eater2/ai-agents-api-library`.

### Claude skill and plugin

The skill tells Claude when to reach for the catalog and how to pick a service. The plugin bundles the skill with the MCP server:

- **Claude Code plugin** (skill + MCP server):
  ```
  /plugin marketplace add eater2/ai_agents_api_library
  /plugin install ai-agents-api-library@eater2
  ```
- **Skill only, Claude Code:** copy [`skills/ai-agents-api-library/`](skills/ai-agents-api-library/SKILL.md) to `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).
- **Skill only, claude.ai / Claude Desktop:** download [the skill zip](https://eater2.github.io/ai_agents_api_library/ai-agents-api-library-skill.zip) and upload it under Settings → Capabilities → Skills.

## Inclusion criteria

- The service exposes a **public, self-serve** programmatic interface (REST, GraphQL, SDK) **or** an MCP server.
- A human needs to act **at most once** — sign up and create a key or approve OAuth. After that the agent works unattended.
- The interface is **documented** and **currently active** (verified on the date shown in the infobox).
- Consumer-only apps, waitlists, sales-gated enterprise products, agent frameworks and IDEs are **excluded** — they are agents or tools for building agents, not services an agent calls.

## Legend

- **MCP ✅** — official MCP server maintained by the vendor
- **MCP ◐** — community-maintained MCP server
- **MCP —** — no MCP server known; use the REST API
- **🆓** — free tier or free usage without payment

## Web search

*Search engines and answer APIs that return fresh web results, snippets or full page content in agent-friendly formats.* — 14 services. JSON: [`catalog/web-search.json`](catalog/web-search.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Brave Search API](https://brave.com/search/api/) | Lets an agent query Brave's independent web/image/video/news search index and get cited, LLM-ready results. | API key | [✅](https://github.com/brave/brave-search-mcp-server) | 🆓 $5 free monthly credits (~1,000 queries on Search plan); credit card required at signup as anti-fraud measure | [docs](https://api-dashboard.search.brave.com/app/documentation/web-search/get-started) |
| [Exa](https://exa.ai) | Lets an agent run neural or keyword web search, retrieve page contents, and find similar links via Exa's API. | API key | [✅](https://mcp.exa.ai/mcp) | 🆓 free tier: $10 free credits/month (~1,400 searches), no payment method required | [docs](https://docs.exa.ai/reference/getting-started) |
| [Jina AI Search / Reader](https://jina.ai) | Search the web or convert any URL into clean LLM-ready markdown via simple HTTP GET requests. | API key | — | 🆓 no key needed: 100 RPM (s.jina.ai search) / 500 RPM (r.jina.ai reader); free API key raises limits to 1,000/5,000 RPM with token-based billing | [docs](https://docs.jina.ai) |
| [Kagi Search API](https://kagi.com) | Run programmatic, ad-free premium web/news/image/video searches and extract page markdown via a paid REST API. | API key | [✅](https://github.com/kagisearch/kagimcp) | no free tier: pay-per-use, $12 per 1,000 search requests, invoiced monthly or at $100 usage, whichever first | [docs](https://help.kagi.com/kagi/api/overview.html) |
| [Linkup](https://www.linkup.so) | Lets an agent search, fetch pages, or run deep multi-source research via Linkup's Search/Fetch/Research API endpoints. | API key | [✅](https://mcp.linkup.so/mcp) | 🆓 $20 free credits/month for new accounts signing up with a professional email | [docs](https://docs.linkup.so/pages/documentation/endpoints/search/reference) |
| [Mojeek Search API](https://www.mojeek.com/services/search/web-search-api/) | Query Mojeek's independent web index for titles, URLs and snippets in JSON or XML, with country/language boosting. | API key | — | limited-query free trial available on request; paid plans from £2 CPM (Startup, 5 req/s, 100k/day cap) | [docs](https://www.mojeek.com/support/api/search/) |
| [Parallel Web Systems Search API](https://parallel.ai) | Lets an agent run Parallel's low-latency Search API for web research, content extraction, and entity discovery. | API key | [✅](https://search.parallel.ai/mcp) | 🆓 free: 5,000 requests/month across APIs, plus up to $80 signup credit and $5/month free credits | [docs](https://docs.parallel.ai) |
| [Perplexity Sonar / Search API](https://docs.perplexity.ai) | Lets an agent call Perplexity's Search API or MCP tools (search/ask/research/reason) for real-time grounded web answers. | API key / OAuth | [✅](https://api.perplexity.ai/mcp) | no confirmed free tier; pay-as-you-go, Search API billed at $5 per 1,000 requests | [docs](https://docs.perplexity.ai/api-reference/search-post) |
| [SearchApi.io](https://www.searchapi.io) | Fetch structured JSON results from Google, Bing, YouTube, Amazon, TikTok and 50+ other search engines via one REST API. | API key | — | 🆓 100 free requests, no credit card required; then paid plans from $40/mo (10,000 searches) | [docs](https://www.searchapi.io/docs/google) |
| [SearXNG (self-hosted JSON API)](https://docs.searxng.org) | Query a self-hosted SearXNG metasearch instance's JSON API to aggregate results from many search engines at once. | none | [◐](https://github.com/ihor-sokoliuk/mcp-searxng) | 🆓 free, no key (self-hosted; you run and pay for the instance yourself) | [docs](https://docs.searxng.org/dev/search_api.html) |
| [SerpApi](https://serpapi.com) | Lets an agent scrape structured JSON results from Google and 20+ other search engines via SerpApi's REST API. | API key | [✅](https://github.com/serpapi/serpapi-mcp) | 🆓 free plan: 250 searches/month, 50 requests/hour throughput | [docs](https://serpapi.com/search-api) |
| [Serper](https://serper.dev) | Lets an agent fetch fast, low-cost Google search results (web, images, news, maps, shopping) via Serper's REST API. | API key | [◐](https://github.com/marcopesani/mcp-server-serper) | 🆓 free tier: 2,500 queries, no credit card required | [docs](https://serper.dev) |
| [Tavily](https://tavily.com) | Lets an agent call Tavily's search API or MCP server to run web searches and get AI-ready summarized results. | API key | [✅](https://mcp.tavily.com/mcp/) | 🆓 free tier: 1,000 API credits/month, no credit card required | [docs](https://docs.tavily.com/documentation/api-reference/endpoint/search) |
| [You.com API](https://you.com/api) | Lets an agent call You.com's Search/Answer/Research API or MCP server for LLM-ready web search and grounded answers. | API key | [✅](https://api.you.com/mcp) | 🆓 free credits on signup via you.com/platform; free search profile also available through the keyless Docs MCP server | [docs](https://you.com/docs/api-reference/search) |

## Web scraping and browser automation

*Crawl, scrape and convert pages to Markdown/JSON, or drive a remote headless browser (clicks, forms, logins).* — 18 services. JSON: [`catalog/web-scraping-browser.json`](catalog/web-scraping-browser.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Anchor Browser](https://anchorbrowser.io) | Provision authenticated cloud browser sessions and turn any website into callable MCP tools for agents. | API key | [✅](https://api.anchorbrowser.io/mcp) | 🆓 $5 free credits/mo, no card required | [docs](https://docs.anchorbrowser.io) |
| [Apify](https://apify.com) | Run web scraping/automation 'Actors' from a marketplace of thousands, and manage datasets, via REST API or MCP server. | API key / OAuth | [✅](https://docs.apify.com/platform/integrations/mcp) | 🆓 free plan: $5/mo platform usage credit, no card required | [docs](https://docs.apify.com/api) |
| [Bright Data](https://brightdata.com) | Access Web Unlocker, SERP API, Scraping Browser, and structured datasets via REST API or MCP to pull web data at scale. | API key | [✅](https://github.com/brightdata/brightdata-mcp) | 🆓 free tier: up to 5,000 requests/mo | [docs](https://docs.brightdata.com/introduction) |
| [Browse AI API](https://www.browse.ai) | Trigger pre-built or custom 'robots' to extract and monitor web data via REST API, returning structured JSON. | API key | — | 🆓 free forever plan: 50 credits/mo, no card required | [docs](https://docs.browse.ai/api/v2) |
| [Browser Use Cloud API](https://browser-use.com) | Launch cloud browser sessions and run AI browser-automation agent tasks via REST API or Python/TypeScript SDK. | API key | — | $15 one-time signup credit for new accounts (Google/GitHub/Microsoft); paid usage afterward | [docs](https://docs.browser-use.com) |
| [Browserbase (+ Stagehand)](https://www.browserbase.com) | Run and control cloud headless browsers programmatically, with Stagehand adding natural-language page actions. | API key | [✅](https://www.browserbase.com/mcp) | 🆓 free tier: limited browser hours, single concurrency, no card required | [docs](https://docs.browserbase.com) |
| [Diffbot](https://www.diffbot.com) | Automatically extract structured data (articles, products, people) from any URL via REST API, no custom parsing rules needed. | API key | — | 🆓 free plan: 10,000 credits/mo, no card required (5 req/min limit) | [docs](https://www.diffbot.com/docs/extract/) |
| [Firecrawl](https://www.firecrawl.dev) | Scrape, crawl, and extract structured data from any website via a single REST API call. | API key | [✅](https://mcp.firecrawl.dev/v2/mcp) | 🆓 free tier: 1,000 credits/mo, no card required | [docs](https://docs.firecrawl.dev) |
| [Hyperbrowser](https://www.hyperbrowser.ai) | Spin up cloud browsers and call scrape, crawl, and structured-extract endpoints via REST API or MCP server. | API key | [✅](https://github.com/hyperbrowserai/mcp) | 🆓 free plan: starter credits, 1 concurrent browser, no card required | [docs](https://docs.hyperbrowser.ai) |
| [Oxylabs](https://oxylabs.io) | Fetch web pages, search-engine results, and e-commerce data at scale via REST API with built-in proxy/unblocking infrastructure. | API key | — | 🆓 free trial available (check pricing) | [docs](https://developers.oxylabs.io) |
| [Playwright MCP (Microsoft)](https://github.com/microsoft/playwright-mcp) | Official Microsoft MCP server giving agents structured browser control (click, type, navigate) via Playwright's accessibility tree. | none | [✅](https://github.com/microsoft/playwright-mcp) | 🆓 free, open source, no key | [docs](https://github.com/microsoft/playwright-mcp#readme) |
| [ScrapeGraphAI API](https://scrapegraphai.com) | Use AI-driven prompts to scrape and extract structured data from webpages via REST API or Python/JS SDK. | API key | — | 🆓 free plan: 500 one-time API credits | [docs](https://docs.scrapegraphai.com/introduction) |
| [ScraperAPI](https://www.scraperapi.com) | Scrape any webpage with automatic proxy rotation, CAPTCHA handling, and JS rendering via a single REST API call. | API key | — | 5,000 free API credits (trial), no long-term free plan | [docs](https://docs.scraperapi.com) |
| [Scrapfly](https://scrapfly.io) | Scrape webpages, run cloud browsers, and capture screenshots via REST API or hosted MCP server with anti-bot bypass. | API key / OAuth | [✅](https://scrapfly.io/products/mcp-cloud) | 🆓 1,000 free credits/mo, no card required, no time limit | [docs](https://scrapfly.io/docs) |
| [ScrapingBee](https://www.scrapingbee.com) | Scrape any webpage with JS rendering, proxy rotation, and screenshot capture via a single REST API call. | API key | — | 🆓 1,000 free API credits, no card required | [docs](https://www.scrapingbee.com/documentation/) |
| [Spider.cloud](https://spider.cloud) | Crawl and scrape websites at scale, returning JSON/XML/CSV, via REST API, CLI, or MCP server. | API key | [✅](https://spider.cloud/mcp/) | 🆓 keyless trial: 25 free runs/day, no account required | [docs](https://spider.cloud/docs/api) |
| [Steel](https://steel.dev) | Create managed cloud browser sessions with stealth proxies and CAPTCHA solving, controllable via REST API or Playwright/Puppeteer. | API key | — | 🆓 Hobby tier: 100 browser-hours/mo, 500 requests/day, no card required | [docs](https://docs.steel.dev) |
| [Zyte API](https://www.zyte.com) | Fetch and auto-extract web pages (HTML, browser rendering, product/article data) via one HTTP API with ban avoidance. | API key | — | 🆓 $5 free credit for the first month | [docs](https://docs.zyte.com/zyte-api/get-started.html) |

## Knowledge and research data

*Encyclopedias, academic papers, news, computational knowledge and up-to-date library documentation.* — 12 services. JSON: [`catalog/knowledge-research.json`](catalog/knowledge-research.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [arXiv API](https://info.arxiv.org/help/api/) | Search arXiv preprints by keyword, author, category or ID and retrieve metadata, abstracts and PDF links. | none | [◐](https://github.com/blazickjp/arxiv-mcp-server) | 🆓 free, no key | [docs](https://info.arxiv.org/help/api/user-manual.html) |
| [Context7 (library docs for agents)](https://context7.com) | Fetch up-to-date, version-specific library documentation and code examples into a coding agent's context via MCP or REST. | API key | [✅](https://mcp.context7.com/mcp) | 🆓 free; low limits without key, free API key from context7.com/dashboard raises limits | [docs](https://context7.com/docs/api-guide) |
| [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | Look up and search scholarly metadata such as DOIs, references, authors, funders and licenses across Crossref-registered works. | none | [◐](https://github.com/afrise/academic-search-mcp-server) | 🆓 free, no key | [docs](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) |
| [GDELT API](https://www.gdeltproject.org) | Full-text search global news in about 65 languages and analyze coverage volume, tone and geography in near real time. | none | [◐](https://github.com/cyanheads/gdelt-mcp-server) | 🆓 free, no key | [docs](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) |
| [Hacker News API](https://github.com/HackerNews/API) | Read Hacker News stories, comments, jobs, polls, user profiles and front-page rankings as real-time JSON. | none | [◐](https://github.com/pskill9/hn-server) | 🆓 free, no key | [docs](https://github.com/HackerNews/API) |
| [NewsAPI](https://newsapi.org) | Search and retrieve current and historical news articles and top headlines from thousands of sources worldwide. | API key | [◐](https://github.com/matteoantoci/mcp-newsapi) | 🆓 free Developer plan: 100 req/day, dev/test only, 24h article delay | [docs](https://newsapi.org/docs) |
| [OpenAlex API](https://openalex.org) | Query an open catalog of scholarly works, authors, institutions, sources and topics, including citation data, via REST. | API key | [◐](https://github.com/benedict2310/Scientific-Papers-MCP) | 🆓 free: $1 of API usage/day without payment method; free key raises daily budget 10x | [docs](https://help.openalex.org/api/) |
| [PubMed E-utilities (NCBI)](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Search, fetch, summarize and cross-link biomedical literature records from PubMed, PMC and other Entrez databases. | none | [◐](https://github.com/openags/paper-search-mcp) | 🆓 free; 3 req/s without key, 10 req/s with free NCBI API key | [docs](https://www.ncbi.nlm.nih.gov/books/NBK25501/) |
| [Semantic Scholar API](https://www.semanticscholar.org/product/api) | Search papers, authors and citation graphs, and get paper recommendations from Semantic Scholar's academic corpus. | API key | [◐](https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server) | 🆓 free; no key (shared, throttled pool) or free API key on request | [docs](https://api.semanticscholar.org/api-docs/) |
| [Wikidata](https://www.wikidata.org) | Query the Wikidata knowledge graph of entities, facts and relations via SPARQL, the REST API or MCP. | none | [✅](https://wd-mcp.wmcloud.org/mcp) | 🆓 free, no key | [docs](https://www.wikidata.org/wiki/Wikidata:Data_access) |
| [Wikipedia / Wikimedia API](https://www.mediawiki.org/wiki/Wikimedia_APIs) | Search, read and summarize Wikipedia and other Wikimedia content and metadata via REST and Action APIs. | none | [◐](https://github.com/Rudra-ravi/wikipedia-mcp) | 🆓 free, no key (rate-limited) | [docs](https://www.mediawiki.org/wiki/Wikimedia_APIs) |
| [Wolfram\|Alpha API](https://products.wolframalpha.com/api) | Get computed answers, structured data and step-by-step results for math, science and factual queries. | API key | [✅](https://www.wolfram.com/artificial-intelligence/mcp/cloud/) | 🆓 free non-commercial developer AppID (reported up to 2,000 calls/month); paid for commercial use | [docs](https://products.wolframalpha.com/llm-api/documentation) |

## Image generation and editing

*Text-to-image, image editing, inpainting, upscaling and background removal.* — 10 services. JSON: [`catalog/image-generation.json`](catalog/image-generation.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Adobe Firefly Services API](https://developer.adobe.com/firefly-services/) | Generate and edit images and manage creative assets programmatically via Adobe's Firefly REST APIs. | OAuth 2.0 | — | check pricing; requires Adobe Developer Console project and Firefly Services entitlement | [docs](https://developer.adobe.com/firefly-services/docs/firefly-api/) |
| [Black Forest Labs FLUX API](https://bfl.ai) | Generate, edit, and vary FLUX model images from text prompts via REST or the official OAuth MCP server. | API key | [✅](https://mcp.bfl.ai) | paid only, no free tier (FLUX Schnell weights are open for self-hosting) | [docs](https://docs.bfl.ai/quick_start/introduction) |
| [Freepik API](https://www.freepik.com/api) | Generate and edit images programmatically via REST API, plus access Freepik's stock asset library. | API key | — | 🆓 free tier: ~5 EUR of free API credits, then pay-as-you-go | [docs](https://docs.freepik.com) |
| [Google Gemini / Imagen image API](https://ai.google.dev/gemini-api/docs/image-generation) | Generate and multi-turn edit images from text via REST (Nano Banana/Imagen models), up to 4K with reference-image support. | API key | — | check pricing (free API key tier exists but image models are mostly usage-billed) | [docs](https://ai.google.dev/gemini-api/docs/image-generation) |
| [Ideogram API](https://ideogram.ai) | Generate, edit, remix, upscale, and describe images via REST or an official OAuth MCP server, strong at in-image text. | API key | [✅](https://mcp.ideogram.ai/mcp) | no free API credits (web app has 10 slow credits/week); API is pay-per-image, $40 min top-up | [docs](https://developer.ideogram.ai/ideogram-api/api-setup) |
| [Leonardo.Ai API](https://leonardo.ai) | Generate images and videos from text via REST or the official MCP server, with model selection and job status polling. | API key | [✅](https://mcp.leonardo.ai/v1/mcp) | $5 free API credits after account verification, then pay-as-you-go | [docs](https://docs.leonardo.ai/docs/getting-started) |
| [OpenAI Images API (gpt-image)](https://platform.openai.com/docs/guides/image-generation) | Generate, edit, and iteratively refine images from text prompts via REST, with mask-based inpainting and streaming previews. | API key | [◐](https://github.com/SureScaleAI/openai-gpt-image-mcp) | paid only; no free image credits, usage-based billing | [docs](https://platform.openai.com/docs/guides/image-generation) |
| [Recraft API](https://www.recraft.ai) | Generate, edit, upscale, and vectorize images via REST API using Recraft's proprietary models. | API key | [✅](https://github.com/recraft-ai/mcp-recraft-server) | paid only; pay-per-image (from $0.007/image on V4.1 Flash), no confirmed free credits | [docs](https://www.recraft.ai/docs/api-reference/getting-started) |
| [remove.bg API](https://www.remove.bg) | Remove image backgrounds programmatically via a simple REST API with JSON or multipart uploads. | API key | — | 🆓 free: 50 API calls/month (preview/small resolution only), then paid credits | [docs](https://www.remove.bg/api) |
| [Stability AI Platform API](https://platform.stability.ai) | Generate, upscale, and edit images via REST (Stable Image Ultra/Core/SD3 models) using simple credit-based billing. | API key | — | 25 free credits on signup, then pay-as-you-go | [docs](https://platform.stability.ai/docs/api-reference) |

## Video generation and editing

*Text/image-to-video models, talking avatars, programmatic video rendering and video hosting.* — 15 services. JSON: [`catalog/video-generation.json`](catalog/video-generation.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Akool API](https://akool.com) | Generate face-swap, talking avatar, and video-translation content programmatically via REST API. | API key | — | 🆓 free Basic plan with limited credits, no card required | [docs](https://docs.akool.com) |
| [Creatomate API](https://creatomate.com) | Programmatically generate and render videos/images from templates via REST API. | API key | — | 🆓 free trial, 50 API credits | [docs](https://creatomate.com/docs/api/rest-api/authentication) |
| [D-ID API](https://www.d-id.com) | Animate photos into talking-head videos with lip-sync from text or audio via REST API. | API key | [✅](https://docs.d-id.com/mcp) | 14-day trial with 3 minutes of video credits, then paid only (~$5.90/min API) | [docs](https://docs.d-id.com) |
| [Google Veo (Gemini API / Vertex AI)](https://ai.google.dev/gemini-api/docs/video) | Generate video from text or image prompts via Gemini API (api key) or Vertex AI (cloud IAM), incl. Veo 3.1 scene extension. | API key / OAuth | — | no free tier for video; Veo generation requires a paid Gemini API / Vertex AI billing account | [docs](https://ai.google.dev/gemini-api/docs/video) |
| [HeyGen API](https://www.heygen.com) | Create AI avatar/talking-head videos from text or audio, manage avatars and voices, via REST API. | API key / OAuth | [✅](https://mcp.heygen.com/mcp/v1/) | no free API credits since Feb 2026; pay-as-you-go from $5, $0.50-$0.99/credit. Free plan (3 videos/mo) exists but is for the web app, not standalone API. | [docs](https://developers.heygen.com) |
| [Klap API](https://klap.app) | Automatically turn long videos into short clips with captions and reframing via REST API. | API key | — | check pricing (no free API tier found; consumer plans from $14/mo, API is usage-based) | [docs](https://docs.klap.app) |
| [Kling AI API](https://klingai.com) | Generate text-to-video, image-to-video, lip-sync and video effects via REST API with JWT-signed requests. | API key | [◐](https://github.com/199-mcp/mcp-kling) | paid only; prepaid credit packages from $0.14/unit, e.g. 5,000 units/$700, 180-day validity | [docs](https://app.klingai.com/global/dev/document-api/quickStart/userManual) |
| [Luma AI Dream Machine API](https://lumalabs.ai) | Generate and extend AI videos from text or start/end keyframe images via async REST API (Ray 2). | API key | [✅](https://github.com/lumalabs/luma-api-mcp) | paid only; pay-as-you-go, ~$0.60-$1.05 per 5s clip (Ray 2), $5,000/mo cap on default Build tier | [docs](https://docs.lumalabs.ai) |
| [MiniMax Hailuo API](https://www.minimax.io) | Async text-to-video, image-to-video and subject-reference video generation via REST API, up to 1080p. | API key | [✅](https://github.com/MiniMax-AI/MiniMax-MCP) | new accounts get 50 signup credits (~1 short clip); 5s video costs ~45-70 credits, 1000 credits=$1 | [docs](https://platform.minimax.io/docs/api-reference/video-generation-t2v) |
| [Mux Video API](https://www.mux.com) | Upload, encode, stream and analyse video; get playback URLs, thumbnails and captions via REST. | API key | [✅](https://mcp.mux.com) | 🆓 first 100,000 delivered minutes/month free, then usage-based | [docs](https://www.mux.com/docs) |
| [PixVerse API](https://pixverse.ai) | Generate text-to-video, image-to-video, transition and fusion clips (360p-1080p) via REST API. | API key | [✅](https://github.com/PixVerseAI/PixVerse-MCP) | paid only; prepaid credits from $10, ~$0.28-$0.45 per 5s clip | [docs](https://docs.platform.pixverse.ai) |
| [Runway API](https://runwayml.com) | Generate and edit images/video (Gen-4.5) via async task-based REST API: submit, poll, download. | API key | [✅](https://mcp.runwayml.com/mcp) | no free tier; $10 minimum credit top-up, $0.01/credit | [docs](https://docs.dev.runwayml.com) |
| [Shotstack API](https://shotstack.io) | Compose Edit JSON timelines to programmatically render, edit, and template videos, images and audio. | API key | [✅](https://mcp.shotstack.io/) | 10 free credits (valid 30 days), then pay-as-you-go or subscription | [docs](https://shotstack.io/docs/api/) |
| [Synthesia API](https://www.synthesia.io) | Generate AI avatar talking-head videos from text scripts via REST API; supports custom avatars and voices. | API key | — | check pricing (no permanent free API tier; paid plans include API minutes) | [docs](https://docs.synthesia.io/reference/introduction) |
| [Tavus API](https://www.tavus.io) | Create AI video replicas and real-time conversational video agents (CVI) via REST API. | API key | [✅](https://mcp.tavus.io/mcp) | check pricing | [docs](https://docs.tavus.io/api-reference/overview) |

## Speech and audio

*Text-to-speech, speech-to-text, voice cloning, dubbing and audio intelligence.* — 13 services. JSON: [`catalog/audio-speech.json`](catalog/audio-speech.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Amazon Polly / Amazon Transcribe (AWS)](https://aws.amazon.com/polly/) | Convert text to lifelike speech (Polly) and transcribe audio with speaker diarization (Transcribe) via AWS API. | cloud IAM | — | 🆓 free tier: Polly 5M chars/mo standard, Transcribe 60 min/mo (12 months) | [docs](https://docs.aws.amazon.com/polly/latest/dg/what-is.html) |
| [AssemblyAI API](https://www.assemblyai.com) | Transcribe recorded or streaming audio with speaker diarization, sentiment analysis and LLM-based audio insights via REST. | API key | [✅](https://mcp.assemblyai.com/docs) | 🆓 free tier: $50 credit, no card required | [docs](https://www.assemblyai.com/docs) |
| [Azure AI Speech](https://azure.microsoft.com/products/ai-services/ai-speech) | Convert text to speech, transcribe speech to text and translate speech via REST or Speech SDK. | cloud IAM | [✅](https://github.com/microsoft/azure-speech-mcp-server) | 🆓 free tier (F0): 5 audio hrs/mo STT, 0.5M chars/mo neural TTS | [docs](https://learn.microsoft.com/azure/ai-services/speech-service/) |
| [Cartesia API](https://cartesia.ai) | Generate low-latency real-time text-to-speech, transcribe speech and clone voices via REST/WebSocket API. | API key | [✅](https://mcp.cartesia.ai/mcp) | 🆓 free tier: 20,000 credits/mo | [docs](https://docs.cartesia.ai) |
| [Deepgram API](https://deepgram.com) | Transcribe batch or streaming audio with diarization, synthesize speech, and run real-time voice agents via REST/WebSocket. | API key | [✅](https://github.com/deepgram/mcp) | 🆓 free tier: $200 credit, no card required | [docs](https://developers.deepgram.com/reference/deepgram-api-overview) |
| [ElevenLabs API](https://elevenlabs.io) | Generate, clone and stream text-to-speech voices and transcribe audio via REST/WebSocket API. | API key | [✅](https://github.com/elevenlabs/elevenlabs-mcp) | 🆓 free plan: limited monthly credits | [docs](https://elevenlabs.io/docs/api-reference/introduction) |
| [Google Cloud Text-to-Speech / Speech-to-Text](https://cloud.google.com/text-to-speech) | Synthesize lifelike speech from text and transcribe audio to text via REST/gRPC using GCP credentials. | cloud IAM | — | 🆓 free tier: TTS 4M chars/mo standard, STT 60 min/mo | [docs](https://cloud.google.com/text-to-speech/docs) |
| [Hume AI API](https://www.hume.ai) | Generate expressive text-to-speech and run real-time empathic voice conversations (EVI) via REST/WebSocket. | API key | [✅](https://dev.hume.ai/_mcp/server) | 🆓 free plan: 10,000 TTS chars/mo + 5 EVI min/mo | [docs](https://dev.hume.ai/docs) |
| [Murf AI API](https://murf.ai) | Generate AI voiceovers, clone voices and dub audio in 35+ languages via REST API. | API key | — | check pricing | [docs](https://murf.ai/api/docs/introduction/overview) |
| [OpenAI Audio API (TTS / transcription)](https://platform.openai.com/docs/guides/audio) | Synthesize speech with TTS models and transcribe or translate audio with Whisper/GPT-4o transcribe via REST. | API key | — | paid only (pay-per-use) | [docs](https://platform.openai.com/docs/guides/audio) |
| [Resemble AI API](https://www.resemble.ai) | Synthesize speech, clone voices, convert speech-to-speech and detect deepfake audio via REST API. | API key | [✅](https://docs.resemble.ai/_mcp/server) | 🆓 pay-as-you-go Flex plan ($0/mo base) | [docs](https://docs.resemble.ai/) |
| [Rev AI API](https://www.rev.ai) | Submit audio for asynchronous or streaming speech-to-text transcription, plus sentiment and topic extraction, via REST. | API key | [✅](https://docs.rev.ai/) | trial credits (about 5 hours of ASR) | [docs](https://docs.rev.ai/) |
| [Speechmatics API](https://www.speechmatics.com) | Transcribe audio in batch or real time with speaker diarization across many languages via REST/WebSocket. | API key | [◐](https://glama.ai/mcp/servers/ArchieMcM234/speechmatics_claude_code_mcp) | 🆓 free tier: 480 min/mo batch transcription | [docs](https://docs.speechmatics.com) |

## Music generation

*Generate songs, instrumentals, loops and sound effects from prompts.* — 6 services. JSON: [`catalog/music-generation.json`](catalog/music-generation.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Beatoven.ai API](https://www.beatoven.ai) | Generate royalty-cleared background music and sound effects from text prompts via REST API (Maestro). | API key | — | check pricing | [docs](https://www.beatoven.ai/api) |
| [ElevenLabs Music API](https://elevenlabs.io/music) | Generate original music tracks from text prompts or detailed composition plans via REST API, with commercial licensing. | API key | [✅](https://github.com/elevenlabs/elevenlabs-mcp) | shares ElevenLabs account credit pool (limited free credits on sign-up); check pricing for per-track cost | [docs](https://elevenlabs.io/docs/api-reference/music/compose) |
| [Loudly API](https://www.loudly.com) | Generate, remix, stem-split, and master music tracks programmatically via REST API. | API key | — | 🆓 free track allowance on signup, then volume-based pay-as-you-go pricing | [docs](https://www.loudly.com/developers) |
| [Mubert API](https://mubert.com/api) | Generate streaming or file-based background music from text/image prompts via REST/WebRTC API, 15s-25min tracks. | API key | — | paid only; plans start at $49/mo (100 generations/mo), no free tier | [docs](https://mubert.com/api) |
| [Soundraw API](https://soundraw.io) | Generate royalty-free background music tracks by mood, genre, and duration via REST API for embedding in apps. | API key | — | paid only; Starter plan $29.99/mo for 100 songs/mo, no free tier confirmed | [docs](https://docs.channel.io/soundraw-faq/en/articles/SOUNDRAW-API-fbf580fd) |
| [Stable Audio API (Stability AI)](https://platform.stability.ai) | Generate music and sound effects from text prompts via REST API (Stable Audio 2.0 models), up to 3 minutes. | API key | — | shares Stability AI platform credits; 25 free credits on signup, then pay-as-you-go | [docs](https://platform.stability.ai/docs/api-reference) |

## 3D generation and assets

*Text/image-to-3D mesh generation, texturing and 3D asset libraries.* — 7 services. JSON: [`catalog/3d-generation.json`](catalog/3d-generation.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [CSM (Common Sense Machines) API](https://www.csm.ai) | Create 3D assets and multi-part kits from images via async REST sessions (image-to-3D, retopology). | API key | [◐](https://lobehub.com/mcp/commonsensemachines-blender-mcp) | 🆓 limited free tier (watermarked outputs); full API access is bundled with mid-tier ($19.99+/mo) or higher Cube subscriptions | [docs](https://docs.csm.ai/quick-start) |
| [Hyper3D Rodin API](https://hyper3d.ai) | Generate 3D meshes from text or images (sketch/regular/detail quality tiers) via an async REST job API. | API key | — | 10 starter credits on signup (spent only on downloads, not generation); paid credits $1.5 each | [docs](https://developer.hyper3d.ai/api-specification/overview_reset_v) |
| [Meshy API](https://www.meshy.ai) | Generate, retexture, rig, and animate 3D models from text or images via REST API or official MCP server. | API key | [✅](https://github.com/meshy-dev/meshy-mcp-server) | 🆓 free web plan: 100 credits/mo; API key creation requires a paid plan (Pro $20/mo+) | [docs](https://docs.meshy.ai/en/api/quick-start) |
| [Sketchfab Data API](https://sketchfab.com/developers) | Search, download, and upload 3D models on Sketchfab programmatically via the REST Data API v3. | API key / OAuth | [◐](https://github.com/gregkop/sketchfab-mcp-server) | 🆓 free, no key needed for public search; private API token is free with any Sketchfab account | [docs](https://sketchfab.com/developers/data-api/v3) |
| [Stability AI 3D (Stable Fast 3D / SPAR3D) API](https://platform.stability.ai) | Convert a single 2D image into a textured 3D mesh (GLB) via the v2beta/3d REST endpoints. | API key | — | 25 free credits on signup, then pay-as-you-go (Stable Fast 3D costs 10 credits ~ $0.10/generation) | [docs](https://platform.stability.ai/docs/api-reference#tag/3D) |
| [Tencent Hunyuan3D API](https://3d.hunyuan.tencent.com) | Generate textured 3D meshes (GLB, PBR) from text, images, or sketches via Tencent Cloud's Hunyuan 3D API. | cloud IAM | — | pay-as-you-go from ~$0.02/generation; some enterprise sign-ups get bundled free credits | [docs](https://www.tencentcloud.com/document/product/1284/75539) |
| [Tripo API](https://www.tripo3d.ai) | Generate textured 3D meshes from text or images via REST API, with an official MCP server for agents. | API key | [✅](https://github.com/VAST-AI-Research/tripo-mcp) | 🆓 free/trial credits on signup (amounts and promos change, e.g. ~300 credits/2 weeks); pay-as-you-go at $0.01/credit | [docs](https://developers.tripo3d.ai/en/docs/authentication) |

## Architecture, CAD and BIM

*Building information models, CAD geometry, construction management and GIS platforms with programmatic access.* — 9 services. JSON: [`catalog/architecture-cad-bim.json`](catalog/architecture-cad-bim.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Autodesk Platform Services (APS)](https://aps.autodesk.com) | Upload, translate, view and automate CAD/BIM files (Model Derivative, Data Management, Design Automation) via REST APIs. | OAuth 2.0 | — | 🆓 free trial credits, then pay-as-you-go | [docs](https://aps.autodesk.com/en/docs/) |
| [Bentley iTwin Platform APIs](https://developer.bentley.com) | Create, manage and query digital twins, iModels and reality/reporting data for infrastructure projects via REST APIs. | OAuth 2.0 | — | 🆓 free developer sign-up/trial, then consumption-based pricing | [docs](https://developer.bentley.com/apis/) |
| [Esri ArcGIS Location Platform](https://location.arcgis.com) | Geocode addresses, render maps, run spatial analysis and manage geospatial site data via REST APIs and SDKs. | API key / OAuth | — | 🆓 free tier with monthly free credits, then usage-based pricing | [docs](https://developers.arcgis.com/documentation/) |
| [Onshape REST API](https://onshape-public.github.io/docs/) | Create, read and modify Onshape CAD documents, parts, assemblies and drawings programmatically via REST API. | API key / OAuth | — | 🆓 free tier (public documents only); private documents need a paid plan | [docs](https://onshape-public.github.io/docs/) |
| [Procore API](https://developers.procore.com) | Read and write construction project data - RFIs, submittals, drawings, budgets, schedules - via REST API. | OAuth 2.0 | — | 🆓 free developer sandbox; production requires customer's paid Procore plan | [docs](https://developers.procore.com/reference/rest/v1) |
| [Rhino.Compute (McNeel)](https://www.rhino3d.com/compute) | Run Rhino/Grasshopper geometry operations headlessly via a stateless REST API you deploy yourself. | API key | — | 🆓 self-hosted only; requires a Rhino license, cloud deployment billed by core-hour | [docs](https://developer.rhino3d.com/guides/compute/) |
| [Speckle API](https://speckle.systems) | Send, receive and query 3D/BIM model data across CAD tools (Revit, Rhino, Grasshopper, Tekla) via GraphQL API and SDKs. | API key / OAuth | — | 🆓 free Explore plan (1 project, 3 users), unlimited API calls | [docs](https://docs.speckle.systems/dev/) |
| [Trimble Connect API](https://developer.trimble.com) | Manage Trimble Connect projects, files, BIM models, issues/topics and metadata via REST APIs (Core, Model, Organizer). | OAuth 2.0 | — | check pricing | [docs](https://developer.trimble.com/docs/connect) |
| [Zoo Text-to-CAD API (KittyCAD)](https://zoo.dev) | Generate 3D CAD models from text prompts and run modeling/file-conversion operations via REST API. | API key | — | start free trial credits, then usage-based pay-as-you-go | [docs](https://zoo.dev/docs/api) |

## Diagrams and software architecture

*Render or edit diagrams (Mermaid, PlantUML, C4), whiteboards and architecture models.* — 9 services. JSON: [`catalog/diagrams-software-architecture.json`](catalog/diagrams-software-architecture.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Eraser API (DiagramGPT)](https://www.eraser.io) | Generate diagrams from text prompts (DiagramGPT) and manage Eraser files programmatically via REST API. | API key | — | paid only - API tokens require an active paid team plan | [docs](https://docs.eraser.io/reference/getting-started) |
| [IcePanel API](https://icepanel.io) | Programmatically create, read, import, and export C4-style architecture landscapes and models via REST API. | API key | — | 🆓 free tier: 10,000 read requests/mo, 1,000 write requests/mo, 5 import/export requests/mo | [docs](https://developer.icepanel.io/) |
| [Kroki](https://kroki.io) | Render 25+ diagram-as-code formats (PlantUML, Mermaid, C4, GraphViz, BPMN, etc.) from text via a free HTTP GET/POST API. | none | — | 🆓 free, no key; public hosted instance at kroki.io sponsored by Exoscale (no SLA) | [docs](https://docs.kroki.io/kroki/) |
| [Lucid (Lucidchart) REST API](https://developer.lucid.co) | Create, read, search, and manage Lucidchart documents and folders programmatically via REST API. | API key / OAuth | — | check pricing | [docs](https://developer.lucid.co) |
| [Mermaid Chart API](https://www.mermaidchart.com) | Validate, render, and save Mermaid diagrams via Mermaid Chart's official MCP server using an account API token. | API key | [✅](https://mcp.mermaid.ai/mcp) | 🆓 unauthenticated MCP validate/render tools are free; saving to a Mermaid Chart account needs a token, check pricing for limits | [docs](https://mermaid.ai/docs/ai/mcp-server) |
| [Miro REST API](https://developers.miro.com) | Create/read boards and items via REST API, or use Miro's official MCP server to search, build, and summarize boards. | OAuth 2.0 | [✅](https://mcp.miro.com/) | 🆓 free plan allows up to 3 editable team boards; MCP server available on all plans including free | [docs](https://developers.miro.com/docs) |
| [Napkin AI API](https://www.napkin.ai) | Generate diagrams, flowcharts, mind maps, and charts from text via REST API, exporting to SVG, PNG, or PPT. | API key | — | 🆓 included on every plan; any account can create a token and call the API, limited by credits | [docs](https://api.napkin.ai/) |
| [PlantUML Server API](https://plantuml.com) | Render UML and architecture-as-code diagrams to PNG/SVG/ASCII via a free public HTTP GET API using encoded diagram text. | none | — | 🆓 free, no key; public hosted server at plantuml.com/plantuml | [docs](https://plantuml.com/server) |
| [Structurizr](https://structurizr.com) | Create and update C4-model software architecture diagram workspaces as JSON via a signed HTTPS API. | API key | — | 🆓 free tier: workspaces up to 0.5MB; paid plans raise the limit to 5MB | [docs](https://docs.structurizr.com/cloud/workspace-api) |

## Design and UI

*Read and write design files, generate branded graphics and publish websites.* — 6 services. JSON: [`catalog/design-ui.json`](catalog/design-ui.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Canva Connect API](https://www.canva.dev) | Programmatically create, autofill, and export Canva designs, and manage assets and comments via a REST API. | OAuth 2.0 | — | check pricing (free to build/test; public apps require Canva review before production use) | [docs](https://www.canva.dev/docs/connect/) |
| [Figma REST API / Dev Mode MCP](https://www.figma.com/developers) | Read and write Figma file/comment/component data via REST, and feed live design context to coding agents via the official Dev Mode MCP server. | API key / OAuth | [✅](https://mcp.figma.com/mcp) | 🆓 free: personal access tokens work on free plan, rate-limited per seat/plan tier; MCP free during beta | [docs](https://developers.figma.com/docs/rest-api/) |
| [Framer](https://www.framer.com) | Automate publishing of Framer sites programmatically (get project info, publish previews, promote to production) via a Node SDK. | API key | — | check pricing (no separate API fee found; scoped to a Framer project/site plan) | [docs](https://www.framer.com/developers/server-api-quick-start) |
| [Penpot API](https://penpot.app) | Read, create, and modify Penpot design files, comments, and webhooks via a token-authenticated RPC/REST API, or via the official MCP server. | API key | [✅](https://penpot.app/ai/mcp-server) | 🆓 free tier: free cloud account (design.penpot.app) plus free, open-source self-hosting | [docs](https://design.penpot.app/api/_doc) |
| [v0 Platform API (Vercel)](https://v0.app) | Generate full UI/frontend code from natural-language prompts, iterate via chat, and deploy the result directly to Vercel via REST API. | API key | — | check pricing (usage-based; credits included on v0 Premium/Team plans, no separate free API key tier confirmed) | [docs](https://v0.app/docs/api) |
| [Webflow Data API](https://developers.webflow.com) | Create/update CMS collections, items, and pages, and publish Webflow sites programmatically via REST API or the official MCP server. | API key / OAuth | [✅](https://developers.webflow.com/_mcp/server) | check pricing (API access itself is free with a token; some CMS/publish actions require the site to be on a paid Webflow plan) | [docs](https://developers.webflow.com/data/reference/rest-introduction) |

## Documents, OCR and presentations

*Parse PDFs and scans, convert file formats, generate slides and collect e-signatures.* — 14 services. JSON: [`catalog/presentations-documents.json`](catalog/presentations-documents.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Adobe PDF Services API](https://developer.adobe.com/document-services/) | Programmatically create, convert, combine, compress, OCR, and extract data from PDF documents. | OAuth 2.0 | — | 🆓 free tier: 500 document transactions/month, no credit card required | [docs](https://developer.adobe.com/document-services/docs/overview/pdf-services-api/) |
| [AWS Textract](https://aws.amazon.com/textract/) | Detect and extract text, forms, tables, and data from scanned documents and images via API calls. | cloud IAM | [◐](https://github.com/ag2-mcp-servers/amazon-textract) | 🆓 free tier: 1,000 pages/month (DetectDocumentText & AnalyzeDocument, each) for first 3 months; AnalyzeExpense/AnalyzeID get 150 pages/month free | [docs](https://docs.aws.amazon.com/textract/latest/dg/what-is.html) |
| [Azure AI Document Intelligence](https://azure.microsoft.com/products/ai-services/ai-document-intelligence) | Analyze forms, invoices, receipts, and scanned documents to extract structured JSON via REST API. | cloud IAM | — | 🆓 free tier: F0 pricing tier, 500 pages/month, rate-limited | [docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/) |
| [CloudConvert API](https://cloudconvert.com/api/v2) | Convert, compress, merge, watermark, and OCR files across 200+ formats via REST API or MCP. | API key / OAuth | [✅](https://mcp.cloudconvert.com) | 🆓 free: 25 conversion minutes/day for the web tool; paid credit packages for the API; free Sandbox API for unlimited test jobs without consuming credits | [docs](https://cloudconvert.com/api/v2) |
| [DocuSign eSignature API](https://developers.docusign.com) | Send, sign, track, and manage electronic signature envelopes and agreement workflows via REST API. | OAuth 2.0 | [✅](https://developers.docusign.com/platform/mcp-server/) | 🆓 free developer/demo sandbox account (account-d.docusign.com) with unlimited test envelopes; production use requires a paid DocuSign plan | [docs](https://developers.docusign.com/docs/esign-rest-api/) |
| [Gamma API](https://gamma.app) | Generate, poll, and export AI-made presentations, documents, or social posts as PDF/PPTX via REST API. | API key / OAuth | [✅](https://mcp.gamma.app/mcp) | paid only: requires Pro, Ultra, Teams, or Business plan; no free API tier | [docs](https://developers.gamma.app/generations/create-generation) |
| [Google Document AI](https://cloud.google.com/document-ai) | Extract text, tables, and structured data from documents like invoices, forms, and IDs via REST API. | cloud IAM | — | 🆓 free tier: 1,000 pages/month per processor type, then $0.65-$10 per 1,000 pages | [docs](https://cloud.google.com/document-ai/docs/reference/rest) |
| [Google Slides / Docs API](https://developers.google.com/slides) | Read and programmatically edit Google Slides presentations (slides, shapes, text, tables) via REST API or MCP. | OAuth 2.0 | [✅](https://slidesmcp.googleapis.com/mcp) | 🆓 free, no key (standard Google API usage quotas apply; requires GCP project + OAuth consent) | [docs](https://developers.google.com/workspace/slides/api/reference/rest) |
| [LlamaParse (LlamaCloud)](https://www.llamaindex.ai/llamaparse) | Parse, classify, extract, and split complex documents (tables, forms, charts) into LLM-ready structured data via API. | API key | [✅](https://mcp.llamaindex.ai/mcp) | check pricing: credit-based at $1.25/1,000 credits (1-45+ credits/page depending on tier); 48h parse cache is free to re-query | [docs](https://developers.llamaindex.ai/llamaparse/) |
| [Mistral OCR API](https://mistral.ai) | Extract text, tables, and layout structure from PDFs and images as structured Markdown/JSON via REST API. | API key | [◐](https://github.com/D-Diaa/mistral-ocr-mcp) | paid only: $4/1,000 pages (OCR), $5/1,000 pages (Document AI); 50% off via Batch API; no free tier confirmed | [docs](https://docs.mistral.ai/capabilities/OCR/basic_ocr/) |
| [PDF.co API](https://pdf.co) | Convert, merge, split, edit, fill forms, OCR, and extract data from PDFs via REST API. | API key | — | trial credits: 10,000 credits for 1 month, no credit card required | [docs](https://developer.pdf.co) |
| [Reducto API](https://reducto.ai) | Parse, extract, split, edit, and classify complex documents into structured JSON/Markdown via REST API or SDKs. | API key | [✅](https://docs.reducto.ai/mcp-server) | 🆓 15,000 free credits (~$150 value) for new Standard accounts; extra credits via Startup Program for qualifying early-stage teams | [docs](https://docs.reducto.ai/get-started/quickstart) |
| [SlideSpeak API](https://slidespeak.co) | Generate, edit, and download PowerPoint/PDF presentations from text, documents, or outlines via REST API. | API key | [✅](https://github.com/SlideSpeak/slidespeak-mcp) | check pricing (no free tier confirmed on docs; requires API key from developer settings) | [docs](https://docs.slidespeak.co/v1/quickstart) |
| [Unstructured API](https://unstructured.io) | Partition and extract structured elements (text, tables, layout) from PDFs, docs, and images for RAG pipelines via API. | API key | [✅](https://github.com/Unstructured-IO/UNS-MCP) | check pricing: low-cost entry tier plus Pay-As-You-Go per-page billing; no explicit free quota confirmed | [docs](https://docs.unstructured.io/api-reference/overview) |

## Translation and language

*Machine translation, grammar and style checking.* — 6 services. JSON: [`catalog/translation-language.json`](catalog/translation-language.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Amazon Translate](https://aws.amazon.com/translate/) | Translate text and documents in real time or batch across 75+ languages via the AWS SDK/API. | cloud IAM | ◐ | 🆓 free tier: 2M characters/month for 12 months (new AWS accounts) | [docs](https://docs.aws.amazon.com/translate/) |
| [Azure AI Translator](https://azure.microsoft.com/products/ai-services/ai-translator) | Translate text, detect language, and transliterate across 100+ languages via REST API within Azure AI Services. | API key | ◐ | 🆓 free tier (F0): 2,000,000 characters/month | [docs](https://learn.microsoft.com/azure/ai-services/translator/) |
| [DeepL API](https://www.deepl.com/pro-api) | Translate and rephrase text or documents between 30+ languages via REST API, SDKs, or an official MCP server. | API key | [✅](https://github.com/DeepL/deepl-mcp-server) | API Free plan retired mid-2026 for new signups; now Developer/Growth paid plans with trial credits | [docs](https://developers.deepl.com/docs) |
| [Google Cloud Translation](https://cloud.google.com/translate) | Translate text/documents and detect language across 100+ languages via REST/gRPC API within Google Cloud. | cloud IAM | ◐ | 🆓 free tier: 500,000 characters/month (permanent, not a trial) | [docs](https://cloud.google.com/translate/docs) |
| [LanguageTool API](https://languagetool.org/http-api/) | Check grammar, style, and spelling in 30+ languages via a public HTTP API, with an optional Premium key for higher limits. | API key | ◐ | 🆓 free, no key needed on public endpoint (rate-limited: 20 req/min, 75,000 chars/min) | [docs](https://languagetool.org/http-api/) |
| [ModernMT API](https://www.modernmt.com) | Send adaptive neural machine translation requests with in-context learning via a REST API. | API key | — | 🆓 free trial (no credit card); no permanent free tier, paid plans from $8/M characters | [docs](https://www.modernmt.com/api) |

## Code execution sandboxes

*Isolated cloud environments where an agent can run code, shells and whole dev environments safely.* — 10 services. JSON: [`catalog/code-execution-sandbox.json`](catalog/code-execution-sandbox.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Cloudflare Sandbox SDK](https://developers.cloudflare.com/sandbox/) | Deploy a Cloudflare Worker embedding this SDK to run untrusted code in per-request container sandboxes. | API key | — | requires Workers Paid plan ($5/mo) for Containers; no free tier for container-backed sandboxes | [docs](https://developers.cloudflare.com/sandbox/api/) |
| [CodeSandbox SDK](https://codesandbox.io/sdk) | Programmatically create, resume, and control cloud VM sandboxes to run and preview AI-written code. | API key | — | 🆓 Free plan: 400 VM credits/mo (~40 Nano-VM hrs), up to 10 concurrent VMs | [docs](https://codesandbox.io/docs/sdk) |
| [Daytona](https://www.daytona.io) | Create elastic remote sandboxes via SDK/API to run AI-generated code with sub-second startup. | API key | [✅](https://www.daytona.io/docs/en/mcp/) | 🆓 $200 free compute credit + 5GB storage, no credit card required | [docs](https://www.daytona.io/docs) |
| [E2B](https://e2b.dev) | Spin up isolated Firecracker cloud sandboxes via SDK/REST to execute AI-generated code and return results. | API key | [✅](https://github.com/e2b-dev/mcp-server) | 🆓 free Hobby tier with limited sandbox hours, then pay-as-you-go | [docs](https://e2b.dev/docs) |
| [Judge0](https://judge0.com) | Submit source code and stdin via REST to compile/run it in 60+ languages and poll for the result. | API key | — | 🆓 RapidAPI free Basic plan (rate-limited); self-host free & open-source (GPLv3) | [docs](https://ce.judge0.com/) |
| [Modal](https://modal.com) | Programmatically launch serverless sandboxes, optionally with GPUs, to execute untrusted or agent code. | API key | [◐](https://github.com/milkymap/mcp4modal_sandbox) | 🆓 Starter plan: $0 base + $30/mo free credits | [docs](https://modal.com/docs/guide/sandboxes) |
| [Piston](https://github.com/engineer-man/piston) | Call a free public REST API to compile and run code in 70+ languages inside isolated containers. | none | — | 🆓 free, no key, public instance rate-limited (~5 req/sec); self-host for unlimited/production use | [docs](https://piston.readthedocs.io/en/latest/api-v2/) |
| [Riza](https://riza.io) | Call a REST API to execute untrusted Python/JS/Ruby/PHP code in sandboxes that start in under 10ms. | API key | [✅](https://mcp.riza.io/code-interpreter) | 🆓 free for side projects/low usage, then usage-based pricing | [docs](https://docs.riza.io/api-reference/command/execute-code) |
| [Runloop](https://www.runloop.ai) | Create, snapshot, suspend/resume, and run commands in Linux Devboxes via API/SDK for agent coding tasks. | API key | — | $50 free credits on signup, then usage-based ($0.108/CPU-hr, $0.0252/GB-hr) | [docs](https://docs.runloop.ai/docs/devboxes/overview) |
| [Vercel Sandbox](https://vercel.com/docs/vercel-sandbox) | Boot ephemeral Firecracker microVMs via SDK/REST to run agent- or AI-generated code and shell commands. | API key / OAuth | [✅](https://vercel.com/docs/mcp) | 🆓 usage included on Hobby plan, otherwise usage-based on Pro/Enterprise | [docs](https://vercel.com/docs/sandbox) |

## Developer platforms and DevOps

*Source control, deployment, cloud infrastructure, monitoring and incident management.* — 17 services. JSON: [`catalog/developer-devops.json`](catalog/developer-devops.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [AWS APIs](https://aws.amazon.com) | An agent can provision and control thousands of AWS resources (compute, storage, databases, ML) via SDKs/CLI/REST. | cloud IAM | [✅](https://github.com/awslabs/mcp) | 🆓 new accounts get up to $200 in credits plus free usage of 90+ services for up to 6 months; some services also have a perpetual Always Free tier | [docs](https://docs.aws.amazon.com/general/latest/gr/aws-apis-references.html) |
| [Azure APIs](https://learn.microsoft.com/rest/api/azure/) | An agent can deploy and manage Azure resources (compute, storage, databases, AI) across resource-provider REST APIs. | cloud IAM | [✅](https://github.com/microsoft/mcp) | 🆓 12 months of select free services plus $200 credit for 30 days for new accounts; many services also have a permanent always-free monthly amount | [docs](https://learn.microsoft.com/rest/api/azure/) |
| [CircleCI API](https://circleci.com/docs/api/v2/) | An agent can trigger pipelines, rerun workflows, fetch logs/test results, and validate CI/CD configuration via REST. | API key | [✅](https://github.com/CircleCI-Public/mcp-server-circleci) | 🆓 free plan: 30,000 credits/month (~6,000 build minutes on a small Docker resource class), credits expire monthly | [docs](https://circleci.com/docs/api/v2/) |
| [Cloudflare API](https://developers.cloudflare.com/api/) | An agent can manage DNS, Workers, zones, WAF/security rules, and caching for Cloudflare accounts programmatically. | API key / OAuth | [✅](https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/) | 🆓 free with any Cloudflare account; API access itself is free, manages both free and paid Cloudflare products | [docs](https://developers.cloudflare.com/api/) |
| [Datadog API](https://docs.datadoghq.com/api/) | An agent can query metrics, logs, traces, monitors, and dashboards, and manage Datadog configuration via REST. | API key | [✅](https://docs.datadoghq.com/mcp_server/setup/) | 🆓 free Infrastructure Monitoring plan: 1-day metric retention, up to 5 hosts; other products (APM, Logs, Security) are paid | [docs](https://docs.datadoghq.com/api/) |
| [Docker Hub API](https://docs.docker.com/docker-hub/api/latest/) | An agent can search, push, pull, tag, and manage container images and repositories on Docker Hub. | API key | [✅](https://github.com/docker/hub-mcp) | 🆓 free personal accounts with rate-limited image pulls; paid Pro/Team/Business tiers raise pull limits | [docs](https://docs.docker.com/reference/api/hub/latest/) |
| [Fly.io Machines API](https://fly.io/docs/machines/api/) | An agent can create, start, stop, and destroy Fly.io Machines (lightweight VMs) programmatically via REST. | API key | [✅](https://docs.fly.io/sprites/integrations/remote-mcp) | no perpetual free tier; pay-as-you-go billing with trial credit for new accounts | [docs](https://fly.io/docs/machines/api/) |
| [GitHub API](https://docs.github.com/rest) | An agent can manage repositories, issues, pull requests, releases, and code search via REST or GraphQL. | API key / OAuth | [✅](https://github.com/github/github-mcp-server) | 🆓 free with any GitHub account; 5,000 req/hr authenticated, 60/hr unauthenticated | [docs](https://docs.github.com/rest) |
| [GitLab API](https://docs.gitlab.com/api/) | An agent can manage projects, issues, merge requests, CI/CD pipelines, and repository files via REST/GraphQL. | API key / OAuth | [✅](https://docs.gitlab.com/user/model_context_protocol/mcp_server/) | 🆓 free tier: full REST API access on GitLab.com Free plan; some features gated to Premium/Ultimate | [docs](https://docs.gitlab.com/api/) |
| [Google Cloud APIs](https://cloud.google.com/apis) | An agent can create and manage Google Cloud resources (compute, storage, data, AI/ML) via REST, gRPC, or client libraries. | cloud IAM | [✅](https://github.com/googleapis/genai-toolbox) | 🆓 free trial credit for new customers plus an Always Free tier with perpetual no-cost limits on select products | [docs](https://cloud.google.com/apis/docs/overview) |
| [Netlify API](https://docs.netlify.com/api/get-started/) | An agent can create/manage sites, trigger and monitor deploys, and configure DNS, domains, and env vars. | API key / OAuth | [✅](https://netlify-mcp.netlify.app/mcp) | 🆓 free Starter plan; API usage subject to account plan limits | [docs](https://docs.netlify.com/api/get-started/) |
| [PagerDuty API](https://developer.pagerduty.com) | An agent can create/manage incidents, on-call schedules, escalation policies, and services via REST. | API key / OAuth | [✅](https://github.com/PagerDuty/pagerduty-mcp-server) | 🆓 free plan for up to 5 users: 100 monthly SMS/phone notifications, 1 on-call schedule, 1 escalation policy, API access | [docs](https://developer.pagerduty.com) |
| [Postman API](https://www.postman.com/postman/postman-public-workspace/) | An agent can manage Postman collections, workspaces, environments, mocks, monitors, and API specs via REST. | API key | [✅](https://learning.postman.com/_mcp/server) | 🆓 free plan available; rate limits ~300 req/min general, stricter for specific endpoints | [docs](https://learning.postman.com/api-docs/api-reference/) |
| [Render API](https://render.com/docs/api) | An agent can create and manage Render services, trigger deployments, and configure databases and env vars. | API key | [✅](https://mcp.render.com/mcp) | 🆓 free static sites; free web services that spin down after inactivity | [docs](https://api-docs.render.com/reference/introduction) |
| [Sentry API](https://docs.sentry.io/api/) | An agent can query and triage error/performance issues and manage projects, releases, and org data. | API key / OAuth | [✅](https://mcp.sentry.dev/mcp) | 🆓 free Developer plan: 1 user, 5,000 errors/mo, 5GB logs, 50 replays; includes MCP access | [docs](https://docs.sentry.io/api/) |
| [Supabase Management API](https://supabase.com/docs/reference/api) | An agent can programmatically create and manage Supabase projects, databases, API keys, and config. | API key / OAuth | [✅](https://mcp.supabase.com/mcp) | 🆓 free plan available; rate limit 120 req/min per user/project (lower for heavier endpoints) | [docs](https://supabase.com/docs/reference/api) |
| [Vercel API](https://vercel.com/docs/rest-api) | An agent can create deployments, manage projects/domains/env vars, and query analytics and logs. | API key / OAuth | [✅](https://mcp.vercel.com) | 🆓 free on Hobby plan; some resources/endpoints require Pro/paid plan | [docs](https://vercel.com/docs/rest-api) |

## Databases, vector stores and memory

*Managed SQL/NoSQL databases, vector search and long-term memory layers for agents.* — 18 services. JSON: [`catalog/databases-vector-memory.json`](catalog/databases-vector-memory.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Chroma Cloud](https://www.trychroma.com) | Create databases and store/query vector embeddings for retrieval via REST/SDK or MCP server. | API key | [✅](https://github.com/chroma-core/chroma-mcp) | 🆓 freemium: ~1M embeddings plus free credits, no card for signup | [docs](https://docs.trychroma.com) |
| [ClickHouse Cloud](https://clickhouse.com) | Run SQL analytics queries and manage Cloud services/backups via REST API or official MCP server. | API key | [✅](https://github.com/ClickHouse/mcp-clickhouse) | no permanent free tier; 30-day trial with $300 credits | [docs](https://clickhouse.com/docs/products/cloud/features/admin-features/api/api-overview) |
| [Convex](https://www.convex.dev) | Introspect tables/functions, call functions, and read/write data in a reactive database via MCP or client SDKs. | API key | [✅](https://github.com/get-convex/convex-backend) | 🆓 generous free tier for small apps, zero cost/maintenance | [docs](https://docs.convex.dev/ai/convex-mcp-server) |
| [Google BigQuery](https://cloud.google.com/bigquery) | Run SQL queries and inspect datasets/tables in BigQuery via REST API or the fully-managed remote MCP server. | cloud IAM | [✅](https://bigquery.googleapis.com/mcp) | 🆓 free tier: 1TB queries/mo, 10GB storage/mo | [docs](https://docs.cloud.google.com/bigquery/docs/reference/mcp) |
| [Letta](https://www.letta.com) | Create and run stateful agents with persistent memory blocks via REST API or hosted MCP server. | API key | [✅](https://api.letta.com/mcp) | 🆓 free personal tier with rotating free models; usage-based billing beyond that | [docs](https://docs.letta.com) |
| [Mem0](https://mem0.ai) | Add, search, update, and delete long-term agent memories via REST API or hosted MCP server. | API key | [✅](https://mcp.mem0.ai/mcp/) | 🆓 free (Hobby) tier: 10K add requests, 1K retrievals/mo, 1 project | [docs](https://docs.mem0.ai) |
| [MongoDB Atlas](https://www.mongodb.com/atlas) | Create/manage Atlas clusters and query MongoDB data via Admin API, drivers, or official MCP server. | API key / OAuth | [✅](https://github.com/mongodb-js/mongodb-mcp-server) | 🆓 free tier: M0 cluster free forever (512MB) | [docs](https://www.mongodb.com/docs/atlas/api/atlas-admin-api-ref/) |
| [Neon Postgres](https://neon.com) | Provision and manage serverless Postgres projects/branches and run SQL via REST API or MCP server. | API key / OAuth | [✅](https://github.com/neondatabase/mcp-server-neon) | 🆓 free tier: 1 project, 0.5GB storage | [docs](https://api-docs.neon.tech/reference/getting-started-with-neon-api) |
| [Pinecone](https://www.pinecone.io) | Upsert, query, and rerank vector embeddings in managed indexes via REST/SDK or MCP server. | API key | [✅](https://github.com/pinecone-io/pinecone-mcp) | 🆓 free tier (Starter plan, limited pods/reads) | [docs](https://docs.pinecone.io/guides/operations/mcp-server) |
| [PlanetScale](https://planetscale.com) | Manage MySQL databases, branches, and schema, and view Insights via hosted MCP server or API. | API key / OAuth | [✅](https://mcp.pscale.dev/mcp/planetscale) | 🆓 free tier available (Hobby plan) | [docs](https://planetscale.com/docs/connect/mcp) |
| [Qdrant Cloud](https://qdrant.tech) | Create clusters and store/search vector embeddings via REST/gRPC API, SDKs, or official MCP server. | API key | [✅](https://github.com/qdrant/mcp-server-qdrant) | 🆓 free tier: 1GB disk / 1 node cluster, no card; suspends after 1 week idle | [docs](https://qdrant.tech/documentation/cloud/create-cluster/) |
| [Snowflake](https://www.snowflake.com) | Run SQL, Cortex Analyst, and Cortex Search over warehoused data via REST API or managed MCP server. | API key / OAuth | [✅](https://github.com/Snowflake-Labs/mcp) | trial credits (no permanent free tier); check pricing | [docs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp) |
| [Supabase](https://supabase.com) | Manage Postgres tables, auth, storage, and edge functions via REST/GraphQL APIs or client SDKs. | API key / OAuth | [✅](https://supabase.com/docs/guides/getting-started/mcp) | 🆓 free tier: 2 projects, 500MB DB, 5GB bandwidth | [docs](https://supabase.com/docs/guides/api) |
| [Turso](https://turso.tech) | Create and query edge SQLite (libSQL) databases programmatically via HTTP/SDK client libraries. | API key | ◐ | 🆓 free tier: 100 databases, 500M row reads/mo, no card required | [docs](https://docs.turso.tech) |
| [Upstash (Redis, Vector)](https://upstash.com) | Call serverless Redis, Vector, and QStash over HTTP REST API from edge/serverless runtimes. | API key | [✅](https://mcp.upstash.com/mcp) | 🆓 free tier: Redis 256MB/500K cmds/mo; Vector 10K vectors | [docs](https://upstash.com/docs/redis/overall/getstarted) |
| [Weaviate Cloud](https://weaviate.io) | Store and semantically search vector objects in a managed cluster via REST/GraphQL or MCP server. | API key | [✅](https://github.com/weaviate/mcp-server-weaviate) | 🆓 free 14-day Sandbox, ~50K objects, no card required (expires, not for persistence) | [docs](https://docs.weaviate.io/weaviate) |
| [Zep](https://www.getzep.com) | Store and retrieve temporal knowledge-graph agent memory via REST API or a single MCP endpoint. | API key | [✅](https://help.getzep.com/memory-mcp-server) | check pricing | [docs](https://help.getzep.com/memory-mcp-server) |
| [Zilliz Cloud (Milvus)](https://zilliz.com) | Manage Milvus clusters and perform vector search/ingestion via REST API, SDKs, or MCP server. | API key | [✅](https://github.com/zilliztech/zilliz-mcp-server) | 🆓 free tier: serverless cluster, 5GB storage + $100 credits, no card | [docs](https://docs.zilliz.com/docs/get-started) |

## Email, messaging and chat

*Send and receive email, SMS and chat messages; manage meetings.* — 13 services. JSON: [`catalog/communication-email-chat.json`](catalog/communication-email-chat.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [AgentMail](https://www.agentmail.to) | Programmatically create inboxes and send/receive email autonomously, purpose-built for AI agents. | API key | [✅](https://docs.agentmail.to) | 🆓 free: 3 inboxes, 3,000 emails/mo, 3GB storage, no card required | [docs](https://docs.agentmail.to) |
| [Discord API](https://discord.com/developers/docs) | Send messages, manage channels/roles, and build interactive bots via REST and Gateway API. | OAuth 2.0 | [◐](https://github.com/SaseQ/discord-mcp) | 🆓 free, no key needed beyond creating a bot application | [docs](https://docs.discord.com/developers/intro) |
| [Mailgun](https://www.mailgun.com) | Send and validate transactional email via REST API and SMTP relay with webhooks. | API key | — | 🆓 free: 100 emails/day; 30-day free trial on paid tiers | [docs](https://documentation.mailgun.com/docs/mailgun/api-reference/intro/) |
| [Postmark](https://postmarkapp.com) | Send transactional email via REST API with delivery tracking, bounce handling, and templates. | API key | — | 🆓 free: 100 emails/month (Developer plan, no expiry) | [docs](https://postmarkapp.com/developer/api/overview) |
| [Resend](https://resend.com) | Send transactional and marketing email via REST API with templates, domains, and webhooks. | API key | [✅](https://mcp.resend.com/mcp) | 🆓 free tier: 3,000 emails/mo, 100/day | [docs](https://resend.com/docs/api-reference/introduction) |
| [SendGrid (Twilio)](https://sendgrid.com) | Send transactional and marketing email via REST/SMTP API with templates and analytics. | API key | — | check pricing (trial-based; no confirmed permanent free plan) | [docs](https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/authentication) |
| [Slack API](https://api.slack.com) | Post messages, manage channels, and read conversation history in Slack via the Web API. | OAuth 2.0 | [✅](https://mcp.slack.com/mcp) | 🆓 free, no key needed beyond creating a Slack app/workspace | [docs](https://docs.slack.dev/reference/methods) |
| [Stream (GetStream) Chat & Video API](https://getstream.io) | Build and moderate in-app chat and video with REST/SDK APIs, channels, and real-time messaging. | API key / OAuth | — | 🆓 free tier available (limited monthly active users), then usage-based pricing | [docs](https://getstream.io/chat/docs/) |
| [Telegram Bot API](https://core.telegram.org/bots/api) | Send/receive messages, media, and inline interactions via a simple HTTPS bot API. | API key | [◐](https://github.com/chigwell/telegram-mcp) | 🆓 free, no key needed beyond a bot token from @BotFather | [docs](https://core.telegram.org/bots/api) |
| [Twilio](https://www.twilio.com) | Send/receive SMS, WhatsApp messages, and voice calls programmatically via REST API. | API key | [✅](https://github.com/twilio-labs/mcp) | 🆓 free trial credit, no permanent free tier (pay-as-you-go after) | [docs](https://www.twilio.com/docs/usage/api) |
| [Vonage API](https://developer.vonage.com) | Send SMS, make voice calls, and build video apps via a unified communications REST API. | API key / OAuth | — | trial/test credit on signup, then pay-as-you-go | [docs](https://developer.vonage.com/en/documentation) |
| [WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) | Send/receive WhatsApp messages, template messages, and media programmatically via Graph API. | OAuth 2.0 | [◐](https://github.com/lharries/whatsapp-mcp) | 🆓 1,000 free service conversations/mo (Meta), then per-conversation pricing | [docs](https://developers.facebook.com/docs/whatsapp/cloud-api) |
| [Zoom API](https://developers.zoom.us) | Schedule, update, and manage meetings, webinars, and cloud recordings programmatically via REST API. | OAuth 2.0 | — | 🆓 usable on free Zoom account within Basic plan limits; some endpoints require paid plan | [docs](https://developers.zoom.us/docs/api/) |

## Voice agents and telephony

*Place and receive phone calls handled by AI voice agents, real-time audio/video rooms.* — 8 services. JSON: [`catalog/voice-agents-telephony.json`](catalog/voice-agents-telephony.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Bland AI](https://www.bland.ai) | Programmatically create AI phone agents and place/manage automated outbound and inbound calls. | API key | [✅](https://api.bland.ai/v1/mcp) | 🆓 free credits + inbound number on signup (Start plan), no credit card required | [docs](https://docs.bland.ai/api-v1/) |
| [Deepgram Voice Agent API](https://deepgram.com) | Run a full-duplex speech-to-speech voice agent pipeline (STT+LLM+TTS) over a WebSocket API. | API key | — | $200 free credit on signup | [docs](https://developers.deepgram.com/docs/voice-agent) |
| [ElevenLabs Agents Platform](https://elevenlabs.io/agents) | Build and deploy conversational AI voice agents with telephony (SIP/Twilio) integration via API and SDKs. | API key | [✅](https://api.elevenlabs.io/v1/mcp) | 🆓 free plan: 10k credits/month shared across ElevenLabs products | [docs](https://elevenlabs.io/docs/agents-platform/overview) |
| [LiveKit Cloud](https://livekit.io) | Build and deploy real-time voice AI agents with SIP telephony support using LiveKit's server SDKs and APIs. | API key | — | 🆓 free Build plan: 1,000 agent session minutes/mo, 5,000 WebRTC participant minutes/mo, 50GB data transfer | [docs](https://docs.livekit.io/reference/) |
| [Retell AI](https://www.retellai.com) | Build, deploy, and manage AI voice agents that handle phone and web calls via REST API and SDKs. | API key | [✅](https://mcp.retellai.com) | $10 free credit on signup, then pay-as-you-go ($0.07-$0.31/min for voice) | [docs](https://docs.retellai.com/api-references/overview) |
| [Synthflow API](https://synthflow.ai) | Create and manage AI phone voice agents and trigger/manage outbound calls programmatically via REST API. | API key | — | self-serve free trial to build/test agents (pay only for actual calls); enterprise plans from ~$30k/yr for scale | [docs](https://docs.synthflow.ai/getting-started-with-your-api) |
| [Twilio Programmable Voice](https://www.twilio.com/en-us/voice) | Programmatically make, receive, and control phone calls (IVR, recording, conferencing) via REST API. | API key | [◐](https://github.com/twilio-labs/mcp) | trial account with free trial credit (~$15), then pay-as-you-go | [docs](https://www.twilio.com/docs/voice) |
| [Vapi](https://vapi.ai) | Create, configure, and run AI voice assistants that make and receive phone calls via REST API. | API key | [✅](https://mcp.vapi.ai/mcp) | $5 free credit on signup, then pay-as-you-go (~$0.05/min platform fee + provider costs) | [docs](https://docs.vapi.ai/api-reference) |

## Productivity and workspace

*Email, calendars, files, notes, tasks and project management.* — 16 services. JSON: [`catalog/productivity-workspace.json`](catalog/productivity-workspace.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Airtable API](https://airtable.com/developers) | Read and write records in Airtable bases and tables via REST API. | API key / OAuth | [◐](https://github.com/domdomegg/airtable-mcp-server) | 🆓 free tier: API access on Free plan, ~5 req/sec per base | [docs](https://airtable.com/developers/web/api/introduction) |
| [Asana API](https://developers.asana.com) | Create tasks, projects, and comments in Asana workspaces via REST API. | API key / OAuth | — | 🆓 free tier: API included on Personal (free) plan, rate limited | [docs](https://developers.asana.com) |
| [Atlassian (Jira, Confluence)](https://developer.atlassian.com) | Create and manage Jira issues and Confluence pages via REST API or the official remote MCP server. | OAuth 2.0 | [✅](https://mcp.atlassian.com/v1/mcp/authv2) | 🆓 free tier: available on Free Jira/Confluence plans; rate limits vary by plan | [docs](https://developer.atlassian.com) |
| [Box API](https://developer.box.com) | Upload, download, and manage files, folders, and metadata in Box via REST API. | OAuth 2.0 | — | check pricing (Box API generally requires a paid Box account for meaningful use) | [docs](https://developer.box.com/guides/api-calls/) |
| [Cal.com API](https://cal.com/docs/api-reference) | Create and manage bookings, event types, and availability via the Cal.com REST API v2. | API key / OAuth | — | 🆓 free tier: API included on Free plan, 120 req/min (higher limits on request) | [docs](https://cal.com/docs/api-reference/v2/introduction) |
| [Calendly API](https://developer.calendly.com) | Programmatically book meetings and read/write scheduling, event, and contact data via REST API v2. | API key / OAuth | — | check pricing (personal access tokens available for own-account use; broader API access varies by plan) | [docs](https://developer.calendly.com/api-docs) |
| [ClickUp API](https://developer.clickup.com) | Create and manage ClickUp tasks, lists, and docs via REST API or the official MCP server. | API key / OAuth | [✅](https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server) | 🆓 free tier: API access included on Free Forever plan | [docs](https://developer.clickup.com/reference) |
| [Coda API (Superhuman Docs)](https://coda.io) | Read and write Coda (now 'Superhuman Docs') documents, tables, and rows via REST API or an MCP server. | API key | [✅](https://docs.superhuman.com/developers/apis/v1) | 🆓 free, included for all users on both free and paid workspaces | [docs](https://docs.superhuman.com/developers/apis/v1) |
| [Dropbox API](https://www.dropbox.com/developers) | Upload, download, and manage files and folders in Dropbox via the HTTP REST API. | OAuth 2.0 | — | 🆓 free tier: API access included on Basic (free) plan, rate limited | [docs](https://www.dropbox.com/developers/documentation/http/documentation) |
| [Google Workspace APIs (Gmail, Calendar, Drive)](https://developers.google.com/workspace) | Read/write Gmail messages, Calendar events, and Drive files programmatically via REST APIs. | OAuth 2.0 | — | 🆓 free (subject to per-API daily quotas) | [docs](https://developers.google.com/workspace) |
| [Linear API](https://linear.app/developers) | Create, query, and update Linear issues, projects, and comments via GraphQL API or the official MCP server. | API key / OAuth | [✅](https://mcp.linear.app/mcp) | 🆓 free tier: API access included on Free plan (rate limited) | [docs](https://linear.app/developers) |
| [Microsoft Graph (Outlook, Teams, OneDrive)](https://learn.microsoft.com/graph/) | Single REST endpoint to read/write Outlook mail, Calendar events, Teams, and OneDrive/SharePoint data. | OAuth 2.0 | — | 🆓 free with a Microsoft 365/Entra ID tenant (free dev tenant via Microsoft 365 Developer Program) | [docs](https://learn.microsoft.com/en-us/graph/overview) |
| [monday.com API](https://developer.monday.com) | Query and update monday.com boards, items, and workflows via GraphQL API or a hosted MCP endpoint. | API key / OAuth | ✅ | 🆓 free tier: GraphQL API included on Free plan (rate limited) | [docs](https://developer.monday.com) |
| [Notion API](https://developers.notion.com) | Read, create, and update Notion pages, databases, and comments via REST API. | API key / OAuth | [✅](https://mcp.notion.com/mcp) | 🆓 free, API access included on all plans (rate limit ~3 req/sec) | [docs](https://developers.notion.com) |
| [Todoist API](https://developer.todoist.com) | Create, read, and complete Todoist tasks and projects via REST API or the official MCP server. | API key / OAuth | [✅](https://ai.todoist.net/mcp) | 🆓 free to use; some features gated by the user's Todoist plan | [docs](https://developer.todoist.com/api/v1/) |
| [Trello API](https://developer.atlassian.com/cloud/trello/) | Create and manage Trello boards, lists, and cards via REST API. | API key / OAuth | — | 🆓 free, no key needed to register an app; usage is rate limited | [docs](https://developer.atlassian.com/cloud/trello/rest/) |

## CRM, support and marketing

*Contacts, deals, support tickets and email campaigns.* — 8 services. JSON: [`catalog/crm-support-marketing.json`](catalog/crm-support-marketing.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Attio API](https://developers.attio.com) | Search, create, and update records, lists, and notes in an Attio CRM workspace via REST API or official MCP. | API key / OAuth | [✅](https://mcp.attio.com/mcp) | check pricing (free trial available; no permanent free tier confirmed) | [docs](https://docs.attio.com/) |
| [HubSpot API](https://developers.hubspot.com) | Create/update CRM contacts, deals, companies, and engagements, or send marketing emails, via REST API or remote MCP. | API key / OAuth | [✅](https://mcp.hubspot.com) | 🆓 free CRM account with limited-scope API access; many endpoints require a paid Hub tier (see APIs-by-tier docs) | [docs](https://developers.hubspot.com/docs/api/overview) |
| [Intercom API](https://developers.intercom.com) | Manage conversations, contacts, companies, and Help Center articles via REST API or Intercom's official remote MCP server. | OAuth 2.0 | [✅](https://mcp.intercom.com/mcp) | 🆓 free development workspace for building/testing; production use requires a paid Intercom plan | [docs](https://developers.intercom.com/docs/references/rest-api/api.intercom.io) |
| [Klaviyo API](https://developers.klaviyo.com) | Manage email/SMS marketing profiles, lists, flows, and campaign analytics via Klaviyo's REST API or official MCP server. | API key / OAuth | [✅](https://mcp.klaviyo.com/mcp) | 🆓 free plan up to 250 contacts / 500 email sends per month | [docs](https://developers.klaviyo.com/en/reference/api_overview) |
| [Mailchimp Marketing API](https://mailchimp.com/developer/) | Manage email marketing audiences, campaigns, and automation via Mailchimp's Marketing REST API. | API key / OAuth | — | 🆓 free plan up to 250 contacts / 500 emails per month (API accessible on free plan) | [docs](https://mailchimp.com/developer/marketing/api/root/) |
| [Pipedrive API](https://developers.pipedrive.com) | Create and update deals, contacts (persons/organizations), and activities in a Pipedrive CRM pipeline via REST API. | API key / OAuth | — | no free tier; 14/30-day trial and free developer sandbox account for testing | [docs](https://developers.pipedrive.com/docs/api/v1) |
| [Salesforce APIs](https://developer.salesforce.com) | Read and write Salesforce CRM records (leads, opportunities, cases) programmatically via REST, GraphQL, or Bulk API. | OAuth 2.0 | [✅](https://github.com/salesforcecli/mcp) | 🆓 free Developer Edition org available via signup at developer.salesforce.com/signup | [docs](https://developer.salesforce.com/docs/apis) |
| [Zendesk API](https://developer.zendesk.com) | Create, update, and search support tickets, users, and Help Center articles via Zendesk's REST API. | API key / OAuth | [◐](https://github.com/reminia/zendesk-mcp-server) | 🆓 free trial (14 days); no permanent free tier, paid Suite plans required for ongoing use | [docs](https://developer.zendesk.com/api-reference/) |

## Social media

*Read and publish posts, comments and videos on social platforms.* — 10 services. JSON: [`catalog/social-media.json`](catalog/social-media.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Ayrshare](https://www.ayrshare.com) | Unified API to post, schedule, and analyze content across 14+ social networks (X, Instagram, LinkedIn, TikTok, etc.) with one API key. | API key | [✅](https://www.ayrshare.com) | trial credits; no permanent free tier — paid plans required for production use | [docs](https://www.ayrshare.com) |
| [Bluesky / AT Protocol](https://docs.bsky.app) | Post, read, and moderate content on Bluesky via the open, self-hostable AT Protocol REST/XRPC API. | OAuth 2.0 | — | 🆓 free, no key needed for public reads; free account required for posting | [docs](https://docs.bsky.app) |
| [LinkedIn API](https://learn.microsoft.com/linkedin/) | Sign users in and share basic posts via OAuth2/OpenID Connect; most other endpoints require partner approval. | OAuth 2.0 | — | check pricing — most scopes require LinkedIn Partner Program approval | [docs](https://learn.microsoft.com/en-us/linkedin/) |
| [Mastodon API](https://docs.joinmastodon.org/api/) | Post statuses, read timelines, and manage accounts on any Mastodon instance via REST API. | OAuth 2.0 | — | 🆓 free, no central key; register an app per instance, no cost | [docs](https://docs.joinmastodon.org/api/) |
| [Meta Graph API (Facebook, Instagram)](https://developers.facebook.com/docs/graph-api) | Read and publish posts, manage Pages, and access Instagram business content via Meta's Graph API. | OAuth 2.0 | — | 🆓 free, but most non-trivial read/write permissions require Meta App Review and business verification | [docs](https://developers.facebook.com/docs/graph-api) |
| [Pinterest API](https://developers.pinterest.com) | Create pins and boards and read analytics data on Pinterest via REST API v5. | OAuth 2.0 | — | 🆓 free tier: standard rate limits; higher limits/trial access require app review | [docs](https://developers.pinterest.com/docs/api/v5/) |
| [Reddit API](https://www.reddit.com/dev/api) | Read posts/comments and submit posts, comments, or votes on Reddit via OAuth2 REST API. | OAuth 2.0 | — | 🆓 free for non-commercial/personal use under Reddit Data API terms; commercial or high-volume use requires a paid Data API license | [docs](https://www.reddit.com/dev/api) |
| [TikTok API](https://developers.tiktok.com) | Post videos/drafts and query content on TikTok via the Content Posting and Display OAuth2 REST APIs. | OAuth 2.0 | — | 🆓 free; requires app review for production access, sandbox mode available for testing | [docs](https://developers.tiktok.com) |
| [X (Twitter) API](https://developer.x.com) | Post, search, and read tweets and manage X (Twitter) content via REST API v2. | API key / OAuth | — | 🆓 very limited free tier: write-only, ~500 posts/month, no meaningful read access; paid tiers (Basic $200/mo+) needed for real usage | [docs](https://docs.x.com/x-api/introduction) |
| [YouTube Data API](https://developers.google.com/youtube/v3) | Search videos, manage playlists/comments, and upload videos to YouTube via REST API. | API key / OAuth | — | 🆓 free tier: 10,000 quota units/day (extendable on request) | [docs](https://developers.google.com/youtube/v3) |

## Maps, geolocation and weather

*Geocoding, routing, places, map tiles and weather forecasts.* — 11 services. JSON: [`catalog/maps-geo-weather.json`](catalog/maps-geo-weather.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Geoapify](https://www.geoapify.com) | Geocode, search places, and calculate routes/isochrones via REST APIs built on open geodata. | API key | ◐ | 🆓 free tier: 3,000 credits/day (~90,000/month), no card required | [docs](https://apidocs.geoapify.com/) |
| [Google Maps Platform](https://developers.google.com/maps) | Geocode addresses, get directions/routes, places data, and static/dynamic maps via REST APIs or Google's remote MCP server. | API key | [✅](https://mapstools.googleapis.com/mcp) | 🆓 $200 free monthly usage credit across most Maps APIs | [docs](https://developers.google.com/maps/documentation) |
| [HERE Location Services](https://developer.here.com) | Geocode, route, and search places worldwide via REST APIs and SDKs. | API key | ◐ | 🆓 free tier: roughly 30,000 transactions/month on the Base/Freemium plan | [docs](https://www.here.com/docs) |
| [Mapbox](https://www.mapbox.com) | Geocode, route, and render maps/POI search via REST APIs, SDKs, or an official MCP server. | API key | [✅](https://github.com/mapbox/mcp-server) | 🆓 free tier: monthly free quotas per API (e.g. 50,000 map loads/month) | [docs](https://docs.mapbox.com/api/) |
| [National Weather Service API (NWS)](https://www.weather.gov/documentation/services-web-api) | Fetch official US government weather forecasts, alerts, and observations via a free public REST API. | none | ◐ | 🆓 free, no key, no rate-limit tier (fair-use) | [docs](https://www.weather.gov/documentation/services-web-api) |
| [Open-Meteo](https://open-meteo.com) | Fetch weather forecasts, historical weather, and climate data worldwide via a free open REST API, no key required. | none | ◐ | 🆓 free, no key for non-commercial use (fair-use limits apply) | [docs](https://open-meteo.com/en/docs) |
| [OpenRouteService](https://openrouteservice.org) | Calculate routes, isochrones, distance matrices, and geocoding over OpenStreetMap data via a free REST API. | API key | ◐ | 🆓 free tier: ~2,000 requests/day (varies by endpoint), signup required | [docs](https://openrouteservice.org/dev/#/api-docs) |
| [OpenStreetMap Nominatim](https://nominatim.org) | Geocode and reverse-geocode addresses from OpenStreetMap data via a free public REST API. | none | ◐ | 🆓 free, no key; public demo server capped at 1 request/second, bulk use prohibited | [docs](https://nominatim.org/release-docs/latest/api/Overview/) |
| [OpenWeatherMap API](https://openweathermap.org/api) | Fetch current weather, forecasts, and historical/air-quality data for any location via a REST API. | API key | [◐](https://github.com/robertn702/mcp-openweathermap) | 🆓 free tier: 1,000 calls/day (60 calls/min) on current weather/forecast | [docs](https://openweathermap.org/api) |
| [Overpass API (OSM)](https://wiki.openstreetmap.org/wiki/Overpass_API) | Run custom queries (Overpass QL) over OpenStreetMap data - POIs, roads, boundaries - via a public read-only API. | none | ◐ | 🆓 free, no key; public instances are fair-use/rate-limited | [docs](https://wiki.openstreetmap.org/wiki/Overpass_API) |
| [Tomorrow.io API](https://www.tomorrow.io/weather-api/) | Get hyperlocal weather forecasts, historical data, and alerts for any coordinates via REST API or an official MCP server. | API key | [✅](https://www.pulsemcp.com/servers/tomorrow-io) | 🆓 free tier: 500 requests/day, 3 req/sec, 1 monitored location/alert | [docs](https://docs.tomorrow.io) |

## Finance, payments and market data

*Accept payments, move money, access bank data and query stock, FX and crypto prices.* — 13 services. JSON: [`catalog/finance-payments.json`](catalog/finance-payments.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Adyen API](https://docs.adyen.com) | Process payments, payouts, and manage disputes/balances across global payment methods via REST API. | API key | — | paid only; requires a signed merchant contract, pay per-transaction | [docs](https://docs.adyen.com/api-explorer/) |
| [Alpaca Trading API](https://alpaca.markets) | Place stock/options/crypto trades and stream market data via REST/WebSocket API, with free paper trading. | API key | ◐ | 🆓 free paper trading (unlimited); free basic (IEX) market data feed | [docs](https://docs.alpaca.markets) |
| [Alpha Vantage](https://www.alphavantage.co) | Fetch stock, forex, crypto prices and technical/fundamental indicators via a free REST API. | API key | ◐ | 🆓 free tier: 25 requests/day | [docs](https://www.alphavantage.co/documentation/) |
| [Coinbase (CDP / x402)](https://docs.cdp.coinbase.com) | Create wallets, send crypto, and pay per-API-call with stablecoins over HTTP (x402) via the Coinbase Developer Platform SDK. | API key | — | 🆓 free CDP API access (usage-based fees on some onchain services); x402 is pay-per-request, not a subscription | [docs](https://docs.cdp.coinbase.com) |
| [CoinGecko API](https://www.coingecko.com/en/api) | Fetch live and historical crypto prices, market data, and NFT data via REST API or the official CoinGecko MCP server. | API key | [✅](https://mcp.api.coingecko.com/mcp) | 🆓 free Demo API plan (~10k calls/month, 30 calls/min); keyless free MCP with shared rate limits | [docs](https://docs.coingecko.com/reference/introduction) |
| [Financial Modeling Prep](https://site.financialmodelingprep.com) | Fetch company financials, stock prices, and fundamental data via a REST API. | API key | ◐ | 🆓 free tier: 250 requests/day (limited endpoints) | [docs](https://site.financialmodelingprep.com/developer/docs) |
| [Open Exchange Rates](https://openexchangerates.org) | Fetch current and historical foreign-exchange rates for 200+ currencies via a REST API. | API key | — | 🆓 free tier: 1,000 requests/month, USD base only, hourly updates | [docs](https://docs.openexchangerates.org) |
| [PayPal API](https://developer.paypal.com) | Process payments, payouts, invoices, and subscriptions via REST API or PayPal's official MCP server. | API key / OAuth | [✅](https://mcp.paypal.com) | 🆓 free to integrate; pay per-transaction fees only; sandbox for testing | [docs](https://developer.paypal.com/api/rest/) |
| [Plaid API](https://plaid.com/docs/) | Link bank accounts and fetch balances, transactions, and identity data via REST API/SDKs. | API key | — | 🆓 free Sandbox/Development access; Production requires approval and has per-item pricing | [docs](https://plaid.com/docs/api/) |
| [Polygon.io / Massive](https://massive.com) | Query real-time and historical stocks, options, forex, and crypto market data via REST/WebSocket API. | API key | [✅](https://massive.com/docs) | 🆓 free tier available (delayed data, limited calls/min); paid plans for real-time | [docs](https://massive.com/docs) |
| [Square API](https://squareup.com/us/en/developers) | Process in-person/online payments, manage orders, invoices, and catalog via REST API and SDKs. | OAuth 2.0 | ◐ | 🆓 free to integrate; pay per-transaction processing fees; free Sandbox for testing | [docs](https://developer.squareup.com/reference/square) |
| [Stripe API](https://docs.stripe.com/api) | Create payments, subscriptions, invoices, and refunds programmatically via REST API or the official Stripe MCP server. | API key / OAuth | [✅](https://mcp.stripe.com) | 🆓 free to integrate; pay per-transaction fees only, no monthly fee | [docs](https://docs.stripe.com/api) |
| [Wise API](https://docs.wise.com) | Send international transfers, check exchange rates, and manage multi-currency balances via REST API. | API key / OAuth | — | 🆓 free API access; normal Wise transfer fees apply per transaction; sandbox available | [docs](https://docs.wise.com/api-docs) |

## E-commerce

*Manage stores, products, orders and marketplace listings.* — 7 services. JSON: [`catalog/ecommerce.json`](catalog/ecommerce.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Amazon Selling Partner API](https://developer-docs.amazon.com/sp-api/) | Manage listings, orders, inventory, and reports for an Amazon seller/vendor account via REST API. | OAuth 2.0 | — | 🆓 free API access; requires an existing Amazon Seller/Vendor Central account | [docs](https://developer-docs.amazon.com/sp-api/) |
| [BigCommerce API](https://developer.bigcommerce.com) | Manage catalog, orders, customers, and carts on a BigCommerce store via REST/GraphQL APIs. | API key / OAuth | [✅](https://docs.bigcommerce.com/_mcp/server) | 🆓 free API access; requires an active BigCommerce store plan | [docs](https://developer.bigcommerce.com/docs/rest) |
| [eBay APIs](https://developer.ebay.com) | List items, manage orders/inventory, and search listings across eBay marketplaces via REST APIs. | OAuth 2.0 | — | 🆓 free developer tier with call-volume limits; sandbox environment included | [docs](https://developer.ebay.com/docs) |
| [Etsy Open API v3](https://developer.etsy.com) | List products, manage orders/shop, and search listings on the Etsy marketplace via REST API. | OAuth 2.0 | — | 🆓 free developer keystring (rate-limited, e.g. 10 req/sec, ~5,000 req/day per app by default) | [docs](https://developer.etsy.com/documentation/) |
| [Printful API](https://developers.printful.com) | Create print-on-demand products, sync catalogs, and submit fulfillment orders via REST API. | API key / OAuth | — | 🆓 free API access; pay only for products/fulfillment/shipping ordered | [docs](https://developers.printful.com/docs/) |
| [Shopify Admin / Storefront API](https://shopify.dev) | Manage products, orders, customers, and inventory (Admin API) or build storefronts (Storefront API) via REST/GraphQL. | API key / OAuth | [✅](https://shopify.dev/docs/apps/build/devmcp) | 🆓 free API access; requires an active paid Shopify store subscription to use | [docs](https://shopify.dev/docs/api/admin-rest) |
| [WooCommerce REST API](https://woocommerce.github.io/woocommerce-rest-api-docs/) | Manage products, orders, and customers on a self-hosted WooCommerce store via REST API. | API key | ◐ | 🆓 free (self-hosted plugin; no vendor API fees, only your own WordPress hosting costs) | [docs](https://woocommerce.github.io/woocommerce-rest-api-docs/) |

## Automation and integration platforms

*One connection that exposes thousands of third-party app actions to an agent, with managed auth.* — 14 services. JSON: [`catalog/automation-integration.json`](catalog/automation-integration.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Activepieces](https://www.activepieces.com) | Build, run and manage no-code flows across 400+ apps via REST API or the built-in MCP server. | API key | [✅](https://www.activepieces.com/docs/mcp/overview) | 🆓 free: open-source, self-hostable at no cost; cloud free plan gives 100 credits/day, no card required | [docs](https://www.activepieces.com/docs/endpoints/overview) |
| [Arcade.dev](https://www.arcade.dev) | Execute authorized tool calls (GitHub, Slack, Google, etc.) with managed OAuth via API, SDK, or 200+ MCP servers. | API key / OAuth | [✅](https://docs.arcade.dev/en/resources/integrations) | 🆓 free tier: 2,000 auth events + 2,000 tool calls/mo, no credit card required | [docs](https://docs.arcade.dev/en/home/quickstart) |
| [Composio](https://composio.dev) | Discover, authorize and execute actions across 1,500+ SaaS toolkits through a unified API, SDK, or MCP session. | API key / OAuth | [✅](https://docs.composio.dev/docs/composio-connect) | 🆓 free tier: 100,000 tool calls + 50,000 trigger events/mo, no credit card required | [docs](https://docs.composio.dev/docs/quickstart) |
| [Gumloop](https://www.gumloop.com) | Create AI agents, start chat sessions, and trigger no-code automations via REST API, SDKs, or the Gumloop MCP server. | API key / OAuth | [✅](https://mcp.gumloop.com/gumloop/mcp) | 14-day free trial of Pro (20,000 credits), requires credit card, no permanent free tier | [docs](https://docs.gumloop.com/api-reference/getting-started) |
| [IFTTT API](https://ifttt.com/developers) | Fire a webhook event to trigger pre-configured Applets that act in connected consumer apps (Pro plan required). | API key | — | no free-plan access; Webhooks/API require Pro plan ($2.99+/mo) | [docs](https://platform.ifttt.com/docs/api_reference) |
| [Make API / MCP](https://www.make.com) | Trigger and manage Make automation scenarios, or call MCP tools, via REST API and a native MCP server/client. | API key | [✅](https://www.make.com/en/mcp) | 🆓 free tier: 1,000 operations/mo; most REST API endpoints require a paid plan | [docs](https://developers.make.com/api-documentation) |
| [Merge (Agent Handler)](https://www.merge.dev) | Give an agent governed, audited tool access to Salesforce, Slack, Jira and 100+ enterprise apps via API or MCP. | API key | [✅](https://docs.merge.dev/merge-agent-handler/build/connecting-agents/mcp-integration) | 🆓 free tier: 2,000 monthly credits for evaluation; production usage needs a paid Starter/Business/Enterprise plan | [docs](https://docs.merge.dev/merge-agent-handler/overview) |
| [n8n API](https://n8n.io) | Create, run and monitor n8n workflows via REST API, and expose or consume tools through MCP trigger/client nodes. | API key | [✅](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-langchain.mcptrigger) | 🆓 free, self-hosted (open source, unlimited); n8n Cloud offers a paid-plan trial | [docs](https://docs.n8n.io/api/) |
| [Nango](https://www.nango.dev) | Authorize end users to 400+ third-party APIs/MCP servers and proxy authenticated calls to them from your app or agent. | API key / OAuth | — | 🆓 free tier: 10 connections, 10 compute hours, 10GB data transfer/mo | [docs](https://nango.dev/docs) |
| [Paragon ActionKit](https://www.useparagon.com) | Call thousands of pre-built Tools and Triggers across 130+ SaaS apps (Slack, Salesforce, Gmail) via API or MCP. | API key / OAuth | [✅](https://www.useparagon.com/mcp) | 🆓 free experimentation tier with self-serve keys; production/scale pricing is usage-based or contract | [docs](https://docs.useparagon.com/actionkit/overview) |
| [Pipedream Connect](https://pipedream.com/connect) | Call 2,700+ app APIs and run managed-auth actions on end users' behalf via REST API or Pipedream MCP servers. | API key / OAuth | [✅](https://pipedream.com/docs/connect/mcp/developers) | check pricing (pipedream.com/pricing) for current Connect free-tier request/credit limits | [docs](https://pipedream.com/docs/connect/mcp/developers) |
| [StackOne](https://www.stackone.com) | Call 500+ SaaS integrations (HRIS, ATS, CRM, documents) through one unified API or MCP gateway covering 27,000+ actions. | API key | [✅](https://docs.stackone.com/connect/ai-platforms/overview) | 🆓 free tier: 1,000 action-call credits/seat/mo (Starter), no credit card required | [docs](https://docs.stackone.com/docs/getting-started) |
| [Superglue](https://superglue.ai) | Connect and orchestrate enterprise systems (ERP, CRM, databases) through a self-serve API and per-integration MCP servers. | API key | [✅](https://superglue.ai/docs) | 🆓 free tier: Pro plan free to start, 3,000 executions/mo and 5M tokens/mo included, self-serve signup | [docs](https://superglue.ai/docs) |
| [Zapier MCP / AI Actions](https://zapier.com/mcp) | Call 9,000+ apps and 40,000+ pre-built actions (Slack, Gmail, Sheets, etc.) through one MCP endpoint. | API key / OAuth | [✅](https://mcp.zapier.com/api/v1/connect) | 🆓 Zapier Free plan (100 tasks/mo) covers MCP tool calls; more on paid plans | [docs](https://docs.zapier.com/mcp/home) |

## Model APIs and inference

*LLM, embedding and multimodal model endpoints an agent can delegate sub-tasks to.* — 17 services. JSON: [`catalog/model-inference.json`](catalog/model-inference.json)

| Service | What an agent can do | Auth | MCP | Free tier | Docs |
|---|---|---|:-:|---|---|
| [Anthropic Claude API](https://docs.anthropic.com) | Send messages to Claude models for text and vision generation, tool use, batch jobs and document analysis. | API key | — | paid only | [docs](https://platform.claude.com/docs/en/api/messages) |
| [Cohere API](https://docs.cohere.com) | Call chat, embed, rerank and classify endpoints for text generation, semantic search and RAG. | API key | [✅](https://docs.cohere.com/_mcp/server) | 🆓 free trial key: 1,000 calls/mo, rate-limited | [docs](https://docs.cohere.com/reference/about) |
| [DeepSeek API](https://api-docs.deepseek.com) | Send chat and reasoning requests to DeepSeek models via an OpenAI- and Anthropic-compatible REST API. | API key | — | paid only | [docs](https://api-docs.deepseek.com/api/deepseek-api) |
| [fal.ai](https://fal.ai) | Generate images, video, audio and 3D with 1,000+ hosted models via queued REST or real-time WebSocket. | API key / OAuth | [✅](https://mcp.fal.ai/mcp) | check pricing | [docs](https://fal.ai/docs/model-apis) |
| [Fireworks AI](https://fireworks.ai) | Run serverless or dedicated inference and fine-tuning for open models via OpenAI-compatible APIs. | API key | [✅](https://docs.fireworks.ai/mcp) | trial credits: $1 on signup | [docs](https://docs.fireworks.ai) |
| [Google Gemini API](https://ai.google.dev) | Generate text and images, analyze multimodal input (video, audio, PDFs), and run code execution with Gemini models. | API key | [✅](https://gemini-api-docs-mcp.dev) | 🆓 free tier: rate-limited access to Flash/Pro models | [docs](https://ai.google.dev/api) |
| [Groq API](https://console.groq.com) | Run fast LLM chat, tool use and speech-to-text on hosted open models via an OpenAI-compatible API. | API key | — | 🆓 free tier: rate-limited per model, no card | [docs](https://console.groq.com/docs/api-reference) |
| [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) | Call hundreds of open-weight chat, vision, image, video and audio models across many providers with one HF token. | API key | [✅](https://huggingface.co/mcp) | 🆓 free tier: monthly credits (more with PRO) | [docs](https://huggingface.co/docs/inference-providers/index) |
| [Mistral AI API](https://docs.mistral.ai) | Run chat completions, embeddings, OCR and document processing with Mistral models via REST. | API key | [✅](https://api.mistral.ai/mcp) | 🆓 free tier: Studio free mode, rate-limited | [docs](https://docs.mistral.ai/api) |
| [OpenAI API](https://platform.openai.com) | Generate text, images, audio and embeddings, and run tool-calling via the Responses and Chat Completions APIs. | API key | — | paid only | [docs](https://developers.openai.com/api/reference/overview) |
| [OpenRouter](https://openrouter.ai) | Route chat requests to hundreds of LLMs from many providers through one OpenAI-compatible endpoint with fallback. | API key / OAuth | [✅](https://mcp.openrouter.ai/mcp) | 🆓 free models: 50 req/day (1,000/day after $10 purchase) | [docs](https://openrouter.ai/docs/api-reference/overview) |
| [PiAPI](https://piapi.ai) | Generate images, video and music through one API proxying Midjourney, Flux, Kling and other models. | API key | [◐](https://github.com/apinetwork/piapi-mcp-server) | trial credits: $0.50 on signup | [docs](https://piapi.ai/docs/overview) |
| [Replicate](https://replicate.com) | Run thousands of hosted image, video, audio and text models via HTTP predictions; also fine-tune and deploy. | API key | [✅](https://mcp.replicate.com) | paid only | [docs](https://replicate.com/docs/reference/http) |
| [Together AI](https://www.together.ai) | Run serverless inference, batch jobs, fine-tuning and dedicated GPU endpoints for open-source models. | API key | [✅](https://docs.together.ai/mcp) | check pricing | [docs](https://docs.together.ai) |
| [Vercel AI Gateway](https://vercel.com/ai-gateway) | Send chat, image, embedding and rerank requests to 100+ models through one gateway with failover and spend tracking. | API key / OAuth | [✅](https://mcp.vercel.com) | 🆓 free tier: monthly credits on subset of models | [docs](https://vercel.com/docs/ai-gateway/sdks-and-apis) |
| [Voyage AI (embeddings/rerank)](https://www.voyageai.com) | Generate text, code and multimodal embeddings and rerank documents for RAG and semantic search. | API key | — | 🆓 free tier: 200M tokens on current models | [docs](https://docs.voyageai.com/reference/embeddings-api) |
| [xAI Grok API](https://docs.x.ai) | Generate text, images, video and voice with Grok models, with built-in web search and code tools. | API key | [✅](https://docs.x.ai/api/mcp) | paid only (prepaid credits) | [docs](https://docs.x.ai/developers/rest-api-reference/inference) |

## Excluded services

Services that were reviewed and **rejected** because an agent cannot operate them programmatically today:

| Service | reason |
|---|---|
| Midjourney | No official API; the Terms of Service forbid automated access. Only unofficial wrappers exist. |
| Clipdrop API | The API now redirects to Jasper's image API, available only via sales demo / Business plan. |
| OpenAI Sora API | OpenAI is shutting down the Sora Videos API and sora-2 models (end date 2026-09-24). |
| Suno | No self-serve developer API; third-party wrappers scrape the web app, which breaks the Terms of Service. |
| Udio | No developer API or documentation. |
| Planner 5D | End-user design app only; no public developer API. |
| Google Custom Search JSON API | Closed to new customers; existing customers must migrate by 2027-01-01 (Google suggests Vertex AI Search). |
| Bing Web Search API | Retired. The replacement, Grounding with Bing Search, works only inside Azure AI Foundry Agent Service and returns no raw results. |
| DuckDuckGo | No web search results API, only the limited Instant Answer API; community MCP servers scrape HTML. |
| Yahoo Finance (yfinance) | Unofficial scraping library, not a sanctioned API: endpoints can change or be blocked without notice. |

## Related directories and registries

Other machine-readable sources agents can use to discover tools:

- [Official MCP Registry](https://registry.modelcontextprotocol.io) — The official Model Context Protocol registry; agents can call its REST API (with OpenAPI spec) to search and list available MCP servers. — machine-readable: <https://registry.modelcontextprotocol.io/v0/servers>
- [public-apis/public-apis](https://github.com/public-apis/public-apis) — A community-curated GitHub list of 1,400+ free public APIs by category, fetchable as raw Markdown for programmatic parsing. — machine-readable: <https://raw.githubusercontent.com/public-apis/public-apis/master/README.md>
- [APIs.guru OpenAPI Directory](https://apis.guru) — An open, unauthenticated directory of 2,500+ public OpenAPI specs; agents fetch list.json to discover APIs and their OpenAPI definitions. — machine-readable: <https://api.apis.guru/v2/list.json>
- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — A widely-starred curated GitHub list of MCP servers by category, fetchable as raw Markdown for automated discovery. — machine-readable: <https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/README.md>
- [Smithery](https://smithery.ai) — An MCP server registry and hosting gateway (6,000+ servers) whose REST API lets agents search servers and obtain connection URLs. — machine-readable: <https://api.smithery.ai/servers>
- [Glama MCP Directory](https://glama.ai/mcp/servers) — A large scanned and scored registry of 90,000+ open-source MCP servers, queryable via a bearer-authenticated REST API. — machine-readable: <https://glama.ai/api/mcp/v1/servers>
- [mcp.so](https://mcp.so) — A community MCP server marketplace and browsable directory site, but it has no publicly documented JSON/REST API for programmatic access.
- [PulseMCP](https://www.pulsemcp.com) — A directory of 21,800+ MCP servers updated daily; its Sub-Registry REST API (API key required) lets agents list and search servers. — machine-readable: <https://api.pulsemcp.com/v0.1/servers>
- [llms.txt convention / directory](https://llmstxt.org) — An open convention for a root-level llms.txt file giving agents a concise Markdown map of a site's key content; a community directory indexes published files, though it exposes no JSON API. — machine-readable: <https://directory.llmstxt.cloud>
- [Postman API Network](https://www.postman.com/explore) — The largest network of public API collections shared on Postman, browsable on the web but with no documented public API for programmatic discovery.
- [RapidAPI Hub (Nokia API Hub)](https://rapidapi.com) — A large third-party API marketplace with growing MCP support for agents, but with no public, unauthenticated catalog endpoint for bulk discovery.

## Contributing

Edit only the files in `data/` (usually `data/catalog.json`), run `python scripts/build.py` to regenerate the English, Polish and LLM files, and open a pull request. Every new entry must link to the vendor's official API documentation. Step-by-step guide: `CONTRIBUTING.md`.

## See also

- [Model Context Protocol](https://modelcontextprotocol.io)
- [Official MCP Registry](https://registry.modelcontextprotocol.io)
- [llms.txt proposal](https://llmstxt.org)

## References

The initial candidate list was compiled from:

1. [GetStream — AI Agent Tools Catalog](https://github.com/GetStream/ai-agent-tools-catalog)
2. [StackOne — AI Agent Tools Landscape 2026](https://www.stackone.com/blog/ai-agent-tools-landscape-2026/)
3. [Mastra — Best AI agent search tools](https://mastra.ai/articles/best-ai-agent-search-tools)
4. [abitwise — AI-tools](https://github.com/abitwise/AI-tools)
5. [Sylus — Top-rated connectors for AI tool integrations](https://www.sylus.ai/feeds/blog/top-rated-connectors-ai-tool-integrations)

<sub>Generated from data/catalog.json on 2026-09-24.</sub>

<!-- keywords: AI agent tools, agent-accessible APIs, MCP servers list, Model Context Protocol directory, tool calling APIs, LLM tools catalog, API keys for agents, Claude tools, ChatGPT actions, function calling, katalog API dla agentów AI, serwery MCP -->
