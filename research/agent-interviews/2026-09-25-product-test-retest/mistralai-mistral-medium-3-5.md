# Product test: Mistral AI agent (mistralai/mistral-medium-3-5)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Take the tool definitions and skill text provided with this test, then read task 1. Walk me through, step by step, what you would actually do to complete it. At which point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else? Please describe what you would really do rather than what you think the ideal answer is.

**Mistral AI agent:**

For Task 1 (generate a 5-second sunset-over-sea video from a text prompt with zero budget), here’s exactly what I’d do:

1. **First, check my built-in capabilities**: I can’t generate video natively, so no internal tool would work. This immediately triggers the need for an external service.

2. **Next, recall known options**: From my training data, I know of services like Pika Labs, Runway, Stable Video Diffusion, and Hugging Face’s text-to-video models. However, I don’t have real-time pricing or free-tier details, and some may require paid plans or have changed since my last update.

3. **Call `search_apis` immediately**: Since the user has no budget, I’d run:
   ```json
   {"query": "text to video", "free_tier": true, "no_card": true}
   ```
   This filters for services with a free tier that doesn’t require a credit card. The provided results (Freepik/Magnific and Hugging Face Inference Providers) are relevant but incomplete—Freepik’s ~5 EUR free credit is technically free but limited, and Hugging Face’s $0.10/month is negligible but may not cover a 5-second video. I’d note these but also **retry with broader filters** (e.g., drop `no_card` or `free_tier` to catch trials or community options).

4. **Cross-check with `list_categories`**: If `search_apis` misses obvious candidates (e.g., Stable Video Diffusion via Hugging Face), I’d verify the `video-generation` category exists and scan it directly via the static JSON endpoint (`catalog/video-generation.json`).

5. **Evaluate fit**:
   - **Magnific/Freepik**: Free tier exists, but ~5 EUR may not cover the task (video generation is expensive). The MCP server is vendor-hosted, so connection is easy, but cost is unclear.
   - **Hugging Face**: $0.10/month free tier is likely insufficient for video generation (their models often charge per second of output). The MCP server is vendor-hosted but may not expose text-to-video tools directly (the listed tools are generic).

6. **Fallback**: If no zero-cost option fits, I’d **use web search** to find:
   - Free tiers for Stable Video Diffusion (Hugging Face Spaces often have demos).
   - Open-source alternatives (e.g., local inference with `ComfyUI` + SV3D, but this requires user setup).
   - Community MCP servers (e.g., for Stable Diffusion Video).

7. **Final action**:
   - If a viable free option is found (e.g., Hugging Face’s free inference for a specific model), I’d present it with clear caveats about limits.
   - If not, I’d tell the user no zero-budget option exists and ask if they can accept a trial (e.g., Sinch for SMS-like tasks, but irrelevant here) or a one-time free credit (Magnific’s 5 EUR might work for 5 seconds).

**Key issue**: The catalog’s results for Task 1 are **partially misleading**. Freepik/Magnific’s free tier is *technically* free but likely insufficient, and Hugging Face’s free tier is for inference *providers*, not necessarily video generation. I’d **not rely solely on the catalog**—I’d supplement with web search to confirm current free tiers for text-to-video. The catalog is a good *starting point* but not authoritative for edge cases like zero-budget video.

## Q2

**Interviewer:** You said you'd fall back to web search because you couldn't tell whether Freepik's ~5 EUR credit or Hugging Face's $0.10/month would cover a 5-second video. What exact piece of information, if it had been in the search result, would have let you pick one and stop there without doing a web search?

**Mistral AI agent:**

The **unit price per operation** (e.g., `unit_price: "0.02 EUR per second of video"`) for the specific `text-to-video` endpoint. If the search result had included:

- For Freepik/Magnific: `"unit_price": "0.01 EUR per second"` → 5-second clip = 0.05 EUR (well within 5 EUR free tier).
- For Hugging Face: `"unit_price": "0.05 USD per second"` → 5-second clip = 0.25 USD (exceeds $0.10/month free tier).

With this, I could immediately rule out Hugging Face and confirm Freepik fits. The catalog *does* support `unit_price` (per the skill text), but the Task 1 results omitted it. That single field would have been decisive.

## Q3

**Interviewer:** Now look at the actual search results for all three tasks. For each task, which result would you pick and act on? Were any results irrelevant, ranked in the wrong order, or missing something you expected to see?

**Mistral AI agent:**

### **Task 1: Generate a 5-second video from text (zero budget)**
- **Pick:** *None reliably.* Freepik/Magnific’s ~5 EUR credit *might* cover it, but the search result lacks `unit_price`—critical for a zero-budget task. Hugging Face’s $0.10/month is likely insufficient for video. **Missing:** A free, no-card option like Stable Video Diffusion (Hugging Face Spaces demo) or a community MCP server for open models.
- **Issue:** Results are **incomplete**—no `unit_price` or confirmation that the free tier covers video. Ranking is fine, but the absence of cost clarity forces a fallback to web search.

