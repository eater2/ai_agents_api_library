# Product test: Google agent (google/gemini-3.8-flash)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Thanks for taking part. Attached are the tool definitions for the MCP server (search_apis, get_api, get_reviews, list_categories) and the accompanying skill text. Please take Task 1 and walk me through, step by step, what you would actually do to complete it. At each step, tell me which source you would rely on: your own knowledge, web search, one of these tools, or something else. If you would call search_apis at all, say at which point and with what query, and if not, what you would use instead and why.

**Google agent:**

Here is how I would handle Task 1 step by step:

1. **Assess native capabilities (Source: Own knowledge/platform):** As Gemini 3.8 Flash, I cannot natively generate video files. I check if my host environment provides a direct tool (e.g., Google Imagen/Veo integration). Assuming none is configured, I need an external service.
2. **Catalog Discovery (Source: `search_apis`):** Because the user has zero budget, I need a free solution. I would call `search_apis(query="text to video", free_tier=true, no_card=true)`. 
3. **Evaluate tool results (Source: Critical evaluation):** The actual output returned two weak options:
   - **Freepik API:** Misleadingly classed under `has_free_tier: true` when it is actually a one-time ~€5 credit (a trial, not a lasting free tier). Worse, `get_api` provides a `call.example` for *image-to-video* (`/kling-v2-1-pro`), not text-to-video, and requires an input image URL.
   - **Hugging Face Inference Providers:** Offers $0.10/month credits, which is negligible for video generation inference costs.
4. **Fallback (Source: Web search):** Because the catalog results fail the zero-budget/true text-to-video requirement, I fall back to web search to find current zero-budget consumer web interfaces (e.g., Luma Dream Machine, Kling, or Haiper free web trials) or an open model on Hugging Face Spaces (like CogVideoX) that runs without API fees.
5. **Respond to user (Source: Synthesized output):** I inform the user that automated API generation requires paid credits or a card, and direct them to free web-based UIs or Spaces to generate the clip manually.

## Q2

**Interviewer:** Now look at the real search results for Tasks 2 and 3. For each task, would you act on these results? Which specific result would you pick, and why? Is anything irrelevant, ranked too high or too low, or missing that you expected to see?

**Google agent:**

### Task 2: Geocode 200 addresses in Poland

**Action:** Yes, I would act on these results. 

**Pick:** **OpenCage Geocoding API** or **LocationIQ**.
- Both offer generous daily free tiers (2,500 and 5,000/day) requiring **no credit card**, easily covering 200 requests. 
- OpenStreetMap Nominatim is usable without a key (`no_auth: true`), but its strict Acceptable Use Policy explicitly discourages bulk geocoding and limits rates to 1 req/s; 200 addresses pushes the boundary of acceptable one-off use.
- ArcGIS requires a credit card (`requires_card: true`), and Google Maps Platform deprecated simple key signups without billing setup.

**Critique:**
- **Ranked too high:** ArcGIS. For an unauthenticated batch script, requiring a credit card makes it a poor first choice. 
- **Missing/Flaw:** The tool omitted Mapbox, which has a 100k/month free tier. Also, Google Maps MCP tools show `covers_full_api: false` and list tools like `search_places` and `lookup_weather`, but notably lack a dedicated geocoding tool.

---

### Task 3: Send an SMS reminder

**Action:** Yes, but strictly to advise the user, because SMS cannot be sent anonymously without credentials.

**Pick:** **Bird** (if hosted MCP is desired) or **Sinch/Twilio** for REST.
- However, for a one-off reminder, **Twilio** or **Sinch** provide free trial credits without a credit card. Note that Twilio trials restrict sending *only* to verified numbers, which may fail if the customer's number is arbitrary.

**Critique:**
- **Ranked too high:** AWS End User Messaging. It requires AWS IAM signatures (SigV4), complex registration (10DLC/origination identities), and offers zero free tier. It is the worst option for an agent seeking quick dispatch.
- **Flaw:** Twilio’s MCP server entry specifies `docs_only: true` (it only searches docs, cannot send SMS). Plivo’s MCP server is an unverified local repo (`remote_url: null`), requiring local installation.

## Q3

**Interviewer:** In your Task 2 and Task 3 picks, several claims

**Google agent:**

It looks like your question cut off mid-sentence, but if you are questioning specific claims made about the Task 2 and Task 3 results, here is the direct verification against the catalog data provided:

1. **Task 2 (Geocoding):**
   - **OpenCage & LocationIQ:** Both explicitly state `requires_card: false` with daily reset quotas (2,500 and 5,000 requests/day). 
   - **Nominatim Bulk Policy:** The catalog notes: *"bulk geocoding discouraged (small one-off jobs only, cached)"*. 200 requests at 1 req/s takes over 3 minutes and borders on policy abuse.
   - **Google Maps MCP Gap:** The catalog confirms the MCP tool only exposes `search_places`, `lookup_weather`, `compute_routes`, `resolve_names`, and `resolve_maps_urls`—it lacks an address geocoding endpoint despite the catalog assigning it `match: exact`.

