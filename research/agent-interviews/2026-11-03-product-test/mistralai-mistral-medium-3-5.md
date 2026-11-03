# Product test: Mistral AI agent (mistralai/mistral-medium-3-5)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through what you would actually do, step by step, from reading the task to producing a result. At which point, if any, would you call search_apis? Where would you instead rely on web search, your own knowledge, or something else? Please describe what you would really do, not what you think we'd like to hear.

**Mistral AI agent:**

For Task 1 ("Make a 5-second video clip of a sunset over the sea from a text prompt. The user has no budget."):

1. **Initial assessment**: I recognize this requires text-to-video generation, which is not a native capability of my model. I don't have built-in tools for this, so I need to check if connected MCP servers or APIs can do it.

2. **First check**: I would quickly recall if I already have access to any connected MCP servers that can generate video. Since the user hasn't connected any, I proceed to search.

3. **Call search_apis**: I'd call `search_apis` with `query="generate video from text prompt"` and `free_tier=true` (since the user has no budget). This is the exact point I'd use the product—it's the fastest way to find a free, verified service for this specific operation.

4. **Evaluate results**: From the provided output, Freepik API (Magnific) and Hugging Face Inference Providers are returned. Freepik's entry shows:
   - It supports text-to-video (`video_generate` tool in MCP)
   - Free tier: ~5 EUR credits (sufficient for a 5-second clip)
   - MCP server is vendor-hosted (`https://mcp.magnific.com`) but requires OAuth, which is a minor friction.

   Hugging Face is less clear (only "listed" match, no MCP tool for video). So Freepik is the better candidate.

5. **Next step**: I'd call `get_api` for `freepik-api` to confirm:
   - Exact endpoint (`text-to-video/ltx-2-pro`)
   - Auth method (OAuth for MCP, or API key for REST)
   - Free tier details (~5 EUR credits)
   - Example call (provided, matches the task).

6. **Decision**: Since the user has no budget, I'd present Freepik/Magnific as the only viable option. I'd tell them:
   - They need to sign up for a free account to get credits.
   - They can use the REST API (simpler) or connect the MCP server (if their platform supports OAuth).
   - The example `curl` command can be adapted for their prompt.

7. **Fallback**: If Freepik's free tier were insufficient or the MCP server failed, I'd try Hugging Face's inference endpoints (but the free tier is tiny: $0.10/month). If both fail, I'd fall back to web search for other free text-to-video APIs (e.g., Pika Labs, but they often require sign-up or have waitlists).

**Where the product helps**: It saves me from guessing or web searching—it gives verified, up-to-date details on free tiers, MCP support, and example calls. The `mcp_fit` field is particularly useful to know if I can use an MCP tool directly.

**Where it doesn’t**: The product doesn’t handle the actual API call or credential setup. I’d still need the user to provision credentials and connect the MCP server or use the REST endpoint. The "no budget" constraint is also not fully addressed—5 EUR is technically free, but the user might not realize it’s a limited credit pool.

## Q2

**Interviewer:** You said you'd call search_apis right after realizing you lack video generation. Suppose this is a real session where you also have a general web search tool, and from memory you already know candidates like Replicate, Runway, or Hugging Face. What would actually decide whether you call search_apis,

**Mistral AI agent:**

In a real session with web search available and prior knowledge of Replicate/Runway/Hugging Face, here's the actual decision process:

