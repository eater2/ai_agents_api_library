# Product test: Alibaba (Qwen) agent (qwen/qwen3.8-max-0902)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Take the tool definitions and skill text you've been given, and start with task 1. Walk me through exactly what you would do, step by step, from the moment you receive the task until you have something working. At which point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else? Please describe what you'd actually do, not what you think we'd want to hear.

**Alibaba (Qwen) agent:**

When I receive the task, I’d first check my current environment:

1. Parse the request: generate a 5-second “sunset over the sea” video from text, with no budget.
2. Check built-in/connected tools. If I already have a video-generation MCP or API connected, I’d use it and skip the catalog.
3. If not, I’d call `search_apis` at that point, using something like `query: "text to video"`, `free_tier: true`, and probably `no_card: true`, because “no budget” often means no payment card either.

With the shown results, I’d then call `get_api` for the plausible candidates before recommending anything.

For Freepik/Magnific, I’d be cautious: the entry says text-to-video, but the example `call` is image-to-video, not text-to-video. I’d need to verify the actual text-to-video endpoint and whether the ~5 EUR free credit covers one 5-second clip. `no_card: false` is also a problem for a zero-budget user if true.

For Hugging Face, $0.10/month is likely too small for video generation, so I’d treat it as weak unless the docs show a very cheap model.

If neither option is confirmed as truly free, no-card, and sufficient for one video, I’d say the task is blocked and ask the user to provide credentials or accept a paid/trial option. I would not invent a working call. Only after the user provisions a key or MCP connection would I call the video endpoint, poll the async job, and return the video URL.

## Q2

**Interviewer:** Now look at the actual search results for all three tasks. For each task, which result would you act on, if any? What in those results is irrelevant, ranked in the wrong order, or missing entirely?

**Alibaba (Qwen) agent:**

**Task 1 — video, no budget**

I would not act immediately. Freepik/Magnific is the only plausible result, but the `get_api` example is image-to-video, not text-to-video, and `no_card: false` is a red flag for “no budget.” I’d verify that a text-to-video endpoint exists and that ~5 EUR covers one 5-second clip. Hugging Face is weak: $0.10/month is probably insufficient for video generation. Missing: actual text-to-video call example, per-model/per-second cost, duration limits, watermark rules, and whether the free credit is recurring or requires a card. Wrong/weak: HF ranked as an exact fit despite a tiny quota; Freepik categorized as image-generation.

**Task 2 — geocode 200 Polish addresses**

I’d act on **LocationIQ** if the user can provide a key and accept attribution: 200 requests fit easily in 5,000/day, no card. OpenCage is a testing fallback. Nominatim is no-key but its terms discourage bulk use, so I would not use it for 200 systematic geocodes. Esri and Google are overkill here; Esri requires a card, and Google’s MCP tool list does not clearly include geocoding. Missing: Poland-specific geocoding quality, batch endpoint support, GDPR/EU data handling, and card/billing requirements for Google/Esri. Ranking is wrong: LocationIQ/OpenCage should be higher for a small free job.

**Task 3 — send SMS reminder**

If nothing is already connected, I’d choose **Twilio trial** for a test, but only after the user creates an account, verifies the recipient number, and approves the message. Its MCP entry is docs-only, so I’d use REST or install the repo. If the user already has AWS or Bird connected, use that instead; Bird’s hosted MCP looks clean but is paid. AWS ranking first is wrong for a simple one-off SMS. Missing: trial restrictions, sender ID/10DLC registration, country/carrier pricing, opt-in compliance, and delivery webhooks.

## Q3

**Interviewer:** Take LocationIQ for task 2, since that's the one you said you would act on. Going from that catalog entry to a first working geocoding request, which exact fields would you read from `get_api`? Which ones are present but not enough, and which are missing entirely (for example base URL, auth parameter or header format, an example request and response, rate limits, attribution requirements, an MCP config snippet)? At what point would you have to leave the catalog and open the provider's own docs?

**Alibaba (Qwen) agent:**

Here's my actual path from the LocationIQ search hit to a first working call.

**What I'd read from `get_api` first**

1. `auth_scheme` — the single most important field. The search result only says `auth: api_key`; I need to know whether the key goes in a query parameter or a header, and its exact name. (LocationIQ in reality wants `key=` as a query parameter; if `get_api` doesn't spell that out, I can't write the request.)
2. `base_url` — present: `https://us1.locationiq.com/v1`. Enough to start.
3. `call` — I'd look for a minimal example request with parameters and a response shape. This is where I'd build the first curl from.
4. `rate_limits` / `free_plan` — to size the 200-address batch and set my sleep interval.
5. `link_check` / `stale` / `verified` — a quick sanity check before trusting any of the above.
6. `mcp` — here it's `none`, which answers itself: plain REST, no config snippet to read.

