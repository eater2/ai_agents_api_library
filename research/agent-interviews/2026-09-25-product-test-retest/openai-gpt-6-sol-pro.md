# Product test: OpenAI agent (openai/gpt-6-sol-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through what you would actually do, step by step, from receiving the task to making a working call. At which point, if any, would you call search_apis? Or would you use web search, your own knowledge or something else instead? Why?

**OpenAI agent:**

1. I’d first check whether this session has a connected video-generation tool or a suitable local model with compute available. I can write the sunset prompt myself, but I can’t produce a video file just by writing it. I wouldn’t use web search or a catalog if a connected tool already handles the job at no cost to the user.

2. If not, I’d call `search_apis` for **text-to-video**, filtering for free use without a card. That is the point where this catalog helps: finding possible services, not making the video. I’d inspect `get_api` for candidates and verify the current limits and prices in vendor documentation.

3. I would **not call either result shown yet**. Freepik/Magnific is marked an exact match, but its supplied example requires an *input image*—it is image-to-video, not a working call for this text-only request. Its credits may also require a card or be insufficient. Hugging Face’s listed MCP tools don’t generate video, and $0.10/month does not establish that a five-second clip is affordable.

4. I’d retry in `video-generation`, then use web search if the catalog still lacks a verified fit. For a genuine no-cost option, I’d get the user to connect or provision it, confirm that this specific generation fits the free quota, use its documented **text-to-video** request, poll any asynchronous job, and return the file. Without such an option and credentials, I’d say I can’t make the clip at zero budget—not substitute an unverified call.

## Q2

**Interviewer:** You already judged task 1's results: Freepik/Magnific flagged "exact match" but image-to-video only, and Hugging Face didn't fit. Now look at the real results for tasks 2 and 3. For each, would you act on them, which result would you pick, and what is irrelevant, badly ranked or missing?

**OpenAI agent:**

### Task 2 — geocode 200 Polish addresses

I’d use these results as a shortlist, **not start the batch yet**. If the user has no existing geocoding provider, I’d pick **LocationIQ’s REST API** provisionally: it explicitly geocodes addresses, needs no card, and its stated 5,000/day quota accommodates 200 requests. I’d check its current terms and Poland coverage, ask the user to provision a key, then rate-limit the calls, constrain results to Poland, and return coordinates alongside match quality and any ambiguous or unmatched addresses.

The ranking is weak for this job. **Nominatim’s public server should not be treated as the convenient no-key choice**: its entry discourages bulk geocoding. OpenCage’s free plan is described as testing-only, so I would not assume it permits a production batch. Esri may fit but says a card is required; Google’s listed MCP tools do **not** include geocoding. Esri’s apparent MCP endpoint is a documentation URL marked “derived,” not a connection I’d trust without checking.

What’s missing is whether these addresses may be sent to a third party, whether this is production use, and the required accuracy. I’d also prefer an already-connected, authorized geocoder over creating another account.

### Task 3 — send an SMS reminder

I **would not send from these search results alone**. I need the message text, destination country, confirmation that this customer may receive the reminder, authorization to incur a charge, and an SMS-capable account connected to this session.

If **Bird is already connected and authorized**, it is my first pick here: its listed hosted MCP has an explicit `sms_send` tool. Otherwise I’d choose based on the user’s existing provider, sender setup, destination-country support and current price—not the ranking. Twilio’s REST API is a plausible alternative, but the displayed remote MCP is **docs-only**, so it cannot send the SMS; its trial also restricts recipients. Sinch and Plivo list installable repositories, not ready-to-call hosted endpoints.

AWS is badly ranked for a simple reminder: `aws___run_script` is broad access, not a dedicated SMS send tool. The US price snippets are irrelevant without the destination country. The results also omit crucial operational checks: registered sender/origination requirements, opt-outs, trial-recipient restrictions and delivery-status handling. I’d confirm those in provider docs before requesting final approval and sending **one** message.

## Q3

**Interviewer:** Take LocationIQ for task 2 and Bird for task 3. If you called `get_api` on each, which exact fields would you read, in what order, to make one working call without leaving the tool? For each field, say whether the current entry has it, has it but you wouldn't trust it, or lacks it. Consider base URL, auth header format, an example request, rate limits, price per call, and an MCP config snippet.

**OpenAI agent:**

I can’t inspect the actual `get_api` entries for LocationIQ or Bird here: only their **search results** are supplied. So “lacks” below means *lacks in the supplied result*, not necessarily in `get_api`. My read order would be:

| Field, in order | LocationIQ — one geocode | Bird — one SMS |
|---|---|---|
| **1. Base URL and operation** | **Has, but verify:** `https://us1.locationiq.com/v1` and geocoding are listed; no specific request URL. | **Has, but verify:** US/EU REST base URLs and SMS are listed; no specific send URL. |
| **2. Auth format** | **Lacks:** says API key, but not where to put it. | **Lacks:** says API key/OAuth, but not which credential or how to send it. |
| **3. Example request** | **Lacks:** no method, path, parameters or response mapping. | **Lacks:** no REST example or `sms_send` input schema. |
| **4. Rate limits** | **Has, but verify:** 2/s and 60/min on the free plan; I’d obey the lower effective limit. | **Lacks** in the supplied result. |
| **5. Price per call** | **Lacks:** a free quota is listed, not a unit price. | **Lacks:** “paid only” gives no applicable per-message price for the destination. |
| **6. MCP config** | **Lacks:** no MCP server listed; use REST. | **Has, but wouldn’t trust as sufficient:** a hosted URL is listed, but its config is marked `derived` and gives no authentication setup. |

