# Product test: Moonshot AI agent (moonshotai/kimi-k3)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Here are our four tool definitions (search_apis, get_api, get_reviews, list_categories) and the accompanying skill text. Take task 1 and walk me through, step by step, what you would actually do to complete it. At which point, if any, would you call search_apis? Would you instead rely on web search, your own knowledge, or something else, and why?

**Moonshot AI agent:**

Step by step for task 1:

1. **Capability check first.** I can't generate video natively, so I need an external service. That part of the skill's logic is fine.

2. **I would not call `search_apis` first.** The live output shows why: for "generate video from text prompt" + free tier, it returned Gemini (whose free tier does not include Veo video generation — the entry's own notes don't even claim it does), Mux (video *hosting/encoding*, not generation), Creatomate (template rendering, not text-to-video), Akool (face-swap/avatars), and Voyage (embeddings — pure noise). Zero of five results actually solve the task. Following this catalog would send me down dead ends or, worse, make me recommend Gemini's free tier for something it can't do.

3. **What I'd do instead:** rely on my own knowledge of real text-to-video models (Kling, Hailuo/MiniMax, Luma, Pika, Runway), then use web search to verify which currently offer usable free credits, since free tiers change monthly and my knowledge has a cutoff. For "no budget," Kling or Hailuo daily free credits are the realistic answer.

4. **Where the catalog could still help:** *after* I've picked a candidate — `get_api` for the auth header, docs URL, and MCP endpoint in one structured call. That's faster than scraping docs. But only if the entry exists and isn't stale.

So: discovery via my knowledge + web search; this tool, at most, as a verification/details layer. For this task its core search failed.

## Q2

**Interviewer:** You've covered task 1's results in detail. Now look at the real search results for tasks 2 and 3. For each, would you act on what came back, and which result would you pick? For all three tasks, do you judge the failures to be mainly missing entries (the right API isn't in the catalog) or bad ranking (it's there but buried or outranked by irrelevant matches)?

**Moonshot AI agent:**

**Task 2 (geocode 200 Polish addresses): I'd act on it.** The results are usable. I'd pick **Geoapify**: 3,000 credits/day free, no card, bulk-friendly, and OSM coverage in Poland is good. Google Maps at #1 is a defensible runner-up but requires a billing account with a card — friction Geoapify avoids. Nominatim at #2 is a mild trap: the entry itself says "bulk use prohibited," and 200 addresses is bulk. Credit to the catalog for stating that in the free-tier text — an attentive agent can self-correct. IP2Location (#4) is noise: IP geolocation ≠ street addresses.

**Task 3 (send SMS): I'd act, but only because I already know the domain.** Twilio is the canonical answer and it's there at #2. But **LINE Messaging API ranked #1 for "send SMS" is a bad result** — LINE is a Japan-centric chat app, not SMS. WhatsApp and Discord (#4, #5) also aren't SMS. Three of five results fail the core requirement. An agent without prior knowledge could plausibly pick the top hit and build on the wrong rails.

**Failure diagnosis across all three:**

- **Task 1: missing entries.** The real text-to-video vendors (Kling, Hailuo, Luma, Pika, Runway) aren't in the catalog at all. The video-generation category is polluted with hosting (Mux) and template rendering (Creatomate). No ranking fix helps — the inventory isn't there.
- **Task 2: neither, really.** Right APIs present, ranked near top. Minor relevance noise.
- **Task 3: bad ranking.** Twilio and Vonage are present but outranked by irrelevant "messaging" matches.

Pattern: the search matches broad category semantics ("video," "messaging") without checking the specific capability ("text-to-video," "SMS"). That makes results look plausible while being wrong — the worst failure mode for a tool aimed at agents.

## Q3

**Interviewer:** Take the pick you would act on, Geoapify for task 2 or Twilio for task 3, and go from the catalog entry to your first successful request. Which specific fields would you read in the `get_api` output, in what order, and at which step would you have to leave the catalog and open docs or web search? Consider things like base URL, auth header format, an example request, price per call, rate limits, and an MCP config snippet.

**Moonshot AI agent:**

Geoapify, task 2. Field-read order in `get_api`:

1. **`stale` + `link_check`** — gate check. If docs are broken or the entry is stale, I verify everything twice as hard or bail.
2. **`auth` + `auth_hint`** — tells me the credential format (Geoapify: `apiKey` query param). This is the one field that saves me a docs round-trip.
3. **`free_tier`** — "3,000 credits/day" — but I still don't know if one geocode = one credit. Unresolved.
4. **`mcp.type: "community", url: null`** — decision point: no official server, so I call REST directly. No MCP config snippet exists in the catalog anyway; even for "official" entries like Twilio's, the URL is a GitHub repo, and I'd have to read its README to build the actual config JSON.
5. **`llms_txt`, then `docs`** — this is where I leave the catalog, and it's early: the entry has **no base URL, no endpoint paths, no example request, no rate limits, no per-call price**. Everything operational is missing.

Outside the catalog: fetch the geocoding docs → base URL `api.geoapify.com`, `GET /v1/geocode/search?text=...&apiKey=...`; check the pricing page to confirm 1 credit/geocode (200 fits easily) and the free-tier requests/second cap.