2. **Task 3 (SMS):**
   - **Twilio Trial Restrictions:** The catalog data specifies: *"only up to 5 verified numbers"*. For arbitrary customer numbers, a Twilio trial will fail outright.
   - **Twilio MCP is Docs-Only:** The catalog lists `docs_only: true` for Twilio's hosted MCP endpoint (`https://mcp.twilio.com/docs`). An agent attempting to execute `send_sms` via that MCP would fail.
   - **AWS Overhead:** AWS SMS lists `auth: "cloud_iam"`, meaning standard API keys cannot be used without SigV4 signing infrastructure.

If you had a specific claim in mind that was cut off, please finish the question and I will address it directly.

## Q4

**Interviewer:** Apologies, my previous question was cut off. Let's move on. Take your Task 2 pick, OpenCage, and go from the `get_api` output to a first successful request for those 200 Polish addresses. Name the exact fields you would read, in order, and at which point, if any, you would leave the catalog for the provider's doc

**Google agent:**

Here is the exact progression from `get_api` to the first request:

1. **`mcp.remote_url` & `mcp.kind`:** I check if a hosted MCP server is ready to use. It shows `remote_url: null` (GitHub repo only). Because I cannot install local `stdio` servers in my execution sandbox, I immediately pivot to direct REST.
2. **`auth_scheme`:** I read `in`, `name`, and `format` to see where the API key goes. OpenCage uses a query parameter (`?key=YOUR_KEY`), not an HTTP header.
3. **`rate_limits`:** I check `rate_limits.summary`. It mandates **1 request/second** on the free tier. For 200 addresses, I must implement a 1-second delay between requests or a pacing queue to avoid HTTP 429 errors.
4. **`call.example` / `base_url`:** I check `base_url` (`https://api.opencagedata.com/geocode/v1`) and the example endpoint path (typically `/json?q=...&key=...`).

**Where I leave the catalog for the provider's docs:**
I leave for `docs` (`https://opencagedata.com/api`) before sending the first call. The catalog gives the generic endpoint, but for 200 Polish addresses I need specific query parameters that the catalog does not provide:
- Restricting search bounds to Poland (`countrycode=pl`).
- Preferred output language (`language=pl`).
- URL-encoding handling for Polish diacritics (`ą, ć, ę, ł, ń, ó, ś, ź, ż`). 

Once confirmed via docs, I ask the user for their OpenCage key and run the script sequentially with a 1-second sleep.

## Q5

**Interviewer:** Now look at the tool descriptions and the skill text themselves. In which situations would they make you call search_apis, and in which would they make you skip it? Also, did they ever tr

**Google agent:**

### When I would call `search_apis`
1. **Explicit API/MCP recommendations:** The user asks: "Which API or MCP server should I use for X?"
2. **Hard platform limits:** I must execute an action requiring third-party infrastructure that neither my native model nor platform tools possess (e.g., dispatching physical SMS, charging cards, interacting with specialized external CAD/BIM systems).
3. **Execution unblocking:** A direct API or tool call failed with 403, 429, or format rejection, and I need an alternative provider.

### When I would skip it
1. **Model-native skills:** Text translation, summarization, writing code, generating SVG/Mermaid diagrams, and standard analysis.
2. **Native platform tools:** Live web search (via Google Search), browsing, Python code execution via sandbox, and any pre-configured enterprise tools.
3. **Direct user provision:** If the user already provided credentials or an endpoint for a specific service (e.g., "Use my SendGrid key").

### Did they ever mislead or trigger a false path?
Yes. The search results in Task 1 and Task 2 exhibited clear trigger traps:
- **`match: exact` on broken capabilities:** Google Maps MCP was marked `match: exact` for geocoding, yet its MCP tool list completely lacked geocoding tools.
- **Trial labeled as `free_tier`:** Freepik was tagged `has_free_tier: true` despite having only a one-time trial credit.
- **`docs_only` trap:** Twilio returned a vendor MCP that only searches documentation, useless for the actionable verb "send SMS".

## Q6

**Interviewer:** Your examples of being misled all come from the result data (match labels, free-tier flags, docs_only), not from the wording of the tool descriptions or the skill. Quote the specific sentence or phrase in the search_apis description or the skill text that most affects whether you call the tool at the right moment, and tell me exactly how you would rewrite it.

**Google agent:**

### The Most Problematic Phrase

From the skill text under **"When to use"**:
> *"The task needs an external service: 'make a 5-second video', 'geocode 200 addresses', 'send this as an SMS'."*

(Mirrored in the `search_apis` tool description: *"Find a third-party API or MCP server for a capability you lack... Use it after checking your built-in and connected tools..."*)

### Why It Triggers Bad Calls
It instructs me to trigger `search_apis` whenever a task merely *needs* an external capability, regardless of whether:
1. The user provided credentials or even wants an automated API call.
2. The user is just asking me to write a script (e.g., "Write a Python script to geocode 200 addresses").
3. A no-auth fallback or simple code approach (e.g., using a Python library with Nominatim) is immediately viable in my code interpreter without discovering new vendor APIs.

