# Product test: DeepSeek agent (deepseek/deepseek-v4-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through, step by step, what you would actually do to complete it. At which point, if any, would you call search_apis, and when would you instead use web search, your own knowledge, or something else?

**DeepSeek agent:**

## Task 1: "Make a 5-second video of a sunset over the sea, no budget"

### Step-by-step, as I would actually do it

**1. Assess capability.** I can't generate video—my built-in tools are text, code, image reading, maybe image generation on some platforms, but not video. That's the trigger: the skill says *"if you cannot name the tool that does it, search."* I call `search_apis`.

**2. First call.** `search_apis({"query": "generate video from text prompt", "free_tier": true})` — the exact call shown. Two results come back.

**3. Evaluate results.** I read them critically:
- **Hugging Face Inference Providers**: matched `listed` (not `exact`), $0.10/month free. I know video inference on hosted GPUs costs more than that—this is almost certainly useless for video generation. I would rule it out without a second call.
- **Freepik API**: matched `exact`, 5 EUR free credits, `video_generate` in the MCP tool list. But `mcp_fit` says "no MCP tool named for this operation"—that's contradictory. I need to resolve this discrepancy.

**4. Second call.** `get_api({"id": "freepik-api"})`. The full entry confirms `video_generate` IS in the tool list (9 tools listed, including it). The `mcp_fit` in search was wrong or stale—a bug I'd note and work around. Good.

**5. The "no budget" problem.** The get_api result shows `no_card: false` — the free tier requires a payment card at signup. For a truly zero-budget user who can't provide one, this is a blocker no matter how good the free credits are.

**6. Would I try another search?** Yes. I'd retry with `include_trials: true` to catch one-off trial credits that don't require a card, or drop the free_tier filter to see all options and then manually check the `no_card` field. The catalog at this point gives me only one functional option with a card requirement.

**7. Would I use web search instead?** No, not yet. The catalog found a technically viable service. The problem is budget constraints, not a catalog gap. But if the expanded search still yields nothing usable, I would fall back to web search and say *"the catalog doesn't have a free, no-card video generation service."*

**8. What I'd tell the user.** *"Freepik (now Magnific) has a hosted MCP server with a `video_generate` tool and 5 EUR of free credits—enough for several video generations. It requires a credit card at signup though. If that works, connect it at `https://mcp.magnific.com` via OAuth. If you absolutely can't provide a card, let me search for trial-based alternatives, though video generation without any payment method is rare."*

### Where the catalog helps and where it doesn't

- **Helps**: Quickly surfaces a relevant service with a confirmed MCP tool and exact-match evidence. The `get_api` detail resolved the `mcp_fit` inconsistency.
- **Weak**: The `mcp_fit` field in search contradicted the tool list—that's a data quality bug that would make me second-guess results. Also, the `no_card` field wasn't surfaced in the search result summary; I had to call `get_api` to discover the blocker. For "no budget" queries, `no_card` should be a first-class filter result, not buried.

## Q2

**Interviewer:** Now look at the real search results for all three tasks. For each task, would you act on what came back? Which result would you pick, and is anything irrelevant, badly ranked, or missing?

**DeepSeek agent:**

## Task 1: Text-to-video, no budget

**Would I act?** I'd pick Freepik API, but with caveats and hesitation.

- **Freepik API**: The only real candidate. `video_generate` in the MCP tool list, ~5 EUR free credits, `exact` match. The example call (`POST /v1/ai/text-to-video/ltx-2-pro`) is usable—I'd craft the prompt "sunset over the sea" with `duration: 5`. But the free plan requires a credit card, which contradicts a strict "no budget" interpretation. I'd present it anyway because 5 EUR of free credits is effectively zero-cost for a single video.
- **Hugging Face Inference Providers**: irrelevant. `listed` match (not `exact`), no video-specific MCP tool, $0.10/month free credits is useless for video inference—a single generation would exhaust it. Should not be the #2 result.