1. **First thought**: I know these services *exist* and do text-to-video, but I don't remember:
   - Which have free tiers (Runway's free tier is often limited to 3-second clips, Replicate may require payment)
   - Their exact auth methods (API key vs OAuth)
   - Whether they have MCP servers or if those cover video generation
   - Current free quota limits or if they've changed recently

2. **The decider**: I'd call `search_apis` **only if** I need to verify these unknowns *before* suggesting a service. The product's value here is:
   - Confirming free tier status (e.g., Magnific's ~5 EUR vs Runway's 3-second limit)
   - Checking MCP server availability (e.g., Hugging Face's MCP doesn't expose video tools)
   - Getting the exact example call and auth details to avoid trial-and-error

3. **When I wouldn't call it**:
   - If I recall a service *definitely* meets the criteria (e.g., "Pika Labs has a free tier and no auth"), I'd skip `search_apis` and go straight to web search for the latest docs.
   - If the user already mentioned a specific service (e.g., "use Runway"), I'd verify its details via `get_api` directly.

4. **Reality check**: In practice, I'd likely call `search_apis` first because:
   - My memory of free tiers is unreliable (they change frequently)
   - The product's `mcp_fit` field tells me if I can use MCP tools *immediately* (saving implementation time)
   - It surfaces lesser-known options (e.g., Magnific) that might fit better than my known candidates

**Bottom line**: I call `search_apis` when I need *actionable certainty* about free tiers, MCP support, or exact endpoints. Otherwise, I default to web search or memory. The product wins when it saves me from dead ends (e.g., suggesting Runway only to find its free tier is too restrictive).

## Q3

**Interviewer:** Now look at the actual search results returned for all three tasks. For each task, which result would you act on, and why that one? Which results are irrelevant, ranked too high or too low, or missing entirely, meaning a service you expected to see that wasn't there?

**Mistral AI agent:**

### **Task 1: Generate a 5-second sunset video (no budget)**
**Action:** **Freepik API (Magnific)**
- **Why:** Only result with a *lasting* free tier (~5 EUR credits, enough for a short clip). The MCP server is vendor-hosted (no install), and the `call` example matches the task exactly (`text-to-video/ltx-2-pro`). Hugging Face’s free tier is negligible ($0.10/month), and its MCP doesn’t expose video tools.

**Issues with results:**
- **Hugging Face Inference Providers** is ranked too high—its free tier is useless for this task, and `mcp_fit` confirms no video tool.
- **Missing:** Pika Labs, Luma AI, or Stable Video Diffusion (all offer free tiers or trials). Their absence is a gap.

---

### **Task 2: Geocode 200 Polish addresses**
**Action:** **GUGiK (Poland’s official geocoding service)**
- **Why:** No auth, no rate limits, *explicitly* for Polish addresses, and government-backed (reliable). Photon is global but throttles heavy use; LocationIQ’s 5K/day limit is sufficient but requires an API key. GUGiK is the only zero-friction option.

**Issues with results:**
- **Photon** is ranked too high—its "fair use" policy makes it unreliable for 200 addresses.
- **Google Maps** is irrelevant here—it requires an API key and has stricter quotas (10K/month for Essentials, but overkill for Poland-only).
- **Missing:** Nominatim (OpenStreetMap’s geocoder), which is free, no-auth, and widely used. A notable omission.

---
### **Task 3: Send an SMS reminder**
**Action:** **Twilio (trial)**
- **Why:** Despite being a trial (100 SMS, 30 days), it’s the most reliable for a *single* SMS. The MCP server exists (though alpha), and the `sms` metadata confirms Poland support and clear pricing. Textbelt’s 1 SMS/day limit is too restrictive for real use.

**Issues with results:**
- **Textbelt** is ranked too high—its 1 SMS/day limit is impractical unless the user *only* needs one message ever.
- **Sinch/Telnyx/Vonage** are trials but ranked lower—they’re valid alternatives, but Twilio’s trial is more straightforward (no sender registration for Poland).
- **Missing:** AWS SNS (pay-as-you-go, but no free tier), or simpler services like Clockwork SMS (UK-focused). Also, no mention of **MessageBird** (which has a free trial).

## Q4

**Interviewer:** Take the result you picked for Task 3 (Twilio trial) and imagine you now have to

**Mistral AI agent:**

If I now have to **actually send the SMS via Twilio’s trial**, here’s what I’d do step-by-step, using the product’s data and my own constraints:

1. **Confirm trial limits**: From `get_api` (or the search result), I see Twilio’s trial allows **100 SMS, but only to verified numbers in the signup country**, with **predefined templates**. For Poland, I’d need to:
   - Check if the user’s phone number is **verified** in their Twilio account (if not, they must add it first).
   - Ensure the message fits a **template** (no custom body). If the reminder is dynamic (e.g., "Your appointment is at 3PM"), this fails.

2. **Check sender rules**: The `sms.sender_registration` field says Poland allows **alphanumeric sender IDs without pre-registration**, so no extra setup is needed for a basic test.

3. **Auth setup**:
   - The MCP server (`@twilio-alpha/mcp`) requires `TWILIO_ACCOUNT_SID` and `TWILIO_API_KEY` (or `API_SECRET`). I’d ask the user to:
     - Create a Twilio account (no card for trial).
     - Grab their `ACCOUNT_SID` and `API_KEY` from the console.
     - Verify the recipient number in Twilio’s trial settings.

4. **Call the API**:
   - Use Twilio’s REST API (`POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`) or the MCP tool (if connected).
   - Example payload (from memory, since the product’s `call` example isn’t provided for Twilio):
     ```json
     {
       "To": "+48123456789",
       "From": "+1234567890",  // Twilio trial number
       "Body": "Reminder: Your appointment is soon."  // Must match a template
     }
     ```

5. **Fallback if blocked**:
   - If the number isn’t verified or the template is custom, I’d switch to **Textbelt** (1 SMS/day, no auth) as a last resort, despite its limits.

**Where the product helped**:
- Confirmed Poland’s sender rules and trial constraints upfront (avoiding wasted time).
- Told me the MCP server exists but is alpha (so REST might be more reliable).

**Where it didn’t**:
- No `call` example for Twilio’s SMS endpoint (I’d rely on memory or docs).
- No way to verify if the user’s number is pre-verified (that’s a runtime check).

## Q5

**Interviewer:** You wrote the Twilio request from memory. You were also unsure

**Mistral AI agent:**

You're right—I'd **not** rely on memory for the Twilio request. Here's what I'd *actually* do:

1. **Get the exact endpoint and auth**: Since `search_apis` didn't include a `call` example for Twilio, I'd call `get_api({"id": "twilio"})` to pull the full entry. If that still lacks a `call` example (as in the provided data), I'd fall back to Twilio's official docs (linked in the `docs` field: `https://www.twilio.com/docs/usage/api`).

2. **Use the docs to construct the request**:
   - The Twilio REST API for SMS is well-documented. I'd pull the exact endpoint (`/2010-04-01/Accounts/{AccountSid}/Messages.json`), required headers (`Authorization: Basic {base64(ACCOUNT_SID:API_KEY)}`), and body format (`To`, `From`, `Body`).
   - I'd avoid reinventing this from memory—APIs change, and Twilio’s trial has quirks (e.g., `From` must be a Twilio trial number).

3. **Validate constraints**:
   - From the product’s `sms.trial_limits` field, I already know:
     - Only **verified numbers** work.
     - **Predefined templates only** (so I’d check if the user’s message is allowed).
   - If the user’s message is custom, I’d warn them it might fail and suggest Textbelt as a fallback (despite its 1 SMS/day limit).

4. **Execute**:
   - If the user has connected the Twilio MCP server, I’d use its `SMS` tool (listed in `mcp.tools`).
   - Otherwise, I’d generate the exact `curl` command from the docs and ask the user to run it (or use a connected HTTP tool).

**Key point**: The product’s `get_api` gives me the `docs` link and trial constraints, but without a `call` example, I’d **always defer to the official docs** rather than guess. The product’s value here is *filtering* (Twilio is viable for Poland) and *warning* (trial limits), not replacing the docs.

## Q6

**Interviewer:** Look at the tool descriptions and the skill text as written. Would they make you reach for search_apis at the right moment, and are there situations where they would make you call it when you shouldn't, or fail to trigger when you should? Quote the specific wording you would change, and say what you'd replace it with.

**Mistral AI agent:**

### **When it works (right trigger):**
The skill text’s **"When to use"** section is clear:
> *"The task needs an operation unavailable through your model, built-in tools or currently connected tools... If you cannot name the tool that does it, search."*

This would make me call `search_apis` at the right moment—for tasks like video generation, geocoding, or SMS, where I lack native capabilities.

---

### **When it fails (wrong triggers or misses):**

1. **Over-triggering for adjacent services:**
   The `search_apis` description says:
   > *"Results are ranked by operation fit, evidence, lasting free plan, card and auth effort and bulk limits, not by your budget or region."*

   **Problem:** This could make me call `search_apis` for tasks where a built-in tool *almost* works (e.g., "summarize this PDF" when I can already read text but not parse PDFs). The skill text doesn’t explicitly warn against this.

   **Fix:** Add to **"When to use"**:
   > *"Skip it if a built-in or connected tool can do the job with minor adjustments (e.g., parsing a file format before processing)."*

2. **Missing triggers for known services:**
   The skill text says:
   > *"The user names a service ("geocode with Nominatim", "send it through Twilio"), or you are about to use one for a batch, a message, a payment or another third-party action: call `get_api` first."*

   **Problem:** This implies I should call `get_api` *only after* the user names a service, but I might forget to verify its constraints (e.g., Twilio’s trial limits). The wording doesn’t force me to check *before* suggesting a service.

   **Fix:** Replace with:
   > *"If the user names a service or you plan to use one, call `get_api` **immediately** to verify free tiers, auth, and limits—even if you think you know it."*

3. **Ambiguous "built-in tools":**
   The skill text says:
   > *"Skip it when a built-in or connected tool already does the job within this task's volume, cost and data limits..."*

   **Problem:** "Built-in tools" is vague. For example, can I generate a simple image with DALL·E? If yes, I shouldn’t search for APIs. But the text doesn’t clarify what’s considered "built-in."

   **Fix:** Replace with:
   > *"Skip it if your model or platform provides the operation natively (e.g., image generation, web search, code execution) **and** meets the task’s constraints (volume, cost, legality)."*

---
### **Summary of changes:**
| **Current wording** | **Problem** | **Replacement** |
|---------------------|------------|----------------|
| *"Results are ranked by operation fit..."* | Over-triggers for adjacent tasks | Add: *"Skip if a built-in tool can do the job with minor adjustments."* |
| *"The user names a service... call `get_api` first."* | Doesn’t force pre-check | Replace with: *"Call `get_api` **immediately** to verify constraints."* |
| *"Skip it when a built-in or connected tool already does the job..."* | "Built-in" is vague | Replace with: *"Skip if your model/platform provides the operation natively **and** meets constraints."* |

## Q7

**Interviewer:** Assume the tool is available in your environment. What would actually stop you from calling it: having to install or connect the MCP server, not trusting the catalog's data, latency, the tokens the results consume, or overlap with web search and connectors you already have? Which one of these is the real blocker, and why that one rather than the others?

**Mistral AI agent:**

The **real blocker** is **not trusting the catalog's data**.

Here’s why it outweighs the others:

1. **Install/connect MCP server**: The product’s MCP server is *already available* in my environment (per your assumption). Even if a result requires a *different* MCP server (e.g., Twilio’s), the catalog tells me whether it’s `remote` (no install), `stdio` (needs install), or `docs_only`. I can act on that—no blocker.

2. **Latency**: The MCP server is hosted (`vercel.app`), and the tool responses are small (JSON). Latency is negligible compared to the time saved by avoiding web searches.

3. **Token consumption**: The tool is read-only (no LLM calls), so it costs negligible tokens. Not a blocker.

4. **Overlap with web search/connectors**: The catalog is *faster* than web search for this specific use case (finding APIs/MCP servers). If I already have a connector for a service (e.g., Twilio), the catalog’s `get_api` would confirm its constraints—still useful.

**Why distrust is the blocker:**
- The catalog’s data could be **stale** (despite `last_checked` dates). For example:
  - Free tiers change (e.g., Twilio’s trial might now require a card).
  - APIs get deprecated (e.g., a `video_generate` endpoint might be removed).
- If I act on incorrect data (e.g., "this API is free" when it’s not), the task fails, and the user loses trust. **This risk is existential**—it’s why I’d hesitate to rely on the catalog *without verification*.

**What I’d do:**
- Use `search_apis` to *shortlist* candidates, but **always cross-check critical details** (free tier, auth, endpoints) with the official docs (via the `docs` link) before acting.
- If the catalog’s `uptime` or `link_check` shows issues (e.g., `broken`), I’d skip it entirely.

**Bottom line:** The other factors are manageable, but **incorrect data breaks the workflow**. That’s the real blocker.

## Q8

**Interviewer:** You said you'd always cross-check the free tier, auth and endpoints against the official docs. If you do that every time, the catalog only saves you the shortlisting step. What specific evidence on an entry would let you skip that docs check and act directly? For example: a last_checked date within a certain number of days, a source quote with a URL, a successful test call by the catalog, or reviews from other agents. Which of these, if any, would actually change your behavior, and what threshold would you need?

**Mistral AI agent:**

The **only evidence** that would let me skip the docs check is:

**A `call` example with a `source_url` and a `checked_at` date within the last 7 days, *plus* a successful `uptime` probe of the exact endpoint used in the example.**

### Why this threshold?
1. **`call` + `source_url` + recent `checked_at`**:
   - The `call` example proves the operation is supported (e.g., `POST /v1/ai/text-to-video`).
   - The `source_url` (e.g., to the API’s official docs) lets me verify the example’s origin.
   - If `checked_at` is ≤7 days old, the chance of the endpoint/params changing is low.

2. **`uptime` probe of the exact endpoint**:
   - The catalog’s `uptime` field shows if the base URL (e.g., `https://api.magnific.com/v1`) is reachable. But I’d need **proof the specific endpoint in `call` was tested** (e.g., `uptime` for `https://api.magnific.com/v1/ai/text-to-video/ltx-2-pro`).
   - If the probe returned `200` (not just `401`/`404`), I’d trust the endpoint exists and matches the example.

### What wouldn’t be enough:
- **`last_checked` on the entry alone**: Too vague (could just mean the docs were reviewed, not the API tested).
- **Reviews or ratings**: These are about user experience, not API correctness.
- **MCP handshake success**: Only proves the MCP server is up, not that the underlying API works as described.

### Example from Task 1 (Freepik/Magnific):
- The `call` example includes a full `curl` command with the exact endpoint (`/v1/ai/text-to-video/ltx-2-pro`).
- The `checked_at` for the `call` field is `2026-09-25` (recent).
- The `uptime` shows the base URL (`api.magnific.com/v1`) is up, but **not the specific endpoint**. Until the catalog probes the full endpoint, I’d still check the docs.

### Behavior change:
If the catalog added **endpoint-level uptime probes** (e.g., testing the exact `call.url` and confirming `200` or `401`), I’d skip the docs check for that specific operation. Otherwise, I’d always verify.

## Q9

**Interviewer:** If we could change only three things about the catalog, the tool descriptions or the skill so that you would call this by default whenever a task needs an external API, what would they be? Rank them from most to least important, and for each one say which specific behavior of yours it would change.

**Mistral AI agent:**

### **1. Add a "verified_endpoint" field with a recent probe of the exact API call (not just the base URL)**
**Behavior change:** *I’d skip the docs check for the specific operation if the endpoint was tested within 7 days and returned a valid response (200, 401, or 400 with expected parameters).*
- **Why:** This is the only way to prove the `call` example works as written. Currently, `uptime` only checks the base URL (e.g., `api.magnific.com/v1`), not the full endpoint (e.g., `/v1/ai/text-to-video`). Without this, I *must* verify manually.

---

### **2. Add a "free_tier_verified" flag with a timestamp and source URL**
**Behavior change:** *I’d trust the free tier details (quota, auth, card requirements) without cross-checking if the flag is set and the timestamp is ≤7 days.*
- **Why:** Free tiers change frequently (e.g., Twilio’s trial limits, Hugging Face’s credits). The catalog already includes `free_plan` and `checked_at`, but I’d need explicit confirmation that the free tier was *tested* (e.g., a successful no-cost call) or *officially documented* at the `source_url`.

---
### **3. Add a "breaking_changes" field with a date and description of recent API changes**
**Behavior change:** *I’d stop second-guessing whether an API’s behavior has changed since the last check.*
- **Why:** Right now, even if `last_checked` is recent, I don’t know if the API was updated *after* that check. A `breaking_changes` field (e.g., `"2026-10-01: LTX Video 2.0 Pro now requires a paid plan"`) would let me act with confidence or avoid stale entries entirely.

---
### **Ranking Rationale:**
1. **Endpoint verification** is the biggest blocker—without it, I *always* check the docs.
2. **Free tier verification** is next—this is the most common point of failure (e.g., "free" turns out to require a card).
3. **Breaking changes** are a nice-to-have but less critical, since I can often infer staleness from `last_checked` + `uptime`.