I’d use `get_api` to fill those gaps, particularly `auth_scheme`, `call`, `rate_limits`, `unit_price`, and `mcp.config`. **Neither supplied result is enough to construct a working call without leaving the catalog**, and neither provides credentials. For Bird, connecting an MCP endpoint still wouldn’t reveal the `sms_send` arguments until I could inspect that server’s live tool schema.

## Q4

**Interviewer:** Q4: Now look at the tool descriptions and the skill text themselves. Would that wording make you call `search_apis` at the right moment, such as when a task needs a service you don't have connected, and keep you from calling it at the wrong one, such as when a connected tool already handles the job? Quote the specific phrases that would misfire, and say what you'd change them to.

**OpenAI agent:**

Mostly yes: “**Skip it when a built-in or connected tool already does the job**” gives me the right first check. But several phrases could still trigger an unnecessary search or make me act on a poor result:

- “**The task needs an external service**” is too broad: a connected tool *is* an external service. Change to: “The task needs a capability unavailable through the model, built-in tools, **or currently connected tools**.”
- “**when your own attempt at a call failed (403, rate limit, unsupported format)**” suggests switching vendors after any error. A 403 may just mean missing permission. Change to: “First diagnose the failure; search for an alternative only if the existing service cannot be made usable within the user’s constraints.”
- “**`match`: exact means one of its `operations` is the requested operation**” overstates what the result proves—as Freepik’s image-to-video example demonstrates. Change to: “`exact` is a search label; verify that the documented endpoint or MCP tool accepts the user’s actual inputs.”
- “**`no_auth: true`: callable now**” ignores network access, terms and batch restrictions. Change to: “No credential required; check access and permitted use before calling.”
- “**A remote endpoint … is connected once**” blurs *hosted* with *connected and authorized in this session*. Change to: “A hosted endpoint needs no installation, but may still require connection, authentication and a suitable operation tool.”
- “**Start from `call.example` when present**” needs a qualifier: “Only if its operation and required inputs match the task; otherwise find the correct vendor example.”

Those changes would keep the catalog a discovery aid rather than permission to call the first “exact” hit.

## Q5

**Interviewer:** What would actually stop you from using this catalog in a real session: install friction, trust in the data, latency, token cost of results, or overlap with your built-in web search and connectors? Pick the one that is the real blocker, and describe the moment in a task where it would make you skip the catalog and go straight to web search or your own knowledge.

**OpenAI agent:**

**Trust in the actionable data** is the blocker. Installation, latency and token cost matter less if a result reliably gets me to a working call. These examples do not: Freepik is labelled “exact” for text-to-video but supplies an image-to-video request; Google’s geocoding result advertises an MCP whose listed tools don’t geocode; Bird’s MCP configuration is marked `derived`.

The moment I’d skip the catalog is **when the next step must be a specific, working request**—for example, the user has approved sending an SMS through Bird and I need the current `sms_send` arguments and authentication procedure. I’d inspect a Bird connector already available in the session, or go straight to Bird’s documentation via web search. I would not route through `search_apis` merely to get a plausible listing I must verify elsewhere.

I might still use the catalog earlier, when I genuinely need a shortlist of providers I don’t know. I wouldn’t use it as the authority for endpoints, prices, permissions or whether an MCP tool performs the operation.

## Q6

**Interviewer:** If you could change only three things so that you would call this catalog by default, before reaching for web search or your own knowledge, what would they be? Rank them, and for the top one, say what a result would have to contain or prove for you to act on it without checking the vendor docs.

**OpenAI agent:**

I’d make it my **default discovery step when no built-in or connected tool can do the job**—not before using a tool I already have.

1. **Make results executable and verifiable, not just searchable.** An “exact” result should identify the specific REST operation or live MCP tool, its required inputs, auth, response, and a tested example for that operation. For me to act **without opening vendor docs**, it would also need current, vendor-sourced evidence for applicable price, quota, terms and geographic restrictions—not merely a recent link check or an uptime probe. A five-second *text-to-video* request must have a tested text-to-video example. If any of that evidence is missing, I’d still check the vendor. Sending an SMS would additionally require the user’s authorization, regardless of catalog quality.

2. **Rank for the actual job, not a capability label.** Filter on input type, destination country, volume, production-versus-testing rights, budget, and whether the listed MCP tool actually performs the operation. Put Nominatim below bulk-permitted geocoders for 200 addresses; don’t promote a docs-only MCP for sending SMS.

3. **Show what I can use in this session.** Distinguish “vendor hosts an MCP” from “this MCP is connected and authenticated here.” Return a short result with the decisive fields and a clear path to connect or provision credentials.

Until then, I’d use the catalog for shortlists, but go to a live connector or vendor docs for the working call.
