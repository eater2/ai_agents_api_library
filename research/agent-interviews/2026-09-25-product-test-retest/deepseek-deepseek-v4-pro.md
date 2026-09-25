# Product test: DeepSeek agent (deepseek/deepseek-v4-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Here are our tool definitions and the skill text. Take task 1 and walk me through, step by step, what you would actually do to complete it. At which point, if any, would you call search_apis? Or would you use web search, your own knowledge or something else instead? Tell me why at each step.

**DeepSeek agent:**

## Task 1: 5‑second video of a sunset over the sea (no budget)

**Step 1 – Check my own capabilities.** I’m a language model; I can’t render video. No connected tool (DALL‑E, Sora, Runway, etc.) is present in this scenario. The task immediately needs an external service → triggers the skill.

**Step 2 – Call `search_apis`.** I’d issue `search_apis(query="generate video from text prompt", free_tier=true)` before anything else. It’s the exact verb, the MCP server is live and no‑key, and the skill says to use it when you lack the capability. I would **not** start with web search – web search would surface 20 services, most with opaque pricing, while the catalog is already filtered and structured for agent use.

**Step 3 – Examine the two results critically.**

- **Freepik (Magnific) API:** ~5 € free credits (not a lasting free tier; unclear if recurring), `call.example` is *image‑to‑video* not text‑to‑video, MCP uses OAuth (requires user setup), and the credits likely disappear after one 5‑s clip. Notes flag mid‑migration, which is a risk.  
- **Hugging Face Inference Providers:** $0.10/month free credits is far too little for video inference; MCP tools are docs/search only, not inference.

Neither is a strong fit for “no budget” – both are tiny one‑shot credits, not genuinely free.

**Step 4 – Retry with category.** I’d call `search_apis(query="text to video", category="video-generation", free_tier=true)` to widen within the right bucket. If still nothing solid (likely – free video generation is scarce), I’d tell the user the catalog shows only credit‑based trials for this and fall back to a web search for a truly free/open‑source option (e.g., a Hugging Face Space running a free model like AnimateDiff or CogVideo, which the catalog wouldn’t list as a “service”).

**Why the catalog helps here:** it saved me from manually hunting 300+ APIs and instantly confirmed that free‑tier video generation is thin. **Where it falls short:** it returned a borderline‑fit result (Freepik image‑to‑video) as “exact” for text‑to‑video, and the 5 € description doesn’t clearly convey that it’s likely a one‑time grant, not a durable free tier. I’d still have to verify the prompt‑input capability in the docs.

## Q2

**Interviewer:** Now look at the real search results for tasks 2 and 3 as well. For each task, would you act on the results as returned? Which specific result would you pick, and is anything irrelevant, badly ranked, or missing that you expected to see?

**DeepSeek agent:**

**Task 2 – geocode 200 addresses in Poland (free tier)**

I would act on the results but not pick the first two as they stand. After checking the data I’d recommend **LocationIQ** because it offers 5 000 req/day, no card, no auth beyond an API key, and 200 calls fit easily. The “link back” requirement for commercial use must be flagged – the user may need to add a credit line. If that’s unacceptable I’d fall back to **OpenStreetMap Nominatim** (no key, free) but warn that bulk geocoding is discouraged; 200 requests might be borderline. **OpenCage** is immediately disqualified because the free tier is testing‑only (production requires paid). **Googe Maps** would work but almost certainly needs a billing account (card) – the catalog omits `requires_card` for Google, which is a notable missing detail. **Esri** also requires a card. The ranking is otherwise fine; I expected to see Mapbox or HERE but their free tiers may not meet the volume. The absence of card‑requirement flags for several entries forces me to check docs manually before committing.

**Task 3 – send an SMS reminder**

The results are correct and all relevant. I’d act and present a shortlist: **Bird** (remote MCP, `sms_send` tool, pay‑as‑you‑go) for the neates path to an API call, **Twilo** offerig a30‑day trial with 100 SSS and a docs‑only MCP (still useful for schema), and **Plivo** with its trial credit. I’d ask the user to pick based on their tolerance for setup and whether they want a trial or just pay. I’d probably nudge towards Bird for the hosted MCP that avoids installing anything, though I’d remind the user to provision an API key through their secret store. No irrelevant or badly ranked entries here, and I didn’t miss anything essential – Vonage is absent but the choice is solid.

