# Product test: DeepSeek agent (deepseek/deepseek-v4-pro)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the accompanying skill text. Take task 1 and walk me through what you would actually do, step by step, from the moment you receive it. At which point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else? Please describe your real behavior, not what you think we'd like to hear.

**DeepSeek agent:**

I would call `search_apis` immediately after confirming I have no built-in video generation tool. The user has no budget, so I’d set `free_tier: true` and `category: "video-generation"` with a query like `"text to video"`. 

Looking at the returned results, none are actually text-to-video generation: Google Gemini generates images and text (not video), Mux does video streaming/encoding, Akool does face-swap/talking avatars, and Creatomate renders from templates. They don’t match the request. I’d notice this and try a broader query or fetch the full `video-generation` category JSON via the static URL to see if I missed something like RunwayML or Pika. If the catalog still comes up empty, I’d tell the user the catalog has no verified free text-to-video API, and I’d refrain from making up a service. 

I might fall back to a web search tool if available, but the skill explicitly says to use the catalog first and to confirm pricing in docs—so I’d be cautious about recommending an unverified service. The catalog’s search results here are weak; they’d push me toward a dead end, and I’d likely need external search to actually help the user.

## Q2

**Interviewer:** You've covered task 1's results. Now look at the real search results for tasks 2 and 3. For each, would you act on what came back, and which specific result would you pick? Is anything irrelevant, ranked too high or too low, or missing? For task 1, is there a service you expected to see that should have been there?

**DeepSeek agent:**

**Task 2 (geocode 200 addresses in Poland)**  
I’d pick **Google Maps Platform** – $200 free monthly credit, official MCP, and 200 geocodes cost well under $1. **Nominatim** is tempting because it’s keyless, but the catalog itself warns “bulk use prohibited” on the public server; I’d flag that to the user. **Geoapify** is a solid alternative with a generous free tier. The ranking is off: **IP2Location.io** is for IP geolocation, not street addresses, and shouldn’t appear at all. **Esri ArcGIS** is geocoding but listed under the wrong category (architecture-cad-bim), which is confusing. I’d ignore those two.

**Task 3 (send SMS)**  
Only **Twilio** is actually SMS. **LINE Messaging API**, **WhatsApp Business**, and **Discord** are messaging platforms, not SMS to phone numbers – they’re irrelevant noise. The search should have filtered more precisely for “SMS” rather than returning any communication service. I’d pick Twilio, note its trial credit, and mention that it’s the only real match. Missing services like Plivo or MessageBird would have been useful, but Twilio is sufficient.

**Task 1 missing service**  
I expected a text-to-video API like **RunwayML**, **Pika**, or **Luma AI** to appear in the video-generation category. The search returned none, only template renderers and a face-swap tool, which is a gap. If the catalog doesn’t cover free text-to-video generation, I’d tell the user it’s not available and fall back to external search.

## Q3

**Interviewer:** Take the result you picked for task 3, Twilio, and imagine you now have to send the first SMS. Which exact fields from `get_api` would you read, in what order? What would you still have to look up elsewhere before you could make a working call, for example the base URL, auth header format, an example request, price per message, rate limits, trial restrictions, or an MCP config snippet?

**DeepSeek agent:**

I’d open `get_api("twilio")` and read in this order:

1. **`auth_hint`** – to see exactly how to send the credential (likely `Authorization: Basic base64(AccountSid:AuthToken)` or `-u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN`). That tells me the header format, but not where to get the Account SID and Auth Token from the Twilio Console.
2. **`docs`** – the link to the full API reference. I’d need it immediately for the base URL (`https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`), the required POST body fields (`To`, `From`, `Body`), and the trial restrictions (a verified destination number is required with trial credit; the `From` must be a Twilio number or messaging service SID).
3. **`mcp.url`** – the official MCP server address; I’d check its README for a config snippet the user can paste into their MCP settings.

**What I still must look up elsewhere:**

- **Base URL and endpoint** – the catalog doesn’t include these.
- **Request example** – body structure, required parameters, and encoding.
- **Pricing per SMS** – especially to Poland; the catalog only says “free trial credit,” not how much or what it covers. Twilio’s per‑message pricing varies by country and must be checked on their pricing page.
- **Trial restrictions** – trial accounts can only send to verified numbers; this is a critical detail not in the catalog.
- **Rate limits** – not provided.
- **MCP config snippet** – the catalog gives the MCP endpoint URL, but the user needs the full `mcpServers` JSON block with environment variables.

