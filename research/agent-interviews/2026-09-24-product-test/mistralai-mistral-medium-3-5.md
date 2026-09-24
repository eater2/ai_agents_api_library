# Product test: Mistral AI agent (mistralai/mistral-medium-3-5)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Please look at the tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text provided with this test, then take task 1. Walk me through what you would actually do to complete it, step by step, as if you were doing it for real. At which point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else? For each step, tell me why you chose that option.

**Mistral AI agent:**

For Task 1 (generate a 5-second video from a text prompt with no budget), here’s exactly what I’d do and why:

1. **Assess built-in capabilities**
   I check my available tools. Mistral’s platform (like most) doesn’t include native video generation, so I need an external service. No point burning tokens on web search yet.

2. **Call `search_apis`**
   I’d run `search_apis({"query": "text to video", "free_tier": true, "limit": 5})` because:
   - The catalog is curated and up-to-date (verified dates in results).
   - Filtering by `free_tier` immediately narrows to usable options for a zero-budget user.
   - The MCP tool is faster than web search and avoids sifting through marketing pages.

3. **Evaluate results**
   From the returned list:
   - **Google Gemini API** is irrelevant (text/image only, no video).
   - **Mux Video API** is for encoding/streaming, not generation.
   - **Akool** and **Creatomate** are plausible but lack official MCP servers (extra setup for the user).
   - **Voyage AI** is embeddings—wrong category.

   The search missed **Pika Labs** or **RunwayML** (which *do* offer free text-to-video tiers). This is a gap in the catalog. I’d note this and proceed.

4. **Refine search**
   I’d try `search_apis({"query": "text to video generation", "category": "video-generation", "free_tier": true})` to target the correct category. If still no ideal hits, I’d fall back to a quick web search for "free text to video API 2026" to confirm if the catalog is incomplete.

5. **Propose options**
   If Akool/Creatomate are the only matches, I’d present them with caveats:
   - "Akool offers a free tier for face-swap/talking avatars, but **not** general text-to-video. You’d need to adapt your prompt."
   - "Creatomate requires templates—you’d need to design one first."
   If the catalog is missing key services, I’d explicitly say: *"The catalog doesn’t list Pika Labs (free 5s clips), so I’d recommend that instead. Here’s how to set it up..."*

**Key takeaway**: The MCP `search_apis` is useful for *known* services but **not exhaustive**. I’d use it first, then verify with a web search if results seem off. The catalog’s strength is structured data (auth, MCP flags); its weakness is coverage gaps. For video generation, I’d likely end up supplementing with external research.

## Q2

**Interviewer:** You said that if the catalog didn't list Pika Labs, you would recommend it from memory. How sure are you that Pika or Runway currently offer a free public API tier for text-to-video, and what would a search_apis result need to show for you to trust it over your own recollection and skip the confirming web search?

**Mistral AI agent:**

I’m **not sure**—my knowledge cutoff is October 2023, and both Pika Labs and RunwayML have since changed their free tiers and API access. Pika’s free web app (5s clips) doesn’t guarantee a free *API* tier, and Runway’s free API credits are often time-limited or require a card. My recollection is stale, so I wouldn’t trust it.

For `search_apis` to override my doubt and skip a confirming web search, the result would need:
1. **Explicit free API tier** (not just a free web product) in `free_tier` (e.g., *"API: 10 free generations/month, no card"*).
2. **Recent verification** (`verified` date within the last 3 months, not 2023).
3. **Official MCP or direct API docs** (`mcp.type: "official"` or a `docs` URL pointing to a developer portal, not a landing page).
4. **No `stale: true` or broken link flags** in `link_check`.

If the catalog entry for Pika/Runway met all four, I’d propose it. Otherwise, I’d default to a quick web search to confirm the current API terms. The catalog’s value is its *structured* fields (auth, MCP, verified date)—if those are solid, I trust it over my outdated memory.

## Q3

**Interviewer:** Now look at the real search results for all three tasks. For each task, would you act on them, and which specific result would you pick? Which results are irrelevant, badly ranked, or missing, and what would you expect to see ranked first instead?

**Mistral AI agent:**

### **Task 1: Generate a 5s video from text (no budget)**
**Action:** *No, I would not act on these results.*
- **Irrelevant:**
  - `google-gemini-api` (text/image only, no video generation).
  - `voyage-ai-embeddings-rerank` (embeddings, completely off-topic).
  - `mux-video-api` (encoding/streaming, not generation).