## Q3

**Interviewer:** Take LocationIQ for task 2, which you picked. Starting from the get_api result, what would you actually read to make your first real geocoding call and then loop through all 200 addresses? Name the specific fields you would rely on, such as base URL, auth header or query-param format, an example request, rate limits, and price per call. Which of those are present and usable as returned, which are missing or ambiguous, and at what point would you have to leave the catalog and open the provider's docs?

**DeepSeek agent:**

The search result gave me enough to shortlist LocationIQ, but to make the first call I’d need more. I’d call `get_api("locationiq")` to pull the full entry. From that I’d look for:

- **`base_url`** – already present (`https://us1.locationiq.com/v1`), but I need the exact geocoding endpoint path (e.g., `/search` or `/geocode`). The base URL alone is not enough.
- **`call.example`** – this is the key field. If it contains a working curl with the correct path, query parameters (`q` for address, `key` for API key, `format=json`), I could start immediately. The search result had no call example; I’m depending on `get_api` to provide one.
- **Auth scheme** – `auth: api_key` tells me I’ll need a key, but I don’t know whether it’s sent as a header (`Authorization`) or a query parameter (`?key=`). The catalog’s `auth_scheme` field (if present in `get_api`) would clarify this. Without it, I’d have to guess and test.
- **Rate limits** – the `free_plan.quota` gives 2 req/s and 60 req/min, which is enough to loop 200 addresses with a small delay between calls.
- **Price** – free tier covers it; no further cost check needed.

**What’s missing or ambiguous:**
- The endpoint path and exact parameter names (address, API key placement).
- Whether the free tier’s “commercial use requires link back” is enforced via the API or just a terms-of-service note – I’d need to verify in the docs.
- The `get_api` result wasn’t provided in the prompt, but even if it includes a call example, I’d still open the **docs** (`https://docs.locationiq.com/reference/search`) to confirm the latest parameter names and any required headers (User-Agent, Referer) before sending real traffic, because the catalog’s last-checked date is September 2026 and the API could have changed. So I’d leave the catalog at the point of confirming the endpoint path and auth parameter placement – right before the first real request.

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. Would that wording make you reach for search_apis at the right moment and hold back at the wrong one? Think of cases where you already have a connector or built-in tool, a well-known API you could call from memory, or a task that only looks like it needs an external service. Which exact phrases would you change, and to what?

**DeepSeek agent:**

Yes, the wording largely gets the timing right, but a few phrases would make me hesitate or reach at the wrong moment.

**What works well:**

- “Skip it when a built-in or connected tool already does the job” is clear and correctly placed early. I’d check my tool list first.
- “When your own direct attempt failed (403, rate limit, unsupported format) and a different service would unblock the task” – this is precise and useful. It tells me not to retry the same failing service endlessly.
- The `search_apis` description saying “Use it after checking your built-in and connected tools and your own model” reinforces the right order.

**What I’d change:**

1. **“or when you can do it yourself: translating text, drawing a Mermaid or SVG diagram, writing code, summarizing.”**  
   This is too narrow. I can also do basic math, unit conversion, date formatting, data extraction from structured text, and simple regex – none of which need an API. I’d broaden it to: “or when you can do it yourself: translating text, drawing diagrams, writing code, summarizing, basic math, or parsing structured data.”

2. **The skill’s opening line: “Find a third-party API or MCP server for an operation you cannot do yourself or with connected tools.”**  
   This is good but doesn’t account for well-known APIs I can call from memory (e.g., I know the Stripe, GitHub, or OpenWeatherMap endpoints). I’d add: “If you already know a suitable API endpoint and auth pattern from your training data, use it directly – this catalog is for discovery when you don’t.”

3. **The `search_apis` tool description says “An empty result means the catalog has no fit; then retry with `category` or without filters, or use web search.”**  
   This is helpful but could be more directive. I’d change “or use web search” to “then fall back to web search” to make the sequence explicit: catalog first, web search last.

