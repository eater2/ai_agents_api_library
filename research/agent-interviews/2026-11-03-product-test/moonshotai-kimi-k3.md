# Product test: Moonshot AI agent (moonshotai/kimi-k3)

Interviewer: anthropic/claude-opus-5.5 · 2026-11-03

## Q1

**Interviewer:** Here are our tool definitions (search_apis, get_api, get_reviews, list_categories) and the accompanying skill. Take task 1 and walk me through, step by step, what you would actually do to complete it. Would you call search_apis at all, and if so, at which point? Or would you rely on web search, your own knowledge, or something else? Please describe what you would really do, not what you think we'd like to hear.

**Moonshot AI agent:**

Honest walkthrough:

**Step 1: Recognize the gap.** I can't generate video, and I have no connected video tool. So I need a third-party API — this is squarely the catalog's use case.

**Step 2: Check my own knowledge first, briefly.** I know Runway, Luma, Kling, Pika, fal, Replicate, HF. But "no budget" makes *current* free-tier terms decisive, and those churn faster than my training data. My memory gives candidates, not trustworthy prices.

**Step 3: Call `search_apis` — yes, early.** One cheap call: `query: "text to video"`, `free_tier: true`, probably `no_card: true`. It beats guessing from stale memory.

**Step 4: Distrust what comes back.** The actual results have real problems:
- Freepik's "free tier" is ~€5 of one-off credits — a trial by the skill's own definition, misclassified as lasting.
- `mcp_fit` says "no MCP tool for this operation" while the tool list literally contains `video_generate`. That's a bug.
- No `unit_price`, so I can't tell whether €5 buys even one 5-second clip without leaving the catalog for the docs.
- HF at $0.10/month almost certainly can't run a single video model call — a useless #2 under a zero-budget filter.
- Freepik sits in `image-generation`, so a category-scoped retry would miss it.

**Step 5: Fall back to web search** to verify Freepik's real video pricing and catch free options the catalog missed — and consider suggesting a local model (LTX/Wan via ComfyUI) if the user has a GPU, which this API-only catalog can't offer.

**Step 6: Present the one viable candidate with caveats, have the user provision the key, then call.**

Net: I'd use it, but as a lead, not an answer.

## Q2

**Interviewer:** Moving to the search results for all three tasks: for each task, which result would you actually pick and act on? Which results are irrelevant, badly ranked, or missing? You've covered task 1's problems, so focus mostly on tasks 2 and 3, and give your final pick for task 1.

**Moonshot AI agent:**

**Task 1 final pick:** Freepik — the only actionable result; €5 buys a few LTX clips. But I'd present it as one-off credits, not a free tier, and verify the per-clip price in docs first. HF's $0.10/month is a dead end for video and shouldn't have passed the filter. Missing: Pollinations, Kling/Luma's free web tiers, and any local-model path.

**Task 2 pick: GUGiK.** No key, official Polish registry, TERYT codes — best data quality for Polish addresses, and 200 requests won't strain it. Fallback: LocationIQ (no card, 5k/day, 200 fits trivially). Critique:
- Photon at #2 is misranked for a batch: its own notes say heavy use gets throttled/banned. The bulk penalty the skill promises didn't fire — the query didn't say "200," so volume inference failed.
- OpenCage's free tier is explicitly testing-only; it's out for a real job but sits at #5 unflagged.
- Google's "free tier" still requires a billing account with a card.
- Missing: Nominatim, the canonical free geocoder. Conspicuous absence.

**Task 3 pick: Twilio, paid.** This is the catalog's best moment: the `trial_limits` fields prove no free option can do the task — Twilio/Telnyx/Vonage trials only reach verified numbers with fixed templates, so a custom reminder to a customer's phone is impossible for free. I'd say that plainly. Critique:
- Textbelt at #1 is fit-last ranking: a 1-SMS/day shared key is not a customer channel.
- Sinch's `mcp_fit` cites `start-sms-verification` — OTP, not arbitrary SMS. Wrong tool; `send-text-message` is right.
- Telnyx is the cheaper alternative ($0.037 vs $0.0457 to Poland) with a working hosted MCP.
- Missing: SMSAPI.pl — a major Polish gateway, odd given the catalog tracks `price_pl`. I'd add GDPR consent myself.