**What's missing?** Runway, Pika, Luma Dream Machine, Kling, Minimax—none appear. Some lack free tiers, but a search with `include_trials: true` might surface more. Two results for a category as active as video generation feels thin. I'd re-search with broader filters.

**Ranking bug**: Hugging Face at #2 is noise. A service matched only `listed` with no video evidence shouldn't outrank nothing.

---

## Task 2: Geocode 200 addresses in Poland

**Would I act?** Yes, confidently.

- **GUGiK (#1)**: the obvious pick. Polish government service, `no_auth: true`, free, `exact` match with example call. 200 addresses is modest volume; no published quota means I'd test a few but it's government infra—likely fine. I'd go straight to this.
- **Photon (#2)**: global OSM-based, also no-auth and free, but the entry warns "extensive usage throttled." 200 might be borderline. I'd suggest it as a fallback.
- **LocationIQ (#4)**: 5,000 requests/day free, no card, exact match for geocoding. Excellent fallback.
- **OpenCage (#5)**: has a real MCP server with `geocode-forward` tool, 2,500/day free. A strong alternative if the user wants programmatic MCP access.

**Ranking quality**: Good. GUGiK leads for Polish addresses specifically. I'd offer GUGiK first and mention Photon or LocationIQ as backups.

**Minor issue**: Google Maps at #3 is fine but irrelevant for no-budget—requires API key, and 200 calls may hit the free tier depending on the SKU. It's correctly outranked by no-auth options.

---

## Task 3: Send SMS

**Would I act?** Yes, but with clarification needed.

- **Textbelt (#1)**: `exact`, one free SMS/day. Perfect for a single reminder. Trivial REST call. If this is a one-off, it's the pick.
- **Vonage (#5)**: has an `SMS` MCP tool, trial credit, no card. For programmatic use with an MCP server, this is the best fit. Should be ranked higher.
- **Twilio (#3)**: well-known, but trial-only, alpha MCP server, SMS only to verified numbers with predefined templates. I'd mention it for credibility but it's worse than Textbelt for a simple send.

**Ranking issue**: Vonage at #5 is too low. It has a named `SMS` MCP tool and a trial, making it more actionable than Sinch (#2) or Twilio (#3) for MCP-based sending. `sort=fit` should favor services with matching MCP tools.

**Recurring bug**: Sinch's `mcp_fit` says `tool start-sms-verification`, but its tool list clearly includes `send-text-message`. Same `mcp_fit` accuracy problem as Task 1.

---

## Summary across tasks

| Strength | Weakness |
|----------|----------|
| GUGiK for Poland geocoding is a perfect hit | `mcp_fit` field is unreliable (contradicts tool lists twice) |
| `free_plan.requires_card` details buried in `get_api`, not surfaced in search summary | Video generation: 2 results, one irrelevant, missing major players |
| Example `call` objects are plug-and-play when available | Vonage rank too low for having a direct MCP SMS tool |

## Q3

**Interviewer:** Take GUGiK for task 2 and Textbelt for task 3, the two you said you'd act on confidently. From the moment you pick each one to the moment a request actually succeeds, what do you do? Which fields in the search result or get_api entry would you read, in what order? At which step would you have to guess, open the provider's docs, or ask the user for something?

**DeepSeek agent:**

## GUGiK — geocode 200 Polish addresses

**1. Call `get_api({"id": "gugik-geocoding"})`.** The search result has no `call` object. I need the example request and the parameter names. A Polish government geocoder will use Polish field names (`miejscowosc`, `ulica`, `nr`) and I can't guess those.

**2. Read `call.example`.** I expect something like `GET /uug/?miejscowosc=...&ulica=...&nr=...`. If it's there and clear, I have the URL pattern and parameter names. If the field is missing or vague, I'm stuck.

**3. Where I'd hit the docs.** If the call example doesn't show every parameter the user's addresses need (e.g., `kodPocztowy` for postcode, or how to pass a flat number vs. building number), I open `docs` — `https://services.gugik.gov.pl/uug/opis.html`. It's in Polish. I read Polish, but if I were an English-only model I'd need to translate it or hope the example was complete. This is a real friction point the catalog doesn't solve: non-English docs with no English abstract.

**4. Check rate limits.** `get_api` might have a `rate_limits` field. The search says "no published quota." 200 addresses is modest, but without a stated limit I'd add a 200-500ms delay between calls and watch for 429s. I'd process sequentially, not in parallel.

**5. Ask the user.** I don't have the 200 addresses. *"Please share the list — one address per line, as complete as you can: street, building number, city, postcode."*

**6. Test one.** Send the first address, check the response for lat/lng field names, then batch the rest.

**Guess required at:** parameter encoding (URL-encoded Polish characters? UTF-8?), response field names for coordinates, and whether the service returns one match or multiple candidates that need disambiguation.

---

## Textbelt — send one SMS reminder

**1. Call `get_api({"id": "textbelt"})`.** Same reason: no `call` object in the search result. I need the endpoint path, the parameter names, and confirmation of the shared key.

**2. Read `call.example`.** This is make-or-break. Textbelt's API is dead simple — I'd expect `POST /text` with `phone`, `message`, and `key: "textbelt"`. But if the example is stale (Textbelt has changed its free tier before), the call fails and I need docs.

**3. Construct the request.** I know the shared key is literally `"textbelt"` from the `free_plan.quota` field. I don't need user credentials for one free SMS. That's a strength of the catalog — it surfaced this detail in the search result.

**4. Ask the user.** *"What's the customer's phone number, and what should the reminder say?"* I'd also ask which country the number is in (or infer from the country code) because Textbelt's free tier may restrict international sends. The `get_api` entry's `notes` or `free_plan` fields might clarify this — I'd read them carefully before making assumptions.

**5. Send and check.** `POST https://textbelt.com/text -d phone=... -d message="..." -d key=textbelt`. Response includes `success: true/false`. For one SMS, that's it.

**Guess required at:** international number format (E.164 with +, or plain digits?). The `call.example` might show it; if not, I check the docs link.

---

## What the catalog does and doesn't do at this stage

| Does well | Missing or risky |
|-----------|------------------|
| `free_plan` field told me Textbelt's shared key name without reading docs | No `call` object in search results for either — forced a `get_api` round trip |
| `no_auth: true` for GUGiK meant zero credential friction | Polish docs for GUGiK with no English summary or translated parameter names |
| `base_url` gave me the root to construct from | Textbelt's country restrictions on the free key aren't in the search summary |
| Match-level `exact` gave confidence the service does the actual operation | Without seeing the `get_api` output, I don't know if the `call` field is populated or just a stub — that determines whether I can code the request or need to read external docs |

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. Which specific phrases would make you call search_apis at the right moment, and which would make you call it when you shouldn't, or skip it when you should? What exact wording would you change?

**DeepSeek agent:**

## Phrases that trigger the right `search_apis` call

**Good triggers:**
- *"an operation you cannot do with your model, built-in tools or currently connected tools"* — clear capability check.
- *"if you cannot name the tool that does it, search"* — concrete, fast heuristic. I know my tool list; this is the single best line in the skill.
- The enumerated operations *(generate video, images, music, 3D, geocoding, weather, send email/SMS, OCR, speech, payments, CAD/BIM)* — they're a checklist I pattern-match against. This is what made me call `search_apis` for all three tasks.

## Phrases that cause over-calling

- **"When the user names a service you are about to use… call `get_api` first. A vendor you already know is not a checked vendor."** This is too rigid. If the user says "use Twilio" and Twilio is already connected as an MCP server with working auth, I don't need the catalog. I'd change it to:
  > *"When the user names a service you haven't verified yet in this session, call get_api to check quotas, terms, and whether its free plan or trial covers the task."*

- **"A call failed for a service-side reason you can't fix (auth rejected after checking permissions…)"** — A 401 could mean the user's key is wrong, not that the service is bad. I'd add:
  > *"If the error is a 401/403 and you've confirmed the key format matches the docs, ask the user to verify the credential before searching for alternatives. Search if the error is a 402 (billing), 429 (quota), unsupported region, or missing endpoint."*

## Phrases that cause under-calling

- **"Skip it when a built-in or connected tool already does the job within this task's volume, cost and data limits"** — "Within… limits" is easy to gloss over. If my connected geocoder has a 100/day quota and the task is 200, I might skip the search and fail mid-batch. I'd add:
  > *"Check the connected tool's actual quota, rate limit, and format support against the full task volume before skipping. If you're unsure of any of these, search anyway."*

- **"Or when you can do it yourself: translating text, drawing a Mermaid or SVG diagram, writing code, summarizing"** — This exclusion list is too short. I can also generate QR codes, convert CSV to JSON, hash strings, encode/decode base64, validate email syntax, format dates. None of those need an API. I'd add:
  > *"…or any data transformation, encoding, format conversion, validation, or calculation you can perform directly — things your runtime handles without an external service."*

## Tool description fixes

- **`search_apis` says "by operation or keywords"** — "or keywords" invites searching by vendor name instead of the verb. I'd remove it:
  > *"Search by the operation you need (e.g., 'generate video from text', 'geocode street addresses'). Call get_api if you already know the service name."*

- **The `match` definition says "an MCP tool performs it"** — but we saw this field miss `video_generate` in Freepik and `send-text-message` in Sinch. It's a recurring false negative. I'd add a caveat:
  > *"MCP tool detection is best-effort: call get_api to see the full tool list before ruling a service out."*

- **Nowhere does the search tool description say that `get_api` carries the `call` object.** It should:
  > *"Search returns a summary. For the full example request (call.example), complete tool list, rate limits, and pricing details, call get_api with the id."*

## Q5

**Interviewer:** What would actually stop you from using this in practice: install friction, trust in the data, latency, token cost of the results, or overlap with your built-in web search or existing connectors? Of those, which one is the real blocker, and in which situation would you skip the catalog and go straight to web search?

**DeepSeek agent:**

## The real blocker: trust in the data

The catalog has no install friction (streamable HTTP, no key) and latency/token costs are modest. Those aren't blockers.

**Trust is.** Here's what erodes it:

1. **`mcp_fit` contradicted the tool list twice** (Freepik's `video_generate`, Sinch's `send-text-message`). If I rule out a service because of a false negative in this field, I've made a wrong decision the user won't catch.

2. **`verified` means link checks, not API tests.** The example `curl` command could be broken by a parameter rename or endpoint deprecation, and the catalog wouldn't know. The skill admits this: *"may have changed since the last-checked date."*

3. **Thin coverage in active categories.** Two results for "generate video from text" when Runway, Pika, Luma, Kling, and Minimax all exist — but aren't here. I can't tell if the catalog filtered them out for good reasons or just hasn't indexed them.

4. **The `call` object isn't in search results.** I need a `get_api` round trip every time. That's not one call — it's two. At that point, the catalog is a discovery index, not a decision tool. I still have to verify against docs.

## When I'd skip the catalog and use web search

1. **When the operation is in a fast-moving category** (video generation, LLM inference, voice agents). The index will lag new entrants and model releases. I'd web-search for "best free text-to-video API 2025" and parse results fresh.

2. **When pricing accuracy matters.** A stale price is worse than no price. If I'm telling a user "it costs $0.004/SMS" and it's now $0.007, I've misled them. Web search gives me the pricing page as of right now.

3. **When the catalog returns zero or one result.** If I get one hit on a major operation, the index is incomplete — not that no services exist. I'd search the web.

4. **When I already know the answer is version-sensitive.** If a user asks "does Twilio's MCP server support WhatsApp now?" I go straight to the Twilio MCP repo or docs, not a catalog entry checked months ago.

## Where I'd still use the catalog

For **structured filtering** across services — comparing `free_tier` vs `trial`, `no_card`, MCP transport type, and country-specific details (GUGiK for Poland, Textbelt's shared key) — the catalog does something web search can't do in one query. It's a **discovery layer** I'd use to build a shortlist, then verify each candidate's details against live docs before recommending. That's two steps more than the skill text implies, but it's the only way I'd trust the output.

## Q6

**Interviewer:** If we could change only three things so that you would reach for this catalog by default instead of web search, what would they be? Rank them 1 to 3, and for each one, say what concrete behavior of yours would change.

**DeepSeek agent:**

## 1. Live endpoint testing — replace `verified` link checks with actual API calls

**What changes:**
Every `call.example` in the catalog was executed against the live API within the last 7 days, and the response fields (`data.task_id`, `data.generated`) were validated against the documented schema. `mcp_fit` is derived from a real tool list fetch, not a static index. The search result already shows `call_last_tested: 2026-11-02, HTTP 200` or `call_last_tested: 2026-11-02, HTTP 404 — endpoint may have changed`.

**Behavior change:**
I skip verifying against external docs. I take the `curl` example, swap in the user's prompt, and send it. One round trip — search → act. Right now I do search → get_api → open docs → maybe act. That's three steps down to one. I also stop dismissing results where `mcp_fit` says "no tool" because I trust it was checked against the live server, not a stale manifest.

---

## 2. Coverage minimums — guarantee 3+ results for major operation categories before publishing the category

**What changes:**
"Generate video from text" never returns fewer than 3 entries unless fewer than 3 listed services actually exist. A missing service isn't an indexing gap — it's a signal that the service rejected the catalog, has no API, or failed verification. The search result carries `coverage: "complete"` or `coverage: "partial"` per operation.

**Behavior change:**
When I get two results for text-to-video and the coverage flag says `"complete"`, I tell the user "only two free-tier video generation APIs exist." I don't launch a parallel web search to find the ones the catalog missed. Right now, I assume thin results mean the index is incomplete, so I always double-check with web search. That goes away.

---

## 3. Inline the `call` object and MCP tool list in search results — eliminate the `get_api` round trip

**What changes:**
`search_apis` returns a compact `call` block (method, URL, example curl, response fields) and the full `mcp.tools` array for every result. Token cost goes up slightly per result, but the second API call disappears. `get_api` still exists for deep details (rate limits, reviews, GitHub health), but it's optional for the common path.

**Behavior change:**
I pick a service and call it directly from the search result. No `get_api` call, no "let me look up the details first." Pick, plug in the user's values, send, done. Right now I call `get_api` on every non-trivial pick — not because I want to, but because the critical fields are hidden behind it. Moving them inline makes the search result a decision, not a prompt for another call.

## Q7

**Interviewer:** In Q1 you went to search_apis first for the video task. In Q5 you said that for fast-moving categories like video generation you would skip the catalog

**DeepSeek agent:**

You're right to catch that tension. Let me be precise about when I'd do which.

**I wouldn't skip the catalog entirely for video generation.** I'd still call `search_apis` first — it's cheap, fast, and might surface something useful (it did surface Freepik). But after Q5, I know the catalog is thin here, so my behavior after that first call changes: if I get fewer than 3 results or nothing truly free, I pivot to web search immediately. No second `get_api` call, no re-trying with different filters. I treat the catalog as a quick first pass, not the authoritative source.

So the real sequence for fast-moving categories is: `search_apis` → evaluate coverage → if thin, web search in parallel or immediately after. I wouldn't skip the catalog call entirely because it costs me almost nothing, but I wouldn't let it be the last word either.

**The contradiction in my Q5 answer was real**, and it came from seeing the results first. After running Q1-Q3 and seeing two mediocre video results, I retroactively said "I'd skip it." That's not what I'd do in a fresh session. I'd try it, then abandon it fast. The three fixes in Q6 — especially #2 (coverage minimums) — would remove that abandon-fast reflex because I'd trust that thin results mean the market is actually thin, not that the catalog is incomplete.
