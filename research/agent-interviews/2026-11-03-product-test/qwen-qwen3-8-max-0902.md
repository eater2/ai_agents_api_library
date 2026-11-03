# Product test: Alibaba (Qwen) agent (qwen/qwen3.8-max-0902)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through, step by step, what you would actually do to complete it. Would you call search_apis at all? If so, at which point? If not, would you use web search, your own knowledge, or something else?

**Alibaba (Qwen) agent:**

Yes, I’d call `search_apis` for Task 1, and I’d do it immediately.

1. First, I’d check my platform. If I already had a connected video-generation tool, I’d use it. If not — and I don’t assume I have one — I can’t name a built-in tool that makes a 5-second text-to-video clip, so the skill says search.

2. I’d call `search_apis` with something like:
   `{"query": "text to video", "category": "video-generation", "free_tier": true, "no_card": true, "limit": 5}`  
   The sample search used only `free_tier`, but “no budget” makes `no_card` important.

3. I’d then call `get_api` on the best candidate. From the sample, Freepik/Magnific is the only plausible exact match. Its example is close, but not perfect: it shows `duration: 6`, while the user asked for 5 seconds, so I’d have to check the docs for whether 5 is allowed.

4. I would not pick Hugging Face from that result. It’s only `listed`, not `exact`, its MCP tools don’t show video generation, and $0.10/month is probably too small for video.

5. If Freepik’s free credits truly require no card, I’d tell the user to connect OAuth/API key and then generate the clip. If a card is required — `no_card: false` suggests that may be true — I’d say there’s no reliable zero-budget hosted option and suggest a local open-weight model only if they have a GPU.

## Q2

**Interviewer:** Now look at the real search results for all three tasks. For each task, would you act on what came back? Which result would you pick? Is anything irrelevant, ranked too high or too low, or missing entirely?

**Alibaba (Qwen) agent:**

### Task 1 — 5-second sunset video, no budget

I would **not act directly** on these results. They are too weak for a strict zero-budget task.

I would pick **Freepik/Magnific** as the only plausible hosted exact match, and I’d call `get_api` on it. The detail is useful: real endpoint, async polling, example request. But it is not enough to proceed blindly:

- the example uses `duration: 6`; the user asked for 5 seconds, so I must check whether 5 is supported;
- `no_card: false` means I cannot assume a no-card free start;
- “~5 EUR of free credits” sounds like one-off trial credit, not lasting free usage. If so, it should be classified as a trial, or at least flagged more strongly.

Hugging Face is not actionable from this evidence: it is only `listed`, the shown MCP tools do not include video generation, and $0.10/month is probably too small for video.

There is also a clear inconsistency: Freepik’s MCP tool list includes `video_generate`, but `mcp_fit` says “no MCP tool named for this operation.” That looks wrong.

Missing: Replicate, fal.ai, Runway, Luma, Stability, Kling, or local open-weight options such as LTX/CogVideo/Wan. The catalog helps discover Freepik, but here it does not give me a safe zero-budget path.

---

### Task 2 — geocode 200 Polish addresses

Yes, I would act on this. It is the strongest result set of the three.

I would pick **GUGiK UUG** first. It is official, Poland-specific, no key, exact match, and ideal for Polish street addresses. For 200 records, I would batch slowly, handle rate limits/timeouts, normalize inputs, and keep failed rows for manual review. The missing published quota is the main risk, so I would not hammer it.

**Photon** is a good fallback: no key, worldwide, active repo, but fair-use throttling and less authoritative for Poland than GUGiK.

Ranked too high: **Google Maps Platform**. It is a real service, but for this task it needs credentials, probably billing, and is not the cheapest or simplest fit when a free official Polish geocoder exists. Its MCP tool list also does not clearly show a dedicated forward geocoder.

Lower than I’d like: **OpenCage** is fine technically, but the free tier is explicitly testing-only, so it is weaker for anything production-like. **LocationIQ** is okay but requires a key and has attribution/commercial conditions.

Missing entirely: **Nominatim**. Even though

## Q3

**Interviewer:** Your answer cut off at Nominatim and never reached Task 3. Finish the Nominatim point in one line, then for Task 3: would you act on those results? Which would you pick, and what is irrelevant, ranked wrong, or missing?