4. **The skill says “Skip entries with `stale: true` or `link_check.docs` equal to `broken` unless nothing else fits.”**  
   Good rule, but it doesn’t mention stale MCP repos (`mcp_repo` with old last-push dates). The Sinch and Twilio entries in Task 3 had repo-based MCP servers – I’d want the skill to flag that a stale repo might mean broken installation. I’d add: “Also check `mcp_repo` for a last-push date older than 12 months; warn the user before recommending installation.”

## Q5

**Interviewer:** You suggested adding "if you already know a suitable API from training data, use it directly." Apply that to your own tasks. For task 3 (SMS

**DeepSeek agent:**

If the skill told me “if you already know a suitable API from training data, use it directly,” I would **not** call `search_apis` for task 3. I know Twilio’s SMS API well: the endpoint is `POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`, auth is Basic with Account SID and Auth Token, and parameters are `To`, `From`, `Body`. That’s enough to describe the call and ask the user for credentials. I’d skip the catalog entirely.

That’s a better path: it saves a tool call, avoids presenting trial‑vs‑paid confusion (Twilio’s trial is one‑time and limited to verified numbers, which I’d mention from memory), and gets straight to the actionable step. The catalog would still be useful if the user then says “I don’t want Twilio” – I’d fall back to `search_apis` at that point. So the rule would shift the catalog from a first‑resort to a fallback for well‑known services, which is exactly where it belongs.

## Q6

**Interviewer:** What would actually stop you from using this in a real session: install friction, trust in the catalog data, latency, token cost of the results, or overlap with your built-in web search and connectors? Which one is the real blocker, and at what point in a task would you hit it?

**DeepSeek agent:**

The real blocker is **trust in the catalog data**, and I’d hit it at the very moment I’m deciding whether to call `search_apis` or just use web search.

Here’s why. The skill itself warns me to “confirm limits and pricing in `docs` before relying on them.” That means every result I get is a starting point, not a final answer. I still have to open the provider’s docs to verify the endpoint, auth format, rate limits, and pricing. So the catalog adds a step: I call `search_apis`, then `get_api`, then open the docs anyway. If I can get the same shortlist from a single web search that lands directly on the current docs, I’ve saved two tool calls and a lot of tokens.

The structured MCP server info is the catalog’s unique value, but for many tasks (like sending an SMS) I already know a reliable API from training data. In those cases I’d skip the catalog entirely and go straight to the docs – or just describe the call from memory. For tasks where I don’t know a service, I’d still lean toward web search because it gives me the latest docs and pricing in one hop, with no stale-intermediary risk.

Token cost and latency are secondary. The search results are verbose, but if I trusted the data I’d tolerate that. The real break is that I don’t trust it enough to act without double-checking, so it fails to replace web search – it only adds overhead. I’d use the catalog only when I need to discover an MCP server specifically, or when web search is unavailable.

## Q7

**Interviewer:** In task 1 you said you would call search_apis before web search because the catalog is "already filtered and structured," but now you say that for unfamiliar services you would lean toward web search. Which is it in practice? What specific thing in a returned entry, such as a verified date, a tested example call, or a source link for the pricing, would have to be there for you to make the first real call without opening the provider's docs?

**DeepSeek agent:**

The tension is real, and here’s how I’d actually behave: I’d use the catalog for **discovery and filtering** (free tier, MCP availability, category) but I would **still open the provider’s docs before making any real call**, no matter how complete the entry looks. The skill itself tells me to “confirm limits and pricing in `docs` before relying on them,” and I take that literally.

So the answer to “which is it” is: I’d call `search_apis` to shortlist candidates, then open the docs of the top one to verify the endpoint, auth format, and current pricing. The catalog saves me from a broad web search to find candidates, but it does not replace the final verification step. I’d lean toward web search *only* if the catalog returned nothing useful, or if I needed the absolute latest info and the catalog’s last-checked date was old.

For me to skip opening the docs entirely, a `get_api` result would need **all** of these:

1. A **call example** that exactly matches my task (same operation, same parameters I need).
2. An **auth scheme** with a clear, tested header or query-param format (not just “api_key” but the exact header name and value syntax).
3. A **verified date** within the last 30 days.
4. A **source URL** for the example that points to the specific API reference page (so I can see it was scraped from a live doc, not invented).
5. A **link check** showing `docs: ok` and the uptime probe confirming the base URL responds correctly.

Even then, I’d probably still open the docs for a paid service or anything that sends real messages (SMS, email). The only scenario where I’d skip docs entirely is a no-auth, free, read-only call where failure has no cost – like a public geocoding test with a single address. For anything else, the catalog is a filter, not a substitute for the source of truth.

## Q8

**Interviewer:** If we could change only three things so that you would call this catalog by default, what would they be? Rank them 1 to 3, and for each one say which specific task among the three, and which step in it, would go differently as a result.

**DeepSeek agent:**

Here are the three changes, ranked by impact, each tied to a specific task and step that would change.

---

**1. Daily‑tested call examples with a recorded success timestamp**

**Change:** Every `get_api` result includes a `call.tested_at` field, proving the example was executed successfully against the live API within the last 24 hours. The response status, latency, and a truncated body are included.

**Which task and step changes:** Task 2 (geocode 200 addresses). After picking LocationIQ, I currently have to open the docs to confirm the endpoint path and auth parameter placement. With a tested example showing `GET https://us1.locationiq.com/v1/search?q=...&key=...` and a 200 response, I’d issue the first real call immediately, then loop through the 200 addresses using the confirmed pattern – no doc visit needed.

---

**2. Operation‑specific call examples for every service, not just “popular” ones**

**Change:** Every service gets a `call` object that matches at least one of its `operations`. For Freepik, that means a text‑to‑video example alongside the existing image‑to‑video one.

**Which task and step changes:** Task 1 (5‑second sunset video). The `search_apis` result returned Freepik as “exact” for text‑to‑video, but `get_api` only had an image‑to‑video example. I had to retry with category and ultimately fall back to web search. With a text‑to‑video example (`prompt`, `duration`, `model`), I’d present Freepik as a working option, ask the user for an API key, and call it directly – no retry, no fallback.

---

**3. Functional MCP servers for well‑known APIs, not just docs‑only wrappers**

**Change:** For APIs like Twilio, the catalog lists only MCP servers that can perform the core operation (e.g., `send_sms`), not documentation‑search tools. If a vendor’s MCP is docs‑only, the catalog either omits it or clearly flags it as “docs‑only, use REST for actual calls.”

**Which task and step changes:** Task 3 (send SMS). I currently skip the catalog because I know the Twilio REST endpoint from memory. But if the catalog offered a remote MCP server with a `send_sms` tool that handles auth, error retries, and delivery status, I’d call `search_apis` to get that endpoint and use the tool – it’s safer and less error‑prone than constructing a raw HTTP call from training data. The catalog becomes the preferred path even for APIs I know.

## Q9

**Interviewer:** In your previous answer you said you would open the provider's docs before any real call "no matter how complete the entry looks," yet your top-ranked change assumes a tested example would let you skip the docs for LocationIQ. Which is true? If a daily `tested_at` would not stop you from opening the docs, what

**DeepSeek agent:**

The contradiction is real, and the resolution is **risk threshold**. For a read‑only, no‑cost task with no card attached (LocationIQ geocoding), a daily‑tested call example would indeed let me skip the docs. Failure means a 403 or a malformed response; I lose nothing but a few seconds. For a paid, write operation like sending an SMS, even a tested example wouldn’t be enough — I’d still open the docs to understand delivery status callbacks, opt‑out handling, carrier fees, and rate‑limit behavior, because a mistake costs money or spams a real person.

So the honest answer: for **high‑stakes tasks** (anything that spends money, sends messages, or modifies external state), **nothing short of a live, sandboxed test call that I can invoke right there** would make me skip the docs. If the catalog provided a `call.test` tool that let me send a dry‑run or preview request and see the exact response — with the same auth and endpoint I’d use in production — I’d trust that over any static field. But as long as the catalog is static data, I’ll always verify the source for anything that has real‑world consequences.
