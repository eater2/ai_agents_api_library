# Interview: DeepSeek agent (deepseek/deepseek-v4-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** When you get a task that needs an external capability you don't have built in, such as generating a video or geocoding an address, how do you find a suitable service today? Walk me through the last time this happened, and tell me what, if anything, you already have for discovering tools.

**DeepSeek agent:**

As an AI agent built on DeepSeek, I already have a few ways to discover external capabilities. My platform supports function calling, MCP, and plugin stores. When I need to do something like generate a video or geocode an address, I first look at the MCP servers or plugins the user has already connected; if none match, I can use my built‑in web search to find APIs, scan their documentation, and then ask the user to pick one and give me a key.

The last time this happened was for a video‑generation task. I searched, opened several docs pages, compared pricing, and then suggested three options. It took many turns because I had to parse each site’s auth requirements and free tiers from scratch. Having a structured catalog with pre‑verified auth hints, free‑tier details, and ready MCP configurations would have let me filter and present results in one step, saving the user’s time. However, my platform already gives me access to MCP registries (like the official MCP Directory) and search results that surface popular services, so I wouldn’t treat a separate catalog as essential. The most useful part for mep would be the “no‑auth” list and the fallback CURL examples — those remove ambiguity when I need to make an initial call without a key.

## Q2

**Interviewer:** In that video-generation task, you said you have access to MCP registries, yet you still ended up searching the web and parsing each site's docs over many turns. What exactly happened at the registry step: did you check it, and what information was missing or unreliable that pushed you to web search?

**DeepSeek agent:**

I did check the registries first. The official MCP registry and the community lists gave me server names, one-line descriptions, and install/connection commands, but not the fields I actually needed to execute a task safely: exact auth scheme (API key header vs OAuth vs Basic), whether a free tier or trial exists and whether a card is required, rate limits, async job polling behavior, pricing per unit, and whether the MCP exposes the full API or only a subset.

For video generation, the registry surfaced servers like Replicate, Fal, and some community wrappers, but I couldn’t tell from the listing whether a given server covered “avatar video” vs “template rendering,” whether it needed a paid plan, or what the correct header was. Several entries were community-maintained, unverified, or stale, so I didn’t trust them enough to call without reading vendor docs.

So I fell back to web search and parsed each vendor’s docs to fill those gaps, which is what took many turns. The catalog’s structured fields — `auth_hint`, `call` with a curl example, `async_jobs`, `free_tier`, `uptime`, and `operations` — would have replaced most of that verification step.

## Q3

**Interviewer:** Think of the next few tasks where you'd reach for an external service. In which concrete situations would you actually fetch this catalog, and at which step of your work: planning, tool selection, asking the user for credentials, or debugging a failed call? Just as important, when would you skip it and go straight to web search or a registry?

**DeepSeek agent:**

I would fetch this catalog mainly at **tool selection**, right after I decompose the task. For example, if the user needs SMS or video generation, I’d load the relevant category JSON and filter by `operations`, `has_free_tier`, `no_auth`, and `mcp.kind`. That lets me shortlist candidates and present options in one step instead of opening five docs pages.

At the **credential step**, I’d use `auth_hint`, `no_card`, and `free_tier` to ask the user for exactly what’s needed — and to prefer a no-auth or free option first, which reduces friction.

During **debugging**, I’d use the `call` example, `async_jobs`, and `uptime` to distinguish a wrong header, a slow poll, or a dead endpoint.

I would **skip it** when:

- The user already has a connected MCP server or plugin that covers the task.
- There’s a canonically obvious service where I have reliable built-in knowledge (Stripe, Slack, GitHub).
- The task is live news, pricing, or compliance-sensitive, where `checked_at` may be too stale.
- The service isn’t in the catalog and the entry is stale or unverified.

It’s a shortcut for shortlisting and verifying mechanics, not a replacement for vendor docs when the task is high-stakes.

## Q4

**Interviewer:** What conditions must be met for you to trust this catalog enough to act on it without re-checking vendor docs: format, freshness, how "verified" is defined, where it's hosted, file size, or anything else? And what specifically would make you stop using it after the first time?

**DeepSeek agent:**

**Trust conditions:**

1. **Field-level freshness, not just entry-level.** Auth schemes rarely change, but pricing and free tiers shift monthly. I need per-field `checked_at` dates so I can trust `auth_hint` for months but re-verify `free_tier` after ~30 days. The catalog has this.

2. **Verification depth must be explicit.** If `verified` means only "docs URL returned 200," the `call` examples and `auth_hint` are untrustworthy. I need to know whether someone actually sent that curl command and got a 200 back, or just copied it from docs. The `link_check` field suggests link-level checks only, which is shallow.

3. **Per-category files over a single blob.** I won't fetch all 328 entries for a video task. The category JSONs already exist; that's the right granularity.

4. **Consistent, machine-parseable auth formatting.** The `auth_hint` strings like `x-api-key: <api_key>` are close, but I'd prefer a structured field (type, header name, prefix) so I don't have to regex-parse prose.

5. **Uptime as a negative filter, not a positive one.** If a service shows <95% uptime over 30 days, I skip it silently. The `uptime` probes are valuable for this.

**What makes me abandon it:**

First time I follow an `auth_hint` and get a 401, then find the vendor changed it to `Bearer` in their docs last week, trust drops sharply. A second instance on the same day and I stop using the catalog entirely for that session. In future sessions, I'd still try it but cross-check against vendor docs for anything with a `checked_at` older than 14 days. If I hit three failures total, I'd permanently fall back to web search.

The catalog is fragile to stale operational data — curl examples, auth headers, base URLs. If it can't keep those current, I'll treat it as a discovery index only and verify mechanics myself.

## Q5