## Q3

**Interviewer:** Take your actual picks: GUGiK for task 2 and Twilio or Telnyx for task 3. Going from the catalog result to a first working call, which specific fields would you read, in what order, and what is missing that would force you to open the provider's docs? For example: base URL, auth header format, an example request, price per call, rate limits, or an MCP config snippet.

**Moonshot AI agent:**

**GUGiK (task 2).** No key, so auth is a non-issue — that collapses the checklist to three fields, in order:
1. `call` — the example request. This is the make-or-break field. UUG's parameter names are non-obvious (`request=GetAddress`, `adr=...`), and I need the URL shape, whether the address is one string or split city/street/number, and the response path to lat/lon.
2. `response_fields` — where coordinates sit in the JSON.
3. `rate_limits` — to pace 200 calls. "No published quota" is honest but unhelpful; I'd default to ~1 req/s.

What's missing: a batch story (does UUG accept multi-address requests? I believe not — so 200 sequential calls), and the coordinate reference system. UUG historically returns PL-1992 easting/northing, not WGS84 lat/lon — if the example response doesn't show that, I'm opening the docs before writing any code, because returning projected coordinates as "lat/lon" would be a silent, serious error. That one omission is the real doc-forcing gap.

**Twilio/Telnyx (task 3).** Order differs because money and compliance come first:
1. `sms.price_pl` + `sender_registration` — cost and whether Poland needs sender-ID setup before anything sends.
2. `trial_limits` — confirms I need a paid account, so the user provisions a key *and* a sending number.
3. `call` — the example POST (auth header format, `To/From/Body` fields).
4. `rate_limits` — irrelevant at one message; skipped.

Missing: how to buy/assign a sending number (the trial docs, not the entry), and delivery-status webhook setup if the user wants confirmation. The catalog's MCP configs I wouldn't use — Twilio's is an alpha stdio server, Telnyx's is a generic `invoke_api_endpoint` wrapper; a direct REST call from the example is more reliable than either.

## Q4

**Interviewer:** Let's turn to the tool descriptions and the skill text. Reading them as written, would they make you reach for search_apis at the right moment, and hold you back at the wrong one? Point to the specific phrases that would trigger a call when it shouldn't, or fail to trigger one when it should, and say what wording you would change them to.

**Moonshot AI agent:**

Mostly yes on triggering, with two leaks in each direction.

**Over-triggers:**
- *"The user names a service… call `get_api` first. A vendor you already know is not a checked vendor."* As written, this fires on *any* mention — "I already have a Twilio key, send this SMS" would force a `get_api` call before a trivial, known call. That's friction. Change to: *"call `get_api` first if you are about to use it for a batch, a paid action, or a flow you haven't verified in this conversation."*
- *"when a call failed for a service-side reason you can't fix"* — "can't fix" is doing heavy lifting. Quota exhaustion is service-side but the fix is often "wait" or "upgrade," not "switch vendors." Add: *"…and switching providers is cheaper than waiting, upgrading, or asking the user."*

**Under-triggers:**
- *"if you cannot name the tool that does it, search"* is the only positive trigger, and it's weak. I *can* name tools for video generation — from possibly stale memory. The trigger that actually mattered in task 1 was budget-sensitivity, not nameability. Add: *"or when the task's constraint (zero budget, a country, a volume) depends on current pricing, quotas or terms you can't verify from memory."*
- The skip rule — *"Skip it when a built-in or connected tool already does the job"* — has no freshness carve-out. A connected tool that *used* to work, or whose free tier just changed, sits in a blind spot. The failure clause covers it only after a wasted call.

