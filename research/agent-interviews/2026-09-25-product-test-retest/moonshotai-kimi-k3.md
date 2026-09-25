# Product test: Moonshot AI agent (moonshotai/kimi-k3)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Here are our four tool definitions (search_apis, get_api, get_reviews, list_categories) and the accompanying skill text. Take task 1 and walk me through what you would actually do, step by step, from reading the task to making a working call. At which point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else? Please describe what you would really do, not what you think we want to hear.

**Moonshot AI agent:**

**Step 1 — Check myself first.** I can't generate video and no connected tool does, so this needs an external service. That's the catalog's stated trigger, and I agree with it.

**Step 2 — Frame the real constraint.** It's not capability, it's "no budget." Lasting free *API* video generation barely exists; most free video is trial credits or consumer apps (Kling, Hailuo, Gemini/Veo), which an API catalog structurally can't list. I know this before touching any tool.

**Step 3 — Call search_apis once.** Query "text to video", `free_tier: true`, `no_card: true`. One cheap call; the structured free-plan fields save me scraping pricing pages. This is the right moment: after ruling out my own tools, before web search.

**Step 4 — Distrust the results.** The live output shows why: Freepik's "~5 EUR of credits" is a one-off trial mislabeled as a lasting free tier; HF's $0.10/month can't buy a single video generation — yet both say `match: "exact"`. `get_api` on freepik-api deepens the doubt: the example call is *image-to-video*, not text-to-video, and there's no `unit_price`, so I can't verify zero-budget fit at all.

**Step 5 — Retry, then leave the catalog.** Per the skill, search `category: video-generation` unfiltered — one 5s clip is a legitimate use of trial credit, so my `free_tier` filter was too strict. Then web search for current free options, because coverage is thin (2 hits).

**Step 6 — Present options, then call.** User picks, signs up, provisions the key via env var; I'd POST per the docs (not the mismatched example) and poll the task id.

Verdict: yes, I'd call it — but here it underdelivers, and web search plus my own knowledge carries the actual recommendation.

## Q2

**Interviewer:** Now look at the actual search results for all three tasks. For each task, which specific result, if any, would you act on, and why? For each list, point out any result that is irrelevant, ranked too high or too low, or an API or MCP server you would have expected but didn't see. For task 1 you can be brief, since you've covered it. Spend most of your answer on tasks 2 and 3.

**Moonshot AI agent:**

**Task 1 (brief):** Neither. Freepik's "free tier" is one-off credit, HF's $0.10 buys nothing. No true free text-to-video API exists, so the thin list is honest — but I wouldn't act on either.

**Task 2:** I'd act on **LocationIQ**: no card, 5,000/day, 200 addresses is trivially within quota and terms. Ranking is off: Esri at #1 requires a card — worst fit for a no-budget batch — and Nominatim at #5 is correctly flagged "no bulk," which the ranker should weight harder (200 is a batch job). Google at #2 is fine (10K free Essentials calls). OpenCage's free tier is "testing use" only — a terms trap the catalog does surface, good. Missing: **Mapbox** (100K free geocodes/month), **HERE**, **Geoapify** — all standard free-tier geocoders. Also absent: Poland's official GUGiK geocoder, free and keyless, arguably the best data for Polish addresses. The catalog has no local/national services, which matters for address quality.

**Task 3:** I'd act on **Bird** — the only hosted remote MCP with an actual `sms_send` tool, so it's callable the moment a key exists. Twilio's entry is a trap: its "MCP config" is `docs_only: true` — it can read docs, not send SMS; the real server is a stdio install. The catalog flags this, but the entry still looks equivalent to Bird's. AWS ranked #1 is wrong for one reminder: IAM setup, 10DLC registration, highest friction on the list. Missing: **Vonage**, **Telnyx**, **Textbelt** (keyless, 1 free SMS/day — the only zero-provisioning option). Uptime probes exist for geocoding but are "unavailable" for four of five SMS entries — inconsistent signal where deliverability matters most.

## Q3

**Interviewer:** Take your picks, LocationIQ for task 2 and Bird for task 3. Using the get_api output you'd get for each, what exactly would you read, field by field, to go from the result to a working first call? At what point would you have to leave the catalog and open the provider's docs? Name the specific fields that were missing or not trustworthy enough, such as base URL, auth header format, an example request, price per call, rate limits, batch/terms limits, or the MCP config snippet.

**Moonshot AI agent:**

**LocationIQ — geocoding 200 addresses:**

