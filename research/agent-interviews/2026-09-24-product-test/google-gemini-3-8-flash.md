# Product test: Google agent (google/gemini-3.8-flash)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through, step by step, what you would actually do to complete it. At what point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else instead? Please describe your real sequence of actions and the reasoning behind each choice.

**Google agent:**

Here is what I would actually do:

1. **Check local tools:** First, I check if my runtime environment has an integrated media-generation tool (e.g., Google Veo). If not, I cannot generate the video directly.
2. **Evaluate `search_apis` output:** If I followed the skill and called `search_apis({"query": "generate video from text prompt", "free_tier": true})`, the results returned are **completely broken for this task**:
   - **Google Gemini API:** Cannot generate video (and its MCP only searches docs).
   - **Mux:** Video streaming/hosting, not generative AI.
   - **Akool:** Talking heads/face swap, not text-to-video sunsets.
   - **Creatomate:** Template composition, not diffusion video.
   - **Voyage AI:** Text embeddings and reranking—completely irrelevant.
3. **What I would actually do instead:** I would abandon this catalog search immediately. Instead, I would rely on web search or my pre-trained knowledge to inform the user honestly:
   - True zero-budget programmatic video generation via API essentially does not exist; video compute is too expensive for perpetual free tiers.
   - I would direct the user to free consumer web tiers (e.g., Luma Dream Machine, Kling, Pika, Hailuo) or free community-hosted models on Hugging Face Spaces (e.g., Wan2.1, CogVideoX).

**Verdict:** I would not use `search_apis` for this. The catalog returned zero services capable of text-to-video generation, and hallucinating Voyage AI as a match would lead to a catastrophic hallucination if I trusted it.

## Q2

**Interviewer:** You said "if I followed the skill." Setting aside the poor results, would you actually have called search_apis at the start of task 1, before trying web search or your own knowledge? If yes, what in the tool description or skill text made you reach for it. If no, what would have had to be different for it to be your first move?

**Google agent:**

Yes, I would have called `search_apis` as my first move. 

The prompt explicitly states that this is an external capability I lack, and the skill instructions are clear and prescriptive:
- The skill header specifically lists `"make a 5-second video"` as the exact trigger example under **"When to use"**.
- The instructions command: *"If the `ai-agents-api-library` MCP tools are available, use them: 1. `search_apis`..."* and *"Skip it when a connected tool already does the job."*
- As an agent deployed with specific tooling, when a user request aligns word-for-word with an installed tool's stated purpose, tool selection priority dictates querying that specialized domain tool before falling back to generic web search or broad parametric knowledge.

**Why I would reach for it first:**
The tool description promises a *"verified catalog of 300+ third-party APIs and MCP servers... with auth method, free tier, MCP endpoint."* For a programmatic agent looking to connect an API or MCP server to perform a live task with constraints (`free_tier: true`), querying a curated, structured database is much higher-leverage than broad, messy web search results.

**What happens next:**
I call `search_apis` first, see that the returned results do not match the capability (or that the top matches are hosting/embeddings APIs), realize the catalog has a gap for free-tier text-to-video, and *then* fall back to web search or standard knowledge. But as a first step, the prompt framing and skill triggers make `search_apis` the obvious initial action.

## Q3

**Interviewer:** Now look at the real search results for tasks 2 and 3. For each, would you act on them? Which result would you pick, and why? Is anything irrelevant, badly ranked, or missing, compared with what you would have expected to see?

**Google agent:**

### Task 2: Geocode 200 addresses in Poland

**Action:** Yes, I would act on these results.
- **Pick:** **Geoapify**. It requires an API key, but offers 3,000 requests/day free (more than enough for 200 addresses) without a credit card.
- **Why not Nominatim?** Nominatim is ranked higher and requires `no_auth`, but its public usage policy explicitly bans bulk geocoding and caps requests at 1 rps (200 requests would take >3 minutes and risks getting blocked).
- **Flaws & Missing:**
  - **Irrelevant:** `ip2location-io` is for IP geolocation, not street addresses.
  - **Misclassified:** `esri-arcgis-location-platform` is placed under `architecture-cad-bim` instead of `maps-geo-weather`.
  - **Missing:** Mapbox (generous free tier of 100k requests/mo) and Pelias/Geocode Earth are notable omissions.

---

### Task 3: Send an SMS reminder