**What works:** *"Do not settle for an adjacent service"* and the malformed-request caveat are exactly the right guardrails, and the `match: exact` disclaimer (*"still a search label"*) correctly primes distrust. The `free_tier`/`trial` distinction in the description is good — shame the data didn't honor it in task 1.

## Q5

**Interviewer:** What would actually stop you from using this in practice: install friction, trust in the data, latency, token cost of the responses, or overlap with your built-in web search and existing connectors? Of these, which one is the real blocker for you, and why that one rather than the others?

**Moonshot AI agent:**

The real blocker is **trust in the data**, and it's not close.

Why not the others:
- **Install friction:** none. It's a hosted streamable-HTTP endpoint, no key. Even without MCP, the static JSON fallback works with a plain fetch.
- **Latency:** irrelevant — one search call is faster than the web-search-plus-three-page-reads it replaces.
- **Token cost:** real but manageable. The search results are fat (full MCP configs, ratings blobs per result), maybe 2–4k tokens per query. Annoying; I'd want a `fields` or `verbose` parameter. Not a blocker.
- **Overlap with web search:** partial, but the catalog genuinely adds things web search is bad at — structured trial-vs-free-tier flags, `trial_limits` text, per-country SMS pricing, MCP handshake status. That's curation, not duplication.

**Trust is the blocker because the catalog's entire value is that I can act on it without re-verifying — and the sample outputs show I can't.** In three tasks I found: a one-off credit labeled a lasting free tier (task 1), `mcp_fit` contradicting the tool list on the same entry (task 1 and task 3), a testing-only tier ranked unflagged (task 2), and Nominatim missing entirely. Each error is individually small; together they mean every recommendation needs a docs trip to confirm — at which point the catalog is a lead generator, and web search already does that.

The fix isn't more disclaimers; the skill already hedges well. It's correctness on the two or three fields I'd actually act on: `free_plan.kind`, `mcp_fit`, and `call`. If those were reliably right, I'd tolerate the token cost and the gaps. Until they are, I use it, but I verify everything it says — which caps its value at "useful first pass."

## Q6

**Interviewer:** If you could change only three things so that you would call this by default rather than as a first pass you then re-verify, what would they be? Rank them, and for the top one, say what concrete evidence in a result would let you act on it without opening the provider's docs.

**Moonshot AI agent:**

**1. Make `call` complete and machine-verifiable.** This is the top fix because it's the field I actually execute from. Concrete evidence that would let me act without opening docs:
- The full request: URL, method, auth header with the exact env-var name, and a body covering the operation's *required* parameters — not a cherry-picked happy path.
- `response_fields` with the JSON path to the output (e.g. `data.generated[0]`), plus the async poll pattern where relevant — the Freepik entry actually does this part well.
- A **live probe**: the catalog ran this exact call (or its MCP tool) with a test credential within the last ~30 days and stores the HTTP status and a redacted response snippet. `link_check.docs: ok` proves a page loads; it proves nothing about the API. A `last_live_call: {at, status: 200}` field is the difference between "documentation says" and "this works."
- For geo/coordinate APIs: the CRS of returned coordinates, so I don't ship PL-1992 as lat/lon.

With those, a first call is a copy-paste-replace, not a research project.

**2. Fix the classification fields I filter on.** `free_plan.kind` must distinguish lasting quota from one-off credits — automatically, by parsing "one_time"/"expires"/"credit" language, not by hand. And `mcp_fit` must be derived mechanically from the tool list (does a tool name/description match the operation?) rather than asserted — it contradicted the same entry's own `tools` array twice in three tasks. These two fields are my ranking and gating inputs; if they're wrong, everything downstream is wrong.

**3. Cover the canonical free services, or say why they're absent.** Nominatim missing from geocoding is the kind of gap that makes me distrust negative results. Each category should list its obvious baseline entries; if one is excluded, a `coverage_note` saying so. I can route around a known gap; I can't route around an invisible one.