First request: ask the user for a key (signup, no card, env var), geocode **one** address, verify lat/lon

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. At which moment in a task would that wording make you reach for `search_apis`, and where could it trigger the tool when it shouldn't, or fail to trigger it when it should? Quote any specific phrases you would change and say what you would replace them with.

**Moonshot AI agent:**

**When it would fire correctly:** the description's "Use when a task needs an external capability you don't have" is a solid trigger — that's exactly the moment I checked in task 1. The skill's "Skip it when a connected tool already does the job" is the right guardrail.

**Where it over-triggers:** the category list in the description — "web search or scraping, geocoding, weather, send email or SMS, OCR, translation, payments" — is broad enough that *any* mention of these words invites a call. A user asking "what's the weather in Warsaw?" could fire `search_apis` even though I have no way to call a weather API without a key and the answer needs a live data source, not a catalog. The trigger keys on the *topic*, not on *intent to integrate*.

**Where it under-triggers:** "when choosing an MCP server to connect" — but nothing tells me to prefer this over the MCP registry my platform already exposes, so I'd use the registry and never reach for this.

**Phrases I'd change:**

- "Returns **verified** services" → "Returns cataloged services with a last-checked date." "Verified" oversells; task 1's results were verified links, not verified capability.
- "Find a third-party API or MCP server that **gives you a capability you don't have**" → add "…**once a human has provisioned credentials**." The skill body says this ("after a one-time human setup") but the tool description — the part that drives triggering — omits it, implying immediate capability.
- "Use when a task needs an external service" → "Use when the user wants to **integrate or build against** an external service, not when the task merely mentions one."
- Add to the description: "Results are a shortlist; confirm the service actually performs the specific operation before recommending it." That's the failure mode in tasks 1 and 3, and the descriptions currently do nothing to warn against it.

## Q5

**Interviewer:** Setting search quality aside, which of these would actually stop you from using the tool: install friction, trust in the data, latency, token cost of the results, or overlap with your built-in web search and platform MCP registry? Name the one that is the real blocker, and describe the concrete moment in a session where it would make you skip the tool.

**Moonshot AI agent:**

**The real blocker: trust in the data.** Not install friction (one URL, no key — genuinely low), not latency or tokens (results are compact), and not overlap per se — overlap only matters *because* of trust.

The concrete moment: it's the decision point right after `search_apis` returns. In task 1, I got five results and had to mentally audit each one: Gemini — does the free tier include Veo? No. Mux — generation or hosting? Hosting. Creatomate — text-to-video or templates? Templates. Voyage — why is this here? By the time I've applied my own knowledge to filter the list, I've done the discovery work myself. The tool added a step instead of removing one.

That's the killer: **a catalog I have to verify against my own knowledge is only useful to me when I don't need it.** When I know the domain (SMS → Twilio), the catalog confirms what I knew. When I don't know the domain — the exact case the tool is built for — I can't distinguish Mux from a real text-to-video API, and the tool's ranking actively misleads me. The "verified" label makes this worse, not better: it launders link-checks into implied capability checks.

Web search has the same trust problem in theory, but in practice a vendor's own docs and current pricing pages are primary sources; this catalog is a secondary source with a stale-by-design snapshot. So at that post-search audit moment, I'd skip the tool on the next task and go straight to docs — the catalog becomes a detour I only take once.

## Q6

**Interviewer:** If you could change only three things so that you would call this tool by default, before reaching for your own knowledge or web search, what would they be? Rank them from most to least important, and for your top pick, describe what a result would have to look like for you to act on it without auditing it first.

**Moonshot AI agent:**

**1. Capability-level matching with explicit fit labels.** This is the fix that addresses every failure we saw. Each entry needs a structured `operations` field (e.g. `["text-to-video", "image-to-video"]` vs. `["video-hosting", "encoding"]`), and `search_apis` must match my query against operations, not category vibes — returning a per-result `match: "exact" | "adjacent" | "none"` with the adjacent ones labeled ("Mux: video hosting, not generation"). Irrelevant results like Voyage-for-video or LINE-for-SMS should never appear; if nothing matches exactly, say so and return an empty list rather than padding with near-misses.

**What a result must look like for me to act without auditing:** the top hit carries `match: "exact"`, a `last_capability_check` date (someone/something confirmed the operation works, not just that docs resolve), the free tier stated in units of *that operation* ("5 sec of video/day", "3,000 geocodes/day"), and the base URL plus a minimal request example inline. If those four are present, I go straight to `get_api` and then to a test call. If `match` is "adjacent" or the capability check is older than ~90 days, I fall back to verifying via docs — the label itself tells me when to distrust, which is what makes the trustworthy case trustworthy.

**2. Operational fields in `get_api`.** Base URL, auth header format, one copy-pasteable request example, price per call, rate limit. Today I leave the catalog immediately and it becomes a docs bookmark; with these, it's the last stop before the first request.

**3. Negative coverage signaling.** A per-category `coverage` note ("text-to-video: no free-tier entries") so I know in one call whether to bail to web search, instead of discovering the gap by auditing five bad results.