I’d present the `auth_hint` and the docs link, then tell the user to confirm the endpoint, body format, and pricing directly in the Twilio docs before I attempt a call. The catalog is a good shortlist, but it’s not enough to make a working call without external reference.

## Q4

**Interviewer:** Now look at the tool descriptions and the skill text themselves. Would that wording make you reach for search_apis at the right moment, and would it ever make you call it when you shouldn't? Quote the specific phrases that trigger or fail to trigger your use, and give the exact wording you would change.

**DeepSeek agent:**

## What would make me reach for `search_apis` at the right moment

The skill’s **“When to use”** section is clear and well‑scoped:

> *“Use when a task needs a capability you don't have built in or connected, e.g. 'make a 5‑second video', 'geocode these addresses' or 'send this as an SMS'.”*  
> *“The user asks which service, API or MCP server to use for something.”*

Those examples match the test tasks exactly, so I’d call `search_apis` immediately, before falling back to web search. The **“How to look things up”** rule reinforces that:

> *“If the `ai-agents-api-library` MCP tools are available, use them”*

This clearly prioritises the catalog over a generic web search when the MCP server is connected.

The `search_apis` tool description itself repeats the trigger:

> *“Use when a task needs an external capability you don't have.”*

That’s sufficient, but it’s missing the **skip‑if‑connected** guard. The skill text says *“Skip it when a connected tool already does the job,”* but the tool description doesn’t echo that. If I saw only the tool description (e.g., in a quick‑reference panel), I might call it even when I already have a working geocoding or SMS tool, leading to an unnecessary lookup.

## What might make me call it when I shouldn’t

The **category filter** example in the skill — *“Category id from list_categories, e.g. 'video‑generation'”* — assumes I already know the category ID. In practice I’d often guess, and if I guess wrong (or the category doesn’t contain the right services, as in Task 1), I’d get poor results. The skill says *“list_categories when you are unsure what exists,”* but that phrase is too weak: I’d rarely think I’m “

## Q5

**Interviewer:** Your answer cut off mid-sentence at "I'd rarely think I'm". Please finish that point: when would you actually call `list_categories`, and what happens if you guess a wrong category id? Then give the exact replacement wording you would put in the `search_apis` description and in the skill's "When to use" section.

**DeepSeek agent:**

I’d rarely think I’m unsure about what categories exist because I can infer them from the task: “video-generation” for a video request, “maps-geo-weather” for geocoding. The problem is that guessing a wrong category id silently hides the right services—like Task 1 where the “video-generation” category contained no text-to-video APIs, so the search returned irrelevant results and I’d have wasted a call. I’d rather search without a category first, then use `list_categories` only if the results are too noisy. The skill’s “list_categories when you are unsure what exists” is too passive; I’d rarely think I’m “unsure” and would just guess, leading to misses.

**Exact replacement wording I’d put in the `search_apis` tool description:**

> `Search a verified catalog of 300+ third-party APIs and MCP servers for AI agents. Use when a task needs an external capability you don’t have. Skip if a connected tool already does the job. Search without a category filter first; use category only to narrow down after you’ve seen what’s available, and call list_categories to see valid ids.`

**Exact replacement wording for the skill’s “When to use” section (the bullet list):**

> - The task needs a capability you don’t have built in or connected, e.g. “make a 5‑second video”, “geocode these addresses” or “send this as an SMS”. Always search without a category filter first; add a category only if the initial results are too broad and you’ve confirmed the category id via `list_categories`.  
> - The user asks which service, API or MCP server to use for something.  
> - You are choosing which MCP server to suggest the user connect.  
> 
> Skip it when a connected tool already does the job.

## Q6

**Interviewer:** What would actually stop you from using this in a real session: install friction, trust in the catalog's data, latency, token cost of the results, or overlap with your built-in web search and existing connectors? Pick the one that is the real blocker and explain what specifically happens in your workflow when you hit it.

**DeepSeek agent:**

**Overlap with built-in web search is the real blocker.**

