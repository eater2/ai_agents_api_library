# Product test: Alibaba (Qwen) agent (qwen/qwen3.8-max-0902)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Here are our tool definitions and skill. Take task 1 and walk me through what you would actually do, step by step, from reading the task to having a working result. At which point, if any, would you call search_apis? Or would you use web search, your own knowledge, or something else instead?

**Alibaba (Qwen) agent:**

For Task 1, I would do this:

1. **Check what I already have.** If my platform has a connected image/video generation tool, I’d use it. If not, I note that I cannot generate video natively.

2. **Interpret the constraint.** “No budget” means I should prefer `no_auth: true`, or at least a genuinely usable free tier without card entry or trial expiry.

3. **Call `search_apis` here**, probably with:
   - `query: "text to video"`
   - `category: "video-generation"`
   - `free_tier: true`
   - maybe `no_auth: true`

   I would call it after checking built-in/connected tools, not before.

4. **Evaluate the returned results.** In your live output, the results are weak: Gemini is not clearly a text-to-video generator, Mux is video hosting/encoding, Akool is avatar/face-swap, Creatomate is template rendering, Voyage is embeddings. So I would not pick any of them from this list alone.

5. **Use another source.** I would either fetch `catalog/video-generation.json`, use `list_categories`, or use web search/my own knowledge to find actual text-to-video services with free credits.

6. **Stop if nothing is truly free.** If all options require signup, card, or credits that are not enough, I would tell the user I cannot produce the video without a connected tool or credentials.

So: yes, I’d call `search_apis`, but only as a shortlist. In this case, its Task 1 results are too mismatched to use directly.

## Q2

**Interviewer:** At step 5, after `search_apis` returned mismatched results, what would you actually do first: rephrase the query and call `search_apis` again, open `catalog/video-generation.json`, or go to web search? What in the results or the tool text would decide that?

**Alibaba (Qwen) agent:**

I’d first retry `search_apis`, but much more constrained:

```json
{
  "query": "text to video",
  "category": "video-generation",
  "free_tier": true
}
```

or maybe `"generate video from prompt"`.

Why not web search immediately: the skill explicitly says to use the MCP tools when available, and the first call failed partly because I gave it a broad natural-language query without using the `category` filter. The schema shows `category`, and the returned entries include a `category` field, so the catalog clearly supports narrower lookup.

What would decide the next move:

- If the second call returns actual text-to-video services with plausible free tiers, I’d use `get_api` on the best one.
- If it still returns things like Mux, Gemini, Voyage, or template renderers, I’d stop trusting the search ranking and fetch `catalog/video-generation.json`. The skill gives the exact category URL and says the category files are small, so that’s the next cheapest reliable step.
- I’d go to web search only if the category file also has no real text-to-video option, or if I need to verify current free-tier limits because the catalog entry is stale, ambiguous, or missing docs.

So: constrained retry first, category JSON second, web search last.

## Q3

**Interviewer:** Now look at the real search results for all three tasks. For each task, would you act on what came back, and which result would you pick? Point to anything irrelevant, ranked too high or too low, or missing.

**Alibaba (Qwen) agent:**

**Task 1 — text-to-video, no budget:** I would not act on any of these. None is actually a text-to-video generator. Mux is hosting/encoding; Creatomate is template rendering; Voyage is embeddings (completely irrelevant — why is it in results at all?); Akool is face-swap/avatars; Gemini's own `what` field says "text and images", no mention of video. Missing: Luma, Runway, Kling, Pika, Minimax, fal.ai, Replicate. The `free_tier: true` filter also let in "free trial, 50 credits" (Creatomate), which is not what "no budget" wants — trials and free tiers are conflated.

**Task 2 — geocode 200 Polish addresses:** Yes, usable. I'd pick **Geoapify** (3,000 credits/day free covers 200 easily, no card) or **Nominatim** if I want zero signup — but its entry correctly warns 1 req/s and "bulk use prohibited", so I'd throttle and flag that to the user. Google works but needs a key and likely a billing account. **IP2Location is irrelevant** — that's IP-address geolocation, not street addresses, and it ranked 4th. Esri is miscategorized as `architecture-cad-bim`. Missing: OpenCage, Mapbox, HERE, Photon.

**Task 3 — send SMS:** I'd pick **Twilio** — only true SMS provider with an official MCP. LINE, WhatsApp and Discord are not SMS and shouldn't rank for "send SMS"; Discord especially. Also inconsistent: Twilio is `has_free_tier: true` while its text says trial-only, but Vonage with the same model is `has_free_tier: false, has_trial: true`. Pick one convention. Missing: Plivo, Sinch, AWS SNS.

## Q4

**Interviewer:** Take Twilio for Task 3 and Geoapify for Task 2. Going from the `get_api` entry to your first working request, which fields would you actually read, and in what order? What is missing that you would otherwise have to find in the docs or on the web, such as the base URL, auth header format, an example request, price per call, rate limits, or an MCP config snippet?

**Alibaba (Qwen) agent:**

I only have the real `get_api` body for Gemini, so I'm inferring Twilio/Geoapify entries from the schema (`docs`, `auth`+`auth_hint`, `mcp`, `free_tier`, `notes`, `link_check`, `openapi`/`llms_txt`, `ratings`).

**Geoapify — fields I'd read, in order:**
1. `docs` → the actual reference.
2. `auth` + `auth_hint` → is the key a header or query param? (Geoapify uses `?apiKey=`, not a header.)
3. `free_tier` → confirm 3,000 credits/day covers 200 calls.
4. `mcp` → it's `community` with `url: null`, so no MCP; I call REST directly.
5. `notes`, `link_check`, then `openapi`/`llms_txt` if present.