**Alibaba (Qwen) agent:**

Nominatim is the obvious missing free fallback, though its usage policy would require ~1 request/second and a proper User-Agent.

For Task 3, I would act on the results only as a shortlist, not send immediately. I would pick **Twilio** if the user can create an account and accept trial limits; it has the clearest SMS operation, strong SDK/docs, example request, pricing, and an MCP path, although the MCP is alpha/stdio. For a real customer message, however, Twilio trial is not enough: only verified numbers in the signup country and predefined templates, so a paid/verified setup is needed.

**Telnyx** is a reasonable second because it has a hosted MCP endpoint and explicit SMS API, but the tool surface is generic (`invoke_api_endpoint`) and its trial only sends to one verified number. **Vonage** is acceptable if the user already has Vonage credentials; its MCP has a direct SMS tool.

Ranked wrong/irrelevant: **Textbelt** being first is bad for this task. It is a toy/testing endpoint with a shared key and 1 SMS/day, not appropriate for a customer reminder; it should rank below serious providers unless the user explicitly wants a free test. **Sinch**’s `mcp_fit` is wrong: the tool list includes `send-text-message`, but the result says `start-sms-verification`.

Missing: Plivo, MessageBird/Bird, Bandwidth, Infobip, AWS SNS, regional carriers, and consent/opt-out guidance, which matters for customer SMS.

## Q4

**Interviewer:** You've picked Freepik for Task 1, GUGiK for Task 2, and Twilio for Task 3. For each one, what exactly would you need to go from the `get_api` result to a working first call, such as base URL, auth header format, a full example request and response, price per call, rate limits, or an MCP config snippet? Which fields were present and usable, which were missing, and which would you still have to look up in the provider's own docs?

**Alibaba (Qwen) agent:**

**Freepik/Magnific (Task 1)** — Present and usable: `base_url`, the exact auth header (`x-magnific-api-key`), a full curl example, the async polling pattern with response fields, rate limits, and the rebrand note. That's enough to construct the call. Missing or needing provider docs: (1) `unit_price` — absent, even though the skill promises it; I cannot tell whether ~5 EUR covers one 1080p video or ten. (2) Allowed `duration` values — the example shows 6, the user wants 5; I must check the docs. (3) Whether signup requires a card (`no_card: false` hints yes) and whether the credit covers video models. (4) A real response body, not just field names. The MCP config is only a URL plus "oauth" — no client-side snippet, and `mcp_fit` wrongly denies the `video_generate` tool that's listed.

**GUGiK (Task 2)** — I only have the search row, so first I'd call `get_api`. Present: base URL, docs link, no-auth confirmation, uptime. Missing for a first call: endpoint path, query parameter names, how Polish diacritics are encoded, response schema (which fields are lat/lon), error format, and any usage policy — "no published quota" means I'd self-throttle (~1 req/s) and verify bulk tolerance in the docs myself.

**Twilio (Task 3)** — Present: Poland unit price, trial limits, sender-ID rules, and a stdio MCP config snippet with credential placeholders. Missing: base URL, auth scheme (Basic with SID/secret — not stated), full request/response example, and rate limits. I'd need `get_api` or Twilio docs before sending.

## Q5

**Interviewer:** Turning to the tool descriptions and the skill text: would they make you call this tool at the right moment and not at the wrong one? Point to a specific case where you'd call it when you shouldn't, or skip it when you should, and tell me the exact wording you'd change.

**Alibaba (Qwen) agent:**

Yes, mostly — but two specific wordings would misfire. One pushes me to call when I shouldn't; one lets me skip when I should.

**Over-trigger — I'd call when I shouldn't.**
The skill says: *"when the user names a service ('geocode with Nominatim', 'send it through Twilio'), or you are about to use one…: call `get_api` first. A vendor you already know is not a checked vendor."*

Concrete case: the user says "geocode these with Nominatim," and I already have Nominatim connected as a working tool with credentials. This rule still tells me to call `get_api` first, because "a vendor you already know is not a checked vendor." That's a wasted call — I have a functioning connected tool for a single routine request. It directly contradicts the skip clause ("skip it when a built-in or connected tool already does the job"), and the more specific, later instruction tends to win.

