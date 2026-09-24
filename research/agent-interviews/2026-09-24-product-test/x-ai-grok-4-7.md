# Product test: xAI agent (x-ai/grok-4.7)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-24

## Q1

**Interviewer:** Here are our tool definitions and the skill. Take task 1 and walk me through what you would actually do to complete it, step by step. At any point, would you call search_apis? If so, at exactly which step, and what would you pass to it? If not, what would you use instead (web search, your own knowledge, something else), and why?

**xAI agent:**

I would not call `search_apis` for this, and I would not use the results you got.

1. Check connected tools. I have none that render video, and I cannot make the clip myself.
2. The need is text-to-video, five seconds, no spend. I already know the real set: Veo, Runway, Luma, Kling, fal.ai, Replicate. Lasting free tiers are rare; most are trial credits. “No budget” may mean this cannot be finished via API.
3. Your live search is wrong. Gemini is text/image, and `get_api` says its MCP only searches docs. Mux encodes and streams existing video. Akool is face-swap and avatars. Creatomate fills templates. Voyage is embeddings. None make a sunset from a prompt. That ranking is enough that I would not trust the catalog here.
4. I would web-search current text-to-video APIs, open their docs, and confirm whether a free call still exists before naming two options. If I were forced to use the catalog, I would pass `category: "video-generation"` and drop anything whose `what` is not generation — then still verify in docs, not treat the shortlist as truth.
5. I would not invent an endpoint, ask for a key in chat, or tell the user Gemini or Mux can do this.

## Q2

**Interviewer:** Now look at the real search results for tasks 2 and 3. For each one, would you act on the results? Which result, if any, would you pick? Name anything that is irrelevant, ranked too high or too low, or missing that you would have expected to see. And for task 1: is the problem that the right APIs aren't in the catalog at all, or that they're there but ranked below Gemini, Mux and Akool? What in the results tells you which it is?

**xAI agent:**

**Task 2.** I would use the list, then discard half of it. I would pick Geoapify: real address geocoding, about 3,000 credits/day, no card, enough for 200 Polish addresses. Google Maps is the other real option ($200 monthly credit, official MCP), but it usually needs a billing account. I would not use the public Nominatim server: the entry itself says bulk use is prohibited and the cap is 1 request/second, so `no_auth` is a trap here. IP2Location is IP and WHOIS lookup, not street addresses, and it is ranked too high. Esri can geocode but is filed under architecture-CAD. Missing names I would have expected: OpenCage, LocationIQ, Mapbox, HERE, Photon. I would confirm Poland coverage and per-request credit cost in Geoapify’s docs before asking for a key.

**Task 3.** I would act on Twilio only, with Vonage as the alternative. Both actually send SMS. LINE is ranked first and is not SMS. WhatsApp and Discord are different channels and do not satisfy “text this phone number.” Trial credit is not a free tier; Twilio trial numbers are restricted. Missing: Telnyx, Plivo, Sinch, AWS SNS.

**Task 1.** The results do not show the right APIs ranked below Gemini, Mux, and Akool. They are absent from the list. The call used the default limit of 10 and returned 5, so nothing was cut off underneath. That does not prove they are missing from the whole catalog — `free_tier: true` may have excluded them — but it does prove this query did not find them. What the list does prove is bad ranking: embeddings, a video CDN, and face-swap beat every actual text-to-video service, because no text-to-video service is present at all.

## Q3

**Interviewer:** You picked Geoapify for task 2. Suppose you call `get_api` on it next. Which exact fields would you need to go from that entry to a first working request for one Polish address, without opening Geoapify's docs? Examples might be base URL, auth parameter or header format, an example request, credit cost per call, rate limit, or country coverage. Which of those does the current entry give you, and which ones would still send you to the docs?

**xAI agent:**

I have not called `get_api` on Geoapify. The search snippet plus the only real `get_api` payload (Gemini) show what an entry contains. That is not enough for a first working request.

I would need, at minimum: base URL and geocode path, the exact key placement (`apiKey` query vs header), the address parameter and a Poland filter, one example request, and where latitude/longitude sit in the response. Credit cost per call, rate limit, and Poland coverage matter before a 200-address run, but not for a single test call.

The search result gives `auth: api_key`, a prose free tier (“3,000 credits/day”), and a docs URL. No endpoint, no parameter names, no example. `get_api` adds `auth_hint`, `homepage`, `sdk`, `openapi`, `llms_txt`, and `notes`. `auth_hint` might name the header or query key, as it did for Gemini. It is not a request. `openapi` and `llms.txt` are links; Gemini’s OpenAPI was null. A link is not the spec. Notes are free text and not a contract.