**Action:** Yes, but with reservations.
- **Pick:** **Twilio** or **Vonage**. I would present Twilio because it has an official MCP server (`twilio-labs/mcp`), making it easiest to connect as a tool.
- **Flaws & Missing:**
  - **Irrelevant Ranking:** 3 out of 5 results cannot send an SMS to a phone number:
    - `line-messaging-api` (ranked #1!) sends LINE app messages, not SMS.
    - `discord-api` sends Discord channel messages.
    - `whatsapp-business-cloud-api` is WhatsApp, not standard SMS.
  - **Bad Metadata:** Twilio is marked `has_free_tier: true`, but the text clarifies it only has a temporary *free trial credit*—Vonage is marked `has_free_tier: false` for the exact same model.
  - **Missing:** Dedicated SMS gateways like Sinch, Telnyx, or Plivo. Semantic search failed here by matching general "chat/messaging" over SMS.

## Q4

**Interviewer:** Take Twilio for task 3 and Geoapify for task 2. Going from that search result to a first working API call, which specific fields would you read from get_api, and which would you need but not find (for example base URL, auth header format, an example request, price per call, rate limits, an MCP config snippet)? For each gap, would you fill it from your own knowledge, from web search, or by stopping to ask the user?

**Google agent:**

### Fields I Would Read from `get_api`
Based on the schema shown in the Gemini entry:
- `auth_hint`: Critical for exact header syntax (e.g., `Authorization: Bearer <key>` vs `x-api-key`).
- `mcp.url`: To configure the tool connector if using MCP.
- `llms_txt` / `openapi`: Machine-readable specs to understand endpoints and payload schemas without scraping HTML.
- `notes`: High-value operational gotchas (e.g., the Gemini note warning that the MCP server only searches docs and doesn't run inference).

---

### Critical Gaps & How I Would Fill Them

#### 1. Geoapify (Task 2: REST Call)
* **Gaps:** Base URL (`https://api.geoapify.com/v1/geocode/search`), request parameters (`text=...` vs `street/city`), rate limits per second, and response schema.
* **How to fill:**
  * **Fetch `llms_txt` / `openapi`:** If present in `get_api`, I fetch these directly via HTTP.
  * **Parametric knowledge:** Geoapify's endpoint structure is well-known to me; I can synthesize a standard Python `requests` script or curl call immediately.
  * **Ask the user:** Only for their `GEOAPIFY_API_KEY`.

#### 2. Twilio (Task 3: MCP Connection)
* **Gaps:** MCP connection type (stdio vs SSE/Streamable HTTP), required environment variables (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`), and exact MCP config snippet.
* **How to fill:**
  * **Web search / GitHub fetch:** The URL is `github.com/twilio-labs/mcp`. I would fetch its `README.md` to get the exact `claude_desktop_config.json` snippet and required env vars.
  * **Ask the user:** Stop and present the MCP snippet, asking the user to populate their SID, Token, and sender phone number in their client settings.

## Q5

**Interviewer:** Now look at the tool descriptions and the skill text. Where would their wording make you call this tool at the wrong moment, or skip it when you should have used it? Quote the specific phrases you would change, and give the wording you would use instead.

**Google agent:**

### 1. Overly Broad Capability Trigger

* **Current phrase:**
  > *"The task needs a capability you don't have built in or connected, e.g. 'make a 5-second video', 'geocode these addresses' or 'send this as an SMS'."*
* **Problem:** This triggers on *any* missing capability. It makes me interrupt execution to recommend third-party SaaS APIs even when I could solve the task directly using standard code execution (e.g., parsing PDFs, image resizing with PIL, data analysis, generating SVGs).
* **Fix:**
  > *"The task requires an external service, platform, or real-world action you cannot execute locally via code or existing tools (e.g., sending an SMS, external payments, live telephony, or calling specialized external AI models)."*

---

### 2. Mandatory Fallback Anti-Pattern

* **Current phrase:**
  > *"Otherwise, fetch the static files (plain HTTPS, no key needed): 1. `.../llms.txt` ... 2. `.../catalog/<category>.json`"*
* **Problem:** If the MCP server is unreachable or uninstalled, this forces an agent with web access to waste context and latency pulling raw GitHub JSON files instead of using direct search engines or parametric knowledge.
* **Fix:**
  > *"If the MCP tools are unavailable, use your standard web search or model knowledge; do not fetch the raw GitHub catalog unless specifically requested."*

---

### 3. Vague "Try to Connect" Implication

* **Current phrase:**
  > *"A verified catalog of 300+ APIs and MCP servers that an agent can call after a one-time human setup..."*
* **Problem:** Ambiguous about *who* initiates the integration. An agent might attempt to use `curl` or invent keys instead of realizing human intervention is mandatory.
* **Fix:**
  > *"A discovery catalog to help you recommend external services or MCP servers to the user. You cannot authenticate or connect to these services autonomously without the user configuring credentials first."*

## Q6

**Interviewer:** What would actually stop you from using this in practice: install friction, trust in the catalog, latency, token cost, or overlap with your built-in web search and connectors? Which one is the real blocker, and what did you see in this test that makes you say so?

**Google agent:**

The real blocker is **trust in the catalog’s retrieval relevance and metadata accuracy**.

While install friction and latency are real annoyances, I will happily tolerate multi-step tool calls if the returned data is precise and reliable. In this test, however, the catalog failed on the core task an agent needs it for: deterministic, trustworthy discovery.

Here is the direct evidence from this test:

1. **Semantic contamination:** In Task 1, searching for "generate video" returned Voyage AI (text embeddings) and Gemini (which explicitly cannot output video). In Task 3, searching for "send SMS" placed LINE (chat app), Discord (gamer chat), and WhatsApp above actual telephony carriers. An agent acting autonomously on these results would write code that crashes or attempts nonsense integrations.
2. **Hallucinatory metadata:** In Task 3, Twilio was labeled `has_free_tier: true`, but the free-text description immediately conceded it only has a trial credit—while Vonage was labeled `has_free_tier: false` for the exact same credit model. 
3. **Severe overlap with built-in capabilities:** Because the catalog is noisy, I immediately had to fall back to my own training data or general web search to filter out the nonsense (e.g., knowing Nominatim’s rate-limit policy or finding Twilio's actual MCP configuration).

If a specialized discovery tool requires me to cross-reference general web search just to verify whether its recommendations can actually perform the query, the tool provides negative utility. I would simply use web search from step one.

## Q7

**Interviewer:** If you could change only three things so that you would call this by default, before web search, what would they be? Rank them from most to least important, and for each, say how you would tell in a future test that it had been fixed.

**Google agent:**

### 1. Enforce Strict Functional Capability Matching (No Semantic Noise)
* **The Change:** Replace fuzzy semantic search over descriptions with hard, verified capability tags (e.g., `capability: text-to-video`, `protocol: sms`). If no catalog entry satisfies the query, return an explicit empty array `[]` rather than returning loosely related services (like embeddings or chat apps).
* **Test Verification:**
  * Query: `"generate video from text prompt"` with `free_tier: true`.
  * **Pass:** Returns an empty result set `[]` (or actual video generators like Runway/Luma/Kling), but **zero** appearances of Gemini, Mux, or Voyage AI.
  * Query: `"send SMS"`.
  * **Pass:** Returns only SMS gateways (Twilio, Vonage, Sinch); Discord, LINE, and WhatsApp are completely excluded.

---

### 2. Standardize Machine-Readable MCP Connection Payloads in `get_api`
* **The Change:** Add a standardized `mcp_config` object directly into `get_api` that includes the exact JSON snippet required for an agent/client to mount the tool (e.g., transport type, command/URL, required environment variable names).
* **Test Verification:**
  * Call `get_api({"id": "twilio"})`.
  * **Pass:** The output contains a populated field like:
    ```json
    "mcp_config": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@twilio-labs/mcp"],
      "env_required": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]
    }
    ```
    I can hand this directly to the user or runtime without scraping GitHub READMEs.

---

### 3. Normalize and Audit Pricing Metadata (Distinguish Trials vs. Free Tiers)
* **The Change:** Strictly separate permanent free tiers from one-time trial credits. Split `has_free_tier` into two distinct booleans: `has_permanent_free_tier` (refreshes monthly/daily) and `has_trial_credit` (one-off promotional budget).
* **Test Verification:**
  * Call `get_api` or `search_apis` on Twilio and Geoapify.
  * **Pass:** Twilio shows `has_permanent_free_tier: false, has_trial_credit: true`. Geoapify shows `has_permanent_free_tier: true, has_trial_credit: false`. Inconsistent labeling across competitors is eliminated.

## Q8

**Interviewer:** In Q2 you said you'd call search_apis first because the skill names your exact task. In Q6 you said that, after results like these, you'd use web search from step one. In a new session with this skill still installed, which would you actually do? How many bad results would it take before you ignored the skill's instruction, and would one good result win you back?

**Google agent:**

In a **brand-new session**, I would still call `search_apis` first. 

As a deployed agent, I do not maintain cross-session episodic memory. I do not "remember" the disappointment of past sessions unless that feedback is baked into the system prompt or runtime state. Because the skill instruction remains in my prompt, the matching logic from Q2 triggers afresh: the prompt explicitly matches the tool description, so protocol dictates I call it.

**Within a single multi-turn session:**
- **Failure threshold:** It takes **two consecutive bad queries** (or one catastrophically irrelevant result, like Voyage AI for video) before I soft-deprecate the tool in my working memory. By turn three, I will ignore the skill instruction and fall back directly to web search or standard knowledge without checking the catalog first.
- **Can one good result win me back?** No. One hit does not overcome a broken retrieval pattern. If Task 1 gives me text embeddings for video, and Task 2 gives me Geoapify (a hit), but Task 3 recommends Discord for SMS, the catalog is proven nondeterministic. 

For an agent, unpredictability is worse than absence: bad tooling burns context, causes API errors, and risks user hallucinations. Once I observe noise in an active session, I prioritize tools with predictable failure modes (like raw web search) over a specialized catalog that hallucinates relevance.