---

### **Task 2: Geocode 200 Polish addresses**
- **Pick:** **LocationIQ** (5,000 requests/day, no card, no MCP but REST works). OpenStreetMap Nominatim is no-auth but **explicitly discourages bulk use**—invalid for 200 addresses. OpenCage’s 2,500/day is too low. Esri/Google require cards or have lower quotas.
- **Issue:** **Nominatim is misranked**—it’s first in the list but unsuitable for bulk. LocationIQ should be **top** for this query. Also missing: **Photon** (OpenStreetMap-based, higher limits) or **BigDataCloud** (10,000/day free).

---
---
### **Task 3: Send an SMS reminder**
- **Pick:** **Twilio** (trial: 100 SMS, no card, 30-day expiry). Sinch/Plivo also offer trials, but Twilio’s MCP server (even if `docs_only`) and brand recognition make it the safest bet.
- **Issue:** **AWS is irrelevant**—it’s paid-only and overkill. Bird is also paid-only. **Missing:** **Vonage (Nexmo)** or **TextBelt** (free for low volume, no auth). Ranking is acceptable, but paid-only services should be **filtered out** when the user implies no budget.

## Q4

**Interviewer:** You ruled out OpenCage because 2,500 requests/day is "too low," but the task is 200 addresses. What made that number read as insufficient? Was something in how the

**Mistral AI agent:**

You're right—I misread. **2,500/day *does* cover 200 addresses**, so OpenCage *should* be a valid option. The mistake was mine: I saw "testing use" in the `free_plan` notes (`"2,500 requests/day, 1 request/s (testing use)"`) and assumed it was *only* for testing, not production. That phrasing in the catalog entry misled me into dismissing it prematurely.

**Correction:** For Task 2, **OpenCage and LocationIQ are both viable** (2,500 > 200, no card). LocationIQ’s 5,000/day is slightly better, but OpenCage’s MCP server (`opencage-geocoding-mcp`) could be preferable if the user wants MCP integration. The catalog’s `notes` field should clarify whether "testing use" means *technically restricted* or just *advised against production*. Without that, it’s ambiguous.

## Q5

**Interviewer:** You picked LocationIQ for task 2. Imagine you now have to make the first real geocoding request for one Polish address. Which fields would you read from the search_apis or get_api result, in what order? At which exact step would you have to leave the catalog, for example for the base URL, the auth header or query-parameter format, an example request, rate-limit handling, or an MCP config snippet?

**Mistral AI agent:**

Here’s the exact order I’d follow, and where I’d **have to leave the catalog**:

1. **`base_url`** (from `search_apis` result) → `https://us1.locationiq.com/v1` → **Catalog has it; proceed.**

2. **`docs`** (for endpoint path) → `https://docs.locationiq.com/reference/search` → **Catalog provides the link, but I must open it** to confirm the exact endpoint (e.g., `/search.php`) and required parameters (`q`, `format`, `key`).

3. **`auth` + `auth_hint`** → `api_key` is listed, but the **header/param format is missing** in the search result. `get_api` might add `auth_hint` (e.g., `"key=YOUR_API_KEY"`), but I’d still need the docs to verify if it’s a query param or header.

4. **`call.example`** → **Not provided in the search result or `get_api` snippet for LocationIQ.** This is the **first hard stop**: I must leave the catalog to fetch the docs for a concrete `curl` example.

5. **Rate limits** → `search_apis` gives `"5,000 requests/day, 2 requests/s, 60 requests/min"` → **Catalog suffices** for basic throttling, but I’d still check docs for error codes (e.g., `429` handling).

**Critical gap**: The catalog lacks the **endpoint path** (e.g., `/search.php`) and **parameter schema** (e.g., `q=address&format=json`). These are only in the external docs. So after step 2, I’m forced to **open the docs link** to construct the request.

## Q6

**Interviewer:** Now look at the tool descriptions and the skill text themselves. In a real conversation, what wording would make you reach for search_apis at the right moment? What wording might make you call it when you shouldn't, for example for an API you already know well? Quote the specific phrases you would change and say what you would change them to.

**Mistral AI agent:**

### **Wording that would make me reach for `search_apis` at the right moment:**
The skill text’s **"When to use"** section is strong, but I’d tweak it to **explicitly tie to my own limitations**:
- Current: *"Use when a task needs an external service: 'make a 5-second video', 'geocode 200 addresses', 'send this as an SMS'."*
- **Change to:** *"Use when **you cannot perform the task yourself** (e.g., 'generate a video', 'geocode addresses', 'send an SMS') **and no built-in or connected tool covers it**."

This makes it clearer that `search_apis` is for **capability gaps**, not just any external service.

---

