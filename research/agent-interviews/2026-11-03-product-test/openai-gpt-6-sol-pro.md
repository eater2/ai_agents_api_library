# Product test: OpenAI agent (openai/gpt-6-sol-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the accompanying skill text. Take task 1 and walk me through what you would actually do, step by step, from the moment you receive it. At which point, if any, would you call search_apis? Where would you instead rely on web search, your own knowledge, or another tool or connector, and why?

**OpenAI agent:**

1. **Check what I can actually use.** I can write or refine the sunset prompt, but I cannot produce a video file from text by reasoning alone. I’d first check whether this deployment already has a video-generation tool or connected service. If it does and its quota covers the job, I’d use that rather than add a catalog lookup.

2. **If not, call `search_apis`.** I’d search for text-to-video with a lasting free tier and no-card preference. That is the point where this catalog helps: finding a possible way to perform an operation I cannot perform myself. I would not treat its ranking as proof that the clip is free or can be exactly five seconds.

3. **Inspect the candidate, then verify the decisive details.** I’d call `get_api` for Freepik/Magnific, then check its current video-model documentation and pricing—by web search or browsing if available. The supplied example requests **six seconds**, not five; “~€5 of credits” does not establish that this model fits that balance, and `no_card: false` is a concern for a zero-budget user. The results also contradict themselves: `video_generate` appears in the MCP tool list, yet `mcp_fit` says there is no video tool. I’d verify the actual tool and its inputs rather than assume either field is right. Hugging Face’s $0.10/month is likewise not evidence that one clip is affordable.

4. **Act only if access and cost are clear.** If an already connected tool or verified free option can make the requested clip, I’d use it. Otherwise I’d say I cannot make it here for zero cost, and offer a ready-to-use prompt—not present a trial or an unverified price as a solution.

## Q2

**Interviewer:** Now look at the actual search results for all three tasks. For each task, which result, if any, would you act on, and why that one? Which results are irrelevant, ranked too high or too low, or missing entirely?

**OpenAI agent:**

### 1. Five-second video, no budget
**I would not act on either result yet.** Freepik/Magnific is the closest fit, but its example generates **six seconds**, the quoted credits may not cover that model, and the entry says a card may be required. Its `mcp_fit` also contradicts its listed `video_generate` tool. Hugging Face is ranked too high for this task: it merely lists video inference, with no demonstrated generation call, and $0.10/month may be insufficient. What’s missing is a verified, no-card route that can produce **five seconds** within a lasting free allowance. I’d check current docs and any already-connected generator before promising a clip.

### 2. Geocode 200 Polish addresses
**I’d investigate GUGiK first**: it is purpose-built for Polish addresses and needs no key. But “no published quota” is not permission to submit 200 requests; I’d check its usage rules and response format, test a few addresses, then rate-limit the batch if permitted. **LocationIQ** is the practical fallback: its stated 5,000/day and 2/s limits cover 200, subject to its terms and account setup. Photon’s public demo is ranked too high for a batch. Google needs setup and its listed MCP tools do not geocode; OpenCage’s free plan is described as testing-only. The search should have used `volume: "bulk"`.

### 3. Send a customer SMS
**I would send nothing from these results alone.** I’d need the destination country, customer consent, authorized message, and a provisioned sender/account. For a real reminder, I’d favor an already-connected production SMS provider; among these, **Twilio’s REST API** is a plausible choice once those details and cost are checked. Textbelt’s shared one-per-day key is ranked too high for customer messaging. Twilio, Sinch, Telnyx and Vonage trials have recipient restrictions, so none is a dependable free production route. Sinch’s `mcp_fit` points to *verification*, not reminder sending; Telnyx’s generic API-invocation tool may work despite being marked no fit.

## Q3

**Interviewer:** Take LocationIQ for the 200 Polish addresses. Suppose `get_api` has just returned its full entry. Which exact fields would you read, in what order, to make a correct first request without opening the provider's docs? Which of those fields are missing or not specific enough today, for example base URL, auth header or query-parameter format, a complete example request and response, rate-limit behaviour on errors, price per call, terms for batch use, or an MCP config snippet?

**OpenAI agent:**

I haven’t seen LocationIQ’s **full** `get_api` entry, so I can’t claim its example or auth fields are present. I’d read them in this order:

1. **`call.operation`, `call.method`, `call.url`, `call.example`**: does the example forward-geocode a street address, and does it show every required query parameter and where the key goes?
2. **`auth_scheme` / `auth_hint` and `base_url`**: confirm the credential placement and that the example’s endpoint matches the current base URL. I would not infer an auth header from `auth: "api_key"`.
3. **`call.response_fields` and any response example**: identify the latitude/longitude fields and how to recognize zero or ambiguous matches.
4. **`rate_limits`, `free_plan`, `unit_price`, `notes` / data-policy or terms fields**: check that 200 requests are permitted, how quickly to send them, whether errors count against quota, and whether use or storage of the results is restricted.
5. **`verified`, source URLs and `link_check`**: assess how much confidence to put in those instructions. **`mcp.config`** matters only if there is an operational MCP server; the search result says LocationIQ has none.