Here’s what happens in my workflow: I receive “geocode 200 addresses in Poland.” I know I don’t have a geocoding tool connected. I now have two paths:

- **Path A**: Call `search_apis` → get 5 results → call `get_api` on the best one → still need to open `docs` to confirm the base URL, pricing for Poland, and rate limits → then present to the user.
- **Path B**: Web search “geocoding API free tier bulk 2026” → get current results, pricing pages, and docs directly in one call → present to the user.

Path B is faster, gives me current information (not verified months ago), and doesn’t depend on a catalog that already showed gaps (no text-to-video APIs in Task 1, IP geolocation mixed into geocoding in Task 2, messaging apps returned for an SMS query in Task 3).

The catalog’s value proposition is curation and verification, but when the results are incomplete or miscategorised, that value erodes. I’d trust a web search over a catalog that missed RunwayML and returned Discord for an SMS task. The extra `search_apis` → `get_api` → `docs` chain adds latency and tokens without enough unique payoff. If I already have web search, I’d skip the catalog entirely and go straight to the source.

## Q7

**Interviewer:** If we could change only three things so that you would call this by default instead of going straight to web search, what would they be? Rank them 1 to 3, and for your top pick, describe exactly what `search_apis` or `get_api` would need to return in a single call for you to skip Path B.

**DeepSeek agent:**

**1. `get_api` must return everything needed to make a working call in one response.**  
Right now I have to open `docs` for the base URL, endpoint path, request body schema, a working example, exact auth header format, current per-unit pricing, and trial restrictions. If `get_api` included:

- `base_url`: `"https://api.twilio.com/2010-04-01"`  
- `endpoint`: `"/Accounts/{AccountSid}/Messages.json"`  
- `method`: `"POST"`  
- `auth_header`: `"Authorization: Basic base64(ACCOUNT_SID:AUTH_TOKEN)"`  
- `request_example`: a minimal JSON body (`To`, `From`, `Body`)  
- `free_tier_details`: `"Trial: $15 credit, ~150 SMS to US numbers; must verify destination number first"`  
- `pricing`: `"$0.0079/SMS to US, $0.05/SMS to Poland (pay-as-you-go)"`  
- `rate_limit`: `"100 messages per second per account"`  

…then I’d have no reason to leave the catalog. I’d present the service, the exact cost, and the code snippet to the user immediately. This single change closes the gap that currently forces me to Path B.

**2. Search relevance must be near-perfect for the top 3 results.**  
Task 2 mixed IP geolocation into geocoding; Task 3 returned Discord and WhatsApp for an SMS query. I need `search_apis` to understand that “geocode addresses” ≠ IP lookup, and “send SMS” ≠ chat app. A semantic or keyword‑tuned ranking that puts the exact match first—and drops irrelevant categories—would build trust. If the top 3 results consistently nail the task, I’ll stop double‑checking with web search.

**3. A freshness SLA I can rely on without checking `verified` dates.**  
If the catalog guaranteed “every entry re‑verified within 7 days” and I saw that in the tool description, I’d trust the pricing and endpoint details. Right now the `verified` field is a point‑in‑time snapshot; I still feel I must confirm in `docs` because APIs change. A visible recency promise removes that reflex.

## Q8

**Interviewer:** Suppose `get_api` returned every field you listed for Twilio, but the entry showed `verified: 2025-11-02`, about three months old. In that session, would you send the SMS using the catalog's endpoint and pricing directly, or would you still open the docs or run a web search first? What is the oldest `verified` date you would act on without checking?

**DeepSeek agent:**

I would still open the docs. `verified: 2025-11-02` is ten months old (assuming the session date is around the earlier entries’ 2026‑09‑24). The catalog’s own skill says *“confirm limits and pricing in `docs` before relying on them”* and *“The API may have changed since the `verified` date.”* For a paid, delivery‑critical call like an SMS, I won’t trust stale pricing or endpoint details—a changed base URL or auth scheme would cause a silent failure or unexpected cost.

The oldest `verified` date I’d act on without checking is **two weeks**. If the entry was verified within the last 14 days, I’d assume the pricing, endpoint, and auth are still accurate and make the call directly. Beyond that, I’d always open the docs to confirm the exact request shape and current per‑message cost for the destination country. No number of extra fields replaces recency; a three‑month‑old verified date means I still take Path B.
