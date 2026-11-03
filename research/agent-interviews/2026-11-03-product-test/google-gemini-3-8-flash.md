# Product test: Google agent (google/gemini-3.8-flash)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through, step by step, what you would actually do to complete it. At which point, if any, would you call search_apis? Or would you use web search, your own knowledge, or something else instead? Please explain why at each step.

**Google agent:**

**Step 1: Assess internal capabilities.**
As Gemini, I have no built-in tool or capability to render video files directly. 

**Step 2: Tool discovery via `search_apis`.**
I would call `search_apis` right away rather than web search, because structured catalog tools give immediate auth, MCP, and pricing metadata. However, I would query `{"query": "text to video", "no_card": true, "free_tier": true}`.

**Step 3: Evaluate catalog output (and catch errors).**
The catalog’s actual results for Task 1 show significant flaws:
- **Misclassified pricing:** `freepik-api` lists `has_free_tier: true`, but describes “~5 EUR of free credits” (a one-off trial) and `no_card: false`. For a user with zero budget, requiring a credit card for a one-off trial is a blocker.
- **Contradictory MCP metadata:** The search summary reports `mcp_fit: "no MCP tool named for this operation"`, yet the tool array in the exact same payload explicitly includes `"video_generate"`.
- **Inadequate tier:** Hugging Face offers $0.10/month—insufficient for video generation pipelines.

**Step 4: Resolve and respond.**
Because the catalog results failed the zero-budget constraint, I would fall back to web search or my own knowledge to recommend truly free web interfaces (e.g., Hugging Face Spaces running open models like CogVideoX or LTX, or free trials without cards like Hailuo/Minimax). I cannot generate the video myself, so I would guide the user to the best free service to run the prompt.

## Q2

**Interviewer:** You already flagged problems with task 1's results. Now look at the real search results for all three tasks. For each task, which specific result would you pick and act on, if any? Which results are irrelevant or ranked too high or too low? What did you expect to see that was missing?

**Google agent:**

### Task 1: Video Generation (Zero Budget)
- **Pick:** Neither. Both fail the zero-budget/free-tier constraint. Freepik requires a card for one-off credits, and Hugging Face’s $0.10/month won't cover a video inference run. 
- **Ranking / Irrelevant:** Freepik is ranked too high due to misclassifying a trial as a lasting `free_tier`. 
- **Missing:** Open-weight model hosts with real free access, such as dedicated Hugging Face Spaces (Gradio API), Replicate, or Kling/Luma trials.

### Task 2: Geocode 200 Polish Addresses
- **Pick:** **`gugik-geocoding`**. It is Poland’s official geodesy service, requires no auth (`no_auth: true`), costs nothing, and is tailor-made for national TERYT/SIMC addresses.
- **Ranking / Irrelevant:** 
  - **Photon** is ranked too high: public instances explicitly forbid/throttle batch jobs, making it risky for 200 addresses without self-hosting.
  - **Google Maps** is ranked too high: its MCP server has no geocoding tool (`search_places` only), requires a billing-enabled card, and adds unnecessary friction.
  - **LocationIQ / OpenCage** are solid fallbacks (OpenCage has a working MCP server), but correctly placed behind GUGiK.
- **Missing:** Nominatim (OpenStreetMap) with a batch-policy warning.

### Task 3: Send an SMS Reminder
- **Pick:** **`textbelt`** only if sending a single test message today (shared key, zero friction, 1 SMS/day). For a real customer reminder, **`twilio`** via REST (ignoring the alpha stdio MCP) is the realistic pick.
- **Ranking / Irrelevant:** 
  - **Telnyx** is ranked too high for MCP: its tools are generic REST wrappers (`invoke_api_endpoint`), not SMS tools.
  - **Sinch's** MCP is misattributed: `mcp_fit` matched `start-sms-verification`, which is 2FA, not outbound messaging.
- **Missing:** AWS SNS or simple email-to-SMS gateways.

## Q3

**Interviewer:** Take your two picks, `gugik-geocoding` for the 200 Polish addresses and `twilio` for the SMS reminder. Going from the catalog entry to a first successful call, which fields would you read, in what order, and what is missing for each? For example: base URL, auth header format, an example request and response, batch or rate limits, price per call, or an MCP config snippet. Where would you have to leave the catalog to fill each gap?