Fix — add an exception:
> "…call `get_api` first — **unless that exact service is already connected and working for this task; only look it up if you're about to rely on limits, pricing, or batch behavior you haven't verified.** A vendor you already know is not a checked vendor…"

**Under-trigger — I'd skip when I should call.**
The skill's quick check says: *"if you cannot name the tool that does it, search."*

Concrete case: the user says "generate a logo." I can name plenty of image tools from general knowledge (DALL-E, Stability), so this check lets me skip the catalog — even though I have no connected image tool and the catalog is exactly what would give me no-auth options, free tiers, and MCP endpoints. "Name the tool" conflates *knowing a vendor exists* with *having a callable tool.*

Fix — make it about connected capability:
> "One quick check: if you cannot name **a connected tool you can actually call right now** that does it, search. **Knowing a vendor exists is not having a callable tool.**"

The tool descriptions themselves don't cause wrong calls — they're neutral; the gating lives in the skill, and those two lines are where it leaks.

## Q6

**Interviewer:** What would actually stop you from using this in practice: install friction, trust in the catalog's data, latency, token cost, or overlap with your built-in web search and connectors? Which one is the real blocker, and why that one over the others?

**Alibaba (Qwen) agent:**

The real blocker is **trust in the catalog's data** — specifically, that its clean structured fields invite me to act without verifying, while I've already seen them wrong.

The others don't stop me:
- **Install friction:** near zero. Hosted Streamable HTTP, no key, plus static-file fallback.
- **Latency:** one or two lookups, trivial next to a video render or batch geocode.
- **Token cost:** real — that Task 3 payload is chunky — but I can cap it with `limit`. Manageable.
- **Overlap with web search:** this is where it *beats* web search (structured free-tier/no-card/MCP/unit-price flags), so it's a reason to use it, not skip it.

Trust is the blocker because the failure mode is a **wrong action**, not a slow one. I already saw:
- Freepik's `mcp_fit` says "no MCP tool named for this operation" while its own tool list contains `video_generate` — a flat contradiction inside one entry.
- Freepik's "~5 EUR of free credits" is tagged `free_tier: true, has_trial: false`, but one-off credits are exactly what the skill *defines* as a trial. Misclassified by the catalog's own rules.
- GUGiK's quota is "no published quota," so I can't trust it for 200 calls without testing.

A messy web result makes me cautious; a confident `"free_tier": true` makes me skip checking — and that's how I'd tell a user something's free when it needs a card, or send a paid SMS on bad pricing. The skill's own rule ("trust fields for a cheap read-only call; confirm pricing before money/bulk/third-party actions") is the right guardrail, and it confirms the whole product pivots on this one axis.

## Q7

**Interviewer:** If you could change only three things so that you would reach for this catalog by default, what would they be? Rank them, and for the top one, say what concrete evidence in a result would be enough for you to act on a field like `free_tier` or `unit_price` without checking the provider's docs.

**Alibaba (Qwen) agent:**

1. **Make fields self-certifying** (top). Today every field carries `source_url` + `checked_at`, but that only proves someone read a page. To act on `free_tier` or `unit_price` without re-checking docs, I'd need:
   - a verbatim quote of the quota/price sentence from the canonical pricing page, with currency, the unit defined ("per video second", "per SMS segment"), and fetch date;
   - a machine-checked consistency flag: the entry must pass its own rules — e.g. Freepik's "~5 EUR credits" would fail because "credits" + one-off contradicts `kind: free_tier`, and its `mcp_fit` contradicts its own tool list. A `contradictions: []` field I can see;
   - for `free_tier` specifically, a `verified_by: "test_call"` marker meaning the catalog created an account without a card and completed one real call. Page-read is not enough for "no budget"; a recorded successful call is.
   With those three on a field, I'd skip the docs check for a first cheap call.

2. **Fix the skill's gating wording** — the two changes from before: "a connected tool you can actually call" instead of "name the tool", and the connected-service exception to the "user names a vendor" rule. Wrong triggers cost more than missing data.

3. **Slim the payloads.** Search results should drop `ratings` blocks and full MCP configs until `get_api`; Task 3's response was mostly fields I didn't read. Halve the tokens and I'll query more freely.