This leads to an eager catalog lookup instead of first establishing user intent and execution feasibility.

---

### How I Would Rewrite It

> **"Use only when an execution step strictly requires a third-party API/MCP connection that cannot be fulfilled by native code execution or platform tools, when the user explicitly asks for service or provider recommendations, or when an existing API integration fails and needs a replacement. Do not call if you only need to write integration code or if the task can be completed inside an available code sandbox."**

## Q7

**Interviewer:** Let's turn to what would stop you from using this at all. Consider install friction, trust in the catalog data, latency, token cost of the responses, and overlap with your built-in Google Search or other connectors. Which of these is the real blocker for you, and what specifically happened, or would happen, that makes it the blocker rather than the others?

**Google agent:**

The real blocker is **trust in the catalog data**, which completely negates its advantage over built-in Google Search.

Here is what specifically happened in the test runs that proves it:
- **Task 1:** Freepik had `has_free_tier: true`, but the text described a one-off trial credit. Furthermore, its `call.example` was for *image-to-video*, failing the text-to-video task.
- **Task 2:** Google Maps MCP was marked `match: exact` for street geocoding, but its tool list (`search_places`, `lookup_weather`, `compute_routes`) contained no geocoding tool.
- **Task 3:** Twilio’s MCP server was marked official and exact, but was actually `docs_only: true`.

Because these subtle mismatches occur on critical fields (`match`, `has_free_tier`, `tools`), **I cannot trust the tool definitions or call examples without independent verification.** 

As shown in Task 2 with OpenCage, I still had to fetch the official vendor documentation to find essential parameters like `countrycode=pl`. If I must always cross-reference external documentation before executing a call to avoid broken runs or billing surprises, the catalog adds latency and burns tokens without saving a step. 

With built-in Google Search, I can query `"OpenCage geocoding API docs countrycode pl"` or `"best free geocoding API no credit card"` and receive fresh, direct documentation immediately, bypassing an unreliable intermediary catalog altogether.

## Q8

**Interviewer:** If you could change only three things so that you would call search_apis by default instead of going straight to Google Search, what would they be? Rank them, and for each one, say what you would need to see in the results before you would act on the catalog without cross-checking the vendor docs.

**Google agent:**

### 1. Granular Query-to-Parameter Schemas (Replace generic `call.example`)
* **The Problem:** The catalog provides vague curl snippets that lack real-world parameters (e.g., country filters, bounding boxes, diacritic handling).
* **What I need to see:** A mini-OpenAPI slice in `get_api` listing exact query/body parameters, their types, and defaults. For OpenCage, seeing `"parameters": {"countrycode": {"type": "string", "desc": "ISO 3166-1 alpha-2 code"}, "q": {"required": true}}` means I can generate a production-ready request for Poland immediately without visiting `docs`.

### 2. Strict, Programmatic Validation of `match` and `free_plan`
* **The Problem:** False positives (`match: exact` on Google Maps MCP lacking geocoding tools; trials labeled as `has_free_tier: true`).
* **What I need to see:** Automated linting against vendor endpoints. If an MCP server is returned for "geocoding", the exact capability must appear in its exposed tool names or schema. For billing, `has_free_tier` must strictly mean a recurring, permanent free allowance with `card_required: false/true`. If it's a one-off trial, mark it `trial_only: true`.

### 3. Actionable MCP Tool Signatures in `search_apis`
* **The Problem:** Knowing an MCP server exists is useless if it is `docs_only` or requires local `stdio` installation that my sandbox cannot run.
* **What I need to see:** A boolean `can_execute: true` and the exact tool input/output JSON schemas directly inside `get_api` (or an MCP registry endpoint). If it says `docs_only: true`, it should never match an operational query like "send SMS".

## Q9

**Interviewer:** You called trust in the catalog data the real blocker, yet you ranked parameter schemas first and match/free-tier validation second. If only one of those three shipped, which one would get you to call search_apis before Google Search on a task like Task 2, and why that one over the other two?

**Google agent:**

You are right to call out that contradiction. If only one can ship, it has to be **Strict Validation of Match and Free-Tier**. 

Without strict validation, parameter schemas are useless because I still wouldn't trust them to be accurate, up to date, or free of hidden billing traps. 

On Task 2, here is why strict validation alone would get me to call `search_apis` first:
- Geocoding APIs generally accept a full address string (`q="Marszałkowska 1, Warsaw, Poland"`). Parameters like `countrycode=pl` are optimizations; the query will still work without them.
- What will **break** the task completely is picking a provider that silently demands a credit card (ArcGIS), an MCP server that doesn't actually expose a geocode tool (Google Maps), or an endpoint with a fake "free tier" that halts after three calls.

If the catalog guarantees that `has_free_tier: true` strictly means recurring free requests with `requires_card: false`, and `match: exact` is verified against actual API capabilities, I can immediately select OpenCage or LocationIQ with 100% confidence. I wouldn't need to cross-check terms or search Google for alternative providers; I would simply format the call with the user's API key and execute. 

Trust is the foundation. Parameter schemas save a follow-up query, but validation is what makes the catalog safe to touch in the first place.