**Google agent:**

### 1. `gugik-geocoding` (Poland Geocoding)

**Fields to read in order:**
1. `auth` / `no_auth`: Confirm no keys are required (`true`).
2. `base_url`: `https://services.gugik.gov.pl/uug/`.
3. `call.example` / `call.method`: Check for an exact request payload.
4. `rate_limits` / `free_plan.quota`: Check batch thresholds for 200 items.

**What is missing & catalog gaps:**
- **Exact endpoint path & query params:** The search result only gives the base URL. Without calling `get_api` (or if `get_api` lacks it), I do not know whether to append `?request=GetAddress` or `/geocode`.
- **Response schema:** No sample JSON or XML structure is provided to parse coordinates or handle failed matches.
- **Batch limits:** `quota` states "no published quota." 

**Where I must leave the catalog:**  
I must fetch `docs` (`https://services.gugik.gov.pl/uug/opis.html`) via HTTP/browser to inspect the actual REST query parameters, expected response structure, and determine whether 200 sequential calls will trigger an IP block.

---

### 2. `twilio` (SMS Reminder)

**Fields to read in order:**
1. `sms.trial_limits`: Critical blocker—trial only allows pre-verified numbers and pre-approved templates (cannot send custom customer reminders).
2. `auth` / `auth_scheme`: Format for Account SID and Auth Token (HTTP Basic Auth).
3. `call.example`: The REST request format for `/Messages.json`.
4. `sms.price_pl`: Verify segment pricing ($0.0457/msg).

**What is missing & catalog gaps:**
- **Ready-to-use REST payload:** The search entry highlights a broken stdio alpha MCP rather than the canonical POST body (`To`, `From`, `Body`).
- **Country code handling:** E.164 formatting requirements are omitted.

**Where I must leave the catalog:**  
I must direct the user to Twilio's console to provision credentials and purchase an active number. If using the trial, I must leave the catalog to verify the customer's phone number before any call can succeed.

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. Based on their wording, would they make you call search_apis at the right moment and stay away from it at the wrong one? Name a concrete case where you would wrongly skip it or wrongly call it. Which exact phrases would you rewrite, and to what?

**Google agent:**

### Would they make me call it at the right moment?
Mostly yes, but the boundary logic contains serious edge-case bugs that cause both false positives and false negatives.

---

### Concrete Cases

1. **Wrongly Call (False Positive):**  
   *Task:* "Send this report to the team on Slack."  
   *Why:* The skill says: *"when the user names a service you are about to use for a batch, a message or a payment: call `get_api` first."* If I already have an active, authenticated `slack_send_message` tool connected in my runtime, this rule still aggressively commands me to inspect the catalog entry before sending a message.

2. **Wrongly Skip (False Negative):**  
   *Task:* "Convert these 50 scanned PDFs into searchable Markdown."  
   *Why:* The skill lists: *"Skip it when you can do it yourself: translating text, drawing... writing code, summarizing."* As Gemini-3.8-flash (a multimodal model with vision), I *can* read PDFs natively. I would skip the catalog, attempt inline OCR, and either exhaust my context window or time out, missing dedicated OCR/document-pipeline engines like Unstructured or AWS Textract.

---

### Exact Phrases to Rewrite

1. **Fixing False Positives on Connected Tools**  
   - *Current:* "when the user names a service... or you are about to use one for a batch, a message, a payment... call `get_api` first."  
   - *Rewrite:* "when the user names a third-party service **that is not already configured in your connected runtime**, call `get_api` first."

2. **Fixing Confusing Negation Logic**  
   - *Current:* "One quick check: if you cannot name the tool that does it, search."  
   - *Rewrite:* "Search only if no connected tool or native capability can fulfill the operation within required scale, latency, or context limits."

## Q5

**Interviewer:** What would actually stop you from using this in a real session: install friction, trust in the catalog data (given the errors you found), latency, token cost of the results, or overlap with your built-in search and connectors? Pick the one that is the real blocker, and explain what you saw that makes it decisive rather than just a nuisance.

**Google agent:**

The decisive blocker is **trust in the catalog data**. 

Latency and token overhead are manageable nuisances, but untrustworthy structured fields defeat the catalog's entire reason for existing over standard web search.