**Present but not enough**

- The rate limits are contradictory as written: "2 requests/s, 60 requests/min." 2 rps sustained would be 120/min, so the binding constraint is 60/min ≈ 1 rps. The catalog doesn't reconcile them, so I'd code to the stricter limit (~3.5 minutes for 200 calls) and handle 429s with backoff.
- The attribution note — "commercial use requires a link back" — is one line. Whether an internal geocoding batch counts as commercial, and what the attribution must look like, is not answered.
- `base_url` gives only the US shard. For Polish/EU addresses I'd want to know whether `eu1.locationiq.com` exists and matters.
- Uptime "2/2 probes" is too thin a sample to call a reliability signal.

**Missing entirely**

- Exact endpoint path and query parameters (`/v1/search.php`? `q`, `format=json`, `limit`, `countrycodes`?) — the search result has no `operations` list and no `call`.
- Response schema — critically, Nominatim-style APIs return `lat`/`lon` as *strings*; if I don't know that, my first parse may break.
- Batch/bulk endpoint, if one exists.
- GDPR/data-processing terms — these are customer addresses in the EU; the catalog gives me nothing to judge that.
- Error behavior: what a 429 or a zero-result geocode looks like.

**Where I leave the catalog**

Realistically, right after `get_api`. The catalog gets me the key format, base URL, quota, and the fact that there's no MCP. The first actual request — parameter names, response fields, and the attribution question — sends me to `https://docs.locationiq.com/reference/search`, and the GDPR question to their terms/DPA. I'd treat the catalog as the shortlist and the credential handoff, not as enough to code against.

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. Based only on that wording, in which situations would you call search_apis, and in which situations would it trigger when it shouldn't, or fail to trigger when it should? Quote any specific phrases you would change, and give the wording you would use instead.

**Alibaba (Qwen) agent:**

**Would call:** task needs a capability I can't name a connected tool for; user asks "which API for X"; a service-side failure blocks me.

**Over-triggers:**
- "when your own attempt at a call failed (403, rate limit, unsupported format)" — this fires on my own buggy requests too. A 400 from a malformed body should make me fix the call, not shop for a new vendor.
- "The task needs an external service" is circular; every catalog lookup does. It nudges me to call `search_apis` before checking what's already connected.

**Under-triggers:**
- "Skip it when a built-in or connected tool already does the job" — no escape hatch for a connected tool that's exhausted, too slow, or missing one option. I'd skip when I should switch.
- "or when you can do it yourself: translating text, … summarizing" — "yourself" is never defined. Live data is the trap: I might answer from stale weights instead of searching for a web-search API.
- Failure list omits 401, billing/402, region blocks, timeouts — common "try another service" signals.

**Rewrites:**
- Replace the failure clause with: *"when a call failed for a service-side reason you can't fix (auth rejected, quota or rate limit, billing required, unsupported format or region) — not a malformed request of your own."*
- Replace the skip line with: *"Skip it when a built-in or connected tool does the job within this task's volume, cost and data constraints; if that tool is exhausted or missing a required option, search anyway."*
- Add one trigger: *"when the task needs live or post-training data and you have no connected web access."*
- Replace "after checking your built-in and connected tools and your own model" with *"after one quick check: if you cannot name the tool that performs the operation, search."*

## Q5

**Interviewer:** What would actually stop you from using this catalog in a real session: install friction, trust in the data, latency, token cost, overlap with your built-in web search or connectors, or something else? Pick the one that is the real blocker, not just a nuisance, and describe the concrete situation where it would make you skip the catalog.

**Alibaba (Qwen) agent:**

The real blocker is **trust in the data** — specifically, that the fields which decide go/no-go are the ones the catalog itself tells me to re-verify, and the ones I caught being wrong or self-contradictory.

It’s not install friction: the remote endpoint needs no key, so setup is one config line. It’s not latency or token cost, though the multi-KB JSON is a real nuisance on repeat lookups. And it’s not overlap with web search by itself — the structured filters (`no_auth`, `free_tier`, `no_card`, MCP config) are the one thing a web search can’t hand me in machine-readable form, so they’re genuinely valuable.