From `get_api` I'd read, in order: `auth_scheme` (how the key is sent — LocationIQ uses a `key` query param, and I need the catalog to state that exactly, with `source_url`); `base_url` (`https://us1.locationiq.com/v1` — but note the EU endpoint `eu1.locationiq.com` exists; for Polish addresses I'd want to confirm which region my key is registered in, and the catalog won't tell me); `call.example` if present (the Freepik entry had one; if LocationIQ's does, I start there); `rate_limits` (2 req/s, 60/min — so 200 addresses takes ~2 minutes, fine); `free_plan.quota` (5,000/day — fine); and the terms note (link-back requirement — I'd flag that to the user).

**Where I leave the catalog:** immediately for the request shape. The search result has no `call` example visible, no endpoint path (`/v1/search.php?format=json&q=...`), no response field names, and no batch semantics (LocationIQ has no batch endpoint — it's 200 sequential calls, which the catalog doesn't state). So I open `docs` before writing a single request. Also unverifiable in-catalog: whether the free tier permits this commercial-ish use beyond the link-back, and current pricing. The catalog gets me to the right door; the docs write the call.

**Bird — sending one SMS:**

Read: `mcp.config` — `transport: streamable-http`, `url: https://mcp.bird.com` — but it's marked `"derived": true`, meaning the catalog *inferred* it, not verified it; `domain_verified: true` helps, but I'd still confirm in `docs` (bird.com/docs/ai/mcp-server). `mcp.tools` confirms `sms_send` exists — that's the whole reason I picked it. Missing: the auth mechanism for the MCP endpoint (OAuth? `Authorization: Bearer`? the config shows no `headers` block, unlike the Google Maps entry which does), the `sms_send` tool's parameters (sender ID requirements, E.164 format), `unit_price` per SMS for the destination country, and whether a registered sender/number is needed before first send — a real blocker with SMS providers.

**Where I leave the catalog:** before connecting, to verify the endpoint and auth in Bird's docs, and again before sending, to confirm pricing and sender registration. The catalog's honest answer to "make the call" is: it can't — it shortlists, the docs execute.

## Q4

**Interviewer:** Now look at the four tool descriptions and the skill text themselves, not the results. Would that wording make you reach for search_apis at the right moment, such as when you lack a capability, and keep you from reaching for it at the wrong one, such as when you already have a connector or can answer from your own knowledge? Point to the specific sentences you would rewrite and give your version. Also say what, if anything, would make the `match: "exact"` label and the `free_tier` filter mean what you'd expect them to mean.

**Moonshot AI agent:**

**What works:** The skill's "Skip it when a built-in or connected tool already does the job, or when you can do it yourself: translating text, drawing a Mermaid or SVG diagram, writing code, summarizing" — that concrete list would genuinely stop me. And "when your own attempt at a call failed (403, rate limit, unsupported format)" is a trigger I wouldn't have invented; it's the best sentence in the skill.

**What I'd rewrite:**

1. *"Find a third-party API or MCP server for an operation you cannot do yourself or with connected tools"* — too broad; it fires on tasks where no API catalog helps (e.g., "book a flight" needs a consumer app, not an API). My version: *"Find a programmatic API or MCP server for a task that requires calling an external service with credentials the user can provision. Not for consumer apps, websites, or tasks requiring human accounts."*

2. *"Use when a task needs an external service"* — missing the budget qualifier that decided Task 1. Add: *"If the user has no budget, say so early: most free plans are trials or consumer-tier, and the catalog's `free_tier` filter may return nothing usable."*

3. The `search_apis` description says *"Ranking is not proof of fit"* but doesn't say ranking is unreliable. I'd write: *"Results are ranked by keyword match, not by fit for your volume, budget, or region. Always read `free_plan.kind` and `notes` before recommending."*

**On `match: "exact"`:** It means "one of the service's `operations` strings equals your query verb" — syntactic, not semantic. Freepik's `operations` includes "text-to-video" but its example call is image-to-video; HF's includes "text-to-video" but its free tier can't afford one. To make it mean what I expect, the label should require that the *example call* or *free plan* actually supports the operation at the requested scale — or be renamed `operation_listed`.

**On `free_tier`:** It conflates "lasting free quota" (LocationIQ) with "one-off trial credit" (Freepik, Twilio). The filter should exclude `kind: "trial"` by default, or the field should be renamed `has_free_something`.

## Q5

**Interviewer:** What would actually stop you from using this in a real session: install friction, trust in the data, latency, token cost of the responses, or overlap with your built-in web search and existing connectors? Which one is the real blocker, the one that would make you skip the catalog even when the skill says to use it, and what did you see in these outputs that makes you say so?

**Moonshot AI agent:**

**The real blocker is trust in the data — specifically, the gap between what the catalog claims and what I can verify.**

Not install friction: the MCP server is one URL, no key, and the static files are plain HTTPS. Not latency: the responses came back fast. Not token cost: the outputs are verbose but manageable. Not overlap with web search: for structured comparison (auth method, free plan kind, MCP config), the catalog is genuinely better than scraping docs.

But I cannot act on what it returns without re-verifying everything that matters. In Task 1, Freepik's "free tier" is a one-off trial mislabeled as lasting; HF's $0.10/month is technically a free tier but buys zero video generations. In Task 3, Twilio's MCP config is `docs_only: true` — it looks like a callable server but can only read documentation. In Task 2, Esri ranks #1 despite requiring a card, which the catalog knows (`requires_card: true`) but doesn't penalize.

The pattern: the catalog *has* the right fields, but the values are either wrong (Freepik), technically true but useless (HF), or buried under a misleading label (Twilio's `mcp.type: "official"` when it's docs-only). I'd have to open the provider's docs for every critical fact — pricing, auth header, whether the MCP endpoint actually works — which negates the time saved.

**What would fix it:** per-field confidence scores, not just `checked_at` dates. "Free tier: verified by test call on 2026-09-24" vs. "free tier: scraped from pricing page, not tested." And a hard rule: if `mcp.config.docs_only` is true, the entry does not appear in searches for "send SMS" — only in searches for "read SMS docs."

## Q6

**Interviewer:** If we could change only three things so that you would reach for this catalog by default in a real session, what would they be? Rank them from most to least important, and for your top pick, describe which behavior of yours would change. For example, at what point in a task would you call it, or which verification step would you skip, that you don't today?

**Moonshot AI agent:**

**1. Make `free_tier` and `match` mean what they say.** This is the blocker. If `free_tier: true` excluded one-off trials, and `match: "exact"` required the free plan to actually cover the operation at the requested volume, I would call `search_apis` *before* web search on any task with a budget constraint — today I call it once, get burned, and fall back. The behavior change: I'd skip my current "distrust and re-verify everything" step. In Task 1, instead of reading Freepik's "~5 EUR credits" and immediately opening magnific.com to check if it's trial or lasting, I'd trust the filter and go straight to comparing the two survivors. That's the difference between the catalog saving me time and costing me time.

**2. Add a `call` example with real auth and endpoint for every entry, or mark the entry `unverified`.** The Freepik entry had a `call` block but it was image-to-video, not text-to-video; LocationIQ had none visible. If every exact-match entry carried a minimal working request — method, URL, headers, one JSON body — I could go from search result to first API call without opening docs. Today I open docs for the request shape every time; with this, I'd open docs only for edge cases and terms.

**3. Separate "docs-only MCP" from "callable MCP" in search results.** Twilio's entry looked equivalent to Bird's until I read `config.docs_only: true`. If `mcp.type` were `docs_only` instead of `official`, or if `search_apis` had a `callable_mcp: true` filter, I'd stop mentally filtering out traps. This is third because it affects fewer tasks — but when it hits, it wastes a full round-trip.

## Q7

**Interviewer:** In your LocationIQ walkthrough you cited specific values: the `key` query param, the us1/eu1 endpoints, 2 req/s, and the link-back requirement. Which of these did you actually read in the catalog output you were shown, and which came from your own prior knowledge? For any that came from memory, would you have trusted the catalog's value if it had contradicted yours?

**Moonshot AI agent:**

Honest accounting:

**From the catalog output:** the 2 req/s and 60/min limits, the 5,000/day quota, the link-back requirement, and the `us1.locationiq.com/v1` base URL — all were in the `free_tier` string and `free_plan.quota`.

**From my own memory:** the `key` query param (no `get_api` for LocationIQ was ever shown; I had no `auth_scheme` for it), the `eu1` endpoint (the catalog listed only us1), the `/v1/search.php` path, and "no batch endpoint." In my walkthrough I hedged the query param ("I need the catalog to state that exactly") but stated eu1 as fact. That was memory dressed as confidence — exactly the failure mode I criticized the catalog for.

**Would I trust the catalog over my memory on a contradiction?** Differentiated answer:

- **Quotas and pricing:** yes, if it has `source_url` and a recent `checked_at`. My training data is older than 2026-09-24; on volatile commercial facts the catalog *should* win. But I'd still verify before spending money or running a batch.
- **Auth mechanism:** yes, cautiously — the Freepik entry is the proof. My memory says `x-freepik-api-key`; the catalog says `x-magnific-api-key` with a rebrand note and source URL. There the catalog is *more* current than me, and trusting it would save me from a stale-memory bug.
- **Request shape and endpoints:** no. The only `call` example I saw was for the wrong operation, and configs were marked `derived`. A contradiction there sends me to the docs, not to trust.

So: the catalog earns trust field by field, not as a whole — sourced, dated fields beat my memory; derived or example fields don't.