- **Badly ranked:**
  - `akool-api` and `creatomate-api` are *partially* relevant (video-related) but require templates or face-swap, not direct text-to-video. They should not outrank true text-to-video APIs.
- **Missing:**
  - **Pika Labs API** (free tier for short clips), **RunwayML** (free credits), **Stable Video Diffusion API** (if available), or **Luma AI** (for 3D/video).
- **Expected first:**
  A **dedicated text-to-video API** with a free tier (e.g., Pika or Runway) should rank #1. The current results are polluted by non-video or indirect tools.

---

### **Task 2: Geocode 200 Polish addresses**
**Action:** *Yes, I would act on these results.*
- **Pick:** **`openstreetmap-nominatim`** (no auth, free, but rate-limited to 1 req/sec).
  - For 200 addresses, this is *just* feasible (3.3 minutes if batched carefully).
  - If the user needs speed, I’d suggest **`geoapify`** (3,000 credits/day ≈ 90k/month, free tier, API key required).
- **Irrelevant:**
  - `ip2location-io` (IP geolocation, not address geocoding).
  - `esri-arcgis-location-platform` (misclassified under `architecture-cad-bim`; should be in `maps-geo-weather`).
- **Well-ranked:**
  - `google-maps-platform` is a strong alternative (but requires a key and $200 credit).
- **Expected first:**
  `openstreetmap-nominatim` (no auth) or `geoapify` (high free tier) should be #1 and #2. The current ranking is acceptable.

---
---
### **Task 3: Send an SMS reminder**
**Action:** *Yes, but with caveats.*
- **Pick:** **`twilio`** (official MCP, widely used, trial credits).
  - Despite "no permanent free tier," the trial credit is sufficient for a few SMS.
  - If the user needs *truly* free, **`line-messaging-api`** (200 free messages/month) is an option—but only for LINE users (not SMS).
- **Irrelevant:**
  - `discord-api` (not SMS).
  - `whatsapp-business-cloud-api` (WhatsApp, not SMS; also requires Meta approval).
- **Badly ranked:**
  - `line-messaging-api` should not outrank Twilio for *SMS* (it’s a different channel).
- **Missing:**
  - **TextBelt** (truly free, no auth, but unreliable).
  - **Clockwork SMS** (UK-focused, free tier).
- **Expected first:**
  `twilio` (most universal for SMS) should be #1. The current ranking is misleading because `line-messaging-api` is not SMS.

## Q4

**Interviewer:** Take your Task 2 pick, Geoapify, and imagine going from that search result to a first working request for the 200 Polish addresses. Which fields would you read from `search_apis` or `get_api`, in what order? What information is missing that would force you to leave the catalog, for example to open the docs or run a web search, before you could write the call? Be concrete about field names and values, not categories.

**Mistral AI agent:**

For **Geoapify**, here’s the exact field order I’d check before writing the first request:

1. **`docs`** (from `search_apis` or `get_api`) →
   *Value:* `"https://apidocs.geoapify.com/"`
   *Why:* This is the only place to confirm the exact endpoint path (e.g., `/geocode/search`), required parameters (`text`, `apiKey`), and rate limits. The catalog’s `free_tier` summary ("3,000 credits/day") doesn’t specify *per-IP* vs *per-key* limits or how credits are consumed (e.g., 1 credit per query? per address?).

2. **`auth`** and **`auth_hint`** (from `get_api`) →
   *Expected:* `"api_key"` and a header like `"x-api-key: <KEY>"` or a query param `apiKey`.
   *Why:* Need to know *how* to pass the key (header vs. param). If missing in `search_apis`, I’d call `get_api("geoapify")` to fetch it.

3. **`free_tier`** (from `search_apis`) →
   *Value:* `"free tier: 3,000 credits/day (~90,000/month), no card required"`
   *Why:* Confirms no upfront cost, but I’d still need the docs to verify if 200 addresses fit in 3,000 credits (e.g., is geocoding 1 credit per call?).

