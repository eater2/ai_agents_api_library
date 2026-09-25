# Product test: xAI agent (x-ai/grok-4.7)

Interviewer: anthropic/claude-opus-5.5 · 2026-09-25

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the skill text. Take task 1 and walk me through what you would actually do, step by step, from reading the task to having a working solution. At which point, if any, would you call search_apis? Or would you rely on web search, your own knowledge, or something else? Tell me what you would really do, not what you think we want to hear.

**xAI agent:**

I cannot render video. I have no built-in text-to-video tool, so I would not fake a clip or hand-wave a prompt as the deliverable.

I would call `search_apis` once, early, after that check. Query: `text to video`, category `video-generation`, `free_tier` and `no_card` both true, volume `single`. "No budget" is a constraint, not a vibe. I would not start from web search; the catalog is the right first lookup. I also would not use the query and filter in the sample. `generate video from text prompt` plus only `free_tier` is too loose.

These two hits are not a working solution. Freepik is categorized under images; `get_api` shows the example is image-to-video (Kling), not text-to-video, `no_card` is false, and "~5 EUR credits" is not a price for one 5-second clip. There is no `unit_price`. Hugging Face's $0.10/month will not pay for a video model, and its MCP tools are hub/search, not generation (`covers_full_api: false`). `match: exact` is wrong on both.

I would discard them, retry once with `category: video-generation` and `no_card: true`, then `get_api` only on a hit whose `operations` include text-to-video and whose quota can cover one clip. If that is empty, I say so and web-search. I would not recommend Nominatim-style adjacent services, and I would not curl Magnific with a guessed key.

A working path is: user picks a service that actually fits, adds the key or remote MCP in connector settings, then I call it and poll the task id. Lookup alone does not produce the file. If nothing is free without a card, I say that and point them at a free web UI for one clip rather than a credit-gated API.

## Q2

**Interviewer:** You already rejected both task 1 hits. Now look at the real search results for tasks 2 and 3. For each one, would you act on the results? Which result would you pick, if any, and which are irrelevant, ranked too high or too low, or missing entirely?

**xAI agent:**

I have no geocoder and no SMS tool, so I would use these lists. I would not follow the ranking.

**Task 2.** I would have searched with `volume: bulk`. I drop Nominatim: the public server forbids bulk, and 200 addresses is bulk; a community MCP on an unverified host does not change that. I would not connect Google’s MCP. Its tools are places, routes, and weather, not geocode, and `domain_verified` is false. Esri’s “MCP URL” is a docs path with `derived: true`; I would not treat it as an endpoint. Esri REST can cover 200 (20k geocodes/month) but needs a card. I would pick LocationIQ: exact operation, 5,000/day, 2 req/s, no card, with an attribution caveat if commercial. OpenCage is second, not first: the free tier is testing-only. Missing and worth a web search: GUGiK/PRG for Polish streets, plus Geoapify or HERE. OSM coverage in Poland is unproven here. I would `get_api` LocationIQ, then ask for a key in connector settings. I would not hit Nominatim 200 times.

**Task 3.** I would not send the SMS. This reaches a third party, and none of these are connected. AWS is ranked too high: paid, IAM, US price only, and the MCP tools are docs plus `run_script`, not send-sms. `covers_full_api: true` is not credible. Twilio’s shown MCP is `docs_only`, and the trial cannot text an unverified customer. Bird is the only hit whose remote MCP lists `sms_send`; I would offer that if they will pay and connect it. Sinch or Plivo only as an install plus a trial, and only to a verified test number. I would confirm authorization and country before any key. Missing Vonage or Telnyx does not change that.

## Q3

**Interviewer:** Take LocationIQ for task 2 and Bird for task 3. Going from the `get_api` response to a first successful call, which exact fields would you read, in what order, and what would you still have to go elsewhere for (base URL, auth header format, example request and response, per-call price, rate limits, error codes, MCP config snippet, anything else)? For each gap, say whether it would stop you or just slow you down.

**xAI agent:**

I was not shown `get_api` for either id, only Freepik. I would call it and trust that payload over the search blurbs. These tools cannot make the call. A key in chat is not a successful call.

**LocationIQ.** Read in order: `operations` (forward geocode, not places), `auth_scheme` (`in`, `name`, `format`), `base_url`, `call` (`method`, `url`, `example`, `response_fields`), `rate_limits`, `free_plan` plus `notes` (attribution, commercial terms), `link_check.docs`. Skip `mcp`; search already says none.

Search already has `https://us1.locationiq.com/v1`, `api_key`, and 2 req/s, but not the header-or-query placement, `/search` params, or lat/lon path. If `call` or `auth_scheme` is missing, I open `docs`. That slows me. I will not guess `key=`. The user's key stops me until it is in a secret or env, not the chat. Error codes only slow a retry. Price does not stop one test on the free tier. Terms for 200 addresses should be confirmed before the batch; that stops the batch, not a single probe. No HTTP tool on my side also stops me.