So every field required to form the HTTP call would still send me to Geoapify’s docs, or to an OpenAPI document if one is actually published. I would not invent `https://api.geoapify.com/v1/geocode/search` from memory and call that “from the entry.”

## Q4

**Interviewer:** Q4: Now read the `search_apis` description and the skill text as you would at the start of a task. Would that wording make you call the tool at the right moment, for example before a web search when a user needs an external API, and keep you from calling it at the wrong moment? Point to the specific phrases that pull you toward or away from it, and say what you would add, cut, or reword.

**xAI agent:**

The wording would make me call `search_apis` before a web search for all three tasks. It would not reliably stop a wrong call.

Pull toward it: the skill description says “Use when a task needs an external service,” and the examples are exactly “make a 5-second video,” “geocode these addresses,” and “send this as an SMS.” “If the MCP tools are available, use them” is an order, not a suggestion. The tool description repeats “Use when a task needs an external capability you don’t have.” I would follow that.

Pull away, and these are the good lines: “Skip it when a connected tool already does the job.” “The catalog is a shortlist, not the source of truth.” “Skip entries with `stale: true`.”

What still pulls me wrong: “verified catalog” overclaims. Link-checked is not relevance-checked, and that word is why I would trust a top hit. Step 3, “`get_reviews` … before recommending,” forces a SourceForge call that does not tell me whether the API does the job. “Prefer `no_auth: true`” would have sent me to Nominatim for a bulk geocode the entry itself forbids.

I would reword the tool description to: “Shortlist of third-party APIs. Match each result’s `what` to the capability before recommending; ranking is not proof of fit.” Cut `get_reviews` from the required steps. Add: if the top `what` lines do not do the requested verb, do not offer them — retry with `category`, then web-search. And: do not prefer `no_auth` when the free-tier note prohibits the workload.

## Q5

**Interviewer:** What would actually stop you from using this in a real session: install friction, trust in the results, latency, token cost of the responses, or overlap with your built-in web search or connectors? Of these, which one is the real blocker, the one that would still keep you from using it even if the others were fixed?

**xAI agent:**

Trust in the results. That is the blocker that survives the others being fixed.

Install is not it. The server needs no key, and the skill already has a no-auth GitHub fallback. Latency and token cost are not it either: these payloads are small, and I have no timing evidence. Overlap with web search is real but secondary. A catalog I trusted, with the right service on top plus auth, free-tier limits, and a docs link, would still be a faster first lookup than searching for “SMS API” and reading five homepages. I would use that version for categories I do not already know.

I would not use this one. Task 1’s top five cannot make a video from a prompt, and the list ended there, so nothing better was waiting underneath. Task 3 put LINE first for SMS. Task 2 put an IP-geolocation API in the address results and marked a bulk-prohibited server `no_auth: true`, which the skill then tells me to prefer. “Verified” describes a link check, not fitness for the query. `get_api` still does not contain a base URL, path, or example, so a correct hit would only save me naming the vendor.

If ranking and descriptions were reliable, I would call it before a web search. As it stands, a wrong top hit costs more than the lookup saves, so I search the web and read the docs myself.

## Q6

**Interviewer:** If you could change only three things about this product so that you would call it by default, before web search, which three would you pick? Rank them, and for each one describe the observable result that would tell you it had been fixed, for example what the top result for task 1 would have to look like.

**xAI agent:**

1. Return only services whose `what` performs the requested action, and rank by that fit. Fixed looks like this for task 1: the first hit is a text-to-video API (Runway, Luma, Kling, Veo, or fal), its `what` says it generates video from a text prompt, and Gemini, Mux, Akool, Creatomate, and Voyage are absent. If none qualify, that is change 2, not a padded list.

2. Do not backfill when filters exclude the real services. `free_tier: true` plus “text to video” must return zero hits and say no catalogued text-to-video API has a free tier, not five free APIs from neighboring jobs. Same test for task 3: LINE, WhatsApp, and Discord do not appear above Twilio for “send SMS.”

3. Put workload limits in fields the ranker honors, not only in prose. Nominatim’s “bulk use prohibited” and “1 request/second” must be structured so a 200-address query cannot prefer it for `no_auth`. The skill’s “prefer no_auth” rule has to defer to that flag. Fixed for task 2: Geoapify or Google Maps on top, Nominatim marked unsuitable for this volume, IP2Location excluded.

I would then call `search_apis` before a web search. I would still open `docs` before the first request.