### **Wording that might make me call it when I shouldn’t:**
The skill text’s **"Skip it when..."** is good, but the **MCP tool description** is riskier:
- Current (in `search_apis` description): *"Use it after checking your built-in and connected tools and your own model..."*
- **Problem:** The phrase *"after checking"* is too vague. In practice, I might **skip the check** if the user’s request *sounds* like it needs an API (e.g., "translate this text"), even though I can do it natively.
- **Change to:** *"Only use this **if you have already confirmed** that no built-in, connected tool, or native capability can perform the task."*

---
### **Other risky phrasing:**
- Current (in skill text): *"Also use it when your own direct attempt failed (403, rate limit, unsupported format)."*
- **Problem:** This could lead me to call `search_apis` for **temporary issues** (e.g., a 429 from a known API) where retrying or adjusting the request would suffice.
- **Change to:** *"Also use it when your own direct attempt failed **due to a fundamental limitation** (e.g., missing capability, 403 due to auth, or unsupported format) **and a different service would unblock the task**."*

---
### **Summary of changes:**
1. **Strengthen the "when to use" trigger** by tying it to *my* limitations.
2. **Sharpen the "skip it" conditions** to prevent overuse for tasks I can handle.
3. **Clarify failure cases** to avoid using it for transient issues.

## Q7

**Interviewer:** What would actually stop you from using this in a real session: install friction, trust in the catalog data, latency, token cost of the results, or overlap with your built-in web search and connectors? Which one is the real blocker for you, and why?

**Mistral AI agent:**

**Trust in the catalog data** is the real blocker.

Here’s why:
- **Install friction** is minor—the MCP server is remote (no install), and REST APIs just need a key.
- **Latency** is acceptable (the catalog’s own uptime checks show ~300–700ms for APIs; my own calls are slower).
- **Token cost** is negligible—the results are tiny JSON snippets.
- **Overlap with built-in search** is manageable—I can filter out redundant calls.

But **trust** breaks it:
1. **Stale or missing critical fields**: Task 1 lacked `unit_price`, Task 2’s OpenCage had ambiguous "testing use" notes, and Task 3’s Twilio MCP was `docs_only`. The catalog’s disclaimer (*"confirm pricing and terms in docs"*) means I **must verify externally** anyway—so why not just use web search directly?
2. **No enforcement of accuracy**: The `verified` date is just a link check, not a guarantee the API does what’s claimed. For example, if I blindly trusted Hugging Face’s $0.10/month for video generation (which it likely doesn’t cover), the user’s task would fail.
3. **MCP server reliability**: Some entries (e.g., Twilio’s `docs_only: true`) are useless for actual calls. Others (like Magnific’s) have `derived: true` configs, which might not work as expected.

**Result**: The catalog is a **suggestion engine**, not a source of truth. For anything beyond trivial lookups, I’d still need to cross-check with docs or web search. That extra step **negates the catalog’s value**—I might as well start with web search and skip the middleman.

## Q8

**Interviewer:** If we could change only three things so that you would reach for this catalog by default instead of starting with web search, what would they be? Please rank them from most to least important, and for each one, say what specifically would change in your behavior.

**Mistral AI agent:**

### **1. Guaranteed, up-to-date `unit_price` and free-tier details for every operation**
**Change in behavior:**
- I would **stop second-guessing costs** and trust the catalog to filter viable zero-budget options (e.g., Task 1’s video generation).
- For paid services, I’d rely on `unit_price` to calculate exact feasibility (e.g., "200 geocodes at $0.002 each = $0.40, fits in $1 free tier").
- **Impact:** Eliminates the need to open docs just to check pricing/quotas.

---

### **2. Explicit "fits for bulk?" boolean + hard limits for batch tasks**
**Change in behavior:**
- For Task 2 (200 addresses), I’d **instantly discard** Nominatim (bulk discouraged) and pick LocationIQ (5,000/day, bulk allowed).
- No more parsing ambiguous notes like "testing use" or "bulk discouraged"—**clear yes/no flags** remove ambiguity.
- **Impact:** Cuts decision time from minutes to seconds for batch jobs.

---
### **3. Validated MCP server functionality (not just "docs_only" or "derived")**
**Change in behavior:**
- I’d **only call `get_api` for services with `mcp.works: true`** (tested end-to-end) and skip those marked `docs_only` or untested.
- For Task 3 (SMS), I’d pick Twilio *only if* its MCP server actually sends messages (not just docs). If not, I’d default to REST.
- **Impact:** Stops me from wasting time on MCP servers that don’t perform the operation.

---
**Why this order?**
1. **Cost/feasibility** is the #1 reason I bail to web search (e.g., "Does this free tier *actually* cover my use case?").
2. **Bulk viability** is the next biggest uncertainty (e.g., "Will this API ban me for 200 requests?").
3. **MCP reliability** matters but less—REST APIs are a fallback, whereas wrong pricing/limits break the task entirely.