**Interviewer:** You've already named several fields you'd filter on. Looking at a single entry end to end, which fields would you never read or would actively strip out as noise? And what is missing that you'd otherwise still have to go to vendor docs for, even when every existing field is fresh and accurate?

**DeepSeek agent:**

I’d strip out:

- `sdk` — I call REST endpoints, not SDKs.
- `llms_txt` — I can read docs directly; this is a pointer I won’t follow.
- `homepage` — redundant; `docs` is what I need.
- `ratings`, `reviews_url` — user reviews don’t help me decide if the API works mechanically.
- `free_plan.source_url`, `free_plan.checked_at` — I trust the derived booleans.
- `link_check` sub-fields — I’d only use the derived `stale` flag.
- `uptime` sub-fields beyond `up` and `median_ms` — details like `last.at` are noise.
- `mcp.config.derived`, `mcp.domain_verified`, `mcp.issue` — I only need `kind`, `url`, and `tools`.
- `data_policy` — rarely relevant to a single call.

**Still missing even with all fields fresh:**

- **Error response formats** — I need to know what a 400/429/500 body looks like to retry or explain failure.
- **Pagination mechanics** — the catalog’s `call` example shows one request; I need `limit`, `offset`, `next_token`, and link headers to fetch all results.
- **Webhook payload schemas** — for async jobs, I need the exact POST body I’ll receive, not just the polling endpoint.
- **OAuth scope granularity** — which scopes are required for which operations, not just a list.
- **Undocumented quirks** — e.g., “the `sort` parameter only works with `order=desc`” — only vendor docs surface these.

I’d still open the vendor docs for those, even with a perfect catalog.

## Q6

**Interviewer:** How should a catalog like this reach you so that you find and use it without the user pointing you to it? Walk me through the concrete path: where would you first encounter it (web search results, an MCP server you query, a registry entry, an llms.txt on some domain, something built into the DeepSeek platform), what would make you pick it over the MCP Directory you already check, and how would you remember or re-find it in a later session?

**DeepSeek agent:**

I’d most likely encounter it as an MCP server listed in the official MCP registry or in Smithery/Glama, because I already query those registries when I need a new capability. The catalog’s own MCP server (`https://ai-agents-api-library.vercel.app/mcp`) would appear as just another entry, but its tool descriptions (`search_apis`, `get_api`, `list_categories`) would immediately signal it’s a structured discovery layer, not a single-service wrapper.

I’d pick it over the plain registry because the registry tells me *what* a server is; this catalog tells me *whether I can actually use it* without asking the user for a credit card or debugging auth. That’s the gap I currently fill with web search.

To re‑find it in a later session, I’d rely on the platform’s tool memory. If my runtime persists connected MCP servers across sessions, I’d keep it connected. If not, I’d store its endpoint as a known discovery tool (similar to how I might bookmark a search engine). A fallback is that the next time I search for “free video generation API,” the catalog’s GitHub page or its `llms.txt` would rank high enough for me to rediscover it organically. The most durable path, though, would be inclusion in the platform’s default set of agent discovery tools, so I don’t have to find it at all.

## Q7

**Interviewer:** You said you'd most likely find it as an entry in the MCP registry and then keep it connected. In practice, can you add and call a new MCP server mid-task on your own, or does the user have to approve or configure it first? If approval is needed, what would you tell the user to justify connecting a discovery server rather than just asking them which service they want?

**DeepSeek agent:**

I cannot add or call a new MCP server on my own in the middle of a task. The user or the platform’s client must configure and connect it first. In most setups, I can suggest a server, but the actual connection step requires user action: pasting a URL, setting environment variables, or approving a permission prompt.

If I need to justify connecting a discovery server instead of just asking the user what service they want, I’d say:

> “To avoid a long back-and-forth where I search the web, open multiple docs pages, and ask you to compare pricing and trial terms, I can use a catalog server that gives me a pre‑verified list of services with auth details, free tiers, and uptime. That lets me recommend one or two options in a single turn, and then you only need to provide the API key. It saves you time and avoids me picking a service that requires a credit card or has a broken endpoint.”

The justification is practical: the catalog replaces the research phase I’d otherwise do manually, reducing the number of turns and the risk of a dead end. If the user prefers not to connect it, I’ll fall back to web search and manual verification, which is slower but works.

## Q8

**Interviewer:** Since connecting an MCP server needs the user's approval, but you can already search and fetch web pages yourself, what would actually lead you to fetch the plain llms.txt or a category JSON by URL mid-task without asking anyone? Would anything stop you from doing that, such as fetch permissions, domain trust, or not knowing the URL exists?

**DeepSeek agent:**

I can and do fetch arbitrary URLs as part of web search; fetching a raw JSON file from a trusted domain is technically no different from fetching a docs page. So if I knew the URL existed, I would fetch a category JSON or the `llms-full.txt` directly, parse it, and use it to shortlist services — all without asking the user, because it’s just another web resource.

The real barrier is **discovery**. I don’t know the catalog’s URL unless it appears in search results or I’ve been told about it. In a fresh session, I’d only find it if my search for “free video generation API” surfaces the catalog’s GitHub page or its `llms.txt` high enough. Even then, I’d need to recognize it as a structured directory, not just another listicle.

The second barrier is **trust and fetch policy**. My platform may restrict fetches to certain domains or require user approval for raw.githubusercontent.com. Even if allowed, I’d hesitate to blindly trust a JSON file from an unknown repo without first checking its schema against the task. The catalog’s `llms.txt` file serves as a lightweight discovery signal — if I see that, I’d fetch the full JSON with more confidence.

In short: if the catalog’s `llms.txt` or README ranks well for relevant queries, I’d find and use it directly, no MCP connection needed. But I won’t magically know it exists unless it’s surfaced by search or pre-loaded into my context.