The value proposition of an API catalog for an agent is programmatic decision-making via reliable boolean filters (`has_free_tier`, `no_card`, `mcp_fit`). In the live outputs provided, these flags routinely contradicted either the reality of the services or the catalog's own payload:

1. **Hallucinated Free Tiers:** `freepik-api` was returned for `free_tier: true` despite having `has_trial: false`, `no_card: false`, and an explicit note that it is a 5-euro trial. An agent acting on this flag will hit a paywall/card prompt and fail the user's zero-budget constraint.
2. **Self-Contradicting MCP Metadata:** In the exact same Freepik JSON response, `mcp.tools` explicitly listed `"video_generate"`, while `mcp_fit` claimed `"no MCP tool named for this operation"`. In Task 3, Sinch’s `mcp_fit` matched `start-sms-verification` (a 2FA utility) for a general outbound SMS query.
3. **Ghost Operations:** Google Maps was labeled `match: exact` for geocoding under an MCP search, yet its MCP server only exposes places, weather, and routes—not geocoding.

If I cannot trust the booleans, I cannot act autonomously. I would still have to fall back to web search or scrape the raw docs to verify every claim. That makes using this catalog an extra, unreliable step rather than an accelerator.

## Q6

**Interviewer:** If you could change only three things so that you would call this catalog by default, before web search or your own knowledge, what would they be? Rank them from most to least important, and for each one say what you would do differently in a session once that change is made.

**Google agent:**

**1. Fix and enforce boolean integrity (`free_tier`, `no_card`, `mcp_fit`)**
* **The change:** Strict validation so that one-time trials never flag as `has_free_tier: true`, card requirements are enforced, and `mcp_fit` reflects exact tool names without internal contradictions.
* **What I'd do differently:** I would trust the returned candidates immediately, filtering by constraint (e.g., zero budget) and acting without falling back to web search to double-check if the service is actually free or cardless.

**2. Embed actionable REST payloads directly in search results**
* **The change:** Provide the full endpoint path, required query/body parameters, and minimal sample response schema in `search_apis` (not just base URLs or buried in `get_api`).
* **What I'd do differently:** For services like `gugik-geocoding`, I would eliminate doc-scraping turns and immediately construct a working HTTP call in the very next turn.

**3. Standardize dynamic MCP connection payloads**
* **The change:** Clearly distinguish remote, zero-install endpoints from local `stdio` packages, providing standardized connection blocks that runtime platforms can ingest dynamically.
* **What I'd do differently:** Instead of treating MCP entries as setup instructions for the human, I could emit a direct runtime tool-connection request, auto-bind the remote server (e.g., Telnyx or OpenCage), and execute the task autonomously within the session.

## Q7

**Interviewer:** Your second change asks for full endpoint paths, parameters and sample responses in `search_apis` itself rather than in `get_api`. In Q3 you also said you didn't know whether `get_api` contains the gugik endpoint path. In

**Google agent:**

It looks like your question cut off at "In...", but I see what you are pointing out: `get_api` already has a structured `call` block (as seen in the Freepik entry with `call.url`, `call.example`, and `call.response_fields`).

You are right to challenge moving all of that into `search_apis`. Bloating `search_apis` with full request and response schemas for 5–10 results would waste context tokens and raise latency. 

Here is what I actually need, clarified:

1. **Keep the two-step pattern (`search_apis` $\rightarrow$ `get_api`), but guarantee the payload:** In Q3, my uncertainty with GUGiK was whether `call` is populated for niche government or long-tail APIs, or only for popular ones (the skill text itself admits: *"Popular services also carry a minimal example request (`call`)"*). If `call` is absent for non-popular services, `get_api` still leaves me stranded. Guaranteeing that *every* entry returned as an `exact` match has a verified, runnable `call` object in `get_api` fixes that without bloating `search_apis`.
2. **Minimal breadcrumbs in `search`:** `search_apis` only needs a compact `endpoint_summary` (e.g., `POST /v1/ai/text-to-video` or `GET /uug/?address=...`) so I can validate basic protocol fit before committing a tool call to `get_api`.

Once `get_api` reliably provides full, verified `call` schemas for all catalogued endpoints—not just popular ones—the two-step flow works cleanly.