From the *shown search result*, I have a base URL and a claimed 5,000/day, 2/s, 60/min free allowance, but **not** a request I could safely construct: no key-placement or query-parameter format, complete request/response example, error and retry behavior, per-call price, or clear batch-use terms. An MCP config snippet is not needed for its REST API. If `get_api` does not supply the request and response details, I’d open LocationIQ’s docs before making even the first test call.

## Q4

**Interviewer:** Look at the descriptions for `search_apis`, `get_api`, `get_reviews` and `list_categories`, and at the skill text. Would they trigger a call at the right moment, such as when you lack a built-in capability, and keep you from calling them at the wrong one, such as when a connector already exists or the user names a specific provider? Quote any phrases you would change, and give the wording you would use instead.

**OpenAI agent:**

**The skill gives a useful trigger, but I would not rely on it to fire in this deployment:** it is labeled a Claude skill, not necessarily an instruction my platform loads. The MCP tool descriptions mostly explain *what the tools return*, not *when to use them*. I’d change these phrases:

- **“if you cannot name the tool that does it, search.”**  
  → “First check built-in and connected tools. Search only when none can perform the operation within the task’s limits, or when the user asks you to compare providers.” Not remembering a tool’s name is not enough.

- **“when the user names a service … call `get_api` first.”**  
  → “If the user names a provider, use their authorized, already-connected tool when it fits. Look up the provider when its capabilities, limits, price or terms matter and are unknown—especially before a batch or third-party action.” Also, `get_api` requires a catalog **id**; the skill should say to find that id first if necessary.

- **“Skip it when a built-in or connected tool already does the job”** conflicts with the unconditional named-provider rule.  
  → “Skip catalog lookup for a suitable existing connector unless a material provider-specific fact needs checking.”

- In `search_apis`, **“exact = … example call or an MCP tool performs it”** overstates the evidence.  
  → “`exact` means catalog evidence names the operation; verify inputs, endpoint, limits and MCP-tool availability before use.”

- In `get_api`, **“Full entry”** suggests completeness.  
  → “Catalogued details; fields may be absent or insufficient to construct a safe request.”

`get_reviews` and `list_categories` are appropriately optional. I’d explicitly say reviews cannot establish task fit, and categories need not be listed before a clear operation search.

## Q5

**Interviewer:** What would actually stop you from using this catalog in practice: installation or setup friction, trust in its accuracy, latency, token cost of the results, or overlap with your built-in web search and existing connectors? Which one is the real blocker, the one that would still stop you even if the others were fixed?

**OpenAI agent:**

**Trust in the results is the real blocker to relying on this catalog for action.** Even if the MCP server were connected, fast, and returned compact results—and even where I had no existing connector—I would still have to verify decisive claims before spending money, running a batch, or contacting a customer.

The examples show why: Freepik lists `video_generate` but says there is no matching MCP tool; its example makes six seconds when the user needs five. LocationIQ’s search result gives a quota but not enough request detail or batch-use terms to make a safe call. Sinch is marked as an SMS fit while `mcp_fit` points to a *verification* tool. A host being reachable, even with a 404, does not prove the operation works.

The other factors matter less. **Setup** is a hard stop if the MCP tools are not connected to my deployment, but it is fixable. **Latency and token cost** would make me use it selectively. **Overlap** means I would skip it when an existing connector already handles the task, but I would still want discovery for genuinely missing capabilities.

So I might use the catalog to find candidates. I would not use its ranking or “last checked” label as authorization to call one without checking the task-specific endpoint, limits and terms.

## Q6

**Interviewer:** If we could change only three things about the catalog, the tools, or the skill so that you would use it by default whenever you lack a capability, what would they be? Rank them from most to least important, and for each, describe the observable change that would let you act on a result without first opening the provider's docs.

**OpenAI agent:**

1. **Make results operation-specific and testable.** For each claimed fit, provide a complete request, credential placement, required parameters, sample success and error responses, and the exact MCP tool schema if applicable. Validate read-only calls against the live service; use provider-published schemas or sandboxes for paid or side-effecting calls. I could act without opening docs when, for example, the video entry shows a supported **five-second** request and the geocoding entry shows exactly how to extract coordinates. Contradictions such as Freepik’s `video_generate`/`mcp_fit` mismatch should fail validation, not reach me.

2. **Attach sourced, task-relevant limits and permission checks.** Show whether 200-address batches are allowed, how 429s and failed calls affect quota, whether results may be stored, and the estimated cost for the requested volume—not just a generic free-tier label. For SMS, show destination-specific sender and trial restrictions. Each claim needs a source and check date; unknowns should be explicit. Then I could proceed within verified limits **after** obtaining the user’s authorization and credentials, rather than opening docs to resolve basic eligibility.

3. **Make the lookup available at the decision point, with short results.** Expose the MCP tools in my actual deployment and make the instruction: check existing connectors first; if none fits, search; retrieve one detailed entry only when needed. Return a compact action summary with links to the underlying evidence. The observable change is that I can find and use a validated recipe without setup or a large search-result dump.

None of these would remove the need for consent before sending an SMS or approval before an unexpected charge.
