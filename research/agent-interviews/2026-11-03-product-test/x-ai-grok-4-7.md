# Product test: xAI agent (x-ai/grok-4.7)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Below are our four tool definitions (search_apis, get_api, get_reviews, list_categories) and the accompanying skill text. Task 1 is the first of the three tasks we've given you. Walk me through, step by step, what you would actually do to complete it. At which point, if any, would you call search_apis, and when would you instead rely on web search, your own knowledge, or something else? Please describe what you'd really do, not what you think we'd like to hear.

**xAI agent:**

I cannot make the clip myself. This environment has no video tool, so I would call `search_apis` once, with the operation named, plus `free_tier`, `no_card`, and `category: video-generation`. I would not start from memory of Runway, Luma, or Kling.

The result you showed is not good enough to act on. `free_tier: true` ranked Freepik/Magnific first for “~5 EUR of free API credits,” which is a signup credit, not a lasting free plan, and `get_api` says `no_card: false`. Its example is LTX 2.0 Pro at 6 seconds and 1080p, with no `unit_price`, so I cannot tell whether €5 covers one 5-second sunset. Search also says `mcp_fit` has no video tool while the tool list includes `video_generate`. That is a contradiction; I would not trust the fit label.

Hugging Face’s $0.10/month is `listed`, not evidenced, and its MCP tools are hub search, not generation. I would not call it.

I would `get_api` only if a result had a lasting no-card quota and a priced text-to-video call whose duration accepts 5. None of these do. I would say the catalog has no usable zero-budget option, then web-search current free text-to-video limits. I would not invent an endpoint or spend the user’s credits. Without a key they provision outside chat, I stop and tell them I cannot produce the file.

## Q2

**Interviewer:** Now look at the real search results for tasks 2 and 3. For each one, would you act on the results? Which result would you pick, and which results are irrelevant, ranked too high or too low, or missing? For task 1, you've said nothing qualifies. Is there a result that should have been in that list, or one that should have ranked first?

**xAI agent:**

Task 2: I would use the list, then `get_api` on GUGiK before any calls. It is the right first hit: Polish street addresses, no key, official codes. I would pace 200 requests and confirm the example takes a full street address. Photon is only a fallback for misses; “throttled or banned” makes it a bad primary for a batch, so it is ranked too high. OpenCage’s free plan is testing-only and should sit below LocationIQ (5k/day, no card). Google’s MCP has no geocode tool and wants a billed key. Nominatim, which the skill itself names, is missing; it should appear last with the public bulk ban, not vanish.

Task 3: I would not send from this list. No free plan delivers a custom reminder to an arbitrary customer. Textbelt’s shared key (1 SMS/day) is ranked far too high. Sinch’s `mcp_fit` cites `start-sms-verification` while `send-text-message` is in the tool list, and its trial only simulates sends to verified numbers. Twilio, Telnyx, and Vonage are the real options, all limited to verified numbers, templates, or a demo suffix. I would not connect Telnyx’s MCP while `auth` is `none`. The destination country was never given, yet Poland prices are attached, so I cannot pick. Bird and Plivo are absent; not fatal if Twilio is there.

Task 1: Nothing in that filtered list should rank first. Freepik’s ~€5 is a depleting credit, `no_card` is false, `unit_price` is missing, and it is filed under image-generation. HF’s $0.10 and hub-only MCP cannot make the clip. A one-clip, zero-budget search needs `include_trials`; lasting no-card text-to-video basically does not exist.

## Q3

**Interviewer:** Take GUGiK for task 2, the one result you said you'd act on. Going from that `get_api` response to your first successful geocoding request, which specific fields would you read, in what order, and what is missing or unclear: base URL, auth, request format, a working example, rate limits, pricing, error behavior, or an MCP config snippet? Name anything you'd still have to look up elsewhere before sending the first of the 200 requests.

**xAI agent:**

I would not send the first request from the search snippet. It has no `get_api` payload here, and the skill says to start from `call.example` only when the inputs match. I would call `get_api` with `gugik-geocoding` first.

In order I would read: `call.operation` (forward street geocode, not reverse), then `call.example` (method, full URL, parameter names, a Polish address), then `base_url`, then `auth` / `no_auth` and any required header, then `rate_limits` and `notes`, then response field names and CRS, then error shape. MCP is correctly absent, so this is a plain HTTP call.

Search only gives `base_url` `https://services.gugik.gov.pl/uug/`, `no_auth: true`, docs, and “no published quota.” The reason claims an example call exists; the request is not in the result. That is not enough to fire 200 times.