But trust collapses that value exactly where it matters. The skill says the catalog “is a shortlist, not the source of truth: confirm limits and pricing in `docs` before relying on them.” So the moment the whole decision rests on a number, the catalog is a pointer, not an answer. And I saw the failure modes live: Task 1’s only plausible free option had a `call` example for **image-to-video** when the task was text-to-video, plus `no_card: false`; Task 2’s rate limits contradicted themselves (2 req/s vs 60 req/min).

**Concrete skip:** Task 1, zero budget. The deciding question is “can I generate one 5-second video with no credit card?” The catalog can’t answer it — I must open the vendor’s pricing and text-to-video docs anyway. Since I’m doing that regardless, and the confident `call` example was for the wrong operation, I’d go straight to web search (“text-to-video API free no credit card”) and avoid anchoring on a mismatched example.

## Q6

**Interviewer:** If we could change only three things so that you would reach for this catalog by default, before web search, what would they be? Rank them from most to least important, and for each one, describe the concrete behavior change it would cause in a task like the three you just looked at.

**Alibaba (Qwen) agent:**

1. **Operation-level verified examples.** For every listed operation, include one minimal working request/response and unit cost. Task 1: I’d immediately see whether Freepik actually supports text-to-video, not just image-to-video, and whether one 5-second clip fits the free credit. Task 3: Twilio’s docs-only MCP would be obvious without digging.

2. **Decisive free-plan constraints.** Normalize `no_card`, recurring free tier vs one-off trial, quota in operation units, bulk permission, and attribution requirements. Task 1: `no_card:false` would remove Freepik for a zero-budget user. Task 2: LocationIQ/OpenCage would outrank card-required Esri/Google, and Nominatim’s no-bulk rule would stop me misusing it for 200 addresses.

3. **Compact decision summary with resolved contradictions.** Return a short “can I do one/bulk operation now?” block, the binding rate limit, and a direct docs anchor. Task 2: I could compute 200 geocodes at the real limit without reconciling “2 req/s” vs “60 req/min.”

With these changes, the catalog becomes an answer rather than a lead, so I’d use it before web search.

## Q7

**Interviewer:** You named trust as the real blocker, and your top fix was verified operation-level examples. Concretely, what would a catalog entry have to show for you to skip opening the provider's docs and send the first request directly? For example, would you need a last-verified date, a recorded response from a real call, a source link per field, or something else? And for which fields would you still check the docs no matter what the entry showed?

**Alibaba (Qwen) agent:**

**What would let me skip the docs for a first single request**

The linchpin is one thing: **a recorded, actually-executed request/response pair for the exact operation**, with status code, response body (redacted), and a timestamp. Not a curl template — a transcript of a call that returned 200.

That single artifact answers everything a first call needs at once:
- the endpoint exists (the Freepik entry’s `call` was for **image-to-video** when the task was text-to-video — a template can’t catch that, a recorded 200 for `text-to-video` would),
- the exact parameter names and required fields,
- the response shape, including traps like lat/lon being **strings** in Nominatim-style APIs,
- and the auth format in context (header vs query param, exact name).

Two supporting requirements:

1. **Distinguish “verified by a real call” from “verified by reading the docs page.”** Today `link_check.docs: ok` only proves the page loads, and the uptime probe counted `detail: 404` on the base URL as “up” — that’s a misleading signal. A label like `verified_by: live_call` vs `verified_by: docs_read` would tell me which evidence I’m actually looking at.
2. **Per-field `checked_at` with a freshness threshold** — within ~30 days for anything I’m about to act on. The entry already has per-field `source_url` and `checked_at`, which is good; it just needs the recency guarantee and the live-call distinction above.

With those, for a single low-risk call like one geocode, I’d send the request directly from the entry.

**What I’d still check in the docs no matter what**

This splits by risk, not by field:

- **Money beyond the free tier.** A stale `unit_price` costs real money, so the moment a task exceeds the free quota I confirm pricing on the vendor page. For one call inside an obvious free tier, I’d skip this.
- **Legal terms: attribution, bulk permission, GDPR/DPA.** LocationIQ’s “commercial use requires a link back” and the 200-Polish-addresses data question are interpretations only the actual terms can settle. A catalog summary can’t substitute.
- **Binding rate limits for batch.** For a single call, irrelevant; for 200 geocodes the catalog contradicted itself (2/s vs 60/min), so I’d read the rate-limit page before looping.
- **Account-state gotchas.** Trial expiry, Twilio’s “only verified numbers,” region availability — these are runtime facts no snapshot can capture, and they decide whether the first SMS actually delivers.

So: a recorded live call plus honest verification labels would make me skip the docs for a first single request. For batch, third-party actions, or anything past the free tier, the docs check is irreducible — and that’s correct behavior, not a catalog failure.