**Bird.** Same order, then `mcp.tools`, `docs_only`, `covers_full_api`, and whether `config.derived` is true. Search marks that URL derived, so I will not connect `https://mcp.bird.com` until `get_api` or the docs page confirms it.

Missing `call.example` only slows me if `docs` loads. A key or OAuth grant stops me. So do workspace, region (`us1` vs `eu1`), and a provisioned originator. Those are not in a catalog entry. Country price and consent stop the send, not the read. Error codes only slow the retry.

## Q4

**Interviewer:** Q4: Look again at the tool descriptions and the skill text. Would they make you call search_apis at the right moment, and hold you back at the wrong one? Name one situation where the current wording would trigger a call you would not want, and one where it would fail to trigger a call you would want. What exact wording would you change, add, or delete?

**xAI agent:**

The three demo tasks would fire correctly: no built-in video, geocode, or SMS tool, and those verbs are in the examples. "Skip if you can do it yourself" would hold me back for translation, SVG, and code. Two edges are wrong.

**Unwanted call.** Skill bullet and `search_apis` description: use it when "your own direct attempt failed (403, rate limit, unsupported format) and another service would unblock the task." Situation: a connected Google Maps or Twilio call returns 403 because the key lacks Geocoding or the number is unverified. I should fix that credential or request, not shop a second vendor. Delete that bullet from both texts. If you keep a fallback, limit it to: no connected tool for this operation, or the user asked to switch providers.

**Missed call.** User names the service and the action is bulk or reaches a third party: "geocode these 200 with Nominatim", "SMS this customer with Twilio." "Which service" does not match, and I do not "lack" a capability, so neither `search_apis` nor `get_api` fires. I would want `get_api` first, to catch a bulk ban, a `docs_only` MCP, and trial limits. Add: "If the user names a service, or you are about to use one for a batch or a message, payment, or other third-party action, call `get_api` before recommending or calling (`search_apis` only if you have no id). A vendor you already know is not already checked."

Also delete "web search or scraping" from the frontmatter. I already have web search; that phrase loads the skill for an ordinary lookup.

## Q5

**Interviewer:** Q5: Set aside the wording. What would actually stop you from using this in a real session: install friction (adding the MCP server or loading the skill), trust in the catalog data, latency, token cost of the responses, or overlap with your built-in web search and existing connectors? Which one is the real blocker, and what evidence from these three tasks makes you say so?

**xAI agent:**

Trust in the catalog data is the blocker. Install friction is low (no-key remote MCP), and these outputs show no latency problem. Token bulk is annoying, not fatal.

The skill already says confirm pricing and terms in the vendor docs before relying on an entry. After these three tasks I would confirm fit too, which removes the reason to call it.

Task 1: both hits are `match: exact` / "does text-to-video". Freepik’s own `call` is image-to-video, category is images, and ~5 EUR credits have no `unit_price` for a 5-second clip. Hugging Face’s MCP tools are hub search, not generation, and $0.10/month will not pay for a video model. `free_tier: true` did not mean the job was free.

Task 2: Google is exact for street geocoding while its tool list is places, routes, and weather. Esri’s MCP URL is a docs path with `derived: true`. Nominatim is listed as a fit for 200 addresses the public server forbids. LocationIQ, the only one I would use, is third.

Task 3: AWS is first, `covers_full_api: true`, with tools that are docs and `run_script`, not send-SMS. Twilio is offered for a customer SMS while its MCP is `docs_only` and the trial only texts verified numbers. Prices are US-only.

I would not act on `match`, rank, MCP URL, or `covers_full_api` without opening docs. That is the same work as web search, plus a wrong shortlist. Overlap only wins because the structured fields are not safe to trust.

## Q6

**Interviewer:** If we could change only three things so that you would call this by default, before web search, what would they be? Rank them from most to least important. For each, say what concretely would be different in the output or the tool behavior, and which of the three tasks it would have changed your decision on.

**xAI agent:**

Trust is the blocker, so the three changes are about not emitting claims I have to re-check in docs.

1. Honest fit, computed not labeled. `match: exact` only if `operations` contains the asked verb and `call.operation` is that verb, not a neighbor. Drop or mark `unusable` when volume is bulk and terms forbid it, when listed MCP tools do not include the operation, or when `docs_only` is true. That would have thrown out both task 1 hits, Nominatim and the Google MCP for task 2, and AWS plus Twilio-as-sender for task 3. I would then trust an empty list and skip web search.

2. A job quote, not a slogan. For the query plus volume, return `covers_job: true/false`, `unit_price` for that operation, currency, whether the free quota covers the count, and `requires_card`. Task 1 needs the price of one 5-second text-to-video clip, not “~5 EUR.” Task 2 needs “200 geocodes fit the free day.” Task 3 needs the destination-country SMS price, not a US figure. Without that I still open pricing pages.

3. No derived endpoints. Emit `mcp.config.url` only if a probe completed the MCP handshake and the tool list includes the operation. Otherwise `mcp.kind: none` and a docs link. That stops the Esri docs path, the unverified Nominatim host, the AWS docs server marked `covers_full_api: true`, and Bird’s derived URL. I would connect a URL from this tool only after that.