**Missing for Geoapify:** base URL and endpoint path (`https://api.geoapify.com/v1/geocode/search`), required params (`text`, `format=json`), response shape (lat/lon live in `features[].properties.lat/.lon`), per-second rate limit (free tier gives daily credits, not RPS), and signup/dashboard URL for the key.

**Twilio — fields in order:**
1. `docs`.
2. `auth` + `auth_hint` — this is the trap: entry says `api_key`, but Twilio uses **HTTP Basic Auth** (Account SID : Auth Token), not a bearer/header key. If `auth_hint` just says "api_key" it's misleading.
3. `mcp` → official repo, but it's a GitHub link, not a config.
4. `free_tier`/`notes` → trial limits.

**Missing for Twilio:** base URL + path (`/2010-04-01/Accounts/{Sid}/Messages.json`), required params (`To`, `From`, `Body`), that `From` must be an owned/verified number, trial restriction (only verified destination numbers), price per SMS, RPS limit, an example curl, and an MCP config snippet (env vars `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`).

So `get_api` gets me to "which service and roughly how to auth", but not to a working request without hitting `docs`.

## Q5

**Interviewer:** Now look at the tool descriptions and the skill text as written. Would they make you reach for this tool at the right moment and not at the wrong one? Name a specific task where you would call it but shouldn't, or skip it but should, and tell me the exact wording you would change.

**Alibaba (Qwen) agent:**

Mostly yes, but two misfires.

**False positive — "Translate this error message into Japanese."** The frontmatter lists "translation" as a trigger, so I'd load the skill and possibly call `search_apis` before remembering I translate natively. The skip condition ("Skip it when a connected tool already does the job") is buried in the body, not the description, and only covers *connected tools*, not my own model. Same trap for "diagrams" and "web search" in the trigger list. Fix that line to: *"Skip it when a connected tool **or your own model** already does the job — translation, summarization, Mermaid diagrams, built-in web search."*

**False negative — mid-task failure.** I'm fetching a page and hit a 403 anti-bot wall; a scraping/browser API would unblock me. But every "When to use" bullet is phrased as a user request ("the user asks", "the task needs"), not my own recovery. I'd likely just retry or give up. Add a bullet: *"when your own direct attempt failed — blocked fetch, unsupported format, rate limit — and an external service would unblock the task."*

**Minor:** `search_apis`'s tool description repeats "Use when a task needs an external capability you don't have" but drops the skip condition entirely, so at call time there's no reminder to check built-ins first. Append *"after checking built-in/connected tools."*

## Q6

**Interviewer:** What would actually stop you from using this in practice: install friction, trust in the catalog data, latency, token cost of results, or overlap with your built-in web search and connectors? Which one is the real blocker, and why that one over the others?

**Alibaba (Qwen) agent:**

The real blocker is **trust in the catalog data — specifically search relevance**. The others are survivable; this one isn't. Let me take them in order.

**Install friction — not it.** The server is no-key Streamable HTTP, and the skill gives a static-file fallback (`raw.githubusercontent.com/.../catalog/<category>.json`) that needs no connection at all. Near-zero friction.

**Latency — not it.** One HTTP call, trivial next to the actual task.

**Token cost — manageable.** Results are moderate; I cap them with `limit`. Only `get_reviews` at 100 would bloat, and I'd just set `limit: 10`. Not a blocker.

**Overlap with web search/connectors — real but partial.** Web search can't hand me `no_auth`, the auth header format, the MCP endpoint, and free-tier limits as one clean object. So the catalog genuinely adds structure *when it's right*. That raises the bar, though: it has to beat a quick web search.

**Trust — the blocker.** Field-level errors I can recover from, because the skill tells me to verify against `docs`. Twilio's auth being labeled `api_key` when it's really HTTP Basic — I'd catch that in the docs. But I can't recover from a search that returns **no valid candidate**. That's what happened in Task 1: Gemini/Mux/Voyage/Creatomate/Akool, none of which generate video from a text prompt. Task 2 surfaced IP2Location (IP geolocation) for street addresses; Task 3 surfaced LINE/WhatsApp/Discord for SMS. That's relevance failures in 3/3 live results.

Why this beats the rest: every other problem is fixable in-band (limit tokens, read docs, use the static fallback). A relevance failure gives me zero usable shortlist, so I fall back to web search anyway — meaning the tool added a step and then nothing. I'd still call it because it's cheap, but one Task-1-style miss and I drop it for that task.

## Q7

**Interviewer:** If you could change only three things so that you would call this by default instead of going straight to web search, what would they be? Rank them, and for each, say what you would do differently once it was fixed.

**Alibaba (Qwen) agent:**

**1. Fix search relevance — match on actual capability, not loose keywords.**
Task 1 returned zero real text-to-video services; Task 2 surfaced IP geolocation for street addresses; Task 3 ranked LINE/WhatsApp/Discord for SMS. Three out of three live searches had at least one wrong-category result.
*Once fixed:* I'd call `search_apis` first on any "I need an external capability" task and treat the top results as a real shortlist. Today I treat it as a guess and verify against web search, which defeats the point.

**2. Make `get_api` return a working request, not just signposts.**
I need the base URL, endpoint path, one example request, and the correct auth format (Twilio is Basic auth, not `api_key`). Right now every path leads to fetching `docs` anyway, so the catalog saves me discovery but not integration.
*Once fixed:* I'd go straight from `get_api` to asking the user for credentials or attempting the call, cutting out the docs round-trip entirely.

**3. Separate free tier from trial, and flag "no card required".**
Task 1's "no budget" constraint was undermined by Creatomate's 50-credit trial counting as `free_tier: true`. I can't filter for genuinely free services without web-checking each one.
*Once fixed:* budget-constrained tasks become one filtered call — `free_tier: true` plus a `no_card` flag — and I can present options without verifying pricing on the web.