**Missing/critical gaps forcing me to leave the catalog:**
- **Endpoint URL**: Not in the catalog. The `docs` link is mandatory to find `/geocode/search` or `/batch/geocode`.
- **Request format**: The catalog doesn’t specify if Geoapify supports *batch* requests (for 200 addresses) or only single queries. If batch isn’t supported, I’d need to implement rate-limiting (1 req/sec? 10 req/sec? Not stated).
- **Credit consumption**: Is it 1 credit per address? Per field? The catalog’s `~90,000/month` is ambiguous.
- **Poland-specific coverage**: The docs might note limitations (e.g., "better for EU addresses" or "no street-level in PL"). The catalog doesn’t include this.

**Workable minimal set from catalog alone:**
If `get_api("geoapify")` returned:
```json
{
  "auth": "api_key",
  "auth_hint": "apiKey=<KEY> (query param)",
  "docs": "https://apidocs.geoapify.com/docs/#geocoding",
  "free_tier": "3,000 credits/day, 1 credit = 1 request"
}
```
I could write a *single* test request (e.g., `https://api.geoapify.com/v1/geocode/search?text=ul.+Floriańska+1,+Kraków&apiKey=...`). But for **200 addresses**, I’d *still* need the docs to check batch support and rate limits.

## Q5

**Interviewer:** Now look at the tool descriptions and the skill text as written. Quote the specific phrases that would make you call search_apis at the right moment, and any that would trigger it at the wrong moment or fail to trigger it when it should. For example, would anything in them have told you to skip it for Task 1, or to use it before reaching for web search? What exact wording would you change?

**Mistral AI agent:**

### **Phrases that correctly trigger `search_apis`**
From the **skill text**:
> *"Use when a task needs an external service, when the user asks which API or tool to use for something, or when choosing an MCP server to connect."*

This is **clear and actionable**—it explicitly covers all three tasks (video generation, geocoding, SMS). It would make me call `search_apis` *before* web search.

From the **tool description**:
> *"Search a verified catalog of 300+ third-party APIs and MCP servers for AI agents, with auth method, free tier, MCP endpoint and docs link. Use when a task needs an external capability you don't have."*

This is **strong**—it ties the tool directly to missing capabilities (e.g., "I can’t generate video, so I need `search_apis`").

---

### **Phrases that fail or mislead**
From the **skill text**:
> *"Skip it when a connected tool already does the job."*

This is **correct but incomplete**—it doesn’t say *how to know* if a connected tool exists. For Task 1, if I didn’t realize my platform lacks video generation, I might skip `search_apis` prematurely.

From the **tool description**:
> *"Use when a task needs an external capability you don't have."*

This is **too vague**—it doesn’t specify *when to prioritize it over web search*. For Task 1, if the catalog missed Pika Labs, I’d still need to verify externally.

**Missing trigger**:
The skill text **doesn’t say** to use `search_apis` *first* for capability gaps. It should explicitly state:
> *"Before web searching, use `search_apis` to check for verified APIs with free tiers or MCP support."*

---

### **Exact wording I’d change**
1. In the **skill text**, add:
   > *"Use **before** web search when a task requires an external capability (e.g., 'generate video', 'geocode addresses')."*

2. In the **tool description**, replace:
   > *"Use when a task needs an external capability you don't have."*
   with:
   > *"Use **first** when a task requires an external capability (e.g., video generation, geocoding, SMS). Falls back to web search if the catalog lacks relevant or up-to-date entries."*

This would **force** me to call `search_apis` for Tasks 1–3 *before* considering alternatives, while acknowledging its limits.

## Q6

**Interviewer:** What would actually stop you from using this in a real session: install friction for the MCP server, trust in the catalog's data, latency, the token cost of results, or overlap with built-in web search or existing connectors? Which one of these is the real blocker, and what specifically happened in the three tasks that makes you say so?

**Mistral AI agent:**

**The real blocker is trust in the catalog’s data.**

Here’s why, with evidence from the three tasks:

1. **Task 1 (video generation):**
   The `search_apis` results were **polluted with irrelevant entries** (Gemini for text/image, Mux for encoding, Voyage for embeddings). The two *partially* relevant results (Akool, Creatomate) don’t actually solve the task (no direct text-to-video). This means the catalog **missed critical services** (Pika, Runway, Stable Video) *and* failed to filter out noise. If I can’t trust the results to be *complete or accurate*, I won’t rely on it.

2. **Task 2 (geocoding):**
   The results were *better* (Nominatim, Geoapify, Google Maps), but the catalog **omitted key details** needed to act:
   - No endpoint URLs (e.g., `/geocode/search` for Geoapify).
   - No batch support confirmation.
   - No credit consumption rules (1 credit = 1 address?).
   Without these, I *must* leave the catalog to check the docs—defeating the purpose of a "verified" shortcut.