Before request one I would still open the docs for the query-string names, how a street plus number plus city is passed, Polish diacritics, the JSON keys for coordinates, and whether those are WGS84 latitude/longitude or a national grid. A national office often does not return WGS84. I also need no-match and error behavior, any User-Agent rule, and whether a 200-call loop is allowed. “No published quota” is not a rate limit. I would not invent the URL.

## Q4

**Interviewer:** Q4: Now look at the tool descriptions and the skill text themselves. In task 1 you said you'd call `search_apis` because there was no video tool available. Which exact sentences or phrases, if any, made you reach for it then? Is there a situation where that wording would make you call it when you shouldn't, for example when you already know the API or the user has named a provider, or fail to call it when you should? Quote the wording you'd change and give your replacement.

**xAI agent:**

The trigger was the skill, not the tool schemas. Two lines: the description’s “operation you cannot do with your model, built-in tools or currently connected tools (generate video…)”, and When to use: “make a 5-second video” plus “if you cannot name the tool that does it, search.” I would have searched anyway; those lines made the call mandatory. Nothing in the tool descriptions says when to invoke `search_apis`.

That name-the-tool line fails the other way. If I can name Runway or Nominatim from memory, it reads as permission to skip, which is exactly when bulk bans and trial limits matter. The later line, “A vendor you already know is not a checked vendor,” only fires if the user names one or I am “about to use one for a batch, a message, a payment.”

That second rule also over-calls. If Twilio is already connected and the user said to use it, I am still sent to a catalog that ranked Textbelt first for SMS.

Replace “if you cannot name the tool that does it, search” with: “Search when no connected tool can do the operation at this volume. Naming a vendor from memory is not a reason to skip.” Replace the named-service sentence with: “If the user names a service that is not already connected, call `get_api` before using it. If it is connected, do not search for alternatives unless they asked for options or the call failed for a service-side reason.”

## Q5

**Interviewer:** What would actually stop you from using this catalog in a real session: install friction, trust in the data, latency, token cost of the responses, or overlap with your built-in web search and already-connected tools? Of the problems you've hit so far (wrong `mcp_fit` labels, `listed` versus evidenced prices, missing examples), which one is the real blocker that would make you skip `search_apis` and go straight to web search?

**xAI agent:**

Trust is the blocker, not install, latency, or tokens. The server is a no-key remote MCP, so there is nothing to install. A search plus one `get_api` is cheaper than reading vendor docs, and I already have web search for the fallback the skill itself allows.

The real defect is that the labels I am told to act on are wrong. Task 1 marked Freepik `has_free_tier: true` for a one-off ~€5 credit, with `no_card: false` and no `unit_price`, then ranked it first for a zero-budget job. Its `mcp_fit` said no video tool while `video_generate` was in the tool list. Task 3 did the same with Sinch: `mcp_fit` named `start-sms-verification` and ignored `send-text-message`. A `listed` match with a chat-completion example is not evidence of text-to-video. Search also never returned the request I would send, so I still open the docs.

I would still call it for an unknown operation, then discard the ranking and verify. I would skip it and go straight to web search when the constraint is budget, bulk terms, or “does this endpoint accept these inputs,” because those are exactly the fields the catalog mislabels. Overlap with connected tools is a skip for a different reason: if the tool is already here, the catalog has nothing to add.

## Q6

**Interviewer:** If you could change only three things so that you would call `search_apis` by default and act on its results instead of re-verifying everything, what would they be? Rank them, and for each one say concretely what the field, behavior or output would look like.

**xAI agent:**

1. Make the filter fields true. `has_free_tier` must be true only for a lasting quota; a ~€5 signup credit is `trial` and must not survive `free_tier: true`. `mcp_fit` must be computed from the `tools` array already in the payload: Freepik’s `video_generate` and Sinch’s `send-text-message` are fits, not “no tool named.” If those two disagree, I re-check every hit.

2. An `exact` search hit must carry the request I would send, not a reason string that claims an example exists. Concrete fields: `method`, full URL, parameter names, one Polish street-address example, response keys for latitude/longitude, CRS (`EPSG:4326` or not), numeric `rate_limits`, and error shape. “No published quota” is not a limit. Without that, I still open the docs before request one of 200.

3. Rank by the filters I passed, and drop what fails them. A zero-budget search must not lead with `no_card: false` and no `unit_price`. `volume: bulk` must sink Photon-style fair-use bans below LocationIQ’s 5,000/day. Put `unit_price` and `free_plan.kind` on the search card so I do not `get_api` just to learn the call is unaffordable. Do not attach Poland SMS prices when no country was asked.

Those three, and I would call it by default and send the first matching request. Anything short of consistent booleans plus a real example, and I still verify.