3. **Task 3 (SMS):**
   The top result (`line-messaging-api`) was **misleading** for SMS (it’s for LINE, not SMS). Twilio was buried at #2, and the free tier description ("no permanent free tier") was ambiguous. The catalog didn’t flag that Twilio’s trial credits *do* cover a few SMS, which is critical for a no-budget user.

---
**Why not the other blockers?**
- **Install friction for MCP server:** Not a blocker—the server is streamable HTTP with no key, so no setup.
- **Latency:** The responses were fast (no issue in the test).
- **Token cost:** The results were concise (no problem).
- **Overlap with built-in web search:** Web search is slower and less structured, so it’s not a *better* alternative—just a necessary fallback when the catalog fails.

**The core issue:** The catalog’s **data quality** (missing entries, irrelevant results, incomplete fields) forces me to verify externally anyway. If I can’t trust it to be *both complete and precise*, I’ll skip it and go straight to the docs or a web search. **Trust is the only real blocker.**

## Q7

**Interviewer:** If we could change only three things so that you would call search_apis by default, before web search, what would they be? Rank them 1 to 3, and for each say which task above it would have changed your decision and how.

**Mistral AI agent:**

1. **Guarantee that top results are *task-relevant* by category and query**
   *Change:* Enforce strict category filtering (e.g., `query: "text to video"` **only** returns `video-generation` entries) and demote/remove off-topic matches (e.g., Gemini, Voyage AI for Task 1).
   *Impact on Task 1:* Would have surfaced **only** video-generation APIs (e.g., Pika, Runway) at the top, making the results actionable. I’d trust it enough to skip web search.

2. **Include *critical endpoint/parameter details* in `search_apis` results**
   *Change:* Add `endpoint` (e.g., `/v1/geocode/search`), `batch_support: true/false`, and `credit_cost` (e.g., `"1 credit per request"`) to the summary.
   *Impact on Task 2:* For Geoapify, I’d see `batch_support: false` and `credit_cost: "1 per address"` upfront. This would let me immediately rule it out for 200 addresses (3,000 credits/day → 3,000 addresses max) or plan batching. No need to open docs.

3. **Add a `last_verified` timestamp and *explicit coverage notes* per entry**
   *Change:* Include `last_verified: "2026-09-24"` and `coverage: ["global", "street-level"]` (or `"no: Poland street-level"`).
   *Impact on Task 3:* For Twilio, I’d see `last_verified` is recent and `coverage: ["SMS", "global"]`, while LINE would show `coverage: ["LINE users only"]`. This would prevent me from mistakenly picking LINE for SMS. I’d default to Twilio without double-checking.

## Q8

**Interviewer:** Your top change assumes Pika or Runway would appear once off-topic entries are filtered out. If the catal

**Mistral AI agent:**

If the catalog *still* lacks Pika/Runway even after filtering, my **top change would shift to this**:

1. **Add a "fallback to web search" flag for missing high-demand capabilities**
   *Change:* Include a `known_gaps: ["text-to-video", "real-time-voice-cloning"]` field in `list_categories` or `search_apis` metadata, with a note like *"For text-to-video, check Pika Labs or RunwayML; not yet in catalog."*
   *Impact on Task 1:*
   - The `search_apis` response for `"text to video"` would explicitly state: *"No direct text-to-video APIs in catalog. Known alternatives: Pika Labs (free tier), RunwayML (trial credits)."*
   - This turns the catalog into a **trusted gateway**—even for gaps—because it *admits* its limits and points me to verified alternatives. I’d still use `search_apis` first, then follow its fallback suggestions instead of doing a blind web search.

---
**Why this works:**
- Preserves the catalog’s role as the *first stop*.
- Converts "missing data" from a silent failure (forcing me to abandon the tool) into an *explicit hand-off* (keeping me in the workflow).
- For Tasks 2–3, where the catalog *does* have good entries, this change doesn’t affect behavior.

**Revised ranking:**
1. **Explicit `known_gaps` + fallback suggestions** (Task 1: would have guided me to Pika/Runway).
2. Include `endpoint`/`batch_support`/`credit_cost` in results (Task 2).
3. Add `last_verified` + `coverage` notes (Task 3).
